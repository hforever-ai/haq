import { notFound } from "next/navigation";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";
import Link from "next/link";
import Image from "next/image";
import { makeT, getLanguages, RTL_LANGS } from "@/lib/i18n";
import { getScheme, getSchemes } from "@/lib/api";
import SchemeCard from "@/components/scheme/SchemeCard";
import FaqAccordion from "@/components/scheme/FaqAccordion";
import SchemeFlowDiagram, { applySteps } from "@/components/scheme/SchemeFlowDiagram";
import SchemeExplainer from "@/components/scheme/SchemeExplainer";

interface Props {
  params: Promise<{ lang: string; slug: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { lang, slug } = await params;
  const scheme = await getScheme(slug);
  if (!scheme) return { title: "Scheme not found" };
  const desc = (scheme.description ?? "").slice(0, 155);
  return {
    title: scheme.name,
    description: desc,
    openGraph: { title: scheme.name, description: desc },
    alternates: {
      languages: Object.fromEntries(
        getLanguages().map((l) => [
          l.code,
          `https://haq.aarambhax.in/${l.code}/yojana/s/${slug}`,
        ])
      ),
    },
  };
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function fmtInr(inr: number): string {
  if (inr >= 10_00_000) return `₹${(inr / 10_00_000).toFixed(1)} लाख`;
  if (inr >= 1_000)     return `₹${(inr / 1_000).toFixed(0)}K`;
  return `₹${inr}`;
}

const BENEFIT_LABELS: Record<string, string> = {
  cash: "नकद",
  kind: "वस्तु/सामग्री",
  service: "सेवा",
  subsidy: "सब्सिडी",
  loan: "ऋण",
  insurance: "बीमा",
  pension: "पेंशन",
  education: "शिक्षा सहायता",
  housing: "आवास",
  health: "स्वास्थ्य सहायता",
  skill_development: "कौशल विकास",
  food_security: "खाद्य सुरक्षा",
};

const RESIDENCE_LABELS: Record<string, string> = {
  rural: "ग्रामीण",
  urban: "शहरी",
  both: "ग्रामीण + शहरी",
};

const EMPLOYMENT_LABELS: Record<string, string> = {
  farmer: "किसान",
  student: "छात्र/छात्रा",
  employed: "नौकरीपेशा",
  unemployed: "बेरोजगार",
  self_employed: "स्वरोजगार",
  any: "सभी",
};

const GENDER_LABELS: Record<string, string> = {
  male: "पुरुष",
  female: "महिला",
  transgender: "ट्रांसजेंडर",
  all: "सभी",
};

export default async function SchemeDetailPage({ params }: Props) {
  const { lang, slug } = await params;
  const t = makeT(lang);

  const [scheme, relatedRes] = await Promise.all([
    getScheme(slug, lang),
    getSchemes({ category: undefined, size: 4 }),
  ]);

  if (!scheme) notFound();

  const related = relatedRes.schemes
    .filter((s) => s.slug !== slug)
    .slice(0, 3);

  const languages = getLanguages();

  // Compute best income display (enriched > old column)
  const incomeLimitInr = scheme.income_limit_annual_inr ??
    (scheme.max_income_lakhs ? scheme.max_income_lakhs * 100_000 : null);

  // Benefit amount display — use translated benefit text if available
  const benefitDisplay = scheme.benefit_text_translated
    || scheme.benefit_amount_description
    || (scheme.benefit_amount_inr ? fmtInr(scheme.benefit_amount_inr) : null)
    || (scheme.benefit_amount_percent ? `${scheme.benefit_amount_percent}% सब्सिडी` : null);

  // Documents — parse if string
  const docs: Array<{ doc_name: string; mandatory: boolean }> =
    Array.isArray(scheme.documents_required) ? scheme.documents_required : [];

  const isEnriched = !!scheme.enriched_at;

  return (
    <div style={{ background: "var(--page)", minHeight: "100vh" }}>

      {/* ── Breadcrumb ── */}
      <div style={{ background: "var(--surface)", borderBottom: "1px solid var(--line)" }}>
        <div className="wrap">
          <nav className="breadcrumb" aria-label="Breadcrumb">
            <Link href={`/${lang}/`}>{t("nav.tagline")}</Link>
            <span className="sep" aria-hidden="true">›</span>
            <Link href={`/${lang}/yojana`}>{t("nav.all_schemes")}</Link>
            {scheme.beneficiary_type?.[0] && (
              <>
                <span className="sep" aria-hidden="true">›</span>
                <Link href={`/${lang}/yojana/${scheme.beneficiary_type[0]}`}>
                  {t(`cat.${scheme.beneficiary_type[0]}`)}
                </Link>
              </>
            )}
            <span className="sep" aria-hidden="true">›</span>
            <span aria-current="page" style={{ color: "var(--ink-2)" }}>
              {scheme.short_title || scheme.name}
            </span>
          </nav>
        </div>
      </div>

      {/* ── Page Hero (premium with illustration) ── */}
      {(() => {
        const catSlug = scheme.beneficiary_type?.[0];
        return (
          <div className="scheme-header-premium">
            <div className="scheme-header-main">
              <div className="hero-eyebrow" style={{ marginBottom: "var(--s3)" }}>
                {scheme.level === "Central" ? t("general.central_scheme") : t("general.state_scheme")}
                {catSlug && ` · ${t(`cat.${catSlug}`)}`}
              </div>
              <h1 className="scheme-title-large">{scheme.name}</h1>
              {scheme.description && (
                <p style={{ color: "rgba(255,255,255,.72)", fontSize: 15, maxWidth: 560, marginBottom: "var(--s5)" }}>
                  {scheme.description.slice(0, 180)}{scheme.description.length > 180 ? "…" : ""}
                </p>
              )}
              <div style={{ display: "flex", gap: "var(--s2)", flexWrap: "wrap", marginBottom: "var(--s5)" }}>
                <span className={`badge ${scheme.level === "Central" ? "badge-central" : "badge-state"}`}>
                  {scheme.level === "Central" ? t("general.central_scheme") : t("general.state_scheme")}
                </span>
                {scheme.state && scheme.state !== "All" && <span className="badge badge-muted">{scheme.state}</span>}
                {(scheme.beneficiary_type ?? []).map((bt) => (
                  <span key={bt} className="badge badge-navy">{t(`cat.${bt}`)}</span>
                ))}
                {scheme.benefit_type && (
                  <span className="badge" style={{ background: "rgba(255,153,51,.15)", color: "var(--saffron-deep)", fontWeight: 700 }}>
                    {BENEFIT_LABELS[scheme.benefit_type] ?? scheme.benefit_type}
                  </span>
                )}
              </div>
              <div className="hero-actions">
                {scheme.apply_url && (
                  <a href={scheme.apply_url} target="_blank" rel="noopener noreferrer" className="btn btn-primary btn-lg">
                    {t("scheme.apply")}
                    <svg width="14" height="14" fill="none" viewBox="0 0 14 14" aria-hidden="true">
                      <path d="M1.5 8.5l7-7M8.5 1.5H3.5M8.5 1.5v5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                    </svg>
                  </a>
                )}
                <Link href={`/${lang}/check`} className="btn btn-lg"
                  style={{ color: "rgba(255,255,255,.75)", border: "1.5px solid rgba(255,255,255,.2)", background: "transparent" }}>
                  {t("hero.cta")}
                </Link>
              </div>
              <SchemeExplainer
                schemeName={scheme.name}
                description={scheme.description ?? null}
                benefitDisplay={benefitDisplay ?? null}
                eligibilityText={scheme.eligibility_text_translated ?? null}
                applyUrl={scheme.apply_url ?? null}
                docs={docs}
                lang={lang}
              />
            </div>
            {catSlug && (
              <div className="scheme-header-visual">
                <div className="scheme-visual-backdrop"
                  style={{ backgroundImage: `url('/scheme-images/cat-${catSlug}.png')` }} />
                <div className="scheme-visual-circle">
                  <Image
                    src={`/scheme-images/cat-${catSlug}.png`}
                    alt=""
                    fill
                    sizes="180px"
                    className="scheme-visual-img"
                    aria-hidden="true"
                  />
                </div>
              </div>
            )}
          </div>
        );
      })()}

      {/* ── Content ── */}
      <div className="wrap" style={{ paddingTop: "var(--s8)", paddingBottom: "var(--s10)" }}>
        <div className="layout-article">

          {/* ── Main ── */}
          <div className="article-body">

            {/* Description */}
            {scheme.description && (
              <p style={{
                fontSize: 15, lineHeight: 1.75, color: "var(--ink)",
                background: "var(--surface)",
                borderLeft: "3px solid var(--saffron)",
                borderRadius: "0 var(--r-md) var(--r-md) 0",
                padding: "var(--s4)", marginBottom: "var(--s6)",
              }}>
                {scheme.description}
              </p>
            )}

            {/* ── Benefit Banner ── */}
            {benefitDisplay && (
              <div style={{
                background: "linear-gradient(135deg, var(--green-tint) 0%, rgba(19,136,8,.08) 100%)",
                border: "1.5px solid rgba(19,136,8,.25)",
                borderRadius: "var(--r-lg)",
                padding: "var(--s5) var(--s6)",
                marginBottom: "var(--s6)",
                display: "flex",
                alignItems: "center",
                gap: "var(--s4)",
              }}>
                <div style={{ fontSize: 36, lineHeight: 1 }}>🎁</div>
                <div>
                  <div style={{ fontSize: 11, fontWeight: 800, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--green-deep)", marginBottom: 4 }}>
                    लाभ — आपको क्या मिलेगा
                  </div>
                  <div style={{ fontSize: 22, fontWeight: 900, color: "var(--green-deep)" }}>
                    {benefitDisplay}
                  </div>
                  {scheme.benefit_type && (
                    <div style={{ fontSize: 12, color: "var(--green-deep)", opacity: 0.7, marginTop: 2 }}>
                      {BENEFIT_LABELS[scheme.benefit_type] ?? scheme.benefit_type}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* ── Eligibility Quick Facts ── */}
            <h2 id="eligibility">{t("scheme.eligibility")}</h2>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
              gap: "var(--s3)",
              margin: "var(--s4) 0 var(--s5)",
            }}>
              {/* Age range */}
              {(scheme.age_min != null || scheme.age_max != null) && (
                <div style={{ background: "var(--navy-tint)", border: "1px solid rgba(11,31,77,.12)", borderRadius: "var(--r-md)", padding: "var(--s3) var(--s4)" }}>
                  <div style={{ fontSize: 10, fontWeight: 800, textTransform: "uppercase", color: "var(--navy)", marginBottom: 4 }}>आयु सीमा</div>
                  <div style={{ fontSize: 18, fontWeight: 900, color: "var(--navy)" }}>
                    {scheme.age_min != null && scheme.age_max != null
                      ? `${scheme.age_min}–${scheme.age_max} वर्ष`
                      : scheme.age_min != null
                        ? `${scheme.age_min}+ वर्ष`
                        : `≤${scheme.age_max} वर्ष`}
                  </div>
                </div>
              )}

              {/* Income */}
              {incomeLimitInr && (
                <div style={{ background: "var(--green-tint)", border: "1px solid rgba(19,136,8,.15)", borderRadius: "var(--r-md)", padding: "var(--s3) var(--s4)" }}>
                  <div style={{ fontSize: 10, fontWeight: 800, textTransform: "uppercase", color: "var(--green-deep)", marginBottom: 4 }}>वार्षिक आय सीमा</div>
                  <div style={{ fontSize: 18, fontWeight: 900, color: "var(--green-deep)" }}>
                    {fmtInr(incomeLimitInr)} तक
                  </div>
                </div>
              )}

              {/* Gender */}
              {scheme.gender && scheme.gender !== "all" && (
                <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: "var(--r-md)", padding: "var(--s3) var(--s4)" }}>
                  <div style={{ fontSize: 10, fontWeight: 800, textTransform: "uppercase", color: "var(--ink-3)", marginBottom: 4 }}>लिंग</div>
                  <div style={{ fontSize: 16, fontWeight: 800, color: "var(--ink)" }}>
                    {GENDER_LABELS[scheme.gender] ?? scheme.gender}
                  </div>
                </div>
              )}

              {/* Residence */}
              {scheme.residence_type && (
                <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: "var(--r-md)", padding: "var(--s3) var(--s4)" }}>
                  <div style={{ fontSize: 10, fontWeight: 800, textTransform: "uppercase", color: "var(--ink-3)", marginBottom: 4 }}>क्षेत्र</div>
                  <div style={{ fontSize: 16, fontWeight: 800, color: "var(--ink)" }}>
                    {RESIDENCE_LABELS[scheme.residence_type] ?? scheme.residence_type}
                  </div>
                </div>
              )}

              {/* Employment */}
              {scheme.employment_status && scheme.employment_status !== "any" && (
                <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: "var(--r-md)", padding: "var(--s3) var(--s4)" }}>
                  <div style={{ fontSize: 10, fontWeight: 800, textTransform: "uppercase", color: "var(--ink-3)", marginBottom: 4 }}>रोजगार</div>
                  <div style={{ fontSize: 16, fontWeight: 800, color: "var(--ink)" }}>
                    {EMPLOYMENT_LABELS[scheme.employment_status] ?? scheme.employment_status}
                  </div>
                </div>
              )}

              {/* State */}
              {scheme.state && scheme.state !== "All" && (
                <div style={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: "var(--r-md)", padding: "var(--s3) var(--s4)" }}>
                  <div style={{ fontSize: 10, fontWeight: 800, textTransform: "uppercase", color: "var(--ink-3)", marginBottom: 4 }}>राज्य</div>
                  <div style={{ fontSize: 15, fontWeight: 700, color: "var(--ink)" }}>{scheme.state}</div>
                </div>
              )}

              {/* Class range (education schemes) */}
              {scheme.min_class && (
                <div style={{ background: "var(--navy-tint)", border: "1px solid rgba(11,31,77,.1)", borderRadius: "var(--r-md)", padding: "var(--s3) var(--s4)" }}>
                  <div style={{ fontSize: 10, fontWeight: 800, textTransform: "uppercase", color: "var(--navy)", marginBottom: 4 }}>कक्षा</div>
                  <div style={{ fontSize: 18, fontWeight: 900, color: "var(--navy)" }}>
                    {scheme.min_class}{scheme.max_class ? ` – ${scheme.max_class}` : "+"}
                  </div>
                </div>
              )}
            </div>

            {/* ── Translated eligibility text ── */}
            {scheme.eligibility_text_translated && (
              <div style={{
                background: "var(--navy-tint)",
                border: "1px solid rgba(11,31,77,.1)",
                borderRadius: "var(--r-md)",
                padding: "var(--s4)",
                marginBottom: "var(--s5)",
                fontSize: 14,
                lineHeight: 1.7,
                color: "var(--ink)",
              }}>
                {scheme.eligibility_text_translated}
              </div>
            )}

            {/* ── Caste / Category ── */}
            {(scheme.caste_categories?.length > 0 || scheme.for_sc_st || scheme.for_minority) && (
              <div style={{ marginBottom: "var(--s6)" }}>
                <h3>जाति / श्रेणी</h3>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--s2)", marginTop: "var(--s3)" }}>
                  {(scheme.caste_categories ?? []).map((c) => (
                    <span key={c} className="badge badge-navy">{c}</span>
                  ))}
                  {scheme.for_sc_st && !scheme.caste_categories?.length && (
                    <span className="badge badge-navy">SC/ST</span>
                  )}
                  {scheme.for_minority && !scheme.minority_required && (
                    <span className="badge badge-navy">अल्पसंख्यक</span>
                  )}
                  {scheme.minority_required && (
                    <span className="badge badge-navy">अल्पसंख्यक (अनिवार्य)</span>
                  )}
                  {scheme.disability_required && (
                    <span className="badge badge-saffron">दिव्यांग (अनिवार्य)</span>
                  )}
                </div>
              </div>
            )}

            {/* ── Special Beneficiary Flags ── */}
            {(scheme.for_widow || scheme.for_pregnant || scheme.for_shg || scheme.for_girl_child) && (
              <div style={{ marginBottom: "var(--s6)" }}>
                <h3>विशेष लाभार्थी</h3>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--s2)", marginTop: "var(--s3)" }}>
                  {scheme.for_widow      && <span className="badge badge-saffron">विधवा महिला</span>}
                  {scheme.for_pregnant   && <span className="badge badge-saffron">गर्भवती महिला</span>}
                  {scheme.for_shg        && <span className="badge badge-saffron">SHG सदस्य</span>}
                  {scheme.for_girl_child && <span className="badge badge-green">बालिका</span>}
                </div>
              </div>
            )}

            {/* ── Documents Required ── */}
            {docs.length > 0 && (
              <div style={{ marginBottom: "var(--s8)" }}>
                <h2 id="documents">आवश्यक दस्तावेज़</h2>
                <div style={{
                  background: "var(--surface)",
                  border: "1px solid var(--line)",
                  borderRadius: "var(--r-lg)",
                  overflow: "hidden",
                  marginTop: "var(--s4)",
                }}>
                  {docs.map((doc, i) => (
                    <div key={i} style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "var(--s3)",
                      padding: "var(--s3) var(--s5)",
                      borderBottom: i < docs.length - 1 ? "1px solid var(--line)" : "none",
                    }}>
                      <div style={{
                        width: 24, height: 24, borderRadius: "50%",
                        background: doc.mandatory ? "var(--saffron)" : "var(--navy-tint)",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        flexShrink: 0, fontSize: 12,
                      }}>
                        {doc.mandatory ? "✓" : "○"}
                      </div>
                      <div style={{ flex: 1 }}>
                        <span style={{ fontSize: 14, fontWeight: doc.mandatory ? 600 : 400, color: "var(--ink)" }}>
                          {doc.doc_name}
                        </span>
                        {doc.mandatory && (
                          <span style={{ fontSize: 11, marginLeft: "var(--s2)", color: "var(--saffron-deep)", fontWeight: 700 }}>
                            अनिवार्य
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                <p style={{ fontSize: 12, color: "var(--ink-3)", marginTop: "var(--s2)" }}>
                  ✓ = अनिवार्य दस्तावेज़ · ○ = सहायक दस्तावेज़
                </p>
              </div>
            )}

            {/* ── How to Apply ── */}
            <h2 id="how-to-apply">{t("scheme.how_to_apply")}</h2>
            <SchemeFlowDiagram steps={applySteps({
              applyUrl: scheme.apply_url ?? undefined,
              mandatoryDocNames: docs.filter(d => d.mandatory).map(d => d.doc_name),
            })} />

            {scheme.apply_url && (
              <a href={scheme.apply_url} target="_blank" rel="noopener noreferrer"
                className="btn btn-primary" style={{ marginTop: "var(--s2)" }}>
                ऑनलाइन आवेदन करें
                <svg width="12" height="12" fill="none" viewBox="0 0 12 12" aria-hidden="true">
                  <path d="M1 6h10M7 2l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </a>
            )}

            {/* ── FAQ ── */}
            <h2 id="faq" style={{ marginTop: "var(--s8)" }}>{t("scheme.faq")}</h2>
            <FaqAccordion items={[
              {
                q: `${scheme.name} के लिए कौन आवेदन कर सकता है?`,
                a: [
                  (scheme.beneficiary_type || []).map(bt => t(`cat.${bt}`)).join(", ") || "सभी नागरिक",
                  scheme.state && scheme.state !== "All" ? `यह योजना ${scheme.state} राज्य के लिए है।` : "यह एक केंद्रीय योजना है।",
                  scheme.gender && scheme.gender !== "all" ? `केवल ${GENDER_LABELS[scheme.gender] ?? scheme.gender} के लिए।` : "",
                  incomeLimitInr ? `वार्षिक आय ${fmtInr(incomeLimitInr)} तक होनी चाहिए।` : "",
                ].filter(Boolean).join(" "),
              },
              {
                q: "इस योजना से कितना लाभ मिलेगा?",
                a: benefitDisplay
                  ? `इस योजना के तहत ${benefitDisplay} का लाभ मिलता है। अधिक जानकारी के लिए आधिकारिक वेबसाइट देखें।`
                  : "लाभ राशि के लिए आधिकारिक वेबसाइट देखें।",
              },
              { q: "आवेदन की अंतिम तिथि क्या है?", a: "आवेदन की अंतिम तिथि के लिए आधिकारिक वेबसाइट देखें। अधिकांश योजनाओं में आवेदन पूरे साल खुला रहता है।" },
              { q: "क्या यह योजना निःशुल्क है?", a: "हाँ, यह सरकारी योजना पूरी तरह निःशुल्क है। किसी भी दलाल या एजेंट को पैसे न दें।" },
            ]} />

            {/* ── CTA ── */}
            <div className="cta-card" style={{ marginTop: "var(--s8)" }}>
              <div>
                <h3>और योजनाएं खोजें</h3>
                <p>{t("hero.sub")}</p>
              </div>
              <Link href={`/${lang}/check`} className="btn btn-primary">
                {t("hero.cta")}
              </Link>
            </div>

            {/* ── Language bar ── */}
            <div className="lang-bar" aria-label="This page in other languages">
              <span>अन्य भाषाओं में:</span>
              {languages.slice(0, 12).map((l) => (
                <Link
                  key={l.code}
                  href={`/${l.code}/yojana/s/${slug}`}
                  className={l.code === lang ? "active" : ""}
                  aria-current={l.code === lang ? "true" : undefined}
                >
                  {l.native}
                </Link>
              ))}
            </div>
          </div>

          {/* ── Sidebar ── */}
          <aside className="sidebar" aria-label="Scheme details">

            {/* Benefit highlight */}
            {benefitDisplay && (
              <div className="sidebar-card" style={{ background: "var(--green-tint)", border: "1.5px solid rgba(19,136,8,.2)" }}>
                <div style={{ fontSize: 11, fontWeight: 800, textTransform: "uppercase", color: "var(--green-deep)", marginBottom: "var(--s2)" }}>
                  लाभ
                </div>
                <div style={{ fontSize: 20, fontWeight: 900, color: "var(--green-deep)", lineHeight: 1.2 }}>
                  {benefitDisplay}
                </div>
                {scheme.benefit_type && (
                  <div style={{ fontSize: 11, color: "var(--green-deep)", opacity: 0.7, marginTop: "var(--s1)" }}>
                    {BENEFIT_LABELS[scheme.benefit_type] ?? scheme.benefit_type}
                  </div>
                )}
              </div>
            )}

            {/* Quick facts */}
            <div className="sidebar-card">
              <h4>त्वरित जानकारी</h4>
              {[
                { label: "स्तर", value: scheme.level === "Central" ? t("general.central_scheme") : t("general.state_scheme") },
                scheme.state && scheme.state !== "All" ? { label: "राज्य", value: scheme.state } : null,
                scheme.ministry ? { label: "मंत्रालय", value: scheme.ministry } : null,
                (scheme.age_min != null || scheme.age_max != null) ? {
                  label: "आयु",
                  value: scheme.age_min != null && scheme.age_max != null
                    ? `${scheme.age_min}–${scheme.age_max} वर्ष`
                    : scheme.age_min != null ? `${scheme.age_min}+ वर्ष` : `≤${scheme.age_max} वर्ष`,
                  highlight: false,
                } : null,
                incomeLimitInr ? { label: "आय सीमा", value: `${fmtInr(incomeLimitInr)} तक`, highlight: true } : null,
                scheme.gender && scheme.gender !== "all" ? { label: "लिंग", value: GENDER_LABELS[scheme.gender] ?? scheme.gender } : null,
                scheme.residence_type ? { label: "क्षेत्र", value: RESIDENCE_LABELS[scheme.residence_type] ?? scheme.residence_type } : null,
                scheme.employment_status && scheme.employment_status !== "any" ? { label: "रोजगार", value: EMPLOYMENT_LABELS[scheme.employment_status] ?? scheme.employment_status } : null,
                (scheme.caste_categories?.length) ? { label: "जाति", value: scheme.caste_categories.join(", ") } : null,
                scheme.min_class ? { label: "कक्षा", value: `${scheme.min_class}${scheme.max_class ? ` – ${scheme.max_class}` : "+"}` } : null,
              ].filter(Boolean).map((item) => (
                item && (
                  <div key={item.label} className="sidebar-item">
                    <span className="label">{item.label}</span>
                    <span className="value" style={item.highlight ? { color: "var(--green)", fontWeight: 800 } : {}}>
                      {item.value}
                    </span>
                  </div>
                )
              ))}
            </div>

            {/* Documents summary */}
            {docs.length > 0 && (
              <div className="sidebar-card">
                <h4>दस्तावेज़ ({docs.length})</h4>
                {docs.slice(0, 5).map((doc, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: "var(--s2)", marginBottom: "var(--s2)", fontSize: 13 }}>
                    <span style={{ color: doc.mandatory ? "var(--saffron-deep)" : "var(--ink-3)", flexShrink: 0, fontWeight: 700 }}>
                      {doc.mandatory ? "●" : "○"}
                    </span>
                    <span style={{ color: "var(--ink-2)" }}>{doc.doc_name}</span>
                  </div>
                ))}
                {docs.length > 5 && (
                  <div style={{ fontSize: 12, color: "var(--ink-3)" }}>+{docs.length - 5} और</div>
                )}
              </div>
            )}

            {/* Apply */}
            {scheme.apply_url && (
              <div className="sidebar-card" style={{ textAlign: "center" }}>
                <a href={scheme.apply_url} target="_blank" rel="noopener noreferrer"
                  className="btn btn-primary btn-block btn-lg">
                  {t("scheme.apply")}
                </a>
                <p style={{ fontSize: 11, color: "var(--ink-3)", marginTop: "var(--s2)" }}>
                  {t("general.official_site")}
                </p>
              </div>
            )}

            {/* Related */}
            {related.length > 0 && (
              <div className="sidebar-card">
                <h4>संबंधित योजनाएं</h4>
                {related.map((r) => (
                  <div key={r.slug} className="related-link">
                    <span className="related-link-dot" aria-hidden="true" />
                    <Link href={`/${lang}/yojana/s/${r.slug}`}>{r.name}</Link>
                  </div>
                ))}
              </div>
            )}

            {/* Eligibility CTA */}
            <div className="sidebar-card"
              style={{ background: "var(--navy)", borderColor: "var(--navy)" }}>
              <div style={{ fontSize: 13, fontWeight: 800, color: "#fff", marginBottom: "var(--s2)" }}>
                अपनी पात्रता जाँचें
              </div>
              <p style={{ fontSize: 12, color: "rgba(255,255,255,.6)", marginBottom: "var(--s4)" }}>
                2 मिनट में जानें कि आप किन योजनाओं के लिए eligible हैं
              </p>
              <Link href={`/${lang}/check`} className="btn btn-primary btn-block">
                {t("hero.cta")}
              </Link>
            </div>

            {/* Data confidence note */}
            {isEnriched && scheme.enrichment_confidence != null && (
              <div style={{
                fontSize: 11, color: "var(--ink-3)",
                textAlign: "center",
                padding: "var(--s3)",
                border: "1px dashed var(--line)",
                borderRadius: "var(--r-sm)",
              }}>
                AI-विश्लेषण विश्वसनीयता: {Math.round(scheme.enrichment_confidence * 100)}%
                <br />
                <span style={{ fontSize: 10 }}>आधिकारिक वेबसाइट से सत्यापित करें</span>
              </div>
            )}
          </aside>
        </div>
      </div>
    </div>
  );
}
