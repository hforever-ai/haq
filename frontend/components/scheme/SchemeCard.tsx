import Link from "next/link";
import type { Scheme } from "@/lib/api";

interface Props {
  scheme: Scheme;
  lang: string;
  t: (key: string) => string;
}

export default function SchemeCard({ scheme: s, lang, t }: Props) {
  const desc = (s.description ?? "").slice(0, 160);

  return (
    <article className="scheme-card">
      <div className="scheme-card-top">
        <span className={`badge ${s.level === "Central" ? "badge-central" : "badge-state"}`}>
          {s.level === "Central" ? t("general.central_scheme") : t("general.state_scheme")}
        </span>
        {s.state && s.state !== "All" && (
          <span className="badge badge-muted" style={{ fontSize: 10 }}>{s.state}</span>
        )}
      </div>

      <h3>{s.name}</h3>

      <p className="desc">
        {desc}
        {(s.description ?? "").length > 160 ? "…" : ""}
      </p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
        {(s.beneficiary_type ?? []).slice(0, 2).map((bt) => (
          <span key={bt} className="badge badge-navy" style={{ fontSize: 10 }}>
            {t(`cat.${bt}`)}
          </span>
        ))}
      </div>

      <div className="scheme-card-footer">
        <Link href={`/${lang}/yojana/s/${s.slug}`} className="btn btn-primary btn-sm">
          {t("scheme.view")}
        </Link>
        {s.apply_url && (
          <a
            href={s.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-ghost btn-sm"
          >
            {t("general.official_site")}
            <svg width="10" height="10" fill="none" viewBox="0 0 10 10" aria-hidden="true">
              <path d="M1.5 8.5l7-7M8.5 1.5H3.5M8.5 1.5v5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
            </svg>
          </a>
        )}
      </div>
    </article>
  );
}
