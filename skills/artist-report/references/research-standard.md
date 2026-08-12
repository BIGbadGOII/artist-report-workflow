# Research standard

## Source order

1. Artist, estate, foundation, catalogue raisonné, or official archive.
2. Museums, public collections, universities, public agencies, and exhibition organizers.
3. Representing galleries and established institutional publishers.
4. Auction-house original lot pages for object-level market evidence, including authenticated pages the user can already access on Sotheby's, Christie's, and Phillips.
5. MutualArt authenticated pages for supplementary object-level records and cross-checking; preserve the underlying auction-house attribution.
6. Reputable independent criticism or journalism for attributed context only.

Do not use aggregators to support a claim when the underlying primary page is available. Search results are discovery aids, not sources.

## Minimum coverage

- Identity: legal/display name, aliases, birth/death where applicable, nationality, locations, disciplines.
- Practice: recurring questions, materials, methods, and attributed interpretations.
- Career: 6–12 dated milestones when evidence permits.
- Works: 6–9 works or series spanning the practice.
- Exhibitions: current/upcoming first, followed by selected historical milestones.
- Institutions: verified public collection presence and gallery relationships.
- Market: object-level examples only; distinguish estimate, hammer, and price with premium.
- Evidence: contradictions, missing data, restricted access, and methodological limits.
- Sources: normally 12–30 direct URLs; fewer is acceptable for poorly documented artists if explicitly labeled.

## Claim discipline

- Verified fact: support with a first-party or institutional source.
- Attributed interpretation: name the speaker or institution.
- System synthesis: clearly label it as synthesis and build only from cited facts.
- Conflict: preserve both versions and explain which is used and why.
- Missing fact: write “not publicly verified” rather than filling the gap.

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

## Bilingual writing

- Write concise institutional Chinese and clear international English.
- Preserve official titles in their source language when translation could create ambiguity.
- Translate meaning, not word order. Keep dates, currencies, dimensions, and proper nouns consistent across languages.
- Avoid promotional superlatives and investment language.

## Sources file

Write `sources.md` as a numbered audit trail. For each source include title, publisher, URL, accessed date, source tier, and the report sections it supports.

Keep URLs directly actionable in the HTML. Link artist statements, institutional interpretations, collection records, gallery records, auction lots, image credits, and reference entries to their original pages. When fewer than 12 sources are available, explain the constrained coverage in both `metadata.coverageDetail` and the evidence section.
