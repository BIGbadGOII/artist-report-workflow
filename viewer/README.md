# Artist Report Browser Viewer (legacy prototype)

> **Legacy, hardcoded prototype — not connected to the report pipeline.** `app/page.tsx` only iframes `public/report-ui/index.html`, which loads a prebuilt Expo web bundle (`public/_expo/…`) and images under `public/assets/` for **Hiroshi Sugimoto only**. It does not read `report.json`, does not use `render_report.py` or its templates, and cannot show any other artist.
>
> For real reports, use the single-file HTML produced by `skills/artist-report/scripts/render_report.py`. It already provides Chinese/English switching, chapter navigation, and a print/PDF stylesheet.

What it shows: the original magazine-style Sugimoto report UI (black-and-white cover, acid-yellow coverage strip, blue exhibitions chapter, work and market cards), default Chinese, instant English switch, and a “Save PDF” button that opens the browser print dialog.

```bash
npm install   # Node >= 22.13
npm run dev
npm run build
```

Known leftovers (kept, not removed, because they are harmless and may matter to whoever deploys this):

- `.openai/hosting.json` — hosting project id from the tool that scaffolded the viewer.
- `worker/index.ts` — vinext/Cloudflare starter worker; declares a `DB: D1Database` binding that nothing uses.
- `public/_expo/` and `public/assets/` (~6 MB) — compiled bundle and Sugimoto images; the only content the viewer can display.

If the viewer is revived, the sensible direction is to load any `report.json` and reuse `skills/artist-report/scripts/templates/` rather than the Expo bundle.
