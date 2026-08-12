#!/usr/bin/env python3
"""Validate and render canonical bilingual artist reports as self-contained HTML."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
from pathlib import Path
from typing import Any

SECTIONS = ["metadata", "visuals", "artist", "quickRead", "biography", "practice", "works", "developments", "exhibitions", "institutions", "market", "evidence", "sources"]
IMAGE_KEYS = {"path", "sourceUrl", "credit", "alt", "rightsNote"}


def bilingual(value: Any, label: str) -> None:
    if not isinstance(value, dict) or set(value) != {"zh", "en"}:
        raise ValueError(f"{label} must contain exactly zh and en")
    if not all(isinstance(value[k], str) and value[k].strip() for k in ("zh", "en")):
        raise ValueError(f"{label}.zh and .en must be non-empty strings")


def collect_images(value: Any, label: str = "report") -> list[tuple[str, dict[str, Any]]]:
    found: list[tuple[str, dict[str, Any]]] = []
    if isinstance(value, dict):
        if set(value) == IMAGE_KEYS:
            found.append((label, value))
        else:
            for key, child in value.items():
                found.extend(collect_images(child, f"{label}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(collect_images(child, f"{label}[{index}]"))
    return found


def validate(report: dict[str, Any], input_path: Path) -> list[tuple[str, dict[str, Any]]]:
    missing = [key for key in SECTIONS if key not in report]
    extra = [key for key in report if key not in SECTIONS]
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected: {', '.join(extra)}")
        raise ValueError(f"Canonical top-level sections do not match ({'; '.join(details)})")
    if report["metadata"].get("reportVersion") != "2.0":
        raise ValueError("metadata.reportVersion must be 2.0")
    if report["metadata"].get("sourceCount") != len(report["sources"]):
        raise ValueError("metadata.sourceCount must equal sources length")
    status = report["visuals"].get("status")
    if status not in {"complete", "partial", "limited", "unavailable"}:
        raise ValueError("visuals.status must be complete, partial, limited, or unavailable")
    for path in ("visuals.summary", "artist.displayName", "artist.secondaryName", "artist.birth", "artist.locations", "artist.nationality", "artist.disciplines", "quickRead.lead", "quickRead.emphasis", "quickRead.body", "biography.interactionLead", "biography.interactionBody", "practice.axisLeft", "practice.axisRight", "practice.summary", "practice.synthesis", "developments.intro", "institutions.intro", "market.status", "market.comparisonTitle", "market.comparisonBody", "market.aggregateStatus", "market.aggregateReason"):
        current: Any = report
        for part in path.split("."):
            current = current.get(part) if isinstance(current, dict) else None
        bilingual(current, path)
    if not 6 <= len(report["works"]) <= 9:
        raise ValueError("works must contain 6–9 entries")
    if not 4 <= len(report["developments"].get("entries", [])) <= 6:
        raise ValueError("developments.entries must contain 4–6 phases")
    if len(report["biography"].get("identityFacts", [])) < 5:
        raise ValueError("biography.identityFacts requires at least 5 facts")
    if len(report["biography"].get("personal", [])) < 2 or len(report["biography"].get("career", [])) < 4:
        raise ValueError("biography requires at least 2 personal and 4 career entries")
    if len(report["practice"].get("methods", [])) < 3:
        raise ValueError("practice.methods requires at least 3 entries")
    if len(report["evidence"]) < 3:
        raise ValueError("evidence requires at least 3 entries")
    for item in report["exhibitions"].get("currentUpcoming", []):
        if item.get("status") not in {"current", "upcoming"} or not item.get("accessed"):
            raise ValueError("current/upcoming exhibitions require status and accessed date")
    for lot_label, lot in ([('market.record', report["market"].get("record"))] + [(f'market.lots[{i}]', x) for i, x in enumerate(report["market"].get("lots", []))]):
        if lot is None:
            continue
        required = {"title", "workYear", "medium", "dimensions", "edition", "house", "saleTitle", "saleDate", "city", "lotNumber", "currency", "estimate", "hammer", "priceWithPremium", "resultBasis", "url", "note", "image"}
        absent = required - set(lot)
        if absent:
            raise ValueError(f"{lot_label} missing: {', '.join(sorted(absent))}")
    images = collect_images(report)
    for label, image in images:
        if set(image) != IMAGE_KEYS:
            raise ValueError(f"{label} has an invalid image object")
        bilingual(image["alt"], f"{label}.alt")
        for field in ("path", "sourceUrl", "credit", "rightsNote"):
            if not isinstance(image[field], str) or not image[field].strip():
                raise ValueError(f"{label}.{field} must be non-empty")
        local = (input_path.parent / image["path"]).resolve()
        if not local.is_file():
            raise ValueError(f"Missing local image for {label}: {local}")
    total = len(images)
    work_images = sum(1 for work in report["works"] if work.get("image"))
    hero = bool(report["artist"].get("heroImage"))
    gaps = report["visuals"].get("gaps", [])
    if status == "complete" and (total < 8 or work_images < 6 or not hero):
        raise ValueError("visuals.status complete requires 8 images, 6 work images, and a hero")
    if status == "partial" and (total < 4 or not gaps):
        raise ValueError("visuals.status partial requires at least 4 images and explicit gaps")
    if status == "limited" and not (1 <= total <= 3 and gaps):
        raise ValueError("visuals.status limited requires 1–3 images and explicit gaps")
    if status == "unavailable" and (total != 0 or not gaps):
        raise ValueError("visuals.status unavailable requires zero images and explicit gaps")
    return images


def embed_images(images: list[tuple[str, dict[str, Any]]], input_path: Path) -> dict[str, str]:
    embedded: dict[str, str] = {}
    for _, image in images:
        rel = image["path"]
        if rel in embedded:
            continue
        local = (input_path.parent / rel).resolve()
        mime = mimetypes.guess_type(local.name)[0] or "application/octet-stream"
        embedded[rel] = f"data:{mime};base64,{base64.b64encode(local.read_bytes()).decode('ascii')}"
    return embedded


HTML = r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Artist Report</title><style>
:root{--ink:#11110f;--paper:#f3f0e8;--white:#faf8f2;--muted:#77756e;--acid:#dfff39;--blue:#3157ff;--orange:#f0552d;--stone:#dcd7cd}*{box-sizing:border-box}html,body{margin:0;background:var(--ink);color:var(--ink);font-family:Arial,"PingFang SC","Microsoft YaHei",sans-serif}.page{width:min(1200px,100%);margin:auto;background:var(--paper);box-shadow:0 0 70px #0007}.hero{min-height:760px;padding:34px 64px 56px;display:flex;flex-direction:column;justify-content:space-between;color:#fff;background:#111 center/cover}.toolbar{display:flex;justify-content:space-between;align-items:center;font-size:11px;font-weight:900;letter-spacing:2px}.toolbar div{display:flex;gap:8px}.toolbar button{border:0;border-radius:22px;padding:8px 13px;background:var(--acid);font-size:10px;font-weight:900;cursor:pointer}.toolbar .print{border:1px solid #777;background:transparent;color:#fff}.index{align-self:flex-end;color:#aaa;font:28px Georgia,serif}.title p{font-size:11px;letter-spacing:1.8px}.title h1{max-width:950px;margin:18px 0 0;font:400 clamp(70px,10vw,142px)/.84 Georgia,"Songti SC",serif;letter-spacing:-6px;white-space:pre-line}.title h2{margin:20px 0 34px;color:#c0bdb3;font-size:18px;font-weight:400;letter-spacing:3px}.facts{display:flex;justify-content:space-between;gap:30px;padding-top:16px;border-top:1px solid #777;font-size:13px}.credit{margin:9px 0 0;font-size:9px;line-height:1.45;color:#888}.hero .credit{color:#bbb}.coverage{display:grid;grid-template-columns:1fr auto auto;align-items:center;gap:20px;padding:22px 64px;background:var(--acid)}.coverage b,.eyebrow{font-size:10px;letter-spacing:1.3px;text-transform:uppercase}.coverage p{max-width:760px;margin:5px 0 0;color:#414137;font-size:11px;line-height:1.5}.coverage strong{font-size:42px}.coverage span{font-size:8px}.section{padding:62px 64px 72px}.paper{background:var(--paper)}.ink{background:var(--ink);color:var(--white)}.stone{background:var(--stone)}.blue{background:var(--blue);color:#fff}.acid{background:var(--acid)}.heading{display:flex;gap:28px;margin-bottom:46px}.heading>span{width:36px;color:#88857d;font-size:10px;font-weight:900;padding-top:8px}.heading h2{margin:0;font:400 clamp(35px,5vw,64px)/1 Georgia,"Songti SC",serif;letter-spacing:-2px}.lead{max-width:920px;margin:0;font:400 clamp(31px,4.2vw,58px)/1.1 Georgia,"Songti SC",serif}.lead em{color:var(--blue);font-style:normal}.body,.section-lead{max-width:820px;margin:30px 0 0;color:#55524c;font-size:16px;line-height:1.8}.blue .section-lead,.ink .section-lead{color:#d8ddff}.image{width:100%;height:100%;object-fit:cover;display:block;background:#cbc7bd}.image-wrap{margin:0}.image-wrap img{aspect-ratio:4/3}.image-wrap figcaption{font-size:9px;color:#77736b;line-height:1.45;margin-top:8px}.portrait-grid,.split{display:grid;grid-template-columns:1.05fr 1fr;gap:36px}.portrait-grid .image-wrap img{aspect-ratio:3/4}.fact-grid,.method-grid,.work-grid,.lot-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.fact,.method{padding:18px 0;border-top:1px solid currentColor}.num{color:#88857d;font-size:9px}.fact p{margin:24px 0 0;font-size:15px;line-height:1.55}.timeline article{display:grid;grid-template-columns:105px 1fr;gap:25px;padding:20px 0;border-top:1px solid #aaa59c}.timeline time{color:var(--blue);font-size:12px;font-weight:900}.timeline h3{font-size:20px;margin:0 0 7px}.timeline p{color:#5f5b54;line-height:1.6;margin:0}.ink .timeline p{color:#c7c3b9}.interaction,.voice,.synthesis,.comparison{margin-top:38px;padding:28px;border:1px solid currentColor}.interaction h3,.voice h3,.synthesis h3,.comparison h3{font:28px Georgia,"Songti SC",serif;margin:0 0 15px}.interaction p,.voice p,.synthesis p,.comparison p{line-height:1.7;margin:0;color:inherit}.practice-images,.exhibition-images{display:grid;grid-template-columns:repeat(2,1fr);gap:18px;margin:34px 0}.method{border-color:#ffffff80}.method .num{color:var(--acid)}.method h3{margin:34px 0 12px;font-size:21px}.method p{color:#d8ddff;font-size:13px;line-height:1.65}.voices{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:36px}.voices .voice{margin:0}.voices small{display:block;margin-top:12px;color:var(--acid)}.work,.lot{border:1px solid var(--ink);background:var(--paper);display:flex;flex-direction:column;min-width:0}.work img,.lot img{width:100%;aspect-ratio:4/3;object-fit:cover}.work-content,.lot-content{padding:18px;display:flex;flex:1;flex-direction:column}.work h3,.lot h3{font:23px Georgia,"Songti SC",serif;margin:8px 0 10px}.meta{color:var(--blue);font-size:10px;font-weight:800;line-height:1.5}.note{margin-top:auto;padding-top:22px;color:#5b5851;font-size:12px;line-height:1.55}.development-hero{margin-bottom:34px}.development-hero img{width:100%;max-height:520px;object-fit:cover}.shows article{display:grid;grid-template-columns:90px 1fr 230px;gap:22px;padding:24px 0;border-top:1px solid #11110f6b}.shows b{font-size:9px}.shows h3{font-size:23px;margin:0 0 5px}.shows p{color:#4b4b40;margin:0}.shows time{text-align:right;font-size:11px}.archive{margin-top:35px}.archive h3{font-size:10px;letter-spacing:1.2px}.columns{display:grid;grid-template-columns:1fr 1fr;gap:60px}.columns h3{color:var(--acid);font-size:10px;letter-spacing:1.4px}.collection,.gallery{padding:16px 0;border-top:1px solid #3b3a36}.collection strong{font-size:28px;color:var(--acid);float:left;width:60px}.collection p,.gallery p{margin:0 0 0 60px;font-size:13px;line-height:1.55}.gallery p{margin-left:0}.signals{margin-top:30px}.signals li{margin:10px 0;line-height:1.55}.record{border:1px solid var(--ink);padding:34px;margin-bottom:24px}.record .price{font:48px Georgia,serif;margin:20px 0}.lot-grid{grid-template-columns:repeat(2,1fr)}.lot .price{font:30px Georgia,serif;margin:12px 0}.rows article{display:grid;grid-template-columns:42px 1fr;gap:20px;padding:20px 0;border-top:1px solid #aaa49a}.rows article>span{color:var(--blue);font-size:10px;font-weight:900}.rows h3{font-size:16px;margin:0 0 8px}.rows p{max-width:840px;color:#5a5750;line-height:1.65;margin:0}.rows small{display:block;color:var(--blue);overflow-wrap:anywhere;margin-top:5px}.disclaimer{margin-top:42px;padding-top:18px;border-top:3px solid var(--orange);color:#77736b;font-size:10px}
.record{padding:0;display:grid;grid-template-columns:minmax(0,1.2fr) minmax(280px,.8fr)}.record>img{width:100%;height:100%;min-height:360px;object-fit:cover}.record-content{padding:34px}
@media(max-width:760px){.hero{min-height:650px;padding:24px 22px 34px}.title h1{font-size:62px;letter-spacing:-4px}.coverage,.section{padding-left:22px;padding-right:22px}.portrait-grid,.split,.fact-grid,.method-grid,.work-grid,.lot-grid,.voices,.columns,.practice-images,.exhibition-images,.record{grid-template-columns:1fr}.timeline article{grid-template-columns:70px 1fr}.shows article{grid-template-columns:70px 1fr}.shows time{grid-column:2;text-align:left}}
@media print{@page{size:A4;margin:9mm}html,body{background:#fff}.toolbar{display:none!important}.page{width:100%;box-shadow:none}.section,.hero,.work,.lot,.image-wrap{break-inside:avoid}.hero{min-height:240mm}}
</style></head><body><main id="app" class="page"></main>
<script id="report-data" type="application/json">__REPORT_DATA__</script><script id="asset-data" type="application/json">__ASSET_DATA__</script><script>
const R=JSON.parse(document.getElementById('report-data').textContent),A=JSON.parse(document.getElementById('asset-data').textContent);let lang=new URLSearchParams(location.search).get('lang')==='en'?'en':'zh';
const esc=s=>String(s??'—').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));const t=x=>esc(x&&x[lang]);
const L=()=>lang==='zh'?{d:'研究档案',q:'60 秒速读',bio:'身份、生平与职业',practice:'创作方法与多重声音',works:'代表作品',dev:'创作发展',shows:'展览',inst:'机构、馆藏与画廊',market:'公开市场',evidence:'证据与待确认问题',refs:'参考来源',pdf:'保存 PDF',current:'展出中',upcoming:'即将展出',personal:'个人经历',career:'职业节点',artist:'艺术家自述',views:'机构解读',synth:'系统综合',history:'历史展览',collections:'公共馆藏',galleries:'画廊关系',signals:'近期动态',record:'核实纪录'}:{d:'RESEARCH DOSSIER',q:'60-SECOND READ',bio:'IDENTITY, LIFE & CAREER',practice:'PRACTICE & MULTIPLE VOICES',works:'REPRESENTATIVE WORKS',dev:'PRACTICE DEVELOPMENT',shows:'EXHIBITIONS',inst:'INSTITUTIONS, COLLECTIONS & GALLERIES',market:'PUBLIC MARKET',evidence:'EVIDENCE & OPEN QUESTIONS',refs:'REFERENCES',pdf:'SAVE PDF',current:'NOW',upcoming:'NEXT',personal:'PERSONAL',career:'CAREER',artist:'ARTIST VOICE',views:'INSTITUTIONAL VIEWS',synth:'SYSTEM SYNTHESIS',history:'ARCHIVE',collections:'PUBLIC COLLECTIONS',galleries:'GALLERY RELATIONSHIPS',signals:'RECENT SIGNALS',record:'VERIFIED RECORD'};
const section=(n,title,tone,body)=>`<section class="section ${tone}"><div class="heading"><span>${n}</span><h2>${title}</h2></div>${body}</section>`;
const image=i=>i?`<figure class="image-wrap"><img class="image" src="${A[i.path]}" alt="${t(i.alt)}"><figcaption>${esc(i.credit)} · ${esc(i.rightsNote)}</figcaption></figure>`:'';
const timeline=xs=>`<div class="timeline">${xs.map(x=>`<article><time>${esc(x.year)}</time><div><h3>${t(x.title)}</h3><p>${t(x.description)}</p></div></article>`).join('')}</div>`;
const lot=x=>{const price=x.priceWithPremium?t(x.priceWithPremium):(x.hammer?t(x.hammer):'—');return `<article class="lot">${x.image?`<img src="${A[x.image.path]}" alt="${t(x.image.alt)}">`:''}<div class="lot-content"><p class="eyebrow">${esc(x.house)} · ${esc(x.saleDate)} · LOT ${esc(x.lotNumber)}</p><h3>${t(x.title)}</h3><p class="meta">${esc(x.workYear)} · ${t(x.medium)} · ${t(x.dimensions)} · ${t(x.edition)}</p><div class="price">${price}</div><p class="note">${t(x.estimate)} · ${t(x.resultBasis)}<br>${t(x.note)}</p>${x.image?`<p class="credit">${esc(x.image.credit)}</p>`:''}</div></article>`};
function render(){const l=L(),a=R.artist,m=R.metadata,hero=a.heroImage?`background-image:linear-gradient(#0007,#0007),url('${A[a.heroImage.path]}')`:'';document.documentElement.lang=lang==='zh'?'zh-CN':'en';document.title=`${t(a.displayName)} — Artist Report`;document.getElementById('app').innerHTML=`
<header class="hero" style="${hero}"><div class="toolbar"><span>ARTIST REPORT</span><div><button id="language">${lang==='zh'?'EN':'中文'}</button><button class="print" id="print">${l.pdf}</button></div></div><div class="index">AR / ${esc(String(m.generatedAt).slice(0,4))}</div><div class="title"><p>${l.d} · ${esc(m.informationCutoff)}</p><h1>${t(a.displayName)}</h1><h2>${t(a.secondaryName)}</h2><div class="facts"><span>${t(a.locations)}</span><span>${t(a.birth)}</span></div>${a.heroImage?`<p class="credit">${esc(a.heroImage.credit)} · ${esc(a.heroImage.rightsNote)}</p>`:''}</div></header>
<div class="coverage"><div><b>${t(m.coverageStatus)} · VISUALS ${esc(R.visuals.status).toUpperCase()}</b><p>${t(m.coverageDetail)} ${t(R.visuals.summary)}</p></div><strong>${esc(m.sourceCount)}</strong><span>SOURCES</span></div>
${section('00',l.q,'paper',`<p class="lead">${t(R.quickRead.lead)} <em>${t(R.quickRead.emphasis)}</em></p><p class="body">${t(R.quickRead.body)}</p>`)}
${section('01',l.bio,'ink',`<div class="portrait-grid"><div><div class="fact-grid">${R.biography.identityFacts.map((x,i)=>`<div class="fact"><span class="num">${String(i+1).padStart(2,'0')}</span><p>${t(x)}</p></div>`).join('')}</div></div>${image(a.identityImage)}</div><div class="split" style="margin-top:44px"><div><p class="eyebrow">${l.personal}</p>${timeline(R.biography.personal)}</div><div><p class="eyebrow">${l.career}</p>${timeline(R.biography.career)}</div></div><div class="interaction"><h3>${t(R.biography.interactionLead)}</h3><p>${t(R.biography.interactionBody)}</p></div>`)}
${section('02',l.practice,'blue',`<p class="eyebrow">${t(R.practice.axisLeft)} — ${t(R.practice.axisRight)}</p><p class="section-lead">${t(R.practice.summary)}</p><div class="practice-images">${R.practice.contextImages.map(image).join('')}</div><div class="method-grid">${R.practice.methods.map((x,i)=>`<article class="method"><span class="num">${String(i+1).padStart(2,'0')}</span><h3>${t(x.title)}</h3><p>${t(x.detail)}</p></article>`).join('')}</div><div class="voices"><div class="voice"><p class="eyebrow">${l.artist}</p><h3>${t(R.practice.artistVoice.quote)}</h3><p>${t(R.practice.artistVoice.context)}</p><small>${esc(R.practice.artistVoice.source.label)}</small></div><div>${R.practice.institutionalViews.map(v=>`<div class="voice"><p class="eyebrow">${l.views} · ${esc(v.institution)}</p><p>${t(v.interpretation)}</p><small>${esc(v.source.label)}</small></div>`).join('')}</div></div><div class="synthesis"><p class="eyebrow">${l.synth}</p><p>${t(R.practice.synthesis)}</p></div>`)}
${section('03',l.works,'paper',`<div class="work-grid">${R.works.map((x,i)=>`<article class="work">${x.image?`<img src="${A[x.image.path]}" alt="${t(x.image.alt)}">`:''}<div class="work-content"><span class="num">${String(i+1).padStart(2,'0')}</span><h3>${t(x.title)}</h3><p class="meta">${esc(x.year)} · ${t(x.medium)} · ${t(x.dimensions)}</p><p class="note">${t(x.note)}</p>${x.image?`<p class="credit">${esc(x.image.credit)} · ${esc(x.image.rightsNote)}</p>`:''}</div></article>`).join('')}</div>`)}
${section('04',l.dev,'stone',`<p class="section-lead">${t(R.developments.intro)}</p><div class="development-hero">${image(R.developments.image)}</div>${timeline(R.developments.entries)}`)}
${section('05',l.shows,'acid',`<div class="exhibition-images">${R.exhibitions.heroImages.map(image).join('')}</div><div class="shows">${R.exhibitions.currentUpcoming.map(x=>`<article><b>${l[x.status]}</b><div><h3>${t(x.title)}</h3><p>${t(x.venue)} · ${t(x.type)}</p></div><time>${t(x.date)}<br>ACCESS ${esc(x.accessed)}</time></article>`).join('')}</div>${R.exhibitions.historyGroups.map(g=>`<div class="archive"><h3>${t(g.label)}</h3>${timeline(g.entries)}</div>`).join('')}`)}
${section('06',l.inst,'ink',`<p class="section-lead">${t(R.institutions.intro)}</p><div class="columns"><div><h3>${l.collections}</h3>${R.institutions.collections.map(x=>`<div class="collection"><strong>${esc(x.metric)}</strong><p><b>${esc(x.institution)}</b><br>${t(x.detail)}<br><span class="credit">ACCESS ${esc(x.accessed)}</span></p></div>`).join('')}</div><div><h3>${l.galleries}</h3>${R.institutions.galleries.map(x=>`<div class="gallery"><b>${esc(x.name)}</b><p>${t(x.detail)}</p></div>`).join('')}</div></div><div class="voices"><div>${image(R.institutions.artistVoice.image)}</div><div class="voice"><p class="eyebrow">${l.artist}</p><h3>${t(R.institutions.artistVoice.quote)}</h3><small>${esc(R.institutions.artistVoice.source.label)}</small></div></div><div class="signals"><h3>${l.signals}</h3><ul>${R.institutions.recentSignals.map(x=>`<li>${t(x)}</li>`).join('')}</ul></div>`)}
${section('07',l.market,'paper',`<p class="section-lead">${t(R.market.status)}</p>${R.market.record?`<div class="record">${R.market.record.image?`<img src="${A[R.market.record.image.path]}" alt="${t(R.market.record.image.alt)}">`:''}<div class="record-content"><p class="eyebrow">${l.record} · ${esc(R.market.record.house)} · ${esc(R.market.record.saleDate)}</p><h3>${t(R.market.record.title)}</h3><div class="price">${R.market.record.priceWithPremium?t(R.market.record.priceWithPremium):(R.market.record.hammer?t(R.market.record.hammer):'—')}</div><p>${t(R.market.record.resultBasis)} · ${t(R.market.record.estimate)}</p>${R.market.record.image?`<p class="credit">${esc(R.market.record.image.credit)} · ${esc(R.market.record.image.rightsNote)}</p>`:''}</div></div>`:''}<div class="lot-grid">${R.market.lots.map(lot).join('')}</div><div class="comparison"><h3>${t(R.market.comparisonTitle)}</h3><p>${t(R.market.comparisonBody)}</p></div><div class="comparison"><p class="eyebrow">${t(R.market.aggregateStatus)}</p><p>${t(R.market.aggregateReason)}</p></div>`)}
${section('08',l.evidence,'stone',`<div class="rows">${R.evidence.map((x,i)=>`<article><span>${String(i+1).padStart(2,'0')}</span><div><h3>${t(x.title)}</h3><p class="eyebrow">${t(x.category)}</p><p>${t(x.detail)}</p></div></article>`).join('')}</div>${R.visuals.gaps.length?`<div class="comparison"><h3>VISUAL GAPS</h3>${R.visuals.gaps.map(x=>`<p>${t(x)}</p>`).join('')}</div>`:''}`)}
${section('09',l.refs,'paper',`<div class="rows">${R.sources.map((x,i)=>`<article><span>[${i+1}]</span><div><h3>${esc(x.title)}</h3><p>${esc(x.publisher)} · ${esc(x.accessed)} · TIER ${esc(x.tier)}</p><small>${esc(x.url)}</small></div></article>`).join('')}</div><p class="disclaimer">Research aid only. No authentication, appraisal, purchase recommendation, price forecast, or investment opinion.</p>`)}
`;document.getElementById('language').onclick=()=>{lang=lang==='zh'?'en':'zh';render()};document.getElementById('print').onclick=()=>window.print()}
render();</script></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = json.loads(args.input.read_text(encoding="utf-8"))
    images = validate(report, args.input)
    if args.check:
        print(f"OK: canonical v2 report; {len(images)} local images; visual status={report['visuals']['status']}")
        return 0
    if not args.output:
        parser.error("--output is required unless --check is used")
    encoded = json.dumps(report, ensure_ascii=False).replace("</", "<\\/")
    assets = json.dumps(embed_images(images, args.input), ensure_ascii=False).replace("</", "<\\/")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(HTML.replace("__REPORT_DATA__", encoded).replace("__ASSET_DATA__", assets), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
