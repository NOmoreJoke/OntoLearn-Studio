import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { lstat, readFile, readdir, readlink, writeFile } from 'node:fs/promises'
import path from 'node:path'
const root = '/workspace/release/linux-arm64-unpacked'
const identity = JSON.parse(await readFile('/opt/i06-main-identity.json', 'utf8'))
const files = {},
  symlinks = {}
async function walk(relative) {
  for (const name of (await readdir(path.join(root, relative))).sort()) {
    const item = path.join(relative, name),
      full = path.join(root, item),
      info = await lstat(full)
    if (info.isDirectory()) await walk(item)
    else if (info.isSymbolicLink()) symlinks[item] = await readlink(full)
    else if (info.isFile())
      files[item] = {
        sha256: createHash('sha256')
          .update(await readFile(full))
          .digest('hex'),
        bytes: info.size,
        mode: info.mode & 0o7777,
        uid: info.uid,
        gid: info.gid,
      }
  }
}
await walk('')
assert.ok(files['@ontolearndesktop'])
assert.ok(files['resources/app.asar'])
assert.ok(files['resources/engine/ontolearn-engine'])
assert.equal(files['chrome-sandbox'].uid, 0)
assert.equal(files['chrome-sandbox'].gid, 0)
assert.equal(files['chrome-sandbox'].mode, 0o4755)
await writeFile(
  process.argv[2],
  JSON.stringify(
    {
      productCandidate: identity.candidate,
      packageRoot: root,
      executable: root + '/@ontolearndesktop',
      files,
      symlinks,
    },
    null,
    2,
  ) + '\n',
)
