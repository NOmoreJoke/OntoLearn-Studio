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
    '--copy-metadata',
    'pyshacl',
    '--copy-metadata',
    'owlrl',
    '--copy-metadata',
    'packaging',
    '--copy-metadata',
    'prettytable',
    '--copy-metadata',
    'wcwidth',
    '--copy-metadata',
    'html5rdf',
    '--add-data',
    `${resolve(root, 'packages/contracts/python/contract_v2.py')}:contracts/python`,
    '--add-data',
    `${resolve(root, 'packages/contracts/v2')}:contracts/v2`,
    '--add-data',
    `${resolve(root, 'uv.lock')}:provenance`,
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
