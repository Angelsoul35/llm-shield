# ADR 0001: Defence in depth — rules and a classifier together

## Status

Accepted.

## Context

Prompt-injection defence can be built from deterministic rules (regexes for known
attack phrases) or from a learned classifier. Each has a failure mode that the
other does not:

- **Rules** are precise and instant on the patterns they encode and never
  false-negative on them, but an attacker who rephrases around the pattern is
  invisible to them.
- **A classifier** generalises to phrasing it was not explicitly given, but is
  probabilistic — it can be wrong on genuinely novel input, and a single
  threshold is a single point of failure.

Choosing only one leaves a known gap.

## Decision

Run **both** on every input and combine them so rule severity sets a floor under
the classifier probability:

```
risk = max(classifier_probability, severity_floor)
```

A high-severity rule blocks outright; the classifier independently blocks novel
attacks with no matching rule. The layers are monotonic: the rule layer can only
raise risk, never lower it.

## Consequences

- **No false negatives on known patterns**, and coverage of novel ones from the
  model — each layer covers the other's weakness.
- **Explainable.** A block names either the rule(s) that fired or the top word
  features that drove the score.
- **Tunable without code.** The classifier thresholds are configuration; an
  operator trades recall against false positives for their traffic.
- **Trade-off.** Two mechanisms are more to maintain than one, and the model adds
  some false positives on benign text near the decision boundary. The `flag`
  verdict (review rather than block) and the tunable thresholds absorb that,
  which is the right place to make the precision/recall call.
