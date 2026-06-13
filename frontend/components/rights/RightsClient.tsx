"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import { Suspense } from "react";

function RightsSearchInner({ lang, initialQ, activeCategory }: {
  lang: string;
  initialQ: string;
  activeCategory: string;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [q, setQ] = useState(initialQ);

  useEffect(() => {
    setQ(searchParams.get("q") ?? "");
  }, [searchParams]);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const params = new URLSearchParams(searchParams.toString());
    if (q.trim()) params.set("q", q.trim());
    else params.delete("q");
    router.push(`${pathname}?${params.toString()}`);
  }

  return (
    <form onSubmit={submit} style={{ marginBottom: "var(--s5)" }}>
      <div className="search-bar" style={{ maxWidth: 480 }}>
        <input
          type="search"
          value={q}
          onChange={e => setQ(e.target.value)}
          placeholder="अधिकार खोजें... (जैसे: दहेज, पेंशन, FIR)"
          aria-label="Search rights"
        />
        <button type="submit" aria-label="Search">
          <svg width="14" height="14" fill="none" viewBox="0 0 14 14">
            <circle cx="6" cy="6" r="4.5" stroke="currentColor" strokeWidth="1.5" />
            <path d="M9 9l3.5 3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>
      </div>
    </form>
  );
}

export default function RightsClient(props: { lang: string; initialQ: string; activeCategory: string }) {
  return (
    <Suspense fallback={<div style={{ height: 52, marginBottom: "var(--s5)" }} />}>
      <RightsSearchInner {...props} />
    </Suspense>
  );
}
