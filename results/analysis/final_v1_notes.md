# Notas manuais — final_v1

Complementa `final_v1_summary.md` (gerado por `src/analyze.py`, commit `ce59df0` + seguinte). Não conclui qual gerador é melhor.

## Conferência da regra de recusa (CLAUDE.md 6.1)
- Amostra: 20 das 196 respostas classificadas como recusa (`final_v1_refusal_sample.md`, seed 42).
- 20/20 são recusas declaradas na primeira frase, sem conteúdo sobre a pergunta (precisão observada 20/20; conferência feita pelo Claude, a confirmar pelo autor).
- Tipos: "I cannot answer based on the context." (todas as 10 do Gemini); recusas do Llama por falta de contexto (176, 195, 116, 33, 67) e recusas de política/segurança (34, 41, 27, 9: informação, opinião, decisão de saúde, conselho médico).
- A precisão não mede a cobertura (respostas que recusam sem casar o padrão); as respostas curtas não classificadas estão listadas no resumo.

## Falhas de formato do juiz (`t1`)
- 8 avaliações sem nota válida após a nova tentativa; 5 delas em pares sem recusa (lista no resumo). `default`: nenhuma.
- Causas: JSON com chave faltando ou com nome errado (ex.: `verduct`, `Statements`) e uma interrupção por repetição de tokens no Ollama (qid 108).
- A nova tentativa reproduziu as 8 falhas: com seed = j e os mesmos parâmetros, a saída do juiz tende a se repetir.
- O qid 24 (open, j=3) já tinha falhado duas vezes antes; não houve terceira tentativa (`--max-failures 2` em `src/evaluate.py`).

## Registro operacional
- Execução: 2026-10-05 a 2026-10-07, com uma pausa a pedido do autor (2026-10-06 16:56–18:24) e um reinício da máquina; os arquivos foram verificados e a execução retomou do ponto salvo.
- A primeira nova tentativa (12:19 de 2026-10-07) não chegou a avaliar nada: o servidor do Ollama tinha sido encerrado junto com o driver (conexão recusada). A nova tentativa válida rodou às 12:20.
