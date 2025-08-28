# Website Analyzer - Global CLI Tool

A comprehensive Playwright-based tool for analyzing websites that can be installed globally and used from any directory.

## 🚀 Global Installation

```bash
# Install globally from this directory
npm install -g .

# Or if published to npm
npm install -g website-analyzer-global
```

## 📋 Usage

After global installation, use from anywhere:

```bash
# Full command
website-analyzer https://example.com

# Short alias
wa https://example.com

# With custom output directory
website-analyzer https://example.com -o ./my-analysis

# Show help
website-analyzer --help

# Show version
website-analyzer --version
```

## 📁 Output Structure

Creates `website-analysis/` folder in current directory (or specified location):

```
website-analysis/
└── example_com_analysis_2024-01-01T12-00-00-000Z.json
```

## ✨ Features

- **🎨 Design Tokens**: Colors, fonts, spacing, shadows, gradients
- **⚡ Performance**: Load times, paint metrics, DOM analysis  
- **🔍 Element Data**: Complete CSS styles, geometry, selectors
- **📱 Responsive**: Multi-viewport analysis (mobile, tablet, desktop)
- **🧩 Components**: Automatic UI pattern recognition
- **📊 Assets**: Images, fonts, stylesheets inventory

## 🛠 Development

```bash
# Install dependencies
npm install

# Test locally
npm test

# Install globally for development
npm install -g .
```

## 📖 CLI Options

| Option | Description | Example |
|--------|-------------|---------|
| `<URL>` | Website URL to analyze | `https://example.com` |
| `-o, --output <dir>` | Custom output directory | `-o ./reports` |
| `-h, --help` | Show help message | `--help` |
| `-v, --version` | Show version | `--version` |

## 🎯 Use Cases

- **Design System Analysis**: Extract design tokens from existing sites
- **Competitive Research**: Analyze competitor websites  
- **Performance Auditing**: Get comprehensive performance data
- **Component Inventory**: Catalog UI patterns and components
- **Responsive Testing**: Check behavior across viewports

## 📊 Sample Output

```json
{
  "metadata": {
    "url": "https://example.com",
    "elementCount": 847,
    "loadTime": 1250,
    "performance": { /* timing data */ }
  },
  "designTokens": {
    "colors": ["#ff0000", "rgb(255,255,255)", ...],
    "fonts": ["Arial bold", "Helvetica 400", ...],
    "spacing": ["16px", "24px", "32px", ...]
  },
  "elements": [ /* detailed element data */ ],
  "componentPatterns": [ /* UI patterns */ ],
  "responsive": { /* viewport analysis */ }
}
```

## 🔧 Requirements

- Node.js 16+
- Chromium (auto-installed with Playwright)
- Network access to target URLs