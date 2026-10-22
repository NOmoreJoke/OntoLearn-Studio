import type {
  BridgeResult,
  DesktopBridge,
  DesktopIpcChannel,
  DesktopIpcHandlers,
  DesktopIpcMap,
  ResultMetadataDTO,
  ResultPageDTO,
} from '@ontolearn/contracts'

declare function invoke<Channel extends DesktopIpcChannel>(
  channel: Channel,
  ...args: DesktopIpcMap[Channel]['args']
): Promise<DesktopIpcMap[Channel]['result']>

// Compile-only witnesses: this function is deliberately never called by runtime tests.
export function desktopIpcTypeWitness(
  bridge: DesktopBridge,
  handlers: DesktopIpcHandlers,
  metadata: ResultMetadataDTO,
  page: ResultPageDTO,
  result: BridgeResult<ResultMetadataDTO>,
): void {
  const channels = {
    'engine:health': true,
    'tasks:restore': true,
    'project:active': true,
    'job:get': true,
    'job:list': true,
    'job:cancel': true,
    'job:subscribe': true,
    'job:unsubscribe': true,
    'result:get': true,
    'result:page': true,
    'operation:get': true,
  } satisfies Record<DesktopIpcChannel, true>
  const metadataRequest: Promise<BridgeResult<ResultMetadataDTO>> = invoke('result:get', 'R')
  const pageRequest: Promise<BridgeResult<ResultPageDTO>> = invoke('result:page', {
    resultId: 'R',
    pageSize: 20,
    cursor: null,
  })
  void invoke('engine:health')
  void invoke('job:unsubscribe', { jobId: 'J', generation: 2 })
  void bridge.unsubscribeJob('J', 2)
  const recordMetadata: Record<string, unknown> = metadata
  const recordPage: Record<string, unknown> = page
  type Presentation = typeof import('../../apps/desktop/src/renderer/src/task-presentation')
  type PresentResult = Presentation['resultSummary']
  const presentationInput: Parameters<PresentResult>[0] = page
  const metadataHandler: DesktopIpcHandlers['result:get'] = handlers['result:get']
  void [channels, metadataRequest, pageRequest, recordMetadata, recordPage, presentationInput]
  void metadataHandler

  // @ts-expect-error unknown channels are outside the finite invoke surface
  void invoke('result:any', 'R')
  // @ts-expect-error tasks:update is an event, not an invoke channel
  void invoke('tasks:update')
  // @ts-expect-error metadata uses a result ID, not page options
  void invoke('result:get', { resultId: 'R', pageSize: 20, cursor: null })
  // @ts-expect-error page uses an options tuple, not an ID tuple
  void invoke('result:page', 'R')
  // @ts-expect-error health has no arguments
  void invoke('engine:health', 'P')
  // @ts-expect-error job:get requires its one argument
  void invoke('job:get')
  // @ts-expect-error job:get accepts one argument only
  void invoke('job:get', 'J', 'P')
  // @ts-expect-error unsubscribe IPC takes one object, unlike the public two-argument method
  void invoke('job:unsubscribe', 'J', 2)
  // @ts-expect-error generation is numeric
  void invoke('job:unsubscribe', { jobId: 'J', generation: '2' })
  // @ts-expect-error page options do not confer project authority
  void bridge.getResultPage({ resultId: 'R', pageSize: 20, cursor: null, projectId: 'P' })
  // @ts-expect-error the named bridge has no generic invoke method
  void bridge.invoke('job:get', 'J')
  // @ts-expect-error Electron's renderer transport is not a public bridge property
  void bridge.ipcRenderer
  // @ts-expect-error a page handler cannot replace a job handler
  const wrongJobHandler: DesktopIpcHandlers['job:get'] = handlers['result:page']
  // @ts-expect-error successful job:get cannot have a null payload
  const nullJob: DesktopIpcHandlers['job:get'] = async () => ({ ok: true, data: null })
  // @ts-expect-error a page payload cannot serve as metadata
  const wrongMetadata: DesktopIpcHandlers['result:get'] = async () => ({ ok: true, data: page })
  // @ts-expect-error health success must carry the complete health DTO
  const wrongHealth: DesktopIpcHandlers['engine:health'] = async () => ({ ok: true, data: null })
  // @ts-expect-error metadata requires all seventeen fields
  const incomplete: ResultMetadataDTO = { resultId: 'R' }
  // @ts-expect-error the channel key union cannot admit a twelfth generic channel
  const extraChannel: DesktopIpcChannel = 'engine:request'
  void [wrongJobHandler, nullJob, wrongMetadata, wrongHealth, incomplete, extraChannel]
  if (result.ok) {
    const full: ResultMetadataDTO = result.data
    // @ts-expect-error success is not also an error branch
    void result.error
    void full
  } else {
    const code: string = result.error.code
    // @ts-expect-error failure cannot supply a success payload
    void result.data
    void code
  }
}
