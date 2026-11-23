import { app, safeStorage } from 'electron'
import { EncryptedCredentialBoundary, type CiphertextRepository } from './credentials'
import { GatewayFailure } from './policy'

/** Main-process construction only. No alternate encryptor or plaintext fallback. */
export function createElectronCredentialBoundary(
  repository: CiphertextRepository,
): EncryptedCredentialBoundary {
  try {
    if (process.type !== 'browser' || !process.versions.electron || !app.isReady())
      throw new Error()
    return new EncryptedCredentialBoundary(safeStorage, repository, process.platform)
  } catch {
    throw new GatewayFailure('CREDENTIAL_UNAVAILABLE')
  }
}
