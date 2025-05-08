#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

// Get current package info
const pkgPath = process.cwd();
const pkgJson = require(path.join(pkgPath, 'package.json'));
const pkgName = pkgJson.name;
const pkgVersion = pkgJson.version;
const tagName = `${pkgName}@${pkgVersion}`;

// Get workflow file name - assumes it's named same as package or specified in a config
const workflowFileName = path.basename(pkgPath) + '.yml';
const workflowPath = path.join(pkgPath, workflowFileName);

// Create a clean directory for our tagged content
const tempDir = path.join(os.tmpdir(), `workflow-tag-${Date.now()}`);
fs.mkdirSync(path.join(tempDir, '.github', 'workflows'), { recursive: true });

// Create the tag with only the workflow file
console.log(`Creating tag ${tagName} with only ${workflowFileName}...`);

try {
  // First, read the workflow content
  const workflowContent = fs.readFileSync(workflowPath, 'utf8');
  
  // Copy the content to the target path in our temp directory
  const targetPath = path.join(tempDir, '.github', 'workflows', workflowFileName);
  fs.writeFileSync(targetPath, workflowContent);
  
  // Initialize a new Git repo in the temp directory
  process.chdir(tempDir);
  execSync('git init');
  execSync('git config user.email "workflow-publisher@example.com"');
  execSync('git config user.name "Workflow Publisher"');
  
  // Add and commit just the workflow file
  execSync('git add .github');
  execSync(`git commit -m "Release ${tagName}"`);
  
  // Create the tag
  execSync(`git tag -a ${tagName} -m "Release ${tagName}"`);
  
  // Push just the tag to the original repository
  const originalRemote = execSync('git remote get-url origin', { cwd: pkgPath }).toString().trim();
  execSync(`git remote add origin ${originalRemote}`);
  execSync(`git push origin ${tagName} --force`);
  
  console.log(`Successfully created and pushed tag ${tagName}`);
  
  // Return to original directory
  process.chdir(pkgPath);
} catch (error) {
  // Make sure we return to the original directory even if there's an error
  process.chdir(pkgPath);
  console.error(`Failed to create tag: ${error.message}`);
  process.exit(1);
}