import { readFileSync } from 'node:fs'
import { expectedSchema, verifyManifest } from './verify.ts'

// Freeze pins must come independently from the controller; this command never derives them from the manifest.
const [manifestPath, root, freezePath] = process.argv.slice(2)
if (!manifestPath || !root || !freezePath || process.argv.length !== 5) {
  console.error(
    'Usage: node scripts/release/verify-release.mjs MANIFEST EVIDENCE_ROOT TRUSTED_FREEZE.json',
  )
  process.exitCode = 2
} else {
  try {
    const readJson = (path) => {
      const bytes = readFileSync(path)
      if (bytes.length > 16 * 1024 * 1024) throw new Error('JSON_BOUNDS')
      return JSON.parse(bytes.toString('utf8'))
    }
    const expected = expectedSchema.parse({
      ...readJson(freezePath),
      now: new Date().toISOString(),
    })
    const result = verifyManifest(readJson(manifestPath), root, expected)
    console.log(JSON.stringify(result, null, 2))
    process.exitCode = result.consistent && result.mode === 'evidence' ? 0 : 1
  } catch {
    console.error('MANIFEST_OR_FREEZE_UNREADABLE_OR_INVALID')
    process.exitCode = 2
  }
}
