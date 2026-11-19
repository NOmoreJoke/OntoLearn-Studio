import type { IpcMain, IpcMainInvokeEvent } from 'electron'
import { randomUUID } from 'node:crypto'
import {
  mainlineDeliveryAckSchema,
  modelGatewayError,
  modelInvalidRequestError,
  type ModelMethod,
  safeError,
  type DesktopIpcChannel,
  type DesktopIpcHandlers,
  type DesktopIpcMap,
  type MainlineProjectBridge,
  type QueryConsumerBridge,
} from '@ontolearn/contracts'
import type { EngineSupervisor, MainlineReplyReceiver, MainlineReplyReceipt } from './engine'
import type { TaskService } from './task-service'
import type { LibraryLocationService } from './library-location-service'
import { validateModelParams } from '@ontolearn/contracts/v2'
import { unavailableModelStatus, type ModelGatewayService } from './model-gateway/model-service'

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
  projects?: MainlineProjectBridge & {
    readonly queries: QueryConsumerBridge
    readonly managementBlocked?: boolean
    readonly restoreBlocked?: boolean
  }
  replies?: MainlineReplyReceiver
  library?: LibraryLocationService
  getModels?: () => Pick<ModelGatewayService, 'handle'> | undefined
}

/** Register the production named routes. Trust is checked before any downstream call. */
export function registerDesktopIpc({
  ipcMain,
  trusted,
  tasks,
  supervisor,
  projects,
  replies,
  library,
  getModels,
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
  const modelRoutes: Record<string, ModelMethod> = {
    'model:status': 'getModelAccessStatus',
    'model:configure': 'configureModel',
    'model:credential': 'storeModelCredential',
    'model:privacy': 'setModelPrivacy',
    'model:select-results': 'selectModelResults',
    'model:field-catalog': 'getModelFieldCatalog',
    'model:select-fields': 'selectModelFields',
    'model:preview': 'previewModelExplanation',
    'model:confirm': 'confirmModelAuthorization',
    'model:start': 'startModelExplanation',
    'model:outcome': 'getModelExplanationOutcome',
    'model:cancel': 'cancelModelExplanation',
  }
  for (const [channel, method] of Object.entries(modelRoutes))
    ipcMain.handle(channel, (event, argument) => {
      if (!trusted(event) || library?.switching) return permission()
      if (!validateModelParams(method, argument))
        return { ok: false, error: modelInvalidRequestError() }
      const models = getModels?.()
      if (models) return models.handle(method, argument)
      return method === 'getModelAccessStatus' && !('auditContextId' in argument)
        ? { ok: true, data: unavailableModelStatus() }
        : { ok: false, error: modelGatewayError('MODEL_UNAVAILABLE') }
    })
  const handlers: DesktopIpcHandlers = {
    'project:checkpoint-list': (args) =>
      projects?.listProjectCheckpoints(args) ?? Promise.resolve(permission()),
    'project:checkpoint-create': (args) =>
      projects?.createProjectCheckpoint(args) ?? Promise.resolve(permission()),
    'project:restore-pending': () =>
      projects?.getPendingProjectRestoreOperations() ?? Promise.resolve(permission()),
    'project:restore-preview': (args) =>
      projects?.previewProjectRestore(args) ?? Promise.resolve(permission()),
    'project:restore-page': (args) =>
      projects?.getProjectRestorePage(args) ?? Promise.resolve(permission()),
    'project:restore-confirm': (args) =>
      projects?.confirmProjectRestore(args) ?? Promise.resolve(permission()),
    'project:restore-apply': (args) =>
      projects?.restoreProject(args) ?? Promise.resolve(permission()),
    'project:restore-operation': (args) =>
      projects?.getProjectRestoreOperation(args) ?? Promise.resolve(permission()),
    'project:quality-read': (args) =>
      projects?.getProjectQualityState(args) ?? Promise.resolve(permission()),
    'project:quality-prepare': (args) =>
      projects?.prepareProjectQualityCheck(args) ?? Promise.resolve(permission()),
    'project:quality-check': (args) =>
      projects?.runProjectQualityCheck(args) ?? Promise.resolve(permission()),
    'project:learning-read': (args) =>
      projects?.getProjectLearningState(args) ?? Promise.resolve(permission()),
    'project:learning-attempt-start': (args) =>
      projects?.startLearningAttempt(args) ?? Promise.resolve(permission()),
    'project:learning-hint-record': (args) =>
      projects?.recordLearningHint(args) ?? Promise.resolve(permission()),
    'project:learning-observation-record': (args) =>
      projects?.recordLearningObservation(args) ?? Promise.resolve(permission()),
    'project:learning-task-check': (args) =>
      projects?.checkLearningTask(args) ?? Promise.resolve(permission()),
    'project:management-pending': () =>
      projects?.getPendingProjectManagementOperations() ?? Promise.resolve(permission()),
    'project:management-catalog': (args) =>
      projects?.getProjectManagementCatalog(args) ?? Promise.resolve(permission()),
    'project:management-state': () =>
      projects?.getProjectManagementState() ?? Promise.resolve(permission()),
    'project:management-preview': (args) =>
      projects?.previewProjectManagement(args) ?? Promise.resolve(permission()),
    'project:management-confirm': (args) =>
      projects?.confirmProjectManagement(args) ?? Promise.resolve(permission()),
    'project:management-apply': (args) =>
      projects?.applyProjectManagement(args) ?? Promise.resolve(permission()),
    'project:management-operation': (args) =>
      projects?.getProjectManagementOperation(args) ?? Promise.resolve(permission()),
    'library:location': async () => library?.getLocation() ?? permission(),
    'library:choose': (args) => library?.choose(args) ?? Promise.resolve(permission()),
    // These two routes are bound to the real frame/document by register below.
    'library:workspace': async () => permission(),
    'library:switch': async () => permission(),
    'project:catalog': (args) => projects?.getProjectCatalog(args) ?? Promise.resolve(permission()),
    'project:create-blank': (args) =>
      projects?.createBlankProject(args) ?? Promise.resolve(permission()),
    'project:create-example': (args) =>
      projects?.createExampleProject(args) ?? Promise.resolve(permission()),
    'project:draft-save': (args) =>
      projects?.saveProjectDraft(args) ?? Promise.resolve(permission()),
    'project:open': (args) => projects?.openProject(args) ?? Promise.resolve(permission()),
    'project:read': (args) => projects?.readProject(args) ?? Promise.resolve(permission()),
    'project:ownership-detail': (args) =>
      projects?.getOwnershipConflictDetailPage(args) ?? Promise.resolve(permission()),
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
  const documents = new WeakMap<
    IpcMainInvokeEvent['sender'],
    { frame: IpcMainInvokeEvent['senderFrame']; token: object }
  >()
  const observed = new WeakSet<IpcMainInvokeEvent['sender']>()
  const documentFor = (event: IpcMainInvokeEvent): object => {
    const sender = event.sender
    if (!observed.has(sender)) {
      observed.add(sender)
      const invalidate = () => {
        const document = documents.get(sender)
        if (document) library?.invalidateDocument(document.token)
        documents.delete(sender)
      }
      sender.on('did-start-navigation', (_event, _url, isInPlace, isMainFrame) => {
        if (isMainFrame && !isInPlace) invalidate()
      })
      sender.once('destroyed', invalidate)
    }
    let document = documents.get(sender)
    if (!document || document.frame !== event.senderFrame) {
      if (document) library?.invalidateDocument(document.token)
      document = { frame: event.senderFrame, token: Object.freeze({}) }
      documents.set(sender, document)
    }
    return document.token
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
      if (channel === 'library:workspace')
        return (
          library?.reportWorkspace(
            args[0] as DesktopIpcMap['library:workspace']['args'][0],
            documentFor(event),
          ) ?? permission()
        )
      if (channel === 'library:switch')
        return (
          library?.switchLocation(
            args[0] as DesktopIpcMap['library:switch']['args'][0],
            documentFor(event),
          ) ?? permission()
        )
      if (library?.switching && channel !== 'library:location') return permission()
      if (
        (projects?.managementBlocked || projects?.restoreBlocked) &&
        [
          'project:create-blank',
          'project:create-example',
          'project:open',
          'project:draft-save',
          'project:changeset-preview',
          'project:changeset-confirm',
          'project:changeset-commit',
          'project:checkpoint-create',
          'project:restore-preview',
          'project:restore-confirm',
          'project:restore-apply',
          'project:learning-attempt-start',
          'project:learning-hint-record',
          'project:learning-observation-record',
          'project:learning-task-check',
          'project:quality-check',
          'project:quality-prepare',
          'query:execute-saved',
          'job:cancel',
        ].includes(channel)
      )
        return permission()
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
  register('project:checkpoint-list', handlers['project:checkpoint-list'])
  register('project:checkpoint-create', handlers['project:checkpoint-create'])
  register('project:restore-pending', handlers['project:restore-pending'])
  register('project:restore-preview', handlers['project:restore-preview'])
  register('project:restore-page', handlers['project:restore-page'])
  register('project:restore-confirm', handlers['project:restore-confirm'])
  register('project:restore-apply', handlers['project:restore-apply'])
  register('project:restore-operation', handlers['project:restore-operation'])
  register('project:quality-read', handlers['project:quality-read'])
  register('project:quality-prepare', handlers['project:quality-prepare'])
  register('project:quality-check', handlers['project:quality-check'])
  register('project:learning-read', handlers['project:learning-read'])
  register('project:learning-attempt-start', handlers['project:learning-attempt-start'])
  register('project:learning-hint-record', handlers['project:learning-hint-record'])
  register('project:learning-observation-record', handlers['project:learning-observation-record'])
  register('project:learning-task-check', handlers['project:learning-task-check'])
  register('project:management-pending', handlers['project:management-pending'])
  register('project:management-catalog', handlers['project:management-catalog'])
  register('project:management-state', handlers['project:management-state'])
  register('project:management-preview', handlers['project:management-preview'])
  register('project:management-confirm', handlers['project:management-confirm'])
  register('project:management-apply', handlers['project:management-apply'])
  register('project:management-operation', handlers['project:management-operation'])
  register('library:location', handlers['library:location'])
  register('library:choose', handlers['library:choose'])
  register('library:workspace', handlers['library:workspace'])
  register('library:switch', handlers['library:switch'])
  register('project:catalog', handlers['project:catalog'])
  register('project:create-blank', handlers['project:create-blank'])
  register('project:create-example', handlers['project:create-example'])
  register('project:draft-save', handlers['project:draft-save'])
  register('project:open', handlers['project:open'])
  register('project:read', handlers['project:read'])
  register('project:ownership-detail', handlers['project:ownership-detail'])
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
