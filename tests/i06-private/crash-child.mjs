import { registerHooks } from 'node:module'
import { readFileSync } from 'node:fs'
import { fileURLToPath, pathToFileURL } from 'node:url'
import ts from 'typescript'
import path from 'node:path'

// Dedicated Node CLI fault process, never an Electron/GUI launcher.
registerHooks({
  resolve(specifier, context, next) {
    if (specifier.startsWith('.') && !path.extname(specifier))
      return next(specifier + '.ts', context)
    return next(specifier, context)
  },
  load(url, context, next) {
    if (url.endsWith('.ts'))
      return {
        format: 'module',
        shortCircuit: true,
        source: ts.transpileModule(readFileSync(fileURLToPath(url), 'utf8'), {
          compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext },
        }).outputText,
      }
    return next(url, context)
  },
})
const [root, rawLocation, rawBinding, stage, kind] = process.argv.slice(2)
const location = JSON.parse(rawLocation)
const binding = JSON.parse(rawBinding)
const observer = async (phase) => {
  if (phase === stage) process.kill(process.pid, 'SIGKILL')
}
if (kind === 'audit') {
  const { PersistentGatewayAudit } = await import(
    pathToFileURL(path.join(root, 'apps/desktop/src/main/model-gateway/persistent-audit.ts'))
  )
  const audit = await PersistentGatewayAudit.open(location, observer)
  await audit.append(binding)
  await audit.close()
} else {
  const { PrivateCiphertextRepository } = await import(
    pathToFileURL(path.join(root, 'apps/desktop/src/main/model-gateway/ciphertext-repository.ts'))
  )
  const store = await PrivateCiphertextRepository.open(location, observer)
  await store.write(binding, Buffer.from('SYNTHETIC_CIPHERTEXT_BYTES'))
  await store.close()
}
