import { lstatSync, openSync, fstatSync, readSync, closeSync, constants } from 'node:fs'
import { createHash } from 'node:crypto'
import { resolve, join } from 'node:path'
import { fileURLToPath } from 'node:url'

// Immutable historical generators, retained as evidence and never executed here.
const root = resolve(fileURLToPath(new URL('..', import.meta.url)))
const pins = [
  {
    path: 'docs/reviews/T01/designated-review-backlog-20261022/coverage/build_coverage.py',
    bytes: 15281,
    sha256: 'bf96c4ba086549d2445b5b40dad71a5b3f59a5cb7e78608e8b0b782d9a9add30',
  },
  {
    path: 'docs/reviews/T01/designated-review-backlog-20261022/preparation-scripts/build_inventory.py',
    bytes: 34744,
    sha256: '289bdc1f670cd76224340548b2167de732c9a142196b733ccc097c138e7cd57c',
  },
  {
    path: 'docs/reviews/T01/designated-review-backlog-20261022/preparation-scripts/build_submission.py',
    bytes: 12364,
    sha256: '364aabf6855b68a0436ab369bc527caf33c44e79735501959a71cfb6b1aeba8f',
  },
  {
    path: 'docs/reviews/T01/designated-review-backlog-20261022/preparation-scripts/verify_persistent_package.py',
    bytes: 2592,
    sha256: '6e24f10637204c2a78d73b4eee8f39fd48e639acee479cc6eed70cfbbe4aa0ed',
  },
]
for (const pin of pins) {
  let current = root
  for (const part of pin.path.split('/')) {
    current = join(current, part)
    if (lstatSync(current).isSymbolicLink())
      throw new Error(`Frozen evidence is a symlink: ${pin.path}`)
  }
  // Reject devices/FIFOs before open; nonblocking also covers replacement races.
  if (!lstatSync(current).isFile())
    throw new Error(`Frozen evidence is not a regular file: ${pin.path}`)
  const fd = openSync(
    current,
    constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0) | (constants.O_NONBLOCK ?? 0),
  )
  try {
    const before = fstatSync(fd)
    if (!before.isFile() || before.size !== pin.bytes)
      throw new Error(`Frozen evidence size differs: ${pin.path}`)
    const raw = Buffer.alloc(pin.bytes + 1)
    let offset = 0
    while (offset < raw.length) {
      const count = readSync(fd, raw, offset, raw.length - offset, null)
      if (count === 0) break
      offset += count
    }
    const after = fstatSync(fd)
    if (
      offset !== pin.bytes ||
      before.dev !== after.dev ||
      before.ino !== after.ino ||
      before.size !== after.size ||
      before.mtimeMs !== after.mtimeMs ||
      createHash('sha256').update(raw.subarray(0, offset)).digest('hex') !== pin.sha256
    )
      throw new Error(`Frozen evidence changed: ${pin.path}`)
  } finally {
    closeSync(fd)
  }
}
console.log(`Verified ${pins.length} immutable review source files.`)
