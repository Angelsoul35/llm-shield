# ADR 0004: A three-way verdict (allow / flag / block)

## Status

Accepted.

## Context

A guardrail that only says "block" or "allow" forces every borderline case into
one of two bad choices: block legitimate traffic (annoying users, generating
support load) or allow a likely attack (defeating the point). Real traffic has a
grey zone — inputs that are suspicious but not clearly malicious — and a binary
gate cannot represent it.

## Decision

Return one of **three** verdicts:

- **block** — a high-severity rule fired, or the classifier probability is at or
  above the block threshold;
- **flag** — a medium-severity rule fired, or the probability is at or above the
  flag threshold (below block);
- **allow** — neither.

The two thresholds (`LS_BLOCK_THRESHOLD`, `LS_FLAG_THRESHOLD`) are configuration.

## Consequences

- **The grey zone has a home.** `flag` lets an application take a softer action —
  add friction, log for review, route to a human, or ask the user to rephrase —
  instead of a hard block.
- **Operator control.** The thresholds move the boundaries without code changes,
  so a high-stakes deployment can widen `block` and a tolerant one can rely on
  `flag`.
- **Honest about uncertainty.** A probabilistic classifier should not pretend to
  a binary certainty it does not have; three levels match the real confidence.
- **Trade-off.** `flag` only helps if the calling application does something with
  it; if ignored, it collapses to `allow`. That is the integrator's
  responsibility, and the verdict plus risk score give them what they need to act.
