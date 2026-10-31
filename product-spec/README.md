# product-spec (legacy)

These files are the original v0.1 product exploration. **They are not the contract the workflow runs on.**

| File | Status |
|---|---|
| `artist-report-spec-v0.1.md` | Legacy. Its content and evidence rules were carried into `skills/artist-report/references/research-standard.md` and `visual-standard.md`. |
| `artist-report-schema-v0.1.json` | Legacy snake_case schema (`report_metadata`, `artist_identity`, …). Superseded by `skills/artist-report/references/report-schema.json` (v2.1). `render_report.py` does not accept v0.1 data. |
| `search-and-generation-architecture.md` | Future design for a hosted product (queues, payments, mobile). Out of scope for this repository. |

Canonical sources of truth:

- Schema: `skills/artist-report/references/report-schema.json`
- Workflow: `skills/artist-report/SKILL.md`
- Validator/renderer: `skills/artist-report/scripts/render_report.py`
- Example that passes `--check`: `examples/marc-chalme-20260805/`

To move an old v0.1 report forward, follow the migration notes in `examples/marc-chalme-20260805/README.md`: reuse only facts already in the report and use the schema's gap fields where data is missing.
