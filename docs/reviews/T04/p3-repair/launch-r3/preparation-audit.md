# 同507第三轮完整双审准备独审

2026-10-23；独立 agent `/root/t04_private_review`。**最终准备审查通过，无未关闭的准备阻断。** 这是准备包/部署/取证边界审查，不是指定模型审查，不继承旧554或上一507轮任何模型Pass；上一轮M过程Fail及总控不接收完整双Pass的结论保持。

## 固定范围与最终字节

- 产品与两方实际review HEAD均精确为 `5070004ec8e3219bea33960bd88f57f1976e9cf8`，批准base均为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。两新树均detached，无分支；不能用不同流程HEAD加产品等价代替同版门。
- `T04-s1-zcode-r3-5070004` 与 `T04-s1-minimax-r3-5070004` 各42项物理产品文件，均与固定507 Git blob及完整product-manifest逐字一致。base→507完整42项diff为256242B/SHA `27c090fc00cd6d1a851695551c2d5e4e9714d9845b9d5f3ee91ae51f9995b030`。
- owner最终package-files的26项payload合计609667B，逐项bytes/SHA均匹配；manifest自身SHA为 `f6c441476b8f91a4c6c4bc57c61084d492e615c5035022f291eb70c4d94dbead`。该manifest明确不包含自身与本独审回执。
- 每棵新树物理部署均恰为本角色18项payload＋本人role manifest，共19项，逐字等owner包及角色manifest。支持包未纳入当前受审Git；实际tracked差异仅保护AGENTS M，另有本角色launch-r3未跟踪输入。AGENTS15147B/SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。
- 两方无另一角色prompt/mapping/setup，无上一507轮round-2报告目录，无round-3报告或占位。共同支持只含指定旧554历史与中性过程事实，未夹带上一507轮双方产品意见。

| 本方完整输入          | 行数 |  字节 | SHA-256                                                            |
| --------------------- | ---: | ----: | ------------------------------------------------------------------ |
| full-zcode-input.md   |  147 | 29675 | `45828e0984d527d2a105dca0b6cd6bc5823713e96f0b802ade914d603bc5bf1c` |
| full-minimax-input.md |  147 | 29715 | `1985d7c54e0d1f0b8804018542e7d57d070c3d4da08b3055e1940f8dc53f1c40` |

两全文的角色差异限于本人模型/树/映射/setup/runtime/报告及探针唯一label；共同完整S1、四P3、历史逐项、FR-400–404/FR-006/C/D/G/第11–12节及父功能边界均保持。两角色均要求全新完整独立判断，不只审四P3、UI或reader；不要求整个M0就绪才判断有界S1。

## 恢复链、环境与政策

- 旧554历史包71成员逐项与固定 `9da9da48b45b4f0cbbe084d95c3d23ebd85c579b` Git blob/清单bytes/SHA一致；T09 provenance19成员逐项与固定 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 的sourcePath和哈希一致。17输入＋PRD＋manifest均可恢复，额外14项仍只作provenance，不冒充执行验收或扩大三副本的实际产品消费面。
- 当前section9、desktop、permissions全文均原字节嵌入两正文；current-agents单独原字节提供。政策中的全局路径明确只是来源引用，不产生审者访问授权；最新桌面政策与总控内部GUI交接要求同时保留，未以旧静默/CLI前提扩大阻塞。
- 两方node_modules与.venv均为各自独立物理目录，非共享symlink。各自uv/npm实际exit0的两组收据/raw，均与本人环境及4成员安装归档匹配。锁内 `@rolldown/binding-darwin-arm64@1.2.14` 当前存在，未登记本轮补装；安装不等于产品验证通过，旧轮首败不移植为本轮失败。
- 日志helper仅静态源码/AST检查，未执行。限定R3树名，以argv直接运行子进程（无shell=True），raw用独占创建拒覆盖，记录实际argv/cwd/UTC起止/exit/bytes/hash；正文固定用本方`.venv/bin/python`。正常check、T04定向、SSR和已批准headless/offline真实组件probe仍授权，工程收据不伪装身份/设置/原生证明。未降模型/权限、改hook或新增OS隔离。

## 本次发现及关闭

1. **恢复路径（P3，已关闭）**：最初R3的policy-sources四条本地path及history/T09两条archive.path沿用旧launch目录。已在R3索引修正六个指针；角色manifest/物理输入/部署收据/总manifest同步，政策snapshot及tar原字节未改。最终全部指针可在本角色R3输入内恢复。
2. **同实际HEAD门（总控明确纠正，已落实）**：初始58a/b2da及修正后026a/a120的不同角色支持HEAD不被接受。总控进一步明确同一base→实际HEAD后，本独审暂缓终态，没有用产品等价代替；owner已将两树实际HEAD统一detached507，支持文件保为独立未跟踪物理输入，并同步两正文/映射/部署语义。旧支持提交由 `refs/t04-history/round3-{zcode,minimax}-support` 保留，末端026a/a120及原祖先58a/b2da的存在/祖先关系已只读核验，不用其作当前受审HEAD。

本独审只读核验脚本曾把operator目录存在误当身份占位而停止；逐文件核对实际仅有`operator/preparation.json`，其taskId/turnId=null、submitted/settings/lease=false。acceptance.json与settings.json均不存在；修正的是本独审断言，不是准备包或产品。该断言失败不计产品测试，也未伪装无失败。

## 身份与接收边界

身份只引用本人operator/acceptance.json与operator/settings.json；缺失为UNKNOWN并正常报告owner，禁止自行session get、全局配置/账号/日志/native/peer读取或恢复搜索，禁止写operator或owner命名证据。发生误写只报告并停止扩展恢复；工程验证可继续其不依赖身份缺口的部分。当前preparation/deployment/mapping一致保持未创建、未发送、未读回真实设置、无lease、无模型报告或终态。

本轮未运行产品测试/check、GUI或模型任务，未读后台/native/global/peer材料；只按授权新增本回执，不改提示、产品、锁或旧原件。包通过不构成任务创建或指定双审通过；owner仍须固定当前过程包/本回执、按总控窗口实际创建两项新任务、逐任务读回设置、核完整输入受理、原turn终态/全文报告/全部意见，并履行原CI/平台/父验收与发布门。
