# Asset Management Best Practices

This project implements a hybrid asset management strategy optimized for performance and maintainability.

## Architecture Overview

### Static Assets (`/public/assets/`)
**Served directly by Next.js/Vercel CDN**

```
/public/assets/
├── images/
│   └── sean-profile.png          # Profile photo (optimized, rarely changes)
├── logos/
│   └── lead-ventures.png         # Company logos (brand assets, static)
└── icons/
    ├── insurance.png             # Service category icons
    ├── medicare.png
    ├── mortgage.png
    └── solar.png
```

**Use cases:**
- Brand logos and identity assets
- Profile photos and team images  
- UI icons and illustrations
- Background images for layouts
- Any assets that rarely change

**Benefits:**
- ✅ Cached at build time by Vercel CDN
- ✅ Optimized with Next.js Image component
- ✅ Version controlled with code
- ✅ Zero database overhead

### Dynamic Content (Payload CMS + Vercel Blob)
**Managed through admin panel, stored in cloud**

**Use cases:**
- Blog post featured images
- User-generated content uploads
- Gallery images managed by admins
- Documents and downloadable assets
- Any content updated through CMS

**Benefits:**
- ✅ Delivered via Vercel Blob CDN
- ✅ No build process required for updates
- ✅ Admin-friendly upload interface
- ✅ Automatic image resizing and optimization

## Implementation Details

### Static Asset Usage

```tsx
// Homepage hero - uses static profile image
<Image
  src="/assets/images/sean-profile.png"
  alt="Sean Reed McGee"
  width={200}
  height={200}
  className="rounded-full"
/>

// Company logos - static brand assets
<Image
  src="/assets/logos/lead-ventures.png"
  alt="Lead Ventures"
  width={60}
  height={60}
  className="object-contain"
/>
```

### Dynamic Content via CMS

```tsx
// Blog post images - managed through Payload CMS
const post = await payload.findByID({
  collection: 'posts',
  id: postId
})

<Image
  src={post.featuredImage.url}  // Served from Vercel Blob
  alt={post.featuredImage.alt}
  width={800}
  height={400}
/>
```

### Configuration

#### Payload CMS Cloud Storage
```typescript
// payload.config.ts
plugins: [
  cloudStorage({
    collections: {
      media: {
        adapter: vercelBlobStorage({
          token: process.env.BLOB_READ_WRITE_TOKEN,
        }),
      },
    },
  }),
],
```

#### Environment Variables
```bash
# .env
BLOB_READ_WRITE_TOKEN=your-vercel-blob-token
DATABASE_URI=mongodb://localhost:27017/sean-reed-mcgee
PAYLOAD_SECRET=your-secret-key
```

## Migration Strategy

### From WordPress Assets
1. **Analyze content types** - Identify static vs dynamic assets
2. **Download assets** - Preserve original directory structure temporarily
3. **Categorize assets** - Sort into static vs CMS-managed
4. **Optimize static assets** - Move to `/public/assets/` with clean naming
5. **Configure cloud storage** - Set up Vercel Blob for dynamic content

### Migration Scripts
```bash
# Migrate with hybrid asset strategy
npm run migrate:cloud

# Legacy migration with all assets in CMS (not recommended)
npm run migrate:media
```

## Performance Metrics

### Static Assets
- **Cache**: Permanent (until deployment)
- **CDN**: Vercel Edge Network
- **Optimization**: Next.js automatic optimization
- **Loading**: Instant on repeat visits

### Dynamic Assets  
- **Cache**: Smart CDN caching
- **CDN**: Vercel Blob global distribution
- **Optimization**: Automatic image processing
- **Loading**: Fast with proper headers

## Content Strategy

### Homepage Structure
```
Hero Section:
├── Profile image (static)      → /assets/images/sean-profile.png
├── Background (static)         → CSS/Tailwind
└── Copy (CMS)                  → About collection

Business Portfolio:
├── Lead Ventures logo (static) → /assets/logos/lead-ventures.png
├── Service icons (static)      → /assets/icons/*.png
└── Descriptions (CMS)          → Companies collection

Blog Section:
├── Post content (CMS)          → Posts collection  
├── Featured images (CMS)       → Vercel Blob storage
└── Layout assets (static)      → /assets/
```

### Admin Panel Workflow
1. **Static assets** - Developer updates, committed to repo
2. **Dynamic content** - Admin manages through Payload CMS interface
3. **Blog images** - Uploaded through rich text editor, stored in Blob
4. **Company data** - Updated through CMS, logos remain static

## Deployment

### Vercel Configuration
- Static assets served from Edge Network
- Blob storage integrated automatically  
- Image optimization enabled
- ISR for CMS content

### Best Practices
- ✅ Keep brand assets static for consistency
- ✅ Use CMS for content that changes frequently
- ✅ Optimize images before committing static assets
- ✅ Set up proper alt text for all images
- ✅ Monitor CDN performance and costs

This hybrid approach provides the best of both worlds: blazing-fast static assets with flexible content management for dynamic needs.