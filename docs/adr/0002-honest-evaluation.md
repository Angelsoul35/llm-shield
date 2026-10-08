# ADR 0002: Honest evaluation over a family-disjoint split

## Status

Accepted.

## Context

The project trains on synthetic prompts, and the easy, tempting evaluation —
split the synthetic set into train/test at random — produces ~1.0 accuracy. That
number is a lie: when both splits come from the same few templates, the test
items are near-duplicates of training items, so the model is graded on
memorisation, not generalisation. A guardrail that quotes that number would give
false confidence and hide real weaknesses (false positives on benign text,
missed novel attacks).

## Decision

Two measures together:

1. **Generate adversarially.** Prompts come from many families with **overlapping
   vocabulary** — benign prompts deliberately contain attack-adjacent words
   (*instructions*, *system*, *ignore*, *mode*). This removes the single-keyword
   shortcut and forces the model to learn combinations.
2. **Evaluate family-disjoint.** `evaluation.py` holds whole prompt families out
   of training, so the test phrasings are structurally unseen. It reports the
   grouped accuracy, the train accuracy, and the gap between them.

The README quotes the **family-disjoint** figure (~0.79), not the
within-distribution one.

## Consequences

- **The reported number means something.** It estimates performance on an attack
  or benign *style* not present in training — the situation that matters in
  production.
- **Overfitting is measured, not assumed.** The train/test gap is reported and
  bounded by a test; a blown-out gap would fail CI.
- **Weaknesses are visible.** Holding out whole attack families surfaces exactly
  where the model is blind, which is why the rules and thresholds exist.
- **Trade-off.** The honest number is much lower and less impressive than ~1.0,
  and the harder data makes the task genuinely harder. That is the point: a
  defensive tool must be evaluated pessimistically, and the conservative figure is
  the baseline a real deployment's retraining is expected to beat.
