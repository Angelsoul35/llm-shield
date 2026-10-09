# Datasets — real prompt-injection data

## `prompt_injections_real.jsonl` — deepset/prompt-injections

A **real**, public dataset of prompt-injection and benign prompts collected in the
wild, used to validate the classifier on real attacks (not only the synthetic
families).

| | |
|---|---|
| **Origin** | `deepset/prompt-injections` (Hugging Face), train + test splits merged |
| **Contents** | 662 prompts (263 injection / 399 benign), one JSON object per line: `{"text", "label"}` (1 = injection) |
| **Retrieved** | 2026-10-09, via the Hugging Face datasets-server |
| **License** | per the dataset card (research/educational use) |

Vendored so the benchmark and its tests run offline and deterministically;
`llm_shield.real_data.fetch_prompt_injections()` refreshes it. `llm_shield.real_benchmark`
trains the same word+char TF-IDF + logistic classifier on it and reports ~0.92 accuracy
/ 0.90 F1 / 0.98 ROC-AUC (cross-validated) — real attacks, well-fit, not a fake 1.0.
