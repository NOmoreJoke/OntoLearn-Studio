import { useId, useState } from 'react'
import {
  checkText,
  compareStatements,
  visibleObservation,
  type QualityObservation,
  type Statement,
} from './presentation'
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
            {rows.map((row) => (
              <tr key={JSON.stringify(row)}>
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
                    {['eq', 'ne', 'lt', 'le', 'gt', 'ge'].map((op) => (
                      <option key={op}>{op}</option>
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
        disabled={rows.length >= 128}
        onClick={() => onChange([...rows, blank()])}
      >
        添加{conclusions ? '结论' : '条件'}
      </button>
    </fieldset>
  )
}

/** Mount with key={projectId} to keep project drafts isolated across workspace switches. */
export function QualityWorkspace(props: {
  projectId: string
  observation?: QualityObservation | null
  onLocate?: (target: QualityObservation['findings'][number]['target']) => void
}) {
  return <QualityEditor key={props.projectId} {...props} />
}

function QualityEditor({
  projectId,
  observation = null,
  onLocate,
}: {
  projectId: string
  observation?: QualityObservation | null
  onLocate?: (target: QualityObservation['findings'][number]['target']) => void
}) {
  const uid = useId()
  const [kind, setKind] = useState<'constraint' | 'rule'>('constraint')
  const [identity, setIdentity] = useState('')
  const [label, setLabel] = useState('')
  const [revision, setRevision] = useState('1')
  const [enabled, setEnabled] = useState(true)
  const [targetClass, setTargetClass] = useState('')
  const [path, setPath] = useState('')
  const [template, setTemplate] = useState<Template>('required')
  const [parameter, setParameter] = useState('')
  const [upper, setUpper] = useState('')
  const [conditions, setConditions] = useState<Pattern[]>([blank()])
  const [conclusions, setConclusions] = useState<Pattern[]>([blank()])
  const [draft, setDraft] = useState('')
  const [error, setError] = useState('')
  const [sample, setSample] = useState('')
  const [expected, setExpected] = useState('[]')
  const [scope, setScope] = useState('asserted')
  const view = visibleObservation(observation, projectId)
  const comparison = view?.actual == null ? null : compareStatements(view.expected, view.actual)
  const field = (name: string) => `${uid}-${name}`
  function prepare() {
    const result = prepareEditorDraft({
      kind,
      identity,
      label,
      revision,
      enabled,
      targetClass,
      path,
      template,
      parameter,
      upper,
      conditions,
      conclusions,
    })
    setError(result.error)
    if (result.draft) setDraft(result.draft)
  }
  return (
    <section className="quality-workspace" aria-label="质量与推理">
      <header>
        <p>检查并发现新知识</p>
        <h2>质量与推理</h2>
      </header>
      <aside role="status">
        正式执行器与项目接线尚未接入。此页可编辑待校验草稿；尚未保存、检查或运行推理。
      </aside>
      <button type="button" disabled title="等待批准执行器与公共接线">
        检查我的项目（未执行）
      </button>
      <details open>
        <summary>创建或编辑约束与规则</summary>
        <form
          onSubmit={(event) => {
            event.preventDefault()
            prepare()
          }}
        >
          <label htmlFor={field('kind')}>定义类型</label>
          <select
            id={field('kind')}
            value={kind}
            onChange={(event) => setKind(event.target.value as typeof kind)}
          >
            <option value="constraint">SHACL 约束</option>
            <option value="rule">受控规则</option>
          </select>
          <label htmlFor={field('id')}>稳定标识</label>
          <input
            id={field('id')}
            value={identity}
            onChange={(event) => setIdentity(event.target.value)}
            required
            maxLength={4096}
          />
          <label htmlFor={field('label')}>名称</label>
          <input
            id={field('label')}
            value={label}
            onChange={(event) => setLabel(event.target.value)}
            required
            maxLength={4096}
          />
          <label htmlFor={field('revision')}>草稿版本</label>
          <input
            id={field('revision')}
            value={revision}
            onChange={(event) => setRevision(event.target.value)}
            inputMode="numeric"
            required
          />
          <label className="quality-check">
            <input
              type="checkbox"
              checked={enabled}
              onChange={(event) => setEnabled(event.target.checked)}
            />
            启用（待正式保存）
          </label>
          {kind === 'constraint' ? (
            <fieldset>
              <legend>约束模板</legend>
              <label htmlFor={field('class')}>目标类 IRI</label>
              <input
                id={field('class')}
                value={targetClass}
                onChange={(event) => setTargetClass(event.target.value)}
                required
              />
              <label htmlFor={field('path')}>直接属性路径 IRI</label>
              <input
                id={field('path')}
                value={path}
                onChange={(event) => setPath(event.target.value)}
                required
              />
              <label htmlFor={field('template')}>模板</label>
              <select
                id={field('template')}
                value={template}
                onChange={(event) => {
                  setTemplate(event.target.value as Template)
                  setParameter('')
                  setUpper('')
                }}
              >
                {Object.entries(templateNames).map(([key, name]) => (
                  <option key={key} value={key}>
                    {name}
                  </option>
                ))}
              </select>
              {template !== 'required' && (
                <>
                  <label htmlFor={field('parameter')}>
                    {template === 'allowedValues'
                      ? '允许的 RDF 项（每行一项）'
                      : template === 'numericRange'
                        ? '最小值（可留空）'
                        : template === 'datatype'
                          ? '数据类型 IRI'
                          : '最大数量'}
                  </label>
                  <textarea
                    id={field('parameter')}
                    value={parameter}
                    onChange={(event) => setParameter(event.target.value)}
                    required={template !== 'numericRange'}
                  />
                </>
              )}
              {template === 'numericRange' && (
                <>
                  <label htmlFor={field('upper')}>最大值（可留空）</label>
                  <input
                    id={field('upper')}
                    value={upper}
                    onChange={(event) => setUpper(event.target.value)}
                  />
                </>
              )}
              <p>不支持任意 SPARQL 约束、逆向路径或完整 SHACL 语法。</p>
            </fieldset>
          ) : (
            <>
              <PatternEditor
                title="全部满足以下条件（合取）"
                rows={conditions}
                onChange={setConditions}
              />
              <PatternEditor
                title="推导一个或多个新事实"
                rows={conclusions}
                onChange={setConclusions}
                conclusions
              />
              <p>
                先计算 RDFS；所有规则读取同一断言与 RDFS
                快照。当前版本不支持规则链，不会将规则输出再次交给规则或
                RDFS。场景动作请在行为模块定义。
              </p>
            </>
          )}
          <button type="submit">生成待校验草稿</button>
          {error && <p role="alert">{error}</p>}
        </form>
        {draft && (
          <section>
            <h3>待校验草稿（未保存）</h3>
            <pre>{draft}</pre>
          </section>
        )}
      </details>
      <details>
        <summary>准备输入样本与预期输出</summary>
        <label htmlFor={field('scope')}>SHACL 验证范围</label>
        <select
          id={field('scope')}
          value={scope}
          onChange={(event) => setScope(event.target.value)}
        >
          <option value="asserted">当前断言事实（不含推导）</option>
          <option value="asserted+rdfs+rules">当前断言与本次推导</option>
        </select>
        <label htmlFor={field('sample')}>输入样本（Turtle，待真实解析）</label>
        <textarea
          id={field('sample')}
          value={sample}
          onChange={(event) => setSample(event.target.value)}
          rows={6}
        />
        <label htmlFor={field('expected')}>预期输出（完整三元组 JSON 数组，待校验）</label>
        <textarea
          id={field('expected')}
          value={expected}
          onChange={(event) => setExpected(event.target.value)}
          rows={5}
        />
        <p>样本仅保存在本页草稿中。实际输出未取得；正式测试必须使用批准执行器并返回错误位置。</p>
      </details>
      <section aria-label="检查与推理结果">
        <h3>检查与推理结果</h3>
        {!view ? (
          <p>未执行。请先完成正式接线并选择当前项目的真实运行结果。</p>
        ) : (
          <>
            <dl>
              <dt>结果状态</dt>
              <dd>
                {view.resultState === 'current'
                  ? '当前'
                  : view.resultState === 'stale'
                    ? '已过期，请重跑'
                    : '历史快照'}
              </dd>
              <dt>输入快照 / 版本</dt>
              <dd>
                {view.inputSnapshotId} / {view.inputVersion}
              </dd>
              <dt>数据范围</dt>
              <dd>
                {view.dataScope}；{view.includesDerived ? '包含推导结果' : '不包含推导结果'}
              </dd>
              <dt>约束 / 规则版本</dt>
              <dd>
                {view.constraintVersion} / {view.ruleVersion}
              </dd>
              <dt>执行语义</dt>
              <dd>{view.executionSemanticsVersion}</dd>
            </dl>
            {view.staleReasons.length > 0 && <p>过期原因：{view.staleReasons.join('、')}</p>}
            <ul>
              {view.checks.map((check) => (
                <li key={check.category}>
                  {check.category}：{checkText[check.state]}。{check.detail}
                </li>
              ))}
            </ul>
            {(['repair', 'improve', 'knowledge'] as const).map((severity) => (
              <section key={severity}>
                <h4>
                  {{ repair: '需要修复', improve: '建议改进', knowledge: '新发现的知识' }[severity]}
                </h4>
                <ul>
                  {view.findings
                    .filter((item) => item.severity === severity)
                    .map((item) => (
                      <li key={item.id}>
                        <span>{item.message}</span>{' '}
                        <button
                          type="button"
                          disabled={!onLocate}
                          onClick={() => onLocate?.(item.target)}
                        >
                          定位 {item.target.id}
                        </button>
                      </li>
                    ))}
                </ul>
              </section>
            ))}
            <StatementTable title="预期输出" rows={view.expected} />
            {view.actual === null ? (
              <p>实际输出未取得，不作通过判断。</p>
            ) : (
              <StatementTable title="实际输出" rows={view.actual} />
            )}
            {comparison && (
              <>
                <StatementTable title="缺少的预期事实" rows={comparison.missing} />
                <StatementTable title="不应出现的事实" rows={comparison.unexpected} />
              </>
            )}
            {view.difference && (
              <>
                <StatementTable title="新增推导" rows={view.difference.added} />
                <StatementTable title="撤回推导" rows={view.difference.withdrawn} />
                <StatementTable title="依据变化" rows={view.difference.changed} />
              </>
            )}
            <h4>执行器返回的依据</h4>
            <p>自定义规则需完整输入—规则—结果链；RDFS 至少展示相关公理和直接输入事实。</p>
            {view.trace.length === 0 ? (
              <p>没有可用依据；不能补写依据或声称存在证明。</p>
            ) : (
              <ol>
                {view.trace.map((node) => (
                  <li key={node.id}>
                    <strong>
                      {node.id} · {node.kind}
                    </strong>
                    <pre>{JSON.stringify(node.statement)}</pre>
                    <p>
                      {node.ruleId ? `规则：${node.ruleId}；` : ''}直接依据：
                      {node.inputs.length ? node.inputs.join('、') : '输入事实或公理'}
                    </p>
                  </li>
                ))}
              </ol>
            )}
          </>
        )}
      </section>
    </section>
  )
}
