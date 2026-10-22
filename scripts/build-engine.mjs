import { spawnSync } from 'node:child_process'
import { randomUUID, createHash } from 'node:crypto'
import * as fs from 'node:fs'
import { dirname, isAbsolute, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const defaultRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/
const distributions = [
  'rdflib',
  'pyparsing',
  'pyshacl',
  'owlrl',
  'packaging',
  'prettytable',
  'wcwidth',
  'html5rdf',
]
const prepareProgram = [
  'import json,sys',
  'from pathlib import Path',
  'from ontolearn_engine.semantic_build_provenance import prepare_build',
  'print(json.dumps(prepare_build(Path(sys.argv[1]),Path(sys.argv[2]))))',
].join('\n')
const finalizeProgram = [
  'import json,sys',
  'from pathlib import Path',
  'from ontolearn_engine.semantic_build_provenance import finalize_build',
  'print(json.dumps(finalize_build(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))))',
].join('\n')

function fail(code) {
  throw new Error(code)
}

function contained(root, path) {
  const suffix = relative(root, path)
  return suffix !== '' && !isAbsolute(suffix) && suffix !== '..' && !suffix.startsWith('../')
}

function entry(io, path) {
  try {
    return io.lstatSync(path)
  } catch (error) {
    if (error && error.code === 'ENOENT') return null
    throw error
  }
}

function directory(io, root, path) {
  if (!contained(root, path)) fail('BUILD_ENGINE_DIRECTORY_INVALID')
  // Build/staging ancestors must not redirect writes outside this checkout.
  let current = path
  while (current !== root) {
    const info = entry(io, current)
    if (info !== null) {
      if (!info.isDirectory() || info.isSymbolicLink()) fail('BUILD_ENGINE_DIRECTORY_INVALID')
    }
    current = dirname(current)
  }
  io.mkdirSync(path, { recursive: true })
}

function helper(run, root, runRoot, program, arguments_, keys) {
  const result = run('uv', ['run', '--frozen', 'python', '-c', program, ...arguments_], {
    cwd: root,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
    shell: false,
    maxBuffer: 4 * 1024 * 1024,
    env: { ...process.env, PYINSTALLER_CONFIG_DIR: resolve(runRoot, 'cache') },
  })
  if (typeof result.stderr === 'string' && result.stderr) process.stderr.write(result.stderr)
  if (result.error || result.status !== 0) {
    if (typeof result.stdout === 'string' && result.stdout) process.stderr.write(result.stdout)
    if (result.error) process.stderr.write(`${String(result.error)}\n`)
    fail('BUILD_ENGINE_PROVENANCE_HELPER_FAILED')
  }
  if (typeof result.stdout !== 'string' || Buffer.byteLength(result.stdout) > 65536)
    fail('BUILD_ENGINE_HELPER_OUTPUT_INVALID')
  let value
  try {
    value = JSON.parse(result.stdout)
  } catch {
    fail('BUILD_ENGINE_HELPER_OUTPUT_INVALID')
  }
  if (
    value === null ||
    typeof value !== 'object' ||
    Array.isArray(value) ||
    Object.keys(value).length !== keys.length ||
    keys.some((key) => typeof value[key] !== 'string')
  )
    fail('BUILD_ENGINE_HELPER_OUTPUT_INVALID')
  return value
}

// Private programmatic build API; no application CLI accepting arbitrary paths.
export function publishEngineCopy({ root, runRoot, engineDirectory, token, io = fs }) {
  if (
    typeof root !== 'string' ||
    !isAbsolute(root) ||
    root !== resolve(root) ||
    !uuidPattern.test(token) ||
    runRoot !== resolve(root, 'build/i05-provenance', token)
  )
    fail('BUILD_ENGINE_ARTIFACT_PATH_INVALID')
  if (engineDirectory !== resolve(runRoot, 'dist/ontolearn-engine'))
    fail('BUILD_ENGINE_ARTIFACT_PATH_INVALID')
  let source = engineDirectory
  while (source !== root) {
    const info = entry(io, source)
    if (info === null || !info.isDirectory() || info.isSymbolicLink())
      fail('BUILD_ENGINE_ARTIFACT_PATH_INVALID')
    source = dirname(source)
  }
  const stagingParent = resolve(root, 'build/engine')
  directory(io, root, stagingParent)
  const target = resolve(stagingParent, 'ontolearn-engine')
  const temporary = resolve(stagingParent, `.ontolearn-engine-${token}`)
  if (entry(io, temporary) !== null) fail('BUILD_ENGINE_STAGING_EXISTS')
  io.cpSync(engineDirectory, temporary, {
    recursive: true,
    force: false,
    errorOnExist: true,
    preserveTimestamps: true,
    verbatimSymlinks: true,
  })
  let archived = null
  if (entry(io, target) !== null) {
    const archiveRoot = resolve(runRoot, 'staging-archive')
    directory(io, root, archiveRoot)
    archived = resolve(archiveRoot, 'ontolearn-engine')
    if (entry(io, archived) !== null) fail('BUILD_ENGINE_STAGING_EXISTS')
    io.renameSync(target, archived)
  }
  try {
    io.renameSync(temporary, target)
  } catch (error) {
    // Publication failure restores staging; immutable run artifacts stay intact.
    if (archived !== null && entry(io, target) === null) io.renameSync(archived, target)
    throw error
  }
  return target
}

export function buildEngine({
  repositoryRoot = defaultRoot,
  run = spawnSync,
  io = fs,
  uuid = randomUUID,
} = {}) {
  const root = resolve(repositoryRoot)
  const token = uuid()
  if (!uuidPattern.test(token)) fail('BUILD_ENGINE_ID_INVALID')
  const parent = resolve(root, 'build/i05-provenance')
  directory(io, root, parent)
  const runRoot = resolve(parent, token)
  if (entry(io, runRoot) !== null) fail('BUILD_ENGINE_OUTPUT_EXISTS')
  const prepared = helper(
    run,
    root,
    runRoot,
    prepareProgram,
    [root, runRoot],
    ['provenancePath', 'contractPath', 'generatedDir', 'anchorPath'],
  )
  const expected = {
    provenancePath: resolve(runRoot, 'provenance/i05-private-build-provenance-v1.json'),
    contractPath: resolve(runRoot, 'provenance/i05-private-contract-v1.json'),
    generatedDir: resolve(runRoot, 'generated'),
    anchorPath: resolve(runRoot, 'generated/_i05_private_build_anchor.py'),
  }
  if (Object.keys(expected).some((key) => prepared[key] !== expected[key]))
    fail('BUILD_ENGINE_HELPER_PATH_INVALID')
  const engineDirectory = resolve(runRoot, 'dist/ontolearn-engine')
  const result = run(
    'uv',
    [
      'run',
      '--frozen',
      'pyinstaller',
      '--noconfirm',
      '--clean',
      '--onedir',
      '--optimize',
      '0',
      '--paths',
      prepared.generatedDir,
      '--hidden-import',
      '_i05_private_build_anchor',
      '--hidden-import',
      'ontolearn_engine.semantic_build_provenance',
      ...distributions.flatMap((name) => ['--collect-all', name]),
      '--collect-data',
      'ontolearn_engine',
      ...distributions.flatMap((name) => ['--copy-metadata', name]),
      '--add-data',
      `${resolve(root, 'packages/contracts/python/contract_v2.py')}:contracts/python`,
      '--add-data',
      `${resolve(root, 'packages/contracts/v2')}:contracts/v2`,
      '--add-data',
      `${resolve(root, 'uv.lock')}:provenance`,
      '--add-data',
      `${prepared.provenancePath}:provenance`,
      '--add-data',
      `${prepared.contractPath}:provenance`,
      '--name',
      'ontolearn-engine',
      '--distpath',
      resolve(runRoot, 'dist'),
      '--workpath',
      resolve(runRoot, 'pyinstaller'),
      '--specpath',
      resolve(runRoot, 'spec'),
      'packages/engine/entrypoint.py',
    ],
    {
      cwd: root,
      stdio: 'inherit',
      shell: false,
      env: { ...process.env, PYINSTALLER_CONFIG_DIR: resolve(runRoot, 'cache') },
    },
  )
  if (result.error || result.status !== 0) fail('BUILD_ENGINE_PYINSTALLER_FAILED')
  const finalized = helper(
    run,
    root,
    runRoot,
    finalizeProgram,
    [root, runRoot, engineDirectory],
    ['bindingPath', 'bindingSha256', 'engineDirectory', 'provenanceSha256'],
  )
  if (
    finalized.bindingPath !== resolve(runRoot, 'artifact-binding-v1.json') ||
    finalized.engineDirectory !== engineDirectory ||
    !/^[0-9a-f]{64}$/.test(finalized.bindingSha256) ||
    !/^[0-9a-f]{64}$/.test(finalized.provenanceSha256)
  )
    fail('BUILD_ENGINE_BINDING_INVALID')
  const stagingDirectory = publishEngineCopy({ root, runRoot, engineDirectory, token, io })
  return { ...finalized, stagingDirectory, rootApproved: false }
}

const parityImports = [
  'ontolearn_engine',
  'ontolearn_engine.quality',
  'ontolearn_engine.quality.rule_calendar',
  'ontolearn_engine.quality.rule_comparator',
  'ontolearn_engine.quality.rule_firing',
  'ontolearn_engine.quality.rule_numbers',
  'ontolearn_engine.quality.rule_profile',
  'ontolearn_engine.quality.rule_revalidation',
  'ontolearn_engine.quality.rule_terms',
  'ontolearn_engine.resources',
  'ontolearn_engine.semantic',
  'ontolearn_engine.semantic_error_adapter',
  'ontolearn_engine.semantic_execution',
  'ontolearn_engine.semantic_offline',
  'ontolearn_engine.semantic_profile_directsteps',
  'ontolearn_engine.semantic_profile_input',
  'ontolearn_engine.semantic_profile_production',
  'ontolearn_engine.semantic_profile_restore',
  'ontolearn_engine.semantic_profile_restore_budget',
  'ontolearn_engine.semantic_query',
  'ontolearn_engine.semantic_scopes',
  'ontolearn_engine.semantic_turtle',
  'ontolearn_engine.semantic_source_package_probe',
  'ontolearn_engine.semantic_build_provenance',
  '_i05_semantic_parity_build_anchor',
]
const parityExcludes = [
  'ontolearn_engine.quality.definitions',
  'ontolearn_engine.quality.planning',
  'ontolearn_engine.__main__',
  'ontolearn_engine.worker',
  'ontolearn_engine.coordinator',
  'ontolearn_engine.job_store',
  'ontolearn_engine.storage',
  'ontolearn_engine.storage_probe',
  'ontolearn_engine.protocol',
  'ontolearn_engine.semantic_samples',
]

const parityProfile = 'i05-source-package-parity'
const parityProvenance = 'provenance/i05/source-package-parity-build.json'
const parityContract = 'provenance/i05/source-package-parity-private-contract-v1.json'
const parityAnchor = '_i05_semantic_parity_build_anchor'

function parityEnvironment(root, runRoot) {
  const env = {}
  // This is the complete child environment, rather than a receipt of selected keys.
  for (const key of ['PATH', 'HOME', 'LANG', 'LC_ALL', 'LC_CTYPE', 'SYSTEMROOT', 'WINDIR'])
    if (typeof process.env[key] === 'string') env[key] = process.env[key]
  return {
    ...env,
    VIRTUAL_ENV: resolve(root, '.venv'),
    UV_PROJECT_ENVIRONMENT: resolve(root, '.venv'),
    UV_NO_SYNC: '1',
    UV_OFFLINE: '1',
    UV_PYTHON_DOWNLOADS: 'never',
    UV_CACHE_DIR: resolve(runRoot, 'evidence/cache/uv'),
    PYTHONDONTWRITEBYTECODE: '1',
    PYTHONNOUSERSITE: '1',
    PYTHONPATH: resolve(root, 'packages/engine/src'),
    TMPDIR: resolve(runRoot, 'evidence/tmp'),
    PYINSTALLER_CONFIG_DIR: resolve(runRoot, 'evidence/cache/pyinstaller'),
  }
}

function parityStream(io, path) {
  const info = io.lstatSync(path)
  if (!info.isFile() || info.isSymbolicLink()) fail('BUILD_PARITY_EVIDENCE_IO_FAILED')
  const fd = io.openSync(path, 'r')
  const hash = createHash('sha256')
  const buffer = Buffer.alloc(65536)
  let bytes = 0
  try {
    const opened = io.fstatSync(fd)
    if (!opened.isFile() || opened.ino !== info.ino || opened.dev !== info.dev)
      fail('BUILD_PARITY_EVIDENCE_IO_FAILED')
    for (;;) {
      const count = io.readSync(fd, buffer, 0, buffer.length, null)
      if (count === 0) break
      hash.update(buffer.subarray(0, count))
      bytes += count
    }
    const finished = io.fstatSync(fd)
    if (
      opened.size !== finished.size ||
      opened.mtimeMs !== finished.mtimeMs ||
      bytes !== finished.size
    )
      fail('BUILD_PARITY_EVIDENCE_IO_FAILED')
  } finally {
    io.closeSync(fd)
  }
  const after = io.lstatSync(path)
  if (
    bytes !== info.size ||
    info.size !== after.size ||
    info.ino !== after.ino ||
    info.dev !== after.dev ||
    info.mtimeMs !== after.mtimeMs
  )
    fail('BUILD_PARITY_EVIDENCE_IO_FAILED')
  return { path, bytes, sha256: hash.digest('hex') }
}

function parityControl(raw, keys) {
  const text = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(raw)
  let offset = 0
  const white = () => {
    while (/[ \t\r\n]/.test(text[offset] ?? '') && offset < text.length) offset++
  }
  const literal = () => {
    white()
    if (text[offset] !== '"') throw new Error('CONTROL_INVALID')
    const start = offset++
    while (offset < text.length) {
      const char = text[offset++]
      if (char === '\\') {
        offset++
        continue
      }
      if (char === '"') return JSON.parse(text.slice(start, offset))
    }
    throw new Error('CONTROL_INVALID')
  }
  white()
  if (text[offset++] !== '{') throw new Error('CONTROL_INVALID')
  const value = Object.create(null)
  white()
  if (text[offset] === '}') offset++
  else
    for (;;) {
      const key = literal()
      white()
      if (Object.hasOwn(value, key) || text[offset++] !== ':') throw new Error('CONTROL_INVALID')
      value[key] = literal()
      white()
      const next = text[offset++]
      if (next === '}') break
      if (next !== ',') throw new Error('CONTROL_INVALID')
    }
  white()
  if (
    offset !== text.length ||
    Object.keys(value).length !== keys.length ||
    keys.some((key) => !Object.hasOwn(value, key))
  )
    throw new Error('CONTROL_INVALID')
  return value
}

function parityError(error) {
  if (!error) return null
  return {
    name: String(error.name ?? 'Error'),
    code: String(error.code ?? 'UNKNOWN'),
    message: String(error.message ?? error).slice(0, 4096),
  }
}

function parityChild({ run, io, root, runRoot, env, phase, args, keys = null }) {
  const stdoutPath = resolve(runRoot, `evidence/${phase}.stdout.log`)
  const stderrPath = resolve(runRoot, `evidence/${phase}.stderr.log`)
  const receiptPath = resolve(runRoot, `evidence/${phase}.receipt.json`)
  const startUtc = new Date().toISOString()
  let stdoutFD = null,
    stderrFD = null,
    result = null,
    error = null,
    ioError = null
  try {
    stdoutFD = io.openSync(stdoutPath, 'wx', 0o600)
    stderrFD = io.openSync(stderrPath, 'wx', 0o600)
    try {
      result = run('uv', args, {
        cwd: root,
        env,
        shell: false,
        stdio: ['ignore', stdoutFD, stderrFD],
      })
      error = result?.error ?? null
    } catch (caught) {
      error = caught
    }
  } catch (caught) {
    ioError = caught
  } finally {
    for (const fd of [stdoutFD, stderrFD]) {
      if (fd !== null) {
        try {
          io.closeSync(fd)
        } catch (caught) {
          ioError ??= caught
        }
      }
    }
  }
  const endUtc = new Date().toISOString()
  let stdout = null,
    stderr = null
  for (const [path, channel] of [
    [stdoutPath, 'stdout'],
    [stderrPath, 'stderr'],
  ]) {
    try {
      const value = parityStream(io, path)
      if (channel === 'stdout') stdout = value
      else stderr = value
    } catch (caught) {
      ioError ??= caught
    }
  }
  const status = Number.isInteger(result?.status) ? result.status : null
  const overflow = error?.code === 'ENOBUFS' || error?.code === 'ERR_CHILD_PROCESS_STDIO_MAXBUFFER'
  const complete = !error && !ioError && !result?.signal && status !== null
  const receipt = {
    format: 'i05-semantic-parity-child/1',
    profile: parityProfile,
    phase,
    argv: ['uv', ...args],
    cwd: root,
    environment: env,
    pid: Number.isInteger(result?.pid) ? result.pid : null,
    startUtc,
    endUtc,
    status,
    signal: result?.signal ?? null,
    error: parityError(error),
    ioError: parityError(ioError),
    overflow,
    complete,
    stdoutPath,
    stderrPath,
    receiptPath,
    stdout,
    stderr,
    captureRange: {
      stdout: stdout ? [0, stdout.bytes] : null,
      stderr: stderr ? [0, stderr.bytes] : null,
    },
  }
  try {
    io.writeFileSync(receiptPath, JSON.stringify(receipt, null, 2) + '\n', {
      flag: 'wx',
      mode: 0o600,
    })
  } catch {
    fail('BUILD_PARITY_EVIDENCE_IO_FAILED')
  }
  if (ioError) fail('BUILD_PARITY_EVIDENCE_IO_FAILED')
  if (error || status !== 0 || result?.signal) fail('BUILD_PARITY_CHILD_FAILED')
  if (keys === null) return null
  // The raw stream is already sealed in its original file; never replay the child.
  const controlPath = resolve(runRoot, `evidence/${phase}.control.json`)
  const control = (accepted, code, error = null) => {
    try {
      io.writeFileSync(
        controlPath,
        JSON.stringify({ accepted, code, error: parityError(error), stdout, receiptPath }) + '\n',
        { flag: 'wx', mode: 0o600 },
      )
    } catch {
      fail('BUILD_PARITY_EVIDENCE_IO_FAILED')
    }
    if (!accepted) fail(code)
  }
  if (stdout.bytes > 65536) control(false, 'BUILD_PARITY_HELPER_OUTPUT_INVALID')
  let raw
  try {
    raw = io.readFileSync(stdoutPath)
  } catch (error) {
    control(false, 'BUILD_PARITY_EVIDENCE_IO_FAILED', error)
  }
  if (
    raw.length !== stdout.bytes ||
    createHash('sha256').update(raw).digest('hex') !== stdout.sha256
  )
    control(false, 'BUILD_PARITY_EVIDENCE_IO_FAILED')
  let value
  try {
    value = parityControl(raw, keys)
  } catch (error) {
    control(false, 'BUILD_PARITY_HELPER_OUTPUT_INVALID', error)
  }
  if (
    value === null ||
    typeof value !== 'object' ||
    Array.isArray(value) ||
    Object.keys(value).length !== keys.length ||
    keys.some((key) => typeof value[key] !== 'string')
  )
    control(false, 'BUILD_PARITY_HELPER_OUTPUT_INVALID')
  control(true, null)
  return value
}

export function buildSemanticParity({
  repositoryRoot = defaultRoot,
  run = spawnSync,
  io = fs,
  uuid = randomUUID,
} = {}) {
  const root = resolve(repositoryRoot),
    token = uuid()
  if (typeof token !== 'string' || !uuidPattern.test(token)) fail('BUILD_ENGINE_ID_INVALID')
  const parent = resolve(root, 'build/i05-semantic-parity')
  directory(io, root, parent)
  const runRoot = resolve(parent, token)
  if (entry(io, runRoot) !== null) fail('BUILD_ENGINE_OUTPUT_EXISTS')
  io.mkdirSync(runRoot)
  const evidence = resolve(runRoot, 'evidence')
  io.mkdirSync(evidence)
  io.mkdirSync(resolve(evidence, 'cache'))
  io.mkdirSync(resolve(evidence, 'tmp'))
  io.writeFileSync(
    resolve(evidence, 'build-request-v1.json'),
    JSON.stringify({ profile: parityProfile, token }),
    { flag: 'wx', mode: 0o600 },
  )
  const env = parityEnvironment(root, runRoot)
  const prepare = prepareProgram.replace(
    'Path(sys.argv[2]))',
    'Path(sys.argv[2]),profile="i05-source-package-parity")',
  )
  const finalize = finalizeProgram.replace(
    'Path(sys.argv[3]))',
    'Path(sys.argv[3]),profile="i05-source-package-parity")',
  )
  const prepared = parityChild({
    run,
    io,
    root,
    runRoot,
    env,
    phase: 'prepare',
    args: ['run', '--frozen', 'python', '-c', prepare, root, runRoot],
    keys: ['provenancePath', 'contractPath', 'generatedDir', 'anchorPath'],
  })
  const expected = {
    provenancePath: resolve(runRoot, parityProvenance),
    contractPath: resolve(runRoot, parityContract),
    generatedDir: resolve(runRoot, 'generated'),
    anchorPath: resolve(runRoot, 'generated', parityAnchor + '.py'),
  }
  if (Object.keys(expected).some((key) => prepared[key] !== expected[key]))
    fail('BUILD_ENGINE_HELPER_PATH_INVALID')
  const artifactDirectory = resolve(runRoot, 'dist/ontolearn-semantic-parity')
  const data = [
    [resolve(root, 'packages/contracts/python/contract_v2.py'), 'contracts/python'],
    ...['schema.json', 'registry.json', 'errors.json'].map((name) => [
      resolve(root, 'packages/contracts/v2', name),
      'contracts/v2',
    ]),
    ...['manifest', 'inputs'].map((kind) => [
      resolve(
        root,
        `packages/engine/src/ontolearn_engine/probe_inputs/i05-source-package-parity-${kind}.json`,
      ),
      'provenance/i05/source-package-parity',
    ]),
    [resolve(root, 'uv.lock'), 'provenance'],
    [prepared.provenancePath, 'provenance/i05'],
    [prepared.contractPath, 'provenance/i05'],
    [resolve(runRoot, 'licenses'), 'licenses'],
  ]
  parityChild({
    run,
    io,
    root,
    runRoot,
    env,
    phase: 'pyinstaller',
    args: [
      'run',
      '--frozen',
      'pyinstaller',
      '--noconfirm',
      '--clean',
      '--onedir',
      '--optimize',
      '0',
      '--paths',
      prepared.generatedDir,
      ...parityImports.flatMap((name) => ['--hidden-import', name]),
      ...parityExcludes.flatMap((name) => ['--exclude-module', name]),
      ...distributions.flatMap((name) => ['--collect-all', name]),
      ...distributions.flatMap((name) => ['--copy-metadata', name]),
      ...data.flatMap(([source, destination]) => ['--add-data', `${source}:${destination}`]),
      '--name',
      'ontolearn-semantic-parity',
      '--distpath',
      resolve(runRoot, 'dist'),
      '--workpath',
      resolve(runRoot, 'pyinstaller'),
      '--specpath',
      resolve(runRoot, 'spec'),
      'packages/engine/src/ontolearn_engine/semantic_source_package_probe.py',
    ],
  })
  const finalized = parityChild({
    run,
    io,
    root,
    runRoot,
    env,
    phase: 'finalize',
    args: ['run', '--frozen', 'python', '-c', finalize, root, runRoot, artifactDirectory],
    keys: ['bindingPath', 'bindingSha256', 'engineDirectory', 'provenanceSha256'],
  })
  if (
    finalized.bindingPath !== resolve(runRoot, 'artifact-binding-v1.json') ||
    finalized.engineDirectory !== artifactDirectory ||
    !/^[0-9a-f]{64}$/.test(finalized.bindingSha256) ||
    !/^[0-9a-f]{64}$/.test(finalized.provenanceSha256)
  )
    fail('BUILD_ENGINE_BINDING_INVALID')
  return {
    profile: parityProfile,
    artifactDirectory,
    bindingPath: finalized.bindingPath,
    bindingSha256: finalized.bindingSha256,
    provenanceSha256: finalized.provenanceSha256,
    rootApproved: false,
  }
}

export function selectBuild(args) {
  if (!Array.isArray(args) || args.some((x) => typeof x !== 'string'))
    fail('BUILD_PARITY_ARGUMENTS_INVALID')
  if (args.length === 0) return buildEngine
  if (args.length === 1 && args[0] === '--i05-source-package-parity') return buildSemanticParity
  fail('BUILD_PARITY_ARGUMENTS_INVALID')
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    console.log(JSON.stringify(selectBuild(process.argv.slice(2))()))
  } catch (error) {
    console.error(error instanceof Error ? error.message : 'BUILD_ENGINE_FAILED')
    process.exitCode = 1
  }
}
