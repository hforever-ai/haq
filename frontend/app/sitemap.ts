import type { MetadataRoute } from "next";

const BASE_URL = "https://haq.aarambhax.in";

const LANGS = [
  "hi","mr","ne","mai","sa","doi","kok",
  "bn","as","gu","pa","or",
  "ta","te","kn","ml",
  "ur","ks","sd","mni","brx","sat",
];

const STATES = [
  "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh",
  "Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka",
  "Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram",
  "Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana",
  "Tripura","Uttar Pradesh","Uttarakhand","West Bengal",
  "Andaman and Nicobar Islands","Chandigarh","Dadra and Nagar Haveli",
  "Daman and Diu","Delhi","Jammu and Kashmir","Ladakh","Lakshadweep","Puducherry",
];

const LIFE_EVENTS = [
  "farmer","student","pregnant","widow","disabled",
  "elderly","child","unemployed","minority","shg","entrepreneur","housing",
];

// Split 60K scheme URLs into two chunks (≤50K each)
export function generateSitemaps() {
  return [{ id: 0 }, { id: 1 }, { id: 2 }];
}

// Fetch all scheme slugs from FastAPI
async function fetchSlugs(): Promise<string[]> {
  const apiBase = process.env.API_BASE_URL ?? "http://localhost:8097";
  try {
    // Fetch all slugs in one call — FastAPI supports large size
    const res = await fetch(`${apiBase}/api/schemes?size=3000`, {
      next: { revalidate: 86400 },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.schemes as Array<{ slug: string }>).map((s) => s.slug);
  } catch {
    return [];
  }
}

export default async function sitemap({
  id,
}: {
  id: number;
}): Promise<MetadataRoute.Sitemap> {
  const now = new Date();

  // Chunk 0 — static pages (home, browse, check, state hubs, life events)
  if (id === 0) {
    const staticPages: MetadataRoute.Sitemap = [];

    for (const lang of LANGS) {
      staticPages.push(
        { url: `${BASE_URL}/${lang}/`,       lastModified: now, changeFrequency: "weekly", priority: 1.0 },
        { url: `${BASE_URL}/${lang}/yojana`, lastModified: now, changeFrequency: "daily",  priority: 0.9 },
        { url: `${BASE_URL}/${lang}/check`,  lastModified: now, changeFrequency: "monthly", priority: 0.9 },
        { url: `${BASE_URL}/${lang}/haq`,    lastModified: now, changeFrequency: "monthly", priority: 0.7 },
        { url: `${BASE_URL}/${lang}/about`,  lastModified: now, changeFrequency: "monthly", priority: 0.5 },
      );
      for (const state of STATES) {
        staticPages.push({
          url: `${BASE_URL}/${lang}/state/${encodeURIComponent(state.toLowerCase().replace(/ /g, "-"))}`,
          lastModified: now, changeFrequency: "weekly", priority: 0.8,
        });
      }
      for (const event of LIFE_EVENTS) {
        staticPages.push({
          url: `${BASE_URL}/${lang}/life/${event}`,
          lastModified: now, changeFrequency: "weekly", priority: 0.8,
        });
      }
    }
    return staticPages;
  }

  // Chunks 1 and 2 — scheme detail pages split across two chunks
  const slugs = await fetchSlugs();
  const half  = Math.ceil(slugs.length / 2);
  const chunk = id === 1 ? slugs.slice(0, half) : slugs.slice(half);

  const entries: MetadataRoute.Sitemap = [];
  for (const slug of chunk) {
    for (const lang of LANGS) {
      entries.push({
        url: `${BASE_URL}/${lang}/yojana/s/${slug}`,
        lastModified: now,
        changeFrequency: "monthly",
        priority: 0.7,
      });
    }
  }
  return entries;
}
