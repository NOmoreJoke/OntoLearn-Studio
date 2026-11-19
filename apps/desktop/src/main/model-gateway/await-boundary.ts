import { GatewayFailure, type FailureCode } from './policy'

// Cancellation stops waiting; an underlying OS/repository promise can finish later,
// but its result has no callback able to send or mutate gateway authority.
export function boundedWait<T>(
  operation: Promise<T>,
  code: FailureCode,
  signal?: AbortSignal,
): Promise<T> {
  return new Promise((resolve, reject) => {
    const cleanup = () => {
      clearTimeout(timer)
      signal?.removeEventListener('abort', abort)
    }
    const abort = () => {
      cleanup()
      reject(new GatewayFailure('CANCELLED'))
    }
    const timer = setTimeout(() => {
      cleanup()
      reject(new GatewayFailure(code))
    }, 5000)
    signal?.addEventListener('abort', abort, { once: true })
    if (signal?.aborted) abort()
    operation.then(
      (value) => {
        cleanup()
        resolve(value)
      },
      () => {
        cleanup()
        reject(new GatewayFailure(code))
      },
    )
  })
}
