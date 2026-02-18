/**
 * Fix Imports Script
 * Removes version suffixes from package imports
 * Example: "@radix-ui/react-slot@1.1.2" → "@radix-ui/react-slot"
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const componentsDir = path.join(__dirname, '../components');

// Regex to match versioned imports
const versionedImportRegex = /from\s+(['"])([^'"]+)@[\d.]+\1/g;

let totalFiles = 0;
let totalReplacements = 0;

function fixImportsInFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  let replacements = 0;
  
  const newContent = content.replace(versionedImportRegex, (match, quote, packageName) => {
    replacements++;
    return `from ${quote}${packageName}${quote}`;
  });
  
  if (replacements > 0) {
    fs.writeFileSync(filePath, newContent, 'utf8');
    console.log(`✅ Fixed ${replacements} import(s) in ${path.basename(filePath)}`);
    totalReplacements += replacements;
  }
  
  return replacements;
}

function processDirectory(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    
    if (entry.isDirectory()) {
      processDirectory(fullPath);
    } else if (entry.isFile() && (entry.name.endsWith('.tsx') || entry.name.endsWith('.ts'))) {
      totalFiles++;
      fixImportsInFile(fullPath);
    }
  }
}

console.log('🔧 Fixing versioned imports...\n');

// Process components directory
if (fs.existsSync(componentsDir)) {
  processDirectory(componentsDir);
} else {
  console.error('❌ Components directory not found');
  process.exit(1);
}

console.log(`\n✨ Complete!`);
console.log(`   Processed: ${totalFiles} files`);
console.log(`   Fixed: ${totalReplacements} imports`);

if (totalReplacements > 0) {
  console.log('\n💡 Next steps:');
  console.log('   1. Run: npm install');
  console.log('   2. Run: npm run dev');
  console.log('   3. Check console for any remaining errors\n');
} else {
  console.log('\n✅ No versioned imports found. Your imports are already correct!\n');
}