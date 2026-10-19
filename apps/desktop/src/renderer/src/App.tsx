import { useState } from 'react'
import type { HealthResult } from '@ontolearn/contracts'

const modules = [
  ['01', '定义业务概念', '本体构建'],
  ['02', '连接业务数据', '数据映射'],
  ['03', '向知识提问', '本体查询'],
  ['04', '检查并发现新知识', '知识推理'],
  ['05', '描述业务如何行动', '行为定义'],
  ['06', '比较不同方案', '沙盘推演'],
]

export function App() {
  const [result, setResult] = useState<HealthResult>()
  const [checking, setChecking] = useState(false)
  async function checkEngine() {
    setChecking(true)
    try {
      const response = window.ontolearn
        ? await window.ontolearn.getEngineHealth()
        : { ok: false as const, error: '当前为浏览器预览，请在桌面应用中检查本地引擎。' }
      setResult(response)
    } catch {
      setResult({ ok: false, error: '检查未完成，请重试。' })
    } finally {
      setChecking(false)
    }
  }
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="wordmark">
          <span className="brand-mark" aria-hidden="true">
            O
          </span>
          <strong>
            OntoLearn<span>STUDIO</span>
          </strong>
        </div>
        <div className="side-label">本体学习与落地工作台</div>
        <nav aria-label="工作台导航">
          <a href="#overview" aria-current="page">
            开发概览 <span>↗</span>
          </a>
          <a href="#modules">
            模块规划 <span>06</span>
          </a>
        </nav>
        <div className="sidebar-note">
          <span className="status-dot" />
          本地优先
          <p>
            无需配置模型 API
            <br />
            即可启动开发环境
          </p>
        </div>
      </aside>
      <main id="overview">
        <header>
          <span>工作台 / 开发概览</span>
          <span className="badge">M0 · 开发骨架</span>
        </header>
        <section className="intro">
          <p className="eyebrow">LEARN. MODEL. UNDERSTAND.</p>
          <h1>
            把业务问题，
            <br />
            转化为可验证的知识。
          </h1>
          <p className="lead">从本体建模到情景推演，在一个本地项目中逐步学习与验证。</p>
        </section>
        <section className="health-panel" aria-labelledby="health-title">
          <div>
            <p className="eyebrow">DEVELOPMENT ENVIRONMENT</p>
            <h2 id="health-title">检查本地引擎连接</h2>
            <p>验证桌面应用与 Python 引擎的真实通信。</p>
          </div>
          <button onClick={() => void checkEngine()} disabled={checking}>
            {checking ? '正在检查…' : '检查本地引擎'}
            <span aria-hidden="true"> ↗</span>
          </button>
          <div className="health-result" role="status" aria-live="polite">
            {result
              ? result.ok
                ? `本地引擎已连接 · v${result.data.engineVersion} · 协议 v${result.data.protocolVersion}`
                : result.error
              : '尚未检查 · 当前仅开放连接检查能力。'}
          </div>
        </section>
        <section id="modules" className="modules-section">
          <div className="section-title">
            <h2>六个模块，一条学习路径</h2>
            <span>需求规划 · 待实现</span>
          </div>
          <div className="modules">
            {modules.map(([number, title, detail]) => (
              <article key={number}>
                <span className="module-number">{number}</span>
                <div>
                  <h3>{title}</h3>
                  <p>{detail}</p>
                </div>
                <span className="planned">待开发</span>
              </article>
            ))}
          </div>
        </section>
        <footer>
          需求基准 PRD V0.6<span>项目编辑、自动保存、模型调用与六模块业务能力尚未接入。</span>
        </footer>
      </main>
    </div>
  )
}
