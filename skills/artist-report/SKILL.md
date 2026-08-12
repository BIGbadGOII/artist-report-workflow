---
name: artist-report
description: Research an artist from current public sources and generate a source-transparent, image-rich bilingual Chinese-English browser dossier in the canonical Hiroshi Sugimoto editorial format, with local credited visual assets and browser PDF export. Use for 艺术家报告, artist dossiers, artist research, market-and-exhibition overviews, bilingual artist profiles, or “研究/生成报告 + 艺术家姓名”.
---

# Artist Report

Create `report.json`, `report.html`, `sources.md`, and a local `assets/` image folder. Match the canonical section logic and visual density defined in [visual-standard.md](references/visual-standard.md); do not treat it as optional inspiration.

## Required workflow

1. Read [research-standard.md](references/research-standard.md), [visual-standard.md](references/visual-standard.md), and [report-schema.json](references/report-schema.json) completely.
2. Resolve identity before collecting facts. Search aliases, dates, nationality, medium, location, and official identifiers. Ask one concise question only if multiple plausible people remain.
3. Browse the live web. Prefer artist/foundation sites, museums, organizers, representing galleries, and original auction records. Open source pages; search snippets are discovery aids only. If the user has an existing authenticated session on Sotheby's, Christie's, Phillips, or MutualArt, use that session to read and extract report-relevant secondary-market data under the authenticated-access rules in [research-standard.md](references/research-standard.md).
4. Research text and visuals together. Build a credited visual set from authoritative pages: artist portrait, practice/context images, 6–9 representative works, exhibition/installations, and object-level auction images when market examples exist.
5. Save approved images under `<output-dir>/assets/`. Record for every image: local `path`, original `sourceUrl`, `credit`, bilingual `alt`, and `rightsNote`. Never use image search thumbnails, hotlinked mystery files, or uncredited images.
6. Inspect the actual pixels of every saved image with an image-viewing tool before assigning it. Verify visible subject, orientation, crop, image quality, and the exact artist/work/exhibition/lot identity against the source-page caption or metadata. Build the placement map using [visual-standard.md](references/visual-standard.md). Never infer content from a filename or URL.
7. If an expected visual category is unavailable or reuse is not supportable, leave it empty and record the exact reason in `visuals.gaps`. Do not silently downgrade to typography-only. A report with fewer than four usable images must use `visuals.status: limited` or `unavailable`.
8. Separate verified fact, attributed artist voice, institutional interpretation, and system synthesis in their dedicated schema fields. Do not collapse them into one undifferentiated paragraph.
9. Write JSON exactly to the schema. Keep all reader-facing prose bilingual. Use structured objects for collections, exhibitions, and auction lots; do not place an entire record into one long string.
10. Create a new directory `artist-reports/<artist-slug>-<YYYYMMDD>/`. Never overwrite an existing report unless explicitly asked.
11. Render and validate:

   ```bash
   python3 <skill-dir>/scripts/render_report.py \
     --input <output-dir>/report.json \
     --output <output-dir>/report.html
   python3 -m json.tool <output-dir>/report.json >/dev/null
   python3 <skill-dir>/scripts/render_report.py --check \
     --input <output-dir>/report.json
   ```

12. Inspect the rendered report in a desktop-width browser. Confirm: images load; each image appears in the semantically correct section; credits are visible; Chinese is default; language switching works; every canonical section is present and expanded; market lots remain object-level; “保存 PDF / SAVE PDF” invokes print; print hides the toolbar. If browser policy blocks `file://`, serve the output directory on localhost with a read-only local HTTP server and inspect that URL.
13. Return clickable paths to `report.html`, `report.json`, and `sources.md`. State the cutoff, visual coverage, material gaps, and any categories downgraded under the visual exception rule.

## Non-negotiable editorial rules

- Use the section order and semantic roles in [visual-standard.md](references/visual-standard.md).
- Present artist voice, institutional reading, and system synthesis as visibly distinct blocks.
- Keep “life/career chronology” separate from “practice development”.
- Separate current/upcoming exhibitions from the historical archive; give exact dates and access dates for current/upcoming items.
- Present public collections with evidence and online-count caveats. Museum participation is not collection ownership.
- Present market evidence as structured lots with title, year, medium, dimensions, edition, sale, lot, currency, estimate, hammer/result basis, URL, and image where available.
- Authenticated market pages may be used only through the user's already logged-in browser session. Never request, expose, store, or replay credentials; never bypass login, paywalls, CAPTCHA, access controls, or anti-bot measures.
- Do not calculate turnover, sell-through, median, or trends without a complete normalized population.
- Never provide authentication, appraisal, buying advice, forecasts, or investment opinions.
- Use images only with recorded source and credit. Prefer authoritative reusable press/collection/auction imagery; copyright remains with the named rightsholder.
- Never place an image by filename guess, aesthetic similarity, or series-level resemblance. Match a work image to the exact work card and a lot image to the exact auction lot; use multi-work or unidentified installation images only as context.
- If live browsing is unavailable, stop rather than fabricate a current report.

## Output behavior

- Default language: Chinese.
- Output: one self-contained HTML file. The renderer embeds local image files as data URIs; remote URLs remain audit metadata, not runtime dependencies.
- Controls: only Chinese/English switching and browser “Save PDF”.
- Existing reports may supply facts only through their cited sources. Never copy one artist’s factual content into another report.
