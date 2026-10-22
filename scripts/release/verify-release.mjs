import { expectedSchema, readJsonFile, verifyManifest } from './verify.ts'

// Freeze pins must come independently from the controller; this command never derives them from the manifest.
const [manifestPath, root, freezePath] = process.argv.slice(2)
if (!manifestPath || !root || !freezePath || process.argv.length !== 5) {
  console.error(
    'Usage: node scripts/release/verify-release.mjs MANIFEST EVIDENCE_ROOT TRUSTED_FREEZE.json',
  )
  process.exitCode = 2
} else {
  try {
    const expected = expectedSchema.parse({
      ...readJsonFile(freezePath),
      now: new Date().toISOString(),
    })
    const result = verifyManifest(readJsonFile(manifestPath), root, expected)
    console.log(JSON.stringify(result, null, 2))
    process.exitCode = result.consistent && result.mode === 'evidence' ? 0 : 1
  } catch {
    console.error('MANIFEST_OR_FREEZE_UNREADABLE_OR_INVALID')
    process.exitCode = 2
  }
}
