# PM / BA skills adoption

Evaluated on 2026-09-18 (Hong Kong time) for Product Managers (PM) and Business Analysts (BA) using the Business Assistant (`business` branch) and the full library (`master`). Four upstream repositories were read at the pinned commits below; later upstream changes do not flow into EFP automatically.

## Sources and decisions

| Repository and pinned commit | Decision | Adopted | Not adopted |
| --- | --- | --- | --- |
| [phuryn/pm-skills](https://github.com/phuryn/pm-skills/tree/8607e3b077817f89bf4a9b623246219734ac3be0) | Main PM method source, MIT | Evidence to opportunity, assumption and experiment; prioritisation; outcome roadmap; metric design | The plugin and command chains, marketing copy, pricing, SQL and statistics tools |
| [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD/tree/0a00053409731db811f2595ceb521dff9dde9a19) | Requirements delivery method source, MIT | PRD scope and traceability, value-sliced stories, readiness gate, change-reason categories and impact walk | Personas, menus, installer, `_bmad` state directory, orchestration and the full development loop |
| [deanpeters/Product-Manager-Skills](https://github.com/deanpeters/Product-Manager-Skills/tree/1b5a524ebb95e9497fa3f25002d8b8ec528d4444) | Evaluated, no text copied or adapted | Candidate methods for discovery, prioritisation, roadmap and metrics can be evaluated separately later | CC BY-NC-SA 4.0 with share-alike; this repository is public and carries no compatible licence, so its text is not redistributed here |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills/tree/19392f7a08264ed00486a251f5b2098321771f94) | Supplementary PM/BA structure, MIT | PRD templates, journey mapping, story and acceptance structure, the working-versus-waiting time view from process-mapper | Whole-repository mirroring, hard-coded score thresholds and capacities, English word-frequency interview scripts, unverified statistics tools |

Licence check: [phuryn MIT](https://github.com/phuryn/pm-skills/blob/8607e3b077817f89bf4a9b623246219734ac3be0/LICENSE), [BMAD MIT](https://github.com/bmad-code-org/BMAD-METHOD/blob/0a00053409731db811f2595ceb521dff9dde9a19/LICENSE), [deanpeters CC BY-NC-SA](https://github.com/deanpeters/Product-Manager-Skills/blob/1b5a524ebb95e9497fa3f25002d8b8ec528d4444/LICENSE), [claude-skills MIT](https://github.com/alirezarezvani/claude-skills/blob/19392f7a08264ed00486a251f5b2098321771f94/LICENSE).

The deanpeters [README licence note](https://github.com/deanpeters/Product-Manager-Skills/blob/1b5a524ebb95e9497fa3f25002d8b8ec528d4444/README.md#license) allows use at work, including at for-profit companies, and requires adaptations to be shared under the same licence with credit. The reason for not adopting is the redistribution boundary of this public skills repository, not a claim that internal use is forbidden.

Each adopted skill directory carries the full upstream licence in `references/LICENSE.upstream.txt` and a `README.md` with the pinned source links, so a single skill and its OpenCode copy keep the notice. The BMAD licence is accompanied by a trademark notice; attribution does not imply endorsement.

## Closest upstream analogues for the BA skills

`analyze-business-process` and `analyze-requirement-change` are EFP-authored. The closest upstream analogues, all MIT, were read and are cited in the skill READMEs rather than claimed absent:

- [bmad-correct-course](https://github.com/bmad-code-org/BMAD-METHOD/tree/0a00053409731db811f2595ceb521dff9dde9a19/skills/bmad-correct-course): change impact across PRD, epics, architecture and UX during a sprint; its reason categories and impact walk are reused, its workflow runtime and proposal format are not.
- [bmad-agent-analyst](https://github.com/bmad-code-org/BMAD-METHOD/tree/0a00053409731db811f2595ceb521dff9dde9a19/skills/bmad-agent-analyst): a persona-driven BA agent; EFP does not use personas.
- [process-mapper](https://github.com/alirezarezvani/claude-skills/tree/19392f7a08264ed00486a251f5b2098321771f94/business-operations/skills/process-mapper): BPMN-style process documentation with cycle-time and bottleneck scripts; only the working-versus-waiting time view is reused, without its scripts or fixed thresholds.

## First batch

| EFP skill | Inputs | Deliverable and boundary |
| --- | --- | --- |
| [product-discovery](../product-discovery/skill.md) | User problem, interviews, feedback and their sources | `output/discovery-<slug>.md`: evidence log, opportunities, assumptions, test cards; a research plan when no material exists |
| [prioritize-roadmap](../prioritize-roadmap/skill.md) | Candidates, goals, constraints, sourced estimates | `output/roadmap-<slug>.md`: reviewable ranking and Now/Next/Later roadmap; qualitative ranking when data is short, no invented RICE inputs or dates |
| [define-product-metrics](../define-product-metrics/skill.md) | Business goals, user behaviour, data situation | `output/metrics-<slug>.md`: calculation contracts, guardrails, events and data checks; no invented baselines |
| [write-product-requirements](../write-product-requirements/skill.md) | Problem, research, process and business rules | `output/prd-<slug>.md`: PRD with stable IDs, acceptance criteria and evidence chain; unknown thresholds stay `To confirm` |
| [break-down-user-stories](../break-down-user-stories/skill.md) | PRD or identified requirements | `output/stories-<slug>.md` and `.csv`: epics, stories, acceptance criteria, coverage matrix; Jira creation only through `jira_bulk_create_from_csv` |
| [review-requirements-readiness](../review-requirements-readiness/skill.md) | Requirements and delivery material of one version | `output/readiness-<slug>.md`: evidenced verdict, findings, closing conditions; unread material is never reported as reviewed |
| [analyze-business-process](../analyze-business-process/skill.md) | Current process, roles, rules, exceptions | `output/process-<slug>.md`: as-is and to-be process, decision tables, gaps; proposals never mixed with confirmed facts |
| [analyze-requirement-change](../analyze-requirement-change/skill.md) | Baseline, change request, existing trace links | `output/change-<slug>.md`: diff, trace matrix, options, decision record; preliminary only when the baseline is missing |

Discovery, prioritisation, PRD, stories and metrics appear in several upstream repositories. EFP merges them into one entry per member task so a request does not match several near-synonymous skills. The two BA skills complete the BA side rather than equating PM growth frameworks with BA work.

## EFP integration conventions

1. The repository root is the skills root. Each skill is `<skill-name>/skill.md` plus `references/` and a `README.md` for provenance; no nested `skills/` directory and no generated `.opencode/`.
2. All eight are `tools: []`, `execution_kind: prompt_only`, `compatibility: full`, `permission.default: ask`, with no Python executor, third-party dependency or upstream installer. `full` means the prompt and its resources are consumable by the OpenCode adapter; it is not business acceptance of the output.
3. In the native agent only `name` and `description` drive activation: a `/<skill-name>` line, the agent profile, or the model choosing the skill by description. The `triggers` list is documentation for the validator and Portal, so every description states what the skill produces and when to use it.
4. The deliverable is a Markdown file under `output/` (`output/<prefix>-<slug>.md`, plus a CSV for stories) with a `workspace:` download link in the reply; revisions rewrite the same path. This follows the `pptx` skill and the runtime's deliverables contract.
5. Inputs come from the member's message, attached files under `uploads/` read with the read tool, and Jira, Confluence or GitHub sources fetched through bash with the runtime CLIs (`jira`, `confluence`, `gh`, always `--json`). `tools: []` does not limit the agent's toolset; it declares that the skill needs no native tool mapping.
6. Skill text is English. Each skill writes the document and the reply in the language the member used and keeps IDs and headings stable.
7. Hand-offs stay explicit: the PRD keeps the `requirements.yaml` buckets (`functional_requirements`, `business_rules`, `acceptance_criteria`, `edge_cases`) used by `collect_requirements_to_bundle`; the stories CSV is the input of `jira_bulk_create_from_csv`; readiness feeds `generate_implementation_plan_from_bundle` and `design_test_cases_from_bundle`. Analysis drafts never overwrite `requirements.yaml` and never create Jira issues.
8. `master` carries the full library; `business` carries the Business Assistant subset. New skills, templates and docs go to both branches. Merging does not update deployed agents; follow the README's skill branch or version update.

## Reusable review scenarios

These scenarios check behaviour after reading the skill; keyword matching is not a substitute for output quality.

| Scenario | Check the actual deliverable |
| --- | --- |
| Two interview notes cover the same respondent; a third contradicts them | Repeated mentions are not counted as separate users; the counter-example and the sample limit stay; without findings only a plan is delivered |
| Feature A gives monthly reach, B yearly reach, C has no effort | No mixed RICE; conversion assumptions and gaps stated; a hard dependency is not overridden by a score; no invented dates |
| "Improve retention" with no data and no events | Eligible population, denominator, window and events defined; baseline and target `To confirm`; no claimed uplift |
| The PRD says "fast approval"; rejection and withdrawal are undefined | Traceable requirements with quantified thresholds `To confirm`; stories expose the exception branches; the readiness review names the decision gap |
| Two documents define the same requirement differently; stories cover the success path only | Both versions cited with locations; the conflict kept; the coverage matrix shows the omission; no overall `ready` |
| An amount sits exactly on an approval threshold and two rules match | The decision table shows the overlap or gap; undecidable cases become questions, not a silent choice |
| A refund rule change without the original baseline or downstream mapping | Preliminary impact and a verification list; unsupplied services, tests or owners are never presented as confirmed impact |

Structural validation uses the repository's validator, contract exporter, pytest and smoke script. `tests/test_pm_ba_skills_contract.py` checks the frontmatter, the English-only text, the deliverable clauses and the provenance READMEs; behaviour reviews are recorded in the pull request.

## Candidates for later

Evaluate after the first batch has been used on real requirements. All MIT unless noted:

- Meeting notes to decisions and actions ([phuryn summarize-meeting](https://github.com/phuryn/pm-skills/tree/8607e3b077817f89bf4a9b623246219734ac3be0/pm-execution/skills/summarize-meeting)).
- Stakeholder map and communication plan ([phuryn stakeholder-map](https://github.com/phuryn/pm-skills/tree/8607e3b077817f89bf4a9b623246219734ac3be0/pm-execution/skills/stakeholder-map)).
- Feedback and feature-request triage ([phuryn analyze-feature-requests](https://github.com/phuryn/pm-skills/tree/8607e3b077817f89bf4a9b623246219734ac3be0/pm-product-discovery/skills/analyze-feature-requests)).
- Pre-mortem risk review of a PRD or launch plan ([phuryn pre-mortem](https://github.com/phuryn/pm-skills/tree/8607e3b077817f89bf4a9b623246219734ac3be0/pm-execution/skills/pre-mortem)), possibly as a mode of `review-requirements-readiness`.
- Product brief or one-pager before the PRD ([bmad-product-brief](https://github.com/bmad-code-org/BMAD-METHOD/tree/0a00053409731db811f2595ceb521dff9dde9a19/skills/bmad-product-brief)).
- Release notes from merged pull requests and Jira issues ([phuryn release-notes](https://github.com/phuryn/pm-skills/tree/8607e3b077817f89bf4a9b623246219734ac3be0/pm-execution/skills/release-notes)), using the `gh` and `jira` CLIs.
- EFP-native ideas without an upstream: extracting requirements from a Confluence page, checking a Jira epic against its PRD, and a UAT plan or sign-off checklist.

Not adopted: deanpeters skills (licence, see above); claude-skills `jira-expert` and `confluence-expert` (administration-oriented and overlapping with the EFP CLIs); phuryn `test-scenarios` (overlaps `design_test_cases_from_bundle`); phuryn `sprint-plan` (a delivery-team task). Before adding calculation scripts, verify formulas, units, boundaries and data dependencies separately; before adding new source text, re-check the pinned licence. Do not mirror repositories on the strength of star counts or skill totals.

This evaluation covers the listed PM/BA items and their reference files; it is not a quality endorsement of the four repositories as a whole.
