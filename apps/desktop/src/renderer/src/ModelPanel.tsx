import { useCallback, useEffect, useRef, useState } from 'react'
import {
  safeError,
  type BridgeResult,
  type JobView,
  type ModelAccessStatus,
  type ModelAuditEntry,
  type ModelConfiguration,
  type ModelExplanationOutcome,
  type ModelExplanationPreview,
  type ModelFieldCatalog,
  type ModelSelection,
  type SafeError,
} from '@ontolearn/contracts'

const auditPurposes: Record<ModelAuditEntry['purpose'], string> = {
  explain: '结果解释',
  suggest: '建议',
  review: '复核',
}
const auditEvents: Record<ModelAuditEntry['event'], string> = {
  'attempt-intent': '已授权并登记发送尝试',
  blocked: '已拒绝',
  'attempt-failed': '已授权，尝试失败',
}

export function ModelPanel({ jobs }: { jobs: JobView[] }) {
  const [status, setStatus] = useState<ModelAccessStatus>()
  const [copyFrom, setCopyFrom] = useState<ModelConfiguration>()
  const [audit, setAudit] = useState<{ contextId: string; entries: ModelAuditEntry[] }>()
  // null is initial auto-selection; '' is the user's explicit new-configuration choice.
  const [configurationId, setConfigurationId] = useState<string | null>(null)
  const [preview, setPreview] = useState<ModelExplanationPreview>()
  const [grantId, setGrantId] = useState<string>()
  const [catalog, setCatalog] = useState<ModelFieldCatalog>()
  const [fieldIds, setFieldIds] = useState<string[]>([])
  const [outcomes, setOutcomes] = useState<ModelExplanationOutcome[]>([])
  const [error, setError] = useState<SafeError>()
  const [busy, setBusy] = useState(false)
  const live = useRef(true)
  const binding = useRef('')
  const polling = useRef(false)
  const outcomeCache = useRef(new Map<string, ModelExplanationOutcome>())
  const secretInput = useRef<HTMLInputElement>(null)
  const configuration = status?.configurations.find(
    (value) => value.configurationId === configurationId,
  )
  const formConfiguration = configuration ?? copyFrom
  const enabled = status?.availability === 'ready' && !!status.contextId

  const refresh = useCallback(async () => {
    const bridge = window.ontolearn
    if (!bridge || polling.current) return
    polling.current = true
    try {
      const reply = await bridge.getModelAccessStatus({})
      if (!live.current) return
      if (!reply.ok) {
        setError(reply.error)
        return
      }
      const next = reply.data
      const key = JSON.stringify({
        context: next.contextId,
        privacy: next.privacy,
        configurations: next.configurations,
        selections: next.selections,
      })
      if (key !== binding.current) {
        setPreview(undefined)
        setGrantId(undefined)
        binding.current = key
      }
      setStatus(next)
      setConfigurationId((previous) =>
        previous !== null &&
        (previous === '' || next.configurations.some((value) => value.configurationId === previous))
          ? previous
          : (next.configurations[0]?.configurationId ?? ''),
      )
      if (!next.contextId) {
        outcomeCache.current.clear()
        setOutcomes([])
        return
      }
      const present = new Set(next.invocations.map((value) => value.invocationId))
      for (const id of outcomeCache.current.keys())
        if (!present.has(id)) outcomeCache.current.delete(id)
      const changed = next.invocations.filter(
        (value) => outcomeCache.current.get(value.invocationId)?.state !== value.state,
      )
      const replies = await Promise.all(
        changed.map((value) =>
          bridge.getModelExplanationOutcome({
            contextId: next.contextId!,
            invocationId: value.invocationId,
          }),
        ),
      )
      if (live.current) {
        for (const reply of replies)
          if (reply.ok) outcomeCache.current.set(reply.data.invocationId, reply.data)
        setOutcomes(
          next.invocations.flatMap((value) => {
            const cached = outcomeCache.current.get(value.invocationId)
            return cached ? [cached] : []
          }),
        )
      }
    } catch {
      if (live.current) setError(safeError(undefined))
    } finally {
      polling.current = false
    }
  }, [])
  useEffect(() => {
    live.current = true
    const initial = setTimeout(() => void refresh(), 0)
    const timer = setInterval(() => {
      if (!document.hidden) void refresh()
    }, 1500)
    return () => {
      live.current = false
      clearTimeout(initial)
      clearInterval(timer)
    }
  }, [refresh])
  async function action<T>(
    work: () => Promise<BridgeResult<T>>,
    accept?: (value: T) => void,
    update = true,
  ) {
    if (busy) return
    setBusy(true)
    setError(undefined)
    try {
      const reply = await work()
      if (!live.current) return
      if (reply.ok) {
        accept?.(reply.data)
        if (update) await refresh()
      } else setError(reply.error)
    } catch {
      if (live.current) setError(safeError(undefined))
    } finally {
      if (live.current) setBusy(false)
    }
  }
  function invalidatePreview() {
    setPreview(undefined)
    setGrantId(undefined)
  }
  async function selectResult(
    resultId: string,
    selection: 'current' | 'historical',
    fields = false,
  ) {
    const bridge = window.ontolearn,
      contextId = status?.contextId
    if (!bridge || !contextId) return
    invalidatePreview()
    if (fields)
      await action(
        () => bridge.getModelFieldCatalog({ contextId, resultId, selection }),
        (value) => {
          setCatalog(value)
          setFieldIds([])
        },
        false,
      )
    else
      await action(() =>
        bridge.selectModelResults({ contextId, results: [{ resultId, selection }] }),
      )
  }
  function receivePreview(value: ModelExplanationPreview) {
    setPreview(value)
    setGrantId(value.authorization.state === 'reusable' ? value.authorization.grantId : undefined)
  }
  return (
    <section id="model-settings" className="model-panel" aria-labelledby="model-title">
      <div className="model-heading">
        <div>
          <h2 id="model-title">模型设置与结果解释</h2>
        </div>
        <button disabled={busy} onClick={() => void refresh()}>
          刷新模型状态
        </button>
      </div>
      <p>
        默认完全本地。选择结果、预览外发范围并明确授权后，才可发送解释请求。本地任务不依赖模型成功。
      </p>
      {!enabled && (
        <p aria-live="polite">模型服务暂不可用或尚未选择本地项目。可以继续使用本地任务。</p>
      )}
      <fieldset disabled={!enabled || busy}>
        <legend>隐私模式</legend>
        <select
          aria-label="项目模型隐私模式"
          value={status?.privacy ?? 'local'}
          onChange={(event) => {
            const privacy = event.target.value as 'local' | 'minimal' | 'project'
            if (status?.contextId && window.ontolearn)
              void action(() =>
                window.ontolearn!.setModelPrivacy({ contextId: status.contextId!, privacy }),
              )
          }}
        >
          <option value="local">完全本地</option>
          <option value="minimal">最小上下文（仅选定材料）</option>
          <option value="project">项目上下文（仍需逐项选择）</option>
        </select>
      </fieldset>
      <details className="model-settings">
        <summary>模型接收配置与凭据</summary>
        <p>
          凭据只经专用入口送入本机安全存储，不回显。更换接收端后需要重新录入；不会自动复制项目隐私授权。
        </p>
        <label>
          配置
          <select
            aria-label="模型配置"
            value={configurationId ?? ''}
            onChange={(event) => {
              setCopyFrom(undefined)
              setConfigurationId(event.target.value)
              invalidatePreview()
            }}
          >
            <option value="">新配置</option>
            {status?.configurations.map((value) => (
              <option key={value.configurationId} value={value.configurationId}>
                {value.displayName}
              </option>
            ))}
          </select>
        </label>
        {configuration && (
          <button
            type="button"
            disabled={!enabled || busy}
            onClick={() => {
              invalidatePreview()
              setCopyFrom(configuration)
              setConfigurationId('')
            }}
          >
            复制为新配置
          </button>
        )}
        <form
          key={
            configuration
              ? configuration.configurationId + configuration.configurationVersion
              : copyFrom
                ? 'copy:' + copyFrom.configurationId
                : 'new'
          }
          onSubmit={(event) => {
            event.preventDefault()
            const form = new FormData(event.currentTarget),
              contextId = status?.contextId
            if (!contextId || !window.ontolearn) return
            invalidatePreview()
            void action(
              () =>
                window.ontolearn!.configureModel({
                  contextId,
                  ...(configuration
                    ? {
                        configurationId: configuration.configurationId,
                        configurationVersion: configuration.configurationVersion,
                      }
                    : { configurationId: null, configurationVersion: null }),
                  displayName: String(form.get('displayName')),
                  endpoint: String(form.get('endpoint')),
                  model: String(form.get('model')),
                }),
              (value) => {
                setCopyFrom(undefined)
                setConfigurationId(value.configurationId)
              },
            )
          }}
        >
          <fieldset disabled={!enabled || busy}>
            <label>
              名称
              <input
                name="displayName"
                required
                maxLength={128}
                defaultValue={
                  copyFrom
                    ? `${copyFrom.displayName.slice(0, 124)}（副本）`
                    : (configuration?.displayName ?? '')
                }
              />
            </label>
            <label>
              HTTPS 接收地址
              <input
                name="endpoint"
                type="url"
                required
                maxLength={2048}
                placeholder="https://…"
                defaultValue={formConfiguration?.endpoint ?? ''}
              />
            </label>
            <label>
              模型名称
              <input
                name="model"
                required
                maxLength={128}
                defaultValue={formConfiguration?.model ?? ''}
              />
            </label>
            <button type="submit">保存配置</button>
          </fieldset>
        </form>
        <form
          key={
            configuration
              ? `credential:${configuration.configurationId}:${configuration.configurationVersion}`
              : 'credential:new'
          }
          onSubmit={(event) => {
            event.preventDefault()
            const bridge = window.ontolearn,
              contextId = status?.contextId,
              input = secretInput.current
            if (!bridge || !contextId || !configuration || !input) return
            invalidatePreview()
            void action(() => {
              const request = bridge.storeModelCredential({
                contextId,
                configurationId: configuration.configurationId,
                configurationVersion: configuration.configurationVersion,
                secret: input.value,
              })
              input.value = ''
              return request
            })
          }}
        >
          <fieldset disabled={!enabled || !configuration || busy}>
            <label>
              API 凭据
              <input
                aria-label="API 凭据"
                ref={secretInput}
                type="password"
                autoComplete="off"
                spellCheck={false}
                maxLength={4096}
                required
              />
            </label>
            <button type="submit">安全保存凭据</button>
            <span>
              本机状态：
              {configuration?.credentialState === 'configured'
                ? '已配置（未验证远程有效性）'
                : '尚未配置或不可用'}
            </span>
          </fieldset>
        </form>
        {configuration && (
          <dl aria-label="模型能力验证状态">
            <dt>连接</dt>
            <dd>未验证</dd>
            <dt>结构化输出</dt>
            <dd>未验证</dd>
            <dt>受控工具调用</dt>
            <dd>未验证</dd>
          </dl>
        )}
      </details>
      <details className="model-settings">
        <summary>当前项目外发记录</summary>
        <button
          type="button"
          disabled={!enabled || busy}
          onClick={() => {
            const contextId = status?.contextId
            const bridge = window.ontolearn
            if (!contextId || !bridge) return
            void action(
              () => bridge.getModelAccessStatus({ auditContextId: contextId }),
              (value) => setAudit({ contextId, entries: value.audit ?? [] }),
              false,
            )
          }}
        >
          读取最近 20 条
        </button>
        {audit &&
          audit.contextId === status?.contextId &&
          (audit.entries.length ? (
            <ul>
              {audit.entries.map((entry) => (
                <li key={entry.eventId}>
                  <time dateTime={entry.time}>{new Date(entry.time).toLocaleString()}</time>
                  {' · '}
                  {entry.endpointOrigin}
                  {' · '}
                  {auditPurposes[entry.purpose]}
                  {' · '}
                  {auditEvents[entry.event]}
                  <details>
                    <summary>授权范围（{entry.scopes.length} 项）</summary>
                    <ul>
                      {entry.scopes.map((scope) => (
                        <li key={scope}>{scope}</li>
                      ))}
                    </ul>
                  </details>
                </li>
              ))}
            </ul>
          ) : (
            <p role="status">当前项目暂无外发记录。</p>
          ))}
      </details>
      <fieldset disabled={!enabled || busy}>
        <legend>明确选择已存结果版本</legend>
        <p>
          预览和发送准备会重读；重读时已不符合“当前”状态则拒绝。历史版本须手动选择，读取状态不保证发送瞬间仍为当前。
        </p>
        {jobs
          .filter((job) => job.state === 'succeeded' && job.resultRef)
          .map((job) => (
            <div className="model-result-choice" key={job.jobId}>
              <code>{job.resultRef!.resultId}</code>
              <button onClick={() => void selectResult(job.resultRef!.resultId, 'current')}>
                选中当前整份结果
              </button>
              <button onClick={() => void selectResult(job.resultRef!.resultId, 'historical')}>
                明确选中此历史版本
              </button>
              <button onClick={() => void selectResult(job.resultRef!.resultId, 'current', true)}>
                读取可选字段
              </button>
            </div>
          ))}
        {!jobs.some((job) => job.state === 'succeeded' && job.resultRef) && (
          <p>尚无已完成结果可选。</p>
        )}
        <button
          onClick={() => {
            if (status?.contextId && window.ontolearn)
              void action(() =>
                window.ontolearn!.selectModelResults({ contextId: status.contextId!, results: [] }),
              )
          }}
        >
          清空选择并取消关联请求
        </button>
      </fieldset>
      {catalog && (
        <fieldset disabled={!enabled || busy}>
          <legend>有限字段目录</legend>
          <p>仅适用于受支持的固定字段模型；没有可信映射时会拒绝。依赖字段必须同时明确选中。</p>
          {catalog.fields.map((field) => (
            <label key={field.fieldId}>
              <input
                type="checkbox"
                checked={fieldIds.includes(field.fieldId)}
                onChange={(event) =>
                  setFieldIds((previous) =>
                    event.target.checked
                      ? [...previous, field.fieldId]
                      : previous.filter((id) => id !== field.fieldId),
                  )
                }
              />
              {field.label} · {field.type}
              {field.nullable ? '（可空）' : ''}
              {field.requires.length
                ? `；需要：${field.requires.map((id) => catalog.fields.find((value) => value.fieldId === id)?.label ?? id).join('、')}`
                : ''}
            </label>
          ))}
          <button
            disabled={!fieldIds.length}
            onClick={() => {
              if (status?.contextId && window.ontolearn) {
                invalidatePreview()
                void action(() =>
                  window.ontolearn!.selectModelFields({
                    contextId: status.contextId!,
                    catalogId: catalog.catalogId,
                    fieldIds,
                  }),
                )
              }
            }}
          >
            选中这些字段
          </button>
        </fieldset>
      )}
      <div aria-label="已选模型材料">
        {status?.selections.map((selection) => (
          <ModelSelectionDetails key={selection.selectionId} value={selection} />
        ))}
      </div>
      <button
        disabled={
          !enabled ||
          busy ||
          status?.privacy === 'local' ||
          !status?.selections.length ||
          configuration?.credentialState !== 'configured'
        }
        onClick={() => {
          if (status?.contextId && window.ontolearn)
            void action(
              () =>
                window.ontolearn!.previewModelExplanation({
                  contextId: status.contextId!,
                  configurationId: configurationId ?? '',
                  selectionIds: status.selections.map((value) => value.selectionId),
                }),
              receivePreview,
              false,
            )
        }}
      >
        预览外发范围
      </button>
      {preview && (
        <div className="model-preview" aria-label="模型外发授权预览">
          <h3>本次解释请求</h3>
          <dl>
            <dt>接收地址</dt>
            <dd>{preview.endpoint}</dd>
            <dt>模型</dt>
            <dd>{preview.model}</dd>
            <dt>配置版本</dt>
            <dd>{preview.configurationVersion}</dd>
            <dt>本机凭据主体</dt>
            <dd>{preview.principal}</dd>
            <dt>用途与隐私</dt>
            <dd>解释 · {preview.privacy}</dd>
          </dl>
          {preview.selections.map((selection) => (
            <ModelSelectionDetails key={selection.selectionId} value={selection} />
          ))}
          <p>
            最终请求仍会检查版本、来源范围、隐私及实际接收配置。取消只能停止本地等待，已经发送的内容无法撤回。
          </p>
          {!grantId && (
            <button
              disabled={busy}
              onClick={() => {
                if (status?.contextId && window.ontolearn)
                  void action(
                    () =>
                      window.ontolearn!.confirmModelAuthorization({
                        contextId: status.contextId!,
                        previewId: preview.previewId,
                      }),
                    (value) => setGrantId(value.grantId),
                    false,
                  )
              }}
            >
              明确授权上述范围
            </button>
          )}
          {grantId && (
            <button
              disabled={busy}
              onClick={() => {
                if (status?.contextId && window.ontolearn)
                  void action(() =>
                    window.ontolearn!.startModelExplanation({
                      contextId: status.contextId!,
                      configurationId: preview.configurationId,
                      grantId,
                      selectionIds: preview.selections.map((value) => value.selectionId),
                    }),
                  )
              }}
            >
              发送解释请求{preview.authorization.state === 'reusable' ? '（复用已有授权）' : ''}
            </button>
          )}
        </div>
      )}
      {error && <ModelError error={error} />}
      <div aria-live="polite">
        {outcomes.map((outcome) => (
          <article className="model-outcome" key={outcome.invocationId}>
            <h3>解释请求 · {outcome.state}</h3>
            <code>{outcome.invocationId}</code>
            {(outcome.state === 'running' || outcome.state === 'cancelling') && (
              <button
                disabled={outcome.state === 'cancelling'}
                onClick={() => {
                  if (status?.contextId && window.ontolearn)
                    void action(() =>
                      window.ontolearn!.cancelModelExplanation({
                        contextId: status.contextId!,
                        invocationId: outcome.invocationId,
                      }),
                    )
                }}
              >
                取消此请求
              </button>
            )}
            {outcome.state === 'cancelled' && <p>已停止本地等待。远端是否已经接收内容未知。</p>}
            {outcome.state === 'completed' && (
              <>
                <p>模型解释仅供参考，不会执行修改或授予工具权限。</p>
                <pre>{outcome.text}</pre>
              </>
            )}
            {outcome.state === 'failed' && <ModelError error={outcome.error} />}
          </article>
        ))}
      </div>
    </section>
  )
}

function ModelSelectionDetails({ value }: { value: ModelSelection }) {
  return (
    <article className="model-selection">
      <p>
        {value.kind === 'whole-result' ? '整份结果' : '选定字段'} · {value.rowCount} 行 ·{' '}
        {value.byteCount} 字节
      </p>
      <dl>
        <dt>结果版本</dt>
        <dd>{value.metadata.resultId}</dd>
        <dt>输入快照</dt>
        <dd>{value.metadata.inputSnapshotId}</dd>
        <dt>读取时状态 / 选择方式</dt>
        <dd>
          {value.metadata.state} / {value.selection}
        </dd>
        <dt>内容摘要</dt>
        <dd>{value.kind === 'fields' ? value.projectionHash : value.bodyHash}</dd>
      </dl>
      {value.kind === 'fields' && (
        <p>已选字段：{value.fields.map((field) => `${field.label} (${field.type})`).join('、')}</p>
      )}
    </article>
  )
}
function ModelError({ error }: { error: SafeError }) {
  const reasons: Record<string, string> = {
    GATEWAY_LOCAL_ONLY: '项目处于完全本地模式。',
    GATEWAY_AUTHORIZATION_REQUIRED: '授权缺失、已失效或不属于当前项目。',
    GATEWAY_SCOPE_EXCEEDED: '材料版本、字段范围或来源已改变。',
    GATEWAY_CONFIGURATION_CHANGED: '接收配置或凭据版本已改变。',
    GATEWAY_CREDENTIAL_UNAVAILABLE: '本机安全凭据不可用。',
    GATEWAY_AUDIT_UNAVAILABLE: '本机发送审计无法持久保存。',
    GATEWAY_REDIRECT_REJECTED: '接收方返回了不允许跟随的重定向。',
    GATEWAY_RESPONSE_LIMIT: '响应超过允许上限。',
    GATEWAY_MODEL_UNAVAILABLE: '模型网络、并发或等待条件不可用。',
    GATEWAY_INVALID_INPUT: '输入或材料超出允许形状或上限。',
  }
  return (
    <div className="error-details" role="alert">
      <p>发生了什么：解释请求未完成（{error.code}）。</p>
      <p>为什么发生：{reasons[error.code] ?? '所选来源或本机条件当前无法通过检查。'}</p>
      <p>影响范围：本地任务仍可继续；失败不证明远端从未收到请求。</p>
      <p>下一步：检查当前配置、隐私与材料版本，重新预览；需要再次发送时请手动发起。</p>
    </div>
  )
}
