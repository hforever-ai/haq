import type { ReactNode } from "react";

export type FlowTheme = "action" | "process" | "success";

export interface FlowStep {
  theme: FlowTheme;
  icon: ReactNode;
  title: string;
  subnote?: string;
}

interface Props {
  steps: FlowStep[];
}

const ICON_CHECK = (
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
    <path d="M7 14l5 5 9-9" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);
const ICON_DOCS = (
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
    <rect x="7" y="5" width="14" height="18" rx="2" stroke="#fff" strokeWidth="2" />
    <path d="M11 11h6M11 15h4" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" />
  </svg>
);
const ICON_APPLY = (
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
    <path d="M6 14h16M16 8l6 6-6 6" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);
const ICON_TRACK = (
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
    <circle cx="14" cy="14" r="8" stroke="#fff" strokeWidth="2" />
    <path d="M14 10v5l3 2" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" />
  </svg>
);

export const PRESET_ICONS = { check: ICON_CHECK, docs: ICON_DOCS, apply: ICON_APPLY, track: ICON_TRACK };

export function applySteps(opts: { applyUrl?: string; mandatoryDocNames?: string[] }): FlowStep[] {
  const { applyUrl, mandatoryDocNames = [] } = opts;
  const docNote = mandatoryDocNames.length > 0
    ? `${mandatoryDocNames.slice(0, 3).join(", ")}${mandatoryDocNames.length > 3 ? " आदि" : ""} तैयार रखें`
    : "आधार, आय प्रमाण, बैंक पासबुक तैयार रखें";
  return [
    { theme: "action",  icon: ICON_CHECK, title: "पात्रता जाँचें",     subnote: "ऊपर दी गई शर्तें पढ़ें और सुनिश्चित करें कि आप योग्य हैं" },
    { theme: "process", icon: ICON_DOCS,  title: "दस्तावेज़ तैयार करें", subnote: docNote },
    { theme: "process", icon: ICON_APPLY, title: applyUrl ? "ऑनलाइन आवेदन करें" : "CSC/कार्यालय जाएं",
      subnote: applyUrl ? "आधिकारिक पोर्टल पर जाएं और फॉर्म भरें" : "नज़दीकी CSC सेंटर या सरकारी कार्यालय में जाएं" },
    { theme: "success", icon: ICON_TRACK, title: "आवेदन ट्रैक करें",    subnote: "आवेदन संख्या नोट करें और समय-समय पर स्थिति जाँचें" },
  ];
}

export default function SchemeFlowDiagram({ steps }: Props) {
  return (
    <div className="flow-container" role="list" aria-label="आवेदन प्रक्रिया">
      <ol className="flow-list">
        {steps.map((step, i) => (
          <li key={i} className="flow-step" role="listitem">
            <div className="step-stamp-wrapper">
              <div className={`step-stamp theme-${step.theme}`}>
                {step.icon}
              </div>
              <span className="step-number">{i + 1}</span>
            </div>
            <div className="step-content">
              <p className="step-title">{step.title}</p>
              {step.subnote && <p className="step-subnote">{step.subnote}</p>}
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
