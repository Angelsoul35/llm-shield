"""Load the real deepset prompt-injection dataset.

The synthetic generator (:mod:`llm_shield.generate`) gives a controlled, family-
disjoint evaluation; this module loads **real** prompt-injection vs benign prompts
(the public ``deepset/prompt-injections`` dataset, vendored under ``datasets/``) and
runs the *same* classifier on them, so the real benchmark measures the same approach
on real attacks collected in the wild.

``fetch_prompt_injections`` refreshes the vendored copy from the Hugging Face
datasets-server.
"""

from __future__ import annotations

import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DATASET_PATH = _REPO_ROOT / "datasets" / "prompt_injections_real.jsonl"
_HF_ROWS_URL = (
    "https://datasets-server.huggingface.co/rows?dataset=deepset%2Fprompt-injections"
    "&config=default&split={split}&offset={offset}&length=100"
)


def load_prompt_injections(path: str | Path | None = None) -> tuple[list[str], list[int]]:
    """Return ``(texts, labels)``: real prompts and their label (1 = injection, 0 = benign)."""
    p = Path(path) if path is not None else _DATASET_PATH
    if not p.exists():
        raise FileNotFoundError(
            f"Vendored prompt-injection data not found at {p}. Run "
            "`python -c 'from llm_shield.real_data import fetch_prompt_injections as f; f()'`."
        )
    texts: list[str] = []
    labels: list[int] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        texts.append(str(row["text"]))
        labels.append(int(row["label"]))
    return texts, labels


def fetch_prompt_injections(dest: str | Path | None = None) -> int:
    """Download the real deepset prompt-injection dataset into ``datasets/``.

    Needs network access to the Hugging Face datasets-server. Returns the number of
    rows written. Only needed to create or refresh the vendored file.
    """
    import urllib.request

    target = Path(dest) if dest is not None else _DATASET_PATH
    rows: list[dict] = []
    for split in ("train", "test"):
        offset = 0
        while True:
            url = _HF_ROWS_URL.format(split=split, offset=offset)
            try:
                with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310 - fixed URL
                    payload = json.load(resp)
            except Exception:  # noqa: BLE001 - a missing split is simply skipped
                break
            batch = payload.get("rows", [])
            if not batch:
                break
            for row in batch:
                rows.append({"text": row["row"]["text"], "label": int(row["row"]["label"])})
            offset += 100
            if offset >= payload.get("num_rows_total", 0):
                break

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    return len(rows)
