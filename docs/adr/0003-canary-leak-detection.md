# ADR 0003: Canary-based system-prompt leak detection

## Status

Accepted.

## Context

One of the attacks we must catch is the model being coaxed into revealing its
system prompt. Detecting this on the output side means deciding whether a given
response "contains the system prompt". Fuzzy-matching the prompt text against the
output is unreliable: it produces false positives when the output legitimately
quotes a sentence, and false negatives when the leak is paraphrased or partial,
and it requires the detector to hold the full prompt.

## Decision

Embed a **canary** — a short, unique, meaningless token — inside the application's
system prompt (configured via `LS_SYSTEM_PROMPT_CANARY`). The output detector does
a single exact-substring check for that canary. If it appears in output, the
system prompt has leaked, because the canary exists nowhere else.

## Consequences

- **Reliable and cheap.** An exact-match on a unique token has effectively no
  false positives and no false negatives for a verbatim leak, in O(n) time.
- **No prompt in the detector.** The detector only needs the canary, not the
  sensitive prompt text, so the secret is not duplicated into the guardrail.
- **Clear signal.** A canary hit is unambiguous evidence to block and alert.
- **Trade-off.** A canary catches a leak of the prompt *as written*; a model that
  paraphrases its instructions without emitting the canary would evade it. This is
  accepted: the canary is a high-precision tripwire for the common verbatim leak,
  and it is complemented by the secret detectors and by not putting truly
  sensitive data in the prompt in the first place. (The canary must be placed
  where a leak would carry it along, e.g. near the start of the system prompt.)
