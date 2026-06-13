import path from "path";
import fs from "fs";

const I18N_DIR = path.join(process.cwd(), "public", "i18n");

export interface LangMeta {
  code: string;
  name: string;
  native: string;
  rtl?: boolean;
}

let _langs: LangMeta[] | null = null;
export function getLanguages(): LangMeta[] {
  if (_langs) return _langs;
  _langs = JSON.parse(
    fs.readFileSync(path.join(I18N_DIR, "_languages.json"), "utf-8")
  );
  return _langs!;
}

export const VALID_LANGS = new Set(getLanguages().map((l) => l.code));
export const RTL_LANGS = new Set(["ur", "ks", "sd"]);

const _cache: Record<string, Record<string, string>> = {};
export function getTranslations(lang: string): Record<string, string> {
  const code = VALID_LANGS.has(lang) ? lang : "hi";
  if (_cache[code]) return _cache[code];
  try {
    _cache[code] = JSON.parse(
      fs.readFileSync(path.join(I18N_DIR, `${code}.json`), "utf-8")
    );
  } catch {
    _cache[code] = JSON.parse(
      fs.readFileSync(path.join(I18N_DIR, "hi.json"), "utf-8")
    );
  }
  return _cache[code];
}

export function makeT(lang: string) {
  const tr = getTranslations(lang);
  return function t(key: string, vars?: Record<string, string | number>): string {
    let val = tr[key] ?? key;
    if (vars) {
      Object.entries(vars).forEach(([k, v]) => {
        val = val.replace(`{${k}}`, String(v));
      });
    }
    return val;
  };
}
