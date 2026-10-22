import { contextBridge, ipcRenderer } from 'electron'
import {
  isTaskUpdate,
  type DesktopBridge,
  type DesktopIpcChannel,
  type DesktopIpcMap,
} from '@ontolearn/contracts'

// The Electron serialization boundary is private; renderer receives named methods only.
function invokeFor<Channel extends DesktopIpcChannel>(channel: Channel) {
  return (...args: DesktopIpcMap[Channel]['args']): Promise<DesktopIpcMap[Channel]['result']> =>
    ipcRenderer.invoke(channel, ...args)
}

const bridge: DesktopBridge = {
  getEngineHealth: () => invokeFor('engine:health')(),
  restoreTasks: () => invokeFor('tasks:restore')(),
  getActiveProject: () => invokeFor('project:active')(),
  getJob: (id) => invokeFor('job:get')(id),
  listJobs: (options) => invokeFor('job:list')(options),
  cancelJob: (id) => invokeFor('job:cancel')(id),
  subscribeJob: (id) => invokeFor('job:subscribe')(id),
  unsubscribeJob: (jobId, generation) => invokeFor('job:unsubscribe')({ jobId, generation }),
  getResult: (id) => invokeFor('result:get')(id),
  getResultPage: (options) => invokeFor('result:page')(options),
  getOperation: (id) => invokeFor('operation:get')(id),
  onTaskUpdate: (listener) => {
    const receive = (_event: Electron.IpcRendererEvent, update: unknown) => {
      if (isTaskUpdate(update)) listener(update)
    }
    ipcRenderer.on('tasks:update', receive)
    return () => ipcRenderer.removeListener('tasks:update', receive)
  },
}
contextBridge.exposeInMainWorld('ontolearn', bridge)
