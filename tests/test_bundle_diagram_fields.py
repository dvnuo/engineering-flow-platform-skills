"""Optional Mermaid diagrams in the plan, runbook and test-case artifacts."""

from __future__ import annotations

from pathlib import Path

from shared_diagram_fields import DIAGRAMS_PROMPT, MAX_DIAGRAMS, normalize_diagrams


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_SKILLS = (
    "generate_implementation_plan_from_bundle",
    "generate_runbook_from_bundle",
    "design_test_cases_from_bundle",
)


def test_normalize_keeps_only_entries_with_mermaid_source():
    diagrams = normalize_diagrams(
        [
            {"title": " Rollout ", "caption": "who calls whom", "mermaid": " flowchart LR\n  A --> B \n"},
            {"title": "no body"},
            {"mermaid": "   "},
            "not a dict",
            {"mermaid": "sequenceDiagram\n  A->>B: hi", "title": 42},
        ]
    )
    assert diagrams == [
        {"title": "Rollout", "caption": "who calls whom", "mermaid": "flowchart LR\n  A --> B"},
        {"mermaid": "sequenceDiagram\n  A->>B: hi"},
    ]


def test_normalize_drops_init_directives_and_caps_the_count():
    source = "%%{init: {'theme': 'dark'}}%%\nflowchart TD\n  A --> B"
    assert normalize_diagrams([{"mermaid": source}]) == [{"mermaid": "flowchart TD\n  A --> B"}]
    many = [{"mermaid": f"flowchart TD\n  A{i} --> B{i}"} for i in range(MAX_DIAGRAMS + 3)]
    assert len(normalize_diagrams(many)) == MAX_DIAGRAMS


def test_normalize_rejects_non_list_input():
    assert normalize_diagrams(None) == []
    assert normalize_diagrams({"mermaid": "flowchart TD"}) == []
    assert normalize_diagrams("flowchart TD") == []


def test_prompt_pins_official_mermaid_and_makes_diagrams_optional():
    assert "top-level key diagrams" in DIAGRAMS_PROMPT
    assert "official Mermaid source only" in DIAGRAMS_PROMPT
    assert "%%{init}" in DIAGRAMS_PROMPT
    assert "otherwise return an empty array" in DIAGRAMS_PROMPT


def test_document_skills_ask_for_diagrams_and_write_them_when_present():
    for name in DOCUMENT_SKILLS:
        skill_py = (ROOT / name / "skill.py").read_text(encoding="utf-8")
        assert "from skills.shared_diagram_fields import DIAGRAMS_PROMPT, normalize_diagrams" in skill_py, name
        assert "+ DIAGRAMS_PROMPT" in skill_py, name
        assert 'diagrams = normalize_diagrams(structured.get("diagrams"))' in skill_py, name
        assert 'payload["diagrams"] = diagrams' in skill_py, name
        skill_md = (ROOT / name / "skill.md").read_text(encoding="utf-8")
        assert "`diagrams`" in skill_md, name
