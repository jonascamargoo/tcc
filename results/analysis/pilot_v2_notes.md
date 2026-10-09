# Notas manuais — pilot_v2

Complementa `pilot_v2_summary.md` (gerado por `src/analyze.py`, commit `56957a6`). Piloto: não conclui qual gerador é melhor.

## Recusas do gerador proprietário
- O Gemini respondeu "I cannot answer based on the context." (texto exato da instrução do prompt) em 6/10 perguntas: qids 6, 26, 57, 62, 188, 189.
- O juiz não devolveu NaN para as recusas. Ele extraiu 1 ou 2 afirmações do tipo "The answer cannot be provided based on the context." e as julgou não sustentadas.
  - `default`: as 30 avaliações de recusas (6 × 5) deram nota 0,0.
  - `t1`: 28 deram 0,0 e 2 deram 1,0 (qid 26 j=3; qid 189 j=3).
- O Llama respondeu às 6 com notas médias entre 0,33 e 0,71 no `default`. Nas qids 57 e 62, os trechos recuperados tratam do tema, mas não respondem diretamente à pergunta, que é aberta ou de opinião. A resposta do Llama mistura o contexto com conhecimento próprio.
- Nas 4 perguntas que os dois responderam (28, 35, 70, 163), as médias foram 1,000 vs 1,000 no `default` e 0,971 vs 0,970 no `t1`.
- Portanto, a diferença observada no Wilcoxon e nas médias vem inteiramente das recusas.

## Outros registros
- As respostas do Llama foram idênticas às do `base_test_v1` em 10/10 (seed 0), o que confirma a reprodutibilidade da geração local.
- Gemini: 8 respostas HTTP 503 antes das 10 respostas válidas, cerca de 18 requisições no dia (limite de 20).

## Regra de recusa aplicada (commit seguinte a 56957a6)
- O `pilot_v2_summary.md` foi gerado de novo com a regra de recusa (CLAUDE.md 6.1). A versão anterior, sem a regra, está em `pilot_v2_sem_regra_recusa/`.
- Restaram 4 pares. No `t1`, a comparação direta (0,971 vs 0,970) e o critério pareado (p = 1,0) divergem. Com n = 4, isso só valida o código.
