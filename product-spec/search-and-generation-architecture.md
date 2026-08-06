# Artist search and report-generation architecture

## Product principle

The customer buys a report, not API tokens. The mobile app never asks for, receives, stores, or displays an OpenAI or research-provider API key.

## User flow

1. The collector enters an artist name, in any common script.
2. The app returns identity candidates with portrait, canonical name, birth/death years, nationality and primary medium.
3. The collector confirms the intended artist.
4. The app shows the report scope, current information cutoff, delivery estimate and price.
5. After payment, the backend creates a report job and returns a job ID.
6. The app displays meaningful progress states for approximately 5–15 minutes.
7. The completed report appears in the collector's library and retains its information cutoff and source snapshot.

## Search layer

Autocomplete should query our own artist index rather than call a language model on every keystroke. Each artist record should hold:

- canonical English name;
- aliases and names in other scripts;
- birth/death years;
- nationality or working locations;
- primary media;
- portrait thumbnail and rights/source metadata;
- stable identifiers such as Wikidata, ULAN and museum IDs;
- an ambiguity flag for artists with similar names.

The first version can seed this index from open structured identifiers and expand it whenever a report is generated. The language model is used after identity confirmation, not as the primary autocomplete database.

## Backend report pipeline

1. Resolve the artist identity and stable identifiers.
2. Retrieve artist, museum, public-agency, gallery, exhibition and auction-house sources.
3. Store source URLs, retrieval times, quotations used internally and image-rights metadata.
4. Extract structured facts into the fixed report schema.
5. Detect conflicts, missing sections and unsupported claims.
6. Generate synthesis only after factual extraction.
7. Run automated citation, date and schema checks.
8. Render the same structured report into the mobile interface.

Every artist receives the same schema. Lack of available evidence produces a visible “not verified” or “insufficient public data” state; it never removes the section.

## Fixed report schema

- artist identity;
- 60-second orientation;
- biography and career development;
- artistic practice and artist statements;
- practice timeline;
- selected works and bodies of work;
- current, upcoming and recent exhibitions;
- public institutional collections;
- gallery representation;
- public auction history and data limitations;
- recent activity;
- conflicts, gaps and methodology;
- source register and information cutoff.

## Token and credential model

- OpenAI and provider credentials live only in the backend secret manager.
- The mobile app receives a short-lived user session token, never a model-provider token.
- The report price includes retrieval, model and infrastructure cost.
- Customers see the report price and delivery estimate, not internal token usage.
- Cost is controlled through cached sources, identity deduplication, structured extraction with smaller models and synthesis with a stronger model only where needed.
- Reopening a finished report reads stored structured data and does not regenerate it.

## Data licensing boundary

Consumer subscriptions to Artnet or MutualArt must not be treated as commercial redistribution licences. Public pages may support discovery and source coverage. Lot-level facts should be checked against auction-house records. Any paid database used automatically at product scale requires an appropriate API or commercial data agreement.

## Suggested infrastructure for the first paid version

- Mobile client: React Native / Expo.
- API and job orchestration: server-side application with authenticated endpoints.
- Database: PostgreSQL for users, artists, jobs, sources and structured reports.
- Queue: managed job queue for 5–15 minute generation tasks.
- Object storage: licensed report images and generated report assets.
- Payments: Stripe or an app-store-compliant purchase path, selected before public launch.
- Secrets: deployment-provider secret manager; never source code or mobile environment variables.

## Progress states shown to the collector

- Confirming artist identity
- Gathering museum and gallery records
- Checking exhibitions and public collections
- Normalising auction evidence
- Resolving source conflicts
- Building the visual report
- Final checks

These states should be tied to real job stages rather than a decorative countdown.
