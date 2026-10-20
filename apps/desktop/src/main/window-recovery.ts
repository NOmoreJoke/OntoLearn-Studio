import { dialog, type BrowserWindow } from 'electron'

type RecoveryReason = 'crashed' | 'unresponsive'

// Recovery recreates only the view. It never calls an engine method, replays a
// renderer request, deletes project data, or changes a durable commit marker.
export function installWindowRecovery(
  window: BrowserWindow,
  reopen: () => void,
  isQuitting: () => boolean,
): void {
  let prompting = false
  let responsive = true
  let gone = false
  const prompt = async (reason: RecoveryReason): Promise<void> => {
    if (prompting || isQuitting() || window.isDestroyed()) return
    prompting = true
    try {
      const { response } = await dialog.showMessageBox(window, {
        type: 'warning',
        title: 'OntoLearn Studio 窗口恢复',
        message: reason === 'crashed' ? '显示窗口已停止运行。' : '显示窗口暂时没有响应。',
        detail:
          '渲染进程异常或繁忙。可以重新打开窗口；已提交的本地数据不受窗口重建影响，未提交的界面输入可能丢失。恢复不会自动执行或重试任务。当前仅支持连接检查，重新打开后请手动检查本地引擎。',
        buttons: ['重新打开窗口', '暂不恢复'],
        defaultId: 1,
        cancelId: 1,
        noLink: true,
      })
      if (response === 0 && !isQuitting() && !window.isDestroyed() && (gone || !responsive))
        reopen()
    } catch {
      // A closed parent can dismiss the native dialog. Do not restart a closed window.
    } finally {
      prompting = false
    }
  }
  window.webContents.on('render-process-gone', (_event, details) => {
    if (details.reason === 'clean-exit') return
    gone = true
    void prompt('crashed')
  })
  window.webContents.on('did-finish-load', () => {
    gone = false
    responsive = true
  })
  window.on('unresponsive', () => {
    responsive = false
    void prompt('unresponsive')
  })
  window.on('responsive', () => {
    responsive = true
  })
}
