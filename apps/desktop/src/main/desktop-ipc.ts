import type { IpcMain, IpcMainInvokeEvent } from 'electron'
import { randomUUID } from 'node:crypto'
import {
  mainlineDeliveryAckSchema,
  safeError,
  type DesktopIpcChannel,
  type DesktopIpcHandlers,
  type DesktopIpcMap,
  type MainlineProjectBridge,
  type QueryConsumerBridge,
} from '@ontolearn/contracts'
import type { EngineSupervisor, MainlineReplyReceiver, MainlineReplyReceipt } from './engine'
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
  supervisor: Pick<EngineSupervisor, 'health' | 'projectFailure' | 'engineSessionId'>
  projects?: MainlineProjectBridge & { readonly queries: QueryConsumerBridge }
  replies?: MainlineReplyReceiver
}

/** Register the production named routes. Trust is checked before any downstream call. */
export function registerDesktopIpc({
  ipcMain,
  trusted,
  tasks,
  supervisor,
  projects,
  replies,
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
    'project:catalog': (args) => projects?.getProjectCatalog(args) ?? Promise.resolve(permission()),
    'project:create-blank': (args) =>
      projects?.createBlankProject(args) ?? Promise.resolve(permission()),
    'project:create-example': (args) =>
      projects?.createExampleProject(args) ?? Promise.resolve(permission()),
    'project:draft-save': (args) =>
      projects?.saveProjectDraft(args) ?? Promise.resolve(permission()),
    'project:open': (args) => projects?.openProject(args) ?? Promise.resolve(permission()),
    'project:read': (args) => projects?.readProject(args) ?? Promise.resolve(permission()),
    'project:changeset-preview': (args) =>
      projects?.previewProjectChangeset(args) ?? Promise.resolve(permission()),
    'project:changeset-diff-page': (args) =>
      projects?.getProjectDiffPage(args) ?? Promise.resolve(permission()),
    'project:changeset-confirm': (args) =>
      projects?.confirmProjectChangeset(args) ?? Promise.resolve(permission()),
    'project:changeset-commit': (args) =>
      projects?.commitProjectChangeSet(args) ?? Promise.resolve(permission()),
    'query:definition-base': () =>
      projects?.queries.getQueryDefinitionBase() ?? Promise.resolve(permission()),
    'query:definition-load': (args) =>
      projects?.queries.loadQueryDefinition(args) ?? Promise.resolve(permission()),
    'query:execute-saved': (args) =>
      projects?.queries.executeSavedQuery(args) ?? Promise.resolve(permission()),
    'query:result-describe': (args) =>
      projects?.queries.getQueryResultDescriptor(args) ?? Promise.resolve(permission()),
    'query:result-text-page': (args) =>
      projects?.queries.getQueryExecutedTextPage(args) ?? Promise.resolve(permission()),
    'query:result-rows-page': (args) =>
      projects?.queries.getQueryRowsPage(args) ?? Promise.resolve(permission()),
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
  // A delivery stays owned until this exact preload/frame acknowledges it.
  // No timeout, navigation or new session deletes an unacknowledged receipt.
  const deliveries = new Map<
    string,
    {
      sender: IpcMainInvokeEvent['sender']
      frame: IpcMainInvokeEvent['senderFrame']
      session: string | undefined
      receipt: MainlineReplyReceipt
    }
  >()
  const accepted = new Map<
    string,
    {
      sender: IpcMainInvokeEvent['sender']
      frame: IpcMainInvokeEvent['senderFrame']
      session: string | undefined
    }
  >()
  ipcMain.handle('project:reply-received', (event, raw: unknown) => {
    if (!trusted(event) || !replies) return permission()
    const parsed = mainlineDeliveryAckSchema.safeParse(raw)
    if (!parsed.success) return permission()
    const id = parsed.data.deliveryId
    const pending = deliveries.get(id)
    const delivery = pending ?? accepted.get(id)
    if (
      !delivery ||
      event.sender !== delivery.sender ||
      event.senderFrame !== delivery.frame ||
      supervisor.engineSessionId !== delivery.session
    )
      return permission()
    if (pending) {
      try {
        replies.consume(pending.receipt)
      } catch {
        return permission()
      }
      deliveries.delete(id)
      // Only bounded recent receipt identities support duplicate acknowledgments.
      if (accepted.size >= 16) accepted.delete(accepted.keys().next().value!)
      accepted.set(id, {
        sender: delivery.sender,
        frame: delivery.frame,
        session: delivery.session,
      })
    }
    return { deliveryVersion: 1, deliveryId: id, accepted: true }
  })
  const register = <Channel extends DesktopIpcChannel>(
    channel: Channel,
    handler: (...args: DesktopIpcMap[Channel]['args']) => Promise<DesktopIpcMap[Channel]['result']>,
  ): void => {
    ipcMain.handle(channel, async (event, ...args: DesktopIpcMap[Channel]['args']) => {
      if (!trusted(event)) return permission()
      const mainline =
        (channel.startsWith('project:') && channel !== 'project:active') ||
        channel.startsWith('query:')
      if (!mainline) return handler(...args)
      if (!projects || !replies) return permission()
      if (deliveries.size >= 16) return permission()
      const originalSender = event.sender,
        originalFrame = event.senderFrame
      // The registered receiver reserves its global slot before invoking work;
      // its same limit includes concurrent calls and UNKNOWN receipts.
      let delivery: Awaited<ReturnType<MainlineReplyReceiver['receive']>>
      try {
        delivery = await replies.receive(() => handler(...args))
      } catch {
        return permission()
      } // Issuer retains unknown; no raw exception crosses IPC.
      const deliveryId = randomUUID()
      deliveries.set(deliveryId, {
        sender: originalSender,
        frame: originalFrame,
        session: replies.binding(delivery.receipt).engineSessionId,
        receipt: delivery.receipt,
      })
      return { deliveryVersion: 1, deliveryId, payload: delivery.value }
    })
  }
  register('engine:health', handlers['engine:health'])
  register('project:catalog', handlers['project:catalog'])
  register('project:create-blank', handlers['project:create-blank'])
  register('project:create-example', handlers['project:create-example'])
  register('project:draft-save', handlers['project:draft-save'])
  register('project:open', handlers['project:open'])
  register('project:read', handlers['project:read'])
  register('project:changeset-preview', handlers['project:changeset-preview'])
  register('project:changeset-diff-page', handlers['project:changeset-diff-page'])
  register('project:changeset-confirm', handlers['project:changeset-confirm'])
  register('project:changeset-commit', handlers['project:changeset-commit'])
  register('query:definition-base', handlers['query:definition-base'])
  register('query:definition-load', handlers['query:definition-load'])
  register('query:execute-saved', handlers['query:execute-saved'])
  register('query:result-describe', handlers['query:result-describe'])
  register('query:result-text-page', handlers['query:result-text-page'])
  register('query:result-rows-page', handlers['query:result-rows-page'])
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
