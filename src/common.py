"""Shared helpers: config loading, result paths, JSONL I/O, Ollama metadata."""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
# Keep Hugging Face downloads inside the project (removable, see INSTALACOES.md).
os.environ.setdefault("HF_HOME", str(ROOT / ".cache" / "hf"))
# Ragas sends usage analytics by default.
os.environ.setdefault("RAGAS_DO_NOT_TRACK", "true")

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def load_config(path):
    """Load a YAML config and pin it to its run_id (abort if it changed)."""
    path = Path(path)
    cfg = yaml.safe_load(path.read_text())
    snapshot = ROOT / "results" / f"{cfg['run_id']}_config.yaml"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    if snapshot.exists():
        if yaml.safe_load(snapshot.read_text()) != cfg:
            sys.exit(f"Config differs from {snapshot}; use a new run_id.")
    else:
        shutil.copyfile(path, snapshot)
    return cfg


def result_path(stage, name):
    path = ROOT / "results" / stage / name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def append_jsonl(path, row):
    with Path(path).open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def code_commit():
    """Current git commit, marked '+dirty' if code or config differ from it."""
    def git(*args):
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                              text=True).stdout.strip()
    commit = git("rev-parse", "--short=12", "HEAD")
    dirty = git("status", "--porcelain", "--", "src", "config", "prompts", "requirements.txt")
    return commit + ("+dirty" if dirty else "")


def ollama_info(base_url, model):
    """Ollama server version and the exact digest of a local model."""
    version = httpx.get(f"{base_url}/api/version").json()["version"]
    tags = httpx.get(f"{base_url}/api/tags").json()["models"]
    digest = next((m["digest"] for m in tags if m["name"] == model), None)
    if digest is None:
        sys.exit(f"Model {model} not found in Ollama; run `ollama pull {model}`.")
    return {"ollama_version": version, "model_digest": digest}
