# T09 S1 replacement-r1 独立准备预检

**结论：本次限定准备范围通过，无发现的实质缺陷或矛盾。** 两方输入完整保留既有 scope 和历史块，新补充明确覆盖旧身份/写面/运行取证规则，未预填指定或产品 Pass。本结论不授予 START、GUI、模型任务、环境安装或发布权限，不继承旧 Z 结论，也不证明未来创建状态。

2026-10-23（Asia/Shanghai），独立 Codex 子 agent `t09_prd_audit`。唯一写入本报告，其余材料只读。

## 实际阅读与字节核对

读取中央 `preparation-manifest.json`、`current-execution-supplement.md`、两份 replacement mapping/template，以及两份 full-input 的新首段、分隔结构和完整新补充；对嵌入旧正文/历史索引只按 manifest 声明的 offset、bytes、SHA 核对，不重新审阅旧模型意见。两份尾部均与 common 补充逐字节相同。

| 原件                   | bytes / 行数 | SHA-256                                                            |
| ---------------------- | ------------ | ------------------------------------------------------------------ |
| Z full-input           | 75876 / 408  | `e7bc2a159c554df686f7d991d3912798d1e1caa7f08ba93f2cdacbd675c088ea` |
| M full-input           | 75943 / 408  | `18fbcbe32a1dd353e36c63a311db31f7257e2b0ef2ad538dc2084880ec47fe1b` |
| common 补充            | 13697        | `155455939e9724908188a07612d69b976d0a03435271f43506b579b7d8fbda04` |
| operator-only manifest | 9627         | `789b25457f3fccf41dd3e15dc3d39048ac7dc15be04f1a23fa5bc0639e06e796` |

Z 的旧正文块位于 byte offset 2813，51699 bytes，SHA `ebdaf40e51c09a602174a9cca2060934e53d376b7a48c2555927eef2565d922f`；M 位于 2844，51735 bytes，SHA `c9a468e258a0ddb18db63c2018e47ff31ab2bd6b8db0738f540e021506774c51`。两份历史块分别位于 54671/54738，均 7470 bytes，SHA `1b77a37904550bc84e0207137df6bf86fd93449cf945179291f1db334a165d54`。全部与声明相符，未以摘要替代原块。

两份 mapping 为 3389/3451 bytes，SHA 分别 `85efab5c0fc5a01c27a3cd01df8535826a045dea29756bc196622a390e820067` / `be4f96d5a92e5d19b41673be857b53d9a88b6229bbe21a75d936a0308a122a94`；template 均 466 bytes、SHA `05a9fe42f4af5902b2a313cac1eb0f3f372db95b2b153facfb84fa47462a78cd`。新增授权的六个精确 NEW 物化文件逐字节等于中央对应 full-input/mapping/template。没有跟随读取旧 mapping、旧报告、原生模型文件、全局配置或运行 metadata。

## 新旧范围与身份边界

保留完整 base→product 55 文件、32 产品源/数据、106 manifest、869 tracked 基线、原 PRD、17 输入/50 计划、所有原验收/历史失败，以及 13 项旧问题和 PARENT-01/02/03。历史索引的“已关闭”明确只属当时记录，要求新任务从头重判。S1 与后排 N0/stage 不拼接，不夹入 12699/245718/e651 能力。

批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`、product `76596656908ed84e577e8202a602e3256d5febcc`、tree `8b646570108026a8deabe8330c548cab0280122d`、公共 review HEAD `72aa83a80a973a3edeb62ed95518bf1a22178985`、process `d96924e715a1b2139a75b70aea40fc30ae1129fe` 分列。它们来自已接收固定证明；本预检未重新读取 Git/HEAD、32 源或未来实际 UI 状态。

新首段和补充优先于嵌入旧文的开发树/branch、round-1/dispatch-runtime 写面及主动身份发现要求。两方 report/runtime/fresh-receipt 路径各自隔离，不覆盖旧产物。template 全为 UNKNOWN，明确不是观测证明；新回执仅操作员可写，模型仅取明确提供的单份 fresh 本人回执。不存在、缺字段或矛盾即 UNKNOWN/无法验证，不采旧 SID、旧设置或环境自述，不主动寻找 provider registry/权限配置/后台入口。

agent list/include_primary、session get、任务枚举/发现、全局或用户级 config/AGENTS/日志/数据库、安装包内部、peer 与旧运行 metadata 均明确禁止。未知 metadata 只可路径/lstat，不读、hash、解析、删改；另一方 prompt 即使列入旧 manifest，也仅保身份，不打开正文核 hash。本人原生附件只限应用明确提供的精确路径及获准 Read，不授附近资产发现。审批拒绝须保留并停止该路径，明禁换工具、Bash/Python/脚本/编码/子进程或私有 RPC 包装绕过。

## 延期、失败与验证门

| 议题      | 新补充实际要求                                                                                                             |
| --------- | -------------------------------------------------------------------------------------------------------------------------- |
| S1-OBS-01 | T10 正式导出接线验收前，补缺能力、exported:false、异迟 context 三类组件断言；未称已覆盖/已修                               |
| S1-OBS-02 | 后继内容候选增强，不动当前冻结题；内容/manifest 改变后新候选及双方新完整审查                                               |
| S1-OBS-03 | 相关内容/oracle 下次维护前，补完整对象、顺序、双 replay 对固定 expected 的直接一致断言；禁止只比长度/计数/公式或互抄弱比较 |

三项仅为总控有条件延期，要求双方独立接受/不接受/证据不足及理由；不豁免更高严重度或范围内必验缺失，也不关闭 13 旧问题或 3 parent。

前组一侧过程 Fail、正式 aborted、曝光范围 UNKNOWN 均保留；没有带入返回正文或宣称零曝光。operator reminder 过宽投影单列为异常，多余上下文排除。显式 headless 首败保留捕获退出文本 1、缺 chromium_headless_shell-1248、18 passed/16 skipped；未设 opt-in 的退出文本 0、42 pytest 和 verify not-executed 均只作历史事实。原 native 整数 exitCode/stderr 缺证没有被 completed/isError=false 替代，旧同版证据是否足够须新任务独立判断。

必要普通对应检查仍允许受控 stdio/临时 SQLite/worker；无变化不机械重跑，不扩为 native、HTTP、产品或正式领域调用。新运行须保存完整 argv/cwd/env 差异、开始/退出时间、分开的完整 stdout/stderr、原件 bytes/SHA，以直接子进程等待取得真实整数 returncode，区分 runner 与 child；不以 tail/grep/管道末命令、echo 或工具成功掩盖失败。

无新增浏览器/环境 setup 票，不为已知 1248 缺失重跑，不换 Playwright/Chromium、全局缓存或放宽 sandbox 求绿。确有新环境需求时，仅报告精确版本/revision、授权私有缓存的存在/lstat、最小 argv 和下载/写入/锁/共享影响，等待精确票。16 skip 不转 Pass；所有领域、durable、bridge/App、资源入包、T08/T10、双 OS/包/native、真人及原 80% 口径、CI/远端/发布/57P0 门保留。

关键身份或重要证据不足须无法验证；范围内阻断/必验缺失不得 Pass，禁止条件 Pass。旧 Z Pass、旧受理/设置或前组结果不得继承；新一对须各自完整新任务、实际 terminal、全文收件和意见处置。准备、template 或新输入均不是 START、新环境、模型任务、Goal 或发布授权。

## 本次未做事项

未读取 reviewer 树旧模型意见、原生模型/global/数据库/schema/产品源码或测试；未执行文内命令，未做产品、环境、浏览器、GUI 或新任务验证。仅对中央准备材料及六份精确 NEW 副本完成上述静态预检，不将已有证明派生的准备状态冒充 fresh 运行证据。

## 格式边界纠正与最终字节

预检定稿期间，T09 开发线自查发现 docs/reviews 默认被 Prettier 忽略并通知总控，普通 --check 的 exit0 不能算实际格式覆盖。本报告没有运行或采信普通检查作为覆盖；本次只对本报告使用显式 --ignore-path /dev/null 格式化和检查。开发线仅显式格式化新 common/JSON 并重新组装 full-input；literal 输入不交给格式工具，旧 packet 没有重格式化或重新证明。manifest 的 formatCheckBoundary 明确保留该边界。

初版到最终正文的变更记录（初版不是当前派发 hash）：

| 方  | 初版 bytes / SHA-256                                                       | 最终 bytes / SHA-256                                                       |
| --- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Z   | 75412 / `72b786795ad3a071ef083e9ab53f09fcb116b49ff5a68735d5a9c525b9019293` | 75876 / `e7bc2a159c554df686f7d991d3912798d1e1caa7f08ba93f2cdacbd675c088ea` |
| M   | 75479 / `ee8fe0a5fca929ab35233e24449c28f0f6ff5cba1e6f221a0b7f2b72d541c65c` | 75943 / `18fbcbe32a1dd353e36c63a311db31f7257e2b0ef2ad538dc2084880ec47fe1b` |

仅归一当前 common 的表格单元格空白和分隔线 padding 后，即精确恢复初版 common SHA `4b4a14166dd7867178fdf548180f8b85a9057f9c3962c42a1a29b72ee10d0bcd`，证实是表格格式变化；最终 common 为 13697 bytes / `155455939e9724908188a07612d69b976d0a03435271f43506b579b7d8fbda04`。两方仍各408行，旧正文/历史块的 offset、bytes 和 SHA 完全未变，mapping/template hash 未变；六个精确 NEW 物化副本再核均与最终中央字节相同。未重读旧 scope、重核 HEAD/32 源或重测环境，准备结论不变。
