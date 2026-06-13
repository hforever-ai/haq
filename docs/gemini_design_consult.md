Here's the complete product design for Aarambha Haq, envisioned for rural/semi-urban Hindi-speaking users on mobile-first devices.

---

## A. THEME.md

Aarambha Haq's theme prioritizes clarity, trust, and ease of use for its target audience. The design is clean, functional, and leverages India's national colors responsibly to build brand recognition and credibility.

### Color System

The color palette is derived from the brand tokens, extended with functional colors for states and feedback. Emphasis on high contrast for accessibility.

```css
:root {
  /* Brand Primary */
  --saffron: #FF9933; /* Accent, Primary CTA, Highlights */
  --green: #138808;   /* Accent, Success, Secondary CTA */
  --navy: #0B1F4D;    /* Primary Text (Headings), Navigation Background */

  /* Neutrals */
  --page: #F6F8FB;    /* Page Background */
  --ink: #16223A;     /* Body Text */
  --ink-2: #5B6678;   /* Secondary Text, Placeholder Text, Icons */
  --line: #E7EBF1;    /* Borders, Dividers, Separators */
  --white: #FFFFFF;   /* Card Background, Button Background */

  /* Functional */
  --error: #D83120;   /* Error states, Negative feedback */
  --success: var(--green); /* Success states, Positive feedback */
  --warning: #F0AD4E; /* Warning states */
  --info: #2196F3;    /* Informational messages */

  /* Gradients & Special */
  --tricolor-gradient: linear-gradient(to right, var(--saffron) 0%, var(--saffron) 33%, var(--white) 33%, var(--white) 66%, var(--green) 66%, var(--green) 100%);
}

/* Usage Rules: */
/* - Primary Text: --ink (Body), --navy (Headings, Main Nav) */
/* - Secondary Text: --ink-2 (Helper text, metadata) */
/* - Links: --saffron (Default), --navy (Hover) */
/* - Buttons: */
/*   - Primary: Background --saffron, Text --white */
/*   - Secondary: Background --green, Text --white */
/*   - Outline: Background --white, Border --saffron, Text --saffron */
/*   - Ghost: Background transparent, Text --saffron */
/* - Backgrounds: --page (Global), --white (Cards, Modals, Forms) */
/* - Borders: --line (Default), --error (Error input), --green (Success input) */
/* - Icons: --ink-2 (Default), --saffron (Active/Highlight) */
/* - Tricolor Strip: Applied as a border or background element in hero/nav. */
```

### Typography Scale

`Noto Sans Devanagari` for Hindi, `Inter` for English (used sparingly for technical terms or fallback). Sizes are optimized for mobile-first readability, with larger defaults for accessibility.

```css
:root {
  /* Font Families */
  --font-display: 'Noto Sans Devanagari', 'Inter', sans-serif;
  --font-body: 'Noto Sans Devanagari', 'Inter', sans-serif;

  /* Font Weights */
  --font-light: 300;
  --font-regular: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Font Sizes (Mobile-first, scaled up for desktop) */
  --text-xs: 12px; /* Small utility text, captions */
  --text-sm: 14px; /* Helper text, metadata */
  --text-base: 16px; /* Body text, form labels */
  --text-md: 18px;   /* Section subtitles, card titles */
  --text-lg: 20px;   /* Card headlines, prominent labels */
  --text-xl: 24px;   /* Page titles, major section headings */
  --text-2xl: 28px;  /* Hero headings */
  --text-3xl: 36px;  /* Main Hero headline */

  /* Line Heights */
  --line-height-tight: 1.2;
  --line-height-base: 1.5;
  --line-height-loose: 1.8;
}

/* Base styles */
html { font-size: 100%; /* Ensures 1rem = 16px by default */ }
body {
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: var(--line-height-base);
  color: var(--ink);
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-display);
  font-weight: var(--font-bold);
  line-height: var(--line-height-tight);
  color: var(--navy);
  margin-bottom: var(--spacing-sm);
}
h1 { font-size: var(--text-3xl); }
h2 { font-size: var(--text-2xl); }
h3 { font-size: var(--text-xl); }
h4 { font-size: var(--text-lg); }
h5 { font-size: var(--text-md); }
h6 { font-size: var(--text-base); color: var(--ink); font-weight: var(--font-semibold); }

/* Responsive Adjustments (Example for larger screens) */
@media (min-width: 768px) {
  h1 { font-size: 44px; }
  h2 { font-size: 36px; }
  h3 { font-size: 28px; }
  h4 { font-size: 24px; }
  /* ... and so on for other text sizes if needed */
}
```

### Spacing System

An 8px base grid ensures consistent and harmonious spacing across the design.

```css
:root {
  --spacing-xxs: 4px;
  --spacing-xs: 8px;
  --spacing-sm: 12px;
  --spacing-md: 16px; /* Base padding/gap for many components */
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-2xl: 48px;
  --spacing-3xl: 64px;
  --spacing-4xl: 80px;
}

/* Usage: Use these variables for margin, padding, gap, border-radius, min-height, etc. */
/* Example: .card { padding: var(--spacing-md); margin-bottom: var(--spacing-lg); } */
```

### Component Specs

#### 1. Navigation (`.main-nav`)

*   **Structure:** `header > nav > .container > .logo-link + .nav-toggle + .nav-menu`
*   **Mobile:**
    *   Sticky top, full width, `var(--navy)` background.
    *   Left: Logo (Aarambha Haq text + stylized tricolor icon).
    *   Right: Hamburger icon (`.nav-toggle`) for menu.
    *   Menu (`.nav-menu`) slides in from right or top (overlay) when toggled, `var(--white)` background, full screen height, with close button.
    *   Menu items: Large, clear links with `var(--ink)` text, padding `var(--spacing-lg)` vertical.
*   **Desktop:**
    *   Sticky top, full width, `var(--navy)` background.
    *   Left: Logo.
    *   Right: Horizontal list of links (`.nav-menu`) with `var(--white)` text.
    *   Hover: Links change to `var(--saffron)`.
*   **Tricolor Strip:** A thin `12px` height `div` or `::before` element directly below the primary nav on mobile, or as part of the logo on desktop, using `--tricolor-gradient`.

#### 2. Hero Section (`.hero`)

*   **Structure:** `section.hero > .container > h1 + p + .cta-button`
*   **Background:** `var(--page)` or a subtle illustration.
*   **Headline (`h1`):** `var(--text-3xl)` on mobile, `var(--navy)` color, bold, compelling (e.g., "अपनी सरकारी योजना ढूंढें").
*   **Subtext (`p`):** `var(--text-md)` on mobile, `var(--ink-2)` color, explaining value proposition.
*   **Primary CTA Button:**
    *   `background-color: var(--saffron); color: var(--white);`
    *   `padding: var(--spacing-sm) var(--spacing-lg); border-radius: var(--spacing-xs);`
    *   `font-size: var(--text-lg); font-weight: var(--font-semibold);`
    *   Prominent, center-aligned on mobile.
*   **Tricolor Strip:** A subtle border or graphic element can be integrated at the bottom of the hero.

#### 3. Category Tile (`.category-tile`)

*   **Structure:** `a.category-tile > .icon-wrapper + h4`
*   **Appearance:**
    *   `background-color: var(--white); border: 1px solid var(--line); border-radius: var(--spacing-xs);`
    *   `display: flex; flex-direction: column; align-items: center; justify-content: center;`
    *   `padding: var(--spacing-lg); text-align: center;`
    *   `min-height: 120px; min-width: 120px;` (Mobile tap target)
*   **Icon (`.icon-wrapper`):** Large, simple SVG icon (e.g., Mahila: woman, Student: book). `color: var(--ink-2); font-size: 32px; margin-bottom: var(--spacing-sm);`
*   **Text (`h4`):** `var(--text-md); color: var(--navy); font-weight: var(--font-semibold);`
*   **Hover/Focus:** `box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-color: var(--saffron);`

#### 4. Scheme Card (`.scheme-card`)

*   **Structure:** `article.scheme-card > h3 + p.description + .tags + .cta-button`
*   **Appearance:**
    *   `background-color: var(--white); border: 1px solid var(--line); border-radius: var(--spacing-xs);`
    *   `padding: var(--spacing-md); margin-bottom: var(--spacing-md);`
    *   `box-shadow: 0 2px 4px rgba(0,0,0,0.05);`
*   **Scheme Name (`h3`):** `var(--text-lg); color: var(--navy); margin-bottom: var(--spacing-xs);`
*   **Description (`p.description`):** `var(--text-base); color: var(--ink); line-height: var(--line-height-base); max-height: 3em; overflow: hidden; text-overflow: ellipsis;` (Truncated)
*   **Tags (`.tags`):** Small `span` elements with `background-color: var(--page); color: var(--ink-2); padding: var(--spacing-xxs) var(--spacing-xs); border-radius: var(--spacing-xxs); font-size: var(--text-sm); margin-right: var(--spacing-xs);`
*   **CTA Button:** (e.g., "योजना देखें") `background-color: var(--green); color: var(--white); padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--spacing-xs); font-size: var(--text-base); margin-top: var(--spacing-md);`

#### 5. Wizard Step (`.wizard-step`)

*   **Structure:** `div.wizard-container > .wizard-progress + form.wizard-form > .question-field + .navigation-buttons`
*   **Progress Indicator (`.wizard-progress`):**
    *   Horizontal bar: `background-color: var(--line); height: 8px; border-radius: 4px;`
    *   Filled segment: `background-color: var(--saffron); height: 100%; width: [calculated]%; border-radius: 4px; transition: width 0.3s ease-in-out;`
    *   Optional step numbers/text above.
*   **Question Field (`.question-field`):**
    *   `label` for question: `var(--text-lg); color: var(--navy); margin-bottom: var(--spacing-md);`
    *   Input/Select/Radio/Checkbox:
        *   Large tap targets. `min-height: 48px;`
        *   `border: 1px solid var(--line); border-radius: var(--spacing-xs); padding: var(--spacing-sm); font-size: var(--text-base);`
        *   `color: var(--ink);`
        *   `focus: border-color: var(--saffron); box-shadow: 0 0 0 2px rgba(255,153,51,0.2);`
        *   Radio/Checkbox: Custom styled to be larger and more visible.
*   **Navigation Buttons (`.navigation-buttons`):**
    *   `display: flex; justify-content: space-between; margin-top: var(--spacing-xl);`
    *   "पिछला" (Previous): `background-color: var(--white); border: 1px solid var(--ink-2); color: var(--ink-2); padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--spacing-xs);`
    *   "आगे बढ़ें" (Next) / "परिणाम देखें" (View Results): `background-color: var(--saffron); color: var(--white); padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--spacing-xs);`
    *   Both `font-size: var(--text-base); font-weight: var(--font-semibold);`

#### 6. Filter Pill (`.filter-pill`)

*   **Structure:** `button.filter-pill`
*   **Appearance (Default):**
    *   `background-color: var(--page); border: 1px solid var(--line); color: var(--ink-2);`
    *   `padding: var(--spacing-xxs) var(--spacing-sm); border-radius: var(--spacing-lg);` (Pill shape)
    *   `font-size: var(--text-sm); white-space: nowrap;`
*   **Appearance (Active/Selected):**
    *   `background-color: var(--saffron); border-color: var(--saffron); color: var(--white);`
    *   `font-weight: var(--font-medium);`
*   **Hover/Focus:** `box-shadow: 0 2px 4px rgba(0,0,0,0.1);`

#### 7. Footer (`.main-footer`)

*   **Structure:** `footer.main-footer > .container > .footer-links + .copyright`
*   **Background:** `var(--navy);`
*   **Color:** `color: var(--white);`
*   **Links (`.footer-links`):**
    *   Grouped into columns (on desktop) or stacked (on mobile).
    *   Links: `color: var(--white); text-decoration: none; font-size: var(--text-base); margin-bottom: var(--spacing-xs);`
    *   Hover: `color: var(--saffron);`
    *   Headings for link groups: `h5 { color: var(--white); margin-bottom: var(--spacing-sm); }`
*   **Copyright (`.copyright`):** `font-size: var(--text-sm); text-align: center; margin-top: var(--spacing-lg); opacity: 0.8;`
*   **Tricolor Strip:** A thin `12px` height `div` or `::before` element at the very top of the footer.

### Animation Tokens (Subtle, Mobile-Friendly)

Animations are kept minimal to ensure performance on lower-end devices and avoid distracting low-literacy users.

```css
:root {
  --transition-duration-fast: 0.15s;
  --transition-duration-normal: 0.3s;
  --transition-ease-in-out: cubic-bezier(0.4, 0, 0.2, 1); /* Standard Material Design curve */
  --transition-ease-out-quad: cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* Usage Examples: */
/* - Button hover: transition: background-color var(--transition-duration-fast) var(--transition-ease-in-out), transform var(--transition-duration-fast) var(--transition-ease-in-out); */
/* - Card shadow on hover: transition: box-shadow var(--transition-duration-normal) var(--transition-ease-in-out); */
/* - Menu slide-in: transition: transform var(--transition-duration-normal) var(--transition-ease-out-quad); */
/* - Form input focus: transition: border-color var(--transition-duration-fast), box-shadow var(--transition-duration-fast); */
```

---

## B. PAGE WIREFRAMES

All wireframes are conceptualized mobile-first, with notes on desktop adaptations. Hindi labels are used throughout.

### 1. Home Page (`/`)

*   **Goal:** Introduce Aarambha Haq, guide users to the eligibility checker or scheme browsing.
*   **Layout:** Hero (Eligibility Check CTA) -> How It Works (optional) -> Popular Categories -> Footer.

```
+------------------------------------------+
|                 NAV BAR                  |
|  [Logo Aarambha Haq]           [☰ Menu]  |
|------------------------------------------|
|       [Saffron|White|Green Strip]        |
+------------------------------------------+
|            HERO SECTION                  |
|  ------------------------------------    |
| |                                    |   |
| | अपनी सरकारी योजना ढूंढें            |   |
| |                                    |   |
| | अपनी पात्रता जांचें, तुरंत परिणाम पाएं |   |
| |                                    |   |
| |         [अपनी पात्रता जांचें >]    |   |
| |         (Primary Button)           |   |
|  ------------------------------------    |
+------------------------------------------+
|  लोकप्रिय श्रेणियां (Popular Categories) |
|  ------------------------------------    |
| |                                    |   |
| | [Icon]       [Icon]       [Icon]   |   |
| | महिला       छात्र         किसान    |   |
| |------------------------------------|   |
| | [Icon]       [Icon]       [Icon]   |   |
| | रोजगार      वृद्ध         दिव्यांग |   |
| |------------------------------------|   |
| |      [सभी श्रेणियां देखें >]       |   |
| |          (Secondary Button)        |   |
|  ------------------------------------    |
+------------------------------------------+
|                 FOOTER                   |
|       [Saffron|White|Green Strip]        |
|  Aarambha Haq © 2023 | गोपनीयता नीति    |
|  हमें संपर्क करें     | हमारे बारे में   |
+------------------------------------------+
```

**Key HTML Structure (`index.html`):**

```html
<header class="main-nav">
  <div class="container">
    <a href="/" class="logo-link">
      <img src="/static/logo.svg" alt="Aarambha Haq" />
      <span>आरंभ हक</span>
    </a>
    <button class="nav-toggle" aria-label="मेनू खोलें">☰</button>
    <nav class="nav-menu">
      <ul>
        <li><a href="/check">पात्रता जांचें</a></li>
        <li><a href="/yojana">सभी योजनाएं</a></li>
        <li><a href="/haq">अपने अधिकार</a></li>
        <li><a href="/about">हमारे बारे में</a></li>
      </ul>
      <button class="nav-close" aria-label="मेनू बंद करें">✕</button>
    </nav>
  </div>
  <div class="tricolor-strip"></div>
</header>

<main>
  <section class="hero">
    <div class="container">
      <h1>अपनी सरकारी योजना ढूंढें</h1>
      <p>अपनी पात्रता जांचें और तुरंत परिणाम पाएं। यह बिल्कुल मुफ़्त है!</p>
      <a href="/check" class="button button--primary">अपनी पात्रता जांचें ></a>
    </div>
  </section>

  <section class="section--categories">
    <div class="container">
      <h2>लोकप्रिय श्रेणियां</h2>
      <div class="category-grid">
        <a href="/yojana/mahila" class="category-tile">
          <img src="/static/icons/mahila.svg" alt="महिला योजनाएं" />
          <h4>महिला</h4>
        </a>
        <!-- ... other popular categories ... -->
        <a href="/yojana/kisan" class="category-tile">
          <img src="/static/icons/kisan.svg" alt="किसान योजनाएं" />
          <h4>किसान</h4>
        </a>
      </div>
      <a href="/yojana" class="button button--secondary button--center">सभी श्रेणियां देखें ></a>
    </div>
  </section>
</main>

<footer class="main-footer">
  <div class="tricolor-strip"></div>
  <div class="container">
    <div class="footer-links">
      <div>
        <h5>जानकारी</h5>
        <ul>
          <li><a href="/about">हमारे बारे में</a></li>
          <li><a href="/haq">अपने अधिकार</a></li>
          <li><a href="/privacy">गोपनीयता नीति</a></li>
        </ul>
      </div>
      <div>
        <h5>संपर्क करें</h5>
        <ul>
          <li><a href="/contact">हमें संपर्क करें</a></li>
          <li><a href="mailto:support@aarambhax.in">ईमेल करें</a></li>
        </ul>
      </div>
    </div>
    <p class="copyright">Aarambha Haq © 2023 | सभी अधिकार सुरक्षित</p>
  </div>
</footer>
```

**Interactive States:**

*   **Nav Toggle:** Clicking `☰` slides in `nav-menu` from right. Clicking `✕` or outside closes it.
*   **Buttons/Links:** Subtle `transform: translateY(-2px); box-shadow: ...;` on hover/focus.
*   **Category Tiles:** Border color changes to `--saffron`, subtle shadow on hover/focus.

### 2. Eligibility Checker Page (`/check`)

*   **Goal:** Guide users through a series of questions to determine scheme eligibility.
*   **Layout:** Progress Indicator -> Question Card -> Navigation Buttons. Multi-step wizard.

```
+------------------------------------------+
|                 NAV BAR                  |
|  [Logo Aarambha Haq]           [☰ Menu]  |
|------------------------------------------|
|       [Saffron|White|Green Strip]        |
+------------------------------------------+
|            पात्रता जांचें (1/5)          |
|  ------------------------------------    |
| |                                    |   |
| | [Progress Bar: ========----------] |   |
| |                                    |   |
| |     आपकी उम्र क्या है?              |   |
| |                                    |   |
| |  [इनपुट फील्ड: उदाहरण के लिए 30]  |   |
| |                                    |   |
| | [पिछला]          [आगे बढ़ें >]    |   |
| | (Secondary Button) (Primary Button) |   |
|  ------------------------------------    |
+------------------------------------------+
|           RESULTS SCREEN (Step 5/5)      |
|  ------------------------------------    |
| |                                    |   |
| | [Progress Bar: ==================] |   |
| |                                    |   |
| |      आप इन योजनाओं के लिए पात्र हैं! |   |
| |                                    |   |
| | [Scheme Card 1]                    |   |
| | [Scheme Card 2]                    |   |
| | [Scheme Card 3]                    |   |
| |                                    |   |
| |      [पूरी सूची देखें >]           |   |
| |          (Secondary Button)        |   |
|  ------------------------------------    |
+------------------------------------------+
|                 FOOTER                   |
|       [Saffron|White|Green Strip]        |
|  Aarambha Haq © 2023 | गोपनीयता नीति    |
|  हमें संपर्क करें     | हमारे बारे में   |
+------------------------------------------+
```

**Key HTML Structure (`check.html`):**

```html
<header class="main-nav">...</header>
<main class="wizard-page">
  <div class="container">
    <h2 class="wizard-title">पात्रता जांचें <span id="current-step">(1/5)</span></h2>
    <div class="wizard-progress">
      <div class="progress-bar" style="width: 20%;"></div>
    </div>

    <form id="eligibility-form" class="wizard-form">
      <!-- Step 1: Age -->
      <div class="wizard-step active" data-step="1">
        <div class="question-field">
          <label for="age">आपकी उम्र क्या है?</label>
          <input type="number" id="age" name="age" placeholder="उदाहरण के लिए 30" required min="1" max="120" />
        </div>
        <div class="navigation-buttons">
          <!-- <button type="button" class="button button--secondary" disabled>पिछला</button> -->
          <button type="submit" class="button button--primary" data-next-step>आगे बढ़ें ></button>
        </div>
      </div>

      <!-- Step 2: Gender (Hidden by default, shown by JS) -->
      <div class="wizard-step" data-step="2" style="display:none;">
        <div class="question-field">
          <label>आपका लिंग क्या है?</label>
          <div class="radio-group">
            <label><input type="radio" name="gender" value="male" required /> पुरुष</label>
            <label><input type="radio" name="gender" value="female" /> महिला</label>
            <label><input type="radio" name="gender" value="other" /> अन्य</label>
          </div>
        </div>
        <div class="navigation-buttons">
          <button type="button" class="button button--secondary" data-prev-step>पिछला</button>
          <button type="submit" class="button button--primary" data-next-step>आगे बढ़ें ></button>
        </div>
      </div>
      <!-- ... other steps (income, location, category interest, etc.) ... -->

      <!-- Results Step (Hidden by default, shown by JS) -->
      <div class="wizard-step" data-step="final" style="display:none;">
        <h3 class="results-heading">आप इन योजनाओं के लिए पात्र हैं!</h3>
        <div id="eligible-schemes-list" class="scheme-grid">
          <!-- Scheme cards will be inserted here by JS -->
          <p class="no-schemes" style="display:none;">हमें आपकी पात्रता के अनुसार कोई योजना नहीं मिली।</p>
        </div>
        <div class="navigation-buttons">
          <button type="button" class="button button--secondary" data-prev-step>पिछला</button>
          <a href="/yojana" class="button button--primary">पूरी सूची देखें ></a>
        </div>
      </div>
    </form>
  </div>
</main>
<footer class="main-footer">...</footer>
```

**Interactive States:**

*   **Progress Bar:** `width` property updates dynamically with `transition` on step change.
*   **Input Focus:** `border-color` changes to `--saffron`, subtle `box-shadow`.
*   **Radio/Checkbox:** Custom styled to show selected state clearly (e.g., larger dot, background color).
*   **Navigation Buttons:** `disabled` state for "पिछला" on first step. "आगे बढ़ें" becomes "परिणाम देखें" on final question.
*   **Form Validation:** On submit, if fields are invalid, show error messages (e.g., "कृपया अपनी उम्र दर्ज करें") in `--error` color below the input.

### 3. Category Browse Page (`/yojana/[category_slug]` or `/yojana`)

*   **Goal:** Allow users to explore schemes by categories or view all schemes, with filtering options.
*   **Layout:** Page Title -> Categories Grid (if all schemes) / Filters (if specific category) -> Search -> Scheme List.

```
+------------------------------------------+
|                 NAV BAR                  |
|  [Logo Aarambha Haq]           [☰ Menu]  |
|------------------------------------------|
|       [Saffron|White|Green Strip]        |
+------------------------------------------+
|             सभी योजनाएं                  |
|  ------------------------------------    |
| |      [महिला] [छात्र] [किसान]       |   |
| |      [रोजगार] [वृद्ध] [दिव्यांग]    |   |
| |      (Category Pills / Tags)       |   |
|  ------------------------------------    |
|                                          |
|  ------------------------------------    |
| | [Search Icon] [योजना का नाम खोजें...] |   |
| |                                    |   |
| | [Filter Icon] [राज्य] [आयु समूह]    |   |
| |               [अन्य फ़िल्टर]         |   |
| |      (Filter Buttons/Pills)        |   |
|  ------------------------------------    |
|                                          |
|  ------------------------------------    |
| |           Scheme Card 1            |   |
| |           Scheme Card 2            |   |
| |           Scheme Card 3            |   |
| |           (List of Schemes)        |   |
|  ------------------------------------    |
+------------------------------------------+
|                 FOOTER                   |
|       [Saffron|White|Green Strip]        |
|  Aarambha Haq © 2023 | गोपनीयता नीति    |
|  हमें संपर्क करें     | हमारे बारे में   |
+------------------------------------------+
```

**Key HTML Structure (`category_browse.html`):**

```html
<header class="main-nav">...</header>
<main>
  <div class="container">
    <h1 class="page-title">सभी योजनाएं</h1> <!-- Or 'महिला योजनाएं' -->

    <section class="category-filters">
      <!-- Only show if viewing ALL schemes, otherwise current category is inferred -->
      <div class="filter-pills-container" role="group" aria-label="श्रेणी के अनुसार फ़िल्टर करें">
        <button class="filter-pill active" data-category="all">सभी</button>
        <button class="filter-pill" data-category="mahila">महिला</button>
        <button class="filter-pill" data-category="student">छात्र</button>
        <!-- ... other categories ... -->
      </div>
    </section>

    <section class="scheme-search-filters">
      <div class="search-bar">
        <label for="search-scheme" class="sr-only">योजना खोजें</label>
        <input type="search" id="search-scheme" placeholder="योजना का नाम खोजें..." aria-label="योजना का नाम खोजें" />
        <button type="button" aria-label="खोजें"><img src="/static/icons/search.svg" alt="" /></button>
      </div>

      <div class="advanced-filters">
        <button class="button button--ghost" aria-expanded="false" aria-controls="filter-panel">
          <img src="/static/icons/filter.svg" alt="" />
          <span>फ़िल्टर</span>
        </button>
        <div id="filter-panel" class="filter-panel" hidden>
          <!-- Filter options (State, Age Group, Income Level, etc.) -->
          <div class="filter-group">
            <h5>राज्य</h5>
            <select name="state">
              <option value="">कोई भी</option>
              <option value="UP">उत्तर प्रदेश</option>
              <!-- ... -->
            </select>
          </div>
          <div class="filter-group">
            <h5>आयु समूह</h5>
            <div class="radio-group">
              <label><input type="radio" name="age-group" value="all" checked /> सभी</label>
              <label><input type="radio" name="age-group" value="youth" /> युवा (18-35)</label>
              <!-- ... -->
            </div>
          </div>
          <button class="button button--primary">फ़िल्टर लागू करें</button>
          <button class="button button--secondary">फ़िल्टर साफ़ करें</button>
        </div>
      </div>
    </section>

    <section class="scheme-list-section">
      <div class="scheme-grid" id="scheme-results">
        <!-- Scheme Cards will be loaded here -->
        <article class="scheme-card">
          <h3>प्रधानमंत्री आवास योजना</h3>
          <p class="description">यह योजना ग्रामीण और शहरी गरीबों को किफायती आवास प्रदान करती है...</p>
          <div class="tags"><span>आवास</span><span>BPL</span></div>
          <a href="/yojana/pm-awas-yojana" class="button button--secondary">योजना देखें</a>
        </article>
        <!-- ... more scheme cards ... -->
      </div>
      <button class="button button--ghost button--center" id="load-more-schemes" style="display:none;">और योजनाएं लोड करें</button>
      <p class="no-results" style="display:none;">कोई योजना नहीं मिली।</p>
    </section>
  </div>
</main>
<footer class="main-footer">...</footer>
```

**Interactive States:**

*   **Category Pills:** Active state (`--saffron` background) updates on click.
*   **Search Bar:** Clear button appears when text is entered.
*   **Filter Button:** Toggles visibility of `filter-panel`. `aria-expanded` updates.
*   **Filter Panel:** Select/Radio/Checkbox elements behave as standard. "फ़िल्टर लागू करें" triggers API call and updates `scheme-grid`.
*   **Scheme Cards:** Standard hover/focus.
*   **Load More:** Button appears if more schemes are available, disappears when all loaded.

### 4. Scheme Detail Page (`/yojana/[slug]`)

*   **Goal:** Provide comprehensive information about a specific government scheme.
*   **Layout:** Scheme Name -> Eligibility Checker for this scheme -> Key Info (Benefits, Documents) -> How to Apply -> Official Link.

```
+------------------------------------------+
|                 NAV BAR                  |
|  [Logo Aarambha Haq]           [☰ Menu]  |
|------------------------------------------|
|       [Saffron|White|Green Strip]        |
+------------------------------------------+
|     प्रधानमंत्री आवास योजना (PMAY)       |
|  ------------------------------------    |
| |  [मुख्य छवि/आइकन]                   |   |
| |                                    |   |
| |  भारत सरकार द्वारा एक पहल...        |   |
| |                                    |   |
| |     [इस योजना के लिए पात्रता जांचें >] |   |
| |          (Primary Button)          |   |
|  ------------------------------------    |
|                                          |
|  ------------------------------------    |
| |              योजना विवरण            |   |
| |  यह योजना ग्रामीण और शहरी गरीबों ... |   |
| |                                    |   |
| |              लाभ (Benefits)        |   |
| |  - किफायती घर                       |   |
| |  - वित्तीय सहायता                   |   |
| |                                    |   |
| |              पात्रता (Eligibility) |   |
| |  - भारतीय नागरिक होना चाहिए          |   |
| |  - आय मानदंड ...                    |   |
|  ------------------------------------    |
|                                          |
|  ------------------------------------    |
| |            आवेदन कैसे करें         |   |
| |  1. आधिकारिक पोर्टल पर जाएं         |   |
| |  2. आवश्यक दस्तावेज जमा करें        |   |
| |                                    |   |
| |      [आधिकारिक वेबसाइट पर जाएं >]   |   |
| |          (Secondary Button)        |   |
|  ------------------------------------    |
+------------------------------------------+
|                 FOOTER                   |
|       [Saffron|White|Green Strip]        |
|  Aarambha Haq © 2023 | गोपनीयता नीति    |
|  हमें संपर्क करें     | हमारे बारे में   |
+------------------------------------------+
```

**Key HTML Structure (`scheme_detail.html`):**

```html
<header class="main-nav">...</header>
<main>
  <div class="container">
    <a href="/yojana" class="back-link">← सभी योजनाएं</a>
    <h1 class="scheme-title">प्रधानमंत्री आवास योजना (PMAY)</h1>
    <p class="scheme-summary">भारत सरकार द्वारा ग्रामीण और शहरी क्षेत्रों में सभी पात्र परिवारों को किफायती आवास उपलब्ध कराने की एक महत्वपूर्ण पहल।</p>

    <div class="scheme-hero-cta">
      <a href="/check?scheme=pm-awas-yojana" class="button button--primary">इस योजना के लिए पात्रता जांचें ></a>
    </div>

    <section class="scheme-details-section">
      <h2>योजना विवरण</h2>
      <p>प्रधानमंत्री आवास योजना का उद्देश्य वर्ष 2022 तक "सभी के लिए आवास" प्रदान करना है। इसमें निम्न आय वर्ग (LIG) और आर्थिक रूप से कमजोर वर्ग (EWS) के परिवारों को घर बनाने या खरीदने के लिए वित्तीय सहायता प्रदान की जाती है।</p>

      <h3>लाभ (Benefits)</h3>
      <ul class="benefit-list">
        <li><img src="/static/icons/check.svg" alt="" /> किफायती घर और भूखंड उपलब्ध कराना</li>
        <li><img src="/static/icons/check.svg" alt="" /> क्रेडिट-लिंक्ड सब्सिडी योजना (CLSS) के तहत ब्याज सब्सिडी</li>
        <li><img src="/static/icons/check.svg" alt="" /> मौजूदा घरों के सुधार या विस्तार के लिए सहायता</li>
      </ul>

      <h3>पात्रता (Eligibility)</h3>
      <ul class="eligibility-list">
        <li><img src="/static/icons/bullet.svg" alt="" /> आवेदक भारतीय नागरिक होना चाहिए।</li>
        <li><img src="/static/icons/bullet.svg" alt="" /> परिवार की वार्षिक आय ₹3 लाख (EWS) से ₹18 लाख (MIG-II) के बीच होनी चाहिए।</li>
        <li><img src="/static/icons/bullet.svg" alt="" /> आवेदक के पास भारत में कहीं भी पक्का घर नहीं होना चाहिए।</li>
        <li><img src="/static/icons/bullet.svg" alt="" /> परिवार के किसी भी सदस्य को केंद्र या राज्य सरकार की किसी अन्य आवास योजना का लाभ नहीं मिल रहा हो।</li>
      </ul>

      <h3>आवश्यक दस्तावेज (Required Documents)</h3>
      <ul class="document-list">
        <li><img src="/static/icons/doc.svg" alt="" /> पहचान प्रमाण (आधार कार्ड, पैन कार्ड)</li>
        <li><img src="/static/icons/doc.svg" alt="" /> निवास प्रमाण (बिजली बिल, राशन कार्ड)</li>
        <li><img src="/static/icons/doc.svg" alt="" /> आय प्रमाण पत्र</li>
        <li><img src="/static/icons/doc.svg" alt="" /> बैंक खाता विवरण</li>
      </ul>

      <h3>आवेदन कैसे करें (How to Apply)</h3>
      <ol class="application-steps">
        <li>प्रधानमंत्री आवास योजना की <a href="https://pmaymis.gov.in/" target="_blank" rel="noopener noreferrer">आधिकारिक वेबसाइट</a> पर जाएं।</li>
        <li>"नागरिक मूल्यांकन" (Citizen Assessment) विकल्प चुनें।</li>
        <li>अपने आधार नंबर और व्यक्तिगत विवरण के साथ आवेदन पत्र भरें।</li>
        <li>आवश्यक दस्तावेज अपलोड करें और आवेदन जमा करें।</li>
      </ol>

      <div class="official-link-section">
        <a href="https://pmaymis.gov.in/" target="_blank" rel="noopener noreferrer" class="button button--green">आधिकारिक वेबसाइट पर जाएं ></a>
        <p class="note">यह आपको सरकारी पोर्टल पर ले जाएगा।</p>
      </div>
    </section>
  </div>
</main>
<footer class="main-footer">...</footer>
```

**Interactive States:**

*   **Buttons:** Standard hover/focus.
*   **Links:** Standard hover/focus. External links open in new tab.
*   **Share button (optional):** A small icon button could be added to share the scheme details via WhatsApp or other platforms.

### 5. Rights KB Page (`/haq`)

*   **Goal:** Provide clear, simple information about citizen rights related to government schemes.
*   **Layout:** Page Title -> Search Bar -> Category Filters -> FAQ-style Article List.

```
+------------------------------------------+
|                 NAV BAR                  |
|  [Logo Aarambha Haq]           [☰ Menu]  |
|------------------------------------------|
|       [Saffron|White|Green Strip]        |
+------------------------------------------+
|             अपने अधिकार (हक)            |
|  ------------------------------------    |
| | [Search Icon] [अधिकार खोजें...]      |   |
| |                                    |   |
| | [Filter Icon] [श्रेणी] [विषय]       |   |
| |      (Filter Buttons/Pills)        |   |
|  ------------------------------------    |
|                                          |
|  ------------------------------------    |
| |       आपका अधिकार क्या है?          |   |
| |  एक संक्षिप्त विवरण...              |   |
| |  [पढ़ें >]                           |   |
| |------------------------------------|   |
| |       सरकारी योजनाओं का लाभ कैसे लें? |   |
| |  एक संक्षिप्त विवरण...              |   |
| |  [पढ़ें >]                           |   |
| |------------------------------------|   |
| |       ...और भी लेख                 |   |
|  ------------------------------------    |
+------------------------------------------+
|                 FOOTER                   |
|       [Saffron|White|Green Strip]        |
|  Aarambha Haq © 2023 | गोपनीयता नीति    |
|  हमें संपर्क करें     | हमारे बारे में   |
+------------------------------------------+
```

**Key HTML Structure (`rights_kb.html`):**

```html
<header class="main-nav">...</header>
<main>
  <div class="container">
    <h1 class="page-title">अपने अधिकार (हक)</h1>
    <p class="page-description">सरकारी योजनाओं और अपने नागरिक अधिकारों के बारे में जानें।</p>

    <section class="kb-search-filters">
      <div class="search-bar">
        <label for="kb-search" class="sr-only">अधिकार खोजें</label>
        <input type="search" id="kb-search" placeholder="अधिकार खोजें..." aria-label="अपने अधिकार लेखों में खोजें" />
        <button type="button" aria-label="खोजें"><img src="/static/icons/search.svg" alt="" /></button>
      </div>

      <div class="filter-pills-container" role="group" aria-label="श्रेणी के अनुसार फ़िल्टर करें">
        <button class="filter-pill active" data-filter="all">सभी</button>
        <button class="filter-pill" data-filter="general">सामान्य जानकारी</button>
        <button class="filter-pill" data-filter="application">आवेदन प्रक्रिया</button>
        <button class="filter-pill" data-filter="grievance">शिकायत निवारण</button>
      </div>
    </section>

    <section class="kb-articles-list">
      <div class="article-card">
        <h3>आपका अधिकार क्या है?</h3>
        <p>भारत का संविधान आपको कई मौलिक अधिकार प्रदान करता है, जिनमें सरकारी योजनाओं का लाभ उठाने का अधिकार भी शामिल है...</p>
        <a href="/haq/what-are-your-rights" class="button button--secondary">पढ़ें ></a>
      </div>
      <div class="article-card">
        <h3>सरकारी योजनाओं का लाभ कैसे लें?</h3>
        <p>सरकारी योजनाओं का लाभ उठाने के लिए सही प्रक्रिया जानना महत्वपूर्ण है। यहां चरण-दर-चरण मार्गदर्शन दिया गया है...</p>
        <a href="/haq/how-to-benefit-from-schemes" class="button button--secondary">पढ़ें ></a>
      </div>
      <!-- ... more articles ... -->
    </div>
    <p class="no-results" style="display:none;">कोई लेख नहीं मिला।</p>
  </section>
</main>
<footer class="main-footer">...</footer>
```

**Interactive States:**

*   **Search Bar:** Clear button appears on input.
*   **Filter Pills:** Active state updates on click. Filters article list dynamically.
*   **Article Cards:** Standard hover/focus.

### 6. About Page (`/about`)

*   **Goal:** Explain the purpose of Aarambha Haq, build trust, and provide transparency.
*   **Layout:** Page Title -> Mission/Vision -> Our Story -> Values -> Contact Info.

```
+------------------------------------------+
|                 NAV BAR                  |
|  [Logo Aarambha Haq]           [☰ Menu]  |
|------------------------------------------|
|       [Saffron|White|Green Strip]        |
+------------------------------------------+
|               हमारे बारे में             |
|  ------------------------------------    |
| |             हमारा मिशन              |   |
| |  "प्रत्येक नागरिक तक सरकारी योजनाओं |   |
| |  की जानकारी पहुंचाना..."             |   |
|  ------------------------------------    |
|                                          |
|  ------------------------------------    |
| |             हमारी कहानी             |   |
| |  Aarambha Haq की शुरुआत इस विचार ... |   |
| |  के साथ हुई थी कि भारत के हर नागरिक |   |
| |  को उनके हक की जानकारी आसानी से मिले। |   |
|  ------------------------------------    |
|                                          |
|  ------------------------------------    |
| |               संपर्क करें             |   |
| |  ईमेल: support@aarambhax.in         |   |
| |                                    |   |
| |  [पता (वैकल्पिक)]                   |   |
|  ------------------------------------    |
+------------------------------------------+
|                 FOOTER                   |
|       [Saffron|White|Green Strip]        |
|  Aarambha Haq © 2023 | गोपनीयता नीति    |
|  हमें संपर्क करें     | हमारे बारे में   |
+------------------------------------------+
```

**Key HTML Structure (`about.html`):**

```html
<header class="main-nav">...</header>
<main>
  <div class="container">
    <h1 class="page-title">हमारे बारे में</h1>
    <p class="page-description">हमारा लक्ष्य भारत के हर नागरिक को उनके हक की जानकारी आसानी से पहुँचाना है।</p>

    <section class="about-section">
      <h2>हमारा मिशन</h2>
      <p>Aarambha Haq का मिशन भारत के हर उस नागरिक तक पहुँच बनाना है, जिसे सरकारी योजनाओं की जानकारी नहीं मिल पाती या जिसे उनकी पात्रता समझने में कठिनाई होती है। हम एक सरल, सुलभ और मुफ़्त मंच प्रदान करते हैं ताकि कोई भी नागरिक अपने हक से वंचित न रहे।</p>
    </section>

    <section class="about-section">
      <h2>हमारी कहानी</h2>
      <p>Aarambha Haq की शुरुआत इस विचार के साथ हुई थी कि भारत की विशाल आबादी, विशेषकर ग्रामीण और अर्ध-शहरी क्षेत्रों में, अक्सर सरकारी कल्याणकारी योजनाओं से अनजान रहती है। डिजिटल डिवाइड और जटिल जानकारी के कारण, कई पात्र लोग उन लाभों से चूक जाते हैं जिनके वे हकदार हैं। हमारा मंच इस अंतर को पाटने और सभी के लिए जानकारी को लोकतांत्रिक बनाने का प्रयास करता है।</p>
    </section>

    <section class="about-section">
      <h2>हमारे मूल्य</h2>
      <ul class="value-list">
        <li><img src="/static/icons/trust.svg" alt="" /> **विश्वास:** हम सटीक और सत्यापित जानकारी प्रदान करने के लिए प्रतिबद्ध हैं।</li>
        <li><img src="/static/icons/accessibility.svg" alt="" /> **सुलभता:** हमारा प्लेटफ़ॉर्म उपयोग में आसान और हर किसी के लिए सुलभ है, भले ही उनकी डिजिटल साक्षरता का स्तर कुछ भी हो।</li>
        <li><img src="/static/icons/transparency.svg" alt="" /> **पारदर्शिता:** हम सभी जानकारी को स्पष्ट और समझने योग्य भाषा में प्रस्तुत करते हैं।</li>
        <li><img src="/static/icons/empowerment.svg" alt="" /> **सशक्तिकरण:** हमारा मानना है कि जानकारी ही शक्ति है, और हम नागरिकों को सशक्त बनाना चाहते हैं।</li>
      </ul>
    </section>

    <section class="about-section contact-info">
      <h2>संपर्क करें</h2>
      <p>यदि आपके कोई प्रश्न या सुझाव हैं, तो कृपया हमसे संपर्क करने में संकोच न करें:</p>
      <p>ईमेल: <a href="mailto:support@aarambhax.in">support@aarambhax.in</a></p>
      <!-- Optional: Physical address, phone number if applicable -->
    </section>
  </div>
</main>
<footer class="main-footer">...</footer>
```

**Interactive States:**

*   **Links:** Standard hover/focus. Mailto link opens email client.

---

## C. IMPLEMENTATION PLAN

The implementation will follow a phased approach, prioritizing core functionality and user experience for the target demographic.

### Project Setup & Tech Stack

*   **Frontend:** Plain HTML, CSS (SCSS/PostCSS for better organization recommended but plain CSS per request), Vanilla JS.
*   **Backend:** FastAPI with Jinja2 for server-side rendering (SSR) HTML templates.
*   **Database:** SQLite for simplicity in early stages, PostgreSQL for production.
*   **Deployment:** Docker for containerization, Nginx for serving static files and reverse proxy.

### Build Sequence

#### Phase 1: Foundation & Static Pages (2-3 weeks)

**Goal:** Establish project structure, core styling, and static content pages.

1.  **Project Setup (1 day):**
    *   Initialize FastAPI project, create `templates`, `static` directories.
    *   Setup basic `main.py` with FastAPI app instance.
    *   Configure Jinja2 templating.
    *   Set up static file serving.
    *   Git repository initialization.
    *   `requirements.txt` (`fastapi`, `uvicorn[standard]`, `jinja2`).
2.  **Global Styles & Theme (`theme.css`) (3 days):**
    *   Implement `--root` variables from `THEME.md` (colors, typography, spacing).
    *   Basic CSS reset, `body` styles.
    *   Global typography rules (H1-H6, P, A).
    *   Base button styles, form input styling.
    *   Utility classes (e.g., `.container`, `.text-center`).
3.  **Navigation & Footer Components (3 days):**
    *   HTML for sticky `header.main-nav` and `footer.main-footer`.
    *   CSS for mobile-first layout, desktop adaptations.
    *   JS for hamburger menu toggle (`nav-toggle`, `nav-menu`).
    *   Tricolor strip implementation.
4.  **Static Pages (Home, About, Rights KB - basic structure) (5 days):**
    *   **Home Page (`index.html`):** Hero section, static category tiles (no data binding yet), placeholder text.
    *   **About Page (`about.html`):** Full content from wireframe.
    *   **Rights KB (`haq.html`):** Basic structure, placeholder article cards.
    *   FastAPI routes for `/`, `/about`, `/haq` to render these templates.
5.  **Iconography & Assets (2 days):**
    *   Collect/create SVG icons (categories, search, filter, check, doc, etc.).
    *   Optimize images.

**Estimated LOC:**
*   HTML: ~400 lines (base templates, home, about, haq)
*   CSS: ~500 lines (theme, global, nav, footer, basic components)
*   JS: ~100 lines (nav toggle)
*   Python (FastAPI): ~50 lines (basic app, routes)

#### Phase 2: Dynamic Content & Scheme Browsing (3-4 weeks)

**Goal:** Enable scheme listing, category browsing, and scheme detail views with real data.

1.  **Database & Data Model (4 days):**
    *   Define SQLAlchemy models for `Scheme`, `Category`, `HaqArticle`.
    *   Create a simple schema for scheme eligibility rules (e.g., `min_age`, `max_income`, `state_id`, `gender`).
    *   Implement database connection (SQLite for dev, PostgreSQL for prod).
    *   Create initial data migration/seeding script for 2,754 schemes.
2.  **Category Browse (`/yojana`, `/yojana/[cat]`) (7 days):**
    *   **Backend:**
        *   FastAPI route `/yojana` to list all categories and schemes.
        *   FastAPI route `/yojana/{category_slug}` to list schemes filtered by category.
        *   API endpoint `/api/schemes` for paginated scheme data, with filters (category, search, state, age, etc.).
    *   **Frontend (`category_browse.html`):**
        *   Render category pills dynamically.
        *   Integrate search bar and filter panel HTML.
        *   Display scheme cards dynamically using JS (fetch from `/api/schemes`).
        *   Implement client-side filtering/search (or API calls for complex filters).
        *   "Load More" functionality for pagination.
3.  **Scheme Detail (`/yojana/[slug]`) (5 days):**
    *   **Backend:**
        *   FastAPI route `/yojana/{scheme_slug}` to fetch and render specific scheme details.
        *   Endpoint for scheme details by slug.
    *   **Frontend (`scheme_detail.html`):**
        *   Render all scheme details (description, benefits, eligibility, docs, how to apply, official link).
        *   "Check eligibility for this scheme" button linking to `/check?scheme=[slug]`.
4.  **Rights KB - Dynamic Content (3 days):**
    *   **Backend:**
        *   FastAPI route `/haq/{article_slug}` to fetch and render article details.
        *   API endpoint for `/api/haq-articles` with search/filter.
    *   **Frontend (`haq.html`):**
        *   Render article cards dynamically from `api/haq-articles`.
        *   Basic search and category filter (JS).

**Estimated LOC:**
*   HTML: ~600 lines (category_browse, scheme_detail, haq_article_detail)
*   CSS: ~400 lines (category grid, scheme card, filter pills, search bar, article card)
*   JS: ~500 lines (dynamic scheme loading, filtering, search, pagination)
*   Python (FastAPI): ~400 lines (models, crud, routes for schemes/categories/articles, API endpoints)

#### Phase 3: Eligibility Checker (The Wizard) (4-5 weeks)

**Goal:** Implement the core eligibility checker functionality, including the multi-step wizard and backend logic.

1.  **Eligibility Logic Backend (10 days):**
    *   Refine `Scheme` model to have comprehensive eligibility criteria (e.g., JSONB field for complex rules).
    *   Develop a `SchemeEligibilityChecker` service in Python.
        *   Method to get initial questions.
        *   Method to process answers, refine questions.
        *   Method to match user profile against all schemes' criteria and return eligible schemes.
    *   FastAPI endpoints:
        *   `POST /api/check/start`: Returns first set of questions.
        *   `POST /api/check/answer`: Accepts user answers, returns next questions or final results.
        *   `GET /api/check/results?session_id=...`: (Optional) If results need to be fetched later.
2.  **Eligibility Checker Frontend (`/check`) (12 days):**
    *   **HTML (`check.html`):** Wizard structure (progress bar, step containers, navigation buttons).
    *   **JS (Wizard Logic):**
        *   Manage wizard state (current step, collected answers).
        *   Dynamically render questions (text input, radio, select) based on API responses from `/api/check/start` and `/api/check/answer`.
        *   Input validation and error messages.
        *   Update progress bar visually.
        *   Handle "Previous" and "Next" button logic.
        *   When eligibility check completes, display eligible schemes using `scheme-card` components.
        *   Handle "no schemes found" state.
        *   Integrate pre-filling logic if coming from a specific scheme detail page (`/check?scheme=[slug]`).
    *   **CSS:** Wizard specific styling (progress bar, question fields, radio/checkbox custom styles).
3.  **Result Display & Refinements (5 days):**
    *   Ensure results are clearly presented, with direct links to scheme details.
    *   Add options to refine search/filters on the results page.
    *   Accessibility testing for the wizard flow.

**Estimated LOC:**
*   HTML: ~200 lines (wizard form specific elements)
*   CSS: ~300 lines (wizard specific components, form elements)
*   JS: ~1000 lines (complex wizard logic, API interaction, dynamic rendering, validation)
*   Python (FastAPI): ~800 lines (eligibility service, complex logic, API endpoints)

#### Phase 4: Refinement, Testing & Deployment (2-3 weeks)

**Goal:** Polish the application, ensure robustness, and prepare for launch.

1.  **Accessibility (A11y) & Usability (5 days):**
    *   Review all pages for WCAG compliance (ARIA attributes, keyboard navigation, color contrast).
    *   Conduct user testing with target audience (rural/semi-urban Hindi speakers) to identify pain points.
    *   Refine UI/UX based on feedback.
2.  **Performance Optimization (4 days):**
    *   Minimize CSS/JS (concatenation, minification).
    *   Optimize images.
    *   Lazy loading for images/schemes.
    *   Ensure fast initial load times, especially for mobile networks.
3.  **Error Handling & Empty States (3 days):**
    *   Implement robust error pages (404, 500).
    *   Handle "no results found" for scheme browsing, search, and eligibility checks.
    *   User-friendly error messages for form validation.
4.  **SEO & Analytics (2 days):**
    *   Add meta tags, structured data (JSON-LD for schemes/articles).
    *   Implement basic analytics (e.g., Google Analytics or plausible.io).
5.  **Deployment (3 days):**
    *   Dockerize FastAPI application.
    *   Set up Nginx configuration.
    *   Deploy to chosen cloud provider (e.g., AWS EC2, DigitalOcean).
    *   Configure HTTPS (Let's Encrypt).
    *   Monitoring setup.

**Estimated LOC:**
*   HTML: ~100 lines (error pages, meta tags)
*   CSS: ~100 lines (minor tweaks, performance related)
*   JS: ~200 lines (performance, analytics, minor fixes)
*   Python (FastAPI): ~100 lines (error handlers, logging, config)

---

**Total Estimated LOC & Time:**

*   **HTML:** ~1300 lines
*   **CSS:** ~1300 lines
*   **JS:** ~1800 lines
*   **Python (FastAPI):** ~1350 lines
*   **Total Development Time:** Approximately 11-15 weeks (excluding extended user research/testing cycles).

This plan provides a structured approach to building Aarambha Haq, ensuring a user-centric design is backed by a robust and efficient technical implementation.