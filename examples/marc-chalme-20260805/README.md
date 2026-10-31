# Example: Marc Chalmé (canonical schema v2.1)

Migrated on 2026-10-31 from the legacy v0.1 sample (`reports/marc-chalme-artist-report.json` plus its zh/en Markdown). **No new research was done**: every fact comes from that sample, and the information cutoff stays 2026-08-05. Where the canonical schema needs data the sample lacks, the report says so explicitly (`gap` objects, `developments.gapNote`, `visuals.gaps`, `potential.gaps`) instead of filling the gap.

Migration decisions:

- No images were ever saved, so `visuals.status` is `unavailable` and every image slot is `null`.
- No artist statement was found, so both `artistVoice` blocks are `gap` objects.
- The sources do not support defensible practice phases, so `developments.entries` is empty and `gapNote` explains why.
- The single askART record has no auction house, currency, or visible price, so it is described in `market.status` rather than shown as a structured lot.
- Source tiers were relabeled from v0.1's three-level scale to the canonical six-step source order.
- `potential` was assembled from facts already in the sample; prizes, residencies, and grants were never searched, and the report says so.

```bash
python3 skills/artist-report/scripts/render_report.py --check --input examples/marc-chalme-20260805/report.json
python3 skills/artist-report/scripts/render_report.py --input examples/marc-chalme-20260805/report.json --output examples/marc-chalme-20260805/report.html
```

`report.html` is generated output and is not committed.
