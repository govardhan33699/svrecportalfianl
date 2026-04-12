# 🌸 Bloom Landing Page — Quick Start

## What You Just Got

A **complete, production-ready React landing page** for Bloom — an AI-powered plant/floral design platform with:

- ✨ **Liquid Glass Morphism** visual effect
- 🎥 **Full-screen video background** (autoplaying, looping)
- 📱 **Responsive two-panel layout** (52% left / 48% right)
- 🎨 **Grayscale color palette** (HSL-based)
- 🔤 **Google Fonts** (Poppins + Source Serif 4)
- 🎯 **Interactive elements** with smooth hover/active states
- 🚀 **Zero-config deployment** ready for Vercel/Netlify

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Dev Server
```bash
npm run dev
```
Opens **http://localhost:5173** automatically

### 3. (Optional) Build for Production
```bash
npm run build
```
Creates optimized `dist/` folder

---

## 📋 What's Included

```
src/
├── main.jsx              ← React entry point
├── BloomHero.jsx         ← Main component (all layout & content)
└── index.css             ← Tailwind + liquid glass styles

index.html               ← HTML entry + Google Fonts CDN

Configuration Files:
├── tailwind.config.js
├── vite.config.js
├── postcss.config.js
├── jsconfig.json
├── .eslintrc.cjs
└── .prettierrc
```

---

## 📝 Key Features

### Layout
- **Left Panel (52%)**: Navigation, hero content, quote
- **Right Panel (48%)**: Social icons, community card, feature showcase
- **Mobile**: Stacks to single column (hidden right panel)
- **Video Background**: Full viewport, z-index 0, content floats above

### Components
- **Navigation**: Logo + "bloom" text + Menu button
- **Hero**: Logo (80×80), heading with mixed serif typography, CTA button
- **Pill Tags**: "Artistic Gallery", "AI Generation", "3D Structures"
- **Quote Section**: "VISIONARY DESIGN" label + serif italic quote
- **Social Bar**: Twitter, LinkedIn, Instagram icons + Account button
- **Feature Cards**: Processing, Growth Archive, Advanced Plant Sculpting

### Styling
- **Glass Effect**: Light (blur 4px) and strong (blur 50px) variants
- **Colors**: Pure grayscale (HSL 0 0% X%) with opacity hierarchy
- **Typography**: Poppins (display), Source Serif 4 (italic only)
- **Interactions**: Hover scale-105, active scale-95, smooth transitions

---

## 🎨 Customize

### 1. Add Real Images
Replace placeholders in `src/BloomHero.jsx`:
- **Logo**: Add `logo.png` (32×32 nav, 80×80 hero)
- **Flower**: Add `hero-flowers.png` (96×64 feature card)

### 2. Change Video
Update URL in `BloomHero.jsx`:
```jsx
src="https://your-video-url.mp4"
```

### 3. Edit Text
Find and replace in `BloomHero.jsx`:
- Heading: "Innovating the spirit of bloom AI"
- Quote: "We imagined a realm with no ending."
- Author: "MARCUS AURELIO"

### 4. Update Social Links
Find social buttons in `BloomHero.jsx` and add `href` attributes:
```jsx
<a href="https://twitter.com/your-handle" className="...">
  <Twitter size={18} />
</a>
```

---

## 📚 Documentation

- **README.md** — Full overview of features and structure
- **IMPLEMENTATION.md** — Detailed setup, components, customization
- **DEPLOYMENT.md** — Deploy to Vercel, Netlify, traditional servers
- **ADVANCED.md** — Deep CSS tweaks, animations, components
- **FILE_STRUCTURE.md** — Complete file organization reference

---

## 🚀 Deploy

### Quickest: Vercel
1. Push to GitHub
2. Go to vercel.com → Connect repo
3. Click "Deploy" — done in 60 seconds

### Alternative: Netlify
1. Connect GitHub
2. Build: `npm run build`
3. Publish: `dist/`

### Traditional Server
```bash
npm run build
scp -r dist/* user@server.com:/var/www/html/
```

See **DEPLOYMENT.md** for detailed instructions.

---

## ✅ Pre-Launch Checklist

- [ ] Install dependencies: `npm install`
- [ ] Test locally: `npm run dev`
- [ ] Add real logo images
- [ ] Add real flower image
- [ ] Update heading/quote text
- [ ] Add social media links
- [ ] Build: `npm run build`
- [ ] Deploy to Vercel/Netlify or your server

---

## 🎯 What to Know

### Design System
- **Only grayscale colors** — Text: white/white-80/white-60/white-50
- **No border classes** — Glass `::before` pseudo-element creates borders
- **Two liquid glass variants** — Light (4px blur) & Strong (50px blur)
- **All interactions interactive** — Hover: scale-105, active: scale-95

### Tech Stack
- **React 18.2** — Component framework
- **Tailwind CSS 3.3** — Utility-first styling
- **Vite 4.4** — Lightning-fast dev server & builder
- **lucide-react** — Icon library (20+ icons included)
- **Google Fonts** — Poppins + Source Serif 4

### Browser Support
✅ Chrome 90+, Firefox 88+, Safari 14+, Edge 90+, Mobile browsers
❌ IE 11 (not supported)

---

## 🆘 Troubleshooting

**Video won't play?**
- Check URL is correct & accessible
- Ensure video codec is H.264 MP4
- On iOS, user may need to interact first

**Fonts not loading?**
- Check internet connection (Google Fonts CDN)
- Verify `index.html` has font link
- Clear browser cache

**Build fails?**
- Run `npm install` again
- Ensure Node.js version ≥ 16
- Check console errors: `npm run build`

**Component not rendering?**
- Ensure `npm install` completed
- Check `npm run dev` server is running
- Open DevTools (F12) for errors

---

## 📞 Next Steps

1. **Run locally**: `npm run dev`
2. **Add images**: Place logo.png & hero-flowers.png in `public/assets/`
3. **Customize**: Edit text, links, colors in `src/BloomHero.jsx`
4. **Build**: `npm run build` when ready
5. **Deploy**: Push to Vercel/Netlify or upload `dist/` to server

---

## ✨ You're All Set!

Everything is ready to go. Start with `npm install` and `npm run dev` — enjoy your Bloom landing page! 🌸

**Questions?** Check README.md, IMPLEMENTATION.md, or ADVANCED.md for detailed guides.

**Ready to deploy?** See DEPLOYMENT.md for step-by-step instructions.
