# Resumo numérico — smoke_v1

Gerado por `src/analyze.py` a partir dos arquivos salvos. Não indica qual gerador é melhor.

- Commit do código usado nas etapas: `não registrado`.

## Recuperação e geração

- Perguntas: 1; trechos indexados: 423; recuperação com trecho da própria página: 1/1.
- Gerador proprietary (gemini-3.8-flash): 1 respostas; tempo mediano 31.3s (total 0.5 min); tokens de saída medianos 132; finish_reason {'stop': 1}.
- Gerador open (llama3.1:8b-instruct-q8_0): 1 respostas; tempo mediano 7.5s (total 0.1 min); tokens de saída medianos 85; finish_reason {'stop': 1}.

## Configuração do juiz: `default`

- Avaliações salvas: 4 (K=2); erros registrados: 0.
- Parâmetros efetivamente enviados: temperature [0.01], top_p [0.1], seed [1, 2], max_tokens [1024].
- Chamadas HTTP ao juiz: 8 (2.00 por avaliação; 0 avaliações com mais de 2); status ≠ 200: 0; finish_reason: {'stop': 8}.
- Evidência de ausência de cache: duração mínima por chamada 7.9s; tokens gerados por chamada: mín. 145, máx. 436 (limite max_tokens 1024); tokens de prompt máx. 1933 (contexto 8192).
- Tempo por avaliação: mediana 31.7s, total 2.3 min.
- Saturação: 100% das notas = 1,0; notas NaN: 0.
- Respostas cujas afirmações variam entre as repetições: 0/2; cujos veredictos variam: 0/2.

**Experimento 1 — variação do juiz**

| Grupo | DP mediano | DP médio | DP P90 | CV mediano |
|---|---|---|---|---|
| proprietary | 0.000 | 0.000 | 0.000 | 0.000 |
| open | 0.000 | 0.000 | 0.000 | 0.000 |
| total | 0.000 | 0.000 | 0.000 | 0.000 |

- Respostas com DP > 0: 0/2.
- Avaliação única por j (vencedor geral): ['tie', 'tie']; proporção de j com vencedor diferente do modal: 0.00.
- Proporção de perguntas cujo vencedor muda entre repetições: 0.00.

**Experimento 2 — critério pareado** (só valida o código no piloto; n pequeno)

- Pares: 1; excluídos por NaN: 0; d = 0: 1 (zero_method=wilcox).
- d mediana 0.000, d média 0.000; W=—, p=—, Z=—, r=—.
- Comparação direta: média proprietário 1.000 vs aberto 1.000 → tie. Critério pareado → no significant difference. Coincidem.

## Configuração do juiz: `t1`

- Avaliações salvas: 4 (K=2); erros registrados: 0.
- Parâmetros efetivamente enviados: temperature [1.0], top_p [1.0], seed [1, 2], max_tokens [1024].
- Chamadas HTTP ao juiz: 8 (2.00 por avaliação; 0 avaliações com mais de 2); status ≠ 200: 0; finish_reason: {'stop': 8}.
- Evidência de ausência de cache: duração mínima por chamada 9.0s; tokens gerados por chamada: mín. 156, máx. 426 (limite max_tokens 1024); tokens de prompt máx. 1933 (contexto 8192).
- Tempo por avaliação: mediana 37.7s, total 2.5 min.
- Saturação: 100% das notas = 1,0; notas NaN: 0.
- Respostas cujas afirmações variam entre as repetições: 2/2; cujos veredictos variam: 0/2.

**Experimento 1 — variação do juiz**

| Grupo | DP mediano | DP médio | DP P90 | CV mediano |
|---|---|---|---|---|
| proprietary | 0.000 | 0.000 | 0.000 | 0.000 |
| open | 0.000 | 0.000 | 0.000 | 0.000 |
| total | 0.000 | 0.000 | 0.000 | 0.000 |

- Respostas com DP > 0: 0/2.
- Avaliação única por j (vencedor geral): ['tie', 'tie']; proporção de j com vencedor diferente do modal: 0.00.
- Proporção de perguntas cujo vencedor muda entre repetições: 0.00.

**Experimento 2 — critério pareado** (só valida o código no piloto; n pequeno)

- Pares: 1; excluídos por NaN: 0; d = 0: 1 (zero_method=wilcox).
- d mediana 0.000, d média 0.000; W=—, p=—, Z=—, r=—.
- Comparação direta: média proprietário 1.000 vs aberto 1.000 → tie. Critério pareado → no significant difference. Coincidem.
