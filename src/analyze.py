"""Steps 4-5: Experiment 1 (judge variation) and Experiment 2 (paired criterion).

Usage: .venv/bin/python src/analyze.py --config config/pilot.yaml

Reads only saved files; makes no model calls. One set of outputs per judge config.
NaN rule (CLAUDE.md 6.1): response score = mean of valid repetitions; a question is
dropped from both comparisons when either response has no valid repetition.
Refusal rule (CLAUDE.md 6.1): an answer that is only the refusal sentence the prompt
asks for has no Faithfulness score; its pair is dropped from both comparisons and
refusals are reported per generator as a separate outcome.
"""

import argparse
import math
import re

import pandas as pd
from common import load_config, read_jsonl, result_path
from scipy.stats import wilcoxon

PROP, OPEN = "proprietary", "open"
ALPHA = 0.05
SD_TOL = 1e-9  # identical scores can give a float SD of ~1e-17
# The refusal sentence of prompts/generation_v1.txt, matched as the whole answer
# (case, surrounding spaces and a final period ignored). Partial refusals are scored.
REFUSAL = "i cannot answer based on the context"


def is_refusal(answer):
    return re.sub(r"\.$", "", answer.strip()).strip().lower() == REFUSAL


def winner(p, o):
    return PROP if p > o else OPEN if o > p else "tie"


def describe(series):
    s = series.dropna()
    if s.empty:
        return {"n": 0}
    return {"n": len(s), "mean": s.mean(), "median": s.median(),
            "p10": s.quantile(0.10), "p25": s.quantile(0.25),
            "p75": s.quantile(0.75), "p90": s.quantile(0.90)}


def per_response(ev):
    """Mean, SD (ddof=1) and CV of the K scores of each answer."""
    rows = []
    for (qid, gen), g in ev.groupby(["qid", "generator"]):
        s = g["score"].dropna()
        mean = s.mean() if len(s) else math.nan
        sd = s.std(ddof=1) if len(s) >= 2 else math.nan
        if sd < SD_TOL:
            sd = 0.0
        rows.append({"qid": qid, "generator": gen, "n_valid": len(s),
                     "n_nan": int(g["score"].isna().sum()), "mean": mean, "sd": sd,
                     "cv": sd / mean if len(s) >= 2 and mean != 0 else math.nan,
                     "statements_vary": g["statements"].map(tuple).nunique() > 1,
                     "verdicts_vary": g["verdict_list"].map(tuple).nunique() > 1})
    return pd.DataFrame(rows)


def single_eval_simulation(ev):
    """Use only repetition j of each answer, as if the judge were run once."""
    wide = ev.pivot_table(index=["j", "qid"], columns="generator", values="score")
    by_j, per_q = [], []
    for j, g in wide.groupby(level="j"):
        g = g.dropna()  # drop questions with NaN in this j only
        by_j.append({"j": j, "n_questions": len(g), "mean_prop": g[PROP].mean(),
                     "mean_open": g[OPEN].mean(),
                     "winner": winner(g[PROP].mean(), g[OPEN].mean())})
        for (_, qid), row in g.iterrows():
            per_q.append({"j": j, "qid": qid, "winner": winner(row[PROP], row[OPEN])})
    return pd.DataFrame(by_j), pd.DataFrame(per_q)


def paired_test(scores):
    """Wilcoxon signed-rank on d = proprietary - open, two-sided, zero_method='wilcox'."""
    d = scores[PROP] - scores[OPEN]
    n_zero = int((d == 0).sum())
    n = len(d) - n_zero
    res = {"n_pairs": len(d), "n_zero_d": n_zero, "n_used": n, "zero_method": "wilcox",
           "median_d": d.median(), "mean_d": d.mean()}
    if n == 0:
        return {**res, "W": math.nan, "p": math.nan, "z": math.nan, "r": math.nan}
    exact = wilcoxon(d, zero_method="wilcox", alternative="two-sided", method="auto")
    asym = wilcoxon(d, zero_method="wilcox", alternative="two-sided", method="asymptotic")
    return {**res, "W": float(exact.statistic), "p": float(exact.pvalue),
            "z": float(asym.zstatistic), "r": abs(float(asym.zstatistic)) / math.sqrt(n)}


def fmt(x, nd=3):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}"


def analyze_config(cfg, name, rows, errors, refused, lines):
    run = cfg["run_id"]
    ev_all = pd.DataFrame(rows)
    ev_all["score"] = ev_all["score"].astype(float)
    ev_all["verdict_list"] = ev_all["verdicts"].map(lambda v: [x["verdict"] for x in v])
    K = int(ev_all["j"].max())
    is_ref = [(q, g) in refused for q, g in zip(ev_all["qid"], ev_all["generator"])]
    ref_ev = ev_all[is_ref]
    ev = ev_all[[not r for r in is_ref]]  # refusals have no Faithfulness score
    refused_q = {q for q, _ in refused}

    # --- Experiment 1 ---
    resp = per_response(ev)
    resp.to_csv(result_path("analysis", f"{run}_{name}_exp1_responses.csv"),
                                 index=False)
    summary = []
    for label, g in [(PROP, resp[resp.generator == PROP]),
                     (OPEN, resp[resp.generator == OPEN]), ("total", resp)]:
        summary.append({"group": label, "metric": "sd", **describe(g["sd"])})
        summary.append({"group": label, "metric": "cv", **describe(g["cv"])})
    pd.DataFrame(summary).to_csv(result_path("analysis", f"{run}_{name}_exp1_summary.csv"),
                                 index=False)

    by_j, per_q = single_eval_simulation(ev)
    by_j.to_csv(result_path("analysis", f"{run}_{name}_exp1_single_eval.csv"), index=False)
    modal = by_j["winner"].mode().iloc[0] if len(by_j) else None
    share_j_differs = (by_j["winner"] != modal).mean() if len(by_j) else math.nan
    q_winners = per_q.groupby("qid")["winner"].agg(["nunique", "size"])
    q_eligible = q_winners[q_winners["size"] >= 2]
    share_q_changes = (q_eligible["nunique"] > 1).mean() if len(q_eligible) else math.nan

    sd_k3 = None
    if K > 3:
        sd_k3 = ev[ev.j <= 3].groupby(["qid", "generator"])["score"].std(ddof=1)

    # --- Experiment 2 ---
    scores = resp.pivot(index="qid", columns="generator", values="mean")
    # Questions still missing one generator's answer are not NaN exclusions.
    answered = ev.groupby("qid")["generator"].nunique()
    refusal_pairs = scores[scores.index.isin(refused_q)]
    scores = scores[~scores.index.isin(refused_q)]
    missing = scores[scores.index.isin(answered[answered < 2].index)]
    excluded = scores[~scores.index.isin(missing.index) & scores.isna().any(axis=1)]
    scores = scores.dropna()
    test = paired_test(scores) if len(scores) else {}
    mean_prop, mean_open = scores[PROP].mean(), scores[OPEN].mean()
    direct = winner(mean_prop, mean_open)
    if test and not math.isnan(test.get("p", math.nan)) and test["p"] < ALPHA:
        paired = PROP if test["median_d"] > 0 or (test["median_d"] == 0 and test["mean_d"] > 0) else OPEN
    else:
        paired = "no significant difference"
    # A direct-comparison tie and "no significant difference" are the same conclusion.
    agree = paired == direct or (direct == "tie" and paired == "no significant difference")
    pd.DataFrame([{**test, "mean_prop": mean_prop, "mean_open": mean_open,
                   "direct_winner": direct, "paired_conclusion": paired, "agree": agree,
                   "n_missing_answer": len(missing), "n_excluded_nan": len(excluded),
                   "n_excluded_refusal": len(refusal_pairs)}]).to_csv(
        result_path("analysis", f"{run}_{name}_exp2.csv"), index=False)

    # --- Calls, timing and cache diagnostics ---
    calls = [c for r in rows for c in r["calls"]]
    sent = pd.DataFrame([c["sent"] for c in calls])
    finish = pd.Series([c["finish_reason"] for c in calls]).value_counts().to_dict()

    lines += [
        f"\n## Configuração do juiz: `{name}`\n",
        f"- Avaliações salvas: {len(ev_all)} (K={K}); erros registrados: {len(errors)}; "
        f"avaliações de recusas, fora das análises: {len(ref_ev)} (notas dadas pelo juiz: "
        f"{ref_ev['score'].value_counts(dropna=False).sort_index().to_dict()}).",
        f"- Parâmetros efetivamente enviados: temperature {sorted(sent['temperature'].dropna().unique().tolist())}, "
        f"top_p {sorted(sent['top_p'].dropna().unique().tolist())}, seed {sorted(sent['seed'].dropna().unique().tolist())}, "
        f"max_tokens {sorted(sent['max_tokens'].dropna().unique().tolist())}.",
        f"- Chamadas HTTP ao juiz: {len(calls)} ({len(calls) / len(ev_all):.2f} por avaliação; "
        f"{(ev_all['n_http_calls'] > 2).sum()} avaliações com mais de 2); "
        f"status ≠ 200: {sum(c['status'] != 200 for c in calls)}; finish_reason: {finish}.",
        # Ollama ids are short random numbers and can collide, so the cache evidence is
        # that every call took real time and generated tokens.
        f"- Evidência de ausência de cache: duração mínima por chamada {min(c['elapsed_s'] for c in calls):.1f}s; "
        f"tokens gerados por chamada: mín. {min(c['usage']['completion_tokens'] for c in calls)}, "
        f"máx. {max(c['usage']['completion_tokens'] for c in calls)} (limite max_tokens "
        f"{int(sent['max_tokens'].max())}); tokens de prompt máx. "
        f"{max(c['usage']['prompt_tokens'] for c in calls)} (contexto {cfg['ollama_context_length']}).",
        f"- Tempo por avaliação: mediana {ev_all['elapsed_s'].median():.1f}s, total {ev_all['elapsed_s'].sum() / 60:.1f} min.",
        f"- Saturação (sem recusas): {(ev['score'] == 1).mean():.0%} das notas = 1,0; "
        f"notas NaN: {ev['score'].isna().sum()}.",
        f"- Respostas cujas afirmações variam entre as repetições: {resp['statements_vary'].sum()}/{len(resp)}; "
        f"cujos veredictos variam: {resp['verdicts_vary'].sum()}/{len(resp)}.",
        "\n**Experimento 1 — variação do juiz**\n",
        "| Grupo | DP mediano | DP médio | DP P90 | CV mediano |",
        "|---|---|---|---|---|",
    ]
    for label in (PROP, OPEN, "total"):
        g = resp if label == "total" else resp[resp.generator == label]
        lines.append(f"| {label} | {fmt(g['sd'].median())} | {fmt(g['sd'].mean())} | "
                     f"{fmt(g['sd'].quantile(0.9))} | {fmt(g['cv'].median())} |")
    lines += [
        f"\n- Respostas com DP > 0: {(resp['sd'] > 0).sum()}/{resp['sd'].notna().sum()}.",
        f"- Avaliação única por j (vencedor geral): {by_j['winner'].tolist()}; "
        f"proporção de j com vencedor diferente do modal: {fmt(share_j_differs, 2)}.",
        f"- Proporção de perguntas cujo vencedor muda entre repetições: {fmt(share_q_changes, 2)}.",
    ]
    if sd_k3 is not None:
        lines.append(f"- DP mediano com j=1..3: {fmt(sd_k3.median())} vs com j=1..{K}: "
                     f"{fmt(resp['sd'].median())}.")
    lines += [
        "\n**Experimento 2 — critério pareado**"
        + (" (só valida o código no piloto; n pequeno)" if run.startswith("pilot") else "") + "\n",
        f"- Pares: {test.get('n_pairs', 0)}; perguntas sem resposta de um dos geradores: "
        f"{len(missing)}; excluídos por recusa: {len(refusal_pairs)}; excluídos por NaN: {len(excluded)}; "
        f"d = 0: {test.get('n_zero_d', '—')} (zero_method=wilcox).",
        f"- d mediana {fmt(test.get('median_d'))}, d média {fmt(test.get('mean_d'))}; "
        f"W={fmt(test.get('W'), 1)}, p={fmt(test.get('p'))}, Z={fmt(test.get('z'))}, r={fmt(test.get('r'))}.",
        f"- Comparação direta: média proprietário {fmt(mean_prop)} vs aberto {fmt(mean_open)} → {direct}. "
        f"Critério pareado → {paired}. "
        f"{'Coincidem.' if agree else 'Divergem.'}",
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    cfg = load_config(args.config)
    run = cfg["run_id"]

    ret = read_jsonl(result_path("retrieval", f"{run}.jsonl"))
    stage_rows = ret + [r for gen in cfg["generation"]["generators"]
                        for r in read_jsonl(result_path("generation", f"{run}_{gen}.jsonl"))]
    stage_rows += [r for name in cfg["evaluation"]["configs"]
                   for r in read_jsonl(result_path("evaluation", f"{run}_{name}.jsonl"))]
    commits = sorted({r.get("code_commit", "não registrado") for r in stage_rows})
    lines = [f"# Resumo numérico — {run}\n",
             "Gerado por `src/analyze.py` a partir dos arquivos salvos. Não indica qual "
             "gerador é melhor.\n",
             f"- Commit do código usado nas etapas: {', '.join(f'`{c}`' for c in commits)}.\n",
             "## Recuperação e geração\n"]
    if ret:
        lines.append(f"- Perguntas: {len(ret)}; trechos indexados: {ret[0]['n_chunks_indexed']}; "
                     f"recuperação com trecho da própria página: "
                     f"{sum(r['same_page_hit'] for r in ret)}/{len(ret)}.")
    refused = set()
    for gen in cfg["generation"]["generators"]:
        g = pd.DataFrame(read_jsonl(result_path("generation", f"{run}_{gen}.jsonl")))
        if g.empty:
            continue
        ref = g[g["answer"].map(is_refusal)]
        refused |= {(q, gen) for q in ref["qid"]}
        short = g[~g["answer"].map(is_refusal) & (g["answer"].str.len() < 150)]
        tokens = g["usage"].map(lambda u: (u or {}).get("output_tokens") or 0)
        lines.append(f"- Gerador {gen} ({g['model'].iloc[0]}): {len(g)} respostas; tempo "
                     f"mediano {g['elapsed_s'].median():.1f}s (total {g['elapsed_s'].sum() / 60:.1f} min); "
                     f"tokens de saída medianos {int(tokens.median())}; finish_reason "
                     f"{g['finish_reason'].value_counts().to_dict()}.")
        lines.append(f"  - Recusas explícitas: {len(ref)}/{len(g)} (qids {ref['qid'].tolist()}); "
                     f"respostas curtas (< 150 caracteres) não classificadas como recusa, para "
                     f"conferência manual: {dict(zip(short['qid'], short['answer']))}.")
    refused_q = sorted({q for q, _ in refused})
    lines.append(f"- Perguntas com recusa de algum gerador (pares fora da Faithfulness): "
                 f"{len(refused_q)} {refused_q}.")

    for name in cfg["evaluation"]["configs"]:
        rows = read_jsonl(result_path("evaluation", f"{run}_{name}.jsonl"))
        errors = read_jsonl(result_path("evaluation", f"{run}_{name}_errors.jsonl"))
        if rows:
            analyze_config(cfg, name, rows, errors, refused, lines)

    out = result_path("analysis", f"{run}_summary.md")
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
