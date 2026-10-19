import type { DesktopBridge } from '@ontolearn/contracts'
declare global {
  interface Window {
    ontolearn?: DesktopBridge
  }
}
