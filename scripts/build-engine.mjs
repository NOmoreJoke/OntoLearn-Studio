import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const result = spawnSync(
  'uv',
  [
    'run',
    '--frozen',
    'pyinstaller',
    '--noconfirm',
    '--clean',
    '--onedir',
    '--name',
    'ontolearn-engine',
    '--distpath',
    'build/engine',
    '--workpath',
    'build/pyinstaller',
    '--specpath',
    'build',
    'packages/engine/entrypoint.py',
  ],
  { cwd: root, stdio: 'inherit', shell: false },
)
if (result.error) {
  console.error('需要先安装 uv 并执行 uv sync --frozen。')
  process.exit(1)
}
process.exit(result.status ?? 1)
