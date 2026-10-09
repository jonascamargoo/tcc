# Resumo numérico — pilot_v2

Gerado por `src/analyze.py` a partir dos arquivos salvos. Não indica qual gerador é melhor.

- Commit do código usado nas etapas: `56957a6d062a`.

## Recuperação e geração

- Perguntas: 10; trechos indexados: 2775; recuperação com trecho da própria página: 10/10.
- Gerador proprietary (gemini-3.8-flash): 10 respostas; tempo mediano 4.7s (total 1.0 min); tokens de saída medianos 8; finish_reason {'stop': 10}.
- Gerador open (llama3.1:8b-instruct-q8_0): 10 respostas; tempo mediano 4.9s (total 0.8 min); tokens de saída medianos 137; finish_reason {'stop': 10}.

## Configuração do juiz: `default`

- Avaliações salvas: 100 (K=5); erros registrados: 0.
- Parâmetros efetivamente enviados: temperature [0.01], top_p [0.1], seed [1, 2, 3, 4, 5], max_tokens [4096].
- Chamadas HTTP ao juiz: 200 (2.00 por avaliação; 0 avaliações com mais de 2); status ≠ 200: 0; finish_reason: {'stop': 200}.
- Evidência de ausência de cache: duração mínima por chamada 1.2s; tokens gerados por chamada: mín. 23, máx. 960 (limite max_tokens 4096); tokens de prompt máx. 1983 (contexto 8192).
- Tempo por avaliação: mediana 25.9s, total 44.7 min.
- Saturação: 40% das notas = 1,0; notas NaN: 0.
- Respostas cujas afirmações variam entre as repetições: 0/20; cujos veredictos variam: 0/20.

**Experimento 1 — variação do juiz**

| Grupo | DP mediano | DP médio | DP P90 | CV mediano |
|---|---|---|---|---|
| proprietary | 0.000 | 0.000 | 0.000 | 0.000 |
| open | 0.000 | 0.000 | 0.000 | 0.000 |
| total | 0.000 | 0.000 | 0.000 | 0.000 |

- Respostas com DP > 0: 0/20.
- Avaliação única por j (vencedor geral): ['open', 'open', 'open', 'open', 'open']; proporção de j com vencedor diferente do modal: 0.00.
- Proporção de perguntas cujo vencedor muda entre repetições: 0.00.
- DP mediano com j=1..3: 0.000 vs com j=1..5: 0.000.

**Experimento 2 — critério pareado** (só valida o código no piloto; n pequeno)

- Pares: 10; perguntas sem resposta de um dos geradores: 0; excluídos por NaN: 0; d = 0: 4 (zero_method=wilcox).
- d mediana -0.389, d média -0.299; W=0.0, p=0.031, Z=-2.226, r=0.909.
- Comparação direta: média proprietário 0.400 vs aberto 0.699 → open. Critério pareado → open. Coincidem.

## Configuração do juiz: `t1`

- Avaliações salvas: 100 (K=5); erros registrados: 0.
- Parâmetros efetivamente enviados: temperature [1.0], top_p [1.0], seed [1, 2, 3, 4, 5], max_tokens [4096].
- Chamadas HTTP ao juiz: 200 (2.00 por avaliação; 0 avaliações com mais de 2); status ≠ 200: 0; finish_reason: {'stop': 200}.
- Evidência de ausência de cache: duração mínima por chamada 1.3s; tokens gerados por chamada: mín. 21, máx. 1180 (limite max_tokens 4096); tokens de prompt máx. 2149 (contexto 8192).
- Tempo por avaliação: mediana 27.2s, total 49.1 min.
- Saturação: 44% das notas = 1,0; notas NaN: 0.
- Respostas cujas afirmações variam entre as repetições: 20/20; cujos veredictos variam: 18/20.

**Experimento 1 — variação do juiz**

| Grupo | DP mediano | DP médio | DP P90 | CV mediano |
|---|---|---|---|---|
| proprietary | 0.000 | 0.109 | 0.447 | 0.103 |
| open | 0.192 | 0.154 | 0.257 | 0.250 |
| total | 0.096 | 0.132 | 0.289 | 0.228 |

- Respostas com DP > 0: 12/20.
- Avaliação única por j (vencedor geral): ['open', 'open', 'open', 'open', 'open']; proporção de j com vencedor diferente do modal: 0.00.
- Proporção de perguntas cujo vencedor muda entre repetições: 0.60.
- DP mediano com j=1..3: 0.000 vs com j=1..5: 0.096.

**Experimento 2 — critério pareado** (só valida o código no piloto; n pequeno)

- Pares: 10; perguntas sem resposta de um dos geradores: 0; excluídos por NaN: 0; d = 0: 1 (zero_method=wilcox).
- d mediana -0.379, d média -0.325; W=3.0, p=0.020, Z=-2.310, r=0.770.
- Comparação direta: média proprietário 0.428 vs aberto 0.754 → open. Critério pareado → open. Coincidem.
