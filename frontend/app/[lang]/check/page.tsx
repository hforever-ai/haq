"use client";

import { useState } from "react";
import Link from "next/link";
import { use } from "react";
import LottiePlayer from "@/components/ui/LottiePlayer";

// ── Types ───────────────────────────────────────────────────────────────────
interface Profile {
  state: string;
  age: number | null;
  gender: string;
  caste: string;
  has_bpl: boolean;
  income: number;  // annual INR (0 = not provided)
  residence: string;
}

interface SchemeResult {
  id: number;
  slug: string;
  name: string;
  short_title: string;
  state: string;
  level: string;
  ministry: string;
  description: string;
  apply_url: string;
  beneficiary_type: string[];
  benefit_type: string | null;
  benefit_amount_inr: number | null;
  benefit_amount_description: string | null;
  age_min: number | null;
  age_max: number | null;
  caste_categories: string[];
}

// ── Constants ───────────────────────────────────────────────────────────────
const STATES = [
  "Andaman and Nicobar Islands","Andhra Pradesh","Arunachal Pradesh","Assam","Bihar",
  "Chandigarh","Chhattisgarh","Dadra & Nagar Haveli and Daman & Diu","Delhi","Goa",
  "Gujarat","Haryana","Himachal Pradesh","Jammu and Kashmir","Jharkhand","Karnataka",
  "Kerala","Ladakh","Lakshadweep","Madhya Pradesh","Maharashtra","Manipur","Meghalaya",
  "Mizoram","Nagaland","Odisha","Puducherry","Punjab","Rajasthan","Sikkim",
  "Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal",
];

const INCOME_RANGES = [
  { label: "₹0 – ₹1 लाख",    value: 100000  },
  { label: "₹1 – ₹2.5 लाख",  value: 250000  },
  { label: "₹2.5 – ₹5 लाख",  value: 500000  },
  { label: "₹5 – ₹10 लाख",   value: 1000000 },
  { label: "₹10 लाख से ज़्यादा", value: 1500000 },
];

const BENEFIT_LABELS: Record<string, string> = {
  cash: "नकद सहायता", pension: "पेंशन", education: "शिक्षा",
  housing: "आवास", health: "स्वास्थ्य", loan: "ऋण/लोन",
  subsidy: "सब्सिडी", insurance: "बीमा", skill_development: "कौशल प्रशिक्षण",
  food_security: "खाद्य सुरक्षा", kind: "वस्तु सहायता", service: "सेवा",
};

// ── Eligibility reason builder ───────────────────────────────────────────────
function buildReasons(s: SchemeResult, profile: Profile): string[] {
  const reasons: string[] = [];
  if (profile.age && s.age_min && s.age_max)
    reasons.push(`आपकी उम्र ${profile.age} साल, पात्रता: ${s.age_min}–${s.age_max} साल`);
  if (profile.gender === "female" && s.beneficiary_type?.includes("women"))
    reasons.push("महिलाओं के लिए विशेष योजना");
  if (profile.state && s.state !== "All" && s.state === profile.state)
    reasons.push(`${profile.state} राज्य योजना`);
  if (s.caste_categories?.length && profile.caste && s.caste_categories.includes(profile.caste))
    reasons.push(`${profile.caste} वर्ग के लिए`);
  if (s.benefit_type && BENEFIT_LABELS[s.benefit_type])
    reasons.push(BENEFIT_LABELS[s.benefit_type]);
  return reasons;
}

// ── Components ───────────────────────────────────────────────────────────────
function WizardProgress({ step, total }: { step: number; total: number }) {
  const pct = Math.round((step / total) * 100);
  return (
    <div>
      <div className="wizard-progress-track">
        <div className="wizard-progress-fill" style={{ width: `${pct}%` }} />
      </div>
      <p style={{ color: "rgba(255,255,255,.45)", fontSize: 12, textAlign: "center", margin: "6px 0 0", letterSpacing: ".04em" }}>
        प्रश्न {step}/{total}
      </p>
    </div>
  );
}

function BigBtn({ onClick, children, secondary }: { onClick: () => void; children: React.ReactNode; secondary?: boolean }) {
  return (
    <button onClick={onClick} style={{
      padding: "16px 24px", borderRadius: 12, fontSize: 16, fontWeight: 700, cursor: "pointer",
      border: secondary ? "2px solid var(--navy)" : "none",
      background: secondary ? "transparent" : "var(--navy)",
      color: secondary ? "var(--navy)" : "#fff",
      transition: "opacity .15s",
    }}>
      {children}
    </button>
  );
}

function OptionCard({ selected, onClick, children }: { selected: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button onClick={onClick} style={{
      padding: "18px 20px", borderRadius: 14, fontSize: 16, fontWeight: 600,
      cursor: "pointer", textAlign: "left", width: "100%",
      border: `2.5px solid ${selected ? "var(--saffron)" : "rgba(11,31,77,.12)"}`,
      background: selected ? "rgba(255,153,51,.08)" : "#fff",
      color: "var(--navy)", transition: "border-color .15s, background .15s",
      display: "flex", alignItems: "center", gap: 12,
    }}>
      <span style={{
        width: 22, height: 22, borderRadius: "50%", flexShrink: 0,
        border: `2.5px solid ${selected ? "var(--saffron)" : "rgba(11,31,77,.25)"}`,
        background: selected ? "var(--saffron)" : "transparent",
        display: "grid", placeItems: "center",
      }}>
        {selected && <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#fff" }} />}
      </span>
      {children}
    </button>
  );
}

function SchemeCard({ scheme, profile }: { scheme: SchemeResult; profile: Profile }) {
  const [open, setOpen] = useState(false);
  const reasons = buildReasons(scheme, profile);
  const langSlug = typeof window !== "undefined"
    ? window.location.pathname.split("/")[1] || "hi"
    : "hi";

  return (
    <div style={{
      background: "#fff", borderRadius: 16, padding: "var(--s5)",
      border: "1.5px solid rgba(11,31,77,.08)",
      boxShadow: "0 2px 12px rgba(11,31,77,.06)",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
        <div style={{ flex: 1 }}>
          {scheme.benefit_type && BENEFIT_LABELS[scheme.benefit_type] && (
            <span style={{
              display: "inline-block", marginBottom: 8,
              fontSize: 11, fontWeight: 700, letterSpacing: ".05em", textTransform: "uppercase",
              background: "rgba(255,153,51,.12)", color: "var(--saffron-deep)",
              padding: "3px 8px", borderRadius: 6,
            }}>
              {BENEFIT_LABELS[scheme.benefit_type]}
            </span>
          )}
          <h3 style={{ fontSize: 16, fontWeight: 700, color: "var(--navy)", margin: 0, lineHeight: 1.3 }}>
            {scheme.name}
          </h3>
          {scheme.ministry && (
            <p style={{ fontSize: 12, color: "var(--ink-3)", margin: "4px 0 0" }}>{scheme.ministry}</p>
          )}
        </div>
        <span style={{
          flexShrink: 0, fontSize: 11, padding: "4px 10px", borderRadius: 20, fontWeight: 700,
          background: scheme.level === "Central" ? "rgba(11,31,77,.08)" : "rgba(19,136,8,.1)",
          color: scheme.level === "Central" ? "var(--navy)" : "#138808",
        }}>
          {scheme.level === "Central" ? "केंद्र" : scheme.state}
        </span>
      </div>

      {/* Benefit amount */}
      {(scheme.benefit_amount_inr || scheme.benefit_amount_description) && (
        <div style={{
          margin: "var(--s3) 0", padding: "10px 14px", borderRadius: 10,
          background: "rgba(19,136,8,.06)", border: "1px solid rgba(19,136,8,.15)",
        }}>
          <span style={{ fontSize: 13, color: "#138808", fontWeight: 700 }}>
            {scheme.benefit_amount_inr
              ? `₹${scheme.benefit_amount_inr.toLocaleString("hi-IN")}`
              : scheme.benefit_amount_description}
          </span>
        </div>
      )}

      {/* Why eligible */}
      <button
        onClick={() => setOpen((p) => !p)}
        style={{
          background: "none", border: "none", cursor: "pointer",
          fontSize: 13, color: "var(--saffron-deep)", fontWeight: 600,
          padding: "8px 0", display: "flex", alignItems: "center", gap: 5,
        }}
      >
        <span>{open ? "▲" : "▼"}</span> आप पात्र क्यों हैं?
      </button>

      {open && reasons.length > 0 && (
        <ul style={{ margin: "4px 0 12px", paddingLeft: 20, fontSize: 13, color: "var(--ink-2)" }}>
          {reasons.map((r) => <li key={r}>{r}</li>)}
        </ul>
      )}

      {scheme.apply_url && (
        <a
          href={scheme.apply_url}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: "inline-flex", alignItems: "center", gap: 6,
            padding: "10px 18px", borderRadius: 10, fontSize: 14, fontWeight: 700,
            background: "var(--saffron)", color: "var(--navy)",
            textDecoration: "none", marginTop: "var(--s2)",
          }}
        >
          आवेदन करें
          <svg width="12" height="12" fill="none" viewBox="0 0 12 12" aria-hidden="true">
            <path d="M2 10L10 2M10 2H6M10 2v4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </a>
      )}

      <Link
        href={`/${langSlug}/yojana/s/${scheme.slug}`}
        style={{ marginLeft: 12, fontSize: 13, color: "var(--ink-3)", textDecoration: "underline" }}
      >
        और जानें
      </Link>
    </div>
  );
}

// ── Main wizard ──────────────────────────────────────────────────────────────
export default function CheckPage({ params }: { params: Promise<{ lang: string }> }) {
  const { lang } = use(params);
  const TOTAL_STEPS = 7;

  const [step, setStep]       = useState(0);  // 0=welcome, 1-7=questions, 8=results
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SchemeResult[] | null>(null);
  const [profile, setProfile] = useState<Profile>({
    state: "", age: null, gender: "", caste: "", has_bpl: false, income: 0, residence: "",
  });

  function next() {
    if (step < TOTAL_STEPS) setStep((s) => s + 1);
    else fetchResults();
  }
  function back() { setStep((s) => Math.max(0, s - 1)); }

  async function fetchResults() {
    setLoading(true);
    setStep(8);
    try {
      const qp = new URLSearchParams({
        gender:         profile.gender || "female",
        age:            String(profile.age || 30),
        state:          profile.state || "All",
        income:         String(profile.income),
        caste:          profile.caste,
        residence:      profile.residence,
        has_bpl:        profile.has_bpl ? "1" : "0",
        has_disability: "0",
        is_minority:    "0",
      });
      // Use relative URL — nginx proxies /api/* to FastAPI on all environments
      const res = await fetch(`/api/check/results?${qp}`);
      const data = await res.json();
      setResults(data.schemes || []);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  function restart() {
    setStep(0);
    setResults(null);
    setProfile({ state: "", age: null, gender: "", caste: "", has_bpl: false, income: 0, residence: "" });
  }

  // ── Styles ─────────────────────────────────────────────────────────────────
  const wrap: React.CSSProperties = {
    maxWidth: 560, margin: "0 auto", padding: "var(--s6) var(--s4)",
  };
  const card: React.CSSProperties = {
    background: "#fff", borderRadius: 20, padding: "var(--s7)",
    boxShadow: "0 8px 40px rgba(11,31,77,.10)", border: "1px solid rgba(11,31,77,.06)",
  };
  const qLabel: React.CSSProperties = {
    fontSize: 22, fontWeight: 800, color: "var(--navy)",
    marginBottom: "var(--s5)", lineHeight: 1.3,
  };

  // ── Welcome ─────────────────────────────────────────────────────────────────
  if (step === 0) return (
    <div style={{ background: "var(--page)", minHeight: "100vh" }}>
      <div style={{ background: "linear-gradient(150deg,#0B1F4D 0%,#16306B 100%)", padding: "var(--s10) 0 var(--s8)" }}>
        <div style={wrap}>
          <div style={{ color: "rgba(255,255,255,.6)", fontSize: 14, marginBottom: "var(--s3)" }}>
            Aarambha Haq · पात्रता जाँच
          </div>
          <h1 style={{ color: "#fff", fontSize: "clamp(24px,5vw,36px)", lineHeight: 1.2, marginBottom: "var(--s4)" }}>
            आपके लिए कौन सी सरकारी योजनाएं हैं?
          </h1>
          <p style={{ color: "rgba(255,255,255,.65)", fontSize: 16, marginBottom: "var(--s7)", maxWidth: 420 }}>
            7 आसान सवालों के जवाब दीजिए। हम 2,754 योजनाओं में से आपके लिए सही योजनाएं खोजेंगे।
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--s3)", marginBottom: "var(--s7)" }}>
            {["बिल्कुल मुफ्त", "2 मिनट में", "22 भाषाओं में"].map((t) => (
              <span key={t} style={{
                fontSize: 13, fontWeight: 700, padding: "6px 14px", borderRadius: 20,
                background: "rgba(255,255,255,.1)", color: "rgba(255,255,255,.8)",
                border: "1px solid rgba(255,255,255,.15)",
              }}>{t}</span>
            ))}
          </div>
          <button onClick={() => setStep(1)} style={{
            padding: "16px 40px", borderRadius: 14, fontSize: 18, fontWeight: 800,
            background: "var(--saffron)", color: "var(--navy)", border: "none", cursor: "pointer",
            display: "inline-flex", alignItems: "center", gap: 10,
          }}>
            शुरू करें
            <svg width="18" height="18" fill="none" viewBox="0 0 18 18" aria-hidden="true">
              <path d="M3 9h12M10 4l5 5-5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      </div>
      <div style={wrap}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(140px,1fr))", gap: "var(--s4)", marginTop: "var(--s6)" }}>
          {[
            { n: "2,754+", label: "योजनाएं" },
            { n: "36",     label: "राज्य / केंद्र" },
            { n: "15",     label: "श्रेणियां" },
          ].map(({ n, label }) => (
            <div key={n} style={{
              textAlign: "center", padding: "var(--s5)",
              background: "#fff", borderRadius: 14, border: "1.5px solid rgba(11,31,77,.07)",
            }}>
              <div style={{ fontSize: 28, fontWeight: 900, color: "var(--navy)" }}>{n}</div>
              <div style={{ fontSize: 13, color: "var(--ink-2)", marginTop: 4 }}>{label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // ── Results ─────────────────────────────────────────────────────────────────
  if (step === 8) return (
    <div style={{ background: "var(--page)", minHeight: "100vh" }}>
      {loading ? (
        <div className="wizard-result-hero" style={{ background: "linear-gradient(150deg,#0B1F4D 0%,#16306B 100%)" }}>
          <div style={wrap}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 20, paddingTop: "var(--s8)", paddingBottom: "var(--s8)" }}>
              <LottiePlayer src="state-loading.json" size={80} loop autoplay />
              <div style={{ color: "rgba(255,255,255,.8)", fontSize: 18, fontWeight: 700 }}>योजनाएं खोज रहे हैं...</div>
              <div style={{ color: "rgba(255,255,255,.4)", fontSize: 14 }}>2,754 योजनाओं में से आपके लिए छाँट रहे हैं</div>
            </div>
          </div>
        </div>
      ) : results && results.length > 0 ? (
        <div className="wizard-result-hero">
          <div style={wrap}>
            <LottiePlayer src="state-success.json" size={64} loop autoplay style={{ marginBottom: "var(--s3)" }} />
            <div className="wizard-result-number">{results.length}</div>
            <h1 style={{ color: "var(--navy)", margin: "var(--s2) 0 var(--s1)", fontSize: "clamp(20px,4vw,28px)" }}>
              योजनाएं मिलीं आपके लिए!
            </h1>
            <p style={{ color: "var(--ink-2)", fontSize: 14, margin: 0 }}>
              {profile.state && `${profile.state} · `}
              {profile.gender === "female" ? "महिला" : profile.gender === "male" ? "पुरुष" : ""}
              {profile.age ? ` · ${profile.age} साल` : ""}
            </p>
          </div>
        </div>
      ) : (
        <div style={{ background: "var(--navy)", padding: "var(--s6) 0" }}>
          <div style={wrap}>
            <h1 style={{ color: "#fff", margin: 0 }}>कोई योजना नहीं मिली</h1>
          </div>
        </div>
      )}

      <div style={wrap}>
        <button onClick={restart} style={{
          background: "none", border: "1.5px solid var(--navy)", borderRadius: 10,
          padding: "10px 20px", fontSize: 14, fontWeight: 700, color: "var(--navy)",
          cursor: "pointer", margin: "var(--s5) 0",
        }}>
          ← नई जाँच करें
        </button>

        {!loading && results && results.length === 0 && (
          <div className="wizard-empty-state">
            <LottiePlayer src="state-empty.json" size={100} loop autoplay
              style={{ margin: "0 auto var(--s4)" }} />
            <h3>फ़िल्टर कम करके देखें</h3>
            <p>अपना राज्य बदलें या जाति/आय जानकारी हटाकर दोबारा कोशिश करें।</p>
            <div style={{ display: "flex", gap: "var(--s3)", justifyContent: "center", flexWrap: "wrap", marginTop: "var(--s5)" }}>
              <button onClick={restart} style={{
                padding: "12px 24px", borderRadius: 12, fontSize: 14, fontWeight: 700,
                background: "var(--saffron)", color: "var(--navy)", border: "none", cursor: "pointer",
              }}>
                दोबारा कोशिश करें
              </button>
              <Link href={`/${lang}/yojana`} className="btn btn-outline">
                सभी योजनाएं देखें
              </Link>
            </div>
          </div>
        )}

        {!loading && results && results.length > 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--s4)", paddingBottom: "var(--s10)" }}>
            {results.map((s) => (
              <SchemeCard key={s.id} scheme={s} profile={profile} />
            ))}
            <div style={{ textAlign: "center", paddingTop: "var(--s4)" }}>
              <Link href={`/${lang}/yojana`} style={{ fontSize: 14, color: "var(--ink-2)" }}>
                सभी 2,754 योजनाएं देखें →
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  // ── Question steps ───────────────────────────────────────────────────────────
  const isLastStep = step === TOTAL_STEPS;

  return (
    <div style={{ background: "var(--page)", minHeight: "100vh" }}>
      <div style={{ background: "var(--navy)", padding: "var(--s4) 0 var(--s5)" }}>
        <div style={{ ...wrap, paddingTop: "var(--s2)", paddingBottom: "var(--s2)" }}>
          <WizardProgress step={step} total={TOTAL_STEPS} />
        </div>
      </div>

      <div style={wrap}>
        <div style={card} className="wizard-step-card" key={step}>

          {/* Step 1: State */}
          {step === 1 && (
            <>
              <p style={qLabel}>आप किस राज्य में रहते हैं?</p>
              <select
                value={profile.state}
                onChange={(e) => setProfile((p) => ({ ...p, state: e.target.value }))}
                style={{
                  width: "100%", padding: "14px 16px", borderRadius: 12, fontSize: 16,
                  border: "2px solid rgba(11,31,77,.15)", background: "#fff", color: "var(--navy)",
                  fontWeight: 600, cursor: "pointer", appearance: "none",
                  backgroundImage: `url("data:image/svg+xml,%3Csvg width='16' height='16' viewBox='0 0 16 16' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M4 6l4 4 4-4' stroke='%230B1F4D' stroke-width='1.5' stroke-linecap='round'/%3E%3C/svg%3E")`,
                  backgroundRepeat: "no-repeat", backgroundPosition: "right 14px center",
                  paddingRight: 40,
                }}
              >
                <option value="">— राज्य चुनें —</option>
                {STATES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
              <p style={{ fontSize: 13, color: "var(--ink-3)", marginTop: "var(--s3)" }}>
                केंद्रीय योजनाएं सभी राज्यों में लागू होती हैं।
              </p>
            </>
          )}

          {/* Step 2: Age */}
          {step === 2 && (
            <>
              <p style={qLabel}>आपकी उम्र कितनी है?</p>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--s3)" }}>
                {[
                  { label: "18–30 साल", min: 18, max: 30 },
                  { label: "31–45 साल", min: 31, max: 45 },
                  { label: "46–60 साल", min: 46, max: 60 },
                  { label: "60 से ऊपर", min: 61, max: 99 },
                ].map(({ label, min, max }) => {
                  const midAge = Math.round((min + max) / 2);
                  const sel = profile.age !== null && profile.age >= min && profile.age <= max;
                  return (
                    <OptionCard key={label} selected={sel} onClick={() => setProfile((p) => ({ ...p, age: midAge }))}>
                      {label}
                    </OptionCard>
                  );
                })}
              </div>
              <div style={{ marginTop: "var(--s4)", display: "flex", alignItems: "center", gap: "var(--s3)" }}>
                <label style={{ fontSize: 13, color: "var(--ink-2)", whiteSpace: "nowrap" }}>सटीक उम्र:</label>
                <input
                  type="number" min={1} max={120}
                  value={profile.age ?? ""}
                  onChange={(e) => setProfile((p) => ({ ...p, age: parseInt(e.target.value) || null }))}
                  placeholder="जैसे: 35"
                  style={{
                    flex: 1, padding: "12px 14px", borderRadius: 10, fontSize: 16,
                    border: "2px solid rgba(11,31,77,.15)", color: "var(--navy)", fontWeight: 700,
                  }}
                />
              </div>
            </>
          )}

          {/* Step 3: Gender */}
          {step === 3 && (
            <>
              <p style={qLabel}>आप पुरुष हैं या महिला?</p>
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--s3)" }}>
                {[
                  { value: "female", label: "महिला", icon: "👩" },
                  { value: "male",   label: "पुरुष", icon: "👨" },
                  { value: "other",  label: "अन्य / ट्रांसजेंडर", icon: "🏳️‍⚧️" },
                ].map(({ value, label, icon }) => (
                  <OptionCard key={value} selected={profile.gender === value}
                    onClick={() => setProfile((p) => ({ ...p, gender: value }))}>
                    <span style={{ fontSize: 22 }}>{icon}</span>
                    <span>{label}</span>
                  </OptionCard>
                ))}
              </div>
            </>
          )}

          {/* Step 4: Caste */}
          {step === 4 && (
            <>
              <p style={qLabel}>आप किस जाति वर्ग से हैं?</p>
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--s3)" }}>
                {[
                  { value: "SC",      label: "अनुसूचित जाति (SC)" },
                  { value: "ST",      label: "अनुसूचित जनजाति (ST)" },
                  { value: "OBC",     label: "अन्य पिछड़ा वर्ग (OBC)" },
                  { value: "EWS",     label: "आर्थिक रूप से कमजोर (EWS)" },
                  { value: "General", label: "सामान्य वर्ग" },
                  { value: "unknown", label: "मुझे नहीं पता" },
                ].map(({ value, label }) => (
                  <OptionCard key={value} selected={profile.caste === value}
                    onClick={() => setProfile((p) => ({ ...p, caste: value }))}>
                    {label}
                  </OptionCard>
                ))}
              </div>
            </>
          )}

          {/* Step 5: BPL / Income */}
          {step === 5 && (
            <>
              <p style={qLabel}>क्या आपके पास BPL राशन कार्ड है?</p>
              <div style={{ display: "flex", gap: "var(--s3)", marginBottom: "var(--s5)" }}>
                <OptionCard selected={profile.has_bpl} onClick={() => setProfile((p) => ({ ...p, has_bpl: true, income: 0 }))}>
                  <span style={{ fontSize: 22 }}>✅</span> हाँ, BPL कार्ड है
                </OptionCard>
                <OptionCard selected={!profile.has_bpl} onClick={() => setProfile((p) => ({ ...p, has_bpl: false }))}>
                  <span style={{ fontSize: 22 }}>❌</span> नहीं है
                </OptionCard>
              </div>
              {!profile.has_bpl && (
                <>
                  <p style={{ fontSize: 15, fontWeight: 700, color: "var(--navy)", marginBottom: "var(--s3)" }}>
                    आपके परिवार की सालाना आय:
                  </p>
                  <div style={{ display: "flex", flexDirection: "column", gap: "var(--s2)" }}>
                    {INCOME_RANGES.map(({ label, value }) => (
                      <OptionCard key={value} selected={profile.income === value}
                        onClick={() => setProfile((p) => ({ ...p, income: value }))}>
                        {label}
                      </OptionCard>
                    ))}
                    <OptionCard selected={profile.income === 0 && !profile.has_bpl}
                      onClick={() => setProfile((p) => ({ ...p, income: 0 }))}>
                      मुझे नहीं पता / बताना नहीं चाहता
                    </OptionCard>
                  </div>
                </>
              )}
            </>
          )}

          {/* Step 6: Residence */}
          {step === 6 && (
            <>
              <p style={qLabel}>आप कहाँ रहते हैं?</p>
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--s3)" }}>
                {[
                  { value: "rural", label: "ग्रामीण क्षेत्र (गाँव)", icon: "🌾" },
                  { value: "urban", label: "शहरी क्षेत्र (शहर)", icon: "🏙️" },
                ].map(({ value, label, icon }) => (
                  <OptionCard key={value} selected={profile.residence === value}
                    onClick={() => setProfile((p) => ({ ...p, residence: value }))}>
                    <span style={{ fontSize: 22 }}>{icon}</span>
                    {label}
                  </OptionCard>
                ))}
              </div>
            </>
          )}

          {/* Step 7: Review */}
          {step === 7 && (
            <>
              <p style={qLabel}>आपकी जानकारी की समीक्षा करें</p>
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--s2)", marginBottom: "var(--s5)" }}>
                {[
                  { label: "राज्य",  value: profile.state || "—" },
                  { label: "उम्र",   value: profile.age ? `${profile.age} साल` : "—" },
                  { label: "लिंग",   value: profile.gender === "female" ? "महिला" : profile.gender === "male" ? "पुरुष" : profile.gender || "—" },
                  { label: "जाति",   value: profile.caste || "—" },
                  { label: "BPL",    value: profile.has_bpl ? "हाँ" : "नहीं" },
                  { label: "आय",     value: profile.income > 0 ? `₹${profile.income.toLocaleString("hi-IN")} / साल` : "बताया नहीं" },
                  { label: "निवास",  value: profile.residence === "rural" ? "ग्रामीण" : profile.residence === "urban" ? "शहरी" : "—" },
                ].map(({ label, value }) => (
                  <div key={label} style={{
                    display: "flex", justifyContent: "space-between",
                    padding: "10px 0", borderBottom: "1px solid rgba(11,31,77,.06)",
                  }}>
                    <span style={{ fontSize: 14, color: "var(--ink-2)" }}>{label}</span>
                    <span style={{ fontSize: 14, fontWeight: 700, color: "var(--navy)" }}>{value}</span>
                  </div>
                ))}
              </div>
              <p style={{ fontSize: 13, color: "var(--ink-3)" }}>
                जानकारी बदलनी है? ← वापस जाएं
              </p>
            </>
          )}

          {/* Navigation */}
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: "var(--s6)", alignItems: "center" }}>
            <button onClick={back} style={{
              background: "none", border: "none", cursor: "pointer",
              fontSize: 15, color: "var(--ink-2)", fontWeight: 600, padding: "10px 0",
            }}>
              ← वापस
            </button>
            <button
              onClick={isLastStep ? fetchResults : next}
              style={{
                padding: "14px 32px", borderRadius: 12, fontSize: 16, fontWeight: 800,
                background: "var(--saffron)", color: "var(--navy)", border: "none", cursor: "pointer",
              }}
            >
              {isLastStep ? "🔍 योजनाएं खोजें" : "अगला →"}
            </button>
          </div>
        </div>

        {/* Skip option */}
        {step < TOTAL_STEPS && (
          <p style={{ textAlign: "center", marginTop: "var(--s4)", fontSize: 13, color: "var(--ink-3)" }}>
            <button onClick={next} style={{
              background: "none", border: "none", cursor: "pointer",
              textDecoration: "underline", color: "var(--ink-3)", fontSize: 13,
            }}>
              यह सवाल छोड़ें →
            </button>
          </p>
        )}
      </div>
    </div>
  );
}
