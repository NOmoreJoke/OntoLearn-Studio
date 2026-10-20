import { contextBridge, ipcRenderer } from 'electron'
import { isTaskUpdate, type DesktopBridge } from '@ontolearn/contracts'

const bridge: DesktopBridge = {
  runSavedQuery: (options) => ipcRenderer.invoke('semantic:query', options),
  runReasoning: (options) => ipcRenderer.invoke('semantic:reasoning', options),
  runValidation: (options) => ipcRenderer.invoke('semantic:validation', options),
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
