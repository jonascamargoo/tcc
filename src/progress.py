"""Progress and feasibility of a run, without any score comparison.

Usage: .venv/bin/python src/progress.py --config config/final.yaml

Shows counts, refusals, errors, NaN and model versions only: no means and no
winners, so checking progress does not peek at the result.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone

from analyze import is_refusal
from common import load_config, read_jsonl, result_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    cfg = load_config(args.config)
    run, n, K = cfg["run_id"], cfg["questions"]["n"], cfg["evaluation"]["K"]

    gens = {g: read_jsonl(result_path("generation", f"{run}_{g}.jsonl"))
            for g in cfg["generation"]["generators"]}
    for g, rows in gens.items():
        refusals = [r["qid"] for r in rows if is_refusal(r["answer"])]
        short = [r["qid"] for r in rows if not is_refusal(r["answer"]) and len(r["answer"]) < 150]
        print(f"{g}: {len(rows)}/{n} answers; refusals {len(refusals)} "
              f"({len(refusals) / max(len(rows), 1):.0%}); short non-refusals {short}; "
              f"versions {dict(Counter(r['model_version'] for r in rows))}; "
              f"requests incl. retries {sum(r['attempts'] for r in rows)}")

    prop = gens.get("proprietary", [])
    if prop:
        first = datetime.fromisoformat(prop[0]["timestamp"])
        days = (datetime.now(timezone.utc) - first).total_seconds() / 86400
        per_day = Counter(r["timestamp"][:10] for r in prop)
        print(f"  proprietary answers per UTC day: {dict(per_day)}")
        if days > 0.5 and len(prop) < n:
            print(f"  estimate: {(n - len(prop)) / (len(prop) / days):.1f} more days")

    answered = {g: {r["qid"] for r in rows if not is_refusal(r["answer"])}
                for g, rows in gens.items()}
    both = set(r["qid"] for r in prop) & set(r["qid"] for r in gens.get("open", []))
    usable = both & answered.get("proprietary", set()) & answered.get("open", set())
    print(f"pairs with both answers: {len(both)}; usable (no refusal): {len(usable)}")

    for name in cfg["evaluation"]["configs"]:
        ev = read_jsonl(result_path("evaluation", f"{run}_{name}.jsonl"))
        errors = read_jsonl(result_path("evaluation", f"{run}_{name}_errors.jsonl"))
        print(f"judge {name}: {len(ev)}/{2 * n * K} evaluations; errors logged "
              f"{len(errors)}; NaN {sum(r['score'] is None for r in ev)}"
              + (f"; last {ev[-1]['timestamp']}" if ev else ""))


if __name__ == "__main__":
    main()
