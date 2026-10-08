from __future__ import annotations

import pytest

from llm_shield.classifier import InjectionClassifier
from llm_shield.config import Settings
from llm_shield.shield import Shield


@pytest.fixture(scope="session")
def classifier() -> InjectionClassifier:
    return InjectionClassifier().fit()


@pytest.fixture
def shield(classifier) -> Shield:
    return Shield(
        classifier=classifier,
        settings=Settings(system_prompt_canary="CANARY-7F3A"),
    )
