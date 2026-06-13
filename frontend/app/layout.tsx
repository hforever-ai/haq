import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Aarambha Haq — सरकारी योजना पात्रता जाँचें",
  description:
    "2,754+ सरकारी योजनाएं — महिला, किसान, छात्र, रोजगार। 22 भारतीय भाषाओं में। मुफ्त पात्रता जाँचें।",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;700;900&family=Noto+Sans:ital,wght@0,400;0,500;0,700;0,900;1,400&family=Noto+Nastaliq+Urdu:wght@400;700&family=Noto+Sans+Bengali:wght@400;700&family=Noto+Sans+Tamil:wght@400;700&family=Noto+Sans+Telugu:wght@400;700&family=Noto+Sans+Kannada:wght@400;700&family=Noto+Sans+Malayalam:wght@400;700&family=Noto+Sans+Gujarati:wght@400;700&family=Noto+Sans+Gurmukhi:wght@400;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
