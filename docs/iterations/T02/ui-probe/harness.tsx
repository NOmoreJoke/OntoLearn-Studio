/** UI-state test harness only; deliberately no Store, IPC, or production capability. */
import { useState } from 'react'
import { createRoot } from 'react-dom/client'
import {
  OntologyPage,
  type EditIntent,
  type EditPreview,
} from '../../../../apps/desktop/src/renderer/src/ontology/OntologyPage'
import {
  type LocalizedText,
  type OntologyView,
} from '../../../../apps/desktop/src/renderer/src/ontology/view-model'
import fixture from './fixture.json'

// Type authored JSON fixture tuples explicitly; this is not a production boundary schema.
const localized = (values: readonly string[][]): readonly LocalizedText[] =>
  values.map((value) => {
    if (value.length !== 2) throw new Error('invalid fixture localized tuple')
    return [value[0], value[1]]
  })
const fixtureView: OntologyView = {
  ...fixture,
  objects: fixture.objects.map((row) => {
    const { kind, classType } = row
    if (
      kind !== 'class' &&
      kind !== 'objectProperty' &&
      kind !== 'dataProperty' &&
      kind !== 'individual'
    )
      throw new Error('invalid fixture object kind')
    if (classType !== undefined && classType !== 'rdfs' && classType !== 'owl')
      throw new Error('invalid fixture class declaration')
    return {
      ...row,
      kind,
      classType,
      labels: localized(row.labels),
      definitions: localized(row.definitions),
    }
  }),
}

function Harness() {
  const [view, setView] = useState(fixtureView)
  const [received, setReceived] = useState<EditIntent>()
  const [receivedBase, setReceivedBase] = useState<Pick<OntologyView, 'project' | 'revision'>>()
  const [failure, setFailure] = useState(false)
  const [delay, setDelay] = useState(false)
  const [release, setRelease] = useState<(() => void) | undefined>()
  async function previewEdit(intent: EditIntent, base: OntologyView): Promise<EditPreview> {
    setReceived(intent)
    setReceivedBase({ project: base.project, revision: base.revision })
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
      <pre aria-label="探针收到的基准">{JSON.stringify(receivedBase)}</pre>
      <OntologyPage
        view={view}
        previewEdit={previewEdit}
        requestDeleteImpact={async () => ['constraint:c1 引用了设备类（合成引用）']}
      />
    </>
  )
}
createRoot(document.getElementById('root')!).render(<Harness />)
