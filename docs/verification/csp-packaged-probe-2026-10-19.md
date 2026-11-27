# 打包态 CSP 定向核验

日期：2026-10-19。对象：现有 `release/mac-arm64/OntoLearn Studio.app`，开发骨架基线 `e628f5e`。只读启动与临时 DOM 探测，不重建产物、不修改源码或持久业务数据；探测结束清理 DOM 并关闭应用。

## 结论

**本机未复现“file 页面没有 CSP”。** 没有 meta CSP，但实际页面响应包含 CSP，且策略处于 enforce 状态，内联脚本、内联 style 元素和 style 属性被拦截。不能仅凭源码的 `loadFile` 就宣布打包态 CSP 失效。

该结果只适用于以下版本与产物，不证明其他系统、Electron 版本或所有 CSP 指令均有效。显式 meta 交付、策略集中管理和真实打包回归仍应纳入[更新计划 C1](../architecture/m0-review-and-update-plan-2026-10-19.md)。

## 产物与运行环境

| 项目                                        | 实际值                                                                                                             |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| 平台 / 架构                                 | macOS / darwin arm64                                                                                               |
| `app.isPackaged`                            | `true`                                                                                                             |
| Electron / Chromium                         | `44.9.0` / `152.0.7977.167`                                                                                        |
| 启动方式                                    | Playwright `_electron.launch` 直接启动 `.app/Contents/MacOS/OntoLearn Studio`，移除环境中的 `ELECTRON_RUN_AS_NODE` |
| 页面                                        | `file://…/OntoLearn Studio.app/Contents/Resources/app.asar/out/renderer/index.html`                                |
| asar 主进程 / renderer HTML 与本地 out 比较 | 两者逐字节一致；不是用另一个 HTML 测试策略                                                                         |
| `out/main/index.js` SHA-256                 | `d8aafa64a3d2282932d8610bc4027c2e87543cf5bb8ee6c677056d1810717e10`                                                 |
| `out/renderer/index.html` SHA-256           | `8c301b8b8e7d60a89510e5270031c639dc56e45d6407880640f1cb7ea393955b`                                                 |

实际刷新页面响应：status `200`、content-type `text/html`，包含下列 `content-security-policy`：

```text
default-src 'self'; script-src 'self' ; style-src 'self' ; img-src 'self' data:; connect-src 'self' ; object-src 'none'; base-uri 'none'; frame-src 'none'; form-action 'none'
```

## 探测结果

先启动原产物测试内联 script/style；为解释与官方文档预期的差异，再启动同一产物，监听页面刷新响应头并细分样式路径。两次内联 script/style 的阻断结果一致。

| 探测                                                | 结果                                                |
| --------------------------------------------------- | --------------------------------------------------- |
| 查询 meta CSP                                       | 无，`null`                                          |
| DOM 追加 `script.textContent`，尝试设置临时全局标记 | 未执行；捕获 `script-src-elem`，`blockedURI=inline` |
| DOM 追加 `<style>`，检查目标节点 computed color     | 未应用；捕获 `style-src-elem`，`blockedURI=inline`  |
| `element.setAttribute('style', ...)`                | 未应用；捕获 `style-src-attr`，`blockedURI=inline`  |
| `element.style.color = ...`（CSSOM 属性赋值）       | 已应用                                              |
| violation 的 `disposition`                          | 三类均为 `enforce`，`originalPolicy` 与响应头一致   |

注入动作由 `page.evaluate` 创建 DOM 元素，**不是**以 `page.evaluate` 本身能执行来判断是否绕过 CSP。以页面脚本标记、computed style 与原生 `securitypolicyviolation` 事件交叉判断；未启用 `bypassCSP`，未替换应用的响应头处理器。

当前 renderer 没有 `style={{}}`。CSSOM 结果说明“所有 React 内联 style 都将被生产 CSP 拦截”没有依据；未来 UI 库是否使用 style 元素、属性字符串或 CSSOM 应逐项验证。

## 最小复现

从仓库根目录执行，需已有上述打包产物和已安装仓库依赖。该片段复现响应头、script/style 元素阻断及 CSSOM 对照；产物哈希比较和 style 属性测试按上表另行核对。

```sh
node --input-type=module <<'NODE'
import { _electron as electron } from '@playwright/test'
import { resolve } from 'node:path'
const env = { ...process.env }
delete env.ELECTRON_RUN_AS_NODE
const application = await electron.launch({
  executablePath: resolve('release/mac-arm64/OntoLearn Studio.app/Contents/MacOS/OntoLearn Studio'),
  args: [], env,
})
try {
  const page = await application.firstWindow()
  page.on('response', response => {
    if (response.url().endsWith('/index.html')) console.log(response.headers())
  })
  await page.reload()
  await page.waitForSelector('h1')
  console.log(await page.evaluate(async () => {
    const violations = []
    const handler = e => violations.push({
      directive: e.effectiveDirective, blockedURI: e.blockedURI,
      disposition: e.disposition, policy: e.originalPolicy,
    })
    document.addEventListener('securitypolicyviolation', handler)
    const script = document.createElement('script')
    script.textContent = 'window.__cspProbe = 1;'
    const style = document.createElement('style')
    style.textContent = '#csp-probe { color: rgb(1, 2, 3); }'
    const target = document.createElement('div')
    target.id = 'csp-probe'
    const cssom = document.createElement('div')
    cssom.style.color = 'rgb(4, 5, 6)'
    document.body.append(target, cssom)
    document.head.append(script, style)
    await new Promise(resolve => setTimeout(resolve, 100))
    const result = {
      inlineScriptExecuted: window.__cspProbe === 1,
      styleElementApplied: getComputedStyle(target).color === 'rgb(1, 2, 3)',
      cssomPropertyApplied: getComputedStyle(cssom).color === 'rgb(4, 5, 6)',
      violations,
    }
    for (const node of [script, style, target, cssom]) node.remove()
    document.removeEventListener('securitypolicyviolation', handler)
    delete window.__cspProbe
    return result
  }))
} finally {
  await application.close()
}
NODE
```

## 尚未覆盖

- Windows/Linux、其他 Electron 版本、正式签名/安装器或干净设备。
- 外联 fetch、外部资源、frame、form 等各指令的完整阻断矩阵。
- 开发态 nonce/HMR 的新回归，以及补 meta 后多份策略叠加的影响。
- 真实候选 RDF/SHACL 依赖及任何长任务能力。

Electron [官方安全指南](https://www.electronjs.org/docs/latest/tutorial/security#7-define-a-content-security-policy)说明 file 加载可使用 meta，并称不能通过 HTTP header 方式交付；本机实际收到了 CSP 响应头且观察到阻断。此处保留二者差异，以当前产物实测判断当前行为，不外推为所有平台保证。
