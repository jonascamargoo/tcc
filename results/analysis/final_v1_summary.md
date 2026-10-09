# Resumo numérico — final_v1

Gerado por `src/analyze.py` a partir dos arquivos salvos. Não indica qual gerador é melhor.

- Commit do código usado nas etapas: `26ab590f382a`, `367d60c1c761`, `72940f223939`.

## Recuperação e geração

- Perguntas: 203; trechos indexados: 2775; recuperação com trecho da própria página: 189/203.
- Gerador proprietary (gemini-3.8-flash): 203 respostas; tempo mediano 5.7s (total 21.8 min); tokens de saída medianos 8; finish_reason {'stop': 203}.
  - Recusas explícitas: 126/203 (qids [0, 3, 6, 8, 9, 11, 13, 14, 16, 17, 18, 21, 24, 25, 26, 30, 31, 33, 34, 37, 39, 40, 41, 42, 44, 45, 46, 47, 50, 51, 52, 53, 56, 57, 60, 61, 62, 63, 64, 66, 67, 68, 69, 73, 74, 75, 76, 77, 78, 79, 80, 82, 84, 85, 88, 90, 91, 95, 97, 98, 99, 101, 102, 103, 106, 111, 112, 113, 114, 116, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 130, 131, 134, 136, 140, 143, 145, 146, 148, 149, 152, 154, 155, 156, 157, 158, 159, 160, 162, 166, 167, 169, 171, 172, 173, 174, 175, 176, 178, 179, 180, 181, 182, 184, 185, 186, 188, 189, 190, 191, 192, 195, 197, 198, 199, 200]); respostas curtas (< 150 caracteres) não classificadas como recusa, para conferência manual: {2: 'Based on the provided context, plasma and urine catecholamine measurement can help detect and diagnose phaeochromocytomas.', 12: 'Based on the context, the **physiologic variant** (associated with normal growth and development) is the normal type of genu valgum.', 59: 'Based on the context, geoarchaeology solves archaeological problems by utilizing the methods of geological investigation.', 100: 'Based on the provided context, the Actual Oxygen Requirement is used to identify the oxygen demand for a system.'}.
- Gerador open (llama3.1:8b-instruct-q8_0): 203 respostas; tempo mediano 3.4s (total 14.5 min); tokens de saída medianos 84; finish_reason {'stop': 203}.
  - Recusas explícitas: 70/203 (qids [0, 3, 8, 9, 13, 17, 24, 27, 31, 33, 34, 37, 40, 41, 44, 46, 51, 56, 60, 61, 64, 66, 67, 68, 73, 78, 80, 84, 85, 86, 88, 91, 93, 95, 98, 106, 111, 113, 114, 116, 120, 123, 125, 127, 128, 134, 140, 143, 145, 148, 154, 156, 157, 158, 166, 167, 176, 178, 179, 180, 181, 185, 188, 189, 190, 191, 192, 195, 197, 200]); respostas curtas (< 150 caracteres) não classificadas como recusa, para conferência manual: {12: 'Based on the context, the type of genu valgum that is normal is a physiologic (normal growth and development) variant, which is the most common type.', 161: 'Remote sensors capture images from afar by detecting and recording reflected or emitted energy.', 175: 'According to context [1], Logistics, which includes Supply Chain Management, contributes over £127 billion to the UK economy.'}.
- Perguntas com recusa de algum gerador (pares fora da Faithfulness): 129 [0, 3, 6, 8, 9, 11, 13, 14, 16, 17, 18, 21, 24, 25, 26, 27, 30, 31, 33, 34, 37, 39, 40, 41, 42, 44, 45, 46, 47, 50, 51, 52, 53, 56, 57, 60, 61, 62, 63, 64, 66, 67, 68, 69, 73, 74, 75, 76, 77, 78, 79, 80, 82, 84, 85, 86, 88, 90, 91, 93, 95, 97, 98, 99, 101, 102, 103, 106, 111, 112, 113, 114, 116, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 130, 131, 134, 136, 140, 143, 145, 146, 148, 149, 152, 154, 155, 156, 157, 158, 159, 160, 162, 166, 167, 169, 171, 172, 173, 174, 175, 176, 178, 179, 180, 181, 182, 184, 185, 186, 188, 189, 190, 191, 192, 195, 197, 198, 199, 200].

## Configuração do juiz: `default`

- Falhas de formato do juiz (sem nota válida após nova tentativa): 0 avaliações []; 0 em pares sem recusa [].
- Avaliações salvas: 2030 (K=5); erros registrados: 0; avaliações de recusas, fora das análises: 980 (notas dadas pelo juiz: {0.0: 579, 0.16666666666666666: 5, 0.3333333333333333: 20, 0.4: 4, 0.5: 36, 0.6666666666666666: 40, 0.75: 15, 0.8: 6, 0.8333333333333334: 5, 0.8571428571428571: 5, 1.0: 265}).
- Parâmetros efetivamente enviados: temperature [0.01], top_p [0.1], seed [1, 2, 3, 4, 5], max_tokens [4096].
- Chamadas HTTP ao juiz: 4060 (2.00 por avaliação; 0 avaliações com mais de 2); status ≠ 200: 0; finish_reason: {'stop': 4060}.
- Evidência de ausência de cache: duração mínima por chamada 1.3s; tokens gerados por chamada: mín. 23, máx. 2733 (limite max_tokens 4096); tokens de prompt máx. 2627 (contexto 8192).
- Tempo por avaliação: mediana 21.4s, total 1078.3 min.
- Saturação (sem recusas): 66% das notas = 1,0; notas NaN: 0.
- Respostas cujas afirmações variam entre as repetições: 2/210; cujos veredictos variam: 1/210.

**Experimento 1 — variação do juiz**

| Grupo | DP mediano | DP médio | DP P90 | CV mediano |
|---|---|---|---|---|
| proprietary | 0.000 | 0.000 | 0.000 | 0.000 |
| open | 0.000 | 0.001 | 0.000 | 0.000 |
| total | 0.000 | 0.001 | 0.000 | 0.000 |

- Respostas com DP > 0: 1/210.
- Avaliação única por j (vencedor geral): ['proprietary', 'proprietary', 'proprietary', 'proprietary', 'proprietary']; proporção de j com vencedor diferente do modal: 0.00.
- Proporção de perguntas cujo vencedor muda entre repetições: 0.01.
- DP mediano com j=1..3: 0.000 vs com j=1..5: 0.000.

**Experimento 2 — critério pareado**

- Pares: 74; perguntas sem resposta de um dos geradores: 0; excluídos por recusa: 129; excluídos por NaN: 0; d = 0: 47 (zero_method=wilcox).
- d mediana 0.000, d média 0.031; W=84.0, p=0.012, Z=-2.524, r=0.486.
- Comparação direta: média proprietário 0.984 vs aberto 0.953 → proprietary. Critério pareado → proprietary. Coincidem.

## Configuração do juiz: `t1`

- Falhas de formato do juiz (sem nota válida após nova tentativa): 8 avaliações [(24, 'open', 3), (108, 'proprietary', 4), (115, 'open', 3), (115, 'proprietary', 3), (150, 'open', 3), (166, 'proprietary', 1), (184, 'open', 1), (193, 'open', 3)]; 5 em pares sem recusa [(108, 'proprietary', 4), (115, 'open', 3), (115, 'proprietary', 3), (150, 'open', 3), (193, 'open', 3)].
- Avaliações salvas: 2022 (K=5); erros registrados: 16; avaliações de recusas, fora das análises: 978 (notas dadas pelo juiz: {0.0: 539, 0.2: 2, 0.25: 13, 0.3333333333333333: 35, 0.4: 2, 0.5: 80, 0.5714285714285714: 1, 0.6: 8, 0.625: 1, 0.6666666666666666: 46, 0.7: 1, 0.7142857142857143: 1, 0.75: 16, 0.8: 9, 0.8333333333333334: 5, 0.8571428571428571: 6, 1.0: 213}).
- Parâmetros efetivamente enviados: temperature [1.0], top_p [1.0], seed [1, 2, 3, 4, 5], max_tokens [4096].
- Chamadas HTTP ao juiz: 4077 (2.02 por avaliação; 29 avaliações com mais de 2); status ≠ 200: 0; finish_reason: {'stop': 4077}.
- Evidência de ausência de cache: duração mínima por chamada 0.6s; tokens gerados por chamada: mín. 4, máx. 2640 (limite max_tokens 4096); tokens de prompt máx. 3327 (contexto 8192).
- Tempo por avaliação: mediana 23.0s, total 1096.1 min.
- Saturação (sem recusas): 62% das notas = 1,0; notas NaN: 0.
- Respostas cujas afirmações variam entre as repetições: 210/210; cujos veredictos variam: 200/210.

**Experimento 1 — variação do juiz**

| Grupo | DP mediano | DP médio | DP P90 | CV mediano |
|---|---|---|---|---|
| proprietary | 0.025 | 0.036 | 0.080 | 0.028 |
| open | 0.079 | 0.095 | 0.224 | 0.093 |
| total | 0.053 | 0.073 | 0.193 | 0.057 |

- Respostas com DP > 0: 142/210.
- Avaliação única por j (vencedor geral): ['proprietary', 'proprietary', 'proprietary', 'proprietary', 'proprietary']; proporção de j com vencedor diferente do modal: 0.00.
- Proporção de perguntas cujo vencedor muda entre repetições: 0.77.
- DP mediano com j=1..3: 0.029 vs com j=1..5: 0.053.

**Experimento 2 — critério pareado**

- Pares: 74; perguntas sem resposta de um dos geradores: 0; excluídos por recusa: 129; excluídos por NaN: 0; d = 0: 13 (zero_method=wilcox).
- d mediana 0.017, d média 0.037; W=443.0, p=0.000, Z=-3.609, r=0.462.
- Comparação direta: média proprietário 0.973 vs aberto 0.936 → proprietary. Critério pareado → proprietary. Coincidem.
