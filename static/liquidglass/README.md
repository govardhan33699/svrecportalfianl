# Bloom – AI-Powered Plant & Floral Design Platform

A full-screen hero landing page featuring liquid glass morphism aesthetic over a looping video background.

## Features

- **Full-Screen Video Background**: Autoplaying, looping, muted video with `object-cover`
- **Liquid Glass Morphism**: Two-tier glass effect with backdrop blur and gradient borders
- **Responsive Two-Panel Layout**: 52% left (content) / 48% right (features) on desktop
- **Grayscale Color Palette**: Pure HSL grayscale with text hierarchy
- **Typography**: Poppins for display/body, Source Serif 4 for italic accents
- **Interactive Elements**: Smooth hover/active scales with `lucide-react` icons

## Project Structure

```
liquidglass/
├── index.html                 # HTML entry point
├── package.json              # Dependencies
├── tailwind.config.js        # Tailwind configuration
├── postcss.config.js         # PostCSS configuration
├── vite.config.js            # Vite build configuration
├── .gitignore                # Git ignore rules
└── src/
    ├── main.jsx              # React entry point
    ├── BloomHero.jsx         # Main hero component
    └── index.css             # Tailwind + liquid glass styles
```

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

Opens at `http://localhost:5173` with hot module reloading.

## Build

```bash
npm run build
```

Generates optimized production bundle in `dist/`.

## Preview

```bash
npm run preview
```

Preview the production build locally.

## Design System

### Liquid Glass Variants

- `.liquid-glass`: Light variant with `backdrop-blur(4px)` and subtle gradient border
- `.liquid-glass-strong`: Heavy variant with `backdrop-blur(50px)` for CTAs and panels

### Color Hierarchy

- `text-white`: 100% opacity
- `text-white/80`: 80% opacity (secondary text)
- `text-white/60`: 60% opacity (tertiary)
- `text-white/50`: 50% opacity (labels)

### Typography

- **Display/Body**: Poppins (font-weight: 500)
- **Italic/Emphasis**: Source Serif 4 (inside `<em>`, `<i>`, `.italic`)
- **Headings**: `text-6xl` / `text-7xl` with `tracking-[-0.05em]`

### Spacing & Sizing

- **Border radius**: `1rem` (--radius)
- **Icon containers**: `w-8 h-8` rounded-full `bg-white/10`
- **Panels**: Left `w-[52%]`, Right `w-[48%]` (desktop only)

## Layout Breakdown

### Left Panel

- Navigation with logo + menu button
- Hero center: Logo, heading, CTA, feature pills
- Bottom quote section with author attribution

### Right Panel (Desktop Only)

- Top social bar (Twitter, LinkedIn, Instagram)
- Community ecosystem card
- Bottom feature section with processing/growth cards
- Advanced plant sculpting feature card with image placeholder

## Video Background

The background video is served from CloudFront and automatically:
- Plays on mount
- Loops infinitely
- Mutes for better UX
- Covers the entire viewport

Replace the URL in `BloomHero.jsx` to use a different video.

## Interactive Elements

All interactive elements use:
- `hover:scale-105` for scale-up effect
- `active:scale-95` for press feedback
- `transition-transform` for smooth animations
- `hover:text-white/80` for text/icon color transitions

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (responsive)

## Fonts

Google Fonts imported automatically in `index.html`:
- **Poppins**: Display and body text
- **Source Serif 4**: Italic/serif accents

## Notes

- No colored accents—pure grayscale aesthetic
- All text uses HSL grayscale notation (`0 0% X%`)
- Pseudo-elements (`::before`) create gradient borders for glass effect
- Mobile hides right panel via `hidden lg:flex`
- Logo placeholder uses simple "B" character (replace with actual logo image)

---

**Built with React, Tailwind CSS, and Vite for a modern, performant landing experience.**
