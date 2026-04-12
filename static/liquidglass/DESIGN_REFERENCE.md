# Design Reference Guide

## 📐 Spacing & Sizing

### Layout Dimensions

| Element | Width | Height | Notes |
|---------|-------|--------|-------|
| Viewport | 100vw | 100vh | Full screen |
| Left Panel | 52% (desktop) | 100vh | Shows on all screens |
| Right Panel | 48% (desktop) | 100vh | Hidden on mobile (lg breakpoint = 1024px) |
| Mobile | 100% | auto | Stacks vertically |

### Padding & Margins

| Component | Padding | Notes |
|-----------|---------|-------|
| Navigation | px-10 py-6 (lg: px-12 py-8) | Top spacing with gap-3 between items |
| Hero Content | px-6 lg:px-12 | Horizontal breathing room |
| Quote Section | px-6 lg:px-12 pb-8 lg:pb-12 | Bottom-heavy for visual anchor |
| Right Panel | px-8 py-8 | Consistent inset from edges |

### Element Sizing

| Element | Size | Purpose |
|---------|------|---------|
| Icon (small) | 18px | lucide icons in buttons |
| Icon (medium) | 20px | Navigation menu icon |
| Icon (large) | 32px | Not used, available |
| Logo (nav) | 32×32 | Navigation bar |
| Logo (hero) | 80×80 | Main section |
| Flower image | 96×64 | Feature card thumbnail |

### Gap & Spacing Units

| Tailwind | Pixels | Usage |
|----------|--------|-------|
| gap-3 | 12px | Pill tags, icon groups |
| gap-4 | 16px | Feature card sections |
| gap-6 | 24px | Hero sections (logo + heading) |
| gap-8 | 32px | Panel-level spacing |

---

## 🎨 Color Palette

### Primary Colors (Grayscale Only)

All colors use HSL notation: `hsl(0 0% X%)`

| Name | HSL Value | CSS Value | Opacity | Usage |
|------|-----------|-----------|---------|-------|
| White (100%) | `hsl(0 0% 100%)` | `#FFFFFF` | 1.0 | Primary text |
| White (80%) | `hsl(0 0% 100%)` | `#FFFFFF` | 0.8 | Secondary headings, serif text |
| White (60%) | `hsl(0 0% 100%)` | `#FFFFFF` | 0.6 | Tertiary text, descriptions |
| White (50%) | `hsl(0 0% 100%)` | `#FFFFFF` | 0.5 | Labels, small caps, dividers |
| White (15%) | `rgba(255,255,255,0.15)` | varies | 0.15 | Button backgrounds, overlays |
| White (10%) | `rgba(255,255,255,0.1)` | varies | 0.1 | Icon containers, subtle dividers |
| Black (0%) | `hsl(0 0% 0%)` | `#000000` | 1.0 | Background only |

### Apply to Elements

```tsx
// Text
className="text-white"        // 100% white
className="text-white/80"     // 80% white
className="text-white/60"     // 60% white
className="text-white/50"     // 50% white

// Backgrounds
className="bg-white/15"       // 15% white overlay
className="bg-white/10"       // 10% white overlay

// Borders (via pseudo-elements, no border classes)
```

---

## 🔤 Typography

### Font Families

| Font | Source | Weight | Usage |
|------|--------|--------|-------|
| Poppins | Google Fonts | 400, 500, 600, 700 | Display, headings, body (use 500) |
| Source Serif 4 | Google Fonts | 400 (italic), 600 | Italic emphasis only inside headings |

### Font Sizes & Weights

| Element | Size | Weight | Weight Token | Line Height |
|---------|------|--------|--------------|-------------|
| H1 (Mobile) | 24px / 1.5rem (text-6xl) | 500 | font-medium | tight |
| H1 (Desktop) | 28px / 1.75rem (text-7xl) | 500 | font-medium | tight |
| H2 | 20px / 1.25rem (text-xl/text-2xl) | 500 | font-medium | tight |
| H3 | 14px / 0.875rem (text-sm/base) | 600 | font-semibold | normal |
| Body | 14px / 0.875rem (text-sm) | 400 | font-normal | relaxed |
| Small | 12px / 0.75rem (text-xs) | 400 | font-normal | tight |
| Pill tags | 12px / 0.75rem (text-xs) | 500 | font-medium | tight |
| Labels | 12px / 0.75rem (text-xs) | 500 | font-medium | tight |

### Letter Spacing

| Element | Tailwind | Value | Purpose |
|---------|----------|-------|---------|
| H1 | tracking-[-0.05em] | -0.05em | Tighter heading |
| H2/H3 | tracking-normal | 0 | Standard |
| Labels | tracking-widest | 0.2em | "VISIONARY DESIGN" |
| Logo text | tracking-tighter | negative | "bloom" word |

### Font Usage Examples

```jsx
// Standard heading
<h1 className="font-display text-6xl lg:text-7xl font-medium tracking-[-0.05em]">
  Innovating the spirit
</h1>

// Italic serif emphasis inside heading
<h1 className="...">
  ... <em className="font-serif text-white/80">spirit</em> ...
</h1>

// Body text
<p className="font-display text-sm lg:text-base text-white/60">
  Description text here
</p>

// Label
<span className="text-xs tracking-widest uppercase text-white/50">
  VISIONARY DESIGN
</span>
```

---

## 💎 Liquid Glass Effect

### Light Variant (.liquid-glass)

```css
.liquid-glass {
  background: rgba(255, 255, 255, 0.01);
  background-blend-mode: luminosity;
  backdrop-filter: blur(4px);
  border: none;
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.liquid-glass::before {
  /* Gradient border via pseudo-element */
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.45) 0%,
    rgba(255, 255, 255, 0.15) 20%,
    transparent 40%,
    transparent 60%,
    rgba(255, 255, 255, 0.15) 80%,
    rgba(255, 255, 255, 0.45) 100%
  );
  padding: 1.4px;
  -webkit-mask-composite: xor;
  mask-composite: exclude;
}
```

**Used For:**
- Pill tags ("Artistic Gallery", "AI Generation", etc.)
- Social icon container
- Community card
- Feature cards (side-by-side)
- Icon containers inside feature cards

### Strong Variant (.liquid-glass-strong)

```css
.liquid-glass-strong {
  background: rgba(255, 255, 255, 0.01);
  background-blend-mode: luminosity;
  backdrop-filter: blur(50px);
  border: none;
  box-shadow: 
    4px 4px 4px rgba(0, 0, 0, 0.05),
    inset 0 1px 1px rgba(255, 255, 255, 0.15);
  position: relative;
  overflow: hidden;
}

.liquid-glass-strong::before {
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.5) 0%,      /* Brighter gradient */
    rgba(255, 255, 255, 0.2) 20%,
    transparent 40%,
    transparent 60%,
    rgba(255, 255, 255, 0.2) 80%,
    rgba(255, 255, 255, 0.5) 100%
  );
  padding: 1.4px;
  -webkit-mask-composite: xor;
  mask-composite: exclude;
}
```

**Used For:**
- Left panel overlay (inset-4 lg:inset-6 rounded-3xl)
- CTA button "Explore Now"
- Menu button
- Feature section outer container (rounded-[2.5rem])

### Key Differences

| Property | Light | Strong |
|----------|-------|--------|
| backdrop-filter blur | 4px | 50px |
| outer-shadow | none | 4px 4px 4px rgba(0,0,0,0.05) |
| inset-shadow opacity | 0.1 | 0.15 |
| gradient top/bottom | 0.45 | 0.5 |
| gradient mid | 0.15 | 0.2 |
| Use case | Subtle tags | Featured elements |

---

## ✨ Interactive States

### Hover Effects

| Element Type | Effect | CSS |
|--------------|--------|-----|
| Buttons/Cards | Scale up | `hover:scale-105` |
| Text/Icons | Color fade | `hover:text-white/80` |
| Containers | Glass intensify | `hover:backdrop-blur-[5px]` (custom) |

### Active Effects

| Element Type | Effect | CSS |
|--------------|--------|-----|
| Buttons | Scale down | `active:scale-95` |
| Containers | Darker inset | `active:shadow-lg` |

### Transition Properties

```css
.interactive {
  transition: transform 300ms ease-out;
}

.interactive:hover {
  transform: scale(1.05);
}

.interactive:active {
  transform: scale(0.95);
}
```

---

## 📏 Border Radius

| Element | Value | Token |
|---------|-------|-------|
| Panel overlay | rounded-3xl | 1.875rem |
| Feature section | rounded-[2.5rem] | 2.5rem |
| Pill tags | rounded-full | 9999px |
| Buttons (most) | rounded-full | 9999px |
| Icon containers | rounded-full | 9999px |
| Small cards | rounded-2xl | 1rem |
| Default | --radius | 1rem |

---

## 🎯 Component Layout Breakdown

### Navigation Bar

```
Height: py-6 (24px) lg:py-8 (32px)
Layout: flex items-center justify-between px-10 lg:px-12

Left Side:
  - Logo box: w-8 h-8 bg-white/20 rounded-lg
  - Logo text: text-2xl font-semibold tracking-tighter text-white

Right Side:
  - Menu button: liquid-glass w-10 h-10 rounded-full
  - Icon inside: Menu size={20}
```

### Hero Center

```
Spacing: mb-12 (logo), mb-8 (heading), mb-12 (button), gap-3 (pills)

Logo:
  - w-20 h-20 bg-white/20 rounded-lg
  - Centered with mx-auto

Heading:
  - font-display text-6xl lg:text-7xl tracking-[-0.05em]
  - text-white font-medium leading-tight
  - mb-8

CTA Button:
  - liquid-glass-strong rounded-full px-8 py-4
  - flex gap-3 items-center
  - Download icon in w-7 h-7 rounded-full bg-white/15

Pills:
  - liquid-glass rounded-full px-6 py-2
  - text-xs text-white/80 font-medium
  - flex gap-3 justify-center flex-wrap
```

### Quote Section

```
Spacing: mb-4 (label), mb-6 (quote), normal (author dividers)

Label:
  - text-xs tracking-widest uppercase text-white/50

Quote:
  - font-serif text-lg lg:text-xl italic text-white/80
  - max-w-md

Author:
  - flex gap-4 items-center text-white/60 text-xs font-medium
  - Divider: h-px w-8 bg-white/30
```

### Right Panel Top Bar

```
Spacing: mb-8 (main), gap-3 (icons)

Social Container:
  - liquid-glass rounded-full px-4 py-3
  - flex items-center gap-3

Icon Buttons:
  - icon-container: w-8 h-8 rounded-full bg-white/10
  - flex items-center justify-center

Divider:
  - w-px h-5 bg-white/20

Account Button:
  - liquid-glass-strong w-12 h-12 rounded-full
  - flex items-center justify-center
```

---

## 🎬 Animation Timing

| Element | Delay | Duration | Easing |
|---------|-------|----------|--------|
| Hover scale | 0ms | 300ms | ease-out |
| Active press | 0ms | 100ms | ease-out |
| Text color fade | 0ms | 300ms | ease-out |

---

## 📊 Responsive Grid

### Desktop Breakpoints

- **sm**: 640px
- **md**: 768px
- **lg**: 1024px ← **Bloom uses this**
- **xl**: 1280px
- **2xl**: 1536px

### Bloom Breakpoint Usage

```
< 1024px (mobile)
  └─ Right panel: hidden (hidden lg:flex)
  └─ Layout: Single column, full width
  └─ Padding: px-6
  └─ Typography: text-6xl (H1)

≥ 1024px (desktop)
  └─ Right panel: visible (flex)
  └─ Layout: Two columns (52% + 48%)
  └─ Padding: px-12
  └─ Typography: text-7xl (H1)
```

---

## 🔍 Z-Index Stacking

| Layer | Z-Index | Content |
|-------|---------|---------|
| Video background | 0 | MP4 video with object-cover |
| Content overlay | 10 | All interactive elements |

---

## 📝 Complete Color Reference

### Copy-Paste Values

```css
/* Text Colors */
color: #FFFFFF;              /* text-white */
color: rgba(255,255,255,.8); /* text-white/80 */
color: rgba(255,255,255,.6); /* text-white/60 */
color: rgba(255,255,255,.5); /* text-white/50 */

/* Background Colors */
background: rgba(255,255,255,.15); /* bg-white/15 */
background: rgba(255,255,255,.10); /* bg-white/10 */
background: rgba(255,255,255,.01); /* glass background */

/* Shadow Colors */
box-shadow: inset 0 1px 1px rgba(255,255,255,.1);  /* light */
box-shadow: inset 0 1px 1px rgba(255,255,255,.15); /* strong */

/* Gradient Colors */
rgba(255,255,255, 0.45) /* gradient bright */
rgba(255,255,255, 0.15) /* gradient mid */
transparent              /* gradient transparent */
```

---

**All values are in Tailwind CSS by default. For custom values, use the exact pixel/percentage units shown above.**
