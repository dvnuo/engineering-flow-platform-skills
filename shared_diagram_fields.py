"""Optional Mermaid diagrams carried by document-shaped bundle artifacts.

The implementation plan, runbook and test-case artifacts are YAML documents
synthesised from strict-JSON model output. Where a flow, sequence or lifecycle
is clearer drawn than listed, the model may add a top-level ``diagrams`` list;
each entry carries Mermaid source that Portal renders inline and that pastes
unchanged into GitHub markdown or Confluence Gliffy. Everything else the model
puts under that key is dropped here rather than written into the bundle.
"""

from __future__ import annotations

from typing import Any, Dict, List

DIAGRAMS_PROMPT = (
    "Optionally include a top-level key diagrams: an array of objects with keys "
    "title, caption and mermaid. mermaid holds official Mermaid source only "
    "(flowchart, sequenceDiagram or stateDiagram-v2; no %%{init} directives, no "
    "HTML in labels, quote labels that contain punctuation), one diagram per "
    "entry, at most 25 nodes. Add a diagram only where a flow, sequence or "
    "lifecycle is clearer drawn than listed; otherwise return an empty array."
)

MAX_DIAGRAMS = 5
_TEXT_FIELDS = ("title", "caption")


def _clean_mermaid(source: Any) -> str:
    """Return trimmed Mermaid source without directive lines, or "" when unusable."""
    if not isinstance(source, str):
        return ""
    lines = [line.rstrip() for line in source.replace("\r\n", "\n").split("\n")]
    # %%{init: ...}%% directives restyle the renderer; Portal owns the theme.
    kept = [line for line in lines if not line.lstrip().startswith("%%{")]
    return "\n".join(kept).strip()


def normalize_diagrams(value: Any) -> List[Dict[str, str]]:
    """Keep only well-formed diagram entries: a Mermaid body plus optional title/caption."""
    if not isinstance(value, list):
        return []
    diagrams: List[Dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        mermaid = _clean_mermaid(item.get("mermaid"))
        if not mermaid:
            continue
        entry: Dict[str, str] = {}
        for key in _TEXT_FIELDS:
            text = item.get(key)
            if isinstance(text, str) and text.strip():
                entry[key] = text.strip()
        entry["mermaid"] = mermaid
        diagrams.append(entry)
        if len(diagrams) >= MAX_DIAGRAMS:
            break
    return diagrams
