#!/usr/bin/env node
'use strict';
// Ask Partner Center which package full names the product already holds.
// Usage: STORE_ACCESS_TOKEN=... node scripts/store-preflight.cjs --store-id 9NLM756D1CZR [--enforce]
//        node scripts/store-preflight.cjs --require-partner-center   (fails when no token is set)
// The token is read from the environment and never printed, logged or written to disk.
const fs = require('node:fs');
const path = require('node:path');
const { readIdentity, preflight } = require('./store.cjs');
const ROOT = path.resolve(__dirname, '..');

async function main(args) {
  const options = { storeId: '9NLM756D1CZR', enforce: false };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--enforce') options.enforce = true;
    else if (args[i] === '--require-partner-center') options.requirePartnerCenter = true;
    else if (args[i] === '--store-id' && args[i + 1]) options.storeId = args[++i];
    else throw Error('Usage: node scripts/store-preflight.cjs [--store-id ID] [--enforce] [--require-partner-center]');
  }
  if (!process.env.STORE_ACCESS_TOKEN) {
    // Local lists cover every full name this repository knows about. Partner Center may know more,
    // so the caller must treat this result as weaker and say so in the build record.
    console.error('STORE_ACCESS_TOKEN is not set: Partner Center was not asked. Local published/rejected lists still block every known full name.');
    if (options.requirePartnerCenter) process.exitCode = 1;
    return;
  }
  const identity = readIdentity();
  const version = JSON.parse(fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8')).version;
  const result = await preflight(identity, version, { storeId: options.storeId });
  console.log(`Version ${version} -> ${result.fullName} (checked against Partner Center)`);
  for (const item of result.checked) console.log(`  held: ${item.name}  [submission ${item.submission}, ${item.status}]`);
  console.log('This full name is free. Upload this file only: dist/store/' + result.fullName + '.msix');
}

if (require.main === module) {
  main(process.argv.slice(2)).catch(error => {
    console.error(error.message);
    process.exitCode = 1;
  });
}
module.exports = { main };
