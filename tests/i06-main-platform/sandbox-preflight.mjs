import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { statSync, readFileSync } from 'node:fs'

const helper = '/workspace/node_modules/electron/dist/chrome-sandbox'
const metadata = statSync(helper)
const namespaces = spawnSync('/usr/bin/unshare', ['--user', '--map-root-user', '/bin/true'], {
  encoding: 'utf8',
  timeout: 3000,
})
const api = spawnSync(helper, ['--get-api'], { encoding: 'utf8', timeout: 3000 })
const result = {
  uid: process.getuid(),
  gid: process.getgid(),
  helperUid: metadata.uid,
  helperMode: (metadata.mode & 4095).toString(8),
  userNamespace: {
    exit: namespaces.status,
    signal: namespaces.signal,
    stdout: namespaces.stdout,
    stderr: namespaces.stderr,
  },
  helperAPI: { exit: api.status, signal: api.signal, stdout: api.stdout, stderr: api.stderr },
  kernelUsernsClone: readFileSync('/proc/sys/kernel/unprivileged_userns_clone', 'utf8').trim(),
  procStatus: readFileSync('/proc/self/status', 'utf8')
    .split('\n')
    .filter((line) => /^(NoNewPrivs|Seccomp|Seccomp_filters|CapEff|CapBnd):/.test(line)),
}
console.log(JSON.stringify(result, null, 2))
assert.equal(result.uid, 1106)
assert.equal(result.helperUid, 0)
assert.equal(result.helperMode, '4755')
assert.equal(namespaces.status, 0)
assert.equal(api.status, 0)
