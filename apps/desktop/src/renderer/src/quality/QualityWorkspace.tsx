import { useEffect, useId, useRef, useState } from 'react'
import type {
  MainlineChangePlanDTO,
  MainlineProjectReadDTO,
  DesktopBridge,
  ProjectQualityReadDTO,
  QualityFindingDTO,
  QualityFr505PatternDTO,
} from '@ontolearn/contracts'
import { validateBusiness3 } from '../../../../../../packages/contracts/src/v2'
import {
  commitWorkspaceChange,
  prepareWorkspaceChange,
  requireWorkspaceReply,
  type WorkspaceChangePreview,
} from '../ontology/workspace-change'
import { compareStatements, type Statement } from './presentation'
import { prepareEditorDraft, type Pattern, type Template } from './draft'
import './quality.css'

const templateNames: Record<Template, string> = {
  required: '必填',
  datatype: '数据类型',
  maxCount: '最大数量',
  allowedValues: '允许值',
  numericRange: '数值范围（含边界）',
}
const blank = (): Pattern => ({ kind: 'type', subject: '?entity', path: '', value: '' })
const operators = { eq: '==', ne: '!=', lt: '<', le: '<=', gt: '>', ge: '>=' }

function StatementTable({ title, rows }: { title: string; rows: readonly Statement[] }) {
  return (
    <section className="quality-statements">
      <h4>{title}</h4>
      {rows.length === 0 ? (
        <p>空集合</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>主体</th>
              <th>属性</th>
              <th>值</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={index}>
                {row.map((cell, index) => (
                  <td key={index}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}

function PatternEditor({
  title,
  rows,
  onChange,
  conclusions = false,
}: {
  title: string
  rows: Pattern[]
  onChange: (rows: Pattern[]) => void
  conclusions?: boolean
}) {
  const uid = useId()
  return (
    <fieldset>
      <legend>{title}</legend>
      {rows.map((row, index) => {
        const prefix = `${uid}-${index}`
        const update = (patch: Partial<Pattern>) =>
          onChange(rows.map((item, i) => (i === index ? { ...item, ...patch } : item)))
        return (
          <div className="quality-pattern" key={index}>
            <label htmlFor={`${prefix}-kind`}>第 {index + 1} 项类型</label>
            <select
              id={`${prefix}-kind`}
              value={row.kind}
              onChange={(event) =>
                update({ kind: event.target.value as Pattern['kind'], path: '', value: '' })
              }
            >
              <option value="type">类型判断/类成员</option>
              <option value="property">属性存在/受控属性</option>
              {!conclusions && <option value="compare">属性值比较</option>}
            </select>
            <label htmlFor={`${prefix}-subject`}>
              {row.kind === 'compare' ? '比较左值' : '主体变量或 IRI'}
            </label>
            <input
              id={`${prefix}-subject`}
              value={row.subject}
              onChange={(event) => update({ subject: event.target.value })}
              required
            />
            {row.kind !== 'type' && (
              <>
                <label htmlFor={`${prefix}-path`}>
                  {row.kind === 'compare' ? '运算符' : '属性 IRI'}
                </label>
                {row.kind === 'compare' ? (
                  <select
                    id={`${prefix}-path`}
                    value={row.path}
                    onChange={(event) => update({ path: event.target.value })}
                    required
                  >
                    <option value="">选择比较</option>
                    {Object.entries(operators).map(([op, symbol]) => (
                      <option key={op} value={op}>
                        {symbol}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    id={`${prefix}-path`}
                    value={row.path}
                    onChange={(event) => update({ path: event.target.value })}
                    required
                  />
                )}
              </>
            )}
            <label htmlFor={`${prefix}-value`}>
              {row.kind === 'type' ? '类 IRI' : '右值 / RDF 项 / 变量'}
            </label>
            <input
              id={`${prefix}-value`}
              value={row.value}
              onChange={(event) => update({ value: event.target.value })}
              required
            />
            <button
              type="button"
              onClick={() => onChange(rows.filter((_, i) => i !== index))}
              disabled={rows.length === 1}
            >
              删除第 {index + 1} 项
            </button>
          </div>
        )
      })}
      <button
        type="button"
        disabled={rows.length >= 32}
        onClick={() => onChange([...rows, blank()])}
      >
        添加{conclusions ? '结论' : '条件'}
      </button>
    </fieldset>
  )
}

type Definition = NonNullable<MainlineChangePlanDTO['definitions']>[number]
type EditorInput = Parameters<typeof prepareEditorDraft>[0]
type Snapshot = { projectId: string; snapshotId: string; revision: number }
type Scope = 'asserted' | 'asserted+derived'
type WorkspaceProps = {
  projectId: string
  bridge: DesktopBridge
  disabled?: boolean
  onDomainSnapshotUpdated: (snapshot: Snapshot) => void
  onLocateTarget: (targets: QualityFindingDTO['targets'], finding: QualityFindingDTO) => void
  onPendingChange?: (pending: boolean) => void
}
type ProjectQuality = { source: MainlineProjectReadDTO; state: ProjectQualityReadDTO }
type ViewLifetime = { active: boolean }
const tierNames = { violation: '违规', warning: '建议改进', info: '提示' }
const stateNames = { current: '当前', stale: '已过期', historical: '历史' }
const emptyForm = (kind: EditorInput['kind']): EditorInput => ({
  kind,
  identity: '',
  label: '',
  revision: '1',
  enabled: true,
  targetClass: '',
  path: '',
  template: 'required',
  parameter: '',
  upper: '',
  conditions: [blank()],
  conclusions: [blank()],
})
function fromPattern(pattern: QualityFr505PatternDTO): Pattern {
  switch (pattern.kind) {
    case 'type':
      return { kind: 'type', subject: pattern.subject, path: '', value: pattern.class }
    case 'property':
      return {
        kind: 'property',
        subject: pattern.subject,
        path: pattern.path,
        value: pattern.object,
      }
    case 'compare':
      return {
        kind: 'compare',
        subject: pattern.left,
        path: pattern.operator,
        value: pattern.right,
      }
  }
}

function editorRevision(source: MainlineProjectReadDTO, kind: EditorInput['kind'], id: string) {
  const current = source.domain.state.definitions.find((row) => row.layer === kind && row.id === id)
  if (!current) return '1'
  const { revision } = JSON.parse(current.payload)
  return String(Number.isSafeInteger(revision) ? revision + 1 : 1)
}

function loadForm(quality: ProjectQuality, kind: EditorInput['kind'], id: string): EditorInput {
  const form = emptyForm(kind)
  const revision = editorRevision(quality.source, kind, id)
  if (kind === 'rule') {
    const rule = quality.state.rules.find((item) => item.id === id)
    if (rule?.format === 'fr505')
      return {
        ...form,
        identity: id,
        label: rule.label ?? '',
        enabled: rule.enabled,
        revision,
        conditions: rule.conditions.map(fromPattern),
        conclusions: rule.conclusions.map(fromPattern),
      }
    if (rule) return { ...form, identity: id, enabled: rule.enabled }
  } else {
    const constraint = quality.state.constraints.find((item) => item.id === id)
    if (constraint?.format === 'fr504') {
      const template = Object.keys(templateNames).includes(constraint.template ?? '')
        ? (constraint.template as Template)
        : 'required'
      const p = constraint.parameters
      const parameter =
        template === 'allowedValues' && Array.isArray(p.values)
          ? p.values.join('\n')
          : String(p.datatype ?? p.maxCount ?? p.minInclusive ?? '')
      return {
        ...form,
        identity: id,
        label: constraint.label ?? '',
        enabled: constraint.enabled,
        revision,
        template,
        parameter,
        upper: String(p.maxInclusive ?? ''),
        targetClass: constraint.targetClass ?? '',
        path: constraint.path ?? '',
      }
    }
    if (constraint) return { ...form, identity: id, enabled: constraint.enabled }
  }
  return form
}

function QualityResults({
  state,
  previous,
  disabled,
  onLocate,
}: {
  state: ProjectQualityReadDTO
  previous: ProjectQualityReadDTO['reasoning']
  disabled: boolean
  onLocate: WorkspaceProps['onLocateTarget']
}) {
  const { reasoning, validation } = state
  const derivation = reasoning?.derivation
  const stale = [reasoning, validation].filter((result) => result?.state === 'stale')
  const previousRows = previous?.derivation
  const comparison =
    derivation && previousRows
      ? compareStatements(
          [...previousRows.rules, ...previousRows.rdfs],
          [...derivation.rules, ...derivation.rdfs],
        )
      : null
  return (
    <section aria-label="检查结果">
      <p data-testid="quality-reasoning-state" data-state={reasoning?.state}>
        推导 · {reasoning ? stateNames[reasoning.state] : '未运行'}
        {reasoning && <> · 快照 {reasoning.inputSnapshotId.slice(0, 12)}</>}
      </p>
      <p
        data-testid="quality-validation-state"
        data-state={validation?.state}
        data-conforms={validation?.conforms ?? undefined}
      >
        SHACL 验证 · {validation ? stateNames[validation.state] : '未运行'}
        {validation?.conforms === true && ' · 符合约束'}
        {validation?.conforms === false && ' · 存在不符合项'}
        {validation && <> · 快照 {validation.inputSnapshotId.slice(0, 12)}</>}
      </p>
      {stale.length > 0 && (
        <aside data-testid="quality-stale-reasons" role="status">
          <strong>上游数据或定义已变化，检查结果已过期。</strong>
          <ul>
            {stale
              .flatMap((result) => result?.staleReasons ?? [])
              .map((reason, index) => (
                <li key={index}>
                  {reason.code} · {reason.dependency}（{reason.before} → {reason.after}）
                </li>
              ))}
          </ul>
        </aside>
      )}
      <p>开放世界下，缺少事实表示尚未记录。SHACL 在所选范围内检查已记录的数据，例如必填字段。</p>
      {validation && (
        <div data-testid="quality-findings">
          {Object.entries(tierNames).map(([tier, name]) => {
            const findings = validation.findings.filter((finding) => finding.tier === tier)
            return (
              <section key={tier} aria-label={name}>
                <h3>
                  {name}（{findings.length}）
                </h3>
                <ul>
                  {findings.map((finding, index) => (
                    <li key={index}>
                      {[
                        finding.focusNode,
                        finding.path,
                        finding.constraint,
                        finding.sourceShape,
                        finding.value,
                      ]
                        .filter((value) => value !== null)
                        .join(' · ')}{' '}
                      <button
                        type="button"
                        disabled={disabled}
                        onClick={() => onLocate(finding.targets, finding)}
                      >
                        定位
                      </button>
                    </li>
                  ))}
                </ul>
              </section>
            )
          })}
        </div>
      )}
      {derivation && (
        <>
          <StatementTable title="规则推导" rows={derivation.rules} />
          <StatementTable title="RDFS 推导" rows={derivation.rdfs} />
          {derivation.warnings.length > 0 && (
            <ul aria-label="推导提示">
              {derivation.warnings.map((warning, index) => (
                <li key={index}>
                  {warning.includes('RULE_CHAIN_UNSUPPORTED')
                    ? `不支持规则链。规则输出不会进入后续规则或 RDFS 的输入。 ${warning}`
                    : warning}
                </li>
              ))}
            </ul>
          )}
          <details open data-testid="quality-rule-traces">
            <summary>规则推导依据（{derivation.ruleTraces.length}）</summary>
            {derivation.ruleTraces.map((trace, index) => (
              <article key={index}>
                <h4>{trace.rule ?? '规则'}</h4>
                <StatementTable title="输入事实" rows={trace.inputs} />
                {trace.output && <StatementTable title="推导结论" rows={[trace.output]} />}
              </article>
            ))}
          </details>
          <details>
            <summary>RDFS 推导依据（{derivation.rdfsTraces.length}）</summary>
            {derivation.rdfsTraces.map((trace, index) => (
              <article key={index}>
                <StatementTable title="依据" rows={trace.basis} />
                <StatementTable title="推导结论" rows={[trace.output]} />
              </article>
            ))}
          </details>
          {comparison && (
            <details>
              <summary>与上次推导比较</summary>
              <StatementTable title="新增" rows={comparison.unexpected} />
              <StatementTable title="撤回" rows={comparison.missing} />
            </details>
          )}
        </>
      )}
    </section>
  )
}

export function QualityWorkspace({
  projectId,
  bridge,
  disabled,
  onDomainSnapshotUpdated,
  onLocateTarget,
  onPendingChange,
}: WorkspaceProps) {
  const uid = useId()
  const field = (name: string) => `${uid}-${name}`
  const [quality, setQuality] = useState<ProjectQuality>()
  const [form, setForm] = useState(() => emptyForm('constraint'))
  const [selected, setSelected] = useState('')
  const [scope, setScope] = useState<Scope>('asserted+derived')
  const [proposal, setProposal] = useState<{ diff: WorkspaceChangePreview; operationId: string }>()
  const [previous, setPrevious] = useState<ProjectQualityReadDTO['reasoning']>(null)
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const [error, setError] = useState('')
  const lifetime = useRef<ViewLifetime>({ active: false })
  const busyRef = useRef(false)

  function update(patch: Partial<EditorInput>) {
    setForm((value) => ({ ...value, ...patch }))
  }
  function requireCurrent(captured: ViewLifetime) {
    if (!captured.active) throw new Error('PERMISSION_DENIED')
  }
  async function readDomain(captured: ViewLifetime) {
    const source = requireWorkspaceReply(await bridge.readProject({ editor: 'quality' }))
    requireCurrent(captured)
    if (source.projectId !== projectId) throw new Error('PERMISSION_DENIED')
    onDomainSnapshotUpdated({
      projectId,
      snapshotId: source.inputSnapshotId,
      revision: source.domain.projectRevision,
    })
    return source
  }
  async function readQuality(captured: ViewLifetime) {
    const state = requireWorkspaceReply(await bridge.getProjectQualityState({ projectId }))
    requireCurrent(captured)
    if (state.projectId !== projectId) throw new Error('PERMISSION_DENIED')
    const source = await readDomain(captured)
    setQuality({ state, source })
  }
  async function perform(work: (captured: ViewLifetime) => Promise<void>) {
    const captured = lifetime.current
    if (busyRef.current || !captured.active) return
    busyRef.current = true
    setBusy(true)
    setNotice('')
    setError('')
    onPendingChange?.(true)
    try {
      await work(captured)
    } catch (cause) {
      if (captured.active) setError(cause instanceof Error ? cause.message : '操作未完成。')
    } finally {
      if (captured.active) {
        busyRef.current = false
        setBusy(false)
        onPendingChange?.(false)
      }
    }
  }
  useEffect(() => {
    if (disabled) return
    const owner = { active: true }
    lifetime.current = owner
    // Start after the StrictMode setup/cleanup cycle so only the live mount reads.
    queueMicrotask(() => {
      if (owner.active) void perform(readQuality)
    })
    return () => {
      owner.active = false
      busyRef.current = false
      onPendingChange?.(false)
    }
    // The parent keys this workspace by the admitted project and view generation.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId, bridge, disabled])

  function loadDefinition(id: string) {
    if (!quality) return
    setSelected(id)
    setForm(loadForm(quality, form.kind, id))
  }

  function prepare(plan: MainlineChangePlanDTO) {
    const source = quality?.source
    if (!source) return
    void perform(async (captured) => {
      const diff = await prepareWorkspaceChange(bridge, source, plan, () =>
        requireCurrent(captured),
      )
      requireCurrent(captured)
      setProposal({ diff, operationId: crypto.randomUUID() })
    })
  }

  function save(enabled = form.enabled) {
    if (!quality) return
    const renamed = selected !== '' && selected !== form.identity
    const idExists = quality.source.domain.state.definitions.some(
      (row) => row.id === form.identity && row.layer === form.kind,
    )
    if (selected !== form.identity && idExists) {
      setError('该标识已存在。请从现有定义中选择后再编辑。')
      return
    }
    const prepared = prepareEditorDraft({
      ...form,
      enabled,
      revision: editorRevision(quality.source, form.kind, form.identity),
    })
    if (prepared.error) {
      setError(prepared.error)
      return
    }
    const definition = {
      layer: form.kind,
      id: form.identity,
      value: JSON.parse(prepared.draft),
    } as Definition
    if (
      !validateBusiness3(
        form.kind === 'rule' ? 'changeSetRuleDefinition' : 'changeSetConstraintDefinition',
        definition,
      )
    ) {
      setError('定义内容不符合模板。请检查字段类型、范围和必填项。')
      return
    }
    prepare({
      definitions: [definition],
      ...(renamed ? { remove_definitions: [{ layer: form.kind, id: selected }] } : {}),
    })
  }

  function commit() {
    if (!proposal) return
    void perform(async (captured) => {
      const job = await commitWorkspaceChange(bridge, proposal.diff, proposal.operationId, () =>
        requireCurrent(captured),
      )
      requireCurrent(captured)
      setProposal(undefined)
      if (job.state !== 'succeeded') throw new Error(job.error?.code ?? job.state)
      setSelected('')
      setForm(emptyForm(form.kind))
      await readQuality(captured)
      setNotice('定义已提交。')
    })
  }

  function runCheck() {
    void perform(async (captured) => {
      const receipt = requireWorkspaceReply(
        await bridge.runProjectQualityCheck({
          projectId,
          operationId: crypto.randomUUID(),
          selection: { kind: 'current' },
          validationScope: scope,
        }),
      )
      requireCurrent(captured)
      if (receipt.projectId !== projectId || receipt.qualityState.projectId !== projectId)
        throw new Error('PERMISSION_DENIED')
      const source = await readDomain(captured)
      if (quality?.state.reasoning?.resultId !== receipt.qualityState.reasoning?.resultId)
        setPrevious(quality?.state.reasoning ?? null)
      setQuality({ source, state: receipt.qualityState })
      const failure = [receipt.reasoningJob, ...receipt.validationJobs].find(
        (job) => job.state !== 'succeeded',
      )
      if (failure) throw new Error(failure.error?.code ?? failure.state)
      setNotice(
        receipt.validationJobs.length ? '检查已完成。' : '推导已完成。当前没有启用的验证约束。',
      )
    })
  }

  const definitions = form.kind === 'rule' ? quality?.state.rules : quality?.state.constraints
  const original = definitions?.find((item) => item.id === selected)
  const readOnly = original?.format === 'legacy' || original?.format === 'turtle'
  const blocked = disabled || busy || Boolean(proposal) || !quality
  return (
    <div className="quality-workspace">
      <h2>质量与推导</h2>
      {error && <p role="alert">{error}</p>}
      {notice && <p role="status">{notice}</p>}
      {busy && <p role="status">正在读取或处理项目质量数据…</p>}
      <div className="quality-run">
        <label htmlFor={field('scope')}>验证范围</label>
        <select
          id={field('scope')}
          value={scope}
          disabled={blocked}
          onChange={(event) => setScope(event.target.value as Scope)}
        >
          <option value="asserted+derived">断言事实＋推导结论</option>
          <option value="asserted">仅当前断言事实</option>
        </select>
        <button
          type="button"
          data-testid="quality-btn-run-check"
          disabled={blocked}
          onClick={runCheck}
        >
          检查我的项目
        </button>
        <button
          type="button"
          disabled={disabled || busy || Boolean(proposal)}
          onClick={() => void perform(readQuality)}
        >
          刷新质量状态
        </button>
      </div>
      {quality && (
        <QualityResults
          state={quality.state}
          previous={previous}
          disabled={blocked}
          onLocate={onLocateTarget}
        />
      )}
      <details open>
        <summary>约束与规则</summary>
        <form
          onSubmit={(event) => {
            event.preventDefault()
            save()
          }}
        >
          <fieldset disabled={blocked}>
            <legend>定义编辑</legend>
            <label htmlFor={field('kind')}>定义类型</label>
            <select
              id={field('kind')}
              value={form.kind}
              onChange={(event) => {
                setSelected('')
                setForm(emptyForm(event.target.value as EditorInput['kind']))
              }}
            >
              <option value="constraint">SHACL 约束</option>
              <option value="rule">受控规则</option>
            </select>
            <label htmlFor={field('selected')}>现有定义</label>
            <select
              id={field('selected')}
              value={selected}
              onChange={(event) => loadDefinition(event.target.value)}
            >
              <option value="">新建定义</option>
              {definitions?.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.id} · {item.enabled ? '已启用' : '已停用'}
                </option>
              ))}
            </select>
            {readOnly ? (
              <>
                <p>
                  导入的 {original.format === 'turtle' ? 'Turtle 约束' : '旧版规则'}可查看和移除。
                </p>
                <pre>{JSON.stringify(original, null, 2)}</pre>
              </>
            ) : (
              <>
                <label htmlFor={field('id')}>稳定标识</label>
                <input
                  id={field('id')}
                  value={form.identity}
                  onChange={(event) => update({ identity: event.target.value })}
                  required
                  maxLength={128}
                />
                <label htmlFor={field('label')}>名称</label>
                <input
                  id={field('label')}
                  value={form.label}
                  onChange={(event) => update({ label: event.target.value })}
                  required
                  maxLength={4096}
                />
                <label className="quality-check">
                  <input
                    type="checkbox"
                    checked={form.enabled}
                    onChange={(event) => update({ enabled: event.target.checked })}
                  />
                  启用
                </label>
                {form.kind === 'constraint' ? (
                  <>
                    <label htmlFor={field('class')}>目标类 IRI</label>
                    <input
                      id={field('class')}
                      value={form.targetClass}
                      onChange={(event) => update({ targetClass: event.target.value })}
                      required
                    />
                    <label htmlFor={field('path')}>直接属性路径 IRI</label>
                    <input
                      id={field('path')}
                      value={form.path}
                      onChange={(event) => update({ path: event.target.value })}
                      required
                    />
                    <label htmlFor={field('template')}>模板</label>
                    <select
                      id={field('template')}
                      value={form.template}
                      onChange={(event) => {
                        update({
                          template: event.target.value as Template,
                          parameter: '',
                          upper: '',
                        })
                      }}
                    >
                      {Object.entries(templateNames).map(([key, name]) => (
                        <option key={key} value={key}>
                          {name}
                        </option>
                      ))}
                    </select>
                    {form.template !== 'required' && (
                      <>
                        <label htmlFor={field('parameter')}>
                          {
                            {
                              datatype: '数据类型 IRI',
                              maxCount: '最大数量',
                              allowedValues: '允许的 RDF 项（每行一项）',
                              numericRange: '最小值（可留空）',
                            }[form.template]
                          }
                        </label>
                        <textarea
                          id={field('parameter')}
                          value={form.parameter}
                          onChange={(event) => update({ parameter: event.target.value })}
                          required={form.template !== 'numericRange'}
                        />
                      </>
                    )}
                    {form.template === 'numericRange' && (
                      <>
                        <label htmlFor={field('upper')}>最大值（可留空）</label>
                        <input
                          id={field('upper')}
                          value={form.upper}
                          onChange={(event) => update({ upper: event.target.value })}
                        />
                      </>
                    )}
                  </>
                ) : (
                  <>
                    <PatternEditor
                      title="全部满足以下条件（合取）"
                      rows={form.conditions}
                      onChange={(conditions) => update({ conditions })}
                    />
                    <PatternEditor
                      title="推导一个或多个新事实"
                      rows={form.conclusions}
                      onChange={(conclusions) => update({ conclusions })}
                      conclusions
                    />
                    <p>规则读取同一份断言与 RDFS 快照。P0 不支持规则链。</p>
                  </>
                )}
                <button type="submit">读取完整差异</button>
                {original && (
                  <button
                    type="button"
                    onClick={() => {
                      if (!quality) return
                      const stored = loadForm(quality, form.kind, selected)
                      const prepared = prepareEditorDraft({ ...stored, enabled: !original.enabled })
                      if (prepared.error) {
                        setError(prepared.error)
                        return
                      }
                      prepare({
                        definitions: [
                          { layer: form.kind, id: selected, value: JSON.parse(prepared.draft) },
                        ],
                      })
                    }}
                  >
                    {original.enabled ? '停用该定义' : '启用该定义'}
                  </button>
                )}
              </>
            )}
            {selected && (
              <button
                type="button"
                onClick={() =>
                  prepare({ remove_definitions: [{ layer: form.kind, id: selected }] })
                }
              >
                删除该定义
              </button>
            )}
          </fieldset>
        </form>
      </details>
      {proposal && (
        <section aria-label="完整差异">
          <h3>完整差异</h3>
          <pre>{JSON.stringify(proposal.diff.rows, null, 2)}</pre>
          <button type="button" disabled={disabled || busy} onClick={commit}>
            确认并提交
          </button>
          <button type="button" disabled={disabled || busy} onClick={() => setProposal(undefined)}>
            放弃差异
          </button>
        </section>
      )}
    </div>
  )
}
