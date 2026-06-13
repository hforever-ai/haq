### 1. Home Hero – Image Carousel

The hero section must transition from a static, dry government banner into an emotional, cinematic storytelling engine. The carousel features 5 selected Indian poster-style illustrations that rotate to represent different segments of the Indian populace.

#### Carousel Image Selections (5 Key Slides)
1. **`cat-mahila.png`**: Representing women's empowerment, maternal health, and self-help groups.
2. **`cat-farmer.png`**: Representing agricultural subsidies, crop insurance, and equipment loans.
3. **`cat-student.png`**: Representing scholarships, skill development, and free laptops.
4. **`cat-employment.png`**: Representing MSME loans, rural employment, and startup grants.
5. **`cat-health.png`**: Representing medical insurance, free diagnostics, and wellness clinics.

#### Desktop Layout (1280px Grid)
- **Container Structure**: 2-column asymmetric CSS Grid (`grid-template-columns: 1.2fr 0.8fr;`) with a maximum width of `1280px` and a height of exactly `480px`.
- **Left Column (Text Content & CTA)**: Occupies `1.2fr`. Vertical flex layout (`flex-direction: column; justify-content: center; align-items: flex-start;`). Features a deep navy background (`--navy`) with an overlay gradient to ensure high readability.
- **Right Column (Image Area)**: Occupies `0.8fr`. Features a 16:9 ratio frame masked with a smooth, organic SVG curve on its left edge to blend seamlessly into the navy text block.
- **Positioning**: Absolute positioning for inactive slides (`opacity: 0; pointer-events: none;`) and relative positioning for the active slide (`opacity: 1; pointer-events: auto;`).

```
+-------------------------------------------------------------------------+
|                                1280px                                   |
+----------------------------------------------------+--------------------+
|  LEFT COLUMN (1.2fr)                               | RIGHT COLUMN (0.8f)|
|                                                    |                    |
|  [Haq-Badge]                                       |  +--------------+  |
|  <h1>आपके अधिकार, आपकी तरक्की</h1>                 |  |              |  |
|  <p>Find schemes tailored for you...</p>           |  |  Image Area  |  |
|                                                    |  |  (16:9 Mask) |  |
|  [Start Finder CTA]                                |  |              |  |
|                                                    |  +--------------+  |
|  (..) Indicator Dots                               |                    |
+----------------------------------------------------+--------------------+
```

#### Mobile Layout (375px Viewport)
- **Stacking Order**: The image is positioned **above** the text.
- **Dimensions**:
  - Image Area: Height exactly `180px`, width `100vw` (full bleeding to the screen edges).
  - Text Area: Height auto-adjusting, padding set to `--s8` (32px) top/bottom and `--s4` (16px) left/right.
- **Layout**: Simple vertical flex block. The left-side SVG mask is disabled on mobile viewports.

#### Auto-Rotate Settings
- **Timing Interval**: `6000ms` (6 seconds) per slide to allow users to read the localized copy.
- **Transition Type**: Cross-fade combined with a subtle horizontal translation (slide-and-fade).
- **Duration**: `650ms` using a custom cubic-bezier curve (`cubic-bezier(0.16, 1, 0.3, 1)` - Ease Out Expo).

#### Indicator Dots
- **Presence**: Yes, positioned at the bottom left of the text column, aligned with the text margins.
- **Style**: Pill-shaped horizontal indicators. The active dot expands to three times the width of an inactive dot.
- **Colors**: Inactive dot: `rgba(255, 255, 255, 0.3)`. Active dot: `--saffron` (`#FF9933`).

#### CSS Implementation

```css
/* Hero Carousel Core Layout */
.hero-carousel {
  position: relative;
  width: 100%;
  max-width: 1280px;
  height: 480px;
  margin: 0 auto;
  background-color: var(--navy);
  border-radius: var(--r-lg);
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(11, 31, 77, 0.15);
}

.hero-slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  opacity: 0;
  pointer-events: none;
  transition: opacity 650ms cubic-bezier(0.16, 1, 0.3, 1), 
              transform 650ms cubic-bezier(0.16, 1, 0.3, 1);
  transform: translateX(20px);
  z-index: 1;
}

.hero-slide.is-active {
  opacity: 1;
  pointer-events: auto;
  transform: translateX(0);
  z-index: 2;
}

/* Content Panel styling */
.hero-slide-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  padding: var(--s12) var(--s16) var(--s12) var(--s12);
  color: #FFFFFF;
  background: linear-gradient(90deg, var(--navy) 80%, rgba(11, 31, 77, 0.85) 100%);
  z-index: 3;
}

.hero-slide-badge {
  background-color: rgba(255, 153, 51, 0.15);
  color: var(--saffron);
  padding: var(--s2) var(--s4);
  border-radius: var(--r-sm);
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: var(--s4);
  border: 1px solid rgba(255, 153, 51, 0.3);
}

.hero-slide-title {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 2.5rem;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: var(--s4);
  color: #FFFFFF;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.hero-slide-desc {
  font-size: 1.1rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: var(--s8);
  max-width: 520px;
}

/* Image Panel with SVG Mask Curve */
.hero-slide-img-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: var(--navy);
}

.hero-slide-img-wrapper::before {
  content: "";
  position: absolute;
  top: 0;
  left: -1px;
  width: 60px;
  height: 100%;
  background-color: var(--navy);
  clip-path: path('M60,0 C40,120 10,240 0,240 C10,240 40,360 60,480 Z');
  z-index: 4;
}

.hero-slide-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  transform: scale(1.05);
  transition: transform 6000ms linear;
}

.hero-slide.is-active .hero-slide-img {
  transform: scale(1);
}

/* Indicators */
.hero-indicators {
  position: absolute;
  bottom: var(--s6);
  left: var(--s12);
  display: flex;
  gap: var(--s2);
  z-index: 10;
}

.hero-dot {
  width: 8px;
  height: 8px;
  border-radius: 4px;
  background-color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  border: none;
  padding: 0;
  transition: width 300ms ease, background-color 300ms ease;
}

.hero-dot.is-active {
  width: 24px;
  background-color: var(--saffron);
}

/* Responsive adjustments for mobile viewports */
@media (max-width: 768px) {
  .hero-carousel {
    height: auto;
    border-radius: 0;
  }
  
  .hero-slide {
    position: relative;
    grid-template-columns: 1fr;
    height: auto;
    opacity: 0;
    display: none;
  }
  
  .hero-slide.is-active {
    opacity: 1;
    display: flex;
    flex-direction: column;
  }
  
  .hero-slide-img-wrapper {
    height: 200px;
    order: 1;
  }
  
  .hero-slide-img-wrapper::before {
    display: none;
  }
  
  .hero-slide-content {
    order: 2;
    padding: var(--s6) var(--s4) var(--s12) var(--s4);
    background: var(--navy);
  }
  
  .hero-slide-title {
    font-size: 1.8rem;
  }
  
  .hero-slide-desc {
    font-size: 0.95rem;
    margin-bottom: var(--s6);
  }
  
  .hero-indicators {
    bottom: var(--s4);
    left: var(--s4);
  }
}
```

---

### 2. Home – Category Tiles Upgrade

To elevate the category tiles from basic elements to premium components, we introduce a dual-layer interactive card design. 

```
+------------------------------------------+
|  .cat-tile (Normal State)                |
|  +------------------------------------+  |
|  |  [Lottie Icon (44x44)]             |  |
|  |  <h3>Mahila Kalyan</h3>            |  |
|  |  <p>42 Schemes</p>                 |  |
|  +------------------------------------+  |
|  (Subtle saffron bottom-border glow)     |
+------------------------------------------+

+------------------------------------------+
|  .cat-tile (Hover State)                  |
|  +------------------------------------+  |
|  |  [Lottie Icon plays]               |  |
|  |  <h3 style="color: --navy">...</h3>|  |
|  |  <p>42 Schemes</p>                 |  |
|  +------------------------------------+  |
|  (Card lifts up, vector image peeks in)  |
|  (Saffron border expands around tile)    |
+------------------------------------------+
```

#### Visual Polish & Interactive Features
- **Gradient Borders**: We apply a pseudo-element gradient border using a combination of `--saffron` and `--green` that fades in on hover.
- **Image Peek**: The matching flat vector illustration (`cat-{slug}.png`) sits scaled-down and semi-transparent (`opacity: 0.03`) in the background of the tile. On hover, this background illustration scales up slightly and increases in opacity to `0.12`, creating a layered depth effect.
- **Lottie Behavior**: Keep the 44×44 Lottie icons. On hover, trigger the Lottie animation playback once from frame `0` to loop-out, adding dynamic visual feedback.
- **Background Styling**: The inactive background uses a clean white base with an ultra-thin border (`1px solid #E2E8F0`). On hover, the background transitions to an off-white cream tone (`#FFFDF9`).

#### CSS Overrides

```css
.cat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--s4);
  padding: var(--s4) 0;
}

.cat-tile {
  position: relative;
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: var(--r-md);
  padding: var(--s6);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-decoration: none;
  overflow: hidden;
  transition: transform 300ms cubic-bezier(0.25, 1, 0.5, 1),
              box-shadow 300ms cubic-bezier(0.25, 1, 0.5, 1),
              border-color 300ms cubic-bezier(0.25, 1, 0.5, 1),
              background-color 300ms cubic-bezier(0.25, 1, 0.5, 1);
  z-index: 1;
}

/* Background image peek styling */
.cat-tile::before {
  content: "";
  position: absolute;
  bottom: -10px;
  right: -10px;
  width: 100px;
  height: 100px;
  background-image: var(--cat-bg-image);
  background-size: contain;
  background-repeat: no-repeat;
  background-position: bottom right;
  opacity: 0.04;
  transform: scale(0.9) rotate(5deg);
  transition: transform 400ms cubic-bezier(0.25, 1, 0.5, 1),
              opacity 400ms cubic-bezier(0.25, 1, 0.5, 1);
  z-index: -1;
  pointer-events: none;
}

/* Premium Gradient Border Hover Effect */
.cat-tile::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: var(--r-md);
  padding: 2px; /* Border thickness */
  background: linear-gradient(135deg, var(--saffron), var(--green));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 300ms ease;
  pointer-events: none;
}

.cat-tile-icon {
  width: 44px;
  height: 44px;
  margin-bottom: var(--s4);
  background: rgba(11, 31, 77, 0.03);
  border-radius: var(--r-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 300ms ease;
}

.cat-tile-title {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--navy);
  margin-bottom: var(--s1);
  line-height: 1.3;
}

.cat-tile-count {
  font-size: 0.85rem;
  color: #64748B;
  font-weight: 600;
}

/* Hover States */
.cat-tile:hover {
  transform: translateY(-6px);
  background-color: #FFFDF9; /* Warm premium tint */
  box-shadow: 0 12px 24px rgba(255, 153, 51, 0.08), 
              0 4px 8px rgba(11, 31, 77, 0.04);
  border-color: transparent;
}

.cat-tile:hover::before {
  opacity: 0.14;
  transform: scale(1.15) rotate(0deg);
}

.cat-tile:hover::after {
  opacity: 1;
}

.cat-tile:hover .cat-tile-icon {
  background-color: rgba(255, 153, 51, 0.1);
}
```

---

### 3. Browse Page – Category Header

The category-specific header dynamically adapts to the selected filter (e.g., `category=mahila`), replacing generic UI patterns with rich, illustrative hero blocks.

```
+-------------------------------------------------------------------------+
|  .cat-hero (Desktop - 1280px)                                           |
|  +--------------------------------------+----------------------------+  |
|  |  [Breadcrumbs]                       |                            |  |
|  |  <h1>महिला कल्याण योजनाएं</h1>       |      [cat-mahila.png]      |  |
|  |  <p>Empowering women through...</p>  |      Vector Illustration   |  |
|  |  [Stats: 42 Schemes | 1.2Cr Saved]   |      (Right Side Panel)    |  |
|  +--------------------------------------+----------------------------+  |
|  (Diagonal separator or soft gradient overlay)                          |
+-------------------------------------------------------------------------+
```

#### Placement & Dimensions
- **Desktop (1280px)**: The header spans the full page width as a rich banner, with content split inside a two-column grid.
  - Left Side (Text & Stats): Takes up `60%` width.
  - Right Side (Illustration Panel): Takes up `40%` width. It houses the `cat-mahila.png` illustration at a fixed height of `280px`.
- **Mobile (375px)**: The illustration does not disappear. Instead, it scales down to form a top strip banner with a height of `120px` and a bottom overlay gradient that blends into the navy content card below.

#### Next.js Image Component Configuration
To ensure proper image delivery, optimal layout shifting behavior (CLS prevention), and crisp rendering across devices, the component is defined as follows:

```jsx
import Image from 'next/image';

// Inside Category Header Component
<div className="cat-hero-img-container">
  <Image
    src={`/scheme-images/cat-${categorySlug}.png`}
    alt={`${categoryName} Illustration`}
    fill
    priority
    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 40vw, 512px"
    quality={85}
    className="cat-hero-img"
  />
</div>
```

#### CSS Implementation

```css
.cat-hero {
  position: relative;
  width: 100%;
  background-color: var(--navy);
  border-radius: var(--r-lg);
  overflow: hidden;
  margin-bottom: var(--s8);
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  min-height: 280px;
}

.cat-hero-content {
  padding: var(--s10) var(--s10) var(--s10) var(--s12);
  display: flex;
  flex-direction: column;
  justify-content: center;
  z-index: 2;
}

.cat-hero-breadcrumb {
  display: flex;
  gap: var(--s2);
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: var(--s3);
}

.cat-hero-breadcrumb a {
  color: var(--saffron);
  text-decoration: none;
}

.cat-hero-title {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 2.2rem;
  font-weight: 800;
  color: #FFFFFF;
  margin-bottom: var(--s2);
}

.cat-hero-desc {
  font-size: 1rem;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: var(--s4);
  max-width: 580px;
}

.cat-hero-stats {
  display: flex;
  gap: var(--s4);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: var(--s4);
}

.cat-stat-item {
  display: flex;
  flex-direction: column;
}

.cat-stat-val {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--saffron);
}

.cat-stat-lbl {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
}

/* Image Container & Overlay */
.cat-hero-img-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 280px;
}

.cat-hero-img {
  object-fit: cover;
  object-position: center;
}

.cat-hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, 
    var(--navy) 0%, 
    rgba(11, 31, 77, 0.9) 30%, 
    rgba(11, 31, 77, 0) 100%
  );
  z-index: 1;
}

/* Mobile responsive specs */
@media (max-width: 768px) {
  .cat-hero {
    grid-template-columns: 1fr;
    min-height: auto;
    border-radius: var(--r-md);
  }
  
  .cat-hero-img-container {
    height: 140px;
    min-height: 140px;
    order: 1;
  }
  
  .cat-hero-content {
    order: 2;
    padding: var(--s6) var(--s4) var(--s8) var(--s4);
  }
  
  .cat-hero-overlay {
    background: linear-gradient(0deg, 
      var(--navy) 0%, 
      rgba(11, 31, 77, 0.7) 50%, 
      rgba(11, 31, 77, 0.2) 100%
    );
  }
  
  .cat-hero-title {
    font-size: 1.6rem;
  }
}
```

---

### 4. Scheme Detail – Header with Image

The detail view uses a split-screen header layout to present key information clearly.

```
+-------------------------------------------------------------------------+
|  .scheme-header                                                         |
|  +--------------------------------------+----------------------------+  |
|  |  [Back to Browse]                    |                            |  |
|  |  [Ministry Tag]                      |      [cat-mahila.png]      |  |
|  |  <h1>PM Matru Vandana Yojana</h1>    |      Illustration Cutout   |  |
|  |  [Badge: Direct Benefit Transfer]    |      (Blurred Backdrop)    |  |
|  +--------------------------------------+----------------------------+  |
+-------------------------------------------------------------------------+
```

#### Layout Specifications
- **Desktop (1280px)**: Two-column grid layout.
  - Left Column (Text, Metadata, Navigation): Spans `65%` of the width.
  - Right Column (Visual Container): Spans `35%` of the width. 
  - To create a depth effect, the selected category illustration is rendered inside a circular frame (`border-radius: 50%`) with a subtle glow, layered over a blurred, low-opacity version of the same image in the background.
- **Mobile (375px)**: The illustration container is hidden on small viewports to keep the focus on the scheme details, badges, and immediate action buttons.

#### CSS Implementation

```css
.scheme-header {
  position: relative;
  width: 100%;
  background-color: var(--navy);
  border-radius: var(--r-lg);
  padding: var(--s10) var(--s12);
  display: grid;
  grid-template-columns: 1.3fr 0.7fr;
  gap: var(--s8);
  overflow: hidden;
  margin-bottom: var(--s8);
}

.scheme-header-main {
  display: flex;
  flex-direction: column;
  justify-content: center;
  z-index: 2;
}

.scheme-back-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--s2);
  color: var(--saffron);
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
  margin-bottom: var(--s6);
}

.scheme-ministry {
  color: var(--green);
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--s2);
}

.scheme-title {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 2.4rem;
  font-weight: 800;
  color: #FFFFFF;
  line-height: 1.25;
  margin-bottom: var(--s4);
}

.scheme-badges {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s2);
}

.scheme-badge-item {
  background-color: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #FFFFFF;
  padding: var(--s1.5) var(--s3);
  border-radius: var(--r-sm);
  font-size: 0.8rem;
  font-weight: 600;
}

/* Right Illustration Cutout */
.scheme-header-visual {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.scheme-visual-backdrop {
  position: absolute;
  width: 260px;
  height: 260px;
  background-image: var(--cat-bg-image);
  background-size: cover;
  filter: blur(20px);
  opacity: 0.15;
  z-index: 1;
}

.scheme-visual-circle {
  position: relative;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  border: 4px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  z-index: 2;
  background-color: #FFFFFF;
}

.scheme-visual-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

@media (max-width: 768px) {
  .scheme-header {
    grid-template-columns: 1fr;
    padding: var(--s6) var(--s4);
    border-radius: var(--r-md);
  }
  
  .scheme-header-visual {
    display: none; /* Hide visual asset on mobile to save space */
  }
  
  .scheme-title {
    font-size: 1.75rem;
  }
}
```

---

### 5. Check Wizard – Premium Feel

The eligibility wizard uses clear progress tracking and transitions to keep the process engaging.

```
+-------------------------------------------------------------------------+
|  .wizard-progress-container                                             |
|  +-------------------------------------------------------------------+  |
|  |  [========== Progress Fill (60% Saffron) ==========]              |  |
|  |  Step 3 of 6: State (राज्य)                                        |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
```

#### Progress Bar Design
- **Style**: Avoid multi-step node indicators, which can feel cluttered on mobile. Instead, use a clean, high-contrast progress bar at the top of the wizard container.
- **Track**: `height: 6px; background-color: rgba(11, 31, 77, 0.08); border-radius: 3px;`
- **Active Fill**: Direct gradient transition from Saffron (`--saffron`) to Green (`--green`).
- **Interactive Stat Indicator**: Floating percentage indicator text (e.g., `Step 3 of 6 (50%)`) rendered in semi-bold navy.

#### Step Card Dimensions & Animations
- **Dimensions**: Maximum width `640px` (desktop), centered horizontally. Height is dynamic based on content to prevent layout shifts.
- **Padding**: Desktop: `--s8` (32px) padding. Mobile: `--s4` (16px) padding.
- **Transition**: Uses a slide-in-and-fade transition to make step changes feel smooth and responsive.

#### Results Moment ("आपके लिए 47 योजनाएं मिलीं!")
When the results load, the interface triggers a celebratory layout:
- **Color Burst Backdrop**: A radial gradient background that expands outward from the center.
- **Scale-Up Animation**: The scheme count text scales up from `0.5` to `1.0` with an elastic bounce.
- **Confetti Effect**: A lightweight CSS particle animation that runs for `2.5 seconds` to celebrate finding matching schemes.

```
      \   |   /
    -  [ 47 ]  -   <-- Scales up with bounce
      /   |   \
  योजनाएं आपके लिए योग्य हैं!
```

#### Kind Empty State ("कोई योजना नहीं मिली")
If no schemes match, the interface displays an encouraging empty state rather than a blank screen.
- **Visuals**: A soft, monochromatic illustration of a warm tea stall or a helper desk, rendered in muted saffron tones.
- **Tone & Copy**: "We couldn't find a direct match, but we are here to help. Try adjusting your filters or speak with a local representative."
- **Action Option**: A primary button to reset the wizard and a secondary button to request manual assistance.

#### CSS Implementation

```css
/* Wizard Outer Container */
.wizard-container {
  max-width: 640px;
  margin: var(--s8) auto;
  padding: 0 var(--s4);
}

/* Progress Area */
.wizard-progress-wrapper {
  margin-bottom: var(--s8);
}

.wizard-progress-track {
  width: 100%;
  height: 6px;
  background-color: rgba(11, 31, 77, 0.08);
  border-radius: var(--r-sm);
  overflow: hidden;
  margin-bottom: var(--s2);
}

.wizard-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--saffron), var(--green));
  width: 0%; /* Dynamic control via state */
  border-radius: var(--r-sm);
  transition: width 400ms cubic-bezier(0.25, 1, 0.5, 1);
}

.wizard-progress-text {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--navy);
}

/* Step Card Wrapper & Animations */
.wizard-step-card {
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: var(--r-lg);
  padding: var(--s8);
  box-shadow: 0 15px 30px rgba(11, 31, 77, 0.05);
  animation: stepEnter 450ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes stepEnter {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Results Hero Styling */
.wizard-result-hero {
  text-align: center;
  padding: var(--s12) var(--s6);
  background: radial-gradient(circle, rgba(255, 153, 51, 0.05) 0%, rgba(255, 255, 255, 0) 70%);
  border-radius: var(--r-lg);
  margin-bottom: var(--s8);
  position: relative;
  overflow: hidden;
}

.wizard-result-number {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 5rem;
  font-weight: 900;
  color: var(--green);
  line-height: 1;
  margin-bottom: var(--s2);
  display: inline-block;
  animation: countPop 600ms cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

@keyframes countPop {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.wizard-result-title {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--navy);
  margin-bottom: var(--s2);
}

/* Confetti background particles */
.confetti-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

/* Warm Empty State Styling */
.wizard-empty-state {
  text-align: center;
  padding: var(--s10) var(--s6);
  background-color: #FFFDF9;
  border: 2px dashed rgba(255, 153, 51, 0.2);
  border-radius: var(--r-lg);
}

.wizard-empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto var(--s4) auto;
  opacity: 0.7;
}

.wizard-empty-title {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--navy);
  margin-bottom: var(--s2);
}

.wizard-empty-desc {
  font-size: 0.95rem;
  color: #64748B;
  line-height: 1.6;
  max-width: 420px;
  margin: 0 auto var(--s6) auto;
}
```

---

### 6. Motion & Micro-Interactions

The application uses subtle CSS transitions and animations to create a polished, interactive experience.

#### Page Transitions
A standard fade-and-slide transition is applied to page loads to ensure a smooth transition between different sections.

```css
.page-transition-enter {
  opacity: 0;
  transform: translateY(8px);
}
.page-transition-enter-active {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 350ms cubic-bezier(0.16, 1, 0.3, 1), 
              transform 350ms cubic-bezier(0.16, 1, 0.3, 1);
}
```

#### Interactive Elements
- **Interactive Buttons**: Buttons scale down slightly on click (`active` state) and smoothly transition their background color and shadow on hover.
- **Card Hover Effects**: Cards lift slightly and display a soft, warm shadow on hover.
- **List and Grid Items**: Grid items use staggered animation delays to fade in sequentially.

#### Accessibility Settings
To support users with motion sensitivities, all transitions and animations are disabled when `prefers-reduced-motion` is active.

```css
@media (prefers-reduced-motion: reduce) {
  *,
  ::before,
  ::after {
    animation-delay: -1ms !important;
    animation-duration: 1ms !important;
    animation-iteration-count: 1 !important;
    background-attachment: initial !important;
    scroll-behavior: auto !important;
    transition-duration: 0s !important;
    transition-delay: 0s !important;
  }
}
```

---

### 7. All New CSS Classes

This section lists all core CSS classes for the application, styled using the design token values: `--saffron`, `--navy`, `--green`, `--s1` to `--s16` (4px grid), and `--r-sm/md/lg`.

```css
/* ==========================================================================
   Aarambha Haq UI Specification - Global Design Tokens Reference
   ========================================================================== */
:root {
  --saffron: #FF9933;
  --navy: #0B1F4D;
  --green: #138808;
  
  /* 4px Grid Spacing Tokens */
  --s1: 4px;
  --s1.5: 6px;
  --s2: 8px;
  --s3: 12px;
  --s4: 16px;
  --s6: 24px;
  --s8: 32px;
  --s10: 40px;
  --s12: 48px;
  --s16: 64px;
  
  /* Border Radius Tokens */
  --r-sm: 6px;
  --r-md: 12px;
  --r-lg: 20px;
}

/* ==========================================================================
   1. Home Hero Carousel Classes
   ========================================================================== */
.hero-carousel {
  position: relative;
  width: 100%;
  max-width: 1280px;
  height: 480px;
  margin: 0 auto;
  background-color: var(--navy);
  border-radius: var(--r-lg);
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(11, 31, 77, 0.15);
}

.hero-slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  opacity: 0;
  pointer-events: none;
  transition: opacity 650ms cubic-bezier(0.16, 1, 0.3, 1), 
              transform 650ms cubic-bezier(0.16, 1, 0.3, 1);
  transform: translateX(20px);
  z-index: 1;
}

.hero-slide.is-active {
  opacity: 1;
  pointer-events: auto;
  transform: translateX(0);
  z-index: 2;
}

.hero-slide-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  padding: var(--s12) var(--s16) var(--s12) var(--s12);
  color: #FFFFFF;
  background: linear-gradient(90deg, var(--navy) 80%, rgba(11, 31, 77, 0.85) 100%);
  z-index: 3;
}

.hero-slide-badge {
  background-color: rgba(255, 153, 51, 0.15);
  color: var(--saffron);
  padding: var(--s2) var(--s4);
  border-radius: var(--r-sm);
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: var(--s4);
  border: 1px solid rgba(255, 153, 51, 0.3);
}

.hero-slide-title {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 2.5rem;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: var(--s4);
  color: #FFFFFF;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.hero-slide-desc {
  font-size: 1.1rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: var(--s8);
  max-width: 520px;
}

.hero-slide-img-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: var(--navy);
}

.hero-slide-img-wrapper::before {
  content: "";
  position: absolute;
  top: 0;
  left: -1px;
  width: 60px;
  height: 100%;
  background-color: var(--navy);
  clip-path: path('M60,0 C40,120 10,240 0,240 C10,240 40,360 60,480 Z');
  z-index: 4;
}

.hero-slide-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  transform: scale(1.05);
  transition: transform 6000ms linear;
}

.hero-slide.is-active .hero-slide-img {
  transform: scale(1);
}

.hero-indicators {
  position: absolute;
  bottom: var(--s6);
  left: var(--s12);
  display: flex;
  gap: var(--s2);
  z-index: 10;
}

.hero-dot {
  width: 8px;
  height: 8px;
  border-radius: 4px;
  background-color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  border: none;
  padding: 0;
  transition: width 300ms ease, background-color 300ms ease;
}

.hero-dot.is-active {
  width: 24px;
  background-color: var(--saffron);
}

/* ==========================================================================
   2. Category Tiles Upgrades (Home Page)
   ========================================================================== */
.cat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--s4);
  padding: var(--s4) 0;
}

.cat-tile {
  position: relative;
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: var(--r-md);
  padding: var(--s6);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-decoration: none;
  overflow: hidden;
  transition: transform 300ms cubic-bezier(0.25, 1, 0.5, 1),
              box-shadow 300ms cubic-bezier(0.25, 1, 0.5, 1),
              border-color 300ms cubic-bezier(0.25, 1, 0.5, 1),
              background-color 300ms cubic-bezier(0.25, 1, 0.5, 1);
  z-index: 1;
}

.cat-tile::before {
  content: "";
  position: absolute;
  bottom: -10px;
  right: -10px;
  width: 100px;
  height: 100px;
  background-image: var(--cat-bg-image);
  background-size: contain;
  background-repeat: no-repeat;
  background-position: bottom right;
  opacity: 0.04;
  transform: scale(0.9) rotate(5deg);
  transition: transform 400ms cubic-bezier(0.25, 1, 0.5, 1),
              opacity 400ms cubic-bezier(0.25, 1, 0.5, 1);
  z-index: -1;
  pointer-events: none;
}

.cat-tile::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: var(--r-md);
  padding: 2px;
  background: linear-gradient(135deg, var(--saffron), var(--green));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 300ms ease;
  pointer-events: none;
}

.cat-tile-icon {
  width: 44px;
  height: 44px;
  margin-bottom: var(--s4);
  background: rgba(11, 31, 77, 0.03);
  border-radius: var(--r-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 300ms ease;
}

.cat-tile-title {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--navy);
  margin-bottom: var(--s1);
  line-height: 1.3;
}

.cat-tile-count {
  font-size: 0.85rem;
  color: #64748B;
  font-weight: 600;
}

.cat-tile:hover {
  transform: translateY(-6px);
  background-color: #FFFDF9;
  box-shadow: 0 12px 24px rgba(255, 153, 51, 0.08), 
              0 4px 8px rgba(11, 31, 77, 0.04);
  border-color: transparent;
}

.cat-tile:hover::before {
  opacity: 0.14;
  transform: scale(1.15) rotate(0deg);
}

.cat-tile:hover::after {
  opacity: 1;
}

.cat-tile:hover .cat-tile-icon {
  background-color: rgba(255, 153, 51, 0.1);
}

/* ==========================================================================
   3. Category Header Classes (Browse Page)
   ========================================================================== */
.cat-hero {
  position: relative;
  width: 100%;
  background-color: var(--navy);
  border-radius: var(--r-lg);
  overflow: hidden;
  margin-bottom: var(--s8);
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  min-height: 280px;
}

.cat-hero-content {
  padding: var(--s10) var(--s10) var(--s10) var(--s12);
  display: flex;
  flex-direction: column;
  justify-content: center;
  z-index: 2;
}

.cat-hero-breadcrumb {
  display: flex;
  gap: var(--s2);
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: var(--s3);
}

.cat-hero-breadcrumb a {
  color: var(--saffron);
  text-decoration: none;
}

.cat-hero-title {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 2.2rem;
  font-weight: 800;
  color: #FFFFFF;
  margin-bottom: var(--s2);
}

.cat-hero-desc {
  font-size: 1rem;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: var(--s4);
  max-width: 580px;
}

.cat-hero-stats {
  display: flex;
  gap: var(--s4);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: var(--s4);
}

.cat-stat-item {
  display: flex;
  flex-direction: column;
}

.cat-stat-val {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--saffron);
}

.cat-stat-lbl {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
}

.cat-hero-img-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 280px;
}

.cat-hero-img {
  object-fit: cover;
  object-position: center;
}

.cat-hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, 
    var(--navy) 0%, 
    rgba(11, 31, 77, 0.9) 30%, 
    rgba(11, 31, 77, 0) 100%
  );
  z-index: 1;
}

/* ==========================================================================
   4. Scheme Detail Header Classes
   ========================================================================== */
.scheme-header {
  position: relative;
  width: 100%;
  background-color: var(--navy);
  border-radius: var(--r-lg);
  padding: var(--s10) var(--s12);
  display: grid;
  grid-template-columns: 1.3fr 0.7fr;
  gap: var(--s8);
  overflow: hidden;
  margin-bottom: var(--s8);
}

.scheme-header-main {
  display: flex;
  flex-direction: column;
  justify-content: center;
  z-index: 2;
}

.scheme-back-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--s2);
  color: var(--saffron);
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
  margin-bottom: var(--s6);
}

.scheme-ministry {
  color: var(--green);
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--s2);
}

.scheme-title {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 2.4rem;
  font-weight: 800;
  color: #FFFFFF;
  line-height: 1.25;
  margin-bottom: var(--s4);
}

.scheme-badges {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s2);
}

.scheme-badge-item {
  background-color: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #FFFFFF;
  padding: var(--s1.5) var(--s3);
  border-radius: var(--r-sm);
  font-size: 0.8rem;
  font-weight: 600;
}

.scheme-header-visual {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.scheme-visual-backdrop {
  position: absolute;
  width: 260px;
  height: 260px;
  background-image: var(--cat-bg-image);
  background-size: cover;
  filter: blur(20px);
  opacity: 0.15;
  z-index: 1;
}

.scheme-visual-circle {
  position: relative;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  border: 4px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  z-index: 2;
  background-color: #FFFFFF;
}

.scheme-visual-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* ==========================================================================
   5. Check Wizard Premium Components
   ========================================================================== */
.wizard-container {
  max-width: 640px;
  margin: var(--s8) auto;
  padding: 0 var(--s4);
}

.wizard-progress-wrapper {
  margin-bottom: var(--s8);
}

.wizard-progress-track {
  width: 100%;
  height: 6px;
  background-color: rgba(11, 31, 77, 0.08);
  border-radius: var(--r-sm);
  overflow: hidden;
  margin-bottom: var(--s2);
}

.wizard-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--saffron), var(--green));
  width: 0%;
  border-radius: var(--r-sm);
  transition: width 400ms cubic-bezier(0.25, 1, 0.5, 1);
}

.wizard-progress-text {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--navy);
}

.wizard-step-card {
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: var(--r-lg);
  padding: var(--s8);
  box-shadow: 0 15px 30px rgba(11, 31, 77, 0.05);
  animation: stepEnter 450ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.wizard-result-hero {
  text-align: center;
  padding: var(--s12) var(--s6);
  background: radial-gradient(circle, rgba(255, 153, 51, 0.05) 0%, rgba(255, 255, 255, 0) 70%);
  border-radius: var(--r-lg);
  margin-bottom: var(--s8);
  position: relative;
  overflow: hidden;
}

.wizard-result-number {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 5rem;
  font-weight: 900;
  color: var(--green);
  line-height: 1;
  margin-bottom: var(--s2);
  display: inline-block;
  animation: countPop 600ms cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

.wizard-result-title {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--navy);
  margin-bottom: var(--s2);
}

.confetti-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.wizard-empty-state {
  text-align: center;
  padding: var(--s10) var(--s6);
  background-color: #FFFDF9;
  border: 2px dashed rgba(255, 153, 51, 0.2);
  border-radius: var(--r-lg);
}

.wizard-empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto var(--s4) auto;
  opacity: 0.7;
}

.wizard-empty-title {
  font-family: 'Noto Sans Devanagari', sans-serif;
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--navy);
  margin-bottom: var(--s2);
}

.wizard-empty-desc {
  font-size: 0.95rem;
  color: #64748B;
  line-height: 1.6;
  max-width: 420px;
  margin: 0 auto var(--s6) auto;
}

/* ==========================================================================
   6. Global Motion & Micro-Interactions
   ========================================================================== */
.btn-premium {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--s3.5) var(--s8);
  background-color: var(--saffron);
  color: #FFFFFF;
  font-weight: 700;
  border-radius: var(--r-sm);
  border: none;
  cursor: pointer;
  overflow: hidden;
  transition: background-color 250ms ease, transform 150ms ease, box-shadow 250ms ease;
  box-shadow: 0 4px 14px rgba(255, 153, 51, 0.3);
}

.btn-premium:hover {
  background-color: #E68019; /* Darkened Saffron */
  box-shadow: 0 6px 20px rgba(255, 153, 51, 0.4);
  transform: translateY(-1px);
}

.btn-premium:active {
  transform: translateY(1px) scale(0.98);
}

.page-transition-enter {
  opacity: 0;
  transform: translateY(8px);
}

.page-transition-enter-active {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 350ms cubic-bezier(0.16, 1, 0.3, 1), 
              transform 350ms cubic-bezier(0.16, 1, 0.3, 1);
}

/* Keyframes */
@keyframes stepEnter {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes countPop {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* ==========================================================================
   7. Media Queries & Responsive Overrides
   ========================================================================== */
@media (max-width: 768px) {
  /* Carousel Mobile */
  .hero-carousel {
    height: auto;
    border-radius: 0;
  }
  
  .hero-slide {
    position: relative;
    grid-template-columns: 1fr;
    height: auto;
    opacity: 0;
    display: none;
  }
  
  .hero-slide.is-active {
    opacity: 1;
    display: flex;
    flex-direction: column;
  }
  
  .hero-slide-img-wrapper {
    height: 200px;
    order: 1;
  }
  
  .hero-slide-img-wrapper::before {
    display: none;
  }
  
  .hero-slide-content {
    order: 2;
    padding: var(--s6) var(--s4) var(--s12) var(--s4);
    background: var(--navy);
  }
  
  .hero-slide-title {
    font-size: 1.8rem;
  }
  
  .hero-slide-desc {
    font-size: 0.95rem;
    margin-bottom: var(--s6);
  }
  
  .hero-indicators {
    bottom: var(--s4);
    left: var(--s4);
  }

  /* Category Header Mobile */
  .cat-hero {
    grid-template-columns: 1fr;
    min-height: auto;
    border-radius: var(--r-md);
  }
  
  .cat-hero-img-container {
    height: 140px;
    min-height: 140px;
    order: 1;
  }
  
  .cat-hero-content {
    order: 2;
    padding: var(--s6) var(--s4) var(--s8) var(--s4);
  }
  
  .cat-hero-overlay {
    background: linear-gradient(0deg, 
      var(--navy) 0%, 
      rgba(11, 31, 77, 0.7) 50%, 
      rgba(11, 31, 77, 0.2) 100%
    );
  }
  
  .cat-hero-title {
    font-size: 1.6rem;
  }

  /* Scheme Detail Mobile */
  .scheme-header {
    grid-template-columns: 1fr;
    padding: var(--s6) var(--s4);
    border-radius: var(--r-md);
  }
  
  .scheme-header-visual {
    display: none;
  }
  
  .scheme-title {
    font-size: 1.75rem;
  }

  /* Wizard Mobile */
  .wizard-step-card {
    padding: var(--s5) var(--s4);
  }
  
  .wizard-result-number {
    font-size: 3.5rem;
  }
}

/* Accessibility: Reduced Motion Support */
@media (prefers-reduced-motion: reduce) {
  *,
  ::before,
  ::after {
    animation-delay: -1ms !important;
    animation-duration: 1ms !important;
    animation-iteration-count: 1 !important;
    background-attachment: initial !important;
    scroll-behavior: auto !important;
    transition-duration: 0s !important;
    transition-delay: 0s !important;
  }
}
```