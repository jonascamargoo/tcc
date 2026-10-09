# Registro de instalações

Tudo o que for instalado ou baixado para este projeto entra aqui, para ser removido ao final.
**Regra:** sempre que possível, o que for baixado fica dentro da pasta do projeto. O que precisar ficar fora dela é anotado na tabela abaixo no momento da instalação.

## Estado da máquina antes do projeto (2026-10-02)

Não remover nada desta seção.

- **Python:** `python@3.12` (3.12.14) já estava instalado via Homebrew. O venv do projeto usa esse Python.
- **Fórmulas Homebrew:** ada-url bash brotli c-ares ca-certificates direnv fmt gettext gh hdrhistogram_c icu4c@78 json-c libffi libnghttp2 libnghttp3 libngtcp2 libunistring libuv llhttp lz4 merve mpdecimal nbytes ncurses node openssl@3 python@3.12 readline simdjson simdutf sqlite uvwasi xz zstd
- **Casks Homebrew:** karabiner-elements
- **Outros:** `~/Library/Caches/pip` já existia (724 MB). As instalações do projeto usam `--no-cache-dir` para não aumentá-lo. `~/.ollama` e `~/.cache/huggingface` não existiam.

## Dentro do projeto

Isso sai ao apagar a pasta, e nada aqui é versionado.

| Caminho | Conteúdo | Tamanho aprox. |
|---|---|---|
| `.venv/` | pacotes Python (`requirements.txt`; versões exatas em `requirements.lock`) | 1,4 GB |
| `.cache/hf/` | embedding `BAAI/bge-small-en-v1.5` e dataset WikiEval (via `HF_HOME`) | 138 MB |
| `.ollama-models/` | `llama3.1:8b-instruct-q8_0` e `mistral-small3.2:24b-instruct-2506-q4_K_M` (via `OLLAMA_MODELS`) | 22 GB |
| `logs/` | logs do servidor Ollama e dos downloads | < 1 MB |
| `.env` | chave do Gemini | — |

## Fora do projeto

Preencher no momento de cada instalação.

| Data | O quê | Onde | Como remover |
|---|---|---|---|
| 2026-10-02 | `brew install ollama` (Ollama 0.35.0) e as dependências novas `mlx` 0.32.1, `mlx-c` 0.6.0_4 e `python@3.14` 3.14.8 | `/opt/homebrew` | `brew uninstall ollama mlx-c mlx python@3.14` |
| 2026-10-02 | Efeito colateral do mesmo comando: o Homebrew atualizou fórmulas que já existiam (`ca-certificates` 2026-09-25, `openssl@3` 3.6.5, `readline` 8.3.6, `xz` 5.8.4, `sqlite` 3.53.4). O `brew cleanup` automático apagou versões antigas e caches (`sqlite` 3.53.3, `xz` 5.8.3, o .dmg em cache do karabiner-elements e o portable-ruby) | `/opt/homebrew`, `~/Library/Caches/Homebrew` | **Não reverter.** São atualizações de dependências compartilhadas e o rebaixamento não é suportado. Para evitar isso em instalações futuras, usar `HOMEBREW_NO_INSTALL_UPGRADE=1 HOMEBREW_NO_INSTALL_CLEANUP=1` |
| 2026-10-02 | Pasta criada pelo Ollama (`id_ed25519`, `id_ed25519.pub`, `cache/`, 4 KB); os modelos **não** ficam aqui | `~/.ollama` | `rm -rf ~/.ollama` |

## Limpeza final

1. Parar o servidor do Ollama (`Ctrl+C` no terminal onde roda `ollama serve`).
2. Desinstalar o Ollama: rodar os comandos `brew uninstall` da tabela e depois `brew list --formula`, comparando com a lista de "antes".
3. Rodar `rm -rf ~/.ollama`.
4. Apagar `.venv/`, `.cache/`, `.ollama-models/` e `.env`, ou a pasta do projeto inteira.
5. Opcional: revogar a chave do Gemini no AI Studio.
