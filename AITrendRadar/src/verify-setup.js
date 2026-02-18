#!/usr/bin/env node

/**
 * Setup Verification Script for Trend Radar
 * Run this after installation to verify your setup
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('\n🔍 Verifying Trend Radar Setup...\n');

let hasErrors = false;
let warnings = 0;

// Required files and directories
const requiredStructure = {
  'package.json': 'file',
  'vite.config.ts': 'file',
  'tsconfig.json': 'file',
  'index.html': 'file',
  'postcss.config.js': 'file',
  'src': 'directory',
  'src/main.tsx': 'file',
  'src/App.tsx': 'file',
  'src/components': 'directory',
  'src/styles': 'directory',
  'src/styles/globals.css': 'file',
  'public': 'directory',
  'node_modules': 'directory',
};

// Check each item
Object.entries(requiredStructure).forEach(([item, type]) => {
  const itemPath = path.join(__dirname, item);
  const exists = fs.existsSync(itemPath);
  
  if (!exists) {
    if (item === 'node_modules') {
      console.log(`⚠️  ${item} - Not found (run 'npm install')`);
      warnings++;
    } else {
      console.log(`❌ ${item} - Missing!`);
      hasErrors = true;
    }
  } else {
    const stat = fs.statSync(itemPath);
    const isCorrectType = type === 'directory' ? stat.isDirectory() : stat.isFile();
    
    if (!isCorrectType) {
      console.log(`❌ ${item} - Wrong type (should be ${type})`);
      hasErrors = true;
    } else {
      console.log(`✅ ${item}`);
    }
  }
});

// Check critical component files
console.log('\n📦 Checking Components...\n');

const criticalComponents = [
  'src/components/Navbar.tsx',
  'src/components/Footer.tsx',
  'src/components/pages/Home.tsx',
  'src/components/ui/button.tsx',
];

criticalComponents.forEach(comp => {
  const compPath = path.join(__dirname, comp);
  if (fs.existsSync(compPath)) {
    console.log(`✅ ${comp}`);
  } else {
    console.log(`❌ ${comp} - Missing!`);
    hasErrors = true;
  }
});

// Check package.json dependencies
console.log('\n📋 Checking package.json...\n');

try {
  const packageJson = JSON.parse(
    fs.readFileSync(path.join(__dirname, 'package.json'), 'utf-8')
  );
  
  const criticalDeps = [
    'react',
    'react-dom',
    'vite',
    'tailwindcss',
    'motion',
    'lucide-react',
  ];
  
  const allDeps = { ...packageJson.dependencies, ...packageJson.devDependencies };
  
  criticalDeps.forEach(dep => {
    if (allDeps[dep]) {
      console.log(`✅ ${dep} (${allDeps[dep]})`);
    } else {
      console.log(`❌ ${dep} - Not found in dependencies!`);
      hasErrors = true;
    }
  });
} catch (err) {
  console.log('❌ Error reading package.json');
  hasErrors = true;
}

// Final report
console.log('\n' + '='.repeat(50));
console.log('\n📊 Setup Verification Results:\n');

if (hasErrors) {
  console.log('❌ Setup has ERRORS - Please fix the issues above');
  console.log('\n📖 Check EXPORT_INSTRUCTIONS.md for help');
  process.exit(1);
} else if (warnings > 0) {
  console.log('⚠️  Setup incomplete - Run "npm install" to continue');
  console.log('\n💡 After installing, run "npm run dev" to start');
  process.exit(0);
} else {
  console.log('✅ Setup looks good!');
  console.log('\n🚀 You can now run: npm run dev');
  console.log('🌐 Then open: http://localhost:5173');
  console.log('\n💡 Tip: Check README.md for more information');
  process.exit(0);
}
