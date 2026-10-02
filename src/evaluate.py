"""Step 3: Ragas Faithfulness, K repetitions per answer, for one judge configuration.

Usage: .venv/bin/python src/evaluate.py --config config/pilot.yaml --judge-config default|t1

Each repetition j uses seed = j. Every HTTP call to the judge is logged with the
parameters actually sent, so the absence of caching can be checked afterwards.
"""

import argparse
import asyncio
import json
import math
import time

import httpx
from common import (ROOT, append_jsonl, code_commit, load_config, now, ollama_info,
                    read_jsonl, result_path)
from langchain_core.globals import get_llm_cache
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.metrics.collections import Faithfulness

SENT_KEYS = ("model", "temperature", "top_p", "seed", "max_tokens")
CALLS = []  # HTTP calls of the evaluation in progress


async def log_response(response):
    await response.aread()
    sent = json.loads(response.request.content or b"{}")
    try:
        body = response.json()
    except ValueError:
        body = {}
    choice = (body.get("choices") or [{}])[0]
    CALLS.append({
        "status": response.status_code,
        "response_id": body.get("id"),
        "finish_reason": choice.get("finish_reason"),
        "usage": body.get("usage"),
        "sent": {k: sent.get(k) for k in SENT_KEYS},
        "elapsed_s": round(response.elapsed.total_seconds(), 2),
    })


def check_no_cache(llm):
    assert get_llm_cache() is None, "LangChain global LLM cache is set"
    assert llm.cache is None, "Ragas LLM cache is set"
    assert not (ROOT / ".cache" / "cache.db").exists(), "Ragas DiskCacheBackend file found"


async def score_once(metric, question, answer, contexts):
    """Same steps as Faithfulness.ascore (Ragas 0.4.3), keeping statements and verdicts."""
    statements = await metric._create_statements(question, answer)
    if not statements:
        return math.nan, statements, []
    verdicts = await metric._create_verdicts(statements, "\n".join(contexts))
    return (metric._compute_score(verdicts), statements,
            [v.model_dump() for v in verdicts.statements])


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--judge-config", required=True)
    args = parser.parse_args()

    cfg = load_config(args.config)
    commit = code_commit()
    ev = cfg["evaluation"]
    overrides = ev["configs"][args.judge_config]
    run = cfg["run_id"]

    retrieval = {r["qid"]: r for r in read_jsonl(result_path("retrieval", f"{run}.jsonl"))}
    answers = []
    for generator in cfg["generation"]["generators"]:
        answers += read_jsonl(result_path("generation", f"{run}_{generator}.jsonl"))

    out = result_path("evaluation", f"{run}_{args.judge_config}.jsonl")
    errors = result_path("evaluation", f"{run}_{args.judge_config}_errors.jsonl")
    done = {(r["qid"], r["generator"], r["j"]) for r in read_jsonl(out)}
    todo = [(a, j) for a in answers for j in range(1, ev["K"] + 1)
            if (a["qid"], a["generator"], j) not in done]
    print(f"Judge config '{args.judge_config}': {len(done)} done, {len(todo)} to do")
    if not todo:
        return

    judge = {"judge_model": ev["judge_model"],
             **ollama_info(cfg["ollama_url"], ev["judge_model"])}
    client = AsyncOpenAI(
        base_url=f"{cfg['ollama_url']}/v1", api_key="ollama",
        http_client=httpx.AsyncClient(timeout=900,
                                      event_hooks={"response": [log_response]}),
    )

    for answer, j in todo:
        llm = llm_factory(ev["judge_model"], provider="openai", client=client,
                          seed=j, **overrides)
        check_no_cache(llm)
        metric = Faithfulness(llm=llm)
        contexts = [c["text"] for c in retrieval[answer["qid"]]["chunks"]]
        key = {"qid": answer["qid"], "generator": answer["generator"],
               "judge_config": args.judge_config, "j": j}

        CALLS.clear()
        t0 = time.perf_counter()
        try:
            score, statements, verdicts = await score_once(
                metric, retrieval[answer["qid"]]["question"], answer["answer"], contexts)
        except Exception as e:  # recorded and retried on the next run
            append_jsonl(errors, {**key, "error": repr(e)[:2000], "calls": list(CALLS),
                                  "timestamp": now()})
            print(f"  ERROR {key}: {repr(e)[:200]}")
            continue
        elapsed = time.perf_counter() - t0

        append_jsonl(out, {
            **key,
            "score": None if math.isnan(score) else score,
            "n_statements": len(statements),
            "statements": statements,
            "verdicts": verdicts,
            **judge,
            "model_args": llm.model_args,
            "n_http_calls": len(CALLS),
            "calls": list(CALLS),
            "code_commit": commit,
            "timestamp": now(),
            "elapsed_s": round(elapsed, 2),
        })
        print(f"  qid {key['qid']} {key['generator']} j={j}: score={score:.3f} "
              f"({len(statements)} statements, {len(CALLS)} calls, {elapsed:.1f}s)")


if __name__ == "__main__":
    asyncio.run(main())
