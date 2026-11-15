/** 项目生命周期准入的共享策略：真实逻辑的唯一来源，供 App 与单测共同使用。 */

export interface ManagementAdmissionTail {
  select(projectId?: string): unknown
  refresh(): Promise<void>
  readSelected(): Promise<void>
}

/** 打开/创建项目与自主恢复的 management 尾段。主进程 ProjectMainlineService
 * 是单并发模型：任何仍在飞行的 management 调用都会让紧随其后的项目读取
 * （readProject 等）得到 PERMISSION_DENIED。因此在渲染 selected-project-version
 * 或把工作台交还给用户之前，必须先串行完成全部 management 读取。 */
export async function settleManagementTail(
  management: ManagementAdmissionTail | undefined,
  projectId: string | undefined,
  options: { refresh?: boolean } = {},
): Promise<void> {
  if (!management || projectId === undefined) return
  management.select(projectId)
  if (options.refresh) await management.refresh()
  await management.readSelected()
}

export interface LibraryAdmissionState {
  documentLeaving: boolean
  libraryBusy: boolean
  frozen: boolean
  managementUnresolved: boolean
}

/** 项目/模块切换与新建共享的准入闸门。本体会话的未保存编辑（ontologyDirty）
 * 不在其中：切换会通过 retireOntology() 自动退役旧会话并丢弃未提交表单，
 * 不再硬阻断项目或模块切换；未提交编辑只保留在 aggregateWorkspace 的
 * dirty 报告里，用于拦截项目库高危迁移等破坏性操作。 */
export function libraryAdmissionBlocked(state: LibraryAdmissionState): boolean {
  return state.documentLeaving || state.libraryBusy || state.frozen || state.managementUnresolved
}
