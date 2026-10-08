"""Deterministic detectors for prompt-injection and data-leak patterns.

These are the fast, first line of defence: regular expressions and simple checks
that catch well-known attack and leak patterns with no model and no latency. They
are intentionally conservative and explainable — each hit names the pattern it
matched — and they run alongside the learned classifier for defence in depth.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class Detection:
    detector: str
    severity: Severity
    detail: str


# (compiled pattern, name, severity). High-severity patterns are direct attempts
# to override instructions, extract the system prompt, or disable safety.
_INJECTION_PATTERNS: list[tuple[re.Pattern[str], str, Severity]] = [
    (
        re.compile(
            r"ignore\s+(all\s+|the\s+|your\s+|any\s+)?(previous|prior|above|earlier)\s+"
            r"(instructions?|prompts?|messages?|context|rules?)",
            re.I,
        ),
        "override_instructions",
        Severity.HIGH,
    ),
    (
        re.compile(
            r"disregard\s+(all\s+|the\s+|your\s+)?(previous|prior|above)\s+"
            r"(instructions?|rules?)",
            re.I,
        ),
        "override_instructions",
        Severity.HIGH,
    ),
    (
        re.compile(r"forget\s+(everything|all|your|the)\s+(instructions?|rules?|above)", re.I),
        "override_instructions",
        Severity.HIGH,
    ),
    (
        re.compile(
            r"\b(reveal|print|show|repeat|output|tell\s+me)\b.{0,30}"
            r"(system\s+prompt|initial\s+(prompt|instructions?)|your\s+(instructions?|rules?))",
            re.I,
        ),
        "system_prompt_extraction",
        Severity.HIGH,
    ),
    (
        re.compile(
            r"\b(you\s+are\s+now|act\s+as|pretend\s+to\s+be)\b.{0,30}"
            r"(dan|stan|jailbroken|unrestricted|no\s+restrictions|evil)",
            re.I,
        ),
        "jailbreak_persona",
        Severity.HIGH,
    ),
    (re.compile(r"\bdo\s+anything\s+now\b", re.I), "jailbreak_persona", Severity.HIGH),
    (
        re.compile(r"\bbypass\b.{0,20}(safety|content|policy|filter|guardrail|restriction)", re.I),
        "bypass_safety",
        Severity.HIGH,
    ),
    (re.compile(r"\bdeveloper\s+mode\b", re.I), "jailbreak_persona", Severity.MEDIUM),
    (
        re.compile(r"</?\s*(system|instructions?|assistant)\s*>", re.I),
        "delimiter_injection",
        Severity.MEDIUM,
    ),
    (
        re.compile(r"\b(pretend|imagine|roleplay|role-play)\b.{0,20}\b(you|that)\b", re.I),
        "roleplay",
        Severity.MEDIUM,
    ),
    (
        re.compile(r"\bwithout\s+(any\s+)?(restrictions?|rules?|limitations?|filters?)\b", re.I),
        "bypass_safety",
        Severity.MEDIUM,
    ),
]

# Likely secrets if they appear in model OUTPUT.
_SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "openai_api_key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "aws_access_key"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "github_token"),
    (re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{20,}"), "bearer_token"),
    (re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"), "private_key"),
]

# A long base64-looking blob can hide an encoded instruction payload.
_BASE64_BLOB = re.compile(r"[A-Za-z0-9+/]{40,}={0,2}")


def scan_injection(text: str) -> list[Detection]:
    seen: set[tuple[str, str]] = set()
    detections: list[Detection] = []
    for pattern, name, severity in _INJECTION_PATTERNS:
        if pattern.search(text):
            key = (name, severity.value)
            if key not in seen:
                seen.add(key)
                detections.append(
                    Detection(detector=name, severity=severity, detail=f"matched {name} pattern")
                )
    if _BASE64_BLOB.search(text):
        detections.append(
            Detection(
                detector="encoded_payload",
                severity=Severity.MEDIUM,
                detail="long base64-like blob that may hide an encoded payload",
            )
        )
    return detections


def scan_secrets(text: str) -> list[Detection]:
    detections: list[Detection] = []
    for pattern, name in _SECRET_PATTERNS:
        if pattern.search(text):
            detections.append(
                Detection(
                    detector=name, severity=Severity.HIGH, detail=f"possible {name} in output"
                )
            )
    return detections


def scan_prompt_leak(text: str, canary: str) -> list[Detection]:
    """Detect the system-prompt canary leaking into output."""
    if canary and canary in text:
        return [
            Detection(
                detector="system_prompt_leak",
                severity=Severity.HIGH,
                detail="system-prompt canary found in output",
            )
        ]
    return []
