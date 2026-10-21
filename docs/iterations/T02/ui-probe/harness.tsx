/** UI-state test harness only; deliberately no Store, IPC, or production capability. */
import { useState } from 'react'
import { createRoot } from 'react-dom/client'
import {
  OntologyPage,
  type EditIntent,
  type EditPreview,
} from '../../../../apps/desktop/src/renderer/src/ontology/OntologyPage'
import { type OntologyView } from '../../../../apps/desktop/src/renderer/src/ontology/view-model'
import fixture from './fixture.json'

function Harness() {
  const [view, setView] = useState(fixture as OntologyView)
  const [received, setReceived] = useState<EditIntent>()
  const [failure, setFailure] = useState(false)
  const [delay, setDelay] = useState(false)
  const [release, setRelease] = useState<(() => void) | undefined>()
  async function previewEdit(intent: EditIntent, base: OntologyView): Promise<EditPreview> {
    setReceived(intent)
    if (failure) throw new Error('synthetic failure')
    if (delay) await new Promise<void>((resolve) => setRelease(() => resolve))
    return {
      project: base.project,
      revision: base.revision,
      summary: '合成 UI 状态响应，未提交',
      added: [],
      removed: [],
      metadataChanges: ['仅测试呈现'],
      impact: [],
    }
  }
  return (
    <>
      <p>仅用于无窗口组件状态探针；不代表引擎、Store 或正式产品接线。</p>
      <button onClick={() => setView((old) => ({ ...old, revision: old.revision + 1 }))}>
        探针：推进版本
      </button>
      <button onClick={() => setView((old) => ({ ...old, project: 'project-b' }))}>
        探针：切换项目
      </button>
      <button onClick={() => setFailure((old) => !old)}>探针：切换失败</button>
      <button onClick={() => setDelay((old) => !old)}>探针：切换延迟</button>
      <button
        onClick={() => {
          release?.()
          setRelease(undefined)
        }}
      >
        探针：释放回复
      </button>
      <pre aria-label="探针收到的意图">{JSON.stringify(received)}</pre>
      <OntologyPage
        view={view}
        previewEdit={previewEdit}
        requestDeleteImpact={async () => ['constraint:c1 引用了设备类（合成引用）']}
      />
    </>
  )
}
createRoot(document.getElementById('root')!).render(<Harness />)
