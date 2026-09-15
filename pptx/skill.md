---
name: pptx
description: Create a PowerPoint (.pptx) deck from the member's request or source material with python-pptx, save it under output/ and hand back a download link.
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - make a ppt
  - make a powerpoint
  - create slides
  - build a deck
  - slide deck
  - presentation deck
  - 做PPT
  - 做一个PPT
  - 生成PPT
  - 制作幻灯片
  - 做个演示文稿
  - /pptx
when_to_use:
  - Use when the member asks for a PPT, PowerPoint, slide deck or presentation file they can download.
  - Use when a summary, report, plan or set of findings should be delivered as slides rather than prose.
  - Use when the member uploads notes, a document or a spreadsheet and wants slides made from it.
  - Do not use for a quick outline in chat; only when a .pptx file is the deliverable.
references:
  - references/layout-guide.md
  - references/spec-example.json
  - scripts/inspect_template.py
  - scripts/slice_icons.py
planning_mode: auto
execution_style: direct
ask_user_policy: blocked_only
output_format: markdown
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - pptx
    - presentation
    - deliverable
    - python-pptx
    - opencode-bash-cli
---

# PPTX deck builder

Produce a real, editable `.pptx` file and give the member a way to download it.
The deck is described in one JSON spec and rendered by
`scripts/build_deck.py` (next to this file; in production
`/app/skills/pptx/scripts/build_deck.py`). Do not hand-write python-pptx code
unless the spec cannot express what the member needs.

## Non-negotiable rules

1. The deliverable is a file under `output/` in the workspace, never slide text
   pasted into chat. Keep the spec out of `output/` so only the deck shows up as
   a deliverable.
2. Every fact on a slide comes from the member's message, an attached file, or
   a tool result. Never invent numbers, quotes, dates or names; if a number is
   missing, say so on the slide ("TBD") and in the reply.
3. Never invent image paths. Use `chart` slides for numbers and `image` slides
   only for files that exist in the workspace.
4. Run the build script with `--validate-only` first, then build. Fix every
   error and act on every warning (split dense slides) before answering.
5. Write slide text in the member's language. For Chinese, Japanese or Korean
   set `theme.east_asian_font`.
6. Reply with a short summary and the download link; do not paste the spec.

## Workflow

### 1. Confirm the brief (only when it changes the deck)

Decide these yourself from context unless the answer would change the whole
deck: audience, purpose (readout, proposal, training), length (default 8–12
slides), language, and whether a company template was supplied. Ask one
question at most, and only when the request is genuinely ambiguous.

### 2. Gather the content

- Read attached documents through their runtime projections or with the `read`
  tool; read spreadsheets before quoting any figure.
- Pull Jira, Confluence or GitHub facts with the runtime CLIs (`jira`,
  `confluence`, `gh`) when the member points at tickets or pages.
- Write down the storyline first: one takeaway sentence per slide. That sentence
  becomes the slide title.

### 3. Write the spec

Save the spec to `.efp/pptx/<slug>.spec.json` (create the directory). Follow
`references/layout-guide.md` for the schema; `references/spec-example.json` is
a full example, also printed by:

```bash
python /app/skills/pptx/scripts/build_deck.py --print-example
```

Rules of thumb: title slide is generated from `title`/`subtitle`; use `section`
dividers for decks over ten slides; put numbers in `kpi`, `chart` or `table`
slides, not in bullets; use `cards` for three or four parallel points; keep at
most 6 bullets and 2 levels per slide; put the narration in `notes`.

### 3a. Brand styles, templates and icons

When a brand skill is available (for example `/pptx-brand`), load it and put
its style in the spec (`"style"` plus `"styles_file"`), or pass `--styles` and
`--style` on the command line. The style brings colours, fonts, the template,
footer, logo and background pictures; the spec only carries content. List the
styles with:

```bash
python /app/skills/pptx/scripts/build_deck.py --list-styles --styles <styles.json>
```

When the member supplies a corporate template or an icon sheet instead, read
them before writing the spec:

```bash
python /app/skills/pptx/scripts/inspect_template.py <template.pptx>
python /app/skills/pptx/scripts/slice_icons.py <sheet.png> --out .efp/pptx/icons --names <name1,name2,...>
```

The inspection reports the theme colours and fonts as a ready `theme` block,
the layouts, and the template's sample slides (its text examples). The slicer
writes one PNG per icon plus a numbered contact sheet; name the icons from that
sheet, then reference them by path in `kpi` metrics or `cards` items.

### 4. Validate, build, verify

```bash
python /app/skills/pptx/scripts/build_deck.py .efp/pptx/<slug>.spec.json --validate-only
python /app/skills/pptx/scripts/build_deck.py .efp/pptx/<slug>.spec.json --output output/<slug>.pptx
```

The script prints JSON. `ok: false` lists `errors` to fix in the spec.
`warnings` are content problems (too dense, too long); fix them and rebuild.
`slides` is the count re-read from the saved file; it must match the spec plus
the generated title slide.

If the script exits with code 3, python-pptx is missing: run
`python -m pip install --user python-pptx` once and retry. If that fails, tell
the member the runtime image needs python-pptx and stop.

When the member supplied a `.pptx`/`.potx` template (uploads land under
`uploads/`), pass `--template <path>`; the template's theme and slide size are
kept and its sample slides are removed.

### 5. Deliver

Reply in the member's language with:

- one or two sentences on what the deck covers and how many slides it has;
- a numbered list of slide titles;
- the download link written exactly as a workspace link, for example
  `[Download q3-review.pptx](workspace:output/q3-review.pptx)`;
- one line saying the file is also in the Server Files panel under `output/`.

The Portal turns `workspace:` links into download links and shows generated
files under `output/` as download cards, so the path in the link must be the
real relative path you saved to.

### 6. Revisions

For "change slide 4" style follow-ups, edit the spec and rebuild to the same
output path so the earlier link keeps working. Only choose a new file name when
the member asks to keep both versions.

## Example exchange

Member: "把这份 Q3 复盘做成 10 页左右的 PPT" with `q3-notes.md` attached.

Assistant: reads the notes, drafts ten takeaway titles, writes
`.efp/pptx/q3-review.spec.json`, validates, builds `output/q3-review.pptx`,
then answers:

> 已生成 10 页的 Q3 复盘 PPT，涵盖采用率、交付内容、成本和 Q4 风险。
> 1. Q3 复盘 … 10. 谢谢
> [下载 q3-review.pptx](workspace:output/q3-review.pptx)
> 文件也可以在 Server Files 面板的 `output/` 目录下载。
