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


def load_items(name, **kwargs):
    """Entry point used by the pipeline; picks the loader from the dataset name."""
    if name == "vibrantlabsai/WikiEval":
        return load_wikieval(name, **kwargs)
    raise ValueError(f"No loader for dataset {name}")


def select_qids(n_total, n, seed):
    return sorted(random.Random(seed).sample(range(n_total), n))
