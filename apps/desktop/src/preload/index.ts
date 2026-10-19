import { contextBridge, ipcRenderer } from 'electron'
import type { DesktopBridge } from '@ontolearn/contracts'

const bridge: DesktopBridge = { getEngineHealth: () => ipcRenderer.invoke('engine:health') }
contextBridge.exposeInMainWorld('ontolearn', bridge)
