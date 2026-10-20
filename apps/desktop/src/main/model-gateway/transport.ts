import http from 'node:http'
import https from 'node:https'
import { GatewayFailure } from './policy'

// Only this internal transport holds headers and writes bytes. No redirect following,
// cookies, proxy environment, arbitrary methods/headers, or user-provided fetch callback.
export function sendOnce(
  endpoint: string,
  secret: string,
  body: string,
  signal: AbortSignal,
  finalGuard: () => void,
): Promise<{ status: number; body: string }> {
  return new Promise((resolve, reject) => {
    let settled = false
    const finish = (error?: GatewayFailure, value?: { status: number; body: string }) => {
      if (settled) return
      settled = true
      clearTimeout(deadline)
      if (error) reject(error)
      else resolve(value!)
    }
    const request = (endpoint.startsWith('https:') ? https : http).request(
      endpoint,
      {
        method: 'POST',
        agent: false,
        signal,
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(body),
          Authorization: `Bearer ${secret}`,
        },
      },
      (response) => {
        const status = response.statusCode ?? 0
        if (status >= 300 && status < 400) {
          finish(new GatewayFailure('REDIRECT_REJECTED'))
          response.destroy()
          request.destroy()
          return
        }
        let size = 0
        const chunks: Buffer[] = []
        response.on('data', (chunk: Buffer) => {
          size += chunk.length
          if (size > 1024 * 1024) {
            finish(new GatewayFailure('RESPONSE_LIMIT'))
            response.destroy()
            request.destroy()
          } else chunks.push(chunk)
        })
        response.on('error', () => finish(new GatewayFailure('MODEL_UNAVAILABLE')))
        response.on('end', () =>
          finish(undefined, { status, body: Buffer.concat(chunks).toString('utf8') }),
        )
      },
    )
    const deadline = setTimeout(() => {
      finish(new GatewayFailure('MODEL_UNAVAILABLE'))
      request.destroy()
    }, 5000)
    request.on('error', () =>
      finish(new GatewayFailure(signal.aborted ? 'CANCELLED' : 'MODEL_UNAVAILABLE')),
    )
    // Wait for the actual new socket connection. No buffered request body/headers
    // exist before this guard; a config change during DNS/TLS/connect aborts it.
    request.on('socket', (socket) => {
      const send = () => {
        if (settled) return
        try {
          if (signal.aborted) throw new GatewayFailure('CANCELLED')
          finalGuard()
          // No await or callback between final authorization and write.
          request.end(body)
        } catch (error) {
          finish(error instanceof GatewayFailure ? error : new GatewayFailure('MODEL_UNAVAILABLE'))
          request.destroy()
        }
      }
      socket.once(endpoint.startsWith('https:') ? 'secureConnect' : 'connect', send)
    })
  })
}
