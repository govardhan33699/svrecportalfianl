# Advanced Customization Guide

## CSS Liquid Glass Deep Dive

### Liquid Glass Light Variant

**Current Configuration:**
```css
.liquid-glass {
  background: rgba(255,255,255,0.01);
  background-blend-mode: luminosity;
  backdrop-filter: blur(4px);
  border: none;
  box-shadow: inset 0 1px 1px rgba(255,255,255,0.1);
}
```

**Adjust Glass Intensity:**
- Increase blur: `backdrop-filter: blur(8px)` → 12px for more frosted effect
- Adjust transparency: `rgba(255,255,255,0.01)` → 0.02 for more opaque
- Change inset shadow: `rgba(255,255,255,0.1)` → 0.2 for stronger depth

### Liquid Glass Strong Variant

**Fine-tuning Heavy Glass:**
```css
.liquid-glass-strong {
  backdrop-filter: blur(50px);  /* Heavy blur for CTAs */
  box-shadow: 4px 4px 4px rgba(0,0,0,0.05), 
              inset 0 1px 1px rgba(255,255,255,0.15);
}
```

**Make More Opaque:**
- Increase background alpha: `rgba(255,255,255,0.01)` → 0.05
- Stronger outer shadow: `4px 4px 4px` → `6px 6px 8px`
- Adjust inset: `0.15` → `0.25`

### Gradient Border Pseudo-Element

The `::before` creates a glowing edge:

```css
.liquid-glass::before {
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.45) 0%,      /* Top brightness */
    rgba(255, 255, 255, 0.15) 20%,
    transparent 40%,
    transparent 60%,
    rgba(255, 255, 255, 0.15) 80%,
    rgba(255, 255, 255, 0.45) 100%     /* Bottom brightness */
  );
  padding: 1.4px;  /* Border thickness */
}
```

**Customize Gradient:**
- ** Thicker border**: `padding: 1.4px` → 2px
- **More glow**: `0.45` → 0.6 (top/bottom)
- **Subtle glow**: `0.45` → 0.3
- **Asymmetric**: Change top vs bottom values

## Tailwind Configuration Tweaks

### Extend Colors

Add custom colors to `tailwind.config.js`:

```js
theme: {
  extend: {
    colors: {
      'glass-light': 'rgba(255,255,255,0.01)',
      'glass-dark': 'rgba(0,0,0,0.1)',
    }
  }
}
```

Use in HTML:
```jsx
<div className="bg-glass-light">...</div>
```

### Custom Spacing

Add custom padding/margin:

```js
spacing: {
  'glass-padding': '1.4px',
  'panel-indent': '4rem',
}
```

### Font Weight Customization

```js
fontWeight: {
  'glass-text': 500,  // Current heading weight
}
```

## Responsive Behavior

### Mobile-First Approach

Current breakpoint: `lg` (1024px)

**To change primary breakpoint:**

Edit component or Tailwind config:

```js
// tailwind.config.js
theme: {
  extend: {
    screens: {
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',      // Current
      'xl': '1280px',
      '2xl': '1536px',
    }
  }
}
```

**For always-visible right panel (mobile):**

Change `hidden lg:flex` to `flex`:

```jsx
<div className="flex w-full lg:w-[48%]">  {/* Mobile visible now */}
```

**For horizontal scroll on mobile:**

```jsx
<div className="flex overflow-x-auto lg:overflow-visible">
```

## Animation Enhancements

### Add More Interactive Effects

**Entrance Animation:**

```css
@layer components {
  .fade-in-up {
    @apply animate-fade-in;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**In Tailwind config:**

```js
animation: {
  'fade-in': 'fadeIn 0.6s ease-out',
}
```

**Use in component:**

```jsx
<h1 className="animate-fade-in">...</h1>
```

### Staggered Animation

For multiple elements:

```css
@keyframes stagger {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}

.pill:nth-child(1) {
  animation: stagger 0.4s 0s ease-out;
}
.pill:nth-child(2) {
  animation: stagger 0.4s 0.1s ease-out;
}
.pill:nth-child(3) {
  animation: stagger 0.4s 0.2s ease-out;
}
```

## Dynamic Theme Support

### Dark/Light Mode Toggle

Add to `tailwind.config.js`:

```js
darkMode: 'class',  // or 'media'
```

Define theme variables:

```css
:root {
  --bg-primary: hsl(0 0% 0%);
  --text-primary: hsl(0 0% 100%);
}

@media (prefers-color-scheme: light) {
  :root {
    --bg-primary: hsl(0 0% 100%);
    --text-primary: hsl(0 0% 0%);
  }
}
```

Use variables in component:

```jsx
<div className="bg-[var(--bg-primary)]">...</div>
```

## Advanced Liquid Glass Effects

### Chromatic Aberration (experimental)

```css
.liquid-glass-advanced {
  backdrop-filter: blur(4px) drop-shadow(0 0 20px rgba(255,255,255,0.1));
}
```

### GPU Acceleration

```css
.liquid-glass {
  transform: translateZ(0);  /* Force GPU rendering */
  will-change: transform;
}
```

### Parallax Scrolling

```jsx
const [scroll, setScroll] = React.useState(0);

useEffect(() => {
  const handleScroll = () => setScroll(window.scrollY);
  window.addEventListener('scroll', handleScroll);
  return () => window.removeEventListener('scroll', handleScroll);
}, []);

<div style={{ transform: `translateY(${scroll * 0.5}px)` }}>
  {/* Parallax content */}
</div>
```

## Performance Optimization Tips

### Reduce Blur for Low-End Devices

```jsx
// Detect if device prefers reduced motion
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

<div className={prefersReduced ? 'backdrop-blur-none' : 'backdrop-blur-lg'}>
```

### Lazy Load Video

```jsx
const videoRef = useRef(null);

useEffect(() => {
  const observer = new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting && videoRef.current) {
      videoRef.current.play();
    }
  });
  observer.observe(videoRef.current);
}, []);
```

### Optimize CSS Delivery

Use critical CSS approach:

```css
/* Inline in <head> */
@media screen and (max-width: 1024px) {
  .right-panel { display: none; }
  .left-panel { width: 100%; }
}
```

## Component Composition Examples

### Create Reusable GlassCard Component

```jsx
function GlassCard({ children, variant = 'light', className = '' }) {
  const variants = {
    light: 'liquid-glass',
    strong: 'liquid-glass-strong',
  };
  
  return (
    <div className={`${variants[variant]} ${className}`}>
      {children}
    </div>
  );
}

// Usage
<GlassCard variant="strong">
  <h2>My Card</h2>
</GlassCard>
```

### Create Icon Button Component

```jsx
function IconButton({ icon: Icon, label, onClick, className = '' }) {
  return (
    <button 
      onClick={onClick}
      className={`icon-container interactive ${className}`}
      title={label}
    >
      <Icon size={20} />
    </button>
  );
}

// Usage
<IconButton icon={Sparkles} label="Account" onClick={handleClick} />
```

### Create Pill Tag Component

```jsx
function PillTag({ text, variant = 'light' }) {
  return (
    <div className={`liquid-glass px-6 py-2 rounded-full interactive ${
      variant === 'strong' ? 'liquid-glass-strong' : ''
    }`}>
      <span className="text-xs text-white/80">{text}</span>
    </div>
  );
}

// Usage
<PillTag text="AI Generation" variant="light" />
```

## Accessibility Enhancements

### Keyboard Navigation

```jsx
<button 
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
  role="button"
  tabIndex={0}
>
  Accessible Button
</button>
```

### ARIA Labels

```jsx
<button className="icon-container" aria-label="Open main menu">
  <Menu size={20} />
</button>
```

### Focus Visibility

```css
@layer components {
  .interactive:focus-visible {
    @apply outline-2 outline-offset-2 outline-white/50;
  }
}
```

### Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Testing

### Snapshot Testing

```jsx
import { render } from '@testing-library/react';
import BloomHero from '../BloomHero';

test('renders without crashing', () => {
  const { container } = render(<BloomHero />);
  expect(container).toMatchSnapshot();
});
```

### Visual Regression Testing

Use services like:
- Percy.io
- Chromatic
- BrowserStack

## Version Control & CI/CD

### GitHub Actions Example

```yaml
name: Build & Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/
```

---

**Ready to push Bloom beyond the default design. Experiment with these patterns and make the landing page truly unique!**
