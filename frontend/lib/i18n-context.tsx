"use client";
import { createContext, useContext } from "react";

interface I18nCtx {
  lang: string;
  dir: "ltr" | "rtl";
  t: (key: string, vars?: Record<string, string | number>) => string;
  languages: { code: string; name: string; native: string }[];
}

const I18nContext = createContext<I18nCtx>({
  lang: "hi",
  dir: "ltr",
  t: (k) => k,
  languages: [],
});

export function I18nProvider({
  lang,
  dir,
  translations,
  languages,
  children,
}: {
  lang: string;
  dir: "ltr" | "rtl";
  translations: Record<string, string>;
  languages: { code: string; name: string; native: string }[];
  children: React.ReactNode;
}) {
  function t(key: string, vars?: Record<string, string | number>): string {
    let val = translations[key] ?? key;
    if (vars) {
      Object.entries(vars).forEach(([k, v]) => {
        val = val.replace(`{${k}}`, String(v));
      });
    }
    return val;
  }

  return (
    <I18nContext.Provider value={{ lang, dir, t, languages }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}
