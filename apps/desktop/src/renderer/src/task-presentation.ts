import { safeError, type SafeError, type JobView } from '@ontolearn/contracts'

export interface ErrorExplanation {
  what: string
  why: string
  fix: string
  detail: string
}
// Fixed, local templates use the validated message key and finite parameters.
// Exception text and catalog parameterMeanings never become UI copy.
export function explainError(
  value: SafeError,
  context: 'health' | 'task' | 'result',
): ErrorExplanation {
  const error = safeError(value)
  const base = {
    what: context === 'health' ? '本地引擎检查未完成。' : '本次操作未完成。',
    why: '系统无法确认本次操作的有效结果。',
    fix: '先刷新任务状态并核对已提交记录，再决定下一步。',
    detail: `错误代码：${error.code}。重试提示不代表允许自动重放写入。`,
  }
  switch (error.messageKey) {
    case 'permission.denied':
      return { ...base, why: '当前窗口没有该项目的访问授权。', fix: '返回已打开的项目后重新查询。' }
    case 'protocol.versionIncompatible':
      return {
        ...base,
        why: '桌面应用与本地引擎协议版本不一致。',
        fix: '使用同一版本的应用与引擎后重新检查。',
      }
    case 'capability.unsupported':
      return {
        ...base,
        what: '当前能力尚不支持。',
        why: '引擎未开放该能力。',
        fix: '返回已开放的功能，不会自动降级执行。',
      }
    case 'job.timeout': {
      const phases: Record<string, string> = {
        startup: '启动',
        handshake: '连接协商',
        request: '请求响应',
        total: '任务总时限',
        heartbeat: '连接心跳',
        cancel: '取消收尾',
      }
      return {
        ...base,
        why: `${phases[String(error.params.phase)] ?? '操作'}超过时限。`,
        fix: '刷新持久任务状态并查看提交点；未确认前不要重新提交写任务。',
      }
    }
    case 'engine.exited':
      return {
        ...base,
        what: '本地引擎连接已中断。',
        why: '协调器进程已退出，最终状态需要对账。',
        fix: '重新检查连接并刷新任务状态，确认提交点后再操作。',
      }
    case 'storage.failure':
      return {
        ...base,
        what: '本地存储操作未确认。',
        why: '存储返回故障，现有提交记录仍是依据。',
        fix: '保留项目文件并查看提交记录；确认存储可用后重新查询。',
      }
    case 'storage.busy':
    case 'job.queueFull':
      return {
        ...base,
        why: `存储或任务队列繁忙；建议等待 ${Number(error.params.retryAfterMs)} 毫秒。`,
        fix: '稍后手动刷新状态；系统不会自动重放写入。',
      }
    case 'project.revisionConflict':
      return {
        ...base,
        why: `项目版本已从预期 ${Number(error.params.expected)} 变为 ${Number(error.params.actual)}。`,
        fix: '刷新项目，重新预览并确认修改。',
      }
    case 'result.payloadEvicted':
      return {
        ...base,
        what: '结果载荷不可用。',
        why: '该不可变结果的载荷已回收，历史元数据仍保留。',
        fix: '查看历史来源；需要重新运行时明确选择输入并发起新任务。',
      }
    case 'result.cursorExpired':
    case 'result.cursorMismatch':
      return {
        ...base,
        what: '结果分页暂不可用。',
        why: '分页凭据已过期或与原结果不一致。',
        fix: '从同一不可变结果的第一页重新读取。',
      }
    case 'resource.notFound':
      return {
        ...base,
        why: '当前授权范围内未找到对应记录。',
        fix: '刷新项目与任务列表，核对历史选择。',
      }
    case 'mapping.valueInvalid':
      return {
        ...base,
        why: `工作表第 ${Number(error.params.row)} 行、第 ${Number(error.params.column)} 列无法通过映射校验。`,
        fix: '查看对应位置的输入与映射规则，修正后重新预览。',
      }
    case 'protocol.invalidRequest':
      return {
        ...base,
        why: '请求结构或绑定信息不符合已批准的契约。',
        fix: '刷新页面后重新查询；如仍出现，请保留错误代码。',
      }
    case 'protocol.sessionMismatch':
    case 'protocol.handshakeRequired':
      return {
        ...base,
        why: '当前连接会话已失效。',
        fix: '重新检查引擎并查询任务，不要重发原写任务。',
      }
    case 'operation.identityConflict':
      return {
        ...base,
        why: '该操作身份已绑定另一份完整输入。',
        fix: '查询原操作与提交记录，不要复用身份发送不同输入。',
      }
    case 'project.ownershipConflict':
      return {
        ...base,
        why: '修改与已登记的数据所有权冲突。',
        fix: '返回修改预览并核对所有权，重新确认处理方案。',
      }
    case 'resource.limitExceeded':
      return {
        ...base,
        why: '操作达到已配置的资源上限。',
        fix: '缩小输入或分页范围后显式发起新操作。',
      }
    case 'semantics.unsupportedConstruct':
      return {
        ...base,
        what: '该语义结构尚不支持。',
        why: '输入使用了当前实现范围以外的结构。',
        fix: '根据已开放的语义范围调整输入。',
      }
    case 'semantics.inputInvalid':
    case 'semantics.networkForbidden':
      return {
        ...base,
        why: '输入未满足本地语义执行边界。',
        fix: '检查输入与本地资源，修正后重新预览。',
      }
    case 'protocol.invalidState':
      return {
        ...base,
        why: '任务状态正在变化或不允许此操作。',
        fix: '刷新任务持久状态后再选择可用操作。',
      }
    case 'protocol.methodNotAllowed':
      return { ...base, why: '该请求不在允许的方法范围内。', fix: '返回已开放的界面入口。' }
    default:
      return base
  }
}
export function jobStatus(job: JobView): string {
  const labels = {
    queued: '排队中',
    running: '运行中',
    cancelling: '取消中（等待收尾）',
    succeeded: '任务已结束',
    failed: '执行失败',
    cancelled: '已取消（已提交历史保留）',
  }
  return labels[job.state]
}
export function resultSummary(page: Record<string, unknown>, job: JobView): string {
  const rows = page.rows
  if (!Array.isArray(rows) || !rows.length || job.state !== 'succeeded')
    return '运行摘要不可用；请查看持久状态与提交点。'
  const row = rows[0] as { cells?: unknown[] }
  const cells = row.cells
  if (
    !cells ||
    cells.length !== 8 ||
    cells[0] !== 'run.summary.v1' ||
    typeof cells[1] !== 'string' ||
    !Number.isInteger(cells[2]) ||
    Number(cells[2]) < 1 ||
    typeof cells[3] !== 'string' ||
    typeof cells[4] !== 'boolean' ||
    typeof cells[5] !== 'boolean' ||
    !Number.isInteger(cells[6]) ||
    Number(cells[6]) < 0 ||
    cells[5] !== Number(cells[6]) > 0 ||
    typeof cells[7] !== 'string'
  )
    return '运行摘要不可用；请查看持久状态与提交点。'
  const binding = page.binding as Record<string, unknown> | undefined
  const commit = job.commitProgress as
    | {
        mode?: string
        committedProgress?: {
          runId: string
          lastCommittedRound: number
          snapshotRef: string
        } | null
      }
    | undefined
  const progress = commit?.committedProgress
  if (
    !job.resultRef ||
    !binding ||
    binding.projectId !== job.projectId ||
    binding.resultId !== job.resultRef.resultId ||
    binding.inputSnapshotId !== job.inputSnapshotId ||
    binding.scope !== job.scope ||
    binding.parametersHash !== job.parametersHash ||
    commit?.mode !== 'rounds' ||
    !progress ||
    cells[1] !== progress.runId ||
    cells[2] !== progress.lastCommittedRound ||
    cells[3] !== progress.snapshotRef
  )
    return '运行摘要不可用；请查看持久状态与提交点。'
  // The producer also validates immutable summary against durable run and terminal evidence.
  return cells[5]
    ? `运行已结束 · 存在未处理事件（${Number(cells[6])}）`
    : '运行已结束 · 该事件队列为空'
}
