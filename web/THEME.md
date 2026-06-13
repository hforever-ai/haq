# Aarambha Haq — Website Theme Specification
> `haq.aarambhax.in` · FastAPI + Jinja2 + Plain HTML/CSS/JS · Phone-first

---

## 1. Brand Identity

**Product:** Aarambha Haq — Free government scheme eligibility checker for India  
**Tagline:** अपना हक़ जानिए  
**Audience:** Hindi-speaking rural/semi-urban India, phone-first, low-literacy friendly  
**Tone:** Trustworthy civic-tech. Not government-ugly. Not startup-flashy. Solid + warm.

---

## 2. Color System

```css
:root {
  /* ── Brand (LOCKED — matches Aarambha/Jansampark studio) ── */
  --saffron:       #FF9933;  /* Primary CTA, highlights, active states */
  --saffron-deep:  #EF7A12;  /* Hover on saffron buttons */
  --saffron-tint:  #FFF4E6;  /* Saffron bg for badges, tag bg */
  --green:         #138808;  /* Success, benefit amounts, secondary CTA */
  --green-deep:    #0E6E06;  /* Hover on green buttons */
  --green-tint:    #E7F4E7;  /* Green badges */
  --navy:          #0B1F4D;  /* Headings, nav bg, structure */
  --navy-2:        #16306B;  /* Hover on navy bg */
  --navy-tint:     #EEF1F8;  /* Light navy bg for sections */

  /* ── Neutrals ── */
  --page:          #F6F8FB;  /* Page background */
  --white:         #FFFFFF;  /* Card/modal/input bg */
  --surface-2:     #F1ECE0;  /* Alt surface (blockquotes, aside) */
  --ink:           #16223A;  /* Body text */
  --ink-2:         #5B6678;  /* Muted text, placeholders, icons */
  --ink-3:         #94A0B2;  /* Disabled, caption */
  --line:          #E7EBF1;  /* Borders, dividers */

  /* ── Semantic ── */
  --error:         #D83120;
  --warning:       #F0AD4E;
  --info:          #2196F3;
  --success:       var(--green);

  /* ── Tricolor ── */
  --tricolor: linear-gradient(to right,
    var(--saffron) 0% 33.33%,
    #fff 33.33% 66.66%,
    var(--green) 66.66% 100%);
}
```

### Usage Rules

| Element | Color |
|---------|-------|
| Primary CTA button | bg `--saffron`, text `#fff`, hover `--saffron-deep` |
| Secondary CTA | bg `--green`, text `#fff`, hover `--green-deep` |
| Outline button | bg `#fff`, border `--saffron`, text `--saffron` |
| Ghost button | transparent bg, text `--ink-2`, hover `--navy` |
| Page background | `--page` |
| Card background | `--white` |
| Nav background | `--navy` |
| Nav links | `#fff`, hover `--saffron` |
| Body text | `--ink` |
| Muted text | `--ink-2` |
| All headings | `--navy` |
| Section highlights | `--navy-tint` background |
| Active filter pill | bg `--saffron`, text `--navy` |
| Category tile hover | border `--saffron` |
| Scheme card CTA | `--green` |
| Footer bg | `#081634` (darker navy) |

---

## 3. Typography

```css
:root {
  /* Families */
  --font: 'Noto Sans Devanagari', 'Inter', system-ui, sans-serif;

  /* Weights */
  --fw-regular: 400;
  --fw-medium:  500;
  --fw-semibold: 600;
  --fw-bold:    700;
  --fw-black:   900;

  /* Scale (mobile-first) */
  --text-xs:   11px;   /* captions, fine print */
  --text-sm:   13px;   /* metadata, tags, badges */
  --text-base: 15px;   /* body text */
  --text-md:   17px;   /* card titles, form labels */
  --text-lg:   20px;   /* section sub-headings */
  --text-xl:   24px;   /* section headings h3 */
  --text-2xl:  30px;   /* page titles h2 */
  --text-3xl:  38px;   /* hero headline h1 */

  /* Line heights */
  --lh-tight:  1.15;
  --lh-snug:   1.3;
  --lh-base:   1.55;
  --lh-loose:  1.8;
}

/* Desktop scale bump */
@media (min-width: 768px) {
  :root {
    --text-base: 16px;
    --text-md:   18px;
    --text-lg:   21px;
    --text-xl:   26px;
    --text-2xl:  34px;
    --text-3xl:  46px;
  }
}

/* Base */
body { font-family: var(--font); font-size: var(--text-base); color: var(--ink); line-height: var(--lh-base); }
h1 { font-size: var(--text-3xl); font-weight: var(--fw-black); color: var(--navy); line-height: var(--lh-tight); }
h2 { font-size: var(--text-2xl); font-weight: var(--fw-bold);  color: var(--navy); }
h3 { font-size: var(--text-xl);  font-weight: var(--fw-bold);  color: var(--navy); }
h4 { font-size: var(--text-lg);  font-weight: var(--fw-semibold); color: var(--navy); }
h5 { font-size: var(--text-md);  font-weight: var(--fw-semibold); color: var(--ink); }
```

---

## 4. Spacing System (8px base grid)

```css
:root {
  --sp-1:  4px;
  --sp-2:  8px;
  --sp-3: 12px;
  --sp-4: 16px;   /* default card padding */
  --sp-5: 20px;
  --sp-6: 24px;
  --sp-8: 32px;
  --sp-10: 40px;
  --sp-12: 48px;
  --sp-16: 64px;
  --sp-20: 80px;
}
```

---

## 5. Animation Tokens

```css
:root {
  --dur-fast:   0.12s;
  --dur-normal: 0.25s;
  --dur-slow:   0.4s;
  --ease:       cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out:   cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* Standard transitions */
.btn       { transition: background var(--dur-fast) var(--ease), transform var(--dur-fast) var(--ease), box-shadow var(--dur-fast) var(--ease); }
.card      { transition: transform var(--dur-normal) var(--ease), box-shadow var(--dur-normal) var(--ease); }
.card:hover { transform: translateY(-3px); box-shadow: 0 12px 28px rgba(11,31,77,.10); }
.filter-pill { transition: background var(--dur-fast) var(--ease), color var(--dur-fast) var(--ease); }

/* Reduced motion */
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; } }
```

---

## 6. Responsive Breakpoints

```css
/* Mobile-first breakpoints */
/* xs: 0-480px    → single column, stacked everything */
/* sm: 481-640px  → minor layout adjustments */
/* md: 641-820px  → 2-column grids */
/* lg: 821-1080px → 3-column grids, full desktop nav */
/* xl: 1081px+    → content max-width capped at 1080px */

.wrap { max-width: 1080px; margin: 0 auto; padding: 0 var(--sp-4); }
@media (min-width: 641px) { .wrap { padding: 0 var(--sp-6); } }
```

---

## 7. Component Library

### 7.1 Navigation `.nav`
```
[Navy bg, sticky top]
LEFT:  logo mark (tricolor square) + "Aarambha Haq" + "हक का दरवाज़ा" tagline
RIGHT: nav links (desktop) | ☰ hamburger (mobile)
BOTTOM: 4px tricolor strip (--tricolor)
Nav links: पात्रता जांचें · सभी योजनाएं · अपने अधिकार · हमारे बारे में
```
```css
.nav { position: sticky; top: 0; z-index: 40; background: var(--navy); }
.nav-inner { display: flex; align-items: center; justify-content: space-between; height: 56px; }
.nav-tricolor { height: 4px; background: var(--tricolor); }
.nav-link { color: rgba(255,255,255,.85); font-weight: var(--fw-bold); font-size: var(--text-sm); }
.nav-link:hover, .nav-link.active { color: var(--saffron); }
```

### 7.2 Hero `.hero`
```
[--navy gradient bg] [Ashoka Chakra watermark, opacity 0.06]
Badge: "2,754+ सरकारी योजनाएं · मुफ़्त"
H1: "अपना हक़ जानिए"
Sub: "अपनी पात्रता जांचें — महिला, छात्र, किसान, वृद्ध सभी के लिए"
CTA: [पात्रता जांचें →] saffron button
Trust bar: [🏛 सरकारी डेटा] [📱 मोबाइल-फ्रेंडली] [🔒 मुफ़्त · रजिस्ट्रेशन नहीं]
```
```css
.hero { background: linear-gradient(150deg, var(--navy), var(--navy-2)); color: #fff; padding: var(--sp-12) 0 var(--sp-10); position: relative; overflow: hidden; }
.hero h1 { color: #fff; }
.hero-sub { color: rgba(255,255,255,.75); font-size: var(--text-md); }
.hero-badge { background: rgba(255,153,51,.18); color: var(--saffron); font-size: var(--text-xs); font-weight: var(--fw-black); padding: var(--sp-1) var(--sp-3); border-radius: 999px; display: inline-block; margin-bottom: var(--sp-4); }
```

### 7.3 Category Tile `.cat-tile`
```
[White card, 1px --line border, 16px radius]
Emoji/SVG icon (32px, --ink-2 color)
Hindi label (bold, --navy)
Count badge (x schemes, --ink-3)
Hover: border --saffron, shadow, translateY(-2px)
```
```css
.cat-tile { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: var(--sp-2); background: var(--white); border: 1.5px solid var(--line); border-radius: 14px; padding: var(--sp-6) var(--sp-4); text-align: center; cursor: pointer; }
.cat-tile:hover { border-color: var(--saffron); box-shadow: 0 8px 20px rgba(11,31,77,.08); transform: translateY(-2px); }
.cat-tile .icon { font-size: 28px; line-height: 1; }
.cat-tile h4 { font-size: var(--text-base); font-weight: var(--fw-bold); color: var(--navy); margin: 0; }
.cat-tile .count { font-size: var(--text-xs); color: var(--ink-3); font-weight: var(--fw-medium); }
```

### 7.4 Scheme Card `.scheme-card`
```
[White card, border, 14px radius]
TOP: Level badge (केंद्र/राज्य) + Category tag
H3: scheme name (--navy, 2-line clamp)
P: brief description (3-line clamp, --ink-2)
Tags: category chips
BOTTOM: [आवेदन करें →] green button + State pill
```
```css
.scheme-card { background: var(--white); border: 1px solid var(--line); border-radius: 14px; padding: var(--sp-4); display: flex; flex-direction: column; gap: var(--sp-3); }
.scheme-card:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(11,31,77,.08); }
.scheme-card h3 { font-size: var(--text-md); font-weight: var(--fw-bold); color: var(--navy); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin: 0; }
.scheme-card .desc { font-size: var(--text-sm); color: var(--ink-2); display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; line-height: var(--lh-snug); }
.scheme-card .tag { font-size: 11px; font-weight: var(--fw-bold); background: var(--navy-tint); color: var(--navy); padding: 3px 9px; border-radius: 999px; }
.scheme-card .level-badge { font-size: 11px; font-weight: var(--fw-black); padding: 3px 9px; border-radius: 999px; }
.level-badge.central { background: var(--saffron-tint); color: var(--saffron-deep); }
.level-badge.state    { background: var(--green-tint); color: var(--green-deep); }
```

### 7.5 Wizard Step `.wizard`
```
Progress bar: saffron fill on --line track (height 6px)
Step counter: "चरण 2 / 5" in --ink-2
Question label: h3 --navy
Input: 48px min-height, full width, border --line → focus border --saffron
Radio group: large tap targets (min 44px), custom styled dots
Nav: [← पिछला] outline | [आगे बढ़ें →] saffron fill
```
```css
.wizard-progress { height: 6px; background: var(--line); border-radius: 3px; margin-bottom: var(--sp-6); overflow: hidden; }
.wizard-progress-fill { height: 100%; background: var(--saffron); border-radius: 3px; transition: width var(--dur-normal) var(--ease); }
.wizard-label { font-size: var(--text-lg); font-weight: var(--fw-bold); color: var(--navy); margin-bottom: var(--sp-4); }
.wizard-input { width: 100%; min-height: 48px; border: 1.5px solid var(--line); border-radius: 10px; padding: var(--sp-3) var(--sp-4); font: inherit; font-size: var(--text-base); color: var(--ink); }
.wizard-input:focus { border-color: var(--saffron); box-shadow: 0 0 0 3px rgba(255,153,51,.15); outline: none; }
.radio-opt { display: flex; align-items: center; gap: var(--sp-3); min-height: 48px; padding: var(--sp-3) var(--sp-4); border: 1.5px solid var(--line); border-radius: 10px; cursor: pointer; font-size: var(--text-base); font-weight: var(--fw-medium); color: var(--ink); }
.radio-opt.selected { border-color: var(--saffron); background: var(--saffron-tint); color: var(--navy); font-weight: var(--fw-bold); }
```

### 7.6 Filter Pill `.pill`
```css
.pill { white-space: nowrap; font-size: var(--text-sm); font-weight: var(--fw-bold); color: var(--ink-2); background: var(--white); border: 1.5px solid var(--line); padding: 6px 14px; border-radius: 999px; cursor: pointer; }
.pill.active, .pill:hover { background: var(--saffron); color: var(--navy); border-color: var(--saffron); }
```

### 7.7 Footer `.footer`
```
[Dark navy #081634 bg]
TOP: 4px tricolor strip
GRID: 3 cols (links | links | about+social)
BOT: "Aarambha Haq © 2026 · Data: MyScheme.gov.in · Free & Open"
```
```css
.footer { background: #081634; color: rgba(255,255,255,.75); padding: var(--sp-10) 0 var(--sp-6); }
.footer-top { height: 4px; background: var(--tricolor); }
.footer a:hover { color: var(--saffron); }
.footer-copy { font-size: var(--text-xs); border-top: 1px solid rgba(255,255,255,.1); margin-top: var(--sp-8); padding-top: var(--sp-4); text-align: center; }
```

---

## 8. Grid Patterns

```css
/* Category tiles */
.cat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--sp-3); }
@media (min-width: 641px) { .cat-grid { grid-template-columns: repeat(4, 1fr); } }
@media (min-width: 821px) { .cat-grid { grid-template-columns: repeat(5, 1fr); } }

/* Scheme cards */
.scheme-grid { display: grid; grid-template-columns: 1fr; gap: var(--sp-4); }
@media (min-width: 641px) { .scheme-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 821px) { .scheme-grid { grid-template-columns: repeat(3, 1fr); } }

/* 3-col desktop sidebar layout (Browse page) */
.browse-layout { display: grid; grid-template-columns: 1fr; gap: var(--sp-6); }
@media (min-width: 821px) { .browse-layout { grid-template-columns: 240px 1fr; } }
```

---

## 9. Utility Classes

```css
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); border: 0; }
.text-center { text-align: center; }
.text-muted { color: var(--ink-2); }
.badge { display: inline-flex; align-items: center; gap: 4px; font-size: 11px; font-weight: 800; padding: 3px 9px; border-radius: 999px; }
.badge-saffron { background: var(--saffron-tint); color: var(--saffron-deep); }
.badge-green   { background: var(--green-tint);   color: var(--green-deep); }
.badge-navy    { background: var(--navy-tint);     color: var(--navy); }
.section { padding: var(--sp-10) 0; }
.section-title { font-size: var(--text-2xl); font-weight: var(--fw-black); color: var(--navy); margin-bottom: var(--sp-6); }
```

---

## 10. Trust Signals (Required on homepage)

```html
<!-- Tricolor accent strip -->
<div class="tricolor-strip" style="height:4px; background: var(--tricolor);"></div>

<!-- Trust bar (below hero) -->
<div class="trust-bar">
  <span>🏛 सरकारी डेटा (MyScheme.gov.in)</span>
  <span>2,754+ योजनाएं</span>
  <span>🔓 मुफ़्त · कोई रजिस्ट्रेशन नहीं</span>
  <span>📱 मोबाइल-फ्रेंडली</span>
</div>
```

---

## 11. Page Titles (Hindi-first)

| Route | `<title>` | `<h1>` |
|-------|-----------|--------|
| `/` | अपना हक़ जानिए — Aarambha Haq | अपना हक़ जानिए |
| `/check` | पात्रता जांचें — Aarambha Haq | पात्रता जांचें |
| `/yojana` | सभी सरकारी योजनाएं | सरकारी योजनाएं |
| `/yojana/mahila` | महिला योजनाएं · 381 योजनाएं | महिला सरकारी योजनाएं |
| `/yojana/student` | छात्र योजनाएं · 748 छात्रवृत्ति | छात्र योजनाएं |
| `/haq` | अपने अधिकार — Aarambha Haq | अपने अधिकार |
| `/about` | हमारे बारे में — Aarambha Haq | हमारे बारे में |
