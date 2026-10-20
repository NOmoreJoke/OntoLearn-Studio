import { EventEmitter } from 'node:events'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { BrowserWindow } from 'electron'

const { showMessageBox } = vi.hoisted(() => ({ showMessageBox: vi.fn() }))
vi.mock('electron', () => ({ dialog: { showMessageBox } }))
import { installWindowRecovery } from '../../apps/desktop/src/main/window-recovery'

function fixture() {
  const window = Object.assign(new EventEmitter(), {
    webContents: new EventEmitter(),
    isDestroyed: () => destroyed,
  })
  let destroyed = false
  let quitting = false
  let choose!: (value: { response: number }) => void
  showMessageBox.mockReturnValue(
    new Promise((resolve) => {
      choose = resolve
    }),
  )
  const reopen = vi.fn()
  installWindowRecovery(window as unknown as BrowserWindow, reopen, () => quitting)
  return {
    window,
    reopen,
    choose: (response: number) => choose({ response }),
    close: () => {
      destroyed = true
    },
    quit: () => {
      quitting = true
    },
  }
}

afterEach(() => vi.clearAllMocks())
describe('recovery dialog races', () => {
  it.each(['responsive', 'close', 'quit', 'decline'] as const)(
    'does not restart after %s while a dialog is pending',
    async (action) => {
      const f = fixture()
      f.window.emit('unresponsive')
      if (action === 'responsive') f.window.emit('responsive')
      if (action === 'close') f.close()
      if (action === 'quit') f.quit()
      f.choose(action === 'decline' ? 1 : 0)
      await Promise.resolve()
      expect(f.reopen).not.toHaveBeenCalled()
    },
  )
  it('coalesces hang then crash and still permits explicit recovery', async () => {
    const f = fixture()
    f.window.emit('unresponsive')
    f.window.webContents.emit('render-process-gone', {}, { reason: 'crashed' })
    f.window.emit('responsive')
    expect(showMessageBox).toHaveBeenCalledTimes(1)
    f.choose(0)
    await Promise.resolve()
    expect(f.reopen).toHaveBeenCalledTimes(1)
  })
  it('does not restart a renderer manually reloaded while a crash dialog was pending', async () => {
    const f = fixture()
    f.window.webContents.emit('render-process-gone', {}, { reason: 'crashed' })
    f.window.webContents.emit('did-finish-load')
    f.choose(0)
    await Promise.resolve()
    expect(f.reopen).not.toHaveBeenCalled()
  })
})
