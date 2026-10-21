import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const sourceRef = '0475d0ec6c486a63c7e8f62f11f35181da6b2576'
// Exact approved source/data inputs, not a discovery or whole-package adoption.
const fixedInputs = [
  [
    'packages/engine/src/ontolearn_engine/resources.py',
    2927,
    '2361c55da7983e46fbdd08e50fc3ec48b281d2c76d0021f82fd94ab50ca54274',
  ],
  [
    'packages/engine/src/ontolearn_engine/semantic.py',
    52609,
    '5a3a53fc79928a7aa7de280a8477541db4053ec9b2bec489bf28a2ad4e935549',
  ],
  [
    'packages/engine/src/ontolearn_engine/semantic_error_adapter.py',
    15426,
    '0572b4730ba1ac28192e84633633d7da222e6603ff7da811c84e1f368eb55014',
  ],
  [
    'packages/engine/src/ontolearn_engine/semantic_execution.py',
    32917,
    'cc701dba39cdeb7f2ae281dfd4a9580b879b9e85f34d3c87a09a3414e7c32731',
  ],
  [
    'packages/engine/src/ontolearn_engine/semantic_offline.py',
    1351,
    '4897d9c6a07756d5f8ed4908b4b7a28ca96c67b2670753b74f73e41bf4b67488',
  ],
  [
    'packages/engine/src/ontolearn_engine/semantic_profile_probe.py',
    13391,
    '2b2dabd91745b4b4c2a3fad39b6386e4edd985189336bf029d9b07a638fc7bf6',
  ],
  [
    'packages/engine/src/ontolearn_engine/semantic_query.py',
    6448,
    'fe8e600de7c0b300038ba0c952497cb8fbbf30f741f1e0d5e1bba78afef8670f',
  ],
  [
    'packages/engine/src/ontolearn_engine/semantic_samples.py',
    33858,
    '387278fa37006c9cdb3b08f1c7e7d6b8c3f0d5fbdaecb554fe02f310ec93cdb9',
  ],
  [
    'packages/engine/src/ontolearn_engine/semantic_scopes.py',
    13051,
    'aa8f1231df09332e9f02d96e3c8e4ef4cb64d4b3fa28067babcd3431de820ebf',
  ],
  [
    'packages/engine/src/ontolearn_engine/semantic_turtle.py',
    33916,
    '4180feb9d0c775669b65338e1cfb37a8d5bb7f3ce155b4804dd53a43efad5214',
  ],
  [
    'packages/engine/src/ontolearn_engine/quality/__init__.py',
    548,
    '9a5130c2fdbe376e5e4c15e68085f01724847ff13e9b2c195cf270e476806d9c',
  ],
  [
    'packages/engine/src/ontolearn_engine/quality/rule_calendar.py',
    4047,
    '6a2e43b029f7069e398f696ff19948d9e806f06fecd9a1e239b889a55e528aec',
  ],
  [
    'packages/engine/src/ontolearn_engine/quality/rule_comparator.py',
    1750,
    '9a495876a182d1cad4cac86bb4651c1627e4afc37e1bf9bb3d62be6bb0e95ff2',
  ],
  [
    'packages/engine/src/ontolearn_engine/quality/rule_firing.py',
    19149,
    '5116aa3e96ae10e7f37eb7afddceef50879869d38af116f9c794437edf49243c',
  ],
  [
    'packages/engine/src/ontolearn_engine/quality/rule_numbers.py',
    7372,
    '6b080a55bd8f4af1a1120b55448e02a1a442c231a32ab575ce6e82de054164f9',
  ],
  [
    'packages/engine/src/ontolearn_engine/quality/rule_profile.py',
    11987,
    'b40b73f65f474cda32ac42caeeb837ad6470a7daeeba9013d8f69e7f0c5a261c',
  ],
  [
    'packages/engine/src/ontolearn_engine/quality/rule_terms.py',
    6176,
    '218c4790e9b35236e393407b5b4e0207890d46fe3ea48a9a69e26aa08ddba1d1',
  ],
  [
    'docs/iterations/I05/profile-probe-inputs.json',
    1839011,
    '6c6ffc3a1a57d1817583c0a71d24e2847cc5d2d673848878c6e6e72dfe6c39de',
  ],
  [
    'packages/engine/pyproject.toml',
    398,
    'bcc8825b1f2902a66ae539e687df57e5b2554247f48a48a65215601a77958365',
  ],
  ['uv.lock', 28440, '86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73'],
  [
    'packages/contracts/python/contract_v2.py',
    20174,
    '0dc96a67cc47a03843a783cc47e649f13d5b5b80a43d520d0f6963b408d274fe',
  ],
  [
    'packages/contracts/v2/binding-regressions.json',
    123964,
    '9601d6d0a31e3e71078ac2562c6b8501c1292bc2be71de742e40c2fc54512a24',
  ],
  [
    'packages/contracts/v2/dependencies.json',
    1438,
    'dee118b368915df4172a77b875d31ce29ad8374cb5fce3915678f7f950cedad4',
  ],
  [
    'packages/contracts/v2/errors.json',
    14400,
    '6986be7cb6742fe955f6ad55b5f1c8565ead3b8b27b80ddfbcdd593187e181f1',
  ],
  [
    'packages/contracts/v2/fixtures.json',
    472098,
    '32031804abf3283e87f070ffbfc3f95cf627f6b71e7bc49711faaff52ec31ad6',
  ],
  [
    'packages/contracts/v2/frame-fixtures.json',
    17537,
    '8e9a142ff04e908cc286c15702cd18b6c2ce9453490585d0855c3f62995dd2e5',
  ],
  [
    'packages/contracts/v2/registry.json',
    13039,
    '59bfb09bbb142f56ff07e759e0d964d5910fa861c6a16edcf5cfa5e47f920efb',
  ],
  [
    'packages/contracts/v2/schema.json',
    122889,
    '9215266523f539c81282bbc96ca88de52b79c99ef39f7696b3a49c58fa7a2b79',
  ],
  [
    'packages/contracts/v2/states.json',
    716,
    'ab54cac024f0f6b31a8a229198ae1c4ab13f63ff88184cdcef78113b9e893416',
  ],
  [
    'packages/engine/src/ontolearn_engine/__init__.py',
    101,
    '4b8460a6ccc649f44188171c3d4c0c9e58e1204c711462d9ecf0aff12135684f',
  ],
  [
    'packages/engine/src/ontolearn_engine/__main__.py',
    489,
    '1fa0f9711a4d90db6fe8ef6c0948aebd93c910526838d6d41fac8a00a568c1d9',
  ],
  [
    'packages/engine/src/ontolearn_engine/contract_probe.py',
    2334,
    '2f86f43d186960ecb890ec98748857a9e8bca181ac6e7dd348db075693c686ea',
  ],
  [
    'packages/engine/src/ontolearn_engine/coordinator.py',
    29559,
    '597d74e318645d0ae4e7152acc29487efc37cb23b501404e60b21f5ed87fc7cb',
  ],
  [
    'packages/engine/src/ontolearn_engine/invalidation-v2.json',
    1745,
    'a4c821797f40adc68c233d3c2bd2273fcabbc449871117a86881ee2e60f13e12',
  ],
  [
    'packages/engine/src/ontolearn_engine/invalidation.py',
    1329,
    'a5e8165f4e8814da387558c89b8b175ac4bcc0e57223b9278f44a8c5120e1ca3',
  ],
  [
    'packages/engine/src/ontolearn_engine/job_store.py',
    64853,
    '42cd05b91f03f4ec9d4d38d49e621094d0246b8b898385032d7c3005a0afd4f2',
  ],
  [
    'packages/engine/src/ontolearn_engine/memory_guard.py',
    7851,
    'f01e1cf25211559bde24c48dceb9d20b2b48335bca19a6ec8015f328db4502ca',
  ],
  [
    'packages/engine/src/ontolearn_engine/process_environment.py',
    741,
    '9a1d305201576cc6cdefa06e89f24b308049d597fd5cb04be950a28eae2f5ef5',
  ],
  [
    'packages/engine/src/ontolearn_engine/protocol.py',
    3770,
    '34f85a3572276dafcb4ef5dceda426c4b8870a89344a0992684b96ae23218ab2',
  ],
  [
    'packages/engine/src/ontolearn_engine/rdf_snapshot.py',
    2530,
    '7cca115fa77e0926a632ba58d404ed39071f7dcfb8d52af2d212e89d36b2309a',
  ],
  [
    'packages/engine/src/ontolearn_engine/storage.py',
    55364,
    '4abf1082f1b864eb9efa155c7cbc890ef70cb196f30e09ad12629ce7a0cf6842',
  ],
  [
    'packages/engine/src/ontolearn_engine/storage_probe.py',
    5611,
    '01415c8c904ad75bf8f6e2bf48430bd04211e0899bee81c490cee9dfe42f90f2',
  ],
  [
    'packages/engine/src/ontolearn_engine/worker.py',
    9314,
    '2fa848aa3a2148e59a24f01c9333701f0f03eed95cffe55a0a78b74f1d06f2f0',
  ],
]
const distributions = [
  'rdflib',
  'pyshacl',
  'pyparsing',
  'owlrl',
  'html5rdf',
  'prettytable',
  'wcwidth',
  'packaging',
]
const excluded = [
  'ontolearn_engine.quality.definitions',
  'ontolearn_engine.quality.planning',
  'ontolearn_engine.quality.rule_revalidation',
]
const sha256 = (data) => createHash('sha256').update(data).digest('hex')
function run(command, args, options = {}) {
  const result = spawnSync(command, args, { cwd: root, shell: false, ...options })
  if (result.error || result.status !== 0) throw new Error('ENGINE_BUILD_PRECONDITION_FAILED')
  return result.stdout?.toString('utf8').trim() ?? ''
}

try {
  const files = fixedInputs.map(([path, bytes, expectedSha256]) => {
    const data = readFileSync(resolve(root, path))
    const digest = sha256(data)
    if (data.length !== bytes || digest !== expectedSha256) {
      throw new Error('ENGINE_BUILD_INPUT_CHANGED')
    }
    return { path, bytes, sha256: digest }
  })
  const writers = ['scripts/build-engine.mjs', 'packages/engine/entrypoint.py']
  const guardedPaths = [...files.map((item) => item.path), ...writers]
  run('git', ['diff', '--exit-code', 'HEAD', '--', ...guardedPaths], { stdio: 'pipe' })
  const combinationRef = run('git', ['rev-parse', 'HEAD'], { stdio: 'pipe' })
  const writerInputs = writers.map((path) => {
    const data = readFileSync(resolve(root, path))
    return { path, bytes: data.length, sha256: sha256(data) }
  })
  const metadataCode = String.raw`
import hashlib, importlib.metadata, json, sys
from pathlib import Path
expected = {'rdflib':'7.6.0','pyshacl':'0.30.1','pyparsing':'3.3.3','owlrl':'7.6.2',
            'html5rdf':'1.2.1','prettytable':'3.18.0','wcwidth':'0.9.2','packaging':'26.3'}
root = Path.cwd()
if Path(sys.prefix).resolve() != root / '.venv' or sys.version_info[:2] != (3, 12):
    raise SystemExit('ENGINE_BUILD_ENVIRONMENT_INVALID')
result = []
for name, version in expected.items():
    dist = importlib.metadata.distribution(name)
    if dist.version != version:
        raise SystemExit('ENGINE_BUILD_DISTRIBUTION_CHANGED')
    entries = []
    for member in dist.files or ():
        path = Path(dist.locate_file(member)).resolve()
        if not path.is_relative_to(root / '.venv'):
            raise SystemExit('ENGINE_BUILD_DISTRIBUTION_PATH_INVALID')
        if not path.is_file():
            raise SystemExit('ENGINE_BUILD_DISTRIBUTION_FILE_MISSING')
        raw = path.read_bytes()
        relative = str(member).replace('\\', '/')
        leaf = path.name.lower()
        license_file = any(word in leaf for word in ('license', 'licence', 'copying', 'notice'))
        entries.append({'path':relative,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                        'licenseFile':license_file})
    licenses = [entry for entry in entries if entry['licenseFile']]
    if not licenses:
        raise SystemExit('ENGINE_BUILD_LICENSE_MISSING')
    result.append({'name':name,'version':version,'files':entries,'licenses':licenses,
                   'requiresDist':dist.requires or [],
                   'licenseExpression':dist.metadata.get('License-Expression'),
                   'licenseField':dist.metadata.get('License')})
print(json.dumps({'python':sys.version,'pyinstaller':importlib.metadata.version('pyinstaller'),
                  'engine':importlib.metadata.version('ontolearn-engine'),
                  'distributions':result},ensure_ascii=False))
`
  const metadata = JSON.parse(
    run('uv', ['run', '--frozen', 'python', '-c', metadataCode], {
      stdio: ['ignore', 'pipe', 'inherit'],
    }),
  )
  if (metadata.pyinstaller !== '6.22.3' || metadata.engine !== '0.1.0') {
    throw new Error('ENGINE_BUILD_TOOL_VERSION_CHANGED')
  }
  const canonicalModules = files
    .slice(0, 18)
    .filter((item) => item.path.startsWith('packages/engine/src/'))
    .map((item) => item.path.slice('packages/engine/src/'.length, -3).replaceAll('/', '.'))
    .map((name) => name.replace(/\.__init__$/, ''))
  if (canonicalModules.length !== 17 || new Set(canonicalModules).size !== 17) {
    throw new Error('ENGINE_BUILD_MODULE_SET_INVALID')
  }
  const provenancePath = resolve(root, 'build/profile-d2/provenance/d2-build-inputs.json')
  const args = [
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
    '--collect-all',
    'pyshacl',
    '--collect-all',
    'owlrl',
    '--collect-all',
    'html5rdf',
  ]
  for (const name of distributions) args.push('--copy-metadata', name)
  for (const name of [...canonicalModules, 'prettytable', 'wcwidth', 'packaging']) {
    args.push('--hidden-import', name)
  }
  for (const name of excluded) args.push('--exclude-module', name)
  for (const [source, destination] of [
    ['packages/contracts/python/contract_v2.py', 'contracts/python'],
    ['packages/contracts/v2', 'contracts/v2'],
    ['uv.lock', 'provenance'],
    ['docs/iterations/I05/profile-probe-inputs.json', 'provenance/i05'],
    ['build/profile-d2/provenance/d2-build-inputs.json', 'provenance'],
  ])
    args.push('--add-data', `${resolve(root, source)}:${destination}`)
  args.push(
    '--name',
    'ontolearn-engine',
    '--distpath',
    'build/engine',
    '--workpath',
    'build/pyinstaller',
    '--specpath',
    'build',
    'packages/engine/entrypoint.py',
  )
  mkdirSync(dirname(provenancePath), { recursive: true })
  writeFileSync(
    provenancePath,
    JSON.stringify(
      {
        format: 'ontolearn-d2-build-inputs/1',
        combinationRef,
        sourceRef,
        files,
        writerInputs,
        canonicalModules,
        excludedModules: excluded,
        toolsAndDistributions: metadata,
        command: ['uv', ...args],
        pythonOptimize: 0,
        scope: 'build input commitments; final archive and engine hashes are external evidence',
      },
      null,
      2,
    ) + '\n',
  )
  const result = spawnSync('uv', args, {
    cwd: root,
    stdio: 'inherit',
    shell: false,
    env: { ...process.env, PYINSTALLER_CONFIG_DIR: resolve(root, 'build/pyinstaller-cache') },
  })
  if (result.error) throw new Error('ENGINE_BUILD_LAUNCH_FAILED')
  process.exitCode = result.status ?? 1
} catch (error) {
  console.error(error instanceof Error ? error.message : 'ENGINE_BUILD_FAILED')
  process.exitCode = 1
}
