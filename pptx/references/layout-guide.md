# Deck spec and layout guide

`scripts/build_deck.py` turns one JSON file into a 16:9 `.pptx`. Everything is
drawn on a blank layout, so the look is the same whichever template the deck
starts from. This page is the schema reference; `spec-example.json` is a
complete, buildable example (`python build_deck.py --print-example`).

## Top-level fields

| Field         | Required | Notes |
| ------------- | -------- | ----- |
| `title`       | yes*     | Deck title. Used for the automatic title slide and the file name. *Optional only when the first slide is an explicit `title` slide. |
| `subtitle`    | no       | Shown under the title on the title slide. |
| `author`      | no       | Shown with `date` at the bottom of the title slide and stored as the file's author. |
| `date`        | no       | Free text, e.g. `2026-09-14`. |
| `footer`      | no       | Small text bottom-left on every content slide. |
| `output`      | no       | Relative path of the file to write. `--output` on the command line wins. Default `output/<slug-of-title>.pptx`. |
| `template`    | no       | `.pptx`/`.potx` whose master, theme and slide size to reuse; its own slides are removed. `--template` wins. |
| `theme`       | no       | Colours and fonts, see below. |
| `logo`        | no       | Logo placed on every slide, see below. |
| `defaults`    | no       | `backgrounds` per slide type, `overlay`, `overlay_color`; see Backgrounds. |
| `style`       | no       | Name of a style in a styles file; with `styles_file` (or `--styles`) the style's theme, template, footer, logo and backgrounds are merged under the spec. Spec values win. |
| `styles_file` | no       | Path of the styles file; `--styles` on the command line wins. |
| `slides`      | yes      | Non-empty list of slide objects. If the first slide is not a `title` slide, one is generated from `title`/`subtitle`. |

## Theme

All colours are 6-digit hex without `#`. Missing keys fall back to the default.

```json
"theme": {
  "primary": "1F3A5F",        // titles, table header, first chart series
  "accent": "E07A1F",         // rules, bullets, second chart series
  "text": "1F2933",
  "muted": "6B7280",
  "background": "FFFFFF",     // page colour; anything but FFFFFF is painted on every slide (covers a template's master background)
  "light": "F3F4F6",          // KPI cards, cards, alternate table rows
  "hero": "0B2545",           // title/closing slide fill when there is no background picture; default primary
  "hero_text": "FFFFFF",      // text on hero slides and photo backgrounds; default background
  "hero_subtext": "E5E7EB",   // subtitle/meta on hero slides; default light
  "font": "Calibri",
  "title_font": "Calibri",    // defaults to font
  "east_asian_font": "Microsoft YaHei"   // set for Chinese/Japanese/Korean decks
}
```

Dark styles set `background`, `text`, `muted` and `light` to dark values and
`primary` to a light title colour. Use the member's brand colours when they
give them; otherwise keep the default navy/orange pair. Never more than two
accent colours.

## Logo

```json
"logo": {
  "light": "/app/skills/pptx-brand/assets/logo/logo-primary.png",   // on light pages
  "dark": "/app/skills/pptx-brand/assets/logo/logo-white.png",      // on hero slides and photo backgrounds
  "position": "top-right",        // content slides: top-left | top-right
  "hero_position": "bottom-right", // title/section/closing/quote: top-left | top-right | bottom-left | bottom-right
  "width_in": 1.1
}
```

`image` is accepted as an alias of `light`. An empty string disables the logo
a style would otherwise add. The title row shrinks to leave room for a
top-positioned logo, so nothing needs to move in the spec.

## Backgrounds

Full-bleed pictures on `title`, `section`, `closing` and `quote` slides. Either
a path or an object:

```json
"background": {
  "image": "/app/skills/pptx-brand/assets/backgrounds/cover-formal.jpg",
  "overlay": 0.45,          // 0..1 tint over the picture; default 0.5 for light text, 0 for dark text
  "overlay_color": "0B2545", // default: theme.hero for light text, theme.background for dark text
  "text": "light"           // light (default) or dark: which text colours to use on the picture
}
```

The picture is cropped to the slide's aspect ratio and sent to the back. On a
slide the key `"background": ""` removes a default background. Defaults per
slide type live in `defaults.backgrounds` (a styles file fills them in):

```json
"defaults": {
  "backgrounds": {"title": "...", "section": {"image": "...", "text": "dark", "overlay": 0}, "closing": "..."},
  "overlay": 0.45,
  "overlay_color": "0B2545"
}
```

Content slides never get a picture background; keep them on the page colour.

## Slide types

Every slide object has a `type`. `notes` (speaker notes, string) is accepted on
every type. Titles should be a takeaway sentence, not a topic label
("Adoption grew 38% in Q3", not "Adoption").

| `type`       | Fields | Use for |
| ------------ | ------ | ------- |
| `title`      | `title`, `subtitle`, `background` | Opening slide. Usually omitted; the deck `title` generates one. |
| `section`    | `title`, `subtitle`, `background` | Divider between parts of a longer deck. |
| `bullets`    | `title`, `bullets` | The default content slide. `bullets` is a list of strings or `{ "text": "...", "level": 0..2 }`. |
| `two_column` | `title`, `left`, `right` | Comparison, before/after, pros/cons. Each column: `heading`, `text` and/or `bullets`. |
| `image`      | `title`, `image`, `caption` | A screenshot, diagram or chart image. `image` must exist; the picture is scaled to fit. |
| `table`      | `title`, `headers`, `rows` | Small numeric or comparison tables. `rows` is a list of lists; up to 12 rows × 8 columns. |
| `chart`      | `title`, `chart` | Native, editable charts. `chart.kind` is `column`, `bar`, `line`, `pie` or `doughnut`; `categories` is a list; `series` is a list of `{ "name", "values" }` with one number per category. Optional `chart.title`, `chart.data_labels: true`. |
| `kpi`        | `title`, `metrics` | 1–6 headline numbers. Each metric: `value`, `label`, optional `description` and `icon` (PNG path). |
| `cards`      | `title`, `items` | 1–8 parallel points, 2–4 per row. Each item: `title`, optional `text` (≤160 chars) and `icon`. |
| `quote`      | `quote`, `attribution`, `background` | A customer or stakeholder quote. |
| `closing`    | `title`, `subtitle`, `background` | Last slide. `title` defaults to "Thank you". |

## Styles files

A brand skill ships `styles.json`:

```json
{
  "brand": "EFP",
  "default_style": "formal",
  "styles": {
    "formal": {
      "description": "External, leadership",
      "theme": { "primary": "0B2545", "accent": "E8590C" },
      "template": "../assets/template/efp-brand-template.pptx",
      "footer": "EFP · internal",
      "logo": { "light": "../assets/logo/logo-primary.png", "dark": "../assets/logo/logo-white.png" },
      "backgrounds": { "title": "../assets/backgrounds/cover-formal.jpg" },
      "overlay": 0.45
    }
  }
}
```

Paths inside a styles file are relative to the styles file. Build with
`--styles STYLES.json --style NAME`, or put `style` and `styles_file` in the
spec. `--list-styles --styles STYLES.json` prints the names and descriptions.

## Content rules the validator enforces or warns about

- One idea per slide. More than 8 bullets, or more than ~700 characters of
  bullet text, gets a warning: split the slide instead of shrinking the font.
- Bullets over 120 characters get a warning: shorten them and put the detail in
  `notes`.
- Titles over 70 characters get a warning; card titles over 40.
- Chart series must have exactly one numeric value per category. Pie charts
  use only the first series.
- Image, icon, logo, background and template paths must exist at validation
  time. Never invent a path; generate the image first (for example with
  matplotlib or `browser screenshot`) or use a `chart` slide with the real
  numbers instead.
- More than 40 slides gets a warning; move supporting material to an appendix
  section or a second deck.

## Companion scripts

- `inspect_template.py TEMPLATE.pptx` prints slide size, theme colours and
  fonts (with a suggested `theme` block), layouts and every sample slide's
  texts and notes. Run it once on a new corporate template before writing the
  style.
- `slice_icons.py SHEET.png --out DIR --names a,b,c` cuts an icon sheet into
  single PNGs, writes `icons.json` and a numbered `contact-sheet.png`.

## Typical deck shapes

- **Status / readout (8–12 slides)**: title → agenda → 1–2 `kpi`/`chart` →
  `section` per theme with 2–3 `bullets`/`two_column`/`cards` → risks → closing.
- **Proposal (6–10 slides)**: title → problem (`bullets`) → options
  (`two_column` or `table`) → recommendation (`bullets`) → plan (`table`) →
  ask (`kpi` or `bullets`) → closing.
- **Training / walkthrough**: `section` dividers between modules, `image`
  slides for screenshots, `cards` for steps, `notes` carrying the narration.

## Language

Write slide text in the language the member used. For Chinese, Japanese or
Korean decks set `theme.east_asian_font` (for example `Microsoft YaHei` or
`Noto Sans CJK SC`) so PowerPoint does not fall back to a serif font.
