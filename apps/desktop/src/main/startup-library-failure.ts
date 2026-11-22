/**
 * Startup project-library failure convergence.
 *
 * `before-quit` can fire while `app.whenReady()` still awaits the startup
 * `libraryStatus()` verification (for example a test driver closing the app
 * before the first window exists). That quit's `stopAndWait()` makes the
 * awaited verification fail spuriously, so the startup failure path must
 * converge into the ongoing quit instead of opening a blocking modal dialog:
 * a synchronous error box on the main thread would stall the quit barrier and
 * `app.quit()` would never return.
 */
export interface StartupLibraryFailureDeps {
  /** True while a `before-quit` handler or an armed quit barrier already owns shutdown. */
  readonly quitConverging: () => boolean
  /** Stop the supervisor and confirm every engine process exited. */
  readonly stopAndWait: () => Promise<void>
  /** Blocking notice when engine exit could not be confirmed on the normal path. */
  readonly engineExitUnconfirmed: () => void
  /** Surface the library failure to the user on the normal path, then quit. */
  readonly reportFailure: () => Promise<void> | void
}

/**
 * Run the startup `libraryStatus()` failure sequence with quit convergence
 * checkpoints. At every checkpoint a converging quit wins: engines are not
 * stopped again, no dialog is shown, and the caller simply returns so the
 * `before-quit` handler's `stopAndWait()` → `app.quit()` completes.
 */
export async function convergeStartupLibraryFailure(
  deps: StartupLibraryFailureDeps,
): Promise<void> {
  if (deps.quitConverging()) return
  try {
    await deps.stopAndWait()
  } catch {
    if (deps.quitConverging()) return
    deps.engineExitUnconfirmed()
    return
  }
  if (deps.quitConverging()) return
  await deps.reportFailure()
}

export interface PreSupervisorRecoveryDeps {
  /** True while a `before-quit` handler or an armed quit barrier already owns shutdown. */
  readonly quitConverging: () => boolean
  /** Blocking recovery question; resolves the chosen dialog button index. */
  readonly promptNeedsRecovery: () => Promise<number>
  /** Point the startup back at the original library after the user confirms. */
  readonly restoreOriginal: () => void
  /** Quit the app when the user declines to continue with the original library. */
  readonly quitApp: () => void
}

/**
 * Complete the pre-supervisor library-recovery choice with quit convergence
 * checkpoints. A quit that fires before the dialog opens, while it is still
 * waiting, or right after the restore wins immediately: the caller must not
 * build an `EngineSupervisor` or spawn any child process after `false`.
 */
export async function completePreSupervisorRecoveryChoice(
  deps: PreSupervisorRecoveryDeps,
): Promise<boolean> {
  if (deps.quitConverging()) return false
  const response = await deps.promptNeedsRecovery()
  if (deps.quitConverging()) return false
  if (response !== 1) {
    deps.quitApp()
    return false
  }
  deps.restoreOriginal()
  return !deps.quitConverging()
}
