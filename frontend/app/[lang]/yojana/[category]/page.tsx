import { redirect } from "next/navigation";

// /[lang]/yojana/[category] → delegates to /[lang]/yojana?category=[category]
// This lets the browse page handle category filtering with URL params
export default async function CategoryPage({
  params,
}: {
  params: Promise<{ lang: string; category: string }>;
}) {
  const { lang, category } = await params;
  redirect(`/${lang}/yojana?category=${category}`);
}
