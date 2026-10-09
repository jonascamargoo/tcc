# Resumo numérico — pilot_v1

Gerado por `src/analyze.py` a partir dos arquivos salvos. Não indica qual gerador é melhor.

- Commit do código usado nas etapas: `8ab080bdee77`.

## Recuperação e geração

- Perguntas: 10; trechos indexados: 423; recuperação com trecho da própria página: 10/10.
- Gerador proprietary (gemini-3.8-flash): 4 respostas; tempo mediano 112.8s (total 8.1 min); tokens de saída medianos 77; finish_reason {'stop': 4}.
- Gerador open (llama3.1:8b-instruct-q8_0): 10 respostas; tempo mediano 2.6s (total 0.5 min); tokens de saída medianos 64; finish_reason {'stop': 10}.

## Configuração do juiz: `default`

- Avaliações salvas: 70 (K=5); erros registrados: 0.
- Parâmetros efetivamente enviados: temperature [0.01], top_p [0.1], seed [1, 2, 3, 4, 5], max_tokens [4096].
- Chamadas HTTP ao juiz: 140 (2.00 por avaliação; 0 avaliações com mais de 2); status ≠ 200: 0; finish_reason: {'stop': 140}.
- Evidência de ausência de cache: duração mínima por chamada 4.5s; tokens gerados por chamada: mín. 68, máx. 796 (limite max_tokens 4096); tokens de prompt máx. 2062 (contexto 8192).
- Tempo por avaliação: mediana 27.6s, total 37.0 min.
- Saturação: 100% das notas = 1,0; notas NaN: 0.
- Respostas cujas afirmações variam entre as repetições: 0/14; cujos veredictos variam: 0/14.

**Experimento 1 — variação do juiz**

| Grupo | DP mediano | DP médio | DP P90 | CV mediano |
|---|---|---|---|---|
| proprietary | 0.000 | 0.000 | 0.000 | 0.000 |
| open | 0.000 | 0.000 | 0.000 | 0.000 |
| total | 0.000 | 0.000 | 0.000 | 0.000 |

- Respostas com DP > 0: 0/14.
- Avaliação única por j (vencedor geral): ['tie', 'tie', 'tie', 'tie', 'tie']; proporção de j com vencedor diferente do modal: 0.00.
- Proporção de perguntas cujo vencedor muda entre repetições: 0.00.
- DP mediano com j=1..3: 0.000 vs com j=1..5: 0.000.

**Experimento 2 — critério pareado** (só valida o código no piloto; n pequeno)

- Pares: 4; perguntas sem resposta de um dos geradores: 6; excluídos por NaN: 0; d = 0: 4 (zero_method=wilcox).
- d mediana 0.000, d média 0.000; W=—, p=—, Z=—, r=—.
- Comparação direta: média proprietário 1.000 vs aberto 1.000 → tie. Critério pareado → no significant difference. Coincidem.

## Configuração do juiz: `t1`

- Avaliações salvas: 70 (K=5); erros registrados: 0.
- Parâmetros efetivamente enviados: temperature [1.0], top_p [1.0], seed [1, 2, 3, 4, 5], max_tokens [4096].
- Chamadas HTTP ao juiz: 141 (2.01 por avaliação; 1 avaliações com mais de 2); status ≠ 200: 0; finish_reason: {'stop': 141}.
- Evidência de ausência de cache: duração mínima por chamada 4.5s; tokens gerados por chamada: mín. 67, máx. 813 (limite max_tokens 4096); tokens de prompt máx. 2439 (contexto 8192).
- Tempo por avaliação: mediana 32.3s, total 39.8 min.
- Saturação: 91% das notas = 1,0; notas NaN: 0.
- Respostas cujas afirmações variam entre as repetições: 13/14; cujos veredictos variam: 11/14.

**Experimento 1 — variação do juiz**

| Grupo | DP mediano | DP médio | DP P90 | CV mediano |
|---|---|---|---|---|
| proprietary | 0.023 | 0.079 | 0.202 | 0.024 |
| open | 0.000 | 0.023 | 0.089 | 0.000 |
| total | 0.000 | 0.039 | 0.089 | 0.000 |

- Respostas com DP > 0: 5/14.
- Avaliação única por j (vencedor geral): ['tie', 'open', 'open', 'tie', 'open']; proporção de j com vencedor diferente do modal: 0.40.
- Proporção de perguntas cujo vencedor muda entre repetições: 0.50.
- DP mediano com j=1..3: 0.000 vs com j=1..5: 0.000.

**Experimento 2 — critério pareado** (só valida o código no piloto; n pequeno)

- Pares: 4; perguntas sem resposta de um dos geradores: 6; excluídos por NaN: 0; d = 0: 2 (zero_method=wilcox).
- d mediana -0.017, d média -0.038; W=0.0, p=0.500, Z=-1.342, r=0.949.
- Comparação direta: média proprietário 0.962 vs aberto 1.000 → open. Critério pareado → no significant difference. Divergem.
