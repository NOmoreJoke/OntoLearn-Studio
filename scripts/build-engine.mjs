import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const inventory = spawnSync('uv', ['run', '--frozen', 'python', 'scripts/i05-build-inventory.py'], {
  cwd: root,
  stdio: 'inherit',
  shell: false,
})
if (inventory.error || inventory.status !== 0) process.exit(inventory.status ?? 1)
const result = spawnSync(
  'uv',
  [
    'run',
    '--frozen',
    'pyinstaller',
    '--noconfirm',
    '--clean',
    '--onedir',
    '--collect-all',
    'rdflib',
    '--collect-all',
    'pyshacl',
    '--collect-all',
    'owlrl',
    '--collect-all',
    'html5rdf',
    '--collect-data',
    'ontolearn_engine',
    '--copy-metadata',
    'rdflib',
    '--copy-metadata',
    'pyparsing',
    '--recursive-copy-metadata',
    'pyshacl',
    '--add-data',
    `${resolve(root, 'build/i05-inventory')}:i05-inventory`,
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
  {
    cwd: root,
    stdio: 'inherit',
    shell: false,
    env: { ...process.env, PYINSTALLER_CONFIG_DIR: resolve(root, 'build/pyinstaller-cache') },
  },
)
if (result.error) {
  console.error('需要先安装 uv 并执行 uv sync --frozen。')
  process.exit(1)
}
process.exit(result.status ?? 1)
