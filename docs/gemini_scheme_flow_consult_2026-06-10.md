Here is the complete, production-ready UI/UX specification and CSS implementation for the **Scheme Explainer Flow Diagram** and the **"Explain This Scheme" AI Feature** for *Aarambha Haq*.

---

### 1. Flow Diagram Component Design

To cater to semi-literate and low-digital-literacy users, the design relies on **high-contrast visual anchors, physical metaphors (stamps, bank passes, identity cards), and minimal text.**

```
[DESKTOP HORIZONTAL FLOW]
 (01) Farmer       ───[→]─── (02) Aadhaar      ───[→]─── (03) ₹2,000      ───[→]─── (04) 3 Times
  Registers                   Verified                    Deposited                 A Year
  [Icon: Tractor]             [Icon: ID Card]             [Icon: Bank/Coin]         [Icon: Calendar]
  (Sub: Online/CSC)           (Sub: Auto-check)           (Sub: Direct to Bank)     (Sub: Every 4 months)

[MOBILE VERTICAL FLOW]
 (01) Farmer Registers
      [Icon: Tractor]
      │
     [↓]
 (02) Aadhaar Verified
      [Icon: ID Card]
      │
     [↓]
 (03) ₹2,000 Deposited
      [Icon: Bank/Coin]
```

#### Visual Style & Layout
*   **Mobile (Default):** Vertical layout. Steps stack sequentially downwards. This matches natural vertical scrolling on low-end mobile devices and prevents text truncation in Indian languages.
*   **Desktop (Min-width: 768px):** Horizontal layout. Steps flow from left-to-right (or right-to-left for Urdu).
*   **Maximum Steps:** Hard limit of **4 steps**. If a scheme has more steps, group them (e.g., combine "Apply Online" and "Upload Photo" into "1. Register & Upload").

#### Node Design
*   **The Anchor Circle (The "Stamp"):** A `56px` circle (`--s14`) with a high-contrast background. It contains a highly recognizable, simplified flat icon.
*   **Step Number Badge:** A small, high-contrast pill overlapping the top-right of the circle (e.g., "01", "02") to establish clear reading order without relying on text.
*   **Label & Sub-note:** 
    *   **Primary Label:** Bold, 16px (`--s4` equivalent), maximum 3 words.
    *   **Sub-note:** 12px, muted color, maximum 5 words (e.g., "Takes 15 days", "Free of cost").

#### Arrow/Connector Style
*   **Mobile:** A thick vertical line (`4px`) connecting the bottom of one circle to the top of the next. An animated down-arrow chevron pulses gently to indicate forward progress.
*   **Desktop:** A thick horizontal line running behind the nodes, with an arrowhead centered between nodes.
*   **Animation:** A subtle CSS keyframe animation mimicking a "flowing liquid" or "moving dash" from Step $N$ to Step $N+1$ to represent progression.

#### Color Coding (Using Brand Tokens)
To prevent cognitive overload, colors represent **states of action**, not just decoration:

| Step Type | Brand Color Token | Hex | Psychological Association |
| :--- | :--- | :--- | :--- |
| **Action / Input** (User's Job) | `--navy` (Deep Blue) | `#0B1F4D` | Authority, trust, action required. |
| **Verification / Process** (Govt's Job) | `--saffron` (Saffron) | `#FF9933` | Active processing, attention, warmth. |
| **Success / Payoff** (The Benefit) | `--green` (Green) | `#138808` | Growth, relief, money received, success. |

---

### 2. SVG vs. HTML/CSS Approach

**Recommended Approach: Hybrid HTML/CSS with Inline SVG Icons.**

#### Why Hybrid over Pure SVG?
*   **Multilingual Text Rendering (11 Languages, including RTL Urdu):** SVG text rendering (`<text>`) is notoriously fragile. It lacks robust automatic line-wrapping, breaks easily when switching from LTR (Hindi/English) to RTL (Urdu), and has poor accessibility (screen reader support).
*   **Next.js Server-Side Rendering (RSC):** HTML/CSS components render instantly on the server with zero layout shift (CLS).
*   **Responsiveness:** Fluid flexbox/grid layouts are significantly easier to manage across low-end mobile viewports ($320\text{px}$ to $400\text{px}$) than responsive SVG viewboxes.

#### Implementation Strategy
*   Use standard semantic HTML elements (`<ol>`, `<li>`, `<section>`).
*   Use CSS Flexbox. Change `flex-direction` from `column` (mobile) to `row` (desktop).
*   Use CSS pseudo-elements (`::after`) for the connecting lines.
*   Use inline SVGs **only** for the icons inside the step circles.

---

### 3. Scheme Categories Flow Patterns

To make different types of welfare recognizable at a glance, the node shapes, colors, and iconography adapt to the scheme's core category:

```
[DIRECT BENEFIT TRANSFER (DBT)]
(Navy: User Action) ───► (Saffron: Verification) ───► (Green: Success/Money)
[Icon: Mobile/Form]      [Icon: Aadhaar Card]         [Icon: Hand receiving coin]

[SERVICE SCHEME]
(Navy: User Action) ───► (Saffron: Govt Approval) ───► (Green: Service Access)
[Icon: Apply Form]       [Icon: Approved Stamp]       [Icon: Smart Card / QR]

[INFRASTRUCTURE SCHEME]
(Navy: Apply)       ───► (Saffron: Geo-Tag Survey) ───► (Green: Handover/Key)
[Icon: Document]         [Icon: Phone Camera]         [Icon: House with Key]

[EMPLOYMENT SCHEME]
(Navy: Register)    ───► (Saffron: Job Card Issued) ───► (Green: Daily Wage Paid)
[Icon: ID Card]          [Icon: Spanner/Tools]        [Icon: Bank Passbook]
```

---

### 4. Data Structure

This TypeScript definition represents the schema stored in the database (PostgreSQL/Prisma) and served via the Next.js App Router API to render the component dynamically:

```typescript
export type StepColorTheme = 'action' | 'process' | 'success';

export type FlowStep = {
  id: string;
  stepNumber: number;
  /** High-contrast icon identifier (maps to a local SVG catalog) */
  iconId: 'tractor' | 'id-card' | 'bank-coin' | 'calendar' | 'form' | 'stamp' | 'house' | 'tools' | 'passbook';
  /** Multilingual text dictionary for 11 languages */
  title: {
    en: string;
    hi: string; // Hindi
    mr: string; // Marathi
    ta: string; // Tamil
    te: string; // Telugu
    ur: string; // Urdu (RTL)
    bn: string; // Bengali
    gu: string; // Gujarati
    kn: string; // Kannada
    ml: string; // Malayalam
    pa: string; // Punjabi
  };
  subNote?: {
    en: string;
    hi: string;
    [key: string]: string;
  };
  theme: StepColorTheme;
};

export type SchemeFlow = {
  schemeId: string;
  category: 'dbt' | 'service' | 'infrastructure' | 'employment';
  steps: FlowStep[]; // Maximum length: 4
};
```

---

### 5. Inline "Explain This Scheme" AI Feature

When a user clicks the **"समझाएं (Explain)"** button (prominently styled with an AI/sparkle icon), a highly responsive panel transitions into view.

*   **Mobile:** Bottom Sheet Drawer sliding up from the bottom, occupying 85% of viewport height. It can be dragged down to dismiss.
*   **Desktop:** Slide-out Sidebar Panel emerging from the right side, occupying 450px of width.

#### UI Components Inside the Panel
1.  **Audio Player (Voice-Over):** A prominent "Listen" button at the top that reads the simplified text aloud in the selected language (crucial for semi-literate users).
2.  **Conversational Summary:** 2 sentences explaining the scheme in ultra-simple terms (e.g., *"This scheme gives ₹6,000 every year to farmers who own small lands. The money goes directly to your bank account."*).
3.  **Mini Flow Diagram:** A condensed version of our flow diagram.
4.  **Quick Eligibility Check:** 3 simple "Yes/No" interactive toggle cards (e.g., "Do you own farming land?", "Is your Aadhaar linked to your phone?").

---

### 6. Complete Scheme Detail Page Layout

```
+-------------------------------------------------------------+
|                     HEADER (Brand & Lang)                   |
+-------------------------------------------------------------+
|                                                             |
|  [ABOVE THE FOLD - FIRST 500px ON MOBILE]                   |
|  - Scheme Title (e.g., PM Kisan Yojana)                     |
|  - One-sentence summary (Big, readable font)                |
|  - Primary Action: [Apply Now] (Navy)                       |
|  - Secondary Action: [समझाएं / Listen to AI] (Saffron Glow) |
|                                                             |
+-------------------------------------------------------------+
|                                                             |
|  [FOLD 1: ELIGIBILITY CHECKLIST]                            |
|  - Green checkmarks / Red crosses                           |
|  - Interactive "Am I Eligible?" micro-calculator            |
|                                                             |
+-------------------------------------------------------------+
|                                                             |
|  [FOLD 2: BENEFITS (WHAT YOU GET)]                          |
|  - Massive text showing monetary value (e.g., ₹6,000 / Yr)  |
|  - Visual representation of the benefit                     |
|                                                             |
+-------------------------------------------------------------+
|                                                             |
|  [FOLD 3: FLOW DIAGRAM (HOW TO APPLY)]                      |
|  - **OUR COMPONENT PLACEMENT**                             |
|  - Serves as the logical bridge between "What is this?"     |
|    and "What do I need to prepare?"                         |
|                                                             |
+-------------------------------------------------------------+
|                                                             |
|  [FOLD 4: DOCUMENTS NEEDED]                                 |
|  - Visual cards of physical documents (Aadhaar, Passbook)   |
|                                                             |
+-------------------------------------------------------------+
|                                                             |
|  [FOLD 5: FAQ & HELP]                                       |
|  - Accordions with simple answers                           |
|                                                             |
+-------------------------------------------------------------+
```

---

### 7. Production-Ready CSS

Save this as your custom CSS file. It uses your design tokens (`--saffron`, `--navy`, `--green`, and spacing scales `--s1` to `--s16`).

```css
/* ==========================================================================
   AARAMBHA HAQ DESIGN SYSTEM TOKENS (Reference)
   ========================================================================== */
:root {
  --saffron: #FF9933;
  --navy: #0B1F4D;
  --navy-light: #1E3A8A;
  --green: #138808;
  --white: #FFFFFF;
  --gray-light: #F3F4F6;
  --gray-muted: #6B7280;
  --border-color: #E5E7EB;
  
  /* Spacing Grid (4px base) */
  --s1: 4px;
  --s2: 8px;
  --s3: 12px;
  --s4: 16px;
  --s6: 24px;
  --s8: 32px;
  --s12: 48px;
  --s14: 56px;
  --s16: 64px;

  /* Border Radii */
  --r-sm: 4px;
  --r-md: 8px;
  --r-lg: 16px;
  --r-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(11, 31, 77, 0.1), 0 2px 4px -1px rgba(11, 31, 77, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* ==========================================================================
   1. FLOW DIAGRAM COMPONENT
   ========================================================================== */
.flow-container {
  padding: var(--s6) 0;
  width: 100%;
}

.flow-list {
  display: flex;
  flex-direction: column;
  list-style: none;
  padding: 0;
  margin: 0;
  position: relative;
}

/* Vertical line for mobile */
.flow-list::before {
  content: '';
  position: absolute;
  left: 28px; /* Half of circle width (56px / 2) */
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--border-color);
  z-index: 1;
}

.flow-step {
  display: flex;
  align-items: flex-start;
  position: relative;
  margin-bottom: var(--s8);
  z-index: 2;
}

.flow-step:last-child {
  margin-bottom: 0;
}

/* Step Stamp/Circle Container */
.step-stamp-wrapper {
  position: relative;
  flex-shrink: 0;
  margin-right: var(--s4);
}

.step-stamp {
  width: var(--s14);
  height: var(--s14);
  border-radius: var(--r-full);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
  transition: transform 0.2s ease;
}

.step-stamp svg {
  width: 28px;
  height: 28px;
  fill: var(--white);
}

/* Color Themes */
.step-stamp.theme-action {
  background-color: var(--navy);
}

.step-stamp.theme-process {
  background-color: var(--saffron);
}

.step-stamp.theme-success {
  background-color: var(--green);
}

/* Step Number Badge */
.step-number {
  position: absolute;
  top: -4px;
  right: -4px;
  background-color: var(--white);
  color: var(--navy);
  font-size: 10px;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: var(--r-full);
  border: 2px solid var(--navy);
  box-shadow: var(--shadow-sm);
}

.step-stamp.theme-process .step-number {
  border-color: var(--saffron);
  color: var(--saffron);
}

.step-stamp.theme-success .step-number {
  border-color: var(--green);
  color: var(--green);
}

/* Text Block */
.step-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-top: var(--s2);
}

.step-title {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 16px;
  font-weight: 700;
  color: var(--navy);
  margin: 0 0 var(--s1) 0;
  line-height: 1.3;
}

.step-subnote {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 12px;
  color: var(--gray-muted);
  margin: 0;
}

/* RTL (Urdu) Support */
[dir="rtl"] .flow-list::before {
  left: auto;
  right: 28px;
}

[dir="rtl"] .step-stamp-wrapper {
  margin-right: 0;
  margin-left: var(--s4);
}

[dir="rtl"] .step-number {
  right: auto;
  left: -4px;
}

/* Desktop Horizontal Layout overrides */
@media (min-width: 768px) {
  .flow-list {
    flex-direction: row;
    justify-content: space-between;
  }

  .flow-list::before {
    left: 0;
    right: 0;
    top: 28px; /* Center horizontally relative to circles */
    width: 100%;
    height: 4px;
  }

  .flow-step {
    flex-direction: column;
    align-items: center;
    text-align: center;
    flex: 1;
    margin-bottom: 0;
  }

  .step-stamp-wrapper {
    margin-right: 0;
    margin-bottom: var(--s3);
  }

  .step-content {
    padding-top: 0;
    align-items: center;
  }
}

/* ==========================================================================
   2. EXPLAINER SIDE PANEL & BOTTOM DRAWER
   ========================================================================== */
.explainer-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(11, 31, 77, 0.5); /* Navy with opacity */
  backdrop-filter: blur(4px);
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s ease, visibility 0.3s ease;
}

.explainer-backdrop.is-open {
  opacity: 1;
  visibility: visible;
}

/* Bottom Sheet Drawer (Mobile Default) */
.scheme-explainer-drawer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 85vh;
  background-color: var(--white);
  border-top-left-radius: var(--r-lg);
  border-top-right-radius: var(--r-lg);
  box-shadow: 0 -10px 25px rgba(0, 0, 0, 0.15);
  z-index: 1001;
  transform: translateY(100%);
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  flex-direction: column;
}

.scheme-explainer-drawer.is-open {
  transform: translateY(0);
}

/* Drag Handle for Mobile */
.drawer-handle {
  width: 40px;
  height: 5px;
  background-color: var(--border-color);
  border-radius: var(--r-full);
  margin: var(--s3) auto;
  flex-shrink: 0;
}

/* Desktop Side Panel overrides */
@media (min-width: 768px) {
  .scheme-explainer-panel {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: auto;
    width: 460px;
    height: 100vh;
    border-top-left-radius: var(--r-lg);
    border-top-right-radius: 0;
    border-bottom-left-radius: var(--r-lg);
    transform: translateX(100%);
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .scheme-explainer-panel.is-open {
    transform: translateX(0);
  }

  .drawer-handle {
    display: none;
  }
}

/* Internal Layout of the Panel */
.panel-header {
  padding: var(--s4) var(--s6);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-title {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 20px;
  font-weight: 800;
  color: var(--navy);
  margin: 0;
}

.panel-close-btn {
  background: none;
  border: none;
  padding: var(--s2);
  cursor: pointer;
  border-radius: var(--r-full);
}

.panel-close-btn:hover {
  background-color: var(--gray-light);
}

.panel-body {
  padding: var(--s6);
  overflow-y: auto;
  flex-grow: 1;
}

/* Conversational AI Block */
.ai-summary-card {
  background-color: var(--gray-light);
  border-left: 4px solid var(--saffron);
  padding: var(--s4);
  border-radius: var(--r-md);
  margin-bottom: var(--s6);
}

.ai-summary-text {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 15px;
  line-height: 1.6;
  color: var(--navy);
  margin: 0;
}

/* Quick Eligibility Interactive Widget */
.eligibility-widget {
  background-color: var(--white);
  border: 1px solid var(--border-color);
  border-radius: var(--r-lg);
  padding: var(--s4);
  margin-top: var(--s6);
}

.widget-title {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 16px;
  font-weight: 700;
  color: var(--navy);
  margin-bottom: var(--s4);
}

.checklist-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--s3) 0;
  border-bottom: 1px solid var(--gray-light);
}

.checklist-item:last-child {
  border-bottom: none;
}

.checklist-label {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 14px;
  color: var(--navy);
}

/* High contrast toggle switches */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 52px;
  height: 28px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--gray-muted);
  transition: .3s;
  border-radius: var(--r-full);
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 4px;
  bottom: 4px;
  background-color: var(--white);
  transition: .3s;
  border-radius: var(--r-full);
}

input:checked + .toggle-slider {
  background-color: var(--green);
}

input:checked + .toggle-slider:before {
  transform: translateX(24px);
}
```

---

### 8. Next.js 15 React Component Pseudocode

This clean component handles state, supports translation triggers, and uses server-friendly semantic HTML.

```tsx
// components/SchemeFlowDiagram.tsx
import React from 'react';
import { FlowStep } from '@/types';

interface SchemeFlowDiagramProps {
  steps: FlowStep[];
  locale: string;
}

export default function SchemeFlowDiagram({ steps, locale }: SchemeFlowDiagramProps) {
  return (
    <section className="flow-container" aria-label="Scheme application process">
      <ol className="flow-list">
        {steps.map((step) => {
          // Fallback handling for localization string selection
          const titleText = step.title[locale as keyof typeof step.title] || step.title['en'];
          const subNoteText = step.subNote ? (step.subNote[locale] || step.subNote['en']) : null;

          return (
            <li key={step.id} className="flow-step">
              <div className="step-stamp-wrapper">
                <div className={`step-stamp theme-${step.theme}`}>
                  {/* Inline SVGs mapping directly to the step.iconId */}
                  <DynamicIcon iconId={step.iconId} />
                  <span className="step-number" aria-hidden="true">
                    {String(step.stepNumber).padStart(2, '0')}
                  </span>
                </div>
              </div>
              <div className="step-content">
                <h3 className="step-title">{titleText}</h3>
                {subNoteText && <p className="step-subnote">{subNoteText}</p>}
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

// Helper component to render clean, high-contrast flat SVGs
function DynamicIcon({ iconId }: { iconId: string }) {
  switch (iconId) {
    case 'tractor':
      return <svg viewBox="0 0 24 24"><path d="M19 16c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm-14 0c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0-3h14v-2H5v2zm14-5H5v2h14V8z"/></svg>;
    case 'id-card':
      return <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm6 12H6v-1.5c0-2 4-3.1 6-3.1s6 1.1 6 3.1V18z"/></svg>;
    case 'bank-coin':
      return <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 13h-2v-2h2v2zm0-4h-2V7h2v4z"/></svg>;
    default:
      return <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" /></svg>;
  }
}
```