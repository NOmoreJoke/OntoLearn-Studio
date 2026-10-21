#!/usr/bin/env node
// Offline N0 supplier. Verification never spawns a process or writes a file.
import fs from 'node:fs'
import path from 'node:path'
import crypto from 'node:crypto'
import { fileURLToPath } from 'node:url'
import { spawnSync } from 'node:child_process'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const lockPath = path.join(root, 'packages/native-location/toolchain-lock.json')
const sourcePaths = [
  'packages/native-location/include/location_abi.h',
  'packages/native-location/src/capability_core.cc',
  'packages/native-location/src/platform_macos.cc',
  'packages/native-location/src/platform_windows.cc',
  'packages/native-location/src/node_binding.cc',
  'apps/desktop/src/main/security/native-location-owner.ts',
  'packages/native-location/tests/location_core_test.cc',
  'packages/native-location/tests/location_child_probe.cc',
  'tests/unit/i06-native-location-owner.test.ts',
]
const writers = [
  'packages/native-location/CMakeLists.txt',
  'packages/native-location/toolchain-lock.json',
  'scripts/build-native-location.mjs',
]
const targets = ['darwin-arm64', 'win32-x64']
const components = ['core', 'addon', 'fixture-addon']
let processExecution = false
const hash = (b) => crypto.createHash('sha256').update(b).digest('hex')
const sha = (v) => typeof v === 'string' && /^[a-f0-9]{64}$/.test(v)
const ref = (v) => typeof v === 'string' && /^[a-f0-9]{40}$/.test(v)
const fail = (message) => {
  throw new Error(message)
}
const need = (condition, message) => {
  if (!condition) fail(message)
}
const object = (v, keys, where) => {
  need(v !== null && typeof v === 'object' && !Array.isArray(v), `${where}: object required`)
  need(
    JSON.stringify(Object.keys(v).sort()) === JSON.stringify([...keys].sort()),
    `${where}: unknown or missing fields`,
  )
}
const text = (v) => typeof v === 'string' && v.length > 0 && !/[\0\r\n;]/.test(v)
const absolute = (v) => text(v) && path.isAbsolute(v)
const approval = (a, where) => {
  object(a, ['approved', 'reference'], where)
  need(typeof a.approved === 'boolean', `${where}: boolean approval required`)
  need(a.reference === null || ref(a.reference), `${where}: fixed approval ref required`)
  need(!a.approved || ref(a.reference), `${where}: approved without fixed reference`)
}
const pinSchema = (p, where) => {
  if (p === null) return
  object(p, ['path', 'realpath', 'bytes', 'sha256'], where)
  need(absolute(p.path) && absolute(p.realpath), `${where}: absolute paths required`)
  need(
    Number.isSafeInteger(p.bytes) && p.bytes >= 0 && sha(p.sha256),
    `${where}: invalid byte/hash pin`,
  )
}

// JSON.parse silently accepts duplicate keys; scan its already-valid grammar first.
function jsonStrict(raw) {
  const parsed = JSON.parse(raw)
  let i = 0
  const ws = () => {
    while (/\s/.test(raw[i] ?? '') && i < raw.length) i++
  }
  function string() {
    const begin = i++
    while (i < raw.length) {
      if (raw[i] === '\\') {
        i += 2
        continue
      }
      if (raw[i++] === '"') return JSON.parse(raw.slice(begin, i))
    }
    fail('unterminated JSON string')
  }
  function value() {
    ws()
    if (raw[i] === '{') {
      i++
      ws()
      const seen = new Set()
      if (raw[i] === '}') {
        i++
        return
      }
      while (true) {
        ws()
        const key = string()
        need(!seen.has(key), `duplicate JSON key: ${key}`)
        seen.add(key)
        ws()
        i++
        value()
        ws()
        if (raw[i++] === '}') return
      }
    }
    if (raw[i] === '[') {
      i++
      ws()
      if (raw[i] === ']') {
        i++
        return
      }
      while (true) {
        value()
        ws()
        if (raw[i++] === ']') return
      }
    }
    if (raw[i] === '"') {
      string()
      return
    }
    while (i < raw.length && !/[\s,}\]]/.test(raw[i])) i++
  }
  value()
  return parsed
}
function parseArgs(args) {
  const result = {}
  for (let i = 0; i < args.length; i++) {
    const arg = args[i]
    need(
      ['--target', '--component', '--verify-only', '--build'].includes(arg),
      `unknown argument: ${arg}`,
    )
    need(!Object.hasOwn(result, arg), `duplicate argument: ${arg}`)
    result[arg] = arg === '--target' || arg === '--component' ? args[++i] : true
  }
  need(targets.includes(result['--target']), 'target must be darwin-arm64 or win32-x64')
  need(components.includes(result['--component']), 'component must be core, addon or fixture-addon')
  need(Boolean(result['--verify-only']) !== Boolean(result['--build']), 'select exactly one mode')
  return {
    target: result['--target'],
    component: result['--component'],
    build: Boolean(result['--build']),
  }
}
function validateSchema(l) {
  object(
    l,
    [
      'schemaVersion',
      'base',
      'source',
      'contract',
      'materials',
      'toolchains',
      'node',
      'windowsAddon',
      'execution',
    ],
    'lock',
  )
  need(
    l.schemaVersion === 1 && l.base === '5f910b52c69d86a1076b2032e5d3c63e715947f3',
    'unsupported schema/base',
  )
  object(l.source, ['approval', 'ref', 'files'], 'source')
  approval(l.source.approval, 'source.approval')
  need(l.source.ref === null || ref(l.source.ref), 'source.ref invalid')
  need(!l.source.approval.approved || ref(l.source.ref), 'approved source needs fixed ref')
  need(
    Array.isArray(l.source.files) && l.source.files.length === sourcePaths.length,
    'exact nine sources required',
  )
  l.source.files.forEach((f, i) => {
    object(f, ['path', 'bytes', 'sha256'], `source[${i}]`)
    need(f.path === sourcePaths[i], `source[${i}]: unexpected path/order`)
    need(
      (f.bytes === null && f.sha256 === null) ||
        (Number.isSafeInteger(f.bytes) && f.bytes > 0 && sha(f.sha256)),
      'invalid source pin',
    )
  })
  object(
    l.contract,
    [
      'ref',
      'headerSha256',
      'handoffSha256',
      'abiVersion',
      'candidateNapiVersion',
      'bindingMinimumApproval',
      'testAssemblyApproval',
    ],
    'contract',
  )
  need(
    l.contract.ref === '6a7789bf0c1e5e7b0f25f37c86e0c9d64c6dc20d' &&
      l.contract.headerSha256 ===
        'fc3f7983d62b0ef4f5a3a056198c00a0b971d2ae722acc33bc6f61937ec8e172' &&
      l.contract.handoffSha256 ===
        '8b3ba7c43935fac973a550944f6c2f5f69c94623162b31a75e0da26053ac7134',
    'unknown readonly ABI contract',
  )
  need(
    l.contract.abiVersion === 1 && l.contract.candidateNapiVersion === 3,
    'contract/API candidate changed; owner review required',
  )
  approval(l.contract.bindingMinimumApproval, 'bindingMinimumApproval')
  approval(l.contract.testAssemblyApproval, 'testAssemblyApproval')
  if (l.source.approval.approved) {
    need(
      l.source.files[0].sha256 === l.contract.headerSha256,
      'adopted ABI header differs from fixed readonly contract',
    )
  }
  object(
    l.materials,
    [
      'indexPath',
      'indexBytes',
      'indexSha256',
      'cmakeVersion',
      'cmakeArchiveBytes',
      'cmakeArchiveSha256',
      'runtimeStatus',
    ],
    'materials',
  )
  need(
    l.materials.indexPath ===
      'docs/reviews/T03/native-location-N0-build/tool-materials/source-index.json' &&
      Number.isSafeInteger(l.materials.indexBytes) &&
      sha(l.materials.indexSha256),
    'invalid material index',
  )
  need(
    l.materials.cmakeVersion === '4.4.4' &&
      l.materials.cmakeArchiveBytes === 89454352 &&
      l.materials.cmakeArchiveSha256 ===
        '4b7b73704b1db9b374e5c9ab8e17ac6148b817b6396ee75cd94a852cbac9d305' &&
      l.materials.runtimeStatus === 'NOT_RUN',
    'unknown static material provenance',
  )
  object(l.toolchains, targets, 'toolchains')
  for (const t of targets) {
    const tc = l.toolchains[t]
    object(
      tc,
      [
        'approval',
        'version',
        'generator',
        'executables',
        'resourceInventory',
        'sdk',
        'environment',
        'systemLibraries',
      ],
      t,
    )
    approval(tc.approval, `${t}.approval`)
    need(tc.version === null || text(tc.version), 'toolchain version invalid')
    need(
      tc.generator === (t === 'darwin-arm64' ? 'Unix Makefiles' : 'Ninja'),
      'generator is fixed per target',
    )
    object(tc.executables, ['cmake', 'c', 'cxx', 'buildTool', 'git'], 'executables')
    for (const [k, p] of Object.entries(tc.executables)) pinSchema(p, `${t}.${k}`)
    pinSchema(tc.resourceInventory, 'resourceInventory')
    object(tc.sdk, ['root', 'version', 'settings', 'terms', 'inventory'], 'sdk')
    need(tc.sdk.root === null || absolute(tc.sdk.root), 'invalid SDK root')
    need(tc.sdk.version === null || text(tc.sdk.version), 'invalid SDK version')
    for (const k of ['settings', 'terms', 'inventory']) pinSchema(tc.sdk[k], `sdk.${k}`)
    object(
      tc.environment,
      t === 'darwin-arm64' ? [] : ['INCLUDE', 'LIB', 'PATH', 'SystemRoot', 'TEMP', 'TMP'],
      'environment',
    )
    for (const v of Object.values(tc.environment))
      need(
        v === null || (typeof v === 'string' && v.length > 0 && !/[\0\r\n]/.test(v)),
        'invalid pinned environment',
      )
    need(
      tc.systemLibraries === null ||
        (Array.isArray(tc.systemLibraries) &&
          tc.systemLibraries.every((p) => {
            pinSchema(p, 'systemLibrary')
            return p !== null
          })),
      'invalid system libraries',
    )
  }
  object(l.node, ['approval', 'version', 'includeRoot', 'headers', 'license'], 'node')
  approval(l.node.approval, 'node.approval')
  need(
    l.node.version === '24.15.0' && (l.node.includeRoot === null || absolute(l.node.includeRoot)),
    'invalid Node input',
  )
  object(
    l.node.headers,
    ['node_api.h', 'node_api_types.h', 'js_native_api.h', 'js_native_api_types.h'],
    'node.headers',
  )
  for (const p of Object.values(l.node.headers)) pinSchema(p, 'node.header')
  pinSchema(l.node.license, 'node.license')
  object(
    l.windowsAddon,
    ['approval', 'electronVersion', 'nodeLib', 'hook', 'hookLicense', 'delayimp'],
    'windowsAddon',
  )
  approval(l.windowsAddon.approval, 'windowsAddon.approval')
  need(
    l.windowsAddon.electronVersion === null ||
      /^\d+\.\d+\.\d+$/.test(l.windowsAddon.electronVersion),
    'invalid Electron version',
  )
  for (const k of ['nodeLib', 'hook', 'hookLicense', 'delayimp']) pinSchema(l.windowsAddon[k], k)
  object(l.execution, targets, 'execution')
  for (const t of targets) {
    object(l.execution[t], components, 'execution target')
    for (const c of components) approval(l.execution[t][c], `execution.${t}.${c}`)
  }
}
function readBounded(p, cap) {
  const stat = fs.statSync(p)
  need(stat.isFile() && stat.size <= cap, `not a bounded regular input: ${p}`)
  const b = fs.readFileSync(p)
  need(b.length === stat.size, `input changed while reading: ${p}`)
  return b
}
function checkPin(p, where, gaps, allowEmpty = false) {
  if (p === null) {
    gaps.push(`${where}: pending pin`)
    return
  }
  need(allowEmpty || p.bytes > 0, `${where}: empty executable/license/manifest input`)
  need(fs.realpathSync(p.path) === p.realpath, `${where}: realpath drift`)
  const b = readBounded(p.path, p.bytes)
  need(b.length === p.bytes && hash(b) === p.sha256, `${where}: bytes/hash drift`)
}
function inventory(p, where, gaps, requiredRoot = null) {
  checkPin(p, where, gaps)
  if (p === null) return
  const v = jsonStrict(readBounded(p.path, 16 * 1024 * 1024).toString('utf8'))
  object(v, ['roots', 'files'], where)
  need(
    Array.isArray(v.roots) && v.roots.length > 0 && v.roots.every(absolute),
    'inventory roots invalid',
  )
  need(
    Array.isArray(v.files) && v.files.length > 0 && v.files.length <= 50000,
    'inventory size invalid',
  )
  if (requiredRoot !== null)
    need(v.roots.includes(requiredRoot), 'SDK inventory does not cover selected supply root')
  const seen = new Set()
  for (const f of v.files) {
    pinSchema(f, 'inventory file')
    need(f !== null && !seen.has(f.path), 'duplicate/null inventory path')
    seen.add(f.path)
    need(
      v.roots.some(
        (r) => f.path.startsWith(`${r}${path.sep}`) && f.realpath.startsWith(`${r}${path.sep}`),
      ),
      'inventory path escapes approved root',
    )
    checkPin(f, where, gaps, true)
  }
}
function verify(l, opts, lockBytes) {
  const gaps = []
  const writerPins = writers.map((p) => {
    const b = readBounded(path.join(root, p), 1024 * 1024)
    return { path: p, bytes: b.length, sha256: hash(b) }
  })
  const m = l.materials
  const index = readBounded(path.join(root, m.indexPath), 1024 * 1024)
  need(
    index.length === m.indexBytes && hash(index) === m.indexSha256,
    'official material index drift',
  )
  if (!l.source.approval.approved)
    gaps.push('source: full nine fixed inputs/adoption pending; not read')
  else
    for (const f of l.source.files) {
      need(f.bytes !== null, `approved source has no pin: ${f.path}`)
      const p = path.join(root, f.path)
      need(fs.realpathSync(p) === p, 'source symlink rejected')
      const b = readBounded(p, f.bytes)
      need(b.length === f.bytes && hash(b) === f.sha256, `source drift: ${f.path}`)
    }
  const tc = l.toolchains[opts.target]
  if (!tc.approval.approved)
    gaps.push(`${opts.target}: supplied/extracted toolchain and SDK acceptance pending; not read`)
  else {
    need(
      tc.version !== null &&
        tc.sdk.root !== null &&
        tc.sdk.version !== null &&
        tc.systemLibraries !== null,
      'approved toolchain has incomplete metadata',
    )
    for (const [k, p] of Object.entries(tc.executables)) checkPin(p, k, gaps)
    inventory(tc.resourceInventory, 'CMake/compiler resource inventory', gaps)
    for (const k of ['settings', 'terms']) checkPin(tc.sdk[k], `sdk.${k}`, gaps)
    inventory(
      tc.sdk.inventory,
      'SDK supply inventory (not future used-header output)',
      gaps,
      tc.sdk.root,
    )
    for (const p of tc.systemLibraries) checkPin(p, 'system library', gaps)
    for (const v of Object.values(tc.environment))
      if (v === null) gaps.push('Windows environment pending')
  }
  if (opts.component !== 'addon' && !l.contract.testAssemblyApproval.approved)
    gaps.push('fixed complete source test assembly approval pending')
  if (opts.component !== 'core') {
    if (!l.contract.bindingMinimumApproval.approved)
      gaps.push(
        'actual complete binding API minimum approval pending; candidate NAPI_VERSION=3 only',
      )
    if (!l.node.approval.approved)
      gaps.push('Node headers/license supply adoption pending; not read')
    else {
      need(l.node.includeRoot !== null, 'approved Node include root missing')
      for (const [name, p] of Object.entries(l.node.headers)) {
        need(
          p === null || p.path === path.join(l.node.includeRoot, name),
          'Node header directory mismatch',
        )
        checkPin(p, `Node ${name}`, gaps)
      }
      checkPin(l.node.license, 'Node LICENSE', gaps)
    }
    if (opts.target === 'win32-x64') {
      if (!l.windowsAddon.approval.approved)
        gaps.push('Windows Electron import/hook/delayimp supply pending; not read')
      else {
        need(l.windowsAddon.electronVersion !== null, 'Windows Electron version missing')
        for (const k of ['nodeLib', 'hook', 'hookLicense', 'delayimp'])
          checkPin(l.windowsAddon[k], k, gaps)
      }
    }
  }
  if (!l.execution[opts.target][opts.component].approved)
    gaps.push(`configure/build execution window pending: ${opts.target}/${opts.component}`)
  const actualHost = `${process.platform}-${process.arch}`
  if (opts.target !== actualHost)
    gaps.push(`host mismatch: ${actualHost}; cross compilation unsupported`)
  return {
    status: gaps.length ? 'incomplete' : 'complete-readonly',
    mode: opts.build ? 'build-preflight' : 'verify-only',
    target: opts.target,
    component: opts.component,
    processExecution: false,
    inputWrites: false,
    lockSha256: hash(lockBytes),
    inputDigest: hash(Buffer.from(JSON.stringify(writerPins))),
    writers: writerPins,
    gaps,
  }
}
function build(l, opts, result) {
  // Only reachable with complete approved input AND this exact execution window.
  const tc = l.toolchains[opts.target]
  const buildDir = path.join(
    root,
    'build/native-location/n0',
    opts.target,
    result.inputDigest,
    opts.component,
  )
  fs.mkdirSync(path.dirname(buildDir), { recursive: true })
  fs.mkdirSync(buildDir) // Existing cache/logs are never reused or overwritten.
  const env =
    opts.target === 'darwin-arm64'
      ? { PATH: '/usr/bin:/bin', HOME: buildDir, TMPDIR: buildDir, LANG: 'C', LC_ALL: 'C' }
      : { ...tc.environment, USERPROFILE: buildDir }
  const configure = [
    '-S',
    path.join(root, 'packages/native-location'),
    '-B',
    buildDir,
    '-G',
    tc.generator,
    `-DNL_TARGET=${opts.target}`,
    `-DNL_COMPONENT=${opts.component}`,
    `-DNL_LOCK_SHA256=${result.lockSha256}`,
    `-DCMAKE_MAKE_PROGRAM=${tc.executables.buildTool.path}`,
    `-DCMAKE_C_COMPILER=${tc.executables.c.path}`,
    `-DCMAKE_CXX_COMPILER=${tc.executables.cxx.path}`,
    '-DCMAKE_BUILD_TYPE=RelWithDebInfo',
    '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON',
  ]
  if (opts.target === 'darwin-arm64')
    configure.push(
      '-DCMAKE_OSX_ARCHITECTURES=arm64',
      `-DCMAKE_OSX_SYSROOT=${tc.sdk.root}`,
      '-DCMAKE_OSX_DEPLOYMENT_TARGET=15.0',
    )
  const selected =
    opts.component === 'core'
      ? ['location_core_test', 'location_child_probe']
      : [opts.component === 'addon' ? 'i06_native_location' : 'i06_native_location_test']
  const commands = [
    {
      executable: tc.executables.git.path,
      argv: ['status', '--porcelain=v1', '--untracked-files=all', '--', ...writers, ...sourcePaths],
      expected: '',
    },
    {
      executable: tc.executables.git.path,
      argv: ['rev-parse', '--verify', 'HEAD'],
      commitReceipt: true,
    },
    ...l.source.files.map((f) => ({
      executable: tc.executables.git.path,
      argv: ['show', `${l.source.ref}:${f.path}`],
      sha256: f.sha256,
    })),
    { executable: tc.executables.cmake.path, argv: configure },
    {
      executable: tc.executables.cmake.path,
      argv: [
        '--build',
        buildDir,
        '--config',
        'RelWithDebInfo',
        '--target',
        ...selected,
        '--parallel',
        '2',
      ],
    },
  ]
  const log = {
    preflight: result,
    environment: env,
    commands: [],
    firstFailure: null,
    tests: 'NOT_RUN',
    dependencyClosure: 'PENDING_POST_BUILD_AUDIT',
  }
  fs.writeFileSync(path.join(buildDir, 'supplier-log.json'), JSON.stringify(log, null, 2), {
    flag: 'wx',
  })
  for (const [i, command] of commands.entries()) {
    const { executable, argv } = command
    const out = fs.openSync(path.join(buildDir, `${i}.stdout`), 'wx')
    const err = fs.openSync(path.join(buildDir, `${i}.stderr`), 'wx')
    let run
    try {
      processExecution = true
      run = spawnSync(executable, argv, {
        cwd: root,
        env,
        shell: false,
        stdio: ['ignore', out, err],
        timeout: 600000,
        windowsHide: true,
      })
    } finally {
      fs.closeSync(out)
      fs.closeSync(err)
    }
    const record = {
      executable,
      argv,
      cwd: root,
      status: run.status,
      signal: run.signal,
      error: run.error?.message ?? null,
    }
    log.commands.push(record)
    if (
      run.status === 0 &&
      !run.error &&
      (command.expected !== undefined || command.sha256 || command.commitReceipt)
    ) {
      const stdout = fs.readFileSync(path.join(buildDir, `${i}.stdout`))
      if (command.expected !== undefined && stdout.toString('utf8') !== command.expected)
        record.error = 'Product sources/writers are dirty or untracked'
      if (command.sha256 && hash(stdout) !== command.sha256)
        record.error = 'Fixed source Git blob differs from adopted bytes'
      if (command.commitReceipt) {
        const commit = stdout.toString('utf8').trim()
        if (!ref(commit)) record.error = 'Invalid supplier HEAD receipt'
        else log.supplierCommit = commit
      }
    }
    if (run.status !== 0 || record.error) log.firstFailure = record
    fs.writeFileSync(path.join(buildDir, 'supplier-log.json'), JSON.stringify(log, null, 2))
    if (log.firstFailure) {
      process.exitCode = 1
      return
    }
  }
  // Build success alone never certifies runtime, cleanup, SDK closure or target OS.
  console.log(JSON.stringify({ status: 'built-unverified', buildDir, tests: 'NOT_RUN' }, null, 2))
}
try {
  const opts = parseArgs(process.argv.slice(2))
  const bytes = readBounded(lockPath, 1024 * 1024)
  const lock = jsonStrict(bytes.toString('utf8'))
  validateSchema(lock)
  const result = verify(lock, opts, bytes)
  console.log(JSON.stringify(result, null, 2))
  if (result.gaps.length) process.exitCode = 2
  else if (opts.build) build(lock, opts, result)
} catch (error) {
  console.error(JSON.stringify({ status: 'rejected', message: error.message, processExecution }))
  process.exitCode = 1
}
