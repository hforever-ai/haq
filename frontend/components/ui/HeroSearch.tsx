"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

interface Props {
  lang: string;
  placeholder: string;
}

export default function HeroSearch({ lang, placeholder }: Props) {
  const [q, setQ] = useState("");
  const router = useRouter();

  function handleSearch() {
    if (q.trim()) {
      router.push(`/${lang}/yojana?q=${encodeURIComponent(q.trim())}`);
    }
  }

  return (
    <div
      className="search-bar"
      style={{
        maxWidth: 540,
        marginBottom: "var(--s8)",
        background: "rgba(255,255,255,.08)",
        borderColor: "rgba(255,255,255,.12)",
      }}
      role="search"
    >
      <input
        type="search"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSearch()}
        placeholder={placeholder}
        aria-label={placeholder}
        style={{ color: "#fff", height: 44 }}
      />
      <button
        onClick={handleSearch}
        aria-label="Search"
        style={{ padding: "0 var(--s4)", color: "rgba(255,255,255,.6)", fontSize: 16 }}
      >
        <svg width="16" height="16" fill="none" viewBox="0 0 16 16" aria-hidden="true">
          <circle cx="6.5" cy="6.5" r="5" stroke="currentColor" strokeWidth="1.5" />
          <path d="M10 10l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      </button>
    </div>
  );
}
