// One source for build-time HTML and the development response header.
export function contentSecurityPolicy(development?: { nonce: string; origin: string }): string {
  const directives: Record<string, string[]> = {
    'default-src': ["'self'"],
    'script-src': ["'self'"],
    'style-src': ["'self'"],
    'img-src': ["'self'", 'data:'],
    'connect-src': ["'none'"],
    'object-src': ["'none'"],
    'base-uri': ["'none'"],
    'frame-src': ["'none'"],
    'form-action': ["'none'"],
  }
  if (development) {
    const origin = new URL(development.origin)
    if (origin.origin !== 'http://127.0.0.1:5173' || !/^[\w+/=-]+$/.test(development.nonce)) {
      throw new Error('INVALID_DEVELOPMENT_CSP')
    }
    directives['script-src'].push(`'nonce-${development.nonce}'`)
    directives['style-src'].push("'unsafe-inline'") // Vite CSS HMR; production uses local CSS.
    directives['connect-src'] = [origin.origin, 'ws://127.0.0.1:5173']
  }
  return Object.entries(directives)
    .map(([name, values]) => `${name} ${values.join(' ')}`)
    .join('; ')
}
