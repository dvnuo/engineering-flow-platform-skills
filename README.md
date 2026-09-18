# engineering-flow-platform-skills (business branch)

Skills for the **Business Assistant** in Engineering Flow Platform (EFP): requirements, planning and analysis work for Product Managers (PM) and Business Analysts (BA). Portal clones this branch into each Business Assistant runtime container at `/app/skills`, and the native agent discovers every `<skill-name>/skill.md` under it.

`master` carries the full skill library. This branch is a curated subset for the native agent: no repository tooling, no `skill.py` executors, no OpenCode metadata. A skill may ship its own scripts that the agent runs through the shell, as `pptx` does. Copy a skill directory from `master` when the role needs it; do not merge `master` into this branch.

## Skills

| Task | Skill | Deliverable |
| --- | --- | --- |
| Validate a user problem or opportunity | [product-discovery](product-discovery/skill.md) | `output/discovery-<slug>.md` |
| Rank candidates and sequence a roadmap | [prioritize-roadmap](prioritize-roadmap/skill.md) | `output/roadmap-<slug>.md` |
| Define success metrics | [define-product-metrics](define-product-metrics/skill.md) | `output/metrics-<slug>.md` |
| Write or revise a PRD | [write-product-requirements](write-product-requirements/skill.md) | `output/prd-<slug>.md` |
| Split requirements into epics and stories | [break-down-user-stories](break-down-user-stories/skill.md) | `output/stories-<slug>.md` and `.csv` |
| Judge whether requirements can be handed over | [review-requirements-readiness](review-requirements-readiness/skill.md) | `output/readiness-<slug>.md` |
| Map a business process and its rules | [analyze-business-process](analyze-business-process/skill.md) | `output/process-<slug>.md` |
| Assess a requirement change | [analyze-requirement-change](analyze-requirement-change/skill.md) | `output/change-<slug>.md` |
| Build a PowerPoint deck from a request or source material | [pptx](pptx/skill.md) | `output/<slug>.pptx`, built by its `scripts/build_deck.py` (python-pptx is in the runtime image) |
| Create Jira issues from a CSV | [jira-bulk-create-from-csv](jira-bulk-create-from-csv/skill.md) | Jira issues, after a mapping table and a dry run |
| Work a Jira issue assigned through a Portal delegation | [delegation-jira-assignee](delegation-jira-assignee/skill.md) | Status comment body returned to Portal |
| Answer a Jira mention delivered through a Portal delegation | [delegation-jira-mention](delegation-jira-mention/skill.md) | Status comment body returned to Portal |

The eight PM/BA skills are prompt-only. They work from what the member supplies (attached files under `uploads/`, pasted text, or Jira, Confluence and GitHub sources fetched with the runtime CLIs) and write a reviewable Markdown document under `output/`, announced with a `workspace:` download link. Skill text is English; the document and the reply follow the member's language. The stories CSV is the input for `jira-bulk-create-from-csv`. The two delegation skills are selected by name in a Portal delegation rule.

Example: `/write-product-requirements Draft a PRD for invoice approval from the attached interview notes; separate facts from assumptions and list the acceptance criteria still to confirm.`

## How the native agent uses a skill

- Only `name` and `description` from the frontmatter reach the model. A skill is activated by a `/<skill-name>` line, by the agent profile, or by the model choosing it from the description, so the description says what the skill produces and when to use it.
- The body of an active skill is injected in full. Files next to `skill.md` (for example `references/template.md`) are read on demand with the `read` tool or `skill(name, file=...)`.
- Deliverables go under `output/` in the workspace, and the reply links them as `[Download x.md](workspace:output/x.md)`; Portal turns that into a download link.

## Layout

```text
/app/skills/                      <- this repository root
  <skill-name>/skill.md           <- frontmatter: name, description; then the instructions
  <skill-name>/references/...     <- templates and other files the skill reads on demand
  <skill-name>/README.md          <- provenance for adapted methods (upstream links, licence)
```

- The repository root is the skills root. Do not create a nested `skills/` directory.
- `name` must equal the directory name. Everything else in the frontmatter is ignored by the runtime, so leave it out.
- Skills adapted from open-source material keep the upstream licence verbatim in `references/LICENSE.upstream.txt` and pin the upstream commit in their `README.md`.

## Updating deployed agents

After a change on this branch, either update the assistant type's skill branch or version in Portal, or restart the Kubernetes deployment so `/app/skills` is cloned again. Merging alone does not update running agents.

CI checks that every `<skill-name>/skill.md` has a frontmatter `name` equal to its directory, a `description`, no duplicate names, and no Chinese text in the skill body outside a worked example section.
