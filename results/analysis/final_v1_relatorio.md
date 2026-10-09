# Relatório dos experimentos — TCC "Fidelidade ao contexto em pipelines RAG"

Relatório gerado em 2026-10-09 a partir dos arquivos salvos do experimento final (`run_id` `final_v1`). Autor do TCC: Jonas Camargo Junior (Engenharia de Computação, CEFET-MG, Campus Timóteo).

## 0. Instruções para quem for usar este relatório (IA assistente de escrita)

- Este documento serve de base para redigir a metodologia, os resultados e a discussão do TCC. Os números vêm de `results/analysis/final_v1_summary.md` e dos CSVs da mesma pasta.
- **O resultado principal do trabalho é o critério de comparação, não "qual gerador é melhor".** Os geradores são só o caso de aplicação. Não escreva que um gerador é superior ao outro.
- Use linguagem cautelosa ("tende a", "pode", "neste caso", "nas condições testadas"). Os resultados valem para um único juiz, uma única base e o subconjunto de 74 perguntas sem recusa.
- O bootstrap foi descartado por decisão explícita do autor e não deve ser sugerido.
- Os rótulos usados nos arquivos são `proprietary` (Gemini) e `open` (Llama).

## 1. Problema e objetivos

**Ideia central.** Alternativas de um pipeline RAG costumam ser comparadas pela média de uma métrica, e quem tem a maior média "vence". A *Faithfulness* do Ragas, porém, é calculada por um LLM-juiz estocástico, então a mesma resposta pode receber notas diferentes em avaliações repetidas. O trabalho verifica se um critério pareado leva a conclusões diferentes da comparação direta das médias. Esse critério considera a variação do juiz (K avaliações por resposta) e o pareamento das respostas por pergunta (teste de Wilcoxon).

**Objetivo geral.** Propor um critério de comparação dos resultados da métrica de fidelidade ao contexto obtidos por um gerador de pesos abertos e por um proprietário, no mesmo pipeline RAG, que vá além da comparação direta das médias.

**Objetivos específicos.**
1. Selecionar um gerador de pesos abertos e um proprietário para compor o mesmo pipeline RAG.
2. Mensurar a variação das notas de fidelidade entre avaliações repetidas de uma mesma resposta e o efeito dessa variação sobre a comparação direta das médias.
3. Aplicar o critério proposto e verificar se ele leva a conclusões diferentes das da comparação direta das médias.

## 2. Método (experimento final, congelado em 2026-10-05)

O princípio do desenho é que **apenas o gerador varia**. Dados, recuperação, prompt e juiz são fixos.

### 2.1 Dados
- **Base:** RAGBench, subconjunto ExpertQA, split de teste, com todas as 203 perguntas (`galileo-ai/ragbench`, revisão `97808f3e5fd1`, licença CC-BY-4.0).
  - Referências: Friel, Belyi e Sanyal, *RAGBench*, arXiv:2407.11005, 2024; Malaviya et al., *ExpertQA*, NAACL 2024, arXiv:2309.07852.
- **O que foi usado:** só as perguntas e os documentos de cada pergunta, juntados sem limpeza como "texto da página". As respostas e os rótulos do RAGBench não foram usados.
- Tudo está em inglês, o idioma original.

### 2.2 Pipeline RAG
- LangChain, em etapa única: uma recuperação e uma geração por pergunta.
- **Trechos:** `RecursiveCharacterTextSplitter` com 1000 caracteres e sobreposição de 200, num total de 2775 trechos indexados.
- **Busca:** embeddings `BAAI/bge-small-en-v1.5` (locais) em `InMemoryVectorStore`, com k = 4.
- O índice contém os documentos das 203 perguntas. Os documentos das outras perguntas funcionam como distratores. Em 189 das 203 perguntas, algum dos 4 trechos recuperados veio dos documentos da própria pergunta.
- **A recuperação foi feita uma única vez e salva.** Os dois geradores receberam exatamente os mesmos trechos.
- O prompt de geração é fixo, idêntico para os dois geradores e está no apêndice A.

### 2.3 Geradores (uma resposta por pergunta)
Cada gerador usa a amostragem recomendada pelo seu fornecedor (decisão do autor em 2026-10-02).

| | Proprietário | Pesos abertos |
|---|---|---|
| Modelo | `gemini-3.8-flash` (API, endpoint compatível com OpenAI) | Llama 3.1 8B Instruct, `llama3.1:8b-instruct-q8_0` (Ollama 0.35.0, local) |
| Amostragem | temperature 1.0 (padrão), top_p e top_k sem alteração, thinking `medium` (padrão) | temperature 0.6, top_p 0.9, seed 0, num_ctx 8192 |
| Fonte da recomendação | Google, *What's new in Gemini 3.5 Flash* e *Gemini 3 Developer Guide* ("strongly recommend keeping the temperature parameter at its default value of 1.0") | Meta, `llama-models/models/llama3/generation.py` e `generation_config.json` do modelo (0.6 / 0.9) |

- O Gemini com temperature 1.0 não é reproduzível, mas as análises leem as respostas salvas.
- O Llama é reprodutível: no piloto, as respostas com seed 0 saíram idênticas em duas execuções (10/10).
- As 3 primeiras respostas do Gemini vieram do free tier e as 200 restantes do tier pago, com o mesmo modelo e os mesmos parâmetros. O custo total foi de cerca de US$ 0,54.

### 2.4 Juiz e métrica
- **Métrica:** a `Faithfulness` do Ragas 0.4.3 (`ragas.metrics.collections`). O juiz decompõe a resposta em afirmações e emite um veredicto (sustentada ou não pelo contexto) para cada uma. A nota é a proporção de afirmações sustentadas. Cada avaliação faz 2 chamadas ao juiz.
- **Juiz:** Mistral Small 3.2 24B, `mistral-small3.2:24b-instruct-2506-q4_K_M`, local via Ollama 0.35.0 (digest `5a408ab55df5…`), com contexto do servidor fixado em 8192 tokens.
  - É de família diferente dos dois geradores, para reduzir o viés de autopreferência.
  - A versão Q8 não cabe na máquina (Apple M5 Pro, 24 GB).
- **Duas configurações de amostragem do juiz, reportadas lado a lado:**
  - `default`: o padrão do Ragas 0.4.3, temperature 0.01 e top_p 0.1, ou seja, quase determinístico. É o que um usuário do Ragas obtém sem mudar nada.
  - `t1`: temperature 1.0 e top_p 1.0, explícitos. Representa um juiz com amostragem plena, o padrão de muitas APIs; o próprio Ragas força temperature 1.0 em alguns modelos de raciocínio. Ela foi incluída porque o piloto mostrou que o `default` quase não varia.
  - Nas duas: `seed = j` na repetição j (j = 1..5) e `max_tokens` = 4096. O padrão do Ragas é 1024, o que truncaria as respostas com mais de ~11 afirmações e afetaria mais as respostas longas.
- **K = 5** avaliações por resposta e por configuração, sem cache. A ausência de cache foi verificada: nenhum cache configurado, 2 requisições HTTP distintas por avaliação, latência mínima de 0,6 s por chamada, e as afirmações extraídas variaram entre as repetições no `t1`.
- O Experimento 1 mede, portanto, a variação induzida pela amostragem de um juiz local, e não o não determinismo de um provedor de API.

### 2.5 Regras de análise (definidas antes de ver as notas do experimento final)
- **Recusas explícitas.**
  - Definição: a resposta começa declarando que não pode responder, fornecer ou verificar. O padrão regex é aplicado igualmente aos dois geradores (apêndice B).
  - Uma recusa não recebe nota de Faithfulness. O juiz transforma a recusa numa meta-afirmação ("the answer cannot be provided…") e tende a lhe dar 0, o que puniria a recusa como se fosse infidelidade.
  - Pares em que algum dos geradores recusou saem do Wilcoxon e da comparação direta. A taxa de recusa é reportada como desfecho separado.
  - Uma primeira versão da regra casava só a frase exata do prompt e era assimétrica: pegava as recusas do Gemini e nenhuma do Llama, que varia a redação. Ela foi revista antes de qualquer nota do experimento final ser vista.
- **Notas NaN** (nenhuma afirmação extraída): a nota da resposta é a média das repetições válidas. Se todas forem NaN, o par sai. Não houve nenhum NaN no experimento final.
- **Falha persistente do juiz** (JSON inválido depois das retentativas internas do Ragas): a avaliação é tentada de novo uma vez. Se falhar de novo, conta como repetição sem nota válida (mesma regra do NaN parcial) e é reportada como "falha de formato do juiz".
- **Experimento 1:**
  - DP amostral (ddof = 1) e CV das K notas de cada resposta.
  - Simulação da prática de avaliar uma única vez: para cada j, usa-se só a nota da repetição j. A partir dela verificam-se o vencedor geral pela média e o vencedor por pergunta.
  - DPs abaixo de 1e-9 são tratados como 0.
- **Experimento 2:**
  - A nota de cada resposta é a média das K notas, e d = nota do proprietário − nota do aberto.
  - Wilcoxon pareado bicaudal, α = 0,05 (`scipy.stats.wilcoxon`, `zero_method="wilcox"`, que descarta os d = 0).
  - Z pela aproximação normal; r = |Z|/√n, com n igual ao número de pares não nulos usados no teste. Escala: ~0,1 pequeno, ~0,3 médio, ≥0,5 grande.
  - A conclusão é contrastada com a comparação direta das médias simples.

## 3. Histórico do piloto (justifica as decisões acima)

- **`pilot_v1` (WikiEval, 10 perguntas):** saturação forte. 100% das notas foram 1,0 no juiz `default` e 91% no `t1`; nenhuma resposta variou no `default` (0/14) e 5/14 variaram no `t1`. Com tudo em 1,0, a comparação perde sentido, e por isso a base foi trocada.
- **`base_test_v1` (RAGBench–ExpertQA, só o Llama, 10 perguntas):** notas menos saturadas. No `default`, 0/10 respostas variaram; no `t1`, 8/10, com DP mediano de 0,19.
- **`pilot_v2` (ExpertQA, os dois geradores, 10 perguntas):**
  - O Gemini recusou 6 das 10 perguntas, e o juiz deu 0 a essas recusas (30/30 no `default`).
  - Sem uma regra de recusa, a diferença entre os geradores vinha inteiramente das recusas, e isso motivou a regra da seção 2.5.
- **Conclusão do piloto:** o `default` tende a ser praticamente determinístico, por isso a configuração `t1` foi mantida no experimento final. K = 5 foi mantido porque o juiz não estava no caminho crítico da execução.

## 4. Execução

- **Período:** de 2026-10-05 a 2026-10-07.
- **Interrupções:** uma pausa a pedido do autor e um reinício da máquina. Em ambos os casos a execução foi retomada a partir dos arquivos salvos, sem refazer nada.
- **Geração:** Gemini com tempo mediano de 5,7 s por resposta (total de 21,8 min, com um erro 503); Llama com 3,4 s por resposta (total de 14,5 min).
- **Avaliação:**
  - `default`: 2030 avaliações (203 perguntas × 2 geradores × 5 repetições), 2,00 chamadas por avaliação, mediana de 21,4 s por avaliação, total de ~18 h.
  - `t1`: 2022 avaliações, 2,02 chamadas por avaliação, mediana de 23,0 s, total de ~18 h.
- **Falhas de formato do juiz:**
  - No `default`: nenhuma.
  - No `t1`: 8 avaliações (0,4%), 5 delas em pares sem recusa. As falhas foram JSON com chave ausente ou com nome errado (por exemplo `verduct`) e uma interrupção por repetição de tokens.
  - A nova tentativa reproduziu as 8 falhas: com a mesma seed e os mesmos parâmetros, a saída do juiz tende a se repetir.
- **Versões:** Ragas 0.4.3, scipy 1.18.1, Python 3.12, Ollama 0.35.0. A versão do modelo Gemini está registrada em cada resposta (`gemini-3.8-flash` nas 203).

## 5. Resultados

### 5.1 Recusas (desfecho separado)

| | Proprietário (Gemini) | Aberto (Llama) |
|---|---|---|
| Respostas | 203 | 203 |
| Recusas explícitas | 126 (62%) | 70 (34%) |
| Tamanho mediano das respostas que não são recusa | 750 caracteres | 703 caracteres |

- Os dois recusaram em 67 perguntas, só o Gemini em 59 e só o Llama em 3.
- **Restam 74 pares sem recusa,** e 129 perguntas foram excluídas.
- Todas as recusas do Gemini usam a frase sugerida no prompt ("I cannot answer based on the context."). As do Llama variam: algumas recusam por falta de contexto, outras por política ("I cannot provide medical advice…").
- **Precisão da regra de recusa:** em 20 respostas classificadas como recusa, sorteadas com seed 42, as 20 são recusas declaradas sem conteúdo sobre a pergunta. Essa conferência foi feita pelo Claude e ainda precisa ser confirmada pelo autor. A amostra não mede a cobertura.
- Respostas curtas (< 150 caracteres) não classificadas como recusa foram listadas para conferência: 4 do Gemini e 3 do Llama, todas com conteúdo.

### 5.2 Saturação
- Notas individuais iguais a 1,0, considerando as 210 respostas sem recusa da seção 5.3: 66% no `default` e 62% no `t1`.
- Nos 74 pares, respostas com média das K notas igual a 1,0:
  - `default`: 92% no Gemini e 70% no Llama.
  - `t1`: 46% no Gemini e 41% no Llama.
- Mediana das notas médias: 1,0 vs 1,0 no `default`; 0,988 vs 0,975 no `t1`.

### 5.3 Experimento 1 — variação do juiz (objetivo específico 2)

São 210 respostas analisadas: as 74 de cada gerador nos pares sem recusa, mais as respostas do gerador que não recusou nos pares com recusa. No total, 77 do Gemini e 133 do Llama. **Por isso, a comparação da variação entre geradores envolve conjuntos diferentes de perguntas.**

**Desvio-padrão das K = 5 notas por resposta:**

| Juiz | Grupo | n | DP médio | DP mediano | P75 | P90 | CV mediano | Respostas com DP > 0 |
|---|---|---|---|---|---|---|---|---|
| `default` | Gemini | 77 | 0,000 | 0,000 | 0,000 | 0,000 | 0,000 | 0 |
| `default` | Llama | 133 | 0,001 | 0,000 | 0,000 | 0,000 | 0,000 | 1 |
| `default` | total | 210 | 0,001 | 0,000 | 0,000 | 0,000 | 0,000 | 1 (0,5%) |
| `t1` | Gemini | 77 | 0,036 | 0,025 | 0,056 | 0,080 | 0,028 | — |
| `t1` | Llama | 133 | 0,095 | 0,079 | 0,130 | 0,224 | 0,093 | — |
| `t1` | total | 210 | 0,073 | 0,053 | 0,112 | 0,193 | 0,057 | 142 (68%) |

- No `t1`, as afirmações extraídas variaram entre as repetições em 210/210 respostas, e os veredictos em 200/210. No `default`, foram 2/210 e 1/210.
- Com só j = 1..3, o DP mediano no `t1` seria 0,029, contra 0,053 com j = 1..5.

**Simulação de avaliação única (74 pares; médias por repetição j):**

| j | `default` Gemini | `default` Llama | `t1` Gemini | `t1` Llama | `t1` n |
|---|---|---|---|---|---|
| 1 | 0,984 | 0,949 | 0,973 | 0,939 | 74 |
| 2 | 0,984 | 0,954 | 0,977 | 0,911 | 74 |
| 3 | 0,984 | 0,954 | 0,986 | 0,931 | 71 |
| 4 | 0,984 | 0,954 | 0,968 | 0,951 | 73 |
| 5 | 0,984 | 0,954 | 0,966 | 0,947 | 74 |

- O n menor que 74 nas repetições 3 e 4 do `t1` vem das falhas de formato do juiz: a pergunta sai só da repetição em que faltou nota.
- **Vencedor geral pela média:** o mesmo gerador (o proprietário) nas 5 repetições, nas duas configurações. Ele não mudou em nenhuma repetição.
- **Vencedor por pergunta,** com empate como categoria:
  - mudou entre as repetições em 1% das perguntas no `default`;
  - mudou em **77%** das perguntas no `t1`.
- A diferença entre as médias na avaliação única variou de 0,030 a 0,035 no `default` e de 0,018 a 0,066 no `t1`.

### 5.4 Experimento 2 — critério pareado (objetivo específico 3)

| | `default` | `t1` |
|---|---|---|
| Pares (sem recusa) | 74 | 74 |
| d > 0 / d < 0 / d = 0 | 22 / 5 / 47 | 41 / 20 / 13 |
| Pares usados no teste (d ≠ 0) | 27 | 61 |
| d mediana | 0,000 | 0,017 |
| d média | 0,031 | 0,037 |
| d: mínimo / P10 / P25 / P75 / P90 / máximo | −0,400 / 0,000 / 0,000 / 0,071 / 0,177 / 0,267 | −0,175 / −0,030 / −0,008 / 0,075 / 0,140 / 0,333 |
| Wilcoxon W | 84,0 | 443,0 |
| p (bicaudal) | 0,012 | 0,0003 |
| Z | −2,52 | −3,61 |
| r = \|Z\|/√n | 0,49 (médio a grande) | 0,46 (médio a grande) |
| Média simples: proprietário vs aberto | 0,984 vs 0,953 | 0,973 vs 0,936 |
| Conclusão da comparação direta | maior média: proprietário | maior média: proprietário |
| Conclusão do critério pareado | diferença significativa, a favor do proprietário | diferença significativa, a favor do proprietário |
| **As conclusões coincidem?** | **Sim** | **Sim** |

## 6. Leitura dos resultados (sugestão, com cautela)

- **Objetivo 2, configuração `default` do Ragas:** o juiz tende a ser praticamente determinístico. Repetir a avaliação quase não muda as notas (1 resposta em 210 variou), e uma única avaliação levaria à mesma comparação que K = 5. Para este juiz e esta configuração, a variação do juiz pode ser considerada desprezível.
- **Objetivo 2, configuração `t1`:**
  - A variação por resposta é moderada: DP mediano de 0,05 e P90 de 0,19, numa escala de 0 a 1.
  - Ela é suficiente para mudar o vencedor por pergunta em cerca de 3/4 das perguntas.
  - Na média agregada, ela tende a se compensar: o vencedor geral não mudou em nenhuma das 5 repetições.
  - Uma leitura possível: a oscilação do juiz ameaça mais as conclusões por pergunta, ou em amostras pequenas, do que a média de 74 pares.
- **Objetivo 3:**
  - Neste caso de aplicação, o critério pareado e a comparação direta das médias **chegaram à mesma conclusão** nas duas configurações do juiz.
  - Esse é um resultado legítimo: o critério proposto não contradisse a média, mas a qualificou. Ele informa:
    - se a diferença é estatisticamente distinguível;
    - o tamanho de efeito (r ≈ 0,46–0,49);
    - quantos pares de fato diferem. No `default`, 47 dos 74 pares têm d = 0 e a mediana de d é 0: na pergunta típica, não há diferença, e o resultado vem de 27 pares (22 a favor do proprietário e 5 do aberto).
  - A comparação direta não revela nenhuma dessas informações.
  - Não se pode generalizar que o critério sempre coincide com a média. Com diferenças menores, amostras menores ou um juiz mais variável, as conclusões podem divergir. No `pilot_v2`, com só 4 pares no `t1`, a média apontava um vencedor (0,971 vs 0,970) e o teste não, mas com n = 4 isso só valida o código.
- **Recusas:** a diferença nas taxas de recusa (62% vs 34%) é um desfecho à parte e pode ser lida de duas formas: maior aderência à instrução do prompt ou recusa excessiva. A regra de recusa evita que o juiz trate recusa como infidelidade.
- **Não concluir qual gerador é melhor.** A comparação de Faithfulness vale só para os 74 pares em que os dois responderam.

## 7. Limitações

1. **Seleção dos pares:** só restam 74 das 203 perguntas (36%), e esses pares tendem a ser as perguntas em que o contexto basta. A comparação vale para esse subconjunto.
2. **Um único juiz** (Mistral Small 3.2 24B, quantizado em Q4_K_M), uma única base (ExpertQA) e um único par de geradores.
3. **Saturação:** muitas notas são 1,0, sobretudo no `default` (92% das médias do Gemini). Isso reduz a sensibilidade da métrica e gera muitos d = 0, que o `zero_method="wilcox"` descarta.
4. **A configuração `t1` não é o padrão do Ragas.** Ela representa um uso plausível (amostragem plena), mas o comportamento padrão é o `default`.
5. **Juiz local:** a variação medida é a induzida pela amostragem, com `seed = j`. Não inclui o não determinismo de provedores de API.
6. **Exp. 1:** os conjuntos de respostas por gerador diferem (77 vs 133), então a comparação da variação entre geradores é só indicativa.
7. **Falhas de formato do juiz:** 8 avaliações no `t1` ficaram sem nota. As respostas afetadas usam a média de 4 repetições.
8. **Regra de recusa:** é baseada em padrão textual na primeira frase. A precisão observada foi de 20/20 na amostra, mas a cobertura não foi medida formalmente.
9. **Corpus:** os documentos do RAGBench foram usados sem limpeza e contêm ruído (URLs, trechos de páginas web).
10. **Gemini:** com temperature 1.0, as respostas não são reproduzíveis. As análises usam as respostas salvas.

## 8. Mudanças em relação ao projeto original (a refletir na metodologia)

- **Base:** RAGBench–ExpertQA (203 perguntas) no lugar do WikiEval, que mostrou saturação no piloto (100% de notas 1,0).
- **Juiz:** local via Ollama (modelo, quantização, versão e digest registrados), em vez de um juiz via API.
- **Amostragem dos geradores:** a recomendação de cada fornecedor, no lugar da "temperatura 0" original.
- **Amostragem do juiz:** padrão do Ragas (`default`) mais a configuração `t1`, com `seed = j`, reportadas lado a lado.
- **Parâmetros técnicos:** `max_tokens` do juiz = 4096, no lugar de 1024; contexto do Ollama fixado em 8192 tokens.
- **Novas regras:** recusas explícitas (com a taxa de recusa como desfecho separado), notas NaN e falha persistente do juiz.
- **Faturamento do Gemini:** o free tier foi usado em 3 respostas e o tier pago nas demais, com o mesmo modelo.

## 9. Arquivos

- **Configuração:** `config/final.yaml`. Prompt: `prompts/generation_v1.txt`. Código: `src/` (data, retrieve, generate, evaluate, analyze).
- **Resultados brutos (JSONL, uma linha por item):**
  - `results/retrieval/final_v1.jsonl`;
  - `results/generation/final_v1_{proprietary,open}.jsonl`;
  - `results/evaluation/final_v1_{default,t1}.jsonl`, com afirmações, veredictos e parâmetros enviados;
  - `results/evaluation/final_v1_t1_errors.jsonl`.
- **Análise:** `results/analysis/final_v1_summary.md` e os CSVs `final_v1_{config}_exp1_{responses,summary,single_eval}.csv` e `final_v1_{config}_exp2.csv`.
- **Notas manuais:** `final_v1_notes.md`. Amostra da regra de recusa: `final_v1_refusal_sample.md`.

## Apêndice A — Prompt de geração (`prompts/generation_v1.txt`)

```
Answer the question using only the information in the context below.
If the context does not contain the answer, say that you cannot answer based on the context.

Context:
{context}

Question: {question}

Answer:
```

## Apêndice B — Regra de recusa (`src/analyze.py`)

```python
REFUSAL = re.compile(
    r"^(based on the (provided |given )?context,\s*)?"
    r"(i cannot|i can't|i can not|i am unable to|i'm unable to|i am not able to|"
    r"you cannot|you can't) (answer|provide|verify)\b", re.IGNORECASE)
```

A regra é aplicada ao início da resposta, depois de `strip()`, e vale igualmente para os dois geradores.
