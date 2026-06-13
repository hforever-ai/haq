import { makeT } from "@/lib/i18n";

export default async function AboutPage({ params }: { params: Promise<{ lang: string }> }) {
  const { lang } = await params;
  const t = makeT(lang);
  return (
    <div className="wrap section" style={{ maxWidth: 720 }}>
      <h1>{t("nav.about")}</h1>
      <p style={{ marginTop: "var(--s4)", fontSize: 16, lineHeight: 1.75 }}>
        Aarambha Haq एक निःशुल्क सेवा है जो भारत के नागरिकों को सरकारी योजनाओं की जानकारी
        22 भारतीय भाषाओं में उपलब्ध कराती है। हमारा डेटा MyScheme.gov.in से लिया गया है।
      </p>

      <div style={{ display: "flex", gap: "var(--s5)", margin: "var(--s6) 0", flexWrap: "wrap" }}>
        {[
          { n: "2,754+", label: "सरकारी योजनाएं" },
          { n: "22",     label: "अनुसूचित भाषाएं" },
          { n: "15",     label: "लाभार्थी श्रेणियां" },
        ].map(({ n, label }) => (
          <div key={n} style={{
            background: "var(--surface)", border: "1px solid var(--line)",
            borderRadius: "var(--r-lg)", padding: "var(--s4) var(--s5)", textAlign: "center",
          }}>
            <div style={{ fontSize: 32, fontWeight: 900, color: "var(--saffron)", lineHeight: 1 }}>{n}</div>
            <div style={{ fontSize: 12, color: "var(--ink-3)", marginTop: 4 }}>{label}</div>
          </div>
        ))}
      </div>

      <div className="tips-box">
        <h4>Aarambha AI Studio के बारे में</h4>
        <ul>
          <li>Aarambha Haq, Aarambha AI Studio का एक निःशुल्क उत्पाद है।</li>
          <li>AI की मदद से भारत के नागरिकों तक सरकारी सेवाएं 22 भाषाओं में पहुँचाते हैं।</li>
          <li>डेटा स्रोत: MyScheme.gov.in (भारत सरकार)</li>
          <li>यह प्लेटफ़ॉर्म पूरी तरह निःशुल्क और विज्ञापन-मुक्त है।</li>
        </ul>
      </div>
    </div>
  );
}
