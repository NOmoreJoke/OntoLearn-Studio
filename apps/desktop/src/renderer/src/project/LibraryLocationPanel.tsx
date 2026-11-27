import { useEffect, useState } from 'react'
import type {
  LibraryLocationBridge,
  LibraryLocationChoice,
  LibraryLocationView,
  LibraryWorkspaceReport,
} from '@ontolearn/contracts'

export function LibraryLocationPanel({
  bridge,
  disabled,
  report,
  freeze,
}: {
  bridge: LibraryLocationBridge
  disabled: boolean
  report: () => LibraryWorkspaceReport
  freeze: (value: boolean) => void
}) {
  const [location, setLocation] = useState<LibraryLocationView>()
  const [choice, setChoice] = useState<LibraryLocationChoice>()
  const [busy, setBusy] = useState(false)
  const [switchPending, setSwitchPending] = useState(false)
  const [notice, setNotice] = useState('')
  useEffect(() => {
    let live = true
    void bridge
      .getLibraryLocation()
      .then((result) => {
        if (!live) return
        if (result.ok) setLocation(result.data)
        else setNotice(`无法读取项目库位置（${result.error.code}）。`)
      })
      .catch(() => {
        if (live) setNotice('无法读取项目库位置，请稍后重试。')
      })
    return () => {
      live = false
    }
  }, [bridge])
  async function choose(intent: 'create' | 'open') {
    if (busy || disabled) return
    freeze(true)
    setBusy(true)
    setNotice('')
    let retained = false
    try {
      const state = report()
      const reported = await bridge.reportLibraryWorkspace(state)
      if (!reported.ok || state.dirty || state.unresolved) {
        setNotice('请先保存或清空编辑表单，并核对未完成操作，再切换项目库。')
        return
      }
      const result = await bridge.chooseLibraryLocation({ intent })
      if (!result.ok) setNotice(`未能选择项目库（${result.error.code}）。`)
      else if (result.data) {
        setChoice(result.data)
        retained = true
      } else setNotice('已取消选择，当前项目库保持。')
    } catch {
      setNotice('未能选择项目库，当前项目库保持。')
    } finally {
      setBusy(false)
      if (!retained) freeze(false)
    }
  }
  async function switchLocation() {
    if (!choice || busy) return
    setBusy(true)
    try {
      const state = report()
      const reported = await bridge.reportLibraryWorkspace(state)
      if (!reported.ok || state.dirty || state.unresolved) {
        setNotice('编辑或操作状态已变化，请取消并先核对当前工作。')
        return
      }
      const result = await bridge.switchLibraryLocation({
        choiceRef: choice.choiceRef,
        documentNonce: state.documentNonce,
        workspaceGeneration: state.generation,
      })
      if (!result.ok) {
        setNotice(
          `尚未完成切换（${result.error.code}）。请先保存或清空编辑、等待或核对未完成操作。`,
        )
        const current = await bridge.getLibraryLocation()
        if (!current.ok || current.data.pending) {
          setSwitchPending(true)
          setNotice(
            '切换尚未完成或状态未确认，编辑继续冻结。请关闭并重新打开应用，按启动提示恢复原项目库或退出。',
          )
        } else setLocation(current.data)
      } else {
        setSwitchPending(true)
        setNotice('已请求重启，正在等待旧引擎关闭。')
        return
      }
    } catch {
      setSwitchPending(true)
      setNotice('未确认切换结果，编辑继续冻结。请关闭并重新打开应用后核对；不会自动重复切换。')
    } finally {
      setBusy(false)
    }
  }
  return (
    <section className="project-location" aria-label="项目库位置">
      <h3>项目库位置</h3>
      <p data-testid="library-location">{location?.label ?? '正在读取本机项目库位置…'}</p>
      <p>新项目创建在此项目库中。选择其他位置后将明确重启应用；旧库项目不会搬迁或覆盖。</p>
      {location?.pending && <p role="alert">存在待完成的项目库切换，请核对启动恢复状态。</p>}
      <button
        type="button"
        disabled={disabled || busy || !!choice}
        onClick={() => void choose('create')}
      >
        选择空目录建立项目库
      </button>
      <button
        type="button"
        disabled={disabled || busy || !!choice}
        onClick={() => void choose('open')}
      >
        选择已有项目库
      </button>
      {choice && (
        <div role="dialog" aria-label="确认切换项目库" className="project-confirmation">
          <p>目标：{choice.label}</p>
          <p>确认后等待当前引擎安全退出，再重启打开所选项目库。不会自动取消任务。</p>
          <button
            type="button"
            disabled={busy || switchPending}
            onClick={() => void switchLocation()}
          >
            确认并重启到此项目库
          </button>
          <button
            type="button"
            disabled={busy || switchPending}
            onClick={() => {
              setChoice(undefined)
              freeze(false)
              setNotice('已取消切换。')
            }}
          >
            取消切换
          </button>
        </div>
      )}
      <p data-testid="library-location-notice" aria-live="polite">
        {notice}
      </p>
    </section>
  )
}
