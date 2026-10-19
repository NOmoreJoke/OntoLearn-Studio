import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
const manifest = JSON.parse(
  readFileSync(new URL('../docs/source-manifest.json', import.meta.url), 'utf8'),
)
for (const file of manifest.files) {
  const data = readFileSync(new URL(`../${file.path}`, import.meta.url))
  const actual = createHash('sha256').update(data).digest('hex')
  if (actual !== file.sha256) throw new Error(`归档文件已变化：${file.path}`)
}
console.log(`已核对 ${manifest.files.length} 个归档源文件。`)
