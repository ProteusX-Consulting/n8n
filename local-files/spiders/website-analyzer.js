const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

class WebsiteAnalyzer {
  constructor() {
    this.browser = null;
    this.page = null;
    this.analysisData = {
      metadata: {},
      designTokens: {
        colors: new Set(),
        fonts: new Set(),
        spacing: new Set(),
        borderRadius: new Set(),
        boxShadows: new Set(),
        gradients: new Set()
      },
      layout: {},
      elements: [],
      assets: {
        images: [],
        fonts: [],
        stylesheets: [],
        scripts: [],
        backgroundImages: []
      },
      componentPatterns: [],
      responsive: {}
    };
  }

  log(message) {
    console.log(`[${new Date().toISOString()}] ${message}`);
  }

  async initialize() {
    this.log('Initializing Playwright browser...');
    this.browser = await chromium.launch({ headless: true });
  }

  async analyzePage(url, viewport = { width: 1920, height: 1080 }) {
    this.log(`Analyzing ${url} at ${viewport.width}x${viewport.height}`);
    
    const context = await this.browser.newContext({ viewport });
    this.page = await context.newPage();
    
    // Enable network tracking for performance metrics
    await this.page.route('**/*', route => {
      route.continue();
    });

    const startTime = Date.now();
    
    try {
      await this.page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      const loadTime = Date.now() - startTime;
      
      this.log('Page loaded, starting analysis...');
      
      // Collect all analysis data
      await this.collectMetadata(url, viewport, loadTime);
      await this.collectPerformanceMetrics();
      await this.collectDesignTokens();
      await this.collectElementData();
      await this.collectLayoutStructure();
      await this.collectAssets();
      await this.identifyComponentPatterns();
      
    } catch (error) {
      this.log(`Error analyzing page: ${error.message}`);
      throw error;
    } finally {
      await context.close();
    }
  }

  async collectMetadata(url, viewport, loadTime) {
    this.log('Collecting metadata...');
    
    const elementCount = await this.page.evaluate(() => {
      return document.querySelectorAll('*').length;
    });

    const domDepth = await this.page.evaluate(() => {
      let maxDepth = 0;
      function getDepth(element, depth = 0) {
        maxDepth = Math.max(maxDepth, depth);
        for (let child of element.children) {
          getDepth(child, depth + 1);
        }
      }
      getDepth(document.body);
      return maxDepth;
    });

    this.analysisData.metadata = {
      url,
      timestamp: new Date().toISOString(),
      viewport,
      loadTime,
      elementCount,
      domDepth,
      userAgent: await this.page.evaluate(() => navigator.userAgent),
      title: await this.page.title(),
      description: await this.page.$eval('meta[name="description"]', el => el.content).catch(() => null)
    };
  }

  async collectPerformanceMetrics() {
    this.log('Collecting performance metrics...');
    
    const metrics = await this.page.evaluate(() => {
      const perfData = performance.getEntriesByType('navigation')[0];
      return {
        domContentLoaded: perfData?.domContentLoadedEventEnd - perfData?.navigationStart || 0,
        loadComplete: perfData?.loadEventEnd - perfData?.navigationStart || 0,
        firstPaint: performance.getEntriesByType('paint').find(p => p.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByType('paint').find(p => p.name === 'first-contentful-paint')?.startTime || 0,
        resourceCount: performance.getEntriesByType('resource').length
      };
    });

    this.analysisData.metadata.performance = metrics;
  }

  async collectDesignTokens() {
    this.log('Extracting design tokens...');
    
    const tokens = await this.page.evaluate(() => {
      const elements = document.querySelectorAll('*');
      const tokens = {
        colors: new Set(),
        fonts: new Set(),
        spacing: new Set(),
        borderRadius: new Set(),
        boxShadows: new Set(),
        gradients: new Set()
      };

      elements.forEach(el => {
        const computed = window.getComputedStyle(el);
        
        // Colors
        const color = computed.color;
        const backgroundColor = computed.backgroundColor;
        const borderColor = computed.borderColor;
        if (color && color !== 'rgba(0, 0, 0, 0)') tokens.colors.add(color);
        if (backgroundColor && backgroundColor !== 'rgba(0, 0, 0, 0)') tokens.colors.add(backgroundColor);
        if (borderColor && borderColor !== 'rgba(0, 0, 0, 0)') tokens.colors.add(borderColor);

        // Fonts
        const fontFamily = computed.fontFamily;
        const fontSize = computed.fontSize;
        const fontWeight = computed.fontWeight;
        if (fontFamily) tokens.fonts.add(`${fontFamily} ${fontWeight}`);

        // Spacing
        const margin = computed.margin;
        const padding = computed.padding;
        const marginValues = [computed.marginTop, computed.marginRight, computed.marginBottom, computed.marginLeft];
        const paddingValues = [computed.paddingTop, computed.paddingRight, computed.paddingBottom, computed.paddingLeft];
        
        marginValues.forEach(val => val && val !== '0px' && tokens.spacing.add(val));
        paddingValues.forEach(val => val && val !== '0px' && tokens.spacing.add(val));

        // Border radius
        const borderRadius = computed.borderRadius;
        if (borderRadius && borderRadius !== '0px') tokens.borderRadius.add(borderRadius);

        // Box shadows
        const boxShadow = computed.boxShadow;
        if (boxShadow && boxShadow !== 'none') tokens.boxShadows.add(boxShadow);

        // Gradients
        const backgroundImage = computed.backgroundImage;
        if (backgroundImage && backgroundImage.includes('gradient')) {
          tokens.gradients.add(backgroundImage);
        }
      });

      return {
        colors: Array.from(tokens.colors),
        fonts: Array.from(tokens.fonts),
        spacing: Array.from(tokens.spacing),
        borderRadius: Array.from(tokens.borderRadius),
        boxShadows: Array.from(tokens.boxShadows),
        gradients: Array.from(tokens.gradients)
      };
    });

    this.analysisData.designTokens = tokens;
  }

  async collectElementData() {
    this.log('Collecting detailed element data...');
    
    const elements = await this.page.evaluate(() => {
      const allElements = Array.from(document.querySelectorAll('*'));
      const elementData = [];

      allElements.forEach((el, index) => {
        const rect = el.getBoundingClientRect();
        const computed = window.getComputedStyle(el);
        
        // Create complete CSS object
        const cssStyles = {};
        for (let i = 0; i < computed.length; i++) {
          const prop = computed[i];
          cssStyles[prop] = computed.getPropertyValue(prop);
        }

        // Generate unique selector
        const generateSelector = (element) => {
          if (element.id) return `#${element.id}`;
          if (element === document.body) return 'body';
          
          let path = [];
          while (element && element.nodeType === Node.ELEMENT_NODE) {
            let selector = element.nodeName.toLowerCase();
            if (element.className && typeof element.className === 'string') {
              selector += '.' + element.className.split(' ').filter(c => c).join('.');
            }
            path.unshift(selector);
            element = element.parentNode;
          }
          return path.join(' > ');
        };

        elementData.push({
          index,
          tagName: el.tagName.toLowerCase(),
          id: el.id || null,
          classes: el.className && typeof el.className === 'string' ? el.className.split(' ').filter(c => c) : [],
          textContent: el.textContent ? el.textContent.trim().substring(0, 200) : null,
          geometry: {
            x: rect.x,
            y: rect.y,
            width: rect.width,
            height: rect.height,
            top: rect.top,
            right: rect.right,
            bottom: rect.bottom,
            left: rect.left
          },
          cssStyles,
          selector: generateSelector(el),
          parentIndex: el.parentElement ? Array.from(document.querySelectorAll('*')).indexOf(el.parentElement) : null,
          childCount: el.children.length,
          attributes: Array.from(el.attributes).reduce((attrs, attr) => {
            attrs[attr.name] = attr.value;
            return attrs;
          }, {})
        });
      });

      return elementData;
    });

    this.analysisData.elements = elements;
  }

  async collectLayoutStructure() {
    this.log('Analyzing layout structure...');
    
    const layout = await this.page.evaluate(() => {
      const body = document.body;
      const html = document.documentElement;
      
      // Detect main layout sections
      const sections = {
        header: document.querySelector('header') || document.querySelector('[role="banner"]'),
        nav: document.querySelector('nav') || document.querySelector('[role="navigation"]'),
        main: document.querySelector('main') || document.querySelector('[role="main"]'),
        aside: document.querySelector('aside') || document.querySelector('[role="complementary"]'),
        footer: document.querySelector('footer') || document.querySelector('[role="contentinfo"]')
      };

      const sectionInfo = {};
      Object.entries(sections).forEach(([key, element]) => {
        if (element) {
          const rect = element.getBoundingClientRect();
          const computed = window.getComputedStyle(element);
          sectionInfo[key] = {
            exists: true,
            dimensions: { width: rect.width, height: rect.height },
            position: { x: rect.x, y: rect.y },
            display: computed.display,
            position: computed.position
          };
        } else {
          sectionInfo[key] = { exists: false };
        }
      });

      // Detect grid and flexbox usage
      const layoutTypes = {
        grid: document.querySelectorAll('[style*="grid"], [class*="grid"]').length,
        flex: document.querySelectorAll('[style*="flex"], [class*="flex"]').length
      };

      return {
        pageHeight: Math.max(body.scrollHeight, html.scrollHeight),
        pageWidth: Math.max(body.scrollWidth, html.scrollWidth),
        sections: sectionInfo,
        layoutTypes,
        scrollable: body.scrollHeight > window.innerHeight
      };
    });

    this.analysisData.layout = layout;
  }

  async collectAssets() {
    this.log('Collecting asset inventory...');
    
    const assets = await this.page.evaluate(() => {
      const images = Array.from(document.querySelectorAll('img')).map(img => {
        const rect = img.getBoundingClientRect();
        return {
          src: img.src,
          alt: img.alt || null,
          width: rect.width,
          height: rect.height,
          naturalWidth: img.naturalWidth,
          naturalHeight: img.naturalHeight,
          loading: img.loading || 'eager'
        };
      });

      const stylesheets = Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(link => ({
        href: link.href,
        media: link.media || 'all',
        disabled: link.disabled
      }));

      const scripts = Array.from(document.querySelectorAll('script[src]')).map(script => ({
        src: script.src,
        async: script.async,
        defer: script.defer,
        type: script.type || 'text/javascript'
      }));

      // Find background images
      const backgroundImages = [];
      document.querySelectorAll('*').forEach(el => {
        const computed = window.getComputedStyle(el);
        const bgImage = computed.backgroundImage;
        if (bgImage && bgImage !== 'none' && bgImage.includes('url(')) {
          const match = bgImage.match(/url\(["']?([^"')]+)["']?\)/);
          if (match) {
            backgroundImages.push({
              url: match[1],
              element: el.tagName.toLowerCase(),
              selector: el.id ? `#${el.id}` : (el.className && typeof el.className === 'string') ? `.${el.className.split(' ')[0]}` : el.tagName.toLowerCase()
            });
          }
        }
      });

      return { images, stylesheets, scripts, backgroundImages, fonts: [] };
    });

    this.analysisData.assets = assets;
  }

  async identifyComponentPatterns() {
    this.log('Identifying component patterns...');
    
    const patterns = await this.page.evaluate(() => {
      const components = new Map();
      
      // Common component selectors
      const componentSelectors = [
        'button', '[class*="button"]', '[class*="btn"]',
        'card', '[class*="card"]',
        '[class*="nav"]', 'nav li',
        '[class*="modal"]', '[class*="dialog"]',
        '[class*="form"]', 'form',
        '[class*="header"]', '[class*="footer"]',
        '[class*="item"]', '[class*="component"]'
      ];

      componentSelectors.forEach(selector => {
        try {
          const elements = document.querySelectorAll(selector);
          if (elements.length > 1) {
            const componentName = selector.replace(/[\[\]"*=]/g, '').replace(/class/, '');
            
            const variations = Array.from(elements).map((el, index) => {
              const rect = el.getBoundingClientRect();
              const computed = window.getComputedStyle(el);
              
              return {
                index,
                classes: el.className && typeof el.className === 'string' ? el.className.split(' ') : [],
                dimensions: { width: rect.width, height: rect.height },
                textContent: el.textContent ? el.textContent.trim().substring(0, 50) : null,
                backgroundColor: computed.backgroundColor,
                color: computed.color
              };
            });

            components.set(componentName, {
              selector,
              count: elements.length,
              variations
            });
          }
        } catch (e) {
          // Skip invalid selectors
        }
      });

      return Array.from(components.entries()).map(([name, data]) => ({
        name,
        ...data
      }));
    });

    this.analysisData.componentPatterns = patterns;
  }

  async analyzeResponsive(url) {
    this.log('Analyzing responsive behavior...');
    
    const viewports = [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1920, height: 1080 }
    ];

    const responsiveData = {};

    for (const viewport of viewports) {
      this.log(`Testing ${viewport.name} viewport...`);
      await this.analyzePage(url, viewport);
      
      responsiveData[viewport.name] = {
        viewport,
        elementCount: this.analysisData.elements.length,
        layoutStructure: this.analysisData.layout,
        designTokens: this.analysisData.designTokens
      };
    }

    this.analysisData.responsive = responsiveData;
  }

  async saveResults(filename = null) {
    if (!filename) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const url = new URL(this.analysisData.metadata.url);
      const domain = url.hostname;
      
      // Create output directory structure
      const outputDir = path.join(__dirname, '..', 'web-output', domain);
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }
      
      filename = path.join(outputDir, `${domain.replace(/\./g, '_')}_analysis_${timestamp}.json`);
    }

    // Convert Sets to Arrays for JSON serialization
    const dataToSave = JSON.parse(JSON.stringify(this.analysisData, (key, value) => {
      if (value instanceof Set) {
        return Array.from(value);
      }
      return value;
    }));

    const outputPath = path.resolve(filename);
    fs.writeFileSync(outputPath, JSON.stringify(dataToSave, null, 2));
    this.log(`Analysis saved to: ${outputPath}`);
    return outputPath;
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }
}

async function main() {
  const url = process.argv[2];
  
  if (!url) {
    console.error('Usage: node website-analyzer.js <URL>');
    process.exit(1);
  }

  const analyzer = new WebsiteAnalyzer();
  
  try {
    await analyzer.initialize();
    
    // Analyze both desktop and mobile
    await analyzer.analyzePage(url, { width: 1920, height: 1080 });
    await analyzer.analyzeResponsive(url);
    
    const outputFile = await analyzer.saveResults();
    console.log(`\nAnalysis complete! Results saved to: ${outputFile}`);
    
  } catch (error) {
    console.error('Analysis failed:', error.message);
    process.exit(1);
  } finally {
    await analyzer.close();
  }
}

if (require.main === module) {
  main();
}

module.exports = WebsiteAnalyzer;