"""Benchmark the injection classifier on REAL prompt-injection data.

Trains the same word+char TF-IDF + logistic classifier (:class:`InjectionClassifier`)
on the real ``deepset/prompt-injections`` dataset and reports cross-validated
accuracy, F1 and ROC-AUC, plus a train/test gap, so the number reflects real attacks
collected in the wild rather than only the synthetic families.

Run it with ``python -m llm_shield.real_benchmark``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split

from .classifier import InjectionClassifier
from .real_data import load_prompt_injections

_SEED = 42
_N_SPLITS = 5


@dataclass
class RealBenchmarkReport:
    n_prompts: int
    n_injection: int
    cv_accuracy: float
    cv_accuracy_std: float
    cv_f1: float
    cv_auc: float
    train_accuracy: float
    test_accuracy: float
    gap: float

    @property
    def verdict(self) -> str:
        if self.cv_accuracy < 0.70:
            return "weak: the classifier barely beats the benign-majority baseline"
        if self.gap > 0.15:
            return "overfit: training accuracy runs well ahead of test"
        return "well-fit: strong on held-out real prompts with train and test close"


def _cv_scores(texts: list[str], y: np.ndarray) -> tuple[float, float, float, float]:
    """Cross-validated accuracy (mean, std), F1 and ROC-AUC with the real classifier."""
    cv = StratifiedKFold(n_splits=_N_SPLITS, shuffle=True, random_state=_SEED)
    accs: list[float] = []
    f1s: list[float] = []
    probs = np.zeros(len(y), dtype=float)
    for train_idx, test_idx in cv.split(texts, y):
        clf = InjectionClassifier().fit(
            [texts[i] for i in train_idx], [int(y[i]) for i in train_idx]
        )
        p = np.array([clf.injection_probability(texts[i]) for i in test_idx])
        probs[test_idx] = p
        pred = (p >= 0.5).astype(int)
        accs.append(accuracy_score(y[test_idx], pred))
        f1s.append(f1_score(y[test_idx], pred, zero_division=0))
    auc = roc_auc_score(y, probs)
    return float(np.mean(accs)), float(np.std(accs)), float(np.mean(f1s)), float(auc)


def run_benchmark(data: tuple[list[str], list[int]] | None = None) -> RealBenchmarkReport:
    texts, labels = data if data is not None else load_prompt_injections()
    y = np.asarray(labels)
    cv_acc, cv_acc_std, cv_f1, cv_auc = _cv_scores(texts, y)

    idx = np.arange(len(texts))
    train_idx, test_idx = train_test_split(idx, test_size=0.25, stratify=y, random_state=_SEED)
    clf = InjectionClassifier().fit([texts[i] for i in train_idx], [int(y[i]) for i in train_idx])
    train_pred = np.array(
        [clf.injection_probability(texts[i]) >= 0.5 for i in train_idx], dtype=int
    )
    test_pred = np.array([clf.injection_probability(texts[i]) >= 0.5 for i in test_idx], dtype=int)

    return RealBenchmarkReport(
        n_prompts=len(texts),
        n_injection=int(y.sum()),
        cv_accuracy=round(cv_acc, 4),
        cv_accuracy_std=round(cv_acc_std, 4),
        cv_f1=round(cv_f1, 4),
        cv_auc=round(cv_auc, 4),
        train_accuracy=round(float(accuracy_score(y[train_idx], train_pred)), 4),
        test_accuracy=round(float(accuracy_score(y[test_idx], test_pred)), 4),
        gap=round(
            float(
                accuracy_score(y[train_idx], train_pred) - accuracy_score(y[test_idx], test_pred)
            ),
            4,
        ),
    )


def format_report(r: RealBenchmarkReport) -> str:
    return "\n".join(
        [
            "llm-shield — real-data benchmark (deepset/prompt-injections)",
            "=" * 60,
            f"prompts: {r.n_prompts} ({r.n_injection} injection / "
            f"{r.n_prompts - r.n_injection} benign)",
            "",
            f"CV accuracy : {r.cv_accuracy:.3f} +/- {r.cv_accuracy_std:.3f}",
            f"CV F1       : {r.cv_f1:.3f}",
            f"CV ROC-AUC  : {r.cv_auc:.3f}",
            f"train / test: {r.train_accuracy:.3f} / {r.test_accuracy:.3f}  (gap {r.gap:.3f})",
            "",
            f"verdict: {r.verdict}",
        ]
    )


def main() -> None:
    print(format_report(run_benchmark()))


if __name__ == "__main__":  # pragma: no cover
    main()
