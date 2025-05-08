#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Get current package info
const pkgPath = process.cwd();
const pkgJson = require(path.join(pkgPath, 'package.json'));
const pkgName = pkgJson.name;
const pkgVersion = pkgJson.version;
const tagName = `${pkgName}@${pkgVersion}`;

// Get workflow file name - assumes it's named same as package or specified in a config
const workflowFileName = path.basename(pkgPath) + '.yml';
const workflowPath = path.join(pkgPath, workflowFileName);

// Path where GitHub expects reusable workflows
const targetWorkflowPath = `.github/workflows/${workflowFileName}`;

// Create the tag with only the workflow file
console.log(`Creating tag ${tagName} with only ${workflowFileName}...`);

try {
  // Create a temporary branch for the tag
  const tempBranch = `temp-release-${pkgName}-${Date.now()}`;
  execSync(`git checkout -b ${tempBranch}`);
  
  // Remove all files except the workflow file and .github structure
  execSync('git rm -rf .');
  
  // Create .github/workflows directory
  execSync('mkdir -p .github/workflows');
  
  // Copy the workflow file to the expected location
  fs.copyFileSync(workflowPath, targetWorkflowPath);
  
  // Add the file and commit
  execSync(`git add ${targetWorkflowPath}`);
  execSync(`git commit -m "Release ${tagName}"`);
  
  // Create the tag
  execSync(`git tag -a ${tagName} -m "Release ${tagName}"`);
  
  // Push the tag
  execSync(`git push origin ${tagName}`);
  
  // Return to the original branch and delete temp branch
  execSync('git checkout -');
  execSync(`git branch -D ${tempBranch}`);
  
  console.log(`Successfully created and pushed tag ${tagName}`);
} catch (error) {
  console.error(`Failed to create tag: ${error.message}`);
  process.exit(1);
}