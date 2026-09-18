# define-product-metrics

Metric dictionary with a reproducible calculation contract, baselines and targets, guardrails, instrumentation needs and acceptance scenarios. Deliverable: `output/metrics-<slug>.md` with a download link.

## Files

- `skill.md`: the skill. English text; the document and the reply follow the member's language.
- `references/template.md`: document template, read on demand by the skill.
- `references/LICENSE.upstream.txt`: the upstream MIT licence, verbatim.

## Provenance

Method adapted from [phuryn/pm-skills](https://github.com/phuryn/pm-skills) by Pawel Huryn (MIT), pinned at `8607e3b077817f89bf4a9b623246219734ac3be0`:

- [metrics-dashboard](https://github.com/phuryn/pm-skills/blob/8607e3b077817f89bf4a9b623246219734ac3be0/pm-product-discovery/skills/metrics-dashboard/SKILL.md)
- [north-star-metric](https://github.com/phuryn/pm-skills/blob/8607e3b077817f89bf4a9b623246219734ac3be0/pm-marketing-growth/skills/north-star-metric/SKILL.md)
- [LICENSE](https://github.com/phuryn/pm-skills/blob/8607e3b077817f89bf4a9b623246219734ac3be0/LICENSE)

EFP additions: the calculation contract (entity, formula, denominator, window, time zone, deduplication, missing-data handling), guardrails per outcome, the instrumentation map with evidence status, acceptance scenarios, the `output/` deliverable contract, runtime CLI inputs, and hand-offs. Attribution does not imply endorsement by the upstream author.
