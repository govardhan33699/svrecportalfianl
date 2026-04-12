# Asset Placeholders

Place the following image files in this directory:

## Required Images

- **logo.png** (32×32)
  - Used in navigation bar
  - Should be a transparent PNG or simple icon
  - Current implementation uses a placeholder "B" letter

- **hero-flowers.png** (96×64)
  - Used in the "Advanced Plant Sculpting" feature card
  - Should be a flower/plant image thumbnail
  - Current implementation uses a gray placeholder box

## Notes

- All images should be optimized (compress with TinyPNG or similar)
- Use PNG format for transparent backgrounds
- For video posterframe, use JPG if needed
- Update paths in `BloomHero.jsx` when adding real assets

## Placeholder Usage

Current component uses:
- `<div className="w-8 h-8 bg-white/20 rounded-lg">B</div>` for logo placeholder
- `<div className="w-full h-16 bg-white/10">Flower Image</div>` for hero-flowers placeholder

Replace these with actual `<img />` tags when assets are ready:

```jsx
<img src="/assets/logo.png" alt="Bloom Logo" className="w-8 h-8" />
<img src="/assets/hero-flowers.png" alt="Flower Sculpture" className="w-full h-16 rounded-2xl object-cover" />
```
