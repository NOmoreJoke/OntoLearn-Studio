import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { readFile, readdir, writeFile, lstat, mkdir, copyFile } from 'node:fs/promises'
import path from 'node:path'

const root = '/probe-data/main-platform'
const inputs = JSON.parse(await readFile(path.join(root, 'scan-input.json'), 'utf8'))
const forbidden = [
  'I06_MAIN_SYNTHETIC_SECRET_',
  'I06_RESPONSE_PRIVATE_MARKER_',
  'PUBLIC_VALUE_',
  'PRIVATE_VALUE_SENTINEL_',
  'PRIVATE_DERIVED_SENTINEL_',
]
async function filesUnder(directory) {
  const files = []
  for (const name of await readdir(directory)) {
    const file = path.join(directory, name),
      info = await lstat(file)
    if (info.isDirectory()) files.push(...(await filesUnder(file)))
    else if (info.isFile()) files.push(file)
  }
  return files
}
const ownedFiles = [
  ...(await filesUnder(root)),
  ...(await filesUnder('/probe-data/fixtures')),
  ...(await filesUnder('/probe-data/profiles')),
]
const logs = ownedFiles.filter((file) => file.endsWith('.log'))
await mkdir(path.join(root, 'fixture-logs'))
for (const file of logs) {
  const bytes = await readFile(file)
  for (const marker of forbidden)
    assert.equal(bytes.includes(Buffer.from(marker)), false, 'ORDINARY_LOG_CONTAINS_PRIVATE_BYTES')
  if (file.startsWith('/probe-data/fixtures/'))
    await copyFile(
      file,
      path.join(
        root,
        'fixture-logs',
        file.slice('/probe-data/fixtures/'.length).replaceAll('/', '--'),
      ),
    )
}
let privateFiles = 0
async function privateWalk(directory) {
  for (const name of await readdir(directory)) {
    const file = path.join(directory, name),
      info = await lstat(file)
    if (info.isDirectory()) await privateWalk(file)
    else if (info.isFile()) {
      privateFiles++
      const bytes = await readFile(file)
      for (const marker of forbidden)
        assert.equal(
          bytes.includes(Buffer.from(marker)),
          false,
          'PRIVATE_METADATA_OR_CIPHERTEXT_PLAINTEXT_LEAK',
        )
    }
  }
}
for (const profile of await readdir('/probe-data/profiles')) {
  const directory = path.join('/probe-data/profiles', profile, 'model-gateway-private-v1')
  try {
    await privateWalk(directory)
  } catch (error) {
    if (error.code !== 'ENOENT') throw error
  }
}
// Exact outgoing bodies are different from source rows that intentionally already exist in Store.
const databases = []
const rawDatabaseFiles = []
for (const file of ownedFiles.filter(
  (file) =>
    file.startsWith('/probe-data/fixtures/') && /\.sqlite(?:-(?:wal|shm|journal))?$/.test(file),
)) {
  const bytes = await readFile(file)
  for (const marker of ['I06_MAIN_SYNTHETIC_SECRET_', 'I06_RESPONSE_PRIVATE_MARKER_']) {
    assert.equal(bytes.includes(Buffer.from(marker)), false, 'PRIVATE_BYTES_IN_SQLITE_RAW_PAGES')
    assert.equal(
      bytes.includes(Buffer.from(marker, 'utf16le')),
      false,
      'PRIVATE_BYTES_IN_UTF16_SQLITE_RAW_PAGES',
    )
  }
  rawDatabaseFiles.push({ path: file, bytes: bytes.length })
}
for (const file of ownedFiles.filter(
  (file) => file.startsWith('/probe-data/fixtures/') && file.endsWith('.sqlite'),
)) {
  const database = JSON.parse(
    execFileSync(
      '/workspace/.venv/bin/python',
      [
        '-I',
        '/workspace/tests/i06-main-platform/scan-database.py',
        file,
        file === inputs.database ? 'require-source' : 'source-optional',
        ...inputs.receiverBodyFiles.map((name) => path.join(root, name)),
      ],
      { encoding: 'utf8' },
    ),
  )
  assert.equal(database.result, 'passed')
  databases.push({ path: file, ...database })
}
assert.ok(databases.some((database) => database.path === inputs.database))
await writeFile(
  path.join(root, 'leak-scan.json'),
  JSON.stringify(
    {
      result: 'passed',
      ordinaryLogFiles: logs.length,
      privateGatewayFiles: privateFiles,
      databases,
      rawDatabaseFiles,
      exportEntry:
        'No project export entry exists in this candidate; actual export artifact scan unavailable.',
    },
    null,
    2,
  ) + '\n',
)
