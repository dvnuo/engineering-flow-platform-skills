# analyze-business-process

As-is and to-be business process analysis: steps with actors and hand-offs, business rules as decision tables, exceptions and recovery, gaps, and the hand-off to requirements. Deliverable: `output/process-<slug>.md` with a download link.

## Files

- `skill.md`: the skill. English text; the document and the reply follow the member's language.
- `references/template.md`: document template, read on demand by the skill.
- `references/LICENSE.upstream.txt`: the upstream MIT licence, verbatim.

## Provenance

EFP-authored BA method. The as-is / to-be mapping, the actor / decider distinction, the decision tables, the exception and recovery modelling and the requirement trace were written for EFP and are not claimed to come from any upstream skill.

Structural references, all from [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT), pinned at `19392f7a08264ed00486a251f5b2098321771f94`:

- [ux-researcher-designer](https://github.com/alirezarezvani/claude-skills/blob/19392f7a08264ed00486a251f5b2098321771f94/product-team/skills/ux-researcher-designer/SKILL.md): journey scope, steps and pain points.
- [product-manager-toolkit prd_templates.md](https://github.com/alirezarezvani/claude-skills/blob/19392f7a08264ed00486a251f5b2098321771f94/product-team/skills/product-manager-toolkit/references/prd_templates.md): requirement boundaries and risks.
- [process-mapper](https://github.com/alirezarezvani/claude-skills/blob/19392f7a08264ed00486a251f5b2098321771f94/business-operations/skills/process-mapper/SKILL.md): the working-versus-waiting time view used when the member supplies durations. Its Python scripts and fixed thresholds are not used.
- [LICENSE](https://github.com/alirezarezvani/claude-skills/blob/19392f7a08264ed00486a251f5b2098321771f94/LICENSE)

Closest upstream analogue not adapted: [bmad-agent-analyst](https://github.com/bmad-code-org/BMAD-METHOD/blob/0a00053409731db811f2595ceb521dff9dde9a19/skills/bmad-agent-analyst/SKILL.md) (a persona-driven BA agent; EFP does not use personas). Attribution does not imply endorsement by the upstream authors.
