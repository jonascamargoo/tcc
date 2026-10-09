#!/bin/zsh
# Driver of the final run (config/final.yaml). Gemini (free tier, 20 requests/day) and the
# local judge run in independent loops, so the daily quota is used while evaluations proceed.
#
# Start from the project root (keeps the Mac awake while plugged in):
#   nohup caffeinate -is zsh src/run_final.sh >> logs/final_v1.log 2>&1 &
# Safe to restart at any time: every step resumes from the saved files.
# Progress: .venv/bin/python src/progress.py --config config/final.yaml

set -u
cd "${0:A:h}/.."
C=config/final.yaml
P=.venv/bin/python
RUN=final_v1
N=203
K=5
export PYTHONUNBUFFERED=1

log() { echo "## $(date '+%F %T') $*"; }
count() { if [ -f "$1" ]; then wc -l < "$1" | tr -d ' '; else echo 0; fi; }
GEN=results/generation/${RUN}_proprietary.jsonl

# The judge relies on the server's context length, so always use a server started here.
pkill -f "ollama serve" && sleep 3
OLLAMA_MODELS=$PWD/.ollama-models OLLAMA_CONTEXT_LENGTH=8192 ollama serve >> logs/ollama_serve.log 2>&1 &
SERVER=$!
until curl -s http://localhost:11434/api/version > /dev/null; do sleep 1; done
log "start (ollama pid $SERVER)"

$P src/retrieve.py --config $C || exit 1
$P src/generate.py --config $C --generator open || exit 1

gemini_loop() {
  while [ "$(count $GEN)" -lt $N ]; do
    log "gemini: $(count $GEN)/$N answers"
    out=$($P src/generate.py --config $C --generator proprietary 2>&1)
    echo "$out" | grep -v "Warning"
    wait_s=$(echo "$out" | sed -n 's/^RETRY_AFTER_S=//p' | tail -1)
    if [ -n "$wait_s" ]; then
      log "gemini: quota exhausted, sleeping $((wait_s + 300))s"
      sleep $((wait_s + 300))
    elif [ "$(count $GEN)" -lt $N ]; then
      log "gemini: stopped without 429 (e.g. repeated 5xx), retrying in 15 min"
      sleep 900
    fi
  done
  log "gemini: done"
}

eval_loop() {
  local total=$((2 * N * K))
  while true; do
    $P src/evaluate.py --config $C --judge-config default
    $P src/evaluate.py --config $C --judge-config t1
    if [ "$(count $GEN)" -ge $N ] &&
       [ "$(count results/evaluation/${RUN}_default.jsonl)" -ge $total ] &&
       [ "$(count results/evaluation/${RUN}_t1.jsonl)" -ge $total ]; then
      break
    fi
    sleep 1800
  done
  log "evaluation: done"
}

gemini_loop &
GEMINI=$!
eval_loop
wait $GEMINI
$P src/analyze.py --config $C
log "end"
kill $SERVER
