# Claude Code Project Notes - Universal Template

This file contains helpful information for Claude Code when working on this project.

## Project Information
- **Project Type**: [Web Application Type - e.g., Next.js, React, WordPress, etc.]
- **Client/Business**: [Client Name and Business Type]
- **Framework**: [Framework Version - e.g., Next.js 15.2.4, React 18, etc.]
- **Language**: [Primary Language - TypeScript, JavaScript, etc.]
- **Styling**: [CSS Framework - Tailwind CSS, Material-UI, etc.]
- **UI Components**: [Component Library - Radix UI, Chakra UI, etc.]
- **Deployment**: [Platform - Vercel, Netlify, AWS, etc.]
- **Integration**: [Special integrations - v0.dev, CMS, etc.]

## Common Commands
- **Build**: `[build command]`
- **Dev Server**: `[dev command]`
- **Lint**: `[lint command]`
- **Start Production**: `[start command]`
- **Package Manager**: [npm/yarn/pnpm]
- **Test**: `[test command]`
- **Deploy**: `[deploy command]`

## Project Structure
- **[main folder]/**: [Description of main application folder]
  - Main pages: [list key pages]
  - API routes: [list API endpoints]
  - [Specialized pages]: [any specialized functionality]
- **components/**: Reusable React components
  - UI components in `ui/` subfolder
  - Business-specific components
- **lib/**: Utility functions and data
  - [Key utilities and data files]
- **public/**: Static assets
- **styles/**: Global CSS and styling

## Key Features
- [Feature 1 - e.g., SEO optimized with sitemap generation]
- [Feature 2 - e.g., Dynamic routing and pages]
- [Feature 3 - e.g., Contact forms and user interactions]
- [Feature 4 - e.g., Content management]
- [Feature 5 - e.g., Performance optimizations]

## Dependencies
- [Framework] with [Frontend Library]
- [CSS Framework] with [extensions]
- [UI Component Library]
- [Icon Library]
- [Analytics/Tracking]
- [Language] for type safety
- [Additional key dependencies]

## SEO Strategy & Content Plan

### Target Markets
- **Primary Location**: [City, State/Region]
- **Secondary Locations**: [Additional target areas]
- **Services**: [Primary services offered]
- **Industry**: [Business industry/niche]

### Content Strategy
- Create keyword-optimized content for local SEO
- Target [location] + [service] combinations
- Use SEMRush keyword data for content planning
- Focus on [primary business objectives]

### Target Areas/Keywords From Research
**Primary Service Keywords:**
- "[primary service] near me" (vol: [volume], diff: [difficulty], intent: [intent])
- "[primary service] cost" (vol: [volume], diff: [difficulty], intent: [intent])
- "[primary service] [location]" (vol: [volume], diff: [difficulty], intent: [intent])

**Location-Specific Keywords:**
- "[service] [city]" (vol: [volume], diff: [difficulty], intent: [intent])
- "[service] [neighborhood]" (vol: [volume], diff: [difficulty], intent: [intent])
- "[business type] [location]" (vol: [volume], diff: [difficulty], intent: [intent])

**Supporting Keywords:**
- "[related service/topic]" (vol: [volume], diff: [difficulty], intent: [intent])
- "[informational keyword]" (vol: [volume], diff: [difficulty], intent: [intent])
- "[commercial keyword]" (vol: [volume], diff: [difficulty], intent: [intent])

### Technical SEO Insights
**SEMRush Data:**
- Site Audit Score: [overall score]
- Technical Issues: [number of issues by severity]
- Backlink Profile: [domain authority, referring domains]
- Organic Traffic: [monthly visits, trending]
- Keyword Rankings: [top performing keywords]

**Lighthouse Performance Data:**
- Performance Score: [0-100]
- Accessibility Score: [0-100]
- Best Practices Score: [0-100]
- SEO Score: [0-100]
- Core Web Vitals:
  - First Contentful Paint (FCP): [time]
  - Largest Contentful Paint (LCP): [time]
  - First Input Delay (FID): [time]
  - Cumulative Layout Shift (CLS): [score]

**Google Search Console Data (Optional):**
- Search Performance:
  - Total Clicks: [number]
  - Total Impressions: [number]
  - Average CTR: [percentage]
  - Average Position: [ranking]
- Top Performing Queries: [list with clicks/impressions]
- Page Experience Metrics: [Core Web Vitals status]
- Mobile Usability Issues: [number and types]
- Index Coverage: [valid pages, errors, warnings]

**Technical Issues Identified:**
- [Issue 1]: [Description and priority level]
- [Issue 2]: [Description and priority level]
- [Issue 3]: [Description and priority level]

**Crawlability & Indexing:**
- Pages Indexed: [number]
- Crawl Errors: [number and types]
- Sitemap Status: [status]
- Robots.txt Issues: [any issues]

**Schema Markup (Structured Data):**
- Current Schema Types: [list types implemented]
- Missing Schema Opportunities: LocalBusiness, Service, FAQPage, BreadcrumbList schemas
- Schema Errors: [any validation issues]
- Implementation: Using Next.js Head component for dynamic structured data

**Meta Tags & Head Optimization:**
- Dynamic titles and descriptions optimization
- Open Graph tags implementation
- Twitter cards configuration
- Using Next.js Head and metadata API for dynamic SEO elements

**XML Sitemap Configuration:**
- Auto-generation using next-sitemap package
- Priority and changefreq settings optimization
- Deployed via platform's static file serving

**Robots.txt Optimization:**
- Crawler directives configuration
- AI bot access permissions (GPTBot, Claude, ChatGPT, Perplexity)
- Sitemap location specification
- Using platform's public folder for static file serving

**LLMs.txt Implementation:**
- Comprehensive AI knowledge base file
- Served from platform's public directory
- Optimized for AI bot understanding

**Performance Optimization (Based on Lighthouse & SEMRush Data):**
- Critical CSS Implementation: Inline above-the-fold styles using Next.js styled-jsx or CSS-in-JS with system font fallbacks
- JavaScript Optimization: Next.js automatic code splitting, dynamic imports, and platform's Edge Runtime optimization
- Image Optimization: Next.js Image component with automatic WebP conversion, responsive sizing, and lazy loading
- Font Loading Strategy: Next.js font optimization with preloading, variable fonts, and fallback strategies
- Resource Hints: DNS prefetch, preload directives, connection optimization using Next.js Head component
- Core Web Vitals Optimization: Target LCP < 2.5s, FID < 100ms, CLS < 0.1 based on Lighthouse data
- Performance Budget: Set based on Lighthouse performance score improvements needed

**Mobile & User Experience:**
- Mobile Optimization: Responsive design using Tailwind CSS, mobile-first approach, touch-friendly UI
- Semantic HTML Structure: Proper heading hierarchy, ARIA labels, landmarks for accessibility and SEO
- User Experience Enhancements: CTAs, FAQ sections, service badges, feature lists with Next.js interactive components

**Analytics & Tracking:**
- Platform Analytics Setup: Web Vitals tracking, conversion events, and performance monitoring
- Google Analytics Setup: Complete GA4 implementation with custom events
- Business Information Display: Consistent NAP (Name, Address, Phone), 24/7 messaging, certifications

**Internal Linking:**
- Link Equity Distribution: [analysis]
- Orphaned Pages: [number]
- Broken Internal Links: [number]
- Navigation & Internal Linking: Breadcrumbs using Next.js Link, related services, cross-linking with prefetch optimization

**Competitor Technical Analysis:**
- Top Competitor Performance Scores: [comparison data]
- Technical Gaps vs Competitors: [key differences]
- Opportunities for Technical Advantage: [recommendations]

### Content Templates & Strategy
**Content Length**: [recommended word count] words per post

**Primary Content Strategy:**
- Educational posts targeting "[topic]" keywords
- Local posts for "near me" searches
- Process/service posts for informational searches
- Case studies and examples with local references

**Content Categories:**
- [Category 1]: [neighborhood/location-specific content]
- [Category 2]: [service-focused guides]
- [Category 3]: [industry trend articles]
- [Category 4]: [educational/how-to content]

**Landing Page Strategy:**
- Service-Specific Landing Pages: Create individual pages for each service offering with platform's file-based routing system
- Location-Specific Landing Pages: Build city/area pages with platform's dynamic routing and ISR (Incremental Static Regeneration)
- Special Campaign Pages: Create specific targeted pages using platform's preview deployments for testing
- Local Content Optimization: City-specific content, service areas, emergency emphasis using platform's edge functions for geo-targeting

**Blog Structure Needed:**
- `/[blog-path]/` directory for blog posts
- Dynamic routing: `/[blog-path]/[slug]/page.tsx`
- Blog listing page: `/[blog-path]/page.tsx`
- SEO metadata integration
- Structured data for articles

**Internal Linking Strategy:**
- Link blog posts to main service pages
- Link to location pages for area mentions
- Cross-reference between related services/topics

### Service Page Optimization Goals
**Current Pages**: [list main service pages]
**Objectives:**
- Increase SERP rankings for main keywords
- Optimize existing content for target keywords
- Improve on-page SEO elements
- Add location-specific content sections
- Include FAQ sections targeting question-based searches
- Optimize for "[service] [location]/near me" searches

**Content Creation Workflow:**
- **AUTO-CONTINUE MODE**: Create one piece of content per session, then STOP automatically to reset context
- User will start new session to continue - NO need to type "continue" or wait for approval
- Progress through priority list automatically when new session starts

**Content Creation Priority Order (Highest Opportunity First):**
1. "[keyword 1]" (vol: [volume], diff: [difficulty]) - [intent] - STATUS: [PENDING/COMPLETED]
2. "[keyword 2]" (vol: [volume], diff: [difficulty]) - [intent] - STATUS: [PENDING/COMPLETED]
3. "[keyword 3]" (vol: [volume], diff: [difficulty]) - [intent] - STATUS: [PENDING/COMPLETED]
4. "[keyword 4]" (vol: [volume], diff: [difficulty]) - [intent] - STATUS: [PENDING/COMPLETED]
5. "[keyword 5]" (vol: [volume], diff: [difficulty]) - [intent] - STATUS: [PENDING/COMPLETED]

**Next Phase Options:**
- Target additional keywords from research
- Create location-specific content
- Develop seasonal/trending content
- Focus on technical SEO improvements

## Website Transformation Strategy

### Client Information & Content
**Client Assets & Content (Consolidated):**
- Content: [copy, service descriptions, team info, business hours, pricing, testimonials]
- Brand Assets: [logo, colors, fonts, imagery - consolidated with downloaded assets]
- Unique Value Propositions: [what sets client apart]
- Service Portfolio: [complete service/product listings]

### Client Website for Replication (Source for This Project)
**Primary Reference Site:**
- Live Website Domain: [URL of the website being replicated/improved]
- Project Type: [Greenfield (new site) / Redesign (existing site improvement)]
- AnimaApp Code Exports: [Multiple page exports available]
  - Homepage Export: [AnimaApp export name/ID]
  - About Page Export: [AnimaApp export name/ID]
  - Services Page Export: [AnimaApp export name/ID]
  - Contact Page Export: [AnimaApp export name/ID]
  - Additional Pages: [List other page exports available]

**For Existing Sites (Redesign Projects):**
- Migration Strategy:
  - Content Migration Plan: [how to transfer existing content]
  - SEO Preservation: [maintaining rankings during redesign]
  - User Impact: [minimizing disruption to existing users]

**Site Data Collection (All Projects):**
- Jina AI Content Scraping:
  - Use Jina Reader API to extract structured content from client site
  - Command: `curl -H "Authorization: Bearer [jina-token]" "https://r.jina.ai/[client-url]"`
  - Extract clean text, headings, and content structure
  - Preserve content hierarchy and semantic markup
- Asset Download Strategy:
  - Use curl/wget to download all site assets locally
  - Command pattern: `wget -r -np -k -E -p [client-domain]`
  - Download images, fonts, stylesheets, and other media
  - Create local asset inventory and reference mapping
- Playwright Structure Analysis:
  - Use Playwright to capture DOM structure and interactive elements
  - Script to extract component patterns and layout structures
  - Capture responsive breakpoints and behavior patterns
  - Document dynamic content loading and user interactions

**For New Sites (Greenfield Projects):**
- Content Creation Needs: [all content must be created from scratch]
- SEO Foundation: [building authority from zero]
- Launch Strategy: [go-live planning for new domain]

**Design System Analysis (All Projects):**
- Visual Style: [modern, clean, professional, etc.]
- Component Library: [buttons, cards, forms, navigation patterns]
- Layout Grid: [12-column, flexbox, CSS Grid system]
- Color Palette: [primary, secondary, accent colors from exports]
- Typography Scale: [font families, sizes, weights from code]
- Interactive Elements: [hover states, transitions, animations]

**Code Structure to Implement:**
- Component Architecture: [reusable components identified in exports]
- Page Templates: [layout patterns from different page exports]
- Responsive Breakpoints: [mobile, tablet, desktop patterns]
- CSS Framework: [Tailwind, styled-components, etc. used in exports]

**Asset Management & References:**
- **CRITICAL**: All assets must be referenced locally, never from AnimaApp domains
- Replace all AnimaApp asset URLs with local file paths
- Update image sources from scraped/downloaded assets
- Ensure fonts are self-hosted and locally referenced
- Replace external CDN links with local copies
- Verify no external dependencies on AnimaApp infrastructure

**Content Integration Plan:**
- Replace placeholder content with client-specific information
- Use Jina-scraped content as source material for real content
- Integrate Playwright-captured structure data with AnimaApp design
- Maintain design structure while customizing messaging
- Preserve layout hierarchy and visual balance
- Adapt CTAs and conversion elements for client goals

### Competitor Research & Benchmarking
**Primary Competitor Analysis (AnimaApp Source):**
- Competitor URL: [AnimaApp URL of top competitor]
  - Design Strengths: [what works well]
  - UX Best Practices: [user flow highlights]
  - Content Strategy: [how they present information]
  - Conversion Elements: [effective CTAs, forms, etc.]
  - Design Elements to Incorporate: [specific features to adapt]

**Industry Standard Features:**
- Must-Have Functionality: [essential features for industry]
- Expected User Flows: [standard customer journeys]
- Common Design Patterns: [industry-specific UI conventions]
- Performance Benchmarks: [speed/performance standards]

### Transformation Methodology
**Phase 1: Data Collection & Preparation**
- Run Jina AI content scraping on target website for structured content extraction
- Execute asset download commands to create local asset library
- Run Playwright scripts to capture DOM structure and interactive elements
- Create asset mapping file to reference local versions of all external assets

**Phase 2: AnimaApp Code Integration & Branding**
- Import AnimaApp code exports for each page type (includes all branding/design)
- Replace all AnimaApp domain references with local asset paths
- Extract reusable components from multiple page exports
- Identify common design system patterns across exports
- Set up project structure using exported code as foundation
- Apply client branding (colors, logos, typography already in AnimaApp exports)

**Phase 3: Content & Structure Integration**
- Merge Jina-scraped content from `client-site/scraped-data/jina-content/` with AnimaApp design templates
- Use Playwright structure data to enhance component interactions
- Replace placeholder content with scraped real content
- Adapt messaging to client's brand voice while preserving layout structure
- Integrate client's unique value propositions into established page templates

**Phase 4: Next.js/Vercel Modernization**
- Convert AnimaApp exports to Next.js 15+ architecture
- Implement Vercel/v0 optimizations and best practices
- Add Next.js Image optimization and performance features
- Integrate Vercel Analytics and deployment configuration
- Modernize component architecture with React Server Components
- Implement dynamic routing and API routes as needed

**Phase 5: Performance & SEO Foundation**
- Optimize for Core Web Vitals using Lighthouse data
- Implement technical SEO improvements from SEMRush audit
- Add schema markup and metadata optimization
- Ensure mobile-first responsive design
- Set up sitemap generation and robots.txt
- Complete technical SEO checklist

**Phase 6: Content Engine & Blog Creation**
- Begin keyword-targeted blog post creation workflow
- Use AUTO-CONTINUE MODE for systematic content creation
- Progress through priority keyword list from SEMRush data
- Create service-specific and location-specific landing pages
- Implement internal linking strategy between blog and main site
- Monitor and iterate based on performance data

### Implementation Checklist
**Pre-Development:**
- [ ] Competitor design analysis complete
- [ ] Client content inventory finalized
- [ ] Brand asset collection complete
- [ ] User flow mapping done
- [ ] Technical requirements documented

**Development Phase:**
- [ ] Base template structure implemented
- [ ] Client content integrated
- [ ] Brand styling applied
- [ ] Custom functionality added
- [ ] Responsive design tested

**Optimization Phase:**
- [ ] Performance metrics meet benchmarks
- [ ] SEO implementation complete
- [ ] Conversion optimization tested
- [ ] Cross-browser compatibility verified
- [ ] Accessibility standards met

**Launch Preparation:**
- [ ] Content review and approval
- [ ] Final testing complete
- [ ] Analytics and tracking setup
- [ ] Backup and deployment ready
- [ ] Launch plan executed

### Success Metrics
**Design Improvements:**
- Visual appeal score improvement: [target %]
- User engagement increase: [target metrics]
- Mobile experience enhancement: [specific improvements]

**Performance Gains:**
- Page load speed improvement: [target time]
- Core Web Vitals optimization: [target scores]
- Conversion rate increase: [target %]

**SEO Enhancements:**
- Keyword ranking improvements: [target positions]
- Organic traffic increase: [target %]
- Technical SEO score improvement: [target score]

## Technical Updates Needed
- **robots.txt**: [Update requirements]
- **llms.txt**: [AI crawler optimizations]
- **sitemap.xml**: [Sitemap improvements]
- **Analytics**: [Tracking implementations]
- **Performance**: [Speed optimizations]
- **Security**: [Security enhancements]

## Notes
- [Project-specific important notes]
- [Integration details]
- [Business focus and specializations]
- [Multi-location or specialized service notes]
- [Any unique technical considerations]

# Important Instruction Reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

IMPORTANT: this template should be customized for each project. Replace all bracketed placeholders with project-specific information before use.

# Template Usage Notes
**DO NOT AUTO-COMPACT THIS FILE** - This is a master template designed to be referenced and copied for new projects. Auto-compacting would remove essential template sections and detailed guidance needed for comprehensive project setup. Always use this file as a complete reference document.

## Data Organization Structure
For optimal Claude Code performance, organize project data in the following structure:

```
project-root/
├── CLAUDE.md (this template filled out)
├── claude-data/
│   ├── client-site/
│   │   ├── anima-exports/
│   │   │   ├── homepage-export/ (AnimaApp code export for homepage)
│   │   │   ├── about-page-export/ (AnimaApp code export for about page)
│   │   │   ├── services-export/ (AnimaApp code export for services)
│   │   │   ├── contact-export/ (AnimaApp code export for contact)
│   │   │   └── additional-pages/ (Other page exports)
│   │   ├── scraped-data/
│   │   │   ├── jina-content/ (Jina AI extracted content by page)
│   │   │   ├── downloaded-assets/ (All site assets and brand assets consolidated)
│   │   │   ├── playwright-structure/ (DOM structure and interaction data)
│   │   │   └── asset-mapping.json (Reference mapping for local assets)
│   │   ├── live-site-analysis.md (analysis of live reference website)
│   │   └── implementation-notes.md (how to adapt exports for client)
│   ├── competitor-analysis/
│   │   ├── competitor-anima-export/ (AnimaApp competitor site files)
│   │   └── analysis-notes.md (competitor research and design adaptation notes)
│   ├── seo-data/
│   │   ├── semrush-exports/ (CSV files from SEMRush)
│   │   ├── lighthouse-reports/ (JSON/HTML reports from Lighthouse)
│   │   ├── search-console-exports/ (GSC performance data - optional)
│   │   ├── keyword-research.md (organized keyword data)
│   │   ├── technical-seo-audit.json (comprehensive technical audit results)
│   │   └── competitor-seo-analysis.md (SEO competitive research)
│   └── requirements/
│       ├── project-brief.md (client requirements and goals)
│       ├── feature-requirements.md (specific functionality needs)
│       └── timeline-budget.md (project constraints)
```

**Usage Instructions:**
1. Copy this template to your project as `CLAUDE.md`
2. Create the `claude-data/` folder structure
3. Upload your organized data files
4. Fill in the template placeholders using: "Reference the data in claude-data/ folders to populate [specific sections]"
5. Claude Code will automatically reference the appropriate data files when working on related tasks

This agentic approach allows Claude Code to:
- Auto-populate template sections from organized data
- Reference competitor designs during transformation work  
- Use SEO data for content creation and technical optimization
- Access client assets for brand customization
- Follow requirements without repeated explanations