import { contextBridge, ipcRenderer } from 'electron'
import {
  isTaskUpdate,
  mainlineDeliveryEnvelopeSchema,
  mainlineDeliveryAcceptedSchema,
  internalError,
  mainlineNoDeliverySchema,
  type DesktopBridge,
  type DesktopIpcChannel,
  type DesktopIpcMap,
} from '@ontolearn/contracts'

/** Private receipt confirmation; renderer receives only the named business result. */
async function receiveMainline<Channel extends DesktopIpcChannel>(
  channel: Channel,
  ...args: DesktopIpcMap[Channel]['args']
): Promise<DesktopIpcMap[Channel]['result']> {
  const raw: unknown = await ipcRenderer.invoke(channel, ...args)
  const delivery = mainlineDeliveryEnvelopeSchema.safeParse(raw)
  if (!delivery.success) {
    // A denied route can reply before any delivery lease is admitted.
    const denied = mainlineNoDeliverySchema.safeParse(raw)
    if (denied.success) return denied.data as DesktopIpcMap[Channel]['result']
    return { ok: false, error: internalError } as DesktopIpcMap[Channel]['result']
  }
  let timer: ReturnType<typeof setTimeout> | undefined
  try {
    const accepted: unknown = await Promise.race([
      ipcRenderer.invoke('project:reply-received', {
        deliveryVersion: 1,
        deliveryId: delivery.data.deliveryId,
      }),
      new Promise<never>((_, reject) => {
        timer = setTimeout(() => reject(new Error('delivery acknowledgment timeout')), 5000)
      }),
    ])
    const parsed = mainlineDeliveryAcceptedSchema.safeParse(accepted)
    if (!parsed.success || parsed.data.deliveryId !== delivery.data.deliveryId)
      throw new Error('delivery acknowledgment rejected')
  } catch {
    // The payload was actually received. Preserve its known durable outcome.
    // Main keeps the original unacknowledged lease; no retry/clear is fabricated.
  } finally {
    clearTimeout(timer)
  }
  return delivery.data.payload as DesktopIpcMap[Channel]['result']
}

const bridge: DesktopBridge = {
  listProjectCheckpoints: (args) => receiveMainline('project:checkpoint-list', args),
  createProjectCheckpoint: (args) => receiveMainline('project:checkpoint-create', args),
  getPendingProjectRestoreOperations: () => receiveMainline('project:restore-pending'),
  previewProjectRestore: (args) => receiveMainline('project:restore-preview', args),
  getProjectRestorePage: (args) => receiveMainline('project:restore-page', args),
  confirmProjectRestore: (args) => receiveMainline('project:restore-confirm', args),
  restoreProject: (args) => receiveMainline('project:restore-apply', args),
  getProjectRestoreOperation: (args) => receiveMainline('project:restore-operation', args),
  getProjectQualityState: (args) => receiveMainline('project:quality-read', args),
  prepareProjectQualityCheck: (args) => receiveMainline('project:quality-prepare', args),
  runProjectQualityCheck: (args) => receiveMainline('project:quality-check', args),
  getProjectLearningState: (args) => receiveMainline('project:learning-read', args),
  startLearningAttempt: (args) => receiveMainline('project:learning-attempt-start', args),
  recordLearningHint: (args) => receiveMainline('project:learning-hint-record', args),
  recordLearningObservation: (args) => receiveMainline('project:learning-observation-record', args),
  checkLearningTask: (args) => receiveMainline('project:learning-task-check', args),
  getPendingProjectManagementOperations: () => receiveMainline('project:management-pending'),
  getProjectManagementCatalog: (args) => receiveMainline('project:management-catalog', args),
  getProjectManagementState: () => receiveMainline('project:management-state'),
  previewProjectManagement: (args) => receiveMainline('project:management-preview', args),
  confirmProjectManagement: (args) => receiveMainline('project:management-confirm', args),
  applyProjectManagement: (args) => receiveMainline('project:management-apply', args),
  getProjectManagementOperation: (args) => receiveMainline('project:management-operation', args),
  getLibraryLocation: () => ipcRenderer.invoke('library:location'),
  chooseLibraryLocation: (args) => ipcRenderer.invoke('library:choose', args),
  reportLibraryWorkspace: (args) => ipcRenderer.invoke('library:workspace', args),
  switchLibraryLocation: (args) => ipcRenderer.invoke('library:switch', args),
  getProjectCatalog: (args) => receiveMainline('project:catalog', args),
  createBlankProject: (args) => receiveMainline('project:create-blank', args),
  createExampleProject: (args) => receiveMainline('project:create-example', args),
  saveProjectDraft: (args) => receiveMainline('project:draft-save', args),
  openProject: (args) => receiveMainline('project:open', args),
  readProject: (args) => receiveMainline('project:read', args),
  getOwnershipConflictDetailPage: (args) => receiveMainline('project:ownership-detail', args),
  previewProjectChangeset: (args) => receiveMainline('project:changeset-preview', args),
  getProjectDiffPage: (args) => receiveMainline('project:changeset-diff-page', args),
  confirmProjectChangeset: (args) => receiveMainline('project:changeset-confirm', args),
  commitProjectChangeSet: (args) => receiveMainline('project:changeset-commit', args),
  getQueryDefinitionBase: () => receiveMainline('query:definition-base'),
  loadQueryDefinition: (args) => receiveMainline('query:definition-load', args),
  executeSavedQuery: (args) => receiveMainline('query:execute-saved', args),
  getQueryResultDescriptor: (args) => receiveMainline('query:result-describe', args),
  getQueryExecutedTextPage: (args) => receiveMainline('query:result-text-page', args),
  getQueryRowsPage: (args) => receiveMainline('query:result-rows-page', args),
  getModelAccessStatus: (params) => ipcRenderer.invoke('model:status', params),
  configureModel: (params) => ipcRenderer.invoke('model:configure', params),
  storeModelCredential: (params) => ipcRenderer.invoke('model:credential', params),
  setModelPrivacy: (params) => ipcRenderer.invoke('model:privacy', params),
  selectModelResults: (params) => ipcRenderer.invoke('model:select-results', params),
  getModelFieldCatalog: (params) => ipcRenderer.invoke('model:field-catalog', params),
  selectModelFields: (params) => ipcRenderer.invoke('model:select-fields', params),
  previewModelExplanation: (params) => ipcRenderer.invoke('model:preview', params),
  confirmModelAuthorization: (params) => ipcRenderer.invoke('model:confirm', params),
  startModelExplanation: (params) => ipcRenderer.invoke('model:start', params),
  getModelExplanationOutcome: (params) => ipcRenderer.invoke('model:outcome', params),
  cancelModelExplanation: (params) => ipcRenderer.invoke('model:cancel', params),
  getEngineHealth: () => ipcRenderer.invoke('engine:health'),
  restoreTasks: () => ipcRenderer.invoke('tasks:restore'),
  getActiveProject: () => ipcRenderer.invoke('project:active'),
  getJob: (id) => ipcRenderer.invoke('job:get', id),
  listJobs: (options) => ipcRenderer.invoke('job:list', options),
  cancelJob: (id) => ipcRenderer.invoke('job:cancel', id),
  subscribeJob: (id) => ipcRenderer.invoke('job:subscribe', id),
  unsubscribeJob: (jobId, generation) =>
    ipcRenderer.invoke('job:unsubscribe', { jobId, generation }),
  getResult: (id) => ipcRenderer.invoke('result:get', id),
  getResultPage: (options) => ipcRenderer.invoke('result:page', options),
  getOperation: (id) => ipcRenderer.invoke('operation:get', id),
  onTaskUpdate: (listener) => {
    const receive = (_event: Electron.IpcRendererEvent, update: unknown) => {
      if (isTaskUpdate(update)) listener(update)
    }
    ipcRenderer.on('tasks:update', receive)
    return () => ipcRenderer.removeListener('tasks:update', receive)
  },
}
contextBridge.exposeInMainWorld('ontolearn', bridge)
