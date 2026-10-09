"""Step 2: one answer per question for one generator, from the saved chunks.

Usage: .venv/bin/python src/generate.py --config config/pilot.yaml --generator proprietary|open
"""

import argparse
import hashlib
import os
import re
import sys
import time

from common import (GEMINI_BASE_URL, ROOT, append_jsonl, code_commit, load_config, now,
                    ollama_info, read_jsonl, result_path)
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI


# Gemini retries are handled here instead of by the client: failed requests also
# count against the free-tier daily quota, so waits are long and a 429 stops the run.
RETRY_WAITS_S = (120, 240, 480)


def make_llm(gen, ollama_url):
    if gen["provider"] == "gemini":
        return ChatOpenAI(model=gen["model"], base_url=GEMINI_BASE_URL,
                          api_key=os.environ["GEMINI_API_KEY"], max_retries=0,
                          **gen["params"])
    if gen["provider"] == "ollama":
        return ChatOllama(model=gen["model"], base_url=ollama_url, **gen["params"])
    raise ValueError(f"Unknown provider: {gen['provider']}")


def invoke_with_retry(llm, messages):
    """Return (message, seconds of the successful call, attempts, seconds waited)."""
    waited = 0
    for attempt in range(1, len(RETRY_WAITS_S) + 2):
        t0 = time.perf_counter()
        try:
            return llm.invoke(messages), time.perf_counter() - t0, attempt, waited
        except Exception as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status == 429:
                # The error says when the quota resets; run_final.sh sleeps until then.
                delay = re.search(r"'retryDelay': '(\d+)s'", str(e))
                print(f"RETRY_AFTER_S={delay.group(1) if delay else 3600}", flush=True)
                sys.exit(f"Quota exhausted (429); progress saved. Rerun later. {e}")
            if status is None or status < 500 or attempt > len(RETRY_WAITS_S):
                raise
            wait = RETRY_WAITS_S[attempt - 1]
            print(f"    HTTP {status}; attempt {attempt} failed, waiting {wait}s")
            time.sleep(wait)
            waited += wait


def format_context(chunks):
    return "\n\n".join(f"[{i}] {c['text']}" for i, c in enumerate(chunks, start=1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--generator", required=True, choices=["proprietary", "open"])
    args = parser.parse_args()

    cfg = load_config(args.config)
    commit = code_commit()
    gen = cfg["generation"]["generators"][args.generator]
    prompt_file = cfg["generation"]["prompt_file"]
    prompt_text = (ROOT / prompt_file).read_text()
    template = ChatPromptTemplate.from_template(prompt_text)

    retrieval_path = result_path("retrieval", f"{cfg['run_id']}.jsonl")
    retrieval = read_jsonl(retrieval_path)
    out = result_path("generation", f"{cfg['run_id']}_{args.generator}.jsonl")
    done = {r["qid"] for r in read_jsonl(out)}
    todo = [r for r in retrieval if r["qid"] not in done]
    print(f"{args.generator} ({gen['model']}): {len(done)} done, {len(todo)} to do")
    if not todo:
        return

    llm = make_llm(gen, cfg["ollama_url"])
    local = ollama_info(cfg["ollama_url"], gen["model"]) if gen["provider"] == "ollama" else {}

    for r in todo:
        messages = template.format_messages(context=format_context(r["chunks"]),
                                            question=r["question"])
        msg, elapsed, attempts, waited = invoke_with_retry(llm, messages)
        meta = msg.response_metadata
        append_jsonl(out, {
            "qid": r["qid"],
            "generator": args.generator,
            "provider": gen["provider"],
            "model": gen["model"],
            "model_version": meta.get("model_name") or meta.get("model"),
            **local,
            "params": gen["params"],
            "prompt_file": prompt_file,
            "prompt_sha256": hashlib.sha256(prompt_text.encode()).hexdigest(),
            "retrieval_ref": retrieval_path.name,
            "chunk_ids": [c["chunk_id"] for c in r["chunks"]],
            "answer": msg.content,
            "usage": msg.usage_metadata,
            "response_id": msg.id,
            "finish_reason": meta.get("finish_reason") or meta.get("done_reason"),
            "attempts": attempts,
            "retry_wait_s": waited,
            "code_commit": commit,
            "timestamp": now(),
            "elapsed_s": round(elapsed, 2),
        })
        print(f"  qid {r['qid']}: {elapsed:.1f}s, {len(msg.content)} chars")


if __name__ == "__main__":
    main()
