# Resumo numérico — pilot_v2

Gerado por `src/analyze.py` a partir dos arquivos salvos. Não indica qual gerador é melhor.

- Commit do código usado nas etapas: `56957a6d062a`.

## Recuperação e geração

- Perguntas: 10; trechos indexados: 2775; recuperação com trecho da própria página: 10/10.
- Gerador proprietary (gemini-3.8-flash): 10 respostas; tempo mediano 4.7s (total 1.0 min); tokens de saída medianos 8; finish_reason {'stop': 10}.
  - Recusas explícitas: 6/10 (qids [6, 26, 57, 62, 188, 189]); respostas curtas (< 150 caracteres) não classificadas como recusa, para conferência manual: {}.
- Gerador open (llama3.1:8b-instruct-q8_0): 10 respostas; tempo mediano 4.9s (total 0.8 min); tokens de saída medianos 137; finish_reason {'stop': 10}.
  - Recusas explícitas: 2/10 (qids [188, 189]); respostas curtas (< 150 caracteres) não classificadas como recusa, para conferência manual: {}.
- Perguntas com recusa de algum gerador (pares fora da Faithfulness): 6 [6, 26, 57, 62, 188, 189].

## Configuração do juiz: `default`

- Avaliações salvas: 100 (K=5); erros registrados: 0; avaliações de recusas, fora das análises: 40 (notas dadas pelo juiz: {0.0: 30, 0.3333333333333333: 5, 0.5: 5}).
- Parâmetros efetivamente enviados: temperature [0.01], top_p [0.1], seed [1, 2, 3, 4, 5], max_tokens [4096].
- Chamadas HTTP ao juiz: 200 (2.00 por avaliação; 0 avaliações com mais de 2); status ≠ 200: 0; finish_reason: {'stop': 200}.
- Evidência de ausência de cache: duração mínima por chamada 1.2s; tokens gerados por chamada: mín. 23, máx. 960 (limite max_tokens 4096); tokens de prompt máx. 1983 (contexto 8192).
- Tempo por avaliação: mediana 25.9s, total 44.7 min.
- Saturação (sem recusas): 67% das notas = 1,0; notas NaN: 0.
- Respostas cujas afirmações variam entre as repetições: 0/12; cujos veredictos variam: 0/12.

**Experimento 1 — variação do juiz**

| Grupo | DP mediano | DP médio | DP P90 | CV mediano |
|---|---|---|---|---|
| proprietary | 0.000 | 0.000 | 0.000 | 0.000 |
| open | 0.000 | 0.000 | 0.000 | 0.000 |
| total | 0.000 | 0.000 | 0.000 | 0.000 |

- Respostas com DP > 0: 0/12.
- Avaliação única por j (vencedor geral): ['tie', 'tie', 'tie', 'tie', 'tie']; proporção de j com vencedor diferente do modal: 0.00.
- Proporção de perguntas cujo vencedor muda entre repetições: 0.00.
- DP mediano com j=1..3: 0.000 vs com j=1..5: 0.000.

**Experimento 2 — critério pareado** (só valida o código no piloto; n pequeno)

- Pares: 4; perguntas sem resposta de um dos geradores: 0; excluídos por recusa: 6; excluídos por NaN: 0; d = 0: 4 (zero_method=wilcox).
- d mediana 0.000, d média 0.000; W=—, p=—, Z=—, r=—.
- Comparação direta: média proprietário 1.000 vs aberto 1.000 → tie. Critério pareado → no significant difference. Coincidem.

## Configuração do juiz: `t1`

- Avaliações salvas: 100 (K=5); erros registrados: 0; avaliações de recusas, fora das análises: 40 (notas dadas pelo juiz: {0.0: 29, 0.25: 1, 0.3333333333333333: 1, 0.6: 2, 0.625: 1, 0.6666666666666666: 1, 1.0: 5}).
- Parâmetros efetivamente enviados: temperature [1.0], top_p [1.0], seed [1, 2, 3, 4, 5], max_tokens [4096].
- Chamadas HTTP ao juiz: 200 (2.00 por avaliação; 0 avaliações com mais de 2); status ≠ 200: 0; finish_reason: {'stop': 200}.
- Evidência de ausência de cache: duração mínima por chamada 1.3s; tokens gerados por chamada: mín. 21, máx. 1180 (limite max_tokens 4096); tokens de prompt máx. 2149 (contexto 8192).
- Tempo por avaliação: mediana 27.2s, total 49.1 min.
- Saturação (sem recusas): 65% das notas = 1,0; notas NaN: 0.
- Respostas cujas afirmações variam entre as repetições: 12/12; cujos veredictos variam: 11/12.

**Experimento 1 — variação do juiz**

| Grupo | DP mediano | DP médio | DP P90 | CV mediano |
|---|---|---|---|---|
| proprietary | 0.037 | 0.048 | 0.105 | 0.039 |
| open | 0.149 | 0.133 | 0.247 | 0.228 |
| total | 0.096 | 0.104 | 0.242 | 0.103 |

- Respostas com DP > 0: 8/12.
- Avaliação única por j (vencedor geral): ['tie', 'proprietary', 'open', 'open', 'proprietary']; proporção de j com vencedor diferente do modal: 0.60.
- Proporção de perguntas cujo vencedor muda entre repetições: 0.75.
- DP mediano com j=1..3: 0.000 vs com j=1..5: 0.096.

**Experimento 2 — critério pareado** (só valida o código no piloto; n pequeno)

- Pares: 4; perguntas sem resposta de um dos geradores: 0; excluídos por recusa: 6; excluídos por NaN: 0; d = 0: 1 (zero_method=wilcox).
- d mediana 0.008, d média 0.000; W=3.0, p=1.000, Z=-0.000, r=0.000.
- Comparação direta: média proprietário 0.971 vs aberto 0.970 → proprietary. Critério pareado → no significant difference. Divergem.
