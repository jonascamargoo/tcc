# Teste de viabilidade da base — base_test_v1

**Este é um teste de viabilidade da base de dados, não parte do experimento final.** Apenas o gerador aberto foi usado; nada aqui compara geradores.

- Commit do código usado nas etapas: `31d0a1455b8f`.
- Base: `galileo-ai/ragbench` / `expertqa` / `test` (revisão `97808f3e5fd1`).
- Perguntas: 10 (seed 42): [6, 26, 28, 35, 57, 62, 70, 163, 188, 189].
- Recuperação: 2775 trechos indexados; trecho da própria pergunta em 10/10; indexação 12s.
- Geração (open, llama3.1:8b-instruct-q8_0): 10 respostas; caracteres medianos 722 (mín 167, máx 1365); tempo total 47s; finish_reason {'stop': 10}.

## Juiz `default`

- Avaliações: 50; erros registrados: 0.
- **Notas = 1,0: 20/50 (40%)**; no pilot_v1: 70/70 (100%) no total, 50/50 (100%) só com o gerador aberto.
- Distribuição das notas: mín 0.333; P10 0.433; P25 0.500; mediana 0.607; P75 1.000; P90 1.000; máx 1.000; média 0.699.
- Afirmações por avaliação: média 7.2, mediana 6 (mín 3, máx 16); no pilot_v1 (aberto): média 4.9.
- Notas NaN: 0.
- Respostas com DP > 0 entre as 5 repetições: 0/10; DP mediano 0.000, DP máximo 0.000.
- Tempo: total 35.4 min; por avaliação mediana 38.3s (máx 85.9s).
- Chamadas ao juiz: 100 (2.00 por avaliação); finish_reason {'stop': 100}; tokens de prompt máx 1983, tokens gerados máx 960.

## Juiz `t1`

- Avaliações: 50; erros registrados: 0.
- **Notas = 1,0: 25/50 (50%)**; no pilot_v1: 64/70 (91%) no total, 47/50 (94%) só com o gerador aberto.
- Distribuição das notas: mín 0.000; P10 0.393; P25 0.500; mediana 0.955; P75 1.000; P90 1.000; máx 1.000; média 0.754.
- Afirmações por avaliação: média 7.3, mediana 7 (mín 3, máx 17); no pilot_v1 (aberto): média 5.0.
- Notas NaN: 0.
- Respostas com DP > 0 entre as 5 repetições: 8/10; DP mediano 0.192, DP máximo 0.271.
- Tempo: total 36.7 min; por avaliação mediana 43.5s (máx 82.3s).
- Chamadas ao juiz: 100 (2.00 por avaliação); finish_reason {'stop': 100}; tokens de prompt máx 2149, tokens gerados máx 948.

## Notas manuais (adicionadas após a execução; não são geradas pelo script)

**Ruído nos documentos** (usados sem limpeza, como combinado):
1. Trechos que são **apenas uma URL** ocupam lugares no top-4 da recuperação. Exemplos: `p25-c4` = `https://blog.partsbase.com/what-materials-are-used-in-aircraft-construction/` (recuperado para a qid 26, de outra pergunta) e `p35-c0` = `https://www.ilobby.com/blog/measure-warehouse-performance` (qid 35).
2. **Cabeçalhos e nomes de site** misturados ao texto, além de espelhos da Wikipédia com marcadores de citação. Exemplos: "Business Women of Missouri | 2016 October…", "Melbourne Boasts World's Tallest Wooden Building - Ironfish Chinese…", `wikibedia.ru` e `wikipedia.moesalih.com` com "[15]", "[48]", "[93]".
3. **Documentos que começam no meio de uma frase** (são recortes de páginas). Exemplo: "a serious safety hazard. In the 1990s, Dr. Mike Zaworotko…" (qid 6).

**Outras observações de adaptação:**
- Uma "página" (os documentos de uma pergunta juntados) chega a 109 mil caracteres. A mediana é ~3,9 mil.
- Um par de perguntas do split tem documentos idênticos.
- O índice passou de 423 trechos (WikiEval) para 2.775.
- O maior número de tokens gerados numa chamada do juiz foi 960, perto do antigo limite de 1024. Isso confirma a utilidade do `max_tokens=4096`.

**Recusa parcial do gerador (qid 188):** o Llama respondeu "I cannot answer that question. However, I can suggest some general guidelines… Would that help?". O juiz extraiu de 3 a 5 afirmações sobre "o assistente" ou "o usuário", **sem gerar NaN**. Em `t1` as notas variaram de 0,0 a 0,67 entre as repetições. Em `default` a nota foi 0,333 nas 5. Recusas tendem a não virar NaN com este juiz e podem produzir notas instáveis.

**Referências da base:**
- Friel, R.; Belyi, M.; Sanyal, A. *RAGBench: Explainable Benchmark for Retrieval-Augmented Generation Systems*. arXiv:2407.11005, 2024. Dados: `galileo-ai/ragbench` (antes `rungalileo/ragbench`), licença CC-BY-4.0.
- Malaviya, C.; Lee, S.; Chen, S.; Sieber, E.; Yatskar, M.; Roth, D. *ExpertQA: Expert-Curated Questions and Attributed Answers*. NAACL 2024. arXiv:2309.07852.
