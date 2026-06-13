"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Props {
  schemeName: string;
  description?: string | null;
  benefitDisplay?: string | null;
  eligibilityText?: string | null;
  applyUrl?: string | null;
  docs: Array<{ doc_name: string; mandatory: boolean }>;
  lang: string;
}

export default function SchemeExplainer({
  schemeName,
  description,
  benefitDisplay,
  eligibilityText,
  applyUrl,
  docs,
  lang,
}: Props) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    if (open) {
      document.addEventListener("keydown", onKey);
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open]);

  const mandatoryDocs = docs.filter((d) => d.mandatory);
  const optionalDocs  = docs.filter((d) => !d.mandatory);

  const STEPS = [
    "पात्रता शर्तें पढ़ें और सुनिश्चित करें कि आप योग्य हैं",
    mandatoryDocs.length > 0
      ? `${mandatoryDocs.slice(0, 3).map((d) => d.doc_name).join(", ")}${mandatoryDocs.length > 3 ? " आदि" : ""} तैयार करें`
      : "आधार, आय प्रमाण, बैंक पासबुक तैयार रखें",
    applyUrl ? "आधिकारिक पोर्टल पर जाकर फॉर्म भरें" : "नज़दीकी CSC सेंटर या सरकारी कार्यालय जाएं",
    "आवेदन संख्या नोट करें और स्थिति ट्रैक करें",
  ];

  return (
    <>
      {/* Trigger button */}
      <button
        onClick={() => setOpen(true)}
        style={{
          display: "inline-flex", alignItems: "center", gap: 8,
          padding: "12px 22px", borderRadius: 12,
          border: "1.5px solid rgba(11,31,77,.18)", background: "#fff",
          color: "var(--navy)", fontWeight: 700, fontSize: 14,
          cursor: "pointer", marginTop: "var(--s3)",
        }}
        aria-expanded={open}
        aria-haspopup="dialog"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.5" />
          <path d="M8 7v4M8 5.5v.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        </svg>
        योजना की पूरी जानकारी
      </button>

      {/* Backdrop */}
      <div
        className={`explainer-backdrop${open ? " is-open" : ""}`}
        onClick={() => setOpen(false)}
        aria-hidden="true"
      />

      {/* Panel */}
      <div
        className={`scheme-explainer-drawer${open ? " is-open" : ""}`}
        role="dialog"
        aria-modal="true"
        aria-label={`${schemeName} — पूरी जानकारी`}
      >
        {/* Handle (mobile only) */}
        <div className="drawer-handle" />

        {/* Header */}
        <div className="panel-header">
          <h3 className="panel-title" style={{ margin: 0, fontSize: 16 }}>{schemeName}</h3>
          <button
            onClick={() => setOpen(false)}
            className="panel-close-btn"
            aria-label="बंद करें"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path d="M5 5l10 10M15 5L5 15" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="panel-body">

          {/* Benefit highlight */}
          {benefitDisplay && (
            <div style={{
              background: "linear-gradient(135deg,rgba(19,136,8,.08) 0%,rgba(19,136,8,.04) 100%)",
              border: "1.5px solid rgba(19,136,8,.2)",
              borderRadius: "var(--r-md)",
              padding: "var(--s4)",
              marginBottom: "var(--s5)",
            }}>
              <div style={{ fontSize: 10, fontWeight: 800, textTransform: "uppercase", letterSpacing: ".06em", color: "var(--green-deep)", marginBottom: 4 }}>
                आपको क्या मिलेगा
              </div>
              <div style={{ fontSize: 20, fontWeight: 900, color: "var(--green-deep)" }}>{benefitDisplay}</div>
            </div>
          )}

          {/* AI summary card */}
          {description && (
            <div className="ai-summary-card">
              <div style={{ fontSize: 10, fontWeight: 800, textTransform: "uppercase", letterSpacing: ".06em", color: "var(--saffron-deep)", marginBottom: "var(--s2)" }}>
                योजना का सारांश
              </div>
              <p className="ai-summary-text">{description}</p>
            </div>
          )}

          {/* Eligibility text */}
          {eligibilityText && (
            <div style={{ marginBottom: "var(--s5)" }}>
              <div style={{ fontSize: 13, fontWeight: 800, color: "var(--navy)", marginBottom: "var(--s2)" }}>पात्रता</div>
              <p style={{ fontSize: 14, lineHeight: 1.7, color: "var(--ink-2)", margin: 0 }}>{eligibilityText}</p>
            </div>
          )}

          {/* Mini flow */}
          <div style={{ marginBottom: "var(--s5)" }}>
            <div style={{ fontSize: 13, fontWeight: 800, color: "var(--navy)", marginBottom: "var(--s3)" }}>आवेदन कैसे करें</div>
            <ol style={{ paddingLeft: 0, margin: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: "var(--s3)" }}>
              {STEPS.map((step, i) => (
                <li key={i} style={{ display: "flex", alignItems: "flex-start", gap: "var(--s3)" }}>
                  <span style={{
                    flexShrink: 0, width: 24, height: 24, borderRadius: "50%",
                    background: i === STEPS.length - 1 ? "var(--green)" : "var(--navy)",
                    color: "#fff", fontSize: 12, fontWeight: 800,
                    display: "grid", placeItems: "center",
                  }}>
                    {i + 1}
                  </span>
                  <span style={{ fontSize: 14, color: "var(--ink)", lineHeight: 1.5, paddingTop: 3 }}>{step}</span>
                </li>
              ))}
            </ol>
          </div>

          {/* Docs quick list */}
          {docs.length > 0 && (
            <div style={{ marginBottom: "var(--s5)" }}>
              <div style={{ fontSize: 13, fontWeight: 800, color: "var(--navy)", marginBottom: "var(--s2)" }}>
                दस्तावेज़ ({docs.length})
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--s2)" }}>
                {mandatoryDocs.slice(0, 6).map((d, i) => (
                  <span key={i} style={{
                    fontSize: 12, padding: "4px 10px", borderRadius: 20,
                    background: "rgba(255,153,51,.1)", color: "var(--saffron-deep)", fontWeight: 600,
                    border: "1px solid rgba(255,153,51,.25)",
                  }}>{d.doc_name}</span>
                ))}
                {optionalDocs.slice(0, 4).map((d, i) => (
                  <span key={i} style={{
                    fontSize: 12, padding: "4px 10px", borderRadius: 20,
                    background: "var(--surface-2)", color: "var(--ink-3)",
                    border: "1px solid var(--line)",
                  }}>{d.doc_name}</span>
                ))}
                {docs.length > 10 && (
                  <span style={{ fontSize: 12, color: "var(--ink-3)", padding: "4px 0" }}>+{docs.length - 10} और</span>
                )}
              </div>
            </div>
          )}

          {/* CTA */}
          <div style={{ display: "flex", gap: "var(--s3)", flexWrap: "wrap", paddingTop: "var(--s2)" }}>
            {applyUrl && (
              <a
                href={applyUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary btn-lg"
                style={{ flex: 1, justifyContent: "center" }}
              >
                ऑनलाइन आवेदन करें
                <svg width="12" height="12" fill="none" viewBox="0 0 12 12" aria-hidden="true">
                  <path d="M1 11L11 1M11 1H6M11 1v5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </a>
            )}
            <Link
              href={`/${lang}/check`}
              className="btn btn-outline"
              style={{ flex: 1, justifyContent: "center", textAlign: "center" }}
              onClick={() => setOpen(false)}
            >
              पात्रता जाँचें
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
