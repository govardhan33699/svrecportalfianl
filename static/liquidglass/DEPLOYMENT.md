# Deployment Guide

## Quick Deploy Options

### Vercel (Recommended for React + Vite)

1. Push code to GitHub
2. Visit [vercel.com](https://vercel.com)
3. Click "New Project" → Select repository
4. Vercel auto-detects Vite and builds correctly
5. Environment variables: Add `.env.local` settings in Vercel dashboard
6. Deploy: Click "Deploy" — live in ~60 seconds

**Environment**: Leave defaults (Vercel detects npm scripts)

### Netlify

1. Connect GitHub repository
2. Build command: `npm run build`
3. Publish directory: `dist`
4. Deploy: Automatic on push to main

**Add Environment Variables**:
- Netlify Dashboard → Site settings → Build & deploy → Environment
- Add `VITE_VIDEO_URL` and any other vars

### GitHub Pages

1. Update `vite.config.js`:
```js
export default defineConfig({
  base: '/liquidglass/',  // if hosting in subdirectory
  plugins: [react()],
})
```

2. Build:
```bash
npm run build
```

3. Push `dist/` folder to `gh-pages` branch:
```bash
git subtree push --prefix dist origin gh-pages
```

### Traditional Server (Apache/Nginx)

1. Build locally:
```bash
npm run build
```

2. Upload `dist/` contents to server root:
```bash
scp -r dist/* user@server.com:/var/www/html/
```

3. Nginx config:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

4. Apache config (`.htaccess`):
```apache
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /
    RewriteRule ^index\.html$ - [L]
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule . /index.html [L]
</IfModule>
```

## Pre-Deployment Checklist

- [ ] Replace logo placeholder with actual `logo.png` (32×32 and 80×80)
- [ ] Replace flower placeholder with actual `hero-flowers.png` (96×64)
- [ ] Update video URL (ensure it continues to work on production domain)
- [ ] Update heading/quote text for your brand
- [ ] Add social media links (update href in icon buttons)
- [ ] Test on multiple browsers (Chrome, Firefox, Safari, Mobile)
- [ ] Verify video background plays without autoplay issues on iOS
- [ ] Set up analytics (Google Analytics, Vercel Analytics, etc.)
- [ ] Enable HTTPS/SSL
- [ ] Set up custom domain
- [ ] Test form submissions (if adding contact forms later)
- [ ] Check Core Web Vitals (PageSpeed Insights)
- [ ] Set up redirects if migrating from old domain

## Performance Optimization

### Image Optimization

```bash
# Install ImageOptim or use online tools
# Compress logo and flower images before committing
```

### Font Loading

Fonts load from Google CDN in `index.html`. Add `font-display: swap` for faster rendering:

```html
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Source+Serif+4:ital@0;1&display=swap" rel="stylesheet">
```

### Video Optimization

- Use H.264 MP.4 codec (best browser support)
- Compress with FFmpeg:
```bash
ffmpeg -i input.mp4 -vcodec libx264 -crf 28 output.mp4
```
- Consider WebM for additional compression on supported browsers
- Host on CDN (CloudFront, Cloudflare, Bunny CDN)

### CSS/JS Minification

Vite automatically minifies production builds. No additional setup needed.

## Domain & SSL

### Set Custom Domain

**Vercel**: Project settings → Domains → Add domain
**Netlify**: Domain settings → Add domain
**GitHub Pages**: Settings → Pages → Custom domain

### Enable HTTPS

- Vercel/Netlify: Automatic with Let's Encrypt
- Traditional servers: Use Certbot:
```bash
sudo certbot certonly --webroot -w /var/www/html -d yourdomain.com
```

## Monitoring & Maintenance

### Monitor Performance

- [Google PageSpeed Insights](https://pagespeed.web.dev)
- [WebPageTest](https://www.webpagetest.org)
- [Lighthouse](https://chromedevtools.io/lighthouse)

### Real-time Metrics

- Vercel Analytics: Automatic for free tier+
- Netlify Analytics: Optional paid feature
- Google Analytics: Add to `index.html`

### Update Deployment

After making changes:

```bash
git add .
git commit -m "Update hero content"
git push origin main
```

Platforms auto-redeploy on push.

## Rollback to Previous Version

**Vercel/Netlify**: Dashboard → Deployments → Select previous → Redeploy

**Custom server**: Keep `dist-backup/` folder, restore if needed

## Troubleshooting Deployment

### White screen on load
- Check browser console for errors
- Verify all assets load (open DevTools → Network tab)
- Ensure video URL is accessible from production domain

### Video background not playing
- Check CORS headers on video CDN
- iOS may require user interaction—test on device
- Verify video codec (H.264 MP4 most compatible)

### Fonts not loading
- Verify Google Fonts CDN link works
- Check `font-display` policy
- Test with cache disabled (DevTools → Network → Disable cache)

### Build fails on CI/CD
- Ensure Node.js version ≥ 16
- Run `npm install` before `npm run build`
- Check `.eslintrc.cjs` for parsing errors

---

**Deployment ready! Choose your platform, follow steps, and go live in minutes.**
