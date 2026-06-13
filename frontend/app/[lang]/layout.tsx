import { redirect } from "next/navigation";
import type { Metadata } from "next";
import {
  getLanguages,
  getTranslations,
  makeT,
  VALID_LANGS,
  RTL_LANGS,
} from "@/lib/i18n";
import { I18nProvider } from "@/lib/i18n-context";
import Nav from "@/components/layout/Nav";
import Footer from "@/components/layout/Footer";

interface Props {
  children: React.ReactNode;
  params: Promise<{ lang: string }>;
}

export async function generateStaticParams() {
  return getLanguages().map((l) => ({ lang: l.code }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { lang } = await params;
  const t = makeT(lang);
  return {
    title: {
      default: `${t("hero.headline")} — Aarambha Haq`,
      template: `%s — Aarambha Haq`,
    },
    description: t("hero.sub"),
    alternates: {
      languages: Object.fromEntries(
        getLanguages().map((l) => [
          l.code,
          `https://haq.aarambhax.in/${l.code}/`,
        ])
      ),
    },
  };
}

export default async function LangLayout({ children, params }: Props) {
  const { lang } = await params;
  if (!VALID_LANGS.has(lang)) redirect("/hi/");

  const languages = getLanguages();
  const translations = getTranslations(lang);
  const dir = (RTL_LANGS.has(lang) ? "rtl" : "ltr") as "ltr" | "rtl";
  const meta = languages.find((l) => l.code === lang)!;

  return (
    <I18nProvider lang={lang} dir={dir} translations={translations} languages={languages}>
      <Nav lang={lang} languages={languages} langNative={meta.native} translations={translations} />
      <main id="main-content" tabIndex={-1}>
        {children}
      </main>
      <Footer lang={lang} languages={languages} translations={translations} />
    </I18nProvider>
  );
}
