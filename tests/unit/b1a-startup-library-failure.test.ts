import { describe, expect, it, vi, type Mock } from 'vitest'
import {
  convergeStartupLibraryFailure,
  type StartupLibraryFailureDeps,
} from '../../apps/desktop/src/main/startup-library-failure'

interface Recording {
  quitting: boolean
  quitBarrier: boolean
  stopAndWait: Mock<() => Promise<void>>
  engineExitUnconfirmed: Mock<() => void>
  reportFailure: Mock<() => Promise<void>>
  deps(): StartupLibraryFailureDeps
}

function recorder(quitting = false, quitBarrier = false): Recording {
  const recording: Recording = {
    quitting,
    quitBarrier,
    stopAndWait: vi.fn(async () => {}),
    engineExitUnconfirmed: vi.fn(),
    reportFailure: vi.fn(async () => {}),
    deps: () => ({
      quitConverging: () => recording.quitting || recording.quitBarrier,
      stopAndWait: (...args: []) => recording.stopAndWait(...args),
      engineExitUnconfirmed: () => recording.engineExitUnconfirmed(),
      reportFailure: () => recording.reportFailure(),
    }),
  }
  return recording
}

describe('B1a startup libraryStatus failure quit convergence', () => {
  it('converges silently without engines, dialogs or a report when a quit already runs', async () => {
    const recording = recorder(true)
    await convergeStartupLibraryFailure(recording.deps())
    expect(recording.stopAndWait).not.toHaveBeenCalled()
    expect(recording.engineExitUnconfirmed).not.toHaveBeenCalled()
    expect(recording.reportFailure).not.toHaveBeenCalled()
  })
  it('converges silently when the armed quit barrier replaces the failure report', async () => {
    const recording = recorder()
    recording.stopAndWait.mockImplementation(async () => {
      // before-quit finishes its own stopAndWait and arms the process barrier.
      recording.quitting = true
      recording.quitBarrier = true
    })
    await convergeStartupLibraryFailure(recording.deps())
    expect(recording.stopAndWait).toHaveBeenCalledOnce()
    expect(recording.engineExitUnconfirmed).not.toHaveBeenCalled()
    expect(recording.reportFailure).not.toHaveBeenCalled()
  })
  it('converges without the unconfirmed-engine dialog when a quit starts while stopping fails', async () => {
    const recording = recorder()
    recording.stopAndWait.mockImplementation(async () => {
      recording.quitting = true
      throw new Error('stop interrupted by quit')
    })
    await convergeStartupLibraryFailure(recording.deps())
    expect(recording.engineExitUnconfirmed).not.toHaveBeenCalled()
    expect(recording.reportFailure).not.toHaveBeenCalled()
  })
  it('still reports the failure and quits through dialogs without any quit', async () => {
    const recording = recorder()
    await convergeStartupLibraryFailure(recording.deps())
    expect(recording.stopAndWait).toHaveBeenCalledOnce()
    expect(recording.engineExitUnconfirmed).not.toHaveBeenCalled()
    expect(recording.reportFailure).toHaveBeenCalledOnce()
  })
  it('still reports unconfirmed engine exit when stopping fails without any quit', async () => {
    const recording = recorder()
    recording.stopAndWait.mockRejectedValue(new Error('engine still running'))
    await convergeStartupLibraryFailure(recording.deps())
    expect(recording.engineExitUnconfirmed).toHaveBeenCalledOnce()
    expect(recording.reportFailure).not.toHaveBeenCalled()
  })
})
