import type { IpcMain, IpcMainInvokeEvent } from 'electron'
import {
  safeError,
  type DesktopIpcChannel,
  type DesktopIpcHandlers,
  type DesktopIpcMap,
} from '@ontolearn/contracts'
import type { EngineSupervisor } from './engine'
import type { TaskService } from './task-service'

export type DesktopIpcDependencies = {
  ipcMain: Pick<IpcMain, 'handle'>
  trusted: (event: IpcMainInvokeEvent) => boolean
  tasks: Pick<
    TaskService,
    | 'restore'
    | 'activeProject'
    | 'getJob'
    | 'listJobs'
    | 'cancelJob'
    | 'subscribeJob'
    | 'unsubscribeView'
    | 'getResult'
    | 'getResultPage'
    | 'getOperation'
  >
  supervisor: Pick<EngineSupervisor, 'health' | 'projectFailure'>
}

/** Register the production named routes. Trust is checked before any downstream call. */
export function registerDesktopIpc({
  ipcMain,
  trusted,
  tasks,
  supervisor,
}: DesktopIpcDependencies): void {
  const permission = () => ({
    ok: false as const,
    error: safeError({
      code: 'PERMISSION_DENIED',
      messageKey: 'permission.denied',
      params: {},
      retryable: false,
    }),
  })
  const handlers: DesktopIpcHandlers = {
    'engine:health': async () => {
      const operation = supervisor.health()
      try {
        return { ok: true, data: await operation }
      } catch (error) {
        return { ok: false, error: supervisor.projectFailure(error, operation) }
      }
    },
    'tasks:restore': () => tasks.restore(),
    'project:active': () => tasks.activeProject(),
    'job:get': (id) => tasks.getJob(id),
    'job:list': (options) => tasks.listJobs(options),
    'job:cancel': (id) => tasks.cancelJob(id),
    'job:subscribe': (id) => tasks.subscribeJob(id),
    'job:unsubscribe': (request) => tasks.unsubscribeView(request),
    'result:get': (id) => tasks.getResult(id),
    'result:page': (options) => tasks.getResultPage(options),
    'operation:get': (id) => tasks.getOperation(id),
  }
  const register = <Channel extends DesktopIpcChannel>(
    channel: Channel,
    handler: (...args: DesktopIpcMap[Channel]['args']) => Promise<DesktopIpcMap[Channel]['result']>,
  ): void => {
    ipcMain.handle(channel, (event, ...args: DesktopIpcMap[Channel]['args']) =>
      trusted(event) ? handler(...args) : permission(),
    )
  }
  register('engine:health', handlers['engine:health'])
  register('tasks:restore', handlers['tasks:restore'])
  register('project:active', handlers['project:active'])
  register('job:get', handlers['job:get'])
  register('job:list', handlers['job:list'])
  register('job:cancel', handlers['job:cancel'])
  register('job:subscribe', handlers['job:subscribe'])
  register('job:unsubscribe', handlers['job:unsubscribe'])
  register('result:get', handlers['result:get'])
  register('result:page', handlers['result:page'])
  register('operation:get', handlers['operation:get'])
}
