/**
 * Design Token Export Script
 * Extracts CSS variables from globals.css and exports to JSON
 * Usage: node scripts/export-tokens.mjs
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Read globals.css
const cssPath = path.join(__dirname, '../styles/globals.css');
const css = fs.readFileSync(cssPath, 'utf8');

// Extract :root block
const rootMatch = /:root\s*\{([\s\S]*?)\n\}/m.exec(css);
if (!rootMatch) {
  console.error('❌ Could not find :root block in globals.css');
  process.exit(1);
}

const rootContent = rootMatch[1];

// Parse CSS variables
const varRegex = /--([a-z0-9\-]+)\s*:\s*([^;]+);/gi;
const vars = {};
let match;

while ((match = varRegex.exec(rootContent)) !== null) {
  const key = match[1].trim();
  const value = match[2].trim();
  vars[key] = value;
}

console.log(`✅ Extracted ${Object.keys(vars).length} CSS variables`);

// Categorize tokens
const tokens = {
  $schema: "https://schemas.figma.com/design-tokens/draft-1",
  $description: "Trend Radar Design Tokens - Exported from code",
  $version: "1.0.0",
  $exportDate: new Date().toISOString(),
  
  color: {
    surface: {},
    ink: {},
    semantic: {},
    charts: {},
  },
  
  typography: {
    size: {},
    lineHeight: {},
    fontWeight: {},
  },
  
  spacing: {},
  
  radius: {},
  
  shadow: {},
  
  other: {},
};

// Categorize each variable
Object.entries(vars).forEach(([key, value]) => {
  // Colors
  if (key === 'background' || key === 'foreground' || key === 'card' || key === 'card-foreground' || 
      key === 'popover' || key === 'popover-foreground' || key === 'primary' || key === 'primary-foreground' ||
      key === 'secondary' || key === 'secondary-foreground' || key === 'muted' || key === 'muted-foreground' ||
      key === 'input' || key === 'input-background' || key === 'switch-background') {
    tokens.color.surface[key] = { $value: value, $type: "color" };
  }
  else if (key === 'accent' || key === 'accent-foreground' || key === 'accent-secondary' || 
           key === 'destructive' || key === 'destructive-foreground' || 
           key === 'border' || key === 'ring') {
    tokens.color.semantic[key] = { $value: value, $type: "color" };
  }
  else if (key.startsWith('chart-')) {
    tokens.color.charts[key] = { $value: value, $type: "color" };
  }
  else if (key.startsWith('sidebar')) {
    tokens.color.surface[key] = { $value: value, $type: "color" };
  }
  
  // Typography
  else if (key.startsWith('text-') && !key.includes('-lh')) {
    const styleName = key.replace('text-', '');
    tokens.typography.size[styleName] = { $value: value, $type: "dimension" };
  }
  else if (key.includes('-lh')) {
    const styleName = key.replace('text-', '').replace('-lh', '');
    tokens.typography.lineHeight[styleName] = { $value: value, $type: "dimension" };
  }
  else if (key.startsWith('font-weight-')) {
    const weightName = key.replace('font-weight-', '');
    tokens.typography.fontWeight[weightName] = { $value: value, $type: "fontWeight" };
  }
  else if (key === 'font-size') {
    tokens.typography.size.base = { $value: value, $type: "dimension" };
  }
  
  // Spacing
  else if (key.startsWith('space-')) {
    const spaceName = key.replace('space-', '');
    tokens.spacing[spaceName] = { $value: value, $type: "dimension" };
  }
  
  // Radius
  else if (key.startsWith('radius') || key === 'radius') {
    tokens.radius[key] = { $value: value, $type: "dimension" };
  }
  
  // Shadow
  else if (key.startsWith('shadow-')) {
    tokens.shadow[key] = { $value: value, $type: "shadow" };
  }
  
  // Other
  else {
    tokens.other[key] = { $value: value };
  }
});

// Add standard Tailwind spacing scale for reference
tokens.spacing = {
  $description: "Standard Tailwind spacing scale used in the application",
  "1": { $value: "4px", $type: "dimension" },
  "2": { $value: "8px", $type: "dimension" },
  "3": { $value: "12px", $type: "dimension" },
  "4": { $value: "16px", $type: "dimension" },
  "5": { $value: "20px", $type: "dimension" },
  "6": { $value: "24px", $type: "dimension" },
  "8": { $value: "32px", $type: "dimension" },
  "10": { $value: "40px", $type: "dimension" },
  "12": { $value: "48px", $type: "dimension" },
  "16": { $value: "64px", $type: "dimension" },
  "20": { $value: "80px", $type: "dimension" },
  "24": { $value: "96px", $type: "dimension" },
};

// Add shadow definitions (standard values used in the app)
tokens.shadow = {
  $description: "Elevation system",
  sm: { 
    $value: "0 1px 2px rgba(0, 0, 0, 0.06)", 
    $type: "shadow",
    $description: "Subtle elevation"
  },
  md: { 
    $value: "0 4px 10px rgba(0, 0, 0, 0.10)", 
    $type: "shadow",
    $description: "Cards, dropdowns"
  },
  lg: { 
    $value: "0 10px 24px rgba(0, 0, 0, 0.14)", 
    $type: "shadow",
    $description: "Modals, popovers"
  },
  "accent-glow": { 
    $value: "0 0 20px rgba(0, 102, 255, 0.3)", 
    $type: "shadow",
    $description: "Accent hover states"
  },
};

// Write to file
const outputPath = path.join(__dirname, '../design-tokens.json');
fs.writeFileSync(outputPath, JSON.stringify(tokens, null, 2));

console.log(`\n✅ Successfully exported design tokens to: design-tokens.json`);
console.log(`\n📊 Token Summary:`);
console.log(`   - Colors: ${Object.keys(tokens.color.surface).length + Object.keys(tokens.color.semantic).length + Object.keys(tokens.color.charts).length}`);
console.log(`   - Typography Sizes: ${Object.keys(tokens.typography.size).length}`);
console.log(`   - Line Heights: ${Object.keys(tokens.typography.lineHeight).length}`);
console.log(`   - Font Weights: ${Object.keys(tokens.typography.fontWeight).length}`);
console.log(`   - Spacing: ${Object.keys(tokens.spacing).length}`);
console.log(`   - Radius: ${Object.keys(tokens.radius).length}`);
console.log(`   - Shadows: ${Object.keys(tokens.shadow).length}`);
console.log(`\n💡 Import this file into Figma using a design tokens plugin`);
console.log(`   Recommended: Tokens Studio for Figma`);
console.log(`   https://www.figma.com/community/plugin/843461159747178978\n`);