---
name: artist-report
description: Research an artist from current public sources and generate a source-transparent bilingual Chinese-English browser report with the established editorial visual style and browser PDF export. Use when a user asks for an 艺术家报告, artist dossier, artist research, market-and-exhibition overview, bilingual artist profile, or says “研究/生成报告 + 艺术家姓名”.
---

# Artist Report

Create a complete research artifact, not a chat-only summary. The normal deliverables are `report.json`, `report.html`, and `sources.md` in a new artist-specific output folder.

## Required workflow

1. Read [research-standard.md](references/research-standard.md) and [report-schema.json](references/report-schema.json) completely before researching.
2. Resolve the requested artist’s identity before collecting facts. Search aliases, dates, nationality, medium, location, and official identifiers. Ask one concise question only when multiple plausible people remain.
3. Browse the live web. Prioritize artist/foundation sites, museums, public institutions, exhibition organizers, representing galleries, and auction-house original records. Never rely on search snippets as evidence.
4. Record every source used. Preserve conflicts, unavailable data, access dates, and information cutoff. Do not infer gated auction results from estimates.
5. Write the report JSON to the schema. Every reader-facing field must contain both `zh` and `en`; keep proper names in their authoritative form where useful.
6. Create a new output directory named `artist-reports/<artist-slug>-<YYYYMMDD>/`. Do not overwrite an existing report unless the user explicitly asks.
7. Run:

   ```bash
   python3 <skill-dir>/scripts/render_report.py \
     --input <output-dir>/report.json \
     --output <output-dir>/report.html
   ```

8. Validate JSON and rendering:

   ```bash
   python3 -m json.tool <output-dir>/report.json >/dev/null
   python3 <skill-dir>/scripts/render_report.py --check --input <output-dir>/report.json
   ```

9. Open `report.html` in the Codex browser for the user. The report must be desktop-width, fully expanded, and expose only Chinese/English switching and browser “Save PDF” interaction.
10. Return clickable paths to `report.html`, `report.json`, and `sources.md`. State the information cutoff and material coverage gaps.

## Research constraints

- Separate verified fact, attributed interpretation, and system synthesis.
- Label current/upcoming exhibitions with exact dates and source access dates.
- Treat aggregate market coverage as unavailable unless a complete normalized lot population exists.
- Never provide authentication, appraisal, buying advice, price forecasts, or investment opinions.
- Use images only when their source and credit are recorded. A typography-only report is preferable to an unattributed image.
- If live browsing is unavailable, stop and explain that current-source research cannot be completed reliably; do not fabricate a report.

## Output behavior

- Default report language: Chinese.
- Browser report: one self-contained HTML file; remote credited images are optional.
- PDF: the report’s “保存 PDF / SAVE PDF” button invokes the browser print dialog and hides the toolbar in print.
- Existing example reports may guide depth, but never reuse their facts for another artist.
