---
name: artist-report
description: Research an artist from current public sources and generate a source-linked, image-rich bilingual Chinese-English browser dossier with credited local visual assets, object-level market evidence, semantic image placement, and browser PDF export. Use for 艺术家报告, artist dossiers, artist research, market-and-exhibition overviews, bilingual artist profiles, or “研究/生成报告 + 艺术家姓名”.
---

# Artist Report

Create `report.json`, `report.html`, `sources.md`, `image-audit.md`, and a local `assets/` image folder. Follow the product contract in [visual-standard.md](references/visual-standard.md).

## Required workflow

1. Read [research-standard.md](references/research-standard.md), [visual-standard.md](references/visual-standard.md), and [report-schema.json](references/report-schema.json) completely.
2. Resolve identity before collecting facts. Search aliases, dates, nationality, medium, location, and official identifiers. Ask one concise question only if multiple plausible people remain.
3. Browse the live web. Prefer artist/foundation sites, museums, organizers, representing galleries, and original auction records. Open source pages; search snippets are discovery aids only. If the user has an existing authenticated session on Sotheby's, Christie's, Phillips, or MutualArt, use that session to read and extract report-relevant secondary-market data under the authenticated-access rules in [research-standard.md](references/research-standard.md).
4. Research text and visuals together. Build a credited visual set from authoritative pages: artist portrait, practice/context images, 6–9 representative works, exhibition/installations, and object-level auction images when market examples exist.
5. Save approved raster images only under `<output-dir>/assets/`. Record for every image: local `path`, original `sourceUrl`, `credit`, bilingual `alt`, and `rightsNote`. Never use image-search thumbnails, hotlinked mystery files, uncredited images, or login-only images without documented redistribution permission.
6. Copy [image-audit-template.md](assets/image-audit-template.md) to `<output-dir>/image-audit.md`. Inspect the actual pixels of every saved image with an image-viewing tool before assigning it. Verify visible subject, orientation, crop, image quality, and exact artist/work/exhibition/lot identity against the source-page caption or metadata. Complete one row per unique asset with SHA-256, visible content, intended role, caption/identity match, crop decision, source URL, and reuse basis. Never infer content from a filename or URL.
7. If an expected visual category is unavailable or reuse is not supportable, leave it empty and record the exact reason in `visuals.gaps`. Do not silently downgrade to typography-only. A report with fewer than four usable images must use `visuals.status: limited` or `unavailable`.
8. Separate verified fact, attributed artist voice, institutional interpretation, and system synthesis in their dedicated schema fields. Do not collapse them into one undifferentiated paragraph.
9. Write JSON exactly to the schema. Keep all reader-facing prose bilingual. Use ISO dates in machine-checked fields and include an ISO date in at least one language for every current/upcoming exhibition range. Use structured objects for collections, exhibitions, and auction lots; do not place an entire record into one long string.
10. Create a new directory `artist-reports/<artist-slug>-<YYYYMMDD>/`. Never overwrite an existing report unless explicitly asked.
11. Render and validate:

   ```bash
   python3 <skill-dir>/scripts/render_report.py \
     --input <output-dir>/report.json \
     --output <output-dir>/report.html
   python3 <skill-dir>/scripts/render_report.py --check \
     --input <output-dir>/report.json
   ```

12. Inspect the rendered report at desktop and mobile widths. Prefer a read-only localhost URL from the outset when browser inspection is required. Confirm: images load without subject-damaging crops; image/text placement is correct; credits and source links are visible; Chinese is default; language switching and chapter navigation work; all sections are expanded; market lots remain object-level; print preview hides controls and does not clip cards. Never bypass a browser URL-policy rejection.
13. Return clickable paths to `report.html`, `report.json`, `sources.md`, and `image-audit.md`. State the cutoff, unique-image coverage, material gaps, and any categories downgraded under the visual exception rule.

## Non-negotiable editorial rules

- Use the section order and semantic roles in [visual-standard.md](references/visual-standard.md).
- Present artist voice, institutional reading, and system synthesis as visibly distinct blocks.
- Keep “life/career chronology” separate from “practice development”.
- Separate current/upcoming exhibitions from the historical archive; give exact dates and access dates for current/upcoming items.
- Present public collections with evidence and online-count caveats. Museum participation is not collection ownership.
- Present market evidence as structured lots with title, year, medium, dimensions, edition, sale, lot, currency, estimate, hammer/result basis, URL, and image where available.
- Authenticated market pages may be used only through the user's already logged-in browser session. Never request, expose, store, or replay credentials; never bypass login, paywalls, CAPTCHA, access controls, or anti-bot measures.
- Treat authenticated text and screenshots as evidence capture, not redistribution permission. Transcribe report-relevant facts; do not embed gated screenshots or images unless reuse permission is independently documented.
- Do not calculate turnover, sell-through, median, or trends without a complete normalized population.
- Never provide authentication, appraisal, buying advice, forecasts, or investment opinions.
- Use images only with recorded source and credit. Prefer authoritative reusable press/collection/auction imagery; copyright remains with the named rightsholder.
- Never place an image by filename guess, aesthetic similarity, or series-level resemblance. Match a work image to the exact work card and a lot image to the exact auction lot; use multi-work or unidentified installation images only as context.
- If live browsing is unavailable, stop rather than fabricate a current report.

## Output behavior

- Default language: Chinese.
- Output: one self-contained HTML file. The renderer embeds validated raster files from `assets/` as data URIs and keeps source URLs as clickable audit links.
- Controls: chapter navigation, Chinese/English switching, and browser “Save PDF”.
- Performance: optimize images before embedding; target a report below 10 MB unless visual fidelity requires more, and record the exception.
- Existing reports may supply facts only through their cited sources. Never copy one artist’s factual content into another report.
