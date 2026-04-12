# Bloom Landing Page — Implementation Guide

## ✅ What's Included

This is a complete, production-ready React + Vite landing page with all requested features:

### Design System

- **Liquid Glass Morphism**
  - `.liquid-glass`: Light variant (backdrop blur 4px)
  - `.liquid-glass-strong`: Heavy variant (backdrop blur 50px) for CTAs and panels
  - Gradient border via `::before` pseudo-elements with CSS mask-composite
  - No border classes—glass effect handles all visual borders

- **Color Palette**
  - Pure HSL grayscale: `hsl(0 0% X%)`
  - Text hierarchy: white, white/80, white/60, white/50
  - Background overlays: white/15, white/10 for interactive elements
  - No colored accents—strict grayscale only

- **Typography**
  - Poppins (Google Fonts): Display/body, font-weight 500
  - Source Serif 4 (Google Fonts): Italic emphasis only (inside `<em>`, `<i>`, `.italic`)
  - Heading sizes: h1 text-6xl/text-7xl, tracking-[-0.05em]

### Layout Features

- **Two-Panel Split** (Desktop)
  - Left: w-[52%] — Hero content, navigation, quote
  - Right: w-[48%] — Social bar, community card, features
  - Mobile: Stacked single column (hidden right panel with `hidden lg:flex`)

- **Full-Screen Video Background**
  - Autoplaying, looping, muted
  - object-fit: cover for full viewport coverage
  - z-index: 0, content floats above at z-10

- **Interactive Elements**
  - All buttons/cards: `hover:scale-105` with `transition-transform`
  - CTA button: Active state `scale-95` for tactile feedback
  - Icons: Color transitions `text-white/80` on hover
  - Smooth 300ms transitions by default

### Components

#### Navigation
- Logo placeholder (32×32, "B" character—replace with image)
- "bloom" text, tracking-tighter, font-semibold, 2xl
- Menu button with lucide Menu icon in liquid-glass pill

#### Hero Section
- Large logo (80×80)
- Main heading with mixed serif/sans-serif: "Innovating the <em>spirit</em> of <em>bloom</em> AI"
- CTA: "Explore Now" with Download icon in circular white/15 background
- Three feature pills: "Artistic Gallery", "AI Generation", "3D Structures"

#### Quote Section
- "VISIONARY DESIGN" label (uppercase, tracking-widest, white/50)
- Serif italic quote: "We imagined a realm with no ending."
- Author with horizontal divider lines: "MARCUS AURELIO"

#### Right Panel (Desktop Only)
- **Top Bar**
  - Social icons: Twitter, LinkedIn, Instagram in liquid-glass container
  - Account button with Sparkles icon
  
- **Community Card**
  - liquid-glass styled
  - Title: "Enter our ecosystem"
  - Description: "Join a community..."

- **Feature Section** (mt-auto)
  - Outer container: liquid-glass rounded-[2.5rem]
  - Two side-by-side cards: Processing (Wand2 icon), Growth Archive (BookOpen icon)
  - Bottom card: Flower placeholder (96×64), title, description, "+" button

### Icons (from lucide-react)

All icons included and ready:
- Sparkles (account button)
- Download (CTA)
- Wand2 (processing card)
- BookOpen (growth archive)
- ArrowRight (social container)
- Twitter, Linkedin, Instagram (social)
- Menu (navigation)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

Installs:
- React 18.2
- React DOM 18.2
- lucide-react (icons)
- Tailwind CSS 3.3
- Vite 4.4
- PostCSS & Autoprefixer

### 2. Development Server

```bash
npm run dev
```

- Opens http://localhost:5173 automatically
- Hot module reloading enabled
- Live CSS changes

### 3. Production Build

```bash
npm run build
```

- Optimizes bundle with Vite
- Outputs to `dist/` folder
- Ready for deployment

### 4. Preview Production Build

```bash
npm run preview
```

## 📂 File Organization

```
src/
├── main.jsx          → React entry point
├── BloomHero.jsx     → Main component (all layout)
└── index.css         → Tailwind + liquid glass styles

public/
└── assets/           → Image placeholders (add logo.png, hero-flowers.png)

index.html           → HTML entry point with Google Fonts CDN
tailwind.config.js   → Tailwind configuration
vite.config.js       → Vite dev server & build settings
```

## 🎨 Customization

### Change Video URL

Edit `BloomHero.jsx`:

```jsx
src="https://your-video-url.mp4"
```

### Add Real Images

Replace placeholders in `BloomHero.jsx`:

```jsx
// Logo (currently: <div className="w-8 h-8 bg-white/20">B</div>)
<img src="/assets/logo.png" alt="Bloom" className="w-8 h-8" />

// Hero flower image (currently: <div className="w-full h-16 bg-white/10">)
<img src="/assets/hero-flowers.png" alt="Flower" className="w-full h-16 rounded-2xl object-cover" />
```

### Adjust Colors

Edit `src/index.css` CSS variables:

```css
:root {
  --radius: 1rem; /* Change border radius */
}
```

Or modify Tailwind opacity values in HTML (e.g., `text-white/80`).

### Modify Text Content

All text is inline in `BloomHero.jsx`. Find and replace strings:
- Heading text
- Button labels
- Card titles
- Quote content

### Responsive Breakpoints

Tailwind breakpoint: `lg` (1024px)
- Mobile: Single column (left panel full width)
- Desktop: Two-panel split

## 🔧 Development Tools

### Code Formatting

```bash
npm install --save-dev prettier
npx prettier --write src/
```

### Linting

```bash
npm install --save-dev eslint eslint-plugin-react
npx eslint src/
```

Configs included:
- `.prettierrc` — Code formatting rules
- `.eslintrc.cjs` — Linting rules
- `jsconfig.json` — IDE support

### Environment Variables

1. Copy `.env.example` to `.env.local`
2. Update values as needed
3. Access in code: `import.meta.env.VITE_*`

## 📋 Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🎯 Performance Notes

- **Video**: Use H.264 MP4 for best compatibility; compress before upload
- **Fonts**: Google Fonts CDN (non-blocking, font-display: swap)
- **Icons**: lucide-react tree-shakes unused icons
- **CSS**: Tailwind purges unused styles in production
- **Bundle**: Vite/esbuild produces ~60KB gzipped (production)

## 🔗 Resources

- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Vite](https://vitejs.dev)
- [lucide-react Icons](https://lucide.dev)
- [Google Fonts](https://fonts.google.com)

## ✨ Next Steps

1. Add real `logo.png` (32×32) **and** (80×80) variant
2. Add `hero-flowers.png` (96×64) flower image
3. Update video URL if hosting elsewhere
4. Modify heading/quote text for your brand
5. Update social media links (href attributes)
6. Set up analytics/tracking if needed
7. Deploy to Vercel, Netlify, GitHub Pages, or your server

---

**Built with modern web standards. All code is vanilla React—no external UI libraries. Pure Tailwind + custom CSS = Complete control.**
