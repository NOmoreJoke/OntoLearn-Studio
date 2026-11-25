import { useState } from 'react'
import {
  defaultProjectPackageOptions,
  type HtmlReportPrepareResultDTO,
  type PackageExportCheckResultDTO,
  type PackageImportCheckResultDTO,
  type ProjectPackageKind,
  type ProjectPackageOptions,
  type ProjectPackagePortabilityDTO,
  type TransferBridge,
  type TransferPickerPurpose,
  type TransferPublicationReceiptDTO,
} from '@ontolearn/contracts'
import { validateBusiness3 } from '@ontolearn/contracts/v2'
import { maskLocalPaths } from '../mapping/local-text'
import { useWorkspaceOperation, type ReportWorkspaceStatus } from '../mapping/workspace-operation'
import { requireWorkspaceReply } from '../ontology/workspace-change'
import { TransferPanel } from './TransferPanel'
import './transfer.css'

const optionLabels: Record<keyof ProjectPackageOptions, string> = {
  agentSessions: 'Agent 会话',
  rawSources: '原始数据文件',
  derived: '当前推导结果',
  history: '历史运行输入与结果',
}
const rejectionLabels: Record<
  Extract<PackageImportCheckResultDTO, { status: 'rejected' }>['reason'],
  string
> = {
  'format-unsupported': '不支持该项目包格式',
  'reader-too-old': '当前应用读取版本过低',
  'writer-too-old': '当前应用写入版本过低',
  'database-unsupported': '不支持该数据库版本',
  'checkpoint-unsupported': '不支持该检查点版本',
  'application-unsupported': '不支持该应用状态版本',
  'kind-mismatch': '选择的类型与项目包类型不符',
  'unsafe-package': '项目包未通过安全检查',
}
const missingLabels: Record<ProjectPackagePortabilityDTO['missing'][number], string> = {
  'raw-source': '原始数据文件',
  'mapping-definition': '映射定义',
  history: '历史记录',
  'scenario-input': '场景输入',
  'scenario-configuration': '场景配置',
  'execution-semantics': '执行语义',
}

export function publicationNeedsReconciliation(receipt: TransferPublicationReceiptDTO) {
  return (
    receipt.state === 'publication-unconfirmed' ||
    receipt.cleanup === 'pending' ||
    (receipt.state === 'published' &&
      (receipt.durability === 'unconfirmed' || receipt.postPublicationError))
  )
}
export function PublicationReceipt({ value }: { value: TransferPublicationReceiptDTO }) {
  const failure = {
    'destination-invalid': '目标无效',
    'target-exists': '目标已存在',
    busy: '目标正被使用',
    'cleanup-pending': '待清理',
    'write-failed': '写入失败',
  }
  return (
    <section aria-label="文件写入回执" role="status">
      {value.state === 'published' && (
        <p>
          已发布 · 持久性{value.durability === 'confirmed' ? '已确认' : '待确认'}
          {value.postPublicationError ? ' · 写入后检查有误' : ''}
        </p>
      )}
      {value.state === 'publication-unconfirmed' && <p>文件可能已写入，发布尚未确认。</p>}
      {value.state === 'cancelled' && <p>已取消写入。</p>}
      {value.state === 'failed' && (
        <p>
          写入失败 · {failure[value.code]}（{value.code}）
        </p>
      )}
      {'sha256' in value && (
        <p>
          SHA-256 {value.sha256} · {value.byteLength} 字节
        </p>
      )}
      <p>清理{value.cleanup === 'complete' ? '完成' : '待确认'}</p>
    </section>
  )
}

function PackageCheck({
  value,
}: {
  value:
    PackageExportCheckResultDTO | Extract<PackageImportCheckResultDTO, { status: 'compatible' }>
}) {
  const { manifest, portability, conflictPolicy } = value
  return (
    <section aria-label="项目包检查结果">
      <p>
        {manifest.kind === 'full' ? '完整项目包' : '模板包'} · {manifest.formatVersion}
      </p>
      <p>
        数据库 {manifest.dbFormatVersion} · 检查点 {manifest.checkpointSchemaVersion} · 应用状态{' '}
        {manifest.applicationStateVersion} · 最低读取 {manifest.minReaderVersion} · 最低写入{' '}
        {manifest.minWriterVersion}
      </p>
      {'packageSha256' in value && <p>包 SHA-256 {value.packageSha256}</p>}
      <dl>
        <dt>恢复当前项目</dt>
        <dd>{portability.restoreCurrent ? '支持' : '不可用'}</dd>
        <dt>重跑原始映射</dt>
        <dd>{portability.rerunMapping ? '支持' : '不可用'}</dd>
        <dt>重放沙盘运行</dt>
        <dd>{portability.replayScenario ? '支持' : '不可用'}</dd>
        <dt>缺少依赖</dt>
        <dd>{portability.missing.map((key) => missingLabels[key]).join('、') || '无'}</dd>
      </dl>
      <p>
        冲突策略 v{conflictPolicy.version} · 拒绝所有权冲突 · 导入分配新的项目标识 ·{' '}
        {conflictPolicy.fingerprint}
      </p>
      <details open>
        <summary>实际项目包清单（{manifest.files.length} 项）</summary>
        <ul>
          {manifest.files.map((file) => (
            <li key={file.path}>
              {file.path} · {file.role} · {file.size} 字节 · SHA-256 {file.sha256}
            </li>
          ))}
        </ul>
      </details>
    </section>
  )
}

function ReportPreview({ value }: { value: HtmlReportPrepareResultDTO }) {
  const { report, credentialScan } = value
  const notes = [
    ['项目目标', report.goals],
    ['能力问题', report.competencyQuestions],
    ['本体概况', report.ontologySummary],
    ['数据概况', report.dataSummary],
    ['主要假设', report.assumptions],
    ['待解决事项', report.unresolved],
  ] as const
  const results = [
    ['查询结果', report.queryResults],
    ['验证结果', report.validationResults],
    ['行为结果', report.behaviorResults],
    ['场景对比', report.scenarioComparisons],
  ] as const
  return (
    <section aria-label="HTML 报告纯文本预览">
      <h3>{report.title}</h3>
      <p>
        项目版本 {report.projectRevision} · {report.generatedAt} · {report.projectionVersion}
      </p>
      <p>
        凭据扫描{' '}
        {credentialScan.status === 'clear' ? '通过（clear）' : '遮蔽并复检通过（redacted）'}
      </p>
      {notes.map(([title, entries]) => (
        <details key={title} open>
          <summary>{title}</summary>
          {entries.length ? (
            <ul>
              {entries.map((entry, index) => (
                <li key={index}>{entry}</li>
              ))}
            </ul>
          ) : (
            <p>无记录</p>
          )}
        </details>
      ))}
      <details open>
        <summary>学习尝试</summary>
        {report.learning.length ? (
          <ul>
            {report.learning.map((attempt) => (
              <li key={JSON.stringify([attempt.taskId, attempt.attemptId])}>
                {attempt.taskId} / {attempt.attemptId} · 操作
                {attempt.operationCompleted ? '已完成' : '未完成'} · 提示 {attempt.hint} · Agent
                协助 {attempt.agentAssistance}
                {' · '}
                {attempt.independentTransferSuccess ? '独立迁移通过' : '无独立迁移通过证据'} · 检查{' '}
                {attempt.check.status} · {attempt.check.summary}
                {attempt.stageOutcomes.length > 0 && <p>{attempt.stageOutcomes.join('；')}</p>}
              </li>
            ))}
          </ul>
        ) : (
          <p>无记录</p>
        )}
      </details>
      {results.map(([title, entries]) => (
        <details key={title} open>
          <summary>{title}</summary>
          {entries.length ? (
            <ul>
              {entries.map((entry) => (
                <li key={entry.resultId}>
                  {entry.resultId} · 版本 {entry.inputRevision} / {entry.semanticsVersion} ·{' '}
                  {entry.scope} · {entry.status} · {entry.statusNote} · {entry.summary}
                </li>
              ))}
            </ul>
          ) : (
            <p>无记录</p>
          )}
        </details>
      ))}
    </section>
  )
}

export function TransferWorkspace({
  bridge,
  projectId,
  revision,
  disabled,
  onStatus,
  onImported,
}: {
  bridge: TransferBridge
  projectId: string
  revision: number
  disabled: boolean
  onStatus: ReportWorkspaceStatus
  onImported: () => Promise<void>
}) {
  const [kind, setKind] = useState<ProjectPackageKind>('full')
  const [options, setOptions] = useState(defaultProjectPackageOptions)
  const [expectedKind, setExpectedKind] = useState<ProjectPackageKind>('full')
  const [exportCheck, setExportCheck] = useState<PackageExportCheckResultDTO>()
  const [importCheck, setImportCheck] = useState<PackageImportCheckResultDTO>()
  const [prepared, setPrepared] = useState<HtmlReportPrepareResultDTO>()
  const [imported, setImported] = useState('')
  const [publication, setPublication] = useState<TransferPublicationReceiptDTO>()
  const [unknown, setUnknown] = useState(false)
  const [reconciled, setReconciled] = useState(false)
  const [cancelled, setCancelled] = useState(false)
  const mustReconcile =
    unknown || (publication !== undefined && publicationNeedsReconciliation(publication))
  const { busy, error, perform } = useWorkspaceOperation(
    onStatus,
    false,
    mustReconcile && !reconciled,
  )

  async function pick(purpose: TransferPickerPurpose, current: () => void) {
    setCancelled(false)
    const reply = await bridge.selectTransferFile({ purpose })
    current()
    if (!reply.ok && ['CANCELLED', 'PERMISSION_DENIED'].includes(reply.error.code)) {
      setCancelled(true)
      return
    }
    const value = requireWorkspaceReply(reply)
    if (
      value.projectId !== projectId ||
      value.purpose !== purpose ||
      !validateBusiness3('w4.transfer.pickerResult', value)
    )
      throw new Error('INVALID_SELECTION')
    return value.selectionId
  }
  function checkExport() {
    void perform(async (current) => {
      setExportCheck(undefined)
      const selectionId = await pick('package-export', current)
      current()
      if (!selectionId) return
      const value = requireWorkspaceReply(
        await bridge.checkProjectPackageExport({
          baseRevision: revision,
          kind,
          options,
          selectionId,
        }),
      )
      current()
      if (
        !validateBusiness3('result_project.transfer.package.export.check', value) ||
        value.projectId !== projectId ||
        value.selectionId !== selectionId ||
        value.kind !== kind ||
        value.baseRevision !== revision ||
        Object.keys(options).some(
          (key) =>
            value.options[key as keyof ProjectPackageOptions] !==
            options[key as keyof ProjectPackageOptions],
        )
      )
        throw new Error('EXPORT_CHECK_INVALID')
      setExportCheck(maskLocalPaths(value))
    })
  }
  function checkImport() {
    void perform(async (current) => {
      setImported('')
      setImportCheck(undefined)
      const selectionId = await pick('package-import', current)
      current()
      if (!selectionId) return
      const value = requireWorkspaceReply(
        await bridge.checkProjectPackageImport({ selectionId, expectedKind }),
      )
      current()
      if (
        !validateBusiness3('result_project.transfer.package.import.check', value) ||
        value.projectId !== projectId ||
        value.selectionId !== selectionId ||
        value.expectedKind !== expectedKind
      )
        throw new Error('IMPORT_CHECK_INVALID')
      setImportCheck(maskLocalPaths(value))
    })
  }
  function startPublication() {
    setReconciled(false)
    setPublication(undefined)
    setUnknown(true)
  }
  function publishPackage() {
    if (!exportCheck || (mustReconcile && !reconciled)) return
    void perform(async (current) => {
      const { selectionId, checkRef } = exportCheck
      setExportCheck(undefined)
      const operationId = crypto.randomUUID()
      startPublication()
      const value = requireWorkspaceReply(
        await bridge.exportProjectPackage({ selectionId, checkRef, operationId }),
      )
      current()
      if (
        !validateBusiness3('result_project.transfer.package.export', value) ||
        value.projectId !== projectId ||
        value.selectionId !== selectionId ||
        value.checkRef !== checkRef ||
        value.operationId !== operationId ||
        value.kind !== exportCheck.kind
      )
        throw new Error('WRONG_PUBLICATION')
      setPublication(value.publication)
      setUnknown(false)
    })
  }
  function importPackage() {
    if (importCheck?.status !== 'compatible') return
    void perform(async (current) => {
      const { selectionId, checkRef, packageSha256 } = importCheck
      const operationId = crypto.randomUUID()
      setImportCheck(undefined)
      startPublication()
      const value = requireWorkspaceReply(
        await bridge.importProjectPackage({
          selectionId,
          checkRef,
          packageSha256,
          expectedKind,
          operationId,
        }),
      )
      current()
      if (
        !validateBusiness3('result_project.transfer.package.import', value) ||
        value.projectId !== projectId ||
        value.selectionId !== selectionId ||
        value.checkRef !== checkRef ||
        value.packageSha256 !== packageSha256 ||
        value.kind !== expectedKind ||
        value.operationId !== operationId ||
        value.importedProjectId === projectId
      )
        throw new Error('INVALID_IMPORT')
      setImported(value.importedProjectId)
      setUnknown(false)
      await onImported()
    })
  }
  function prepareReport() {
    void perform(async (current) => {
      setPrepared(undefined)
      const reply = requireWorkspaceReply(
        await bridge.prepareProjectHtmlReport({ baseRevision: revision }),
      )
      current()
      if (
        !validateBusiness3('result_project.transfer.report.prepare', reply) ||
        reply.projectId !== projectId ||
        reply.report.projectId !== projectId ||
        reply.baseRevision !== revision ||
        reply.report.projectRevision !== revision
      )
        throw new Error('INVALID_REPORT')
      setPrepared(maskLocalPaths(reply))
    })
  }
  function exportReport() {
    if (!prepared || (mustReconcile && !reconciled)) return
    void perform(async (current) => {
      const selectionId = await pick('report-html', current)
      current()
      if (!selectionId) return
      const { reportRef } = prepared
      const operationId = crypto.randomUUID()
      setPrepared(undefined)
      startPublication()
      const value = requireWorkspaceReply(
        await bridge.exportProjectHtmlReport({
          selectionId,
          reportRef,
          baseRevision: revision,
          operationId,
        }),
      )
      current()
      if (
        !validateBusiness3('result_project.transfer.report.export', value) ||
        value.projectId !== projectId ||
        value.selectionId !== selectionId ||
        value.reportRef !== reportRef ||
        value.operationId !== operationId ||
        value.baseRevision !== revision
      )
        throw new Error('WRONG_PUBLICATION')
      setPublication(value.publication)
      setUnknown(false)
    })
  }
  const locked = disabled || busy || (mustReconcile && !reconciled)
  return (
    <TransferPanel
      connected={
        <>
          <fieldset disabled={locked}>
            <legend>导出项目包</legend>
            <label>
              包类型{' '}
              <select
                value={kind}
                onChange={(e) => {
                  setKind(e.target.value as ProjectPackageKind)
                  setExportCheck(undefined)
                }}
              >
                <option value="full">完整项目包</option>
                <option value="template">模板包</option>
              </select>
            </label>
            {(Object.keys(optionLabels) as (keyof ProjectPackageOptions)[]).map((key) => (
              <label key={key}>
                <input
                  type="checkbox"
                  checked={options[key]}
                  onChange={(e) => {
                    setOptions({ ...options, [key]: e.target.checked })
                    setExportCheck(undefined)
                  }}
                />
                {optionLabels[key]}
              </label>
            ))}
            <p>项目包排除凭据、私有审计及发送授权。</p>
            <button type="button" onClick={checkExport}>
              选择目标并检查项目包
            </button>
            {exportCheck && (
              <>
                <PackageCheck value={exportCheck} />
                <button type="button" onClick={publishPackage}>
                  确认导出项目包
                </button>
              </>
            )}
          </fieldset>
          <fieldset disabled={locked}>
            <legend>导入项目包</legend>
            <label>
              预期包类型{' '}
              <select
                value={expectedKind}
                onChange={(e) => {
                  setExpectedKind(e.target.value as ProjectPackageKind)
                  setImportCheck(undefined)
                }}
              >
                <option value="full">完整项目包</option>
                <option value="template">模板包</option>
              </select>
            </label>
            <button type="button" onClick={checkImport}>
              选择并检查待导入项目包
            </button>
            {importCheck?.status === 'rejected' && (
              <p role="alert">
                {rejectionLabels[importCheck.reason]}（{importCheck.reason}）
              </p>
            )}
            {importCheck?.status === 'compatible' && (
              <>
                <PackageCheck value={importCheck} />
                <button type="button" onClick={importPackage}>
                  确认导入为新项目
                </button>
              </>
            )}
            {imported && <p role="status">已导入新项目 {imported}</p>}
          </fieldset>
          <fieldset disabled={locked}>
            <legend>HTML 报告</legend>
            <button type="button" onClick={prepareReport}>
              准备并预览 HTML 报告
            </button>
            {prepared && (
              <>
                <ReportPreview value={prepared} />
                <button type="button" onClick={exportReport}>
                  选择目标并导出 HTML 报告
                </button>
              </>
            )}
          </fieldset>
          {cancelled && <p role="status">未完成文件选择。</p>}
          {publication && <PublicationReceipt value={publication} />}
          {error && <p role="alert">迁移操作未完成，请查看检查结果与文件回执。</p>}
          {mustReconcile && !reconciled && !busy && (
            <div role="alert">
              <p>
                结果待核对。请先检查目标文件或项目列表，并确认不需要恢复操作，再重新检查或发起写入。
              </p>
              <button type="button" disabled={disabled} onClick={() => setReconciled(true)}>
                已人工核对，解除写入锁定
              </button>
            </div>
          )}
        </>
      }
    />
  )
}
