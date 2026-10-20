import { contextBridge, ipcRenderer } from 'electron'
import { isTaskUpdate, type DesktopBridge } from '@ontolearn/contracts'

const bridge: DesktopBridge = {
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
