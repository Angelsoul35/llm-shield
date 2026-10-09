"""Leakage-free evaluation of the injection classifier.

Within-distribution accuracy on templated data is misleadingly high, so this
module measures what actually matters:

* **family-disjoint generalisation** — train on some prompt families, test on the
  *held-out* families, so the test phrasings are structurally unseen;
* **the train/test gap** — a large gap signals overfitting, a low score on both
  signals underfitting.

Run with ``python -m llm_shield.evaluation``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import accuracy_score, f1_score

from .classifier import InjectionClassifier
from .generate import make_grouped_dataset


@dataclass
class EvalReport:
    grouped_accuracy: float
    grouped_f1: float
    train_accuracy: float
    train_test_gap: float
    n_train: int
    n_test: int
    held_out_families: list[str]


def family_disjoint_eval(n: int = 2000, seed: int = 23, holdout_frac: float = 0.4) -> EvalReport:
    texts, labels, families = make_grouped_dataset(n, seed)
    texts = np.array(texts)
    labels = np.array(labels)
    families = np.array(families)

    rng = np.random.default_rng(seed)
    # Hold out whole families from BOTH classes, so both benign and injection
    # test phrasings are unseen structures.
    benign_fams = sorted({f for f in families if f.startswith("benign:")})
    inject_fams = sorted({f for f in families if f.startswith("inject:")})

    def pick(fams: list[str]) -> set[str]:
        k = max(1, round(len(fams) * holdout_frac))
        return set(rng.choice(fams, size=k, replace=False))

    held = pick(benign_fams) | pick(inject_fams)
    test_mask = np.array([f in held for f in families])

    clf = InjectionClassifier().fit(list(texts[~test_mask]), list(labels[~test_mask]))

    def preds(xs):
        return np.array([1 if clf.injection_probability(t) >= 0.5 else 0 for t in xs])

    test_pred = preds(texts[test_mask])
    train_pred = preds(texts[~test_mask])

    grouped_acc = accuracy_score(labels[test_mask], test_pred)
    train_acc = accuracy_score(labels[~test_mask], train_pred)
    return EvalReport(
        grouped_accuracy=round(float(grouped_acc), 3),
        grouped_f1=round(float(f1_score(labels[test_mask], test_pred)), 3),
        train_accuracy=round(float(train_acc), 3),
        train_test_gap=round(float(train_acc - grouped_acc), 3),
        n_train=int((~test_mask).sum()),
        n_test=int(test_mask.sum()),
        held_out_families=sorted(held),
    )


if __name__ == "__main__":
    report = family_disjoint_eval()
    print("Family-disjoint evaluation (test families never seen in training):")
    print(f"  held-out families : {report.held_out_families}")
    print(f"  train / test size : {report.n_train} / {report.n_test}")
    print(f"  grouped accuracy  : {report.grouped_accuracy}")
    print(f"  grouped F1        : {report.grouped_f1}")
    print(f"  train accuracy    : {report.train_accuracy}")
    print(f"  train-test gap    : {report.train_test_gap}  (small = not overfit)")
