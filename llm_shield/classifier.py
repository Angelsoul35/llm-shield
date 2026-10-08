"""A learned prompt-injection classifier with word and character n-grams.

Two TF-IDF views are combined in a :class:`FeatureUnion`: word unigrams/bigrams
capture phrasing, character n-grams (``char_wb``, 3-5) capture sub-word cues and
survive light obfuscation and typos. A class-weight-balanced
:class:`LogisticRegression` on top keeps the model linear, so every decision is a
weighted sum of features and the top contributors are the explanation.

The model is regularised (``C=1.0``) and evaluated with a family-disjoint split
(see :mod:`llm_shield.evaluation`) so the reported accuracy reflects
generalisation to unseen phrasings, not memorised templates.
"""

from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion

from .generate import make_dataset


def _build_features() -> FeatureUnion:
    return FeatureUnion(
        [
            ("word", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2)),
            ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2)),
        ]
    )


class InjectionClassifier:
    def __init__(self, C: float = 1.0) -> None:
        self._features = _build_features()
        self._model = LogisticRegression(max_iter=2000, C=C, class_weight="balanced")
        self._fitted = False

    def fit(
        self, texts: list[str] | None = None, labels: list[int] | None = None
    ) -> InjectionClassifier:
        if texts is None:
            texts, labels = make_dataset()
        x = self._features.fit_transform(texts)
        self._model.fit(x, labels)
        self._fitted = True
        return self

    def injection_probability(self, text: str) -> float:
        if not self._fitted:
            raise RuntimeError("Classifier is not fitted. Call fit() first.")
        x = self._features.transform([text])
        return round(float(self._model.predict_proba(x)[0][1]), 4)

    def top_terms(self, text: str, k: int = 4) -> list[tuple[str, float]]:
        if not self._fitted:
            return []
        x = self._features.transform([text]).toarray().ravel()
        contributions = x * self._model.coef_[0]
        names = self._features.get_feature_names_out()
        order = np.argsort(contributions)[::-1]
        out: list[tuple[str, float]] = []
        for i in order:
            if contributions[i] <= 0:
                break
            # Report readable word features; skip raw char n-grams in the display.
            name = names[i]
            if name.startswith("word__"):
                out.append((name.removeprefix("word__"), round(float(contributions[i]), 4)))
            if len(out) >= k:
                break
        return out
