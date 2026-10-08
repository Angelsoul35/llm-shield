"""The shield: combine rule detectors and the classifier into a verdict.

Input is scanned for injection (rules + classifier); output is scanned for secret
and system-prompt leaks (rules). Each scan returns a verdict — allow, flag, or
block — a risk score, and the detections that justify it. Defence in depth: a
high-severity rule blocks on its own, and the classifier blocks novel attacks the
rules miss.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum

from .classifier import InjectionClassifier
from .config import Settings, get_settings
from .detectors import Detection, Severity, scan_injection, scan_prompt_leak, scan_secrets


class Verdict(StrEnum):
    ALLOW = "allow"
    FLAG = "flag"
    BLOCK = "block"


@dataclass
class ScanResult:
    stage: str
    verdict: Verdict
    risk_score: float
    detections: list[dict] = field(default_factory=list)
    top_terms: list[tuple[str, float]] = field(default_factory=list)

    def as_dict(self) -> dict:
        data = asdict(self)
        data["verdict"] = self.verdict.value
        return data


def _max_severity(detections: list[Detection]) -> Severity | None:
    order = {Severity.LOW: 0, Severity.MEDIUM: 1, Severity.HIGH: 2}
    if not detections:
        return None
    return max((d.severity for d in detections), key=lambda s: order[s])


class Shield:
    def __init__(
        self, classifier: InjectionClassifier | None = None, settings: Settings | None = None
    ) -> None:
        self.settings = settings or get_settings()
        self.classifier = classifier or InjectionClassifier().fit()

    def scan_input(self, text: str) -> ScanResult:
        detections = scan_injection(text)
        prob = self.classifier.injection_probability(text)
        severity = _max_severity(detections)

        # Rule severity sets a floor on the risk score.
        floor = {None: 0.0, Severity.LOW: 0.3, Severity.MEDIUM: 0.6, Severity.HIGH: 0.95}[severity]
        risk = round(max(prob, floor), 4)

        if severity is Severity.HIGH or prob >= self.settings.block_threshold:
            verdict = Verdict.BLOCK
        elif severity is Severity.MEDIUM or prob >= self.settings.flag_threshold:
            verdict = Verdict.FLAG
        else:
            verdict = Verdict.ALLOW

        return ScanResult(
            stage="input",
            verdict=verdict,
            risk_score=risk,
            detections=[asdict(d) | {"severity": d.severity.value} for d in detections],
            top_terms=self.classifier.top_terms(text),
        )

    def scan_output(self, text: str) -> ScanResult:
        detections = scan_secrets(text) + scan_prompt_leak(
            text, self.settings.system_prompt_canary
        )
        verdict = Verdict.BLOCK if detections else Verdict.ALLOW
        risk = 1.0 if detections else 0.0
        return ScanResult(
            stage="output",
            verdict=verdict,
            risk_score=risk,
            detections=[asdict(d) | {"severity": d.severity.value} for d in detections],
        )
