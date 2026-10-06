# CLAUDE.md — Experimentos do TCC (Fidelidade ao contexto em pipelines RAG)

Este arquivo dá o contexto do projeto para o Claude Code. Leia-o inteiro antes de escrever código.

## 1. Sobre o trabalho

TCC de Engenharia de Computação (CEFET-MG, Campus Timóteo). Autor: Jonas Camargo Junior.

**Ideia central.** Na prática, alternativas de um pipeline RAG costumam ser comparadas pela média de uma métrica (quem tem a maior média "vence"). Mas a métrica usada aqui, a *Faithfulness* do Ragas, é calculada por um LLM-juiz estocástico: a mesma resposta pode receber notas diferentes em avaliações repetidas. O trabalho verifica se um critério de comparação pareado (que considera a variação do juiz e o pareamento das respostas) leva a conclusões diferentes da comparação direta das médias. O caso de aplicação é a comparação entre um gerador de pesos abertos e um proprietário.

**Objetivo geral.** Propor um critério de comparação dos resultados da métrica de fidelidade ao contexto obtidos por um modelo gerador de pesos abertos e por um proprietário, aplicados a um mesmo pipeline RAG, que vá além da comparação direta das médias.

**Objetivos específicos.**
1. Selecionar um modelo gerador de pesos abertos e um proprietário para compor o mesmo pipeline RAG.
2. Mensurar a variação das pontuações de fidelidade entre avaliações repetidas de uma mesma resposta e seu efeito sobre a comparação direta das médias.
3. Aplicar o critério proposto e verificar se ele conduz a conclusões diferentes das da comparação direta das médias.

O resultado principal é o **critério de comparação**, não "qual gerador é melhor". Os geradores são o caso de aplicação.

## 2. Fase atual: PILOTO

> **Atualização (2026-10-05):** o piloto terminou (`pilot_v1`, `base_test_v1`, `pilot_v2`), e o experimento final foi congelado e iniciado (seção 6.1.3). Esta seção fica como registro do piloto.

Ainda não é o experimento completo. O piloto serve para preencher decisões pendentes da metodologia antes da execução final.

**Escopo do piloto:** 5 a 10 perguntas, os dois geradores, K entre 3 e 5.

**O piloto deve responder:**
- A Faithfulness satura perto de 1? (Se quase tudo der 1,0, a comparação perde sentido.)
- Qual o tamanho da oscilação do juiz entre avaliações repetidas? (Se for ~0, o Experimento 1 precisa ser repensado.)
- Quanto tempo leva cada geração e cada avaliação? Quantas chamadas de API?
- O modelo de pesos abertos roda de forma viável na máquina disponível?
- Que valor de K parece suficiente?

Ao final do piloto, gere um resumo curto em português com esses pontos, números observados e recomendações. **Não** tire conclusões sobre qual gerador é melhor a partir do piloto.

## 3. Desenho experimental (não alterar sem avisar)

O princípio é: **apenas o gerador varia.** Dados, recuperação, prompt e juiz são fixos.

### 3.1 Dados
- Conjunto WikiEval (Es et al., 2023): 50 perguntas, cada uma associada a uma página da Wikipédia sobre eventos a partir de 2022. Provavelmente disponível no Hugging Face como `explodinggradients/WikiEval` — **confirmar** e inspecionar as colunas antes de usar.
- Usar apenas as perguntas e os textos das páginas. Não usar os rótulos humanos nem as respostas prontas do conjunto.
- Tudo em inglês (idioma original). Não traduzir.
- Pendente: o autor considera criar as próprias perguntas no lugar do WikiEval. Manter o carregamento de dados isolado em um módulo para facilitar a troca.

### 3.2 Pipeline RAG
- LangChain, configuração de etapa única (*one-shot*): uma recuperação e uma geração por pergunta, sem reformulação nem múltiplas consultas.
- Divisão das páginas em trechos, embeddings e armazenamento vetorial. Parâmetros pendentes (tamanho do trecho, sobreposição, modelo de embedding, base vetorial, k): centralizar tudo em um arquivo de configuração.
- **A recuperação é executada uma única vez por pergunta e os trechos são salvos.** Os dois geradores recebem exatamente os mesmos trechos, lidos do arquivo salvo.
- Prompt de geração fixo, idêntico para os dois geradores, salvo em arquivo versionado (vai para o apêndice do TCC).

### 3.3 Geração
- Dois geradores: `gemini-3.8-flash` (proprietário, via API) e Llama 3.1 8B Instruct (pesos abertos, via Ollama local). Detalhes na seção 6.1.
- Uma única resposta por pergunta.
- **Regra de amostragem dos geradores:** cada gerador usa a configuração recomendada pelo seu fornecedor (decisão do autor em 2026-10-02, que substitui a "temperatura 0" original).
  - **Gemini:** temperature 1.0 (o padrão), sem alterar top_p e top_k, com thinking no padrão do modelo (`medium`). Fontes:
    - Google, *What's new in Gemini 3.5 Flash* (https://ai.google.dev/gemini-api/docs/whats-new-gemini-3.5, acessado em 2026-10-02), que vale para todos os Gemini 3.x: "`temperature`, `top_p`, `top_k`: we strongly recommend not changing the default values. Gemini 3's reasoning capabilities are optimized for the default settings." No guia de migração: "Remove `temperature`, `top_p`, `top_k` from your config (no longer recommended)."
    - Google, *Gemini 3 Developer Guide* (https://ai.google.dev/gemini-api/docs/gemini-3, página marcada como obsoleta, acessada em 2026-10-02): "For all Gemini 3 models, we strongly recommend keeping the temperature parameter at its default value of `1.0`. [...] Changing the temperature (setting it below 1.0) may lead to unexpected behavior, such as looping or degraded performance [...]."
    - Thinking padrão `medium` para o `gemini-3.8-flash`: Google, *Gemini thinking* (https://ai.google.dev/gemini-api/docs/thinking, tabela "Controlling thinking", acessada em 2026-10-02).
  - **Llama 3.1 8B Instruct:** temperature 0.6, top_p 0.9 e seed fixa (registrada na configuração). Fontes:
    - Meta, implementação de referência `meta-llama/llama-models`, arquivo `models/llama3/generation.py` (padrões `temperature: float = 0.6`, `top_p: float = 0.9`; https://github.com/meta-llama/llama-models, acessado em 2026-10-02).
    - `generation_config.json` do modelo `meta-llama/Llama-3.1-8B-Instruct` no Hugging Face (`"temperature": 0.6`, `"top_p": 0.9`). O repositório oficial é restrito; os valores foram conferidos numa cópia pública idêntica, `unsloth/Meta-Llama-3.1-8B-Instruct`.
  - O Gemini via API não é reproduzível com temperature 1.0, mas isso não afeta as análises, que leem as respostas salvas.
- Salvar cada resposta com: id da pergunta, gerador, modelo exato/versão, prompt usado, trechos usados (ou referência a eles), timestamp e tempo de execução.

### 3.4 Avaliação
- Métrica: `Faithfulness` do Ragas (a resposta é decomposta em afirmações; a nota é a proporção de afirmações sustentadas pelo contexto).
- **Fixar a versão do Ragas** no `requirements`. A API do Ragas mudou bastante entre versões; consultar a documentação da versão instalada em vez de assumir a sintaxe.
- Juiz: um LLM de **família diferente** dos dois geradores (para reduzir viés de autopreferência): Mistral Small 3.2 24B local (seção 6.1). Registrar os parâmetros efetivamente enviados.
- **Regra de amostragem do juiz (diferente da dos geradores):** o juiz **não** segue a recomendação do fornecedor. Ele segue o padrão do Ragas:
  - `default`, a configuração principal: temperature 0.01 e top_p 0.1, os padrões de `InstructorModelArgs` no Ragas 0.4.3.
  - `t1`, a configuração adicional: temperature 1.0 e top_p 1.0, ambos explícitos.
  - Nas duas, `seed = j` na repetição j. As duas configurações são reportadas no piloto e no experimento final.
  - **`max_tokens` = 4096 nas duas configurações**, no lugar do padrão de 1024 do Ragas (decisão do autor em 2026-10-02). Motivo: no teste de fumaça, a chamada de veredictos gastou ~85 tokens por afirmação, então respostas com mais de ~11 afirmações seriam truncadas e falhariam. O truncamento afetaria mais as respostas longas e, portanto, mais um dos geradores. `max_tokens` não é parâmetro de amostragem: temperature e top_p continuam no padrão do Ragas.
- Cada resposta é avaliada **K vezes** com os mesmos parâmetros.
- **Atenção a cache:** verificar se o Ragas, o LangChain ou o cliente de API fazem cache de chamadas. Se houver cache, as K avaliações sairiam idênticas artificialmente. Desativar qualquer cache nas avaliações repetidas e confirmar isso no piloto.
- Salvar cada avaliação individualmente (id da pergunta, gerador, índice da repetição j, nota, e, se disponível, as afirmações extraídas e os veredictos).

## 4. Análises

Todas as análises devem rodar sobre os arquivos salvos, sem novas chamadas aos modelos.

### 4.1 Experimento 1 — variação do juiz (objetivo específico 2)
- Para cada resposta: desvio-padrão (amostral, ddof=1) e coeficiente de variação (desvio ÷ média) das K notas. Tratar média zero no CV.
- Resumir por gerador e no total: média, mediana, percentis.
- **Efeito sobre a comparação direta:** simular a prática comum de avaliar uma única vez. Para cada repetição j (1..K), usar só a nota da repetição j de cada resposta e:
  - calcular a média de cada gerador e ver qual "vence" na comparação direta;
  - ver, por pergunta, qual gerador tem a nota maior.
  - Reportar: com que frequência o vencedor geral muda entre repetições, e em que proporção das perguntas o vencedor por pergunta muda entre repetições.

### 4.2 Experimento 2 — critério pareado (objetivo específico 3)
- Nota de cada resposta = média das K avaliações.
- Para cada pergunta, d = nota do proprietário − nota do aberto.
- Descritivo: mediana (principal) e média de d.
- Teste de postos sinalizados de Wilcoxon pareado, **bicaudal**, α = 0,05 (`scipy.stats.wilcoxon`). Registrar como os zeros foram tratados (`zero_method`).
- Tamanho de efeito r = |Z| / √n, com n = número de pares usados no teste. Obter Z pela aproximação normal (por exemplo, `method="approx"` no scipy, conforme a versão instalada) ou calculá-lo a partir de W. Escala de referência: ~0,1 pequeno, ~0,3 médio, ≥0,5 grande.
- **Contraste:** comparar a conclusão do critério pareado com a da comparação direta das médias (a direta usa as médias simples de cada gerador). Reportar se as conclusões coincidem ou divergem.
- **Não usar bootstrap.** Foi uma decisão explícita do autor.

## 5. Organização e reprodutibilidade

Estrutura sugerida (ajustar se fizer sentido):

```
config/        parâmetros (modelos, k, K, chunking, caminhos)
prompts/       prompt de geração versionado
src/           carregamento de dados, recuperação, geração, avaliação, análises
data/          dados de entrada (não versionar arquivos grandes)
results/
  retrieval/   trechos recuperados por pergunta
  generation/  respostas por gerador
  evaluation/  uma linha por avaliação (pergunta, gerador, j, nota)
  analysis/    tabelas e figuras
```

Regras:
- Chaves de API em `.env`, nunca no código ou no repositório.
- Dependências com versão fixada.
- Resultados brutos em formato estruturado (JSONL ou CSV), **nunca sobrescritos**; cada execução em arquivo ou pasta própria, com identificação de data/configuração.
- Cada etapa (recuperação, geração, avaliação, análise) executável separadamente e retomável: se falhar no meio, não refazer o que já foi salvo.
- Registrar o número de chamadas e o tempo de cada etapa.
- **Tudo deve ser removível ao final do projeto.** Downloads ficam dentro da pasta do projeto sempre que possível (`.venv/`, `HF_HOME=.cache/hf`, `OLLAMA_MODELS=.ollama-models`, `pip --no-cache-dir`). Qualquer coisa instalada fora dela é anotada em `INSTALACOES.md` no momento da instalação, com o comando de remoção.

## 6. Decisões

### 6.1 Tomadas
- **Gerador proprietário:** `gemini-3.8-flash` via API (conta no free tier), acessado pelo endpoint do Gemini compatível com OpenAI.
- **Amostragem:** os geradores seguem a recomendação do fornecedor e o juiz segue o padrão do Ragas, como descrito nas seções 3.3 e 3.4.
- **Gerador de pesos abertos:** Llama 3.1 8B Instruct via Ollama local (Apple M5 Pro, 24 GB), com a tag `llama3.1:8b-instruct-q8_0`.
- **Juiz:** Mistral Small 3.2 24B via Ollama local, com a tag `mistral-small3.2:24b-instruct-2506-q4_K_M` (a Q8 tem 26 GB e não cabe). É de família diferente dos dois geradores (cumpre a 3.4), e o Ragas o acessa pelo endpoint do Ollama compatível com OpenAI.
- **Seed do juiz:** `seed = j` na repetição j. É reprodutível e varia entre as repetições.
- **Configurações do juiz, no piloto e no experimento final:** os Experimentos 1 e 2 são reportados separadamente para cada uma.
  - `default`: o padrão do Ragas, temperature 0.01 e top_p 0.1.
  - `t1`: temperature 1.0 e top_p 1.0, ambos explícitos; sem isso o Ragas enviaria top_p 0.1. O top_k fica no padrão do Ollama, que é registrado.
- **Experimento 1:** com juiz local, mede a variação induzida pela amostragem do juiz em cada configuração, e não o não determinismo de um provedor de API.
- **Notas NaN** (nenhuma afirmação extraída):
  - Se só parte das K avaliações der NaN, a nota da resposta é a média das válidas, e o número de descartadas fica registrado.
  - Se as K derem NaN, o par sai tanto do Wilcoxon quanto da comparação direta das médias, e quantos saíram (e quais) é reportado.
  - No Exp. 1, o desvio exige pelo menos 2 notas válidas. Na simulação de avaliação única, a pergunta sai só da repetição j em que houver NaN.
- **Falha persistente do juiz** (decisão do autor em 2026-10-06): uma avaliação que falha (por exemplo, JSON inválido depois das retentativas do Ragas) fica registrada em `<run>_<config>_errors.jsonl` e é tentada de novo uma vez. Se falhar de novo, ela conta como repetição sem nota válida, com a mesma regra do NaN parcial (média das repetições válidas), e é reportada como "falha de formato do juiz".
- **Recusas explícitas** (decisão do autor em 2026-10-05, depois do `pilot_v2`):
  - Uma resposta é recusa quando começa declarando que não pode responder, fornecer ou verificar. O padrão é fixo (`REFUSAL` em `src/analyze.py`) e é aplicado igualmente aos dois geradores. Exemplos: "I cannot answer based on the context.", "Based on the context, I cannot answer…", "I cannot provide medical advice…". Uma recusa não recebe nota de Faithfulness, mesmo que venha conteúdo depois dela.
  - Motivo: a recusa não faz afirmações sobre o conteúdo, mas o juiz a converte numa meta-afirmação e lhe dá 0 (30/30 no `default` e 28/30 no `t1` no `pilot_v2`).
  - Revisão de 2026-10-05, ainda sem ver notas do `final_v1`: a primeira versão casava só a frase exata do prompt. Essa versão pegava as recusas do Gemini e nenhuma das do Llama, que usa redações variadas (72/203 respostas começam com recusa). Ela era assimétrica.
  - Ao final, uma amostra aleatória de 20 respostas classificadas será conferida manualmente, para reportar a precisão da regra.
  - O par sai tanto do Wilcoxon quanto da comparação direta das médias, como no caso de NaN. As avaliações do juiz continuam salvas e são reportadas à parte.
  - A taxa de recusa por gerador é reportada como desfecho separado.
  - As respostas curtas que não forem classificadas como recusa são listadas para conferência manual.
  - No Exp. 1, a variação é calculada por resposta e inclui as respostas do outro gerador nesses pares. A simulação de avaliação única usa só os pares sem recusa.
  - Limitação: os pares que restam tendem a ser as perguntas em que o contexto basta, e a comparação vale para esse subconjunto.
- **Dados (piloto):** WikiEval, hoje publicado como `vibrantlabsai/WikiEval`. O conjunto não traz as páginas completas, então o corpus usa a coluna `context_v2` das 50 páginas.
- **Perguntas do piloto:** 10, sorteadas com seed fixa (42), registrada na configuração.
- **Prompt de geração:** `prompts/generation_v1.txt`, na versão aprovada no plano.
- **Ragas:** 0.4.3, com a Faithfulness de `ragas.metrics.collections`.

### 6.1.1 Teste de viabilidade de base (não é parte do experimento final)
- **Motivo:** o pilot_v1 com o WikiEval mostrou saturação forte (100% de notas 1,0 no juiz `default`).
- **Base testada:** RAGBench, subconjunto ExpertQA, split de teste (203 perguntas; `galileo-ai/ragbench`, antes `rungalileo/ragbench`, revisão `97808f3e5fd1`, licença CC-BY-4.0).
- **Uso dos dados:** só as perguntas e os documentos de cada pergunta, juntados como "texto da página" sem limpeza. As respostas e os rótulos do RAGBench não são usados.
- **Configuração:** `config/base_test.yaml`, `run_id` `base_test_v1`. Só o gerador aberto (Llama), K=5, as duas configurações do juiz, e o resto idêntico ao piloto. Execução única.
- **Referências:**
  - Friel, R.; Belyi, M.; Sanyal, A. *RAGBench: Explainable Benchmark for Retrieval-Augmented Generation Systems*. arXiv:2407.11005, 2024.
  - Malaviya, C.; Lee, S.; Chen, S.; Sieber, E.; Yatskar, M.; Roth, D. *ExpertQA: Expert-Curated Questions and Attributed Answers*. NAACL 2024. arXiv:2309.07852.

### 6.1.2 Piloto v2 no RAGBench–ExpertQA
- **Decisão do autor (2026-10-05):** depois do teste de viabilidade, o piloto continua no RAGBench–ExpertQA (split de teste) com os dois geradores. O `pilot_v1` (WikiEval) fica registrado como está, com as respostas do Gemini incompletas.
- **Configuração:** `config/pilot_v2.yaml`, `run_id` `pilot_v2`. Mesmas 10 perguntas (seed 42), K=5, as duas configurações do juiz, e o resto idêntico ao `pilot_v1`.
- **Análise:** desvios-padrão abaixo de 1e-9 são tratados como 0 (ruído de ponto flutuante quando as K notas são iguais).
- Uso dos dados e referências: como na 6.1.1.

### 6.1.3 Experimento final (congelado em 2026-10-05)
- **Configuração:** `config/final.yaml`, `run_id` `final_v1`. É idêntica ao `pilot_v2`, exceto pelo número de perguntas.
- **Base:** RAGBench–ExpertQA, split de teste, todas as 203 perguntas (dados e referências como na 6.1.1).
- **Recuperação:** os valores do piloto. Trechos de 1000 caracteres com sobreposição de 200, `BAAI/bge-small-en-v1.5`, `InMemoryVectorStore` e k = 4. O índice tem as 203 perguntas, e os documentos das outras perguntas servem de distratores.
- **Prompt:** `prompts/generation_v1.txt`, sem alterações. As recusas seguem a regra da 6.1.
- **K = 5,** nas duas configurações do juiz. O juiz roda em paralelo à coleta do Gemini e não está no caminho crítico, então K = 5 não atrasa o fim do experimento.
- **Execução:** `src/run_final.sh`, que roda o Gemini e o juiz em laços independentes.
  - O laço do Gemini usa a cota diária do free tier e dorme até o `retryDelay` informado no erro 429. Estimativa de 10 a 18 dias, porque os erros 503 também consomem a cota.
  - O progresso é acompanhado com `src/progress.py`, que mostra só contagens, recusas, erros e versões, sem médias nem vencedores.
  - Os dois laços retomam do ponto em que pararam se forem reiniciados.
  - O Mac precisa ficar na tomada e com a tampa aberta, porque o `caffeinate -s` só impede o sono na tomada.
- **Faturamento do Gemini (2026-10-06):** o autor adicionou crédito pré-pago à chave. As 3 primeiras respostas (qids 0–2) vieram do free tier e as demais do tier pago, com o mesmo modelo e os mesmos parâmetros. O custo estimado é de ~US$ 0,0025 por resposta: ~700 tokens de entrada a US$ 0,75/M e ~520 de saída, com o thinking, a US$ 3,75/M (preços de https://ai.google.dev/gemini-api/docs/pricing, acessado em 2026-10-06). A geração restante rodou de uma vez com `src/generate.py` (log em `logs/final_v1_gemini_paid.log`).
- **Checkpoint de viabilidade depois de 2 ou 3 dias:** taxa de recusa, erros, NaN, pares úteis e versão do Gemini. Ele não olha notas.
- **Regra de congelamento:** qualquer mudança em base, perguntas, recuperação, prompt ou parâmetros dos geradores exige um novo `run_id` e refazer a geração. Mudanças no juiz, no K ou nas análises não exigem novas chamadas ao Gemini.

### 6.2 Pendentes
- Nenhuma decisão de desenho pendente para a coleta. As regras de análise podem ser ajustadas depois, sem novas chamadas.

### 6.3 Mudanças a refletir na metodologia do TCC
- Base final: RAGBench–ExpertQA (split de teste, 203 perguntas) no lugar do WikiEval. O piloto no WikiEval mostrou saturação (seção 6.1.1). O corpus são os documentos de cada pergunta, juntados sem limpeza (com o ruído descrito no resumo do `base_test_v1`), e as respostas e rótulos do RAGBench não são usados.
- O juiz é local, via Ollama: modelo, quantização Q4_K_M, versão do Ollama e digest do modelo.
- Seeds por repetição (`seed = j`) e as duas configurações do juiz, reportadas lado a lado.
- `max_tokens` do juiz = 4096 (no lugar de 1024), com o motivo da 3.4.
- Contexto do servidor Ollama fixado em 8192 tokens (`OLLAMA_CONTEXT_LENGTH`).
- O Experimento 1 mede explicitamente a variação induzida pela amostragem do juiz, em cada configuração.
- A regra para notas NaN.
- Parâmetros de recuperação finais (6.1.3). O Gemini foi acessado no free tier (3 respostas) e no tier pago (as demais), com o mesmo modelo, e a versão do modelo está registrada em cada resposta.
- A regra para recusas explícitas, com a taxa de recusa por gerador como desfecho separado e a limitação de seleção dos pares.
- A regra de amostragem dos geradores (recomendação do fornecedor, com as fontes da 3.3) e a do juiz (padrão do Ragas mais `t1`, com `seed = j`).

## 7. Como trabalhar com o autor

- Comunicação em português; código, prompts e dados em inglês.
- Respostas concisas, com linguagem cautelosa ("pode", "tende a") ao interpretar resultados.
- Antes de gerar muitos arquivos ou uma estrutura grande, apresentar a estrutura proposta e confirmar.
- Se algo no desenho experimental parecer problemático ou inviável, **avisar antes de mudar**. O texto do TCC descreve este desenho, então mudanças precisam ser refletidas na metodologia.
