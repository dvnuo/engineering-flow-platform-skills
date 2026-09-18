---
name: pptx-brand
description: "Make a deck in the company brand (EFP sample brand with four styles: formal, review, keynote, training) using the pptx engine with the brand template, backgrounds, icons, logo and style rules shipped in this skill. Use together with pptx when a member wants a deck in the company style, mentions the corporate template, brand colours, logo or 'our format', or when the deck will be shown outside the team or archived; not for a quick outline in chat."
---

# Brand decks (EFP sample brand)

This skill turns `/pptx` into an on-brand deck. Everything company specific
lives here: the style rules (`references/style-guide.md`), the asset catalogue
(`references/assets.md`), the text examples (`references/text-examples.md`) and
the machine-readable styles (`references/styles.json`). The engine in
`/app/skills/pptx` renders; do not copy its rules here and do not hand-write
python-pptx code.

The sample brand is called EFP and all assets under `assets/` are placeholders.
To adopt a real brand, replace the files and keep the names, or edit
`styles.json` and `assets.md`.

## Non-negotiable rules

1. Load `/pptx` first and follow its workflow and delivery rules; this skill
   adds constraints, it does not replace them.
2. Pick exactly one style from `styles.json` (`formal`, `review`, `keynote`,
   `training`) using the decision table in the style guide, and build with
   `--styles` and `--style`. Never mix styles in one deck.
3. Use only assets listed in `references/assets.md`, by absolute path under
   `/app/skills/pptx-brand/assets/`. Never invent an image path.
4. Icons: `assets/icons/navy/` on light pages, `assets/icons/white/` on dark
   pages and photo backgrounds. Never both on one page.
5. Backgrounds only on title, section, closing and quote slides. The style
   already sets sensible defaults; override per slide only with a reason.
6. The logo is placed by the style; do not add logo images to slides.
7. Every fact on a slide comes from the member, an attachment or a tool
   result. Titles are conclusions, not topics (see the text examples).

## Workflow

### 1. Choose the style

Read `references/style-guide.md` section 2. Decide from audience and occasion;
ask only when the answer would change the whole deck (for example an external
customer deck versus an internal review). Say which style you chose in the
reply.

### 2. Read the brand references you need

```bash
cat /app/skills/pptx-brand/references/style-guide.md
cat /app/skills/pptx-brand/references/assets.md
cat /app/skills/pptx-brand/references/text-examples.md
python /app/skills/pptx/scripts/build_deck.py --list-styles --styles /app/skills/pptx-brand/references/styles.json
```

When a member supplies a new template or icon sheet, describe it first:

```bash
python /app/skills/pptx/scripts/inspect_template.py <template.pptx>
python /app/skills/pptx/scripts/slice_icons.py <sheet.png> --out .efp/pptx/icons --names <name1,name2,...>
```

### 3. Write the spec

Follow `/pptx` for the storyline and the schema. Add at the top of the spec:

```json
"style": "formal",
"styles_file": "/app/skills/pptx-brand/references/styles.json"
```

Reference icons with absolute paths, for example
`/app/skills/pptx-brand/assets/icons/navy/users.png`. Match the deck shapes in
the text examples: `formal` opens with numbers, `keynote` has one idea per
slide, `training` is steps and screenshots.

### 4. Validate, build, verify

```bash
python /app/skills/pptx/scripts/build_deck.py .efp/pptx/<slug>.spec.json --validate-only
python /app/skills/pptx/scripts/build_deck.py .efp/pptx/<slug>.spec.json --output output/<slug>.pptx
```

The styles file named in the spec is picked up automatically; `--styles` and
`--style` on the command line override it. Fix every error and warning before
delivering. The summary reports the style and template that were used.

### 5. Deliver

As in `/pptx`: a short summary, the slide list, the
`[Download <slug>.pptx](workspace:output/<slug>.pptx)` link, and the style
name. Mention when a placeholder asset was used where the member's real
material would be better (for example a screenshot slide left out because no
screenshot was supplied).

## Example

Member: "用公司模板做一份三季度汇报，给管理层看" with `q3-notes.md` attached.

Assistant: style `formal` (leadership audience), reads the notes, drafts eleven
takeaway titles following the formal outline in the text examples, writes
`.efp/pptx/q3-review.spec.json` with the style header and navy icons on the KPI
page, validates, builds `output/q3-review.pptx`, then answers with the summary
and the download link.
