"""Summary of a dataset feasibility test (one generator), compared with pilot_v1.

Usage: .venv/bin/python src/summarize_base_test.py --config config/base_test.yaml

Reads only saved files; makes no model calls. This is not part of the final
experiment and says nothing about which generator is better.
"""

import argparse

import pandas as pd
from common import load_config, read_jsonl, result_path

REFERENCE_RUN = "pilot_v1"
SD_TOL = 1e-9  # identical scores can give a float SD of ~1e-17
QUANTILES = [("mín", 0), ("P10", 0.10), ("P25", 0.25), ("mediana", 0.50), ("P75", 0.75),
             ("P90", 0.90), ("máx", 1)]


def load_eval(run, name):
    rows = read_jsonl(result_path("evaluation", f"{run}_{name}.jsonl"))
    ev = pd.DataFrame(rows)
    if not ev.empty:
        ev["score"] = ev["score"].astype(float)
    return ev, read_jsonl(result_path("evaluation", f"{run}_{name}_errors.jsonl"))


def share_one(ev):
    return f"{(ev['score'] == 1).sum()}/{len(ev)} ({(ev['score'] == 1).mean():.0%})"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    cfg = load_config(args.config)
    run = cfg["run_id"]

    ret = read_jsonl(result_path("retrieval", f"{run}.jsonl"))
    gens = {g: pd.DataFrame(read_jsonl(result_path("generation", f"{run}_{g}.jsonl")))
            for g in cfg["generation"]["generators"]}
    stage_rows = ret + [r for g in gens.values() for r in g.to_dict("records")]

    lines = [f"# Teste de viabilidade da base — {run}\n",
             "**Este é um teste de viabilidade da base de dados, não parte do experimento "
             "final.** Apenas o gerador aberto foi usado; nada aqui compara geradores.\n",
             f"- Base: `{cfg['dataset']['name']}` / `{cfg['dataset'].get('subset')}` / "
             f"`{cfg['dataset'].get('split')}` (revisão `{cfg['dataset']['revision'][:12]}`).",
             f"- Perguntas: {len(ret)} (seed {cfg['questions']['seed']}): "
             f"{[r['qid'] for r in ret]}."]

    if ret:
        lines.append(f"- Recuperação: {ret[0]['n_chunks_indexed']} trechos indexados; trecho da "
                     f"própria pergunta em {sum(r['same_page_hit'] for r in ret)}/{len(ret)}; "
                     f"indexação {ret[0]['index_s']:.0f}s.")
    for name, g in gens.items():
        if g.empty:
            continue
        lines.append(f"- Geração ({name}, {g['model'].iloc[0]}): {len(g)} respostas; "
                     f"caracteres medianos {g['answer'].str.len().median():.0f} "
                     f"(mín {g['answer'].str.len().min()}, máx {g['answer'].str.len().max()}); "
                     f"tempo total {g['elapsed_s'].sum():.0f}s; finish_reason "
                     f"{g['finish_reason'].value_counts().to_dict()}.")

    for name in cfg["evaluation"]["configs"]:
        ev, errors = load_eval(run, name)
        if ev.empty:
            continue
        stage_rows += ev.to_dict("records")
        ref, _ = load_eval(REFERENCE_RUN, name)
        ref_open = ref[ref["generator"] == "open"] if not ref.empty else ref
        q = ev["score"].quantile([p for _, p in QUANTILES])
        per_resp = ev.groupby("qid")["score"].agg(["mean", lambda s: s.std(ddof=1)])
        calls = [c for r in ev["calls"] for c in r]
        nan = ev[ev["score"].isna()]
        lines += [
            f"\n## Juiz `{name}`\n",
            f"- Avaliações: {len(ev)}; erros registrados: {len(errors)}.",
            f"- **Notas = 1,0: {share_one(ev)}**; no {REFERENCE_RUN}: {share_one(ref)} no total, "
            f"{share_one(ref_open)} só com o gerador aberto.",
            "- Distribuição das notas: " + "; ".join(
                f"{label} {v:.3f}" for (label, _), v in zip(QUANTILES, q)) +
            f"; média {ev['score'].mean():.3f}.",
            f"- Afirmações por avaliação: média {ev['n_statements'].mean():.1f}, mediana "
            f"{ev['n_statements'].median():.0f} (mín {ev['n_statements'].min()}, máx "
            f"{ev['n_statements'].max()}); no {REFERENCE_RUN} (aberto): média "
            f"{ref_open['n_statements'].mean():.1f}.",
            f"- Notas NaN: {len(nan)}"
            + (f" (qid/j: {list(zip(nan['qid'], nan['j']))}; nenhuma afirmação extraída: "
               f"{(nan['n_statements'] == 0).sum()})" if len(nan) else "") + ".",
            f"- Respostas com DP > 0 entre as {int(ev['j'].max())} repetições: "
            f"{(per_resp.iloc[:, 1] > SD_TOL).sum()}/{len(per_resp)}; DP mediano "
            f"{per_resp.iloc[:, 1].median():.3f}, DP máximo {per_resp.iloc[:, 1].max():.3f}.",
            f"- Tempo: total {ev['elapsed_s'].sum() / 60:.1f} min; por avaliação mediana "
            f"{ev['elapsed_s'].median():.1f}s (máx {ev['elapsed_s'].max():.1f}s).",
            f"- Chamadas ao juiz: {len(calls)} ({len(calls) / len(ev):.2f} por avaliação); "
            f"finish_reason {pd.Series([c['finish_reason'] for c in calls]).value_counts().to_dict()}; "
            f"tokens de prompt máx {max(c['usage']['prompt_tokens'] for c in calls)}, "
            f"tokens gerados máx {max(c['usage']['completion_tokens'] for c in calls)}.",
        ]

    commits = sorted({r.get("code_commit", "não registrado") for r in stage_rows})
    lines.insert(2, f"- Commit do código usado nas etapas: {', '.join(f'`{c}`' for c in commits)}.")
    out = result_path("analysis", f"{run}_summary.md")
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
