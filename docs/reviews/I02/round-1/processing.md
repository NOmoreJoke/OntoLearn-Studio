# Round 1 意见处理与门禁记录

base `1b6df7a220fc9a67d7046133a340085f03f0a96c` → 同一 candidate `2cc03da82ffccc8448c7b03dc6cff87595027653`。两应用任务均实际结束且开发会话完整读回报告：ZCode GLM-5.3/最高明确通过（3 P3、2观察，均可延期）；MiniMax M3.1-Flash/xhigh 明确通过（5非阻断、0阻断）。不改报告严重程度/结论，不以 Codex 判断替代其意见。

本次只追加流程证据与勘误，没有修改实现/测试/配置/依赖/验收标准；所有非阻断项逐项处理如下。

| 来源 | 处理 | 依据与证据 / 剩余边界 |
| --- | --- | --- |
| Z P3-1 自愈后选择恢复无反馈 | 延期 M1 | 守卫避免重建已健康窗口符合当前 design；竞态单测已覆盖。将来可补用户反馈，本轮不影响 health 恢复。 |
| Z P3-2 / M-03 非法 dev origin/nonce 无窗口未处理拒绝 | 采纳事实，延期修复 | MiniMax 实测错误配置 localhost:5173 导致 0 窗与 stderr 拒绝；没有把它说成正常退出。固定 Vite 127.0.0.1:5173 + strictPort、生成合法 nonce 的正常启动及 packaged 分支不触发，三态实际通过；校验 fail-closed 不放宽。冻结范围不要求支持任意手工 origin；未来改开发端口/启动配置前应做显式诊断+非零退出并统一 origin 来源。两报告均明确非阻断（Z允许延期、M建议推送前但非必须），保留缺陷与后续处理约束，不声称已修。 |
| Z P3-3 createWindow 抛错 | 部分采纳，诊断延期 | `window-recovery.ts` 的 `try` 覆盖 `reopen()`，同步 throw 实际进入 catch，故“成为未处理拒绝”措辞不成立；原生提示与重建异常无日志这一事实成立，与 M-02 合并保留。先建后销使同步构造失败时旧窗保留。未证明真实环境曾发生该异常。 |
| Z O1 / M-01 随机 dev nonce 进入生产 main | 采纳，证据解释关闭；可复现构建优化延期 | 原 manifest 的 equalsBuild 表示**同一次 build** 包内外逐字节相同，不能解释成第二次独立 build SHA 相同。main 内嵌一次随机值导致 main/asar 跨构建不同，renderer/preload 独立复算相同；nonce 在 packaged 分支不使用，不削弱生产策略。新增 `package-manifest-semantics.json` 明确这一语义。冻结验收未要求可复现构建；采用 M-01 允许的证据标注方案，不声称源码已优化。 |
| Z O2 dev connect-src 显式 origin | 不需修改 | 固定开发 origin 下与 self 等价，两模型实际开发矩阵均通过。若调整 origin 必须同步策略/重新验证。 |
| M-02 原生提示整体 stub / catch 无诊断 | 采纳证据勘误并补实测；诊断改进延期 | 原自动化只证明请求、选项与选择分支，不能证明 native sheet；`native-dialog-probe/README.md` 明确修正既有证据解释。Run 2 在同一真实 packaged 进程、不替换 showMessageBox、关闭 inspector 后真实 hang/crash，CUA 截图+AX+点击证明提示可见、接受后“尚未检查”再手动 health、拒绝无重建。满足原验收，并未降低为仅请求。空 catch 任意异常诊断仍未修；作为原非阻断建议保留。Run 1 工具重启/不确定观察单独保留，不计通过。 |
| M-04 未来构建插件注入 inline | 延期 M1 构建目标/UI库变更前 | 当前锁定产物仅外链脚本与CSS，三态实测通过。生产 HTML 不得新增无法被当前 CSP 授权的内联 script/style；新增构建插件/目标时应验证最终 HTML 和 enforce 矩阵，不放宽 unsafe-inline/eval。此为交接约束，未引入新验收标准。 |
| M-05 导航约束交接 | 部分采纳 | design 已写所有文档/子frame导航拒绝、hash保留，因此“完全未记入”不符；交接仍在此明确：目前仅 hash 导航及 hash 后 health 经实测。history API 改 pathname/query 会使 isTrustedDocument 不再信任，不能泛称所有 history 路由可用；未来路由应重新评估可信文档协议。 |
| H-1 preferences 与 contents 区分 | 已关闭 | 冻结 design 分层、后建 contents 事件监听与 preferences 字段分别验证；两模型均复核关闭。 |
| H-2 恢复选择竞态 | 已关闭；补充证据 | 冻结6项竞态测试与双方实际运行；原生 sheet 的措辞缺口归 M-02，本次真实 UI 另补，不覆盖异常历史。 |
| H-3 native 驱动有界失败 | 已关闭 | deadline/exit/socket close/finally 清理与2项失败测试，双方独立通过。 |

## 推送前结论

无阻断问题，两指定模型均明确通过同一候选；M-01/M-02 的证据缺口已以流程证据澄清并补真实运行，没有假称源码修复。M-03 等未修建议明确延期且不影响两报告原通过判定。若后续需要任何实现/测试/配置/依赖/验收变更，必须新候选、双方全新任务重审。

下一步逐项 hash 复核 15 冻结路径、64 保护路径与报告原文；确认 candidate 之后只含 docs/reviews/I02 流程证据；fetch 远端 develop 必须仍为 base。以上通过才 push/PR，遵守实际 CI/合并门禁，不使用 admin 或 bypass。
