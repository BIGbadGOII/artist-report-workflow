#!/usr/bin/env python3
"""Render an artist-report JSON file as a self-contained bilingual HTML report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED = ["metadata", "artist", "quickRead", "identityFacts", "career", "practice", "works", "exhibitions", "institutions", "market", "evidence", "sources"]


def validate(report: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED if key not in report]
    if missing:
        raise ValueError(f"Missing required report keys: {', '.join(missing)}")
    for key in ("displayName", "secondaryName", "birth", "locations", "nationality", "disciplines"):
        value = report["artist"].get(key)
        if not isinstance(value, dict) or not isinstance(value.get("zh"), str) or not isinstance(value.get("en"), str):
            raise ValueError(f"artist.{key} must contain zh and en strings")
    if report["metadata"].get("sourceCount") != len(report["sources"]):
        raise ValueError("metadata.sourceCount must equal the number of sources")


HTML = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Artist Report</title><style>
:root{--ink:#11110f;--paper:#f3f0e8;--white:#faf8f2;--muted:#77756e;--acid:#dfff39;--blue:#3157ff;--orange:#f0552d}*{box-sizing:border-box}html,body{margin:0;min-height:100%;background:var(--ink);color:var(--ink);font-family:Arial,"PingFang SC","Microsoft YaHei",sans-serif}.page{width:min(1200px,100%);margin:auto;background:var(--paper);box-shadow:0 0 70px #0006}.hero{min-height:760px;padding:34px 64px 56px;display:flex;flex-direction:column;justify-content:space-between;color:#fff;background:radial-gradient(circle at 76% 22%,#3d3d3a 0,#22221f 22%,#11110f 57%);background-size:cover;background-position:center}.toolbar{display:flex;justify-content:space-between;align-items:center;font-size:11px;font-weight:900;letter-spacing:2px}.toolbar div{display:flex;gap:8px}.toolbar button{border:0;border-radius:22px;padding:8px 13px;background:var(--acid);font-size:10px;font-weight:900;cursor:pointer}.toolbar .print{border:1px solid #777;background:transparent;color:#fff}.index{align-self:flex-end;color:#77746c;font:28px Georgia,serif}.title p{font-size:11px;letter-spacing:1.8px}.title h1{max-width:950px;margin:18px 0 0;font:400 clamp(70px,10vw,142px)/.84 Georgia,"Songti SC",serif;letter-spacing:-6px}.title h2{margin:20px 0 34px;color:#b8b4aa;font-size:18px;font-weight:400;letter-spacing:3px}.facts{display:flex;justify-content:space-between;gap:30px;padding-top:16px;border-top:1px solid #666;font-size:13px}.coverage{display:flex;align-items:center;gap:18px;padding:22px 64px;background:var(--acid)}.coverage div{flex:1}.coverage b{font-size:10px;letter-spacing:1.2px}.coverage p{max-width:680px;margin:5px 0 0;color:#404038;font-size:11px;line-height:1.5}.coverage strong{font-size:42px}.coverage>span{align-self:flex-end;margin-bottom:7px;font-size:8px}.section{padding:62px 64px 72px}.paper{background:var(--paper)}.ink{background:var(--ink);color:var(--white)}.stone{background:#dcd7cd}.blue{background:var(--blue);color:#fff}.acid{background:var(--acid)}.heading{display:flex;gap:28px;margin-bottom:46px}.heading>span{width:36px;color:#88857d;font-size:10px;font-weight:900;padding-top:8px}.heading h2{margin:0;font:400 clamp(35px,5vw,64px)/1 Georgia,"Songti SC",serif;letter-spacing:-2px}.lead{max-width:900px;margin:0;font:400 clamp(32px,4.2vw,58px)/1.1 Georgia,"Songti SC",serif}.body,.section-lead{max-width:800px;margin:30px 0 0;color:#55524c;font-size:16px;line-height:1.8}.blue .section-lead{color:#d8ddff}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.fact,.method,.work{padding:18px 0;border-top:1px solid currentColor}.num{color:#88857d;font-size:9px}.fact p{margin:24px 0 0;font-size:16px;line-height:1.5}.timeline article{display:grid;grid-template-columns:110px 1fr;gap:28px;padding:24px 0;border-top:1px solid #aaa59c}.timeline time{color:var(--blue);font-size:12px;font-weight:900}h3,p{margin-top:0}.timeline h3{font-size:22px;margin-bottom:8px}.timeline p{max-width:760px;color:#5f5b54;line-height:1.65}.method{border-color:#ffffff80}.method .num{color:var(--acid)}.method h3{margin-top:36px;font-size:23px}.method p{color:#ced5ff;font-size:13px;line-height:1.65}.work{min-height:270px;padding:20px;border:1px solid var(--ink);display:flex;flex-direction:column}.work h3{margin-top:36px;font:25px Georgia,"Songti SC",serif}.work .meta{color:var(--blue);font-size:10px;font-weight:800}.work .note{margin-top:auto;padding-top:28px;color:#5b5851;font-size:12px;line-height:1.6}.shows article{display:grid;grid-template-columns:90px 1fr 220px;gap:22px;padding:24px 0;border-top:1px solid #11110f6b}.shows b{font-size:9px}.shows h3{font-size:24px;margin-bottom:5px}.shows p{color:#4b4b40}.shows time{text-align:right;font-size:11px}.columns{display:grid;grid-template-columns:1fr 1fr;gap:80px}.columns h3{color:var(--acid);font-size:10px;letter-spacing:1.4px}.columns p{margin:0;padding:16px 0;border-top:1px solid #3b3a36;font-size:15px}.market{border:1px solid var(--ink);padding:34px}.market .status{color:var(--orange);font-size:11px;font-weight:900}.market strong{display:block;max-width:850px;margin:28px 0;font:42px/1.1 Georgia,"Songti SC",serif}.market p:not(.status){max-width:800px;color:#5d5952;line-height:1.65}.rows article{display:grid;grid-template-columns:42px 1fr;gap:20px;padding:20px 0;border-top:1px solid #aaa49a}.rows article>span{color:var(--blue);font-size:10px;font-weight:900}.rows h3{font-size:16px;margin-bottom:8px}.rows p{max-width:800px;color:#5a5750;line-height:1.65}.rows small{display:block;color:var(--blue);overflow-wrap:anywhere}.disclaimer{margin-top:42px;padding-top:18px;border-top:3px solid var(--orange);color:#77736b;font-size:10px}.credit{font-size:9px;color:#aaa;margin-top:12px}
@media(max-width:760px){.hero{min-height:650px;padding:24px 22px 34px}.title h1{font-size:62px;letter-spacing:-4px}.coverage,.section{padding-left:22px;padding-right:22px}.grid,.columns{grid-template-columns:1fr}.timeline article{grid-template-columns:70px 1fr}.shows article{grid-template-columns:70px 1fr}.shows time{grid-column:2;text-align:left}}
@media print{@page{size:A4;margin:10mm}html,body{background:#fff}.toolbar{display:none!important}.page{width:100%;box-shadow:none}.section,.hero{break-inside:avoid}}
</style></head><body><main id="app" class="page"></main>
<script id="report-data" type="application/json">__REPORT_DATA__</script><script>
const R=JSON.parse(document.getElementById('report-data').textContent);let lang=new URLSearchParams(location.search).get('lang')==='en'?'en':'zh';
const esc=s=>String(s??'—').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));const t=x=>esc(x&&x[lang]);
const L=()=>lang==='zh'?{d:'研究档案',c:'资料覆盖',q:'60 秒速读',i:'艺术家身份',career:'经历与职业发展',p:'创作方法',w:'关键作品',e:'展览',inst:'公共收藏与画廊',m:'公开市场',ev:'证据与待确认问题',s:'参考来源',pdf:'保存 PDF',current:'展出中',upcoming:'即将展出',past:'历史展览'}:{d:'RESEARCH DOSSIER',c:'COVERAGE',q:'60-SECOND READ',i:'ARTIST IDENTITY',career:'LIFE & CAREER',p:'HOW THE PRACTICE WORKS',w:'KEY WORKS',e:'EXHIBITIONS',inst:'COLLECTIONS & GALLERIES',m:'PUBLIC MARKET',ev:'EVIDENCE & OPEN QUESTIONS',s:'REFERENCES',pdf:'SAVE PDF',current:'NOW',upcoming:'NEXT',past:'PAST'};
const section=(n,title,tone,body)=>`<section class="section ${tone}"><div class="heading"><span>${n}</span><h2>${title}</h2></div>${body}</section>`;
function render(){const l=L(),a=R.artist,md=R.metadata,hero=a.heroImage&&a.heroImage.url?`style="background-image:linear-gradient(#0007,#0007),url('${esc(a.heroImage.url)}')"`:'';document.documentElement.lang=lang==='zh'?'zh-CN':'en';document.title=`${t(a.displayName)} — Artist Report`;document.getElementById('app').innerHTML=`
<header class="hero" ${hero}><div class="toolbar"><span>ARTIST REPORT</span><div><button id="language">${lang==='zh'?'EN':'中文'}</button><button class="print" id="print">${l.pdf}</button></div></div><div class="index">AR / ${esc(String(md.generatedAt).slice(0,4))}</div><div class="title"><p>${l.d} · ${esc(md.informationCutoff)}</p><h1>${t(a.displayName)}</h1><h2>${t(a.secondaryName)}</h2><div class="facts"><span>${t(a.locations)}</span><span>${t(a.birth)}</span></div>${a.heroImage&&a.heroImage.credit?`<p class="credit">${esc(a.heroImage.credit)}</p>`:''}</div></header>
<div class="coverage"><div><b>${l.c}</b><p>${t(md.coverageDetail||md.coverageStatus)}</p></div><strong>${esc(md.sourceCount)}</strong><span>SOURCES</span></div>
${section('00',l.q,'paper',`<p class="lead">${t(R.quickRead.lead)}</p><p class="body">${t(R.quickRead.body)}</p>`)}
${section('01',l.i,'ink',`<div class="grid">${R.identityFacts.map((x,i)=>`<div class="fact"><span class="num">${String(i+1).padStart(2,'0')}</span><p>${t(x)}</p></div>`).join('')}</div>`)}
${section('02',l.career,'stone',`<div class="timeline">${R.career.map(x=>`<article><time>${esc(x.year)}</time><div><h3>${t(x.title)}</h3><p>${t(x.description)}</p></div></article>`).join('')}</div>`)}
${section('03',l.p,'blue',`<p class="section-lead">${t(R.practice.summary)}</p><div class="grid">${R.practice.methods.map((x,i)=>`<article class="method"><span class="num">${String(i+1).padStart(2,'0')}</span><h3>${t(x.title)}</h3><p>${t(x.detail)}</p></article>`).join('')}</div>`)}
${section('04',l.w,'paper',`<div class="grid">${R.works.map((x,i)=>`<article class="work"><span class="num">${String(i+1).padStart(2,'0')}</span><h3>${t(x.title)}</h3><p class="meta">${esc(x.year)} · ${t(x.medium)}</p><p class="note">${t(x.note)}</p></article>`).join('')}</div>`)}
${section('05',l.e,'acid',`<div class="shows">${R.exhibitions.map(x=>`<article><b>${l[x.status]||esc(x.status)}</b><div><h3>${t(x.title)}</h3><p>${t(x.venue)}</p></div><time>${t(x.date)}</time></article>`).join('')}</div>`)}
${section('06',l.inst,'ink',`<div class="columns"><div><h3>PUBLIC COLLECTIONS</h3>${R.institutions.collections.map(x=>`<p>${t(x)}</p>`).join('')}</div><div><h3>GALLERY RELATIONSHIPS</h3>${R.institutions.galleries.map(x=>`<p>${t(x)}</p>`).join('')}</div></div>`)}
${section('07',l.m,'paper',`<div class="market"><p class="status">${t(R.market.status)}</p>${R.market.record?`<strong>${t(R.market.record)}</strong>`:''}${R.market.notes.map(x=>`<p>${t(x)}</p>`).join('')}</div>`)}
${section('08',l.ev,'stone',`<div class="rows">${R.evidence.map((x,i)=>`<article><span>${String(i+1).padStart(2,'0')}</span><div><h3>${t(x.title)}</h3><p>${t(x.detail)}</p></div></article>`).join('')}</div>`)}
${section('09',l.s,'paper',`<div class="rows">${R.sources.map((x,i)=>`<article><span>[${i+1}]</span><div><h3>${esc(x.title)}</h3><p>${esc(x.publisher)} · ${esc(x.accessed)}</p><small>${esc(x.url)}</small></div></article>`).join('')}</div><p class="disclaimer">Research aid only. No authentication, appraisal, purchase recommendation or investment opinion.</p>`)}
`;document.getElementById('language').onclick=()=>{lang=lang==='zh'?'en':'zh';render()};document.getElementById('print').onclick=()=>window.print()}
render();
</script></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = json.loads(args.input.read_text(encoding="utf-8"))
    validate(report)
    if args.check:
        print("OK")
        return 0
    if not args.output:
        parser.error("--output is required unless --check is used")
    encoded = json.dumps(report, ensure_ascii=False).replace("</", "<\\/")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(HTML.replace("__REPORT_DATA__", encoded), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
