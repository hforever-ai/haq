import Link from "next/link";

interface LangMeta { code: string; name: string; native: string }

interface FooterProps {
  lang: string;
  languages: LangMeta[];
  translations: Record<string, string>;
}

function t(tr: Record<string, string>, key: string): string {
  return tr[key] ?? key;
}

const SCHEME_CATS = [
  { slug: "mahila",     key: "cat.women",      count: 381 },
  { slug: "student",    key: "cat.student",    count: 748 },
  { slug: "farmer",     key: "cat.farmer",     count: 400 },
  { slug: "employment", key: "cat.employment", count: 459 },
  { slug: "disability", key: "cat.disability", count: 289 },
  { slug: "pension",    key: "cat.pension",    count: 259 },
  { slug: "health",     key: "cat.health",     count: 184 },
  { slug: "housing",    key: "cat.housing",    count: 69  },
];

export default function Footer({ lang, languages, translations: tr }: FooterProps) {
  return (
    <footer className="footer" role="contentinfo">
      <div className="footer-top" aria-hidden="true" />
      <div className="wrap">
        <div className="footer-grid">

          <div className="footer-brand">
            <div className="f-name">Aarambha Haq</div>
            <p>{t(tr, "footer.tagline")}</p>
            <p style={{ marginTop: "var(--s3)", fontSize: 11, opacity: .5 }}>
              {t(tr, "footer.data_note")}
            </p>
            <p style={{ marginTop: "var(--s2)", fontSize: 11, opacity: .45 }}>
              {t(tr, "footer.free_note")}
            </p>
          </div>

          <div className="footer-col">
            <h5>{t(tr, "footer.links.schemes")}</h5>
            {SCHEME_CATS.map((c) => (
              <Link key={c.slug} href={`/${lang}/yojana/${c.slug}`}>
                {t(tr, c.key)}
              </Link>
            ))}
          </div>

          <div className="footer-col">
            <h5>{t(tr, "nav.about")}</h5>
            <Link href={`/${lang}/check`}>{t(tr, "nav.check_eligibility")}</Link>
            <Link href={`/${lang}/haq`}>{t(tr, "nav.your_rights")}</Link>
            <Link href={`/${lang}/yojana`}>{t(tr, "nav.all_schemes")}</Link>
            <Link href={`/${lang}/about`}>{t(tr, "nav.about")}</Link>
            <a href="https://www.myscheme.gov.in" target="_blank" rel="noopener noreferrer">
              MyScheme.gov.in
            </a>
          </div>

          <div className="footer-col">
            <h5>भाषा / Language</h5>
            <div className="footer-sitemap">
              {languages.map((l) => (
                <Link key={l.code} href={`/${l.code}/`}>{l.native}</Link>
              ))}
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <span>{t(tr, "footer.copyright")}</span>
          <span style={{ color: "rgba(255,255,255,.2)" }}>·</span>
          <a href="https://aarambhax.in" target="_blank" rel="noopener noreferrer"
             style={{ color: "rgba(255,255,255,.35)" }}>
            Aarambha AI Studio
          </a>
          <span style={{ color: "rgba(255,255,255,.2)" }}>·</span>
          <Link href={`/${lang}/about`} style={{ color: "rgba(255,255,255,.35)" }}>
            {t(tr, "nav.about")}
          </Link>
        </div>
      </div>
    </footer>
  );
}
