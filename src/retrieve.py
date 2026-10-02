"""Step 1: chunk all pages, embed, and retrieve the top-k chunks once per question.

Usage: .venv/bin/python src/retrieve.py --config config/pilot.yaml
"""

import argparse
import time

from common import append_jsonl, code_commit, load_config, now, read_jsonl, result_path
from data import load_wikieval, select_qids
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_config(args.config)
    commit = code_commit()
    rc = cfg["retrieval"]
    out = result_path("retrieval", f"{cfg['run_id']}.jsonl")
    done = {r["qid"] for r in read_jsonl(out)}

    items = load_wikieval(**cfg["dataset"])
    qids = select_qids(len(items), cfg["questions"]["n"], cfg["questions"]["seed"])
    todo = [it for it in items if it["qid"] in qids and it["qid"] not in done]
    print(f"Selected qids: {qids}; already done: {len(done)}; to do: {len(todo)}")
    if not todo:
        return

    # The index holds every page, so other pages act as distractors.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=rc["chunk_size"], chunk_overlap=rc["chunk_overlap"]
    )
    docs = []
    for it in items:
        for i, chunk in enumerate(splitter.split_text(it["page_text"])):
            docs.append(Document(
                page_content=chunk,
                metadata={"chunk_id": f"p{it['qid']}-c{i}", "page_qid": it["qid"],
                          "source": it["source"]},
            ))

    t0 = time.perf_counter()
    embeddings = HuggingFaceEmbeddings(
        model_name=rc["embedding_model"], encode_kwargs={"normalize_embeddings": True}
    )
    store = InMemoryVectorStore.from_documents(docs, embeddings)
    index_s = time.perf_counter() - t0
    print(f"Indexed {len(docs)} chunks from {len(items)} pages in {index_s:.1f}s")

    for it in todo:
        t0 = time.perf_counter()
        hits = store.similarity_search_with_score(it["question"], k=rc["k"])
        chunks = [{"chunk_id": d.metadata["chunk_id"], "page_qid": d.metadata["page_qid"],
                   "source": d.metadata["source"], "score": float(s), "text": d.page_content}
                  for d, s in hits]
        append_jsonl(out, {
            "qid": it["qid"],
            "question": it["question"],
            "source": it["source"],
            "chunks": chunks,
            "same_page_hit": any(c["page_qid"] == it["qid"] for c in chunks),
            "params": rc,
            "n_chunks_indexed": len(docs),
            "index_s": round(index_s, 2),
            "code_commit": commit,
            "timestamp": now(),
            "elapsed_s": round(time.perf_counter() - t0, 3),
        })
    print(f"Saved {len(todo)} rows to {out}")


if __name__ == "__main__":
    main()
