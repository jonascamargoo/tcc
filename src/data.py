"""Question/page loading, kept separate so the data source can be swapped later.

Only the questions and page texts are used; the dataset's human labels and
ready-made answers are ignored on purpose.
"""

import random

from datasets import load_dataset


def load_wikieval(name, revision, page_text_column):
    ds = load_dataset(name, revision=revision, split="train")
    items = []
    for qid, row in enumerate(ds):
        question = row["question"].strip()
        if question.startswith("Question:"):
            question = question[len("Question:"):].strip()
        items.append({
            "qid": qid,
            "question": question,
            "source": row["source"],
            "page_text": "\n\n".join(row[page_text_column]),
        })
    return items


def load_ragbench(name, revision, subset, split):
    """RAGBench subset (e.g. expertqa). Each question's documents, joined, play the
    role of its "page"; they are used as provided, without cleaning."""
    ds = load_dataset(name, subset, revision=revision, split=split)
    return [{
        "qid": qid,
        "question": row["question"].strip(),
        "source": row["id"],
        "page_text": "\n\n".join(row["documents"]),
    } for qid, row in enumerate(ds)]


def load_items(name, **kwargs):
    """Entry point used by the pipeline; picks the loader from the dataset name."""
    if name == "vibrantlabsai/WikiEval":
        return load_wikieval(name, **kwargs)
    if name == "galileo-ai/ragbench":
        return load_ragbench(name, **kwargs)
    raise ValueError(f"No loader for dataset {name}")


def select_qids(n_total, n, seed):
    return sorted(random.Random(seed).sample(range(n_total), n))
