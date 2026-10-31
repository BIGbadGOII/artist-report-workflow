# Canonical visual and section standard

This file is the portable product contract. The Hiroshi Sugimoto report is the design lineage, not a runtime dependency or an artist-specific template. Keep the information architecture consistent while allowing the art direction to respond to each artist's work.

## Required section order

1. **Cover** — portrait/hero image, bilingual names, location, birth, cutoff, visible credit.
2. **Coverage strip** — source count, textual coverage, visual coverage status.
3. **60-second read** — one thesis sentence plus concise orientation paragraph.
4. **Identity and biography** — identity facts; personal chronology; career chronology; a short interaction analysis explaining how biography informs practice.
5. **Practice** — conceptual axis or map, methods, artist voice, attributed institutional interpretations, and explicitly labeled system synthesis. Include two contextual images when available.
6. **Representative works** — 6–9 image-led cards spanning the practice; title, year, medium/dimensions, significance, visible credit.
7. **Practice development** — 4–6 phases distinct from biography; one anchor image when available.
8. **Exhibitions** — image header; current/upcoming first with exact dates and access date; historical exhibitions grouped by period.
9. **Institutions and galleries** — verified public holdings, online-count caveats, gallery relationships, artist quote, and recent activity signals.
10. **Public market** — prominent verified record plus 3–6 object-level lot cards when available; images, estimates, hammer/price basis, edition and dimensions; comparison warning and aggregate-data status.
11. **Potential assessment** — sourced momentum signals beside sourced counter-signals/risks, assessment gaps, and the fixed no-forecast disclaimer.
12. **Evidence and open questions** — conflicts, unavailable data, attribution boundaries, image gaps, and methodology.
13. **References** — numbered audit trail with direct URLs and access dates.

## Visual minimums

Default target:

- 1 credited artist portrait or studio portrait.
- 2 credited practice/context images.
- 6–9 credited representative-work images.
- 1–2 credited exhibition or installation images.
- One image per displayed market lot when the auction house exposes it publicly.

The renderer accepts missing individual images. These are coverage tiers, not claims of literal completeness:

- `complete`: the visual baseline is met: at least 8 unique local image hashes, hero, identity portrait, 2 context images, 6 unique work images, an exhibition image, and an image for every displayed market object.
- `partial`: at least 4 unique local image hashes and an explicit gap note for every missing category.
- `limited`: 1–3 total local images with explicit reasons.
- `unavailable`: no images; explain the access/licensing limitation. Never describe this as equivalent to the canonical visual report.

## Image object contract

Each non-null image contains:

- `path`: path below the report's `assets/` directory. Absolute paths, parent traversal, symlink escape, and non-image payloads are invalid.
- `sourceUrl`: direct authoritative page or asset URL used to obtain it.
- `credit`: visible credit naming artist/photographer, work or context, and supplying institution where known.
- `alt.zh` and `alt.en`: descriptive bilingual alternative text.
- `rightsNote`: concise rights/courtesy statement. Do not claim public-domain status without evidence.

The renderer embeds `path` as a data URI. It never hotlinks `sourceUrl`.

## Semantic image audit and placement

Inspect every downloaded image itself before writing the image object. Do not treat a successful download, filename, URL slug, page order, or alt text as proof of content.

For each image, verify together:

- **Visible content** — portrait, studio, single artwork, multi-work installation, exhibition view, document, or auction lot.
- **Identity** — artist and, for a single work or lot, exact title, year, medium/panel count, and source-page caption. Reject mismatches.
- **Usability** — adequate resolution, meaningful crop, correct orientation, no loading placeholder, logo, cookie banner, unrelated work, or excessive interface chrome.
- **Placement** — assign one primary semantic role before rendering; write bilingual alt text from what is actually visible.

Place by content:

- Artist or studio portrait → cover or identity/biography. A portrait may be reused in the artist-voice block when appropriate.
- Wide, legible installation view → cover, practice context, practice-development anchor, or exhibition header according to its documented exhibition.
- Single artwork with exact caption match → that work's representative-work card only. A visually similar work from the same series is not a substitute.
- Auction-house image with exact sale and lot match → that market record or lot card only.
- Multi-work installation or an image whose individual works cannot be identified → context/exhibition only, never a single-work card.
- Ambiguous, mislabeled, low-quality, unrelated, or unverifiable image → exclude and record the gap when it affects required coverage.

After rendering, visually scan the page again. Confirm that neighboring text describes the displayed image, cards do not repeat the wrong work, crops preserve the subject, and no image has migrated to a semantically incorrect section.

Record the inspection in `image-audit.md`. Use one row per unique SHA-256 asset and include visible content, semantic role, identity/caption match, crop decision, source URL, and reuse basis. Reusing a portrait in another artist-identity block is allowed, but duplicate bytes never increase visual coverage.

Display single artworks and auction objects with `object-fit: contain` or an equivalent uncropped treatment. A hero or documented installation view may use a cover crop only after the crop is visually checked and recorded.

## Information placement rules

- Identity fields contain identity, not interpretive prose.
- Biography chronology records life and career events; practice development records changes in artistic method.
- Artist voice contains attributable statements and a source label.
- Institutional views name the interpreting institution or curator.
- System synthesis is clearly labeled and never presented as a quotation.
- Exhibition status is derived from `startDate`/`endDate` relative to the information cutoff (the renderer falls back to dates parsed from the display text only when those fields are absent).
- Missing artist voice or practice phases render as visible “not publicly verified” blocks, never as invented text.
- Potential signals are facts with source links; the momentum and counter-signal columns are shown side by side so neither reads as the whole story.
- Collection entries require an institution-owned collection/record page or equivalent direct institutional evidence.
- Market records are objects, never prose-only summaries. Preserve sale currency and distinguish estimate, hammer, and price with premium.

## Browser acceptance checklist

- Desktop report is fully expanded and approximately 1200 px wide.
- A compact chapter navigation lets readers reach every canonical section; it is hidden in print.
- No broken images; every displayed image has a visible credit.
- Every displayed image has passed content inspection and appears beside semantically matching text.
- Chinese and English views contain equivalent information.
- Current/upcoming exhibition labels agree with cutoff dates.
- Print preview does not clip cards or show the toolbar.
- Chapter navigation, source links, language switching, and print are the only interactive elements.
