"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname, useSearchParams } from "next/navigation";

interface Props {
  lang: string;
  currentCategory: string;
  currentLevel: string;
}

const LEVELS = [
  { value: "", label: "सभी" },
  { value: "Central", label: "केंद्रीय" },
  { value: "State", label: "राज्य" },
];

const INDIAN_STATES = [
  "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh",
  "Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka",
  "Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram",
  "Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana",
  "Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Delhi",
];

export default function BrowseFilters({ lang, currentCategory, currentLevel }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Controlled input — syncs with URL (back/forward navigation)
  const [searchValue, setSearchValue] = useState(searchParams.get("q") ?? "");
  useEffect(() => {
    setSearchValue(searchParams.get("q") ?? "");
  }, [searchParams]);

  function setFilter(key: string, value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value) params.set(key, value);
    else params.delete(key);
    params.delete("page");
    router.push(`${pathname}?${params.toString()}`);
  }

  function handleSearch(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setFilter("q", searchValue.trim());
  }

  return (
    <aside style={{ display: "flex", flexDirection: "column", gap: "var(--s4)" }}>

      {/* Search */}
      <div className="sidebar-card">
        <h4>खोजें</h4>
        <form onSubmit={handleSearch} style={{ marginTop: "var(--s2)" }}>
          <div className="search-bar" style={{ marginBottom: "var(--s2)" }}>
            <input
              name="q"
              type="search"
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              placeholder="योजना खोजें..."
              style={{ height: 36 }}
            />
            <button type="submit" style={{ padding: "0 var(--s3)", color: "var(--ink-3)" }}>
              <svg width="14" height="14" fill="none" viewBox="0 0 14 14">
                <circle cx="6" cy="6" r="4.5" stroke="currentColor" strokeWidth="1.5" />
                <path d="M9 9l3.5 3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </button>
          </div>
        </form>
      </div>

      {/* Level filter */}
      <div className="sidebar-card">
        <h4>स्तर</h4>
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--s2)", marginTop: "var(--s2)" }}>
          {LEVELS.map((l) => (
            <button
              key={l.value}
              onClick={() => setFilter("level", l.value)}
              style={{
                padding: "6px var(--s3)", borderRadius: "var(--r-sm)", textAlign: "left",
                border: "1.5px solid",
                borderColor: currentLevel === l.value ? "var(--saffron)" : "var(--line)",
                background: currentLevel === l.value ? "var(--saffron-tint)" : "transparent",
                color: currentLevel === l.value ? "var(--saffron-deep)" : "var(--ink-2)",
                fontWeight: currentLevel === l.value ? 700 : 400,
                fontSize: 13, cursor: "pointer",
              }}
            >
              {l.label}
            </button>
          ))}
        </div>
      </div>

      {/* State filter */}
      <div className="sidebar-card">
        <h4>राज्य</h4>
        <select
          onChange={(e) => setFilter("state", e.target.value)}
          defaultValue={searchParams.get("state") ?? ""}
          style={{
            width: "100%", padding: "6px var(--s3)", borderRadius: "var(--r-sm)",
            border: "1.5px solid var(--line)", fontSize: 13, color: "var(--ink)",
            background: "var(--surface)", marginTop: "var(--s2)",
          }}
        >
          <option value="">सभी राज्य</option>
          {INDIAN_STATES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {/* Clear filters */}
      {(currentCategory || currentLevel || searchParams.get("state") || searchParams.get("q")) && (
        <button
          onClick={() => router.push(`/${lang}/yojana`)}
          className="btn btn-ghost btn-sm btn-block"
        >
          सभी फ़िल्टर हटाएं
        </button>
      )}
    </aside>
  );
}
