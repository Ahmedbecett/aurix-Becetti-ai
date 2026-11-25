const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { packageVersion, validateIdentity, readIdentity, manifest, validateAssets, validateRuntime, ASSETS, stage, packageFamilyName, packageSid, validateProduct } = require('../../scripts/store.cjs');
const identity = { identityName: 'TestPublisher.AURIX', publisher: 'CN=Test Publisher', publisherDisplayName: 'Test Publisher', displayName: 'AURIX' };
const root = path.resolve(__dirname, '../..');

test('Store version is four-part with nonzero major, zero reserved revision and bounded fields', () => {
  assert.equal(packageVersion('1.0.0'), '1.0.0.0');
  assert.equal(packageVersion('65535.65535.65535'), '65535.65535.65535.0');
  for (const v of ['0.1.0', '1.0.0.1', '1.0.0-beta', '1.0', '65536.0.0', '1.-1.0', '1.1.65536', '01.0.0']) assert.throws(() => packageVersion(v), /Store version/);
});
test('missing, sample and malformed Partner Center values block a Store candidate', () => {
  assert.throws(() => validateIdentity({}), /identityName/);
  const example = JSON.parse(fs.readFileSync(path.join(root, 'store/identity.example.json'), 'utf8'));
  assert.throws(() => validateIdentity(example), /identityName/);
  for (const patch of [{ publisher: '' }, { publisher: 'Test Publisher' }, { identityName: '../evil' }, { identityName: 'Microsoft.Aurix' }, { publisherDisplayName: 'YOUR_NAME' }, { displayName: ' AURIX' }, { clientSecret: 'must-not-be-accepted' }]) assert.throws(() => validateIdentity({ ...identity, ...patch }));
  assert.deepEqual(validateIdentity(identity), identity);
});
test('manifest escapes identity data, exposes only full trust and does not invent device claims', () => {
  const output = manifest({ ...identity, displayName: 'AURIX & <studio>', publisherDisplayName: 'Owner "A"' }, '1.0.0');
  assert.match(output, /AURIX &amp; &lt;studio&gt;/);
  assert.match(output, /Owner &quot;A&quot;/);
  assert.match(output, /Version="1\.0\.0\.0" ProcessorArchitecture="x64"/);
  assert.match(output, /Windows\.Desktop.*MinVersion="10\.0\.19045\.0"/);
  assert.match(output, /Executable="app\\AURIX\.exe" EntryPoint="Windows\.FullTrustApplication"/);
  assert.equal((output.match(/<rescap:Capability /g) || []).length, 1);
  assert.match(output, /Name="runFullTrust"/);
  assert.doesNotMatch(output, /broadFileSystemAccess|microphone|webcam|runas|\{\{/);
});
test('Store identity can be supplied by public environment values without a credential file', () => {
  const env = { MSSTORE_IDENTITY_NAME: identity.identityName, MSSTORE_PUBLISHER: identity.publisher, MSSTORE_PUBLISHER_DISPLAY_NAME: identity.publisherDisplayName, MSSTORE_DISPLAY_NAME: identity.displayName };
  assert.deepEqual(readIdentity('store/does-not-exist.json', env), identity);
  assert.throws(() => readIdentity('store/does-not-exist.json', {}), /identityName/);
});
test('owner-provided publisher, PFN and package SID agree and the reserved display name remains unconfirmed', () => {
  const owner = JSON.parse(fs.readFileSync(path.join(root, 'store/identity.store.json'), 'utf8'));
  const product = JSON.parse(fs.readFileSync(path.join(root, 'store/product.json'), 'utf8'));
  assert.equal(packageFamilyName(owner), 'Ahmedbecetti.AURIXAI_y0zvy3a8v70hm');
  assert.equal(packageSid(packageFamilyName(owner)), product.packageSid);
  assert.equal(packageSid(product.packageFamilyName.toUpperCase()), product.packageSid);
  assert.equal(validateProduct(owner, product).storeId, '9NLM756D1CZR');
  assert.equal(product.displayNameConfirmed, false);
  assert.equal(readIdentity('store/identity.store.json', {}).identityName, owner.identityName);
  assert.throws(() => validateProduct({ ...owner, publisher: 'CN=Wrong publisher' }, product), /do not match/);
  assert.throws(() => validateProduct(owner, { ...product, packageSid: 'S-1-15-2-wrong' }), /do not match/);
  assert.throws(() => validateProduct(owner, { ...product, storeId: 'invalid' }), /product ID/);
  assert.match(manifest(owner, '1.0.0'), /Name="Ahmedbecetti.AURIXAI" Publisher="CN=A5D5DC31-4A15-4059-8030-D96C51054596"/);
});
test('all manifest logos are real PNGs of the declared dimensions', () => {
  validateAssets();
  const output = manifest(identity, '1.0.0');
  for (const name of Object.keys(ASSETS)) assert.ok(output.includes('Assets\\' + name), name);
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'aurix-assets-'));
  try { fs.writeFileSync(path.join(temp, 'StoreLogo.png'), 'not a png'); assert.throws(() => validateAssets(temp), /Invalid PNG/); }
  finally { fs.rmSync(temp, { recursive: true, force: true }); }
});
test('Store staging rejects a non-PE file and a mismatched CPU architecture', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'aurix-pe-'));
  try {
    const exe = path.join(temp, 'AURIX.exe');
    fs.writeFileSync(exe, 'not an executable');
    assert.throws(() => validateRuntime(temp), /not a Windows PE/);
    // Synthetic headers are unit-test fixtures only, never staged as a package.
    const bytes = Buffer.alloc(134);
    bytes.write('MZ'); bytes.writeUInt32LE(128, 60); bytes.writeUInt32LE(0x00004550, 128); bytes.writeUInt16LE(0x14c, 132);
    fs.writeFileSync(exe, bytes);
    assert.throws(() => validateRuntime(temp), /valid x64/);
    bytes.writeUInt16LE(0x8664, 132); fs.writeFileSync(exe, bytes);
    assert.throws(() => validateRuntime(temp), /app.asar/);
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
});
test('no runtime means no staged or fake MSIX output', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'aurix-runtime-'));
  try { assert.throws(() => stage(identity, '1.0.0', temp), /Missing Windows/); }
  finally { fs.rmSync(temp, { recursive: true, force: true }); }
});
test('Store automation keeps SDK validation, checks process errors and never submits or sideload-signs', () => {
  const ps = fs.readFileSync(path.join(root, 'scripts/build-store.ps1'), 'utf8');
  assert.match(ps, /\$MakeAppx pack \/d/);
  assert.match(ps, /\$MakeAppx unpack \/p/);
  assert.match(ps, /verify-msix\.py/);
  assert.match(ps, /--staged/);
  assert.match(ps, /if \(\$LASTEXITCODE -ne 0\)/);
  assert.doesNotMatch(ps, /^\s*&.*\/nv/m);
  assert.doesNotMatch(ps, /New-SelfSignedCertificate|Import-Certificate|msstore publish|Add-AppxPackage/);
  const workflow = fs.readFileSync(path.join(root, '.github/workflows/microsoft-store.yml'), 'utf8');
  assert.match(workflow, /workflow_dispatch/);
  assert.match(workflow, /MSSTORE_PUBLISHER:/);
  assert.doesNotMatch(workflow, /secrets\.|push:|pull_request:/);
});
