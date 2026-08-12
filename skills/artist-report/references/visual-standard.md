# Canonical visual and section standard

The canonical product reference is the Hiroshi Sugimoto browser report in `/Users/bigbadgoii/Documents/ARTSREARCH/viewer/`. Match its information architecture and editorial density, not its artist-specific facts.

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
11. **Evidence and open questions** — conflicts, unavailable data, attribution boundaries, image gaps, and methodology.
12. **References** — numbered audit trail with direct URLs and access dates.

## Visual minimums

Default target:

- 1 credited artist portrait or studio portrait.
- 2 credited practice/context images.
- 6–9 credited representative-work images.
- 1–2 credited exhibition or installation images.
- One image per displayed market lot when the auction house exposes it publicly.

The renderer accepts missing individual images, but validation applies these states:

- `complete`: at least 8 total local images, including a hero and at least 6 work images.
- `partial`: at least 4 total local images and an explicit gap note for every missing category.
- `limited`: 1–3 total local images with explicit reasons.
- `unavailable`: no images; explain the access/licensing limitation. Never describe this as equivalent to the canonical visual report.

## Image object contract

Each non-null image contains:

- `path`: path relative to `report.json`; it must resolve to a local file.
- `sourceUrl`: direct authoritative page or asset URL used to obtain it.
- `credit`: visible credit naming artist/photographer, work or context, and supplying institution where known.
- `alt.zh` and `alt.en`: descriptive bilingual alternative text.
- `rightsNote`: concise rights/courtesy statement. Do not claim public-domain status without evidence.

The renderer embeds `path` as a data URI. It never hotlinks `sourceUrl`.

## Information placement rules

- Identity fields contain identity, not interpretive prose.
- Biography chronology records life and career events; practice development records changes in artistic method.
- Artist voice contains attributable statements and a source label.
- Institutional views name the interpreting institution or curator.
- System synthesis is clearly labeled and never presented as a quotation.
- Exhibition status is derived from exact dates relative to the information cutoff.
- Collection entries require an institution-owned collection/record page or equivalent direct institutional evidence.
- Market records are objects, never prose-only summaries. Preserve sale currency and distinguish estimate, hammer, and price with premium.

## Browser acceptance checklist

- Desktop report is fully expanded and approximately 1200 px wide.
- No broken images; every displayed image has a visible credit.
- Chinese and English views contain equivalent information.
- Current/upcoming exhibition labels agree with cutoff dates.
- Print preview does not clip cards or show the toolbar.
- Only language and print controls are interactive.
