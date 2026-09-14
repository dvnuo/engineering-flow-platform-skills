# Deck spec and layout guide

`scripts/build_deck.py` turns one JSON file into a 16:9 `.pptx`. Everything is
drawn on a blank layout, so the look is the same whichever template the deck
starts from. This page is the schema reference; `spec-example.json` is a
complete, buildable example (`python build_deck.py --print-example`).

## Top-level fields

| Field      | Required | Notes |
| ---------- | -------- | ----- |
| `title`    | yes*     | Deck title. Used for the automatic title slide and the file name. *Optional only when the first slide is an explicit `title` slide. |
| `subtitle` | no       | Shown under the title on the title slide. |
| `author`   | no       | Shown with `date` at the bottom of the title slide and stored as the file's author. |
| `date`     | no       | Free text, e.g. `2026-09-14`. |
| `footer`   | no       | Small text bottom-left on every content slide. |
| `output`   | no       | Relative path of the file to write. `--output` on the command line wins. Default `output/<slug-of-title>.pptx`. |
| `theme`    | no       | See below. |
| `slides`   | yes      | Non-empty list of slide objects. If the first slide is not a `title` slide, one is generated from `title`/`subtitle`. |

## Theme

All colours are 6-digit hex without `#`. Missing keys fall back to the default.

```json
"theme": {
  "primary": "1F3A5F",        // title text, title-slide background, first series
  "accent": "E07A1F",         // rules, bullets, second series
  "text": "1F2933",
  "muted": "6B7280",
  "background": "FFFFFF",
  "light": "F3F4F6",          // KPI cards, alternate table rows
  "font": "Calibri",
  "title_font": "Calibri",    // defaults to font
  "east_asian_font": "Microsoft YaHei"   // optional; set for Chinese/Japanese/Korean decks
}
```

Use the member's brand colours when they give them; otherwise keep the default
navy/orange pair. Never pick more than two accent colours.

## Slide types

Every slide object has a `type`. `notes` (speaker notes, string) is accepted on
every type. Titles should be a takeaway sentence, not a topic label
("Adoption grew 38% in Q3", not "Adoption").

| `type`       | Fields | Use for |
| ------------ | ------ | ------- |
| `title`      | `title`, `subtitle` | Opening slide. Usually omitted; the deck `title` generates one. |
| `section`    | `title`, `subtitle` | Divider between parts of a longer deck. |
| `bullets`    | `title`, `bullets` | The default content slide. `bullets` is a list of strings or `{ "text": "...", "level": 0..2 }`. |
| `two_column` | `title`, `left`, `right` | Comparison, before/after, pros/cons. Each column: `heading`, `text` and/or `bullets`. |
| `image`      | `title`, `image`, `caption` | A screenshot, diagram or chart image. `image` is a path relative to the spec file or the workspace; it must exist. The picture is scaled to fit. |
| `table`      | `title`, `headers`, `rows` | Small numeric or comparison tables. `rows` is a list of lists; up to 12 rows × 8 columns. |
| `chart`      | `title`, `chart` | Native, editable charts. `chart.kind` is `column`, `bar`, `line`, `pie` or `doughnut`; `categories` is a list; `series` is a list of `{ "name", "values" }` with one number per category. Optional `chart.title`, `chart.data_labels: true`. |
| `kpi`        | `title`, `metrics` | 1–6 headline numbers. Each metric: `value`, `label`, optional `description`. |
| `quote`      | `quote`, `attribution` | A customer or stakeholder quote. |
| `closing`    | `title`, `subtitle` | Last slide. `title` defaults to "Thank you". |

## Content rules the validator enforces or warns about

- One idea per slide. More than 8 bullets, or more than ~700 characters of
  bullet text, gets a warning: split the slide instead of shrinking the font.
- Bullets over 120 characters get a warning: shorten them and put the detail in
  `notes`.
- Titles over 70 characters get a warning.
- Chart series must have exactly one numeric value per category. Pie charts
  use only the first series.
- Image paths must exist at validation time. Never invent a path; generate the
  image first (for example with matplotlib or `browser screenshot`) or use a
  `chart` slide with the real numbers instead.
- More than 40 slides gets a warning; move supporting material to an appendix
  section or a second deck.

## Typical deck shapes

- **Status / readout (8–12 slides)**: title → agenda → 1–2 `kpi`/`chart` →
  `section` per theme with 2–3 `bullets`/`two_column` → risks → closing.
- **Proposal (6–10 slides)**: title → problem (`bullets`) → options
  (`two_column` or `table`) → recommendation (`bullets`) → plan (`table`) →
  ask (`kpi` or `bullets`) → closing.
- **Training / walkthrough**: `section` dividers between modules, `image`
  slides for screenshots, `notes` carrying the narration.

## Language

Write slide text in the language the member used. For Chinese, Japanese or
Korean decks set `theme.east_asian_font` (for example `Microsoft YaHei` or
`Noto Sans CJK SC`) so PowerPoint does not fall back to a serif font.
