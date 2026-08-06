"use client";

import { marked } from "marked";
import { useEffect, useMemo, useState } from "react";

type Language = "zh" | "en";
type ReportContent = Record<Language, string>;

const copy = {
  zh: {
    product: "ARTIST REPORT",
    type: "研究档案 · 2026年8月5日",
    location: "东京 · 纽约",
    born: "生于 1948",
    coverage: "资料覆盖充分",
    coverageDetail: "创作与机构资料完整；公开市场汇总资料有限。",
    sources: "22 项来源",
    save: "保存报告",
    saved: "已保存",
    export: "打印 / 保存 PDF",
    savedNote: "已保存在此浏览器中",
    loading: "正在打开报告…",
    error: "报告内容加载失败，请刷新页面重试。",
    note: "研究辅助材料，不构成鉴定、估值、购买建议或投资意见。",
  },
  en: {
    product: "ARTIST REPORT",
    type: "RESEARCH DOSSIER · 05 AUG 2026",
    location: "Tokyo · New York",
    born: "b. 1948",
    coverage: "EXTENSIVE COVERAGE",
    coverageDetail: "Practice and institutions are well documented. Aggregate market data is partial.",
    sources: "22 sources",
    save: "Save report",
    saved: "Saved",
    export: "Print / Save PDF",
    savedNote: "Saved in this browser",
    loading: "Opening report…",
    error: "The report could not be loaded. Refresh the page to try again.",
    note: "Research aid only. No authentication, appraisal, purchase recommendation or investment opinion.",
  },
} as const;

marked.setOptions({ gfm: true, breaks: false });

export function ReportViewer() {
  const [language, setLanguage] = useState<Language>("zh");
  const [content, setContent] = useState<ReportContent | null>(null);
  const [saved, setSaved] = useState(false);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const storedLanguage = window.localStorage.getItem("artist-report-language");
    if (storedLanguage === "zh" || storedLanguage === "en") setLanguage(storedLanguage);
    setSaved(window.localStorage.getItem("artist-report-saved") === "hiroshi-sugimoto-2026-08-05");

    Promise.all([
      fetch("/content/hiroshi-sugimoto-zh.md").then((response) => {
        if (!response.ok) throw new Error("Chinese report unavailable");
        return response.text();
      }),
      fetch("/content/hiroshi-sugimoto-en.md").then((response) => {
        if (!response.ok) throw new Error("English report unavailable");
        return response.text();
      }),
    ])
      .then(([zh, en]) => setContent({ zh, en }))
      .catch(() => setFailed(true));
  }, []);

  const html = useMemo(() => {
    if (!content) return "";
    return marked.parse(content[language], { async: false }) as string;
  }, [content, language]);

  const setReportLanguage = (nextLanguage: Language) => {
    setLanguage(nextLanguage);
    window.localStorage.setItem("artist-report-language", nextLanguage);
    document.documentElement.lang = nextLanguage === "zh" ? "zh-CN" : "en";
  };

  const saveReport = () => {
    window.localStorage.setItem("artist-report-saved", "hiroshi-sugimoto-2026-08-05");
    window.localStorage.setItem("artist-report-language", language);
    setSaved(true);
  };

  const labels = copy[language];

  return (
    <main className="viewer">
      <header className="toolbar" aria-label={language === "zh" ? "报告工具栏" : "Report toolbar"}>
        <a className="brand" href="#top" aria-label="Artist Report">
          <span className="brand-mark" aria-hidden="true">AR</span>
          <span>{labels.product}</span>
        </a>

        <div className="toolbar-actions">
          <div className="language-switch" role="group" aria-label={language === "zh" ? "切换语言" : "Change language"}>
            <button className={language === "zh" ? "active" : ""} onClick={() => setReportLanguage("zh")} aria-pressed={language === "zh"}>中文</button>
            <button className={language === "en" ? "active" : ""} onClick={() => setReportLanguage("en")} aria-pressed={language === "en"}>EN</button>
          </div>
          <button className={`save-button ${saved ? "saved" : ""}`} onClick={saveReport}>
            <span aria-hidden="true">{saved ? "✓" : "+"}</span> {saved ? labels.saved : labels.save}
          </button>
          <button className="export-button" onClick={() => window.print()}>
            {labels.export}
          </button>
        </div>
      </header>

      <article className="report" id="top">
        <section className="cover">
          <img src="/report-images/sugimoto-portrait.jpg" alt={language === "zh" ? "杉本博司肖像" : "Portrait of Hiroshi Sugimoto"} />
          <div className="cover-shade" />
          <div className="cover-content">
            <p className="eyebrow">{labels.type}</p>
            <h1>{language === "zh" ? "杉本博司" : "Hiroshi\nSugimoto"}</h1>
            <p className="secondary-name">{language === "zh" ? "HIROSHI SUGIMOTO" : "杉本博司"}</p>
            <div className="cover-meta"><span>{labels.location}</span><span>{labels.born}</span></div>
          </div>
        </section>

        <section className="coverage-band">
          <div><strong>{labels.coverage}</strong><span>{labels.coverageDetail}</span></div>
          <b>{labels.sources}</b>
        </section>

        <section className="visual-intro" aria-label={language === "zh" ? "代表作品" : "Selected works"}>
          <figure><img src="/report-images/ua-playhouse.jpg" alt="U.A. Playhouse, New York, 1978" /><figcaption>U.A. Playhouse, New York · 1978</figcaption></figure>
          <figure><img src="/report-images/sea-of-japan.jpg" alt="Sea of Japan, Oki, 1987" /><figcaption>Sea of Japan, Oki · 1987</figcaption></figure>
        </section>

        <div className="report-body" lang={language === "zh" ? "zh-CN" : "en"}>
          {failed ? <p className="status-message">{labels.error}</p> : null}
          {!failed && !content ? <p className="status-message">{labels.loading}</p> : null}
          {content ? <div dangerouslySetInnerHTML={{ __html: html }} /> : null}
        </div>

        <footer className="report-footer">
          <p>{labels.note}</p>
          {saved ? <span>{labels.savedNote}</span> : null}
        </footer>
      </article>
    </main>
  );
}
