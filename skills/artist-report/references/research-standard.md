# Research standard

## Source order

1. Artist, estate, foundation, catalogue raisonné, or official archive.
2. Museums, public collections, universities, public agencies, and exhibition organizers.
3. Representing galleries and established institutional publishers.
4. Auction-house original lot pages for object-level market evidence, including authenticated pages the user can already access on Sotheby's, Christie's, and Phillips.
5. MutualArt authenticated pages for supplementary object-level records and cross-checking; preserve the underlying auction-house attribution.
6. Reputable independent criticism or journalism for attributed context only.

Do not use aggregators to support a claim when the underlying primary page is available. Search results are discovery aids, not sources.

`sources[].tier` in `report.json` is the position in this list (1–6). Specialist market databases other than MutualArt (for example askART or artnet) are tier 5 and need the same underlying-house attribution.

## Minimum coverage

- Identity: legal/display name, aliases, birth/death where applicable, nationality, locations, disciplines.
- Practice: recurring questions, materials, methods, and attributed interpretations.
- Career: 6–12 dated milestones when evidence permits.
- Works: 6–9 works or series spanning the practice.
- Exhibitions: current/upcoming first, followed by selected historical milestones.
- Institutions: verified public collection presence and gallery relationships.
- Market: object-level examples only; distinguish estimate, hammer, and price with premium.
- Potential assessment: sourced momentum signals, counter-signals, and gaps (see below).
- Evidence: contradictions, missing data, restricted access, and methodological limits.
- Sources: normally 12–30 direct URLs; fewer is acceptable for poorly documented artists if explicitly labeled.

## Claim discipline

- Verified fact: support with a first-party or institutional source.
- Attributed interpretation: name the speaker or institution.
- System synthesis: clearly label it as synthesis and build only from cited facts.
- Conflict: preserve both versions and explain which is used and why.
- Missing fact: write “not publicly verified” rather than filling the gap. When a whole required block is missing (artist voice, practice phases), use the schema gap mechanism: `{"gap": {"zh": …, "en": …}}` for `artistVoice`, `developments.gapNote` with fewer than four entries.

## Market discipline

- Never equate matching titles with matching objects.
- Record medium, dimensions, edition, printing/casting date, sale, lot, currency, estimate, result basis, and URL when available.
- When the user has an existing logged-in session on Sotheby's, Christie's, Phillips, or MutualArt, reading, extracting, and recording data visible in that session is allowed for the requested report. Use the existing browser session; do not ask the user to send credentials.
- Treat screenshots as evidence capture, not as the final data model. Transcribe each relevant lot into the structured market fields and retain the page URL, access date, auction house, sale, lot number, currency, and result basis.
- Mark login-only evidence in the lot note and `sources.md` as `authenticated session / 已登录会话`. Do not reproduce account identifiers, subscription details, unrelated saved lots, browsing history, or other private account data.
- Access to a gated page does not grant permission to redistribute its screenshots or images. Keep authenticated screenshots out of the self-contained report unless independent reuse permission is documented; prefer a public auction-house asset or leave the image empty and record the gap.
- Do not bypass login, paywalls, CAPTCHA, geographic restrictions, access controls, rate limits, or anti-bot measures. If the existing session is unavailable, continue with public evidence and record the coverage gap.
- A logged-in result list is not automatically a complete population. Record the applied artist identity, filters, sort order, visible result count, pagination coverage, and access date before calculating aggregate statistics.
- Do not calculate sell-through, turnover, median, or trends from any incomplete sample, whether public or authenticated.
- Do not infer a result when it is not visible in either public evidence or the user's authenticated session.

## Potential assessment (潜力评估)

`potential` answers one question: what does the public record show about the artist's current trajectory, and what does it not show? It is an evidence summary, not a forecast.

Momentum signals (`potential.signals`). Each signal needs a category, a date or period, a factual bilingual description, and at least one `sourceRef` whose URL appears in `sources`. Look for:

- `institutional-exhibition`: museum, kunsthalle, biennial, or public-institution shows in roughly the last five years. Commercial gallery shows go under `gallery-exhibition`; never upgrade them.
- `prize-award`, `residency-grant`: from the awarding body's own page.
- `representation`: current galleries per the artist and gallery sites; new or added representation with a date if published.
- `art-fair`: verified exhibitor listings from the fair organizer.
- `critical-attention`: named critics or publications; separate independent criticism from gallery copy.
- `collection`: institution-owned collection records only (same evidence bar as the institutions section).
- `market-activity`: factual market observations only — public auction results with lot references, gallery-marked sales, published asking prices labeled as primary-market offers.

Counter-signals and risks (`potential.counterSignals`). Record with the same structure: missing institutional validation, thin or gallery-only criticism, sparse or unverifiable auction data, unresolved date or representation conflicts, long exhibition gaps, identity ambiguity. A scoped negative finding (“not found in the reviewed sources”) may have an empty `sourceRefs` list; say what was searched.

Gaps (`potential.gaps`). State which signal categories were not researched or could not be accessed, so absence of a signal is never read as evidence.

Hard limits, enforced by the validator where possible:

- No price predictions, valuation, appreciation language, rankings, scores, or buy/sell/hold recommendations — in this section or anywhere else. Phrases such as “undervalued”, “investment opportunity”, “prices will rise”, “升值潜力”, “投资价值”, or “建议买入” fail `--check`.
- Do not calculate growth rates or trends from incomplete samples (see market discipline).
- Keep signal descriptions factual: who, what, where, when, source. Interpretation belongs in `summary`, which must stay proportional to the evidence and mention the main counter-signals.
- The renderer always prints a fixed bilingual disclaimer under this section; do not rely on wording in the data for it.

## Fair-driven artist selection

When the user asks you to choose an artist from an art fair (or another pool such as a biennial list or prize shortlist) instead of naming one:

1. Identify the exact edition (name, year, city, dates). Get the exhibitor or artist list from the organizer's official site or official catalogue. Gallery announcements, press round-ups, and social posts are discovery aids only; confirm each candidate against the official list or the exhibiting gallery's own fair page.
2. Apply only the user's stated criteria (sector, medium, region, emerging vs. established). If none are given, ask one concise question or state the default you use (for example: living artist, enough public sources for a report).
3. Shortlist 3–5 candidates. For each, record the booth/gallery, the official-list URL, why they fit the brief, how much public evidence exists, and the main risk or gap.
4. Choose one and explain the choice in terms of fit and research coverage — never expected market performance.
5. Save this as `<output-dir>/selection-notes.md` using `assets/selection-notes-template.md`, and cite the official list in `sources` (tier 2, exhibition organizer). The fair presentation itself can then appear as an `art-fair` signal.

## Bilingual writing

- Write concise institutional Chinese and clear international English.
- Preserve official titles in their source language when translation could create ambiguity.
- Translate meaning, not word order. Keep dates, currencies, dimensions, and proper nouns consistent across languages.
- Avoid promotional superlatives and investment language.

## Sources file

Write `sources.md` as a numbered audit trail. For each source include title, publisher, URL, accessed date, source tier, and the report sections it supports.

Keep URLs directly actionable in the HTML. Link artist statements, institutional interpretations, collection records, gallery records, auction lots, image credits, and reference entries to their original pages. When fewer than 12 sources are available, explain the constrained coverage in both `metadata.coverageDetail` and the evidence section.
