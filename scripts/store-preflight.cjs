#!/usr/bin/env node
'use strict';
// Ask Partner Center which package full names the product already holds.
// Usage: STORE_ACCESS_TOKEN=... node scripts/store-preflight.cjs --store-id 9NLM756D1CZR [--enforce]
// The token is read from the environment and never printed, logged or written to disk.
const fs = require('node:fs');
const path = require('node:path');
const { readIdentity, preflight } = require('./store.cjs');
const ROOT = path.resolve(__dirname, '..');

async function main(args) {
  const options = { storeId: '9NLM756D1CZR', enforce: false };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--enforce') options.enforce = true;
    else if (args[i] === '--store-id' && args[i + 1]) options.storeId = args[++i];
    else throw Error('Usage: node scripts/store-preflight.cjs [--store-id ID] [--enforce]');
  }
  if (!process.env.STORE_ACCESS_TOKEN) {
    // Local lists are a subset of Partner Center. --enforce still fails closed, because a version
    // that only Partner Center knows about (a rejected submission) must never be rebuilt.
    console.error('STORE_ACCESS_TOKEN is not set: Partner Center was not asked. Local lists still block every known full name.');
    if (options.enforce) process.exitCode = 1;
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
