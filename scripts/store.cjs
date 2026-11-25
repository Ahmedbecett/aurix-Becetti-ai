'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const ROOT = path.resolve(__dirname, '..');
const ASSETS = Object.freeze({
  'StoreLogo.png': [50, 50], 'Square44x44Logo.png': [44, 44],
  'Square150x150Logo.png': [150, 150], 'Square310x310Logo.png': [310, 310],
  'Wide310x150Logo.png': [310, 150]
});
const xml = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[c]));
function packageVersion(version) {
  if (typeof version !== 'string' || version !== version.trim() || !/^[1-9]\d*\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/.test(version) || version.split('.').some(n => Number(n) > 65535)) {
    throw Error('Store version must be stable major.minor.patch, major > 0, each component <= 65535.');
  }
  return version + '.0';
}
function validateIdentity(identity) {
  const keys = ['identityName', 'publisher', 'publisherDisplayName', 'displayName'];
  if (!identity || typeof identity !== 'object' || Array.isArray(identity) || Object.keys(identity).some(key => !keys.includes(key))) throw Error('Identity configuration must contain only the four public Store identity fields, never credentials.');
  for (const key of keys) {
    const value = identity[key];
    if (typeof value !== 'string' || !value.trim() || value !== value.trim() || /[\x00-\x1f]/.test(value) || /^(YOUR_|REPLACE_|TODO|PLACEHOLDER)/i.test(value)) {
      throw Error(`Missing or invalid ${key}. Copy public identity values exactly from Partner Center; see STORE-AR.md.`);
    }
  }
  if (!/^[A-Za-z0-9.-]{3,50}$/.test(identity.identityName) || /^(Microsoft|Windows)\./i.test(identity.identityName)) throw Error('Invalid Store Package/Identity/Name.');
  if (!identity.publisher.startsWith('CN=') || identity.publisher.length > 8192) throw Error('Publisher must be the exact Partner Center distinguished name beginning CN=.');
  for (const key of ['displayName', 'publisherDisplayName']) if (identity[key].length > 256) throw Error(`${key} is too long.`);
  return { ...identity };
}
function packageFamilyName(identity) {
  validateIdentity(identity);
  const hash = crypto.createHash('sha256').update(identity.publisher, 'utf16le').digest().subarray(0, 8);
  const bits = [...hash].map(byte => byte.toString(2).padStart(8, '0')).join('') + '0';
  const alphabet = '0123456789abcdefghjkmnpqrstvwxyz';
  let publisherId = '';
  for (let at = 0; at < bits.length; at += 5) publisherId += alphabet[parseInt(bits.slice(at, at + 5), 2)];
  return identity.identityName + '_' + publisherId;
}
function packageSid(familyName) {
  const hash = crypto.createHash('sha256').update(familyName.toLowerCase(), 'utf16le').digest();
  return 'S-1-15-2-' + Array.from({ length: 7 }, (_, index) => hash.readUInt32LE(index * 4)).join('-');
}
function validateProduct(identity, product) {
  const family = packageFamilyName(identity);
  if (product.identityName !== identity.identityName || product.packageFamilyName !== family || product.packageSid !== packageSid(family)) throw Error('Partner Center identity, Publisher, PFN and SID do not match. Do not build a package with mismatched product identity.');
  if (product.displayNameConfirmed && (!product.reservedDisplayName || identity.displayName !== product.reservedDisplayName)) throw Error('Manifest display name must exactly match the reserved Partner Center name: ' + product.reservedDisplayName);
  if (!/^[A-Z0-9]{12}$/.test(product.storeId)) throw Error('Invalid public Microsoft Store product ID.');
  return product;
}
function productFor(identity) {
  const filename = path.join(ROOT, 'store/product.json');
  if (!fs.existsSync(filename)) return null;
  const product = JSON.parse(fs.readFileSync(filename, 'utf8'));
  return product.identityName === identity.identityName ? validateProduct(identity, product) : null;
}
function readIdentity(file, env = process.env) {
  let identity = {};
  // An explicit file never silently falls back. Public owner identity is tracked;
  // the optional ignored local file takes precedence when no file is specified.
  const defaultFile = fs.existsSync(path.join(ROOT, 'store/identity.json')) ? 'store/identity.json' : 'store/identity.store.json';
  const fullPath = path.resolve(ROOT, file || defaultFile);
  if (fs.existsSync(fullPath)) identity = JSON.parse(fs.readFileSync(fullPath, 'utf8').replace(/^\uFEFF/, ''));
  const names = { identityName: 'MSSTORE_IDENTITY_NAME', publisher: 'MSSTORE_PUBLISHER', publisherDisplayName: 'MSSTORE_PUBLISHER_DISPLAY_NAME', displayName: 'MSSTORE_DISPLAY_NAME' };
  for (const [key, name] of Object.entries(names)) if (env[name] !== undefined) identity[key] = env[name];
  return validateIdentity(identity);
}
function manifest(identity, version) {
  validateIdentity(identity);
  const replacements = { IDENTITY_NAME: identity.identityName, PUBLISHER: identity.publisher, PUBLISHER_DISPLAY_NAME: identity.publisherDisplayName, DISPLAY_NAME: identity.displayName, VERSION: packageVersion(version) };
  return fs.readFileSync(path.join(ROOT, 'store/AppxManifest.xml.template'), 'utf8').replace(/\{\{([A-Z_]+)\}\}/g, (_m, key) => {
    if (!(key in replacements)) throw Error('Unknown manifest variable ' + key);
    return xml(replacements[key]);
  });
}
function validateAssets(root = path.join(ROOT, 'store/assets')) {
  for (const [name, [w, h]] of Object.entries(ASSETS)) {
    const bytes = fs.readFileSync(path.join(root, name));
    if (bytes.length < 24 || bytes.subarray(0, 8).toString('hex') !== '89504e470d0a1a0a' || bytes.readUInt32BE(16) !== w || bytes.readUInt32BE(20) !== h) throw Error(`Invalid PNG dimensions: ${name}, expected ${w}x${h}.`);
  }
}
function validateRuntime(app) {
  const exe = path.join(app, 'AURIX.exe');
  if (!fs.existsSync(exe)) throw Error('Missing Windows AURIX.exe. Build the x64 Electron runtime on Windows first.');
  const descriptor = fs.openSync(exe, 'r');
  try {
    const dos = Buffer.alloc(64);
    if (fs.readSync(descriptor, dos, 0, 64, 0) !== 64 || dos.subarray(0, 2).toString() !== 'MZ') throw Error('AURIX.exe is not a Windows PE executable.');
    const offset = dos.readUInt32LE(60);
    const pe = Buffer.alloc(6);
    if (offset < 64 || offset + 6 > fs.fstatSync(descriptor).size || fs.readSync(descriptor, pe, 0, 6, offset) !== 6 || pe.readUInt32LE(0) !== 0x00004550 || pe.readUInt16LE(4) !== 0x8664) throw Error('AURIX.exe must be a valid x64 Windows PE executable.');
  } finally { fs.closeSync(descriptor); }
  if (!fs.existsSync(path.join(app, 'resources/app.asar'))) throw Error('Missing packaged app.asar.');
}
function stage(identity, version, appDir) {
  const app = path.resolve(ROOT, appDir || 'dist/store-runtime/win-unpacked');
  const output = path.join(ROOT, 'dist/store');
  const staging = path.join(output, 'staging');
  if (app === output || app.startsWith(output + path.sep)) throw Error('Runtime directory must be outside dist/store.');
  validateAssets();
  validateRuntime(app);
  const content = manifest(identity, version);
  const product = productFor(identity);
  fs.mkdirSync(output, { recursive: true });
  fs.rmSync(staging, { recursive: true, force: true });
  fs.mkdirSync(staging);
  fs.cpSync(app, path.join(staging, 'app'), { recursive: true, dereference: false });
  fs.cpSync(path.join(ROOT, 'store/assets'), path.join(staging, 'Assets'), { recursive: true });
  fs.writeFileSync(path.join(staging, 'AppxManifest.xml'), content, 'utf8');
  fs.cpSync(path.join(ROOT, 'store/submission'), path.join(output, 'submission'), { recursive: true });
  const name = `${identity.identityName}_${packageVersion(version)}_x64.msix`;
  const report = {
    ...identity, packageVersion: packageVersion(version), architecture: 'x64', packageFile: name,
    packageFamilyName: packageFamilyName(identity), packageSid: packageSid(packageFamilyName(identity)),
    storeId: product?.storeId || null, displayNameConfirmed: product?.displayNameConfirmed === true,
    manifestSHA256: crypto.createHash('sha256').update(content).digest('hex'),
    submissionStatus: 'NOT_SUBMITTED', signing: 'Unsigned candidate for Partner Center only; not a sideload installer',
    requiredManualGates: [...(product?.displayNameConfirmed ? [] : ['Confirm the exact reserved display name in Partner Center before final submission']), 'Deploy and verify desktop Google auth bridge and Windows privacy page', 'Run real Windows 10/11 Google login and every advertised AI feature', 'Run Windows App Certification Kit on a signed test copy', 'Capture actual Windows screenshots', 'Complete IARC, AI disclosure, privacy declarations and runFullTrust justification', 'Confirm provider rights, content safeguards and monitored reporting inbox']
  };
  fs.writeFileSync(path.join(output, 'store-build.json'), JSON.stringify(report, null, 2) + '\n');
  return { staging, packagePath: path.join(output, name), report };
}
function main(args) {
  const options = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--check') options.check = true;
    else if (['--identity', '--app-dir'].includes(args[i]) && args[i + 1] && !args[i + 1].startsWith('--')) options[args[i].slice(2)] = args[++i];
    else throw Error('Usage: node scripts/store.cjs [--check] [--identity file.json] [--app-dir directory]');
  }
  const identity = readIdentity(options.identity);
  const version = JSON.parse(fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8')).version;
  manifest(identity, version); validateAssets();
  const product = productFor(identity);
  if (product && !product.displayNameConfirmed) console.warn('Reserved display name is not yet confirmed. The configured display name is provisional, not a submission approval.');
  if (options.check) console.log(`Store identity and assets valid: ${identity.identityName} ${packageVersion(version)} (not built, tested or submitted).`);
  else { const result = stage(identity, version, options['app-dir']); console.log(`Staged ${result.staging}\nCandidate package: ${result.packagePath}`); }
}
if (require.main === module) { try { main(process.argv.slice(2)); } catch (err) { console.error(err.message); process.exitCode = 1; } }
module.exports = { ASSETS, packageVersion, validateIdentity, readIdentity, manifest, validateAssets, validateRuntime, packageFamilyName, packageSid, validateProduct, stage };
