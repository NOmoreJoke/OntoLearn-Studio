import { spawnSync } from 'node:child_process'
import { mkdirSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
// pyshacl's frozen loader uses sys._MEIPASS/assets, not pyshacl/assets.
const hooksDir = resolve(root, 'build/pyinstaller-hooks')
mkdirSync(hooksDir, { recursive: true })
writeFileSync(
  resolve(hooksDir, 'hook-pyshacl.py'),
  [
    'from pathlib import Path',
    'from PyInstaller.utils.hooks import get_package_paths',
    '',
    '_, package_dir = get_package_paths("pyshacl")',
    'assets = Path(package_dir) / "assets"',
    'names = (',
    '    "dash.pickle", "dash.ttl", "schema.pickle", "schema.ttl",',
    '    "shacl-shacl.pickle", "shacl-shacl.ttl", "shacl.pickle", "shacl.ttl",',
    ')',
    'datas = []',
    'for name in names:',
    '    source = assets / name',
    '    if not source.is_file():',
    '        raise FileNotFoundError(source)',
    '    datas.append((str(source), "assets"))',
    '',
  ].join('\n'),
  'utf8',
)
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
    '--collect-data',
    'ontolearn_engine',
    // semantic.py / semantic_execution.py lazy-import the quality/ and
    // semantic_profile_* submodules inside execution branches; PyInstaller's
    // static analysis misses them unless they are collected explicitly.
    '--collect-submodules',
    'ontolearn_engine',
    '--additional-hooks-dir',
    hooksDir,
    '--hidden-import',
    'prettytable',
    '--hidden-import',
    'wcwidth',
    '--copy-metadata',
    'rdflib',
    '--copy-metadata',
    'pyparsing',
    '--copy-metadata',
    'pyshacl',
    '--copy-metadata',
    'owlrl',
    '--copy-metadata',
    'html5rdf',
    '--copy-metadata',
    'packaging',
    '--copy-metadata',
    'prettytable',
    '--copy-metadata',
    'wcwidth',
    '--add-data',
    `${resolve(root, 'packages/contracts/python/contract_v2.py')}:contracts/python`,
    '--add-data',
    `${resolve(root, 'packages/contracts/v2')}:contracts/v2`,
    '--add-data',
    `${resolve(root, 'uv.lock')}:provenance`,
    // Frozen learning runtime: baselines.verify() cross-checks these three
    // roots, so the T01 ledger works from sys._MEIPASS exactly like checkout.
    '--add-data',
    `${resolve(root, 'content/learning')}:content/learning`,
    '--add-data',
    `${resolve(root, 'tests/fixtures/product-baselines')}:tests/fixtures/product-baselines`,
    '--add-data',
    `${resolve(root, 'docs/prd/PRD-本体学习与落地Agent工作台.md')}:docs/prd`,
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
