# T01 启动诊断合同 r3：原始 payload 字节依据与精确路径门

本页只补总控 P2-RAW-1024 及错误链责任前置，保留 [r1](business3-ready-startup-contract-r1.md)、[r2](business3-ready-startup-contract-r2.md) 和原 R1–R4 的设计关闭结论。仅文档提案，不注册新码，不修改或启用产品、测试、runtime3、公共 ready。

## 1. 固定输入与审查处置

全文读取本体根 `iteration-control/2026-10-21-weekly-release/T01-controller-business3-ready-startup-design-review.md`，实际 SHA256 为 `55d18362b395c00036eca633ebe3ff93b38e0923e4e1d03965ea5e0ac5d65680`，与总控固定输入一致。r1 实际 SHA256 为 `f715934e6a8bfd130fbb0c01c62d33026b6f19f990bc4268eb66a0ee6a3673ed`；r2 为 `e18a4ee8ec4fe32fe4d6df7b900f73aa4ee350723e8f1923109a7d3d925da281`，均保持原件。

接受总控反例：当前 reader 在 LF 处分帧、清零内部 size、去末尾 CR、严格解码后只回调 decoded value。合法诊断前加 2000 个 ASCII 空格或改变 JSON 转义，仍可得到相同对象；回调时的 bufferedBytes 与 `JSON.stringify(value)` 都不能证明实际收到的原帧不超过 1024B。r2 的 decoded-value 入口须取得同一个 reader 提供的原始计量证据，不能另造 parser 或凭解码对象重建原字节。

本页为该接口及计量口径的明确采纳提案，仍须实际 owner offer、T01 接受、独立核验和 root 登记生效；不能用设计处置绕过路径交接。

## 2. 唯一计量口径与只读 metadata

采用总控建议：`payloadByteLength` 表示同一个现有 JsonlReader 为当前帧累计收到的**全部原始 payload 字节数，不含分隔 LF，计入去除末尾 CR 之前的字节**。前后空白、JSON 转义的反斜杠和字符、所有实际 UTF8 字节均计入；不是 Unicode 字符数、decoded 字符串长度、重编码结果或去 CR 后长度。跨 chunk 的累计不能丢失或重复。没有 LF 的未完成数据仍按原 reader 的缓冲、帧限和 EOF 规则处理，不因诊断合同成为完整记录。

最小内部接口提案是在原 `frame(value)` 回调增加来自 reader 的只读 metadata：`Readonly<{ payloadByteLength: number }>`。该值必须来自当前完整帧清零/去 CR 前的实际累计整数，和该次 decoded value 一一对应；不传原文，不重 parse，不在业务 JSON 里加入字段。main 的接收方不得从 child 对象属性、bufferedBytes、全局累计量或上一次回调借用此证据。readonly 是内部 API 约束，不是 child 真实性证明；reader 仍是唯一原字节计量来源。

reader 继续完成原严格 JSONL 解析、重复键/Unicode/深度检查和通用 262144B 帧限，不改变 hello、业务帧、notification 的现有限额。metadata 不放宽原 parser；解析失败根本不进入合格 startupFailure 分支。不能把全部 pre-hello 帧统一降到 1024B，也不能在 engine.ts 外挂另一个 JSON/行解析器。

main 在当前受信 child/generation 的同步 decoded-value 分派处，先识别独立 startupFailure，再同时核验：受信 profile3、尚未成功 hello、一次性、严格 shape/有限 error、trusted expected registry hash，以及 metadata 的实际 `payloadByteLength <= 1024`。缺失或无效 metadata、超限或任一其他条件不成立，均按无效帧同步失效；不能接纳后补查或退入三次 anomalies 容忍。普通帧仍走自己的严格合同，不消费诊断专属 1024B 限额。

仅当以上全部成立，才闭锁首个安全 startupCause，并同步 terminal、reader.stop、拒 startup promise/全部 pending、停止新发送和终止自有 child；同 chunk 后续帧不继续分派。EOF/close/stdin-error/timeout/cleanup 不覆盖首错。ready 后的该记录仍是无效帧，产生真实 ready→disconnected，不抹除历史或 durable 结果。上述行为延续 r2，不新增业务 envelope、null-session 通配或 error2/error3 例外。

## 3. 真实 producer 与完整 golden 计划

真实 producer 在全部自有收尾尝试后，最多输出一条合格记录，使用实际单行 UTF8 payload 加一个 LF；不输出 CRLF、BOM、额外空行、前缀日志或堆栈。生产端须以**最终实际将写出的 payload bytes**核验 1024B，不含最终 LF；写出相同字节后 flush 并退出非零。不是接收方对 decoded 对象重新序列化计量。无可信资源 hash 时仍固定 stderr 与通用退出；写失败不伪造成功。逐资源 cleanup、首错和不伪 settled 保持 r2。

后续获准实施时，golden 必须保存完整原始输入 bytes（含 LF/CR 的精确存在）、预期 payloadByteLength、严格 decoded 值或解析拒绝、profile/generation/hello 前后状态、最终 SafeError/退出及同 chunk 后续帧是否分派。不得只保存 pretty JSON、摘要长度或一个“进程关闭”断言。四个诊断分支用同候选实际 registry hash，各自保存 producer 单行 UTF8 golden，并由两端独立核对实际字节；r1 的 b35 hash 仍仅是历史示例。

必要边界矩阵如下，均为计划，尚未运行：

| 输入/场景                                                                | 必须固定的 oracle                                                                                                                                                                |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 合法严格诊断，LF 分隔，完整原 payload 分别为 1023、1024、1025B           | 通过 JSON 合法前后 ASCII 空白补齐精确边界；1023/1024 可接纳，1025 同步拒绝，不能按 stringify 后的紧凑长度接受。四种错误分支均保留完整值 fixture。                                |
| 合法紧凑诊断前加 2000 个 ASCII 空格                                      | decoded 值不变，仍在通用帧限内；实际 payload 超过 1024，必须拒绝。                                                                                                               |
| 同一 decoded 诊断使用直接 ASCII 与合法 `\uXXXX` 转义写法                 | 完整原 bytes 与长度按实际不同；另构造 decoded 相同但原长为 1024/1025 的配对，分别接受/拒绝。不能从对象等价推导字节等价。                                                         |
| LF 与 CRLF 口径                                                          | LF 不计入；同一 JSON payload 末尾加 CR 再 LF，CR 计一字节。构造原长 1024/1025 的对应样本，计量后才去 CR/解码；真实 producer 只输出 LF。                                          |
| 跨 chunk、边界恰切在 CR/LF、转义序列或 UTF8 多字节内部                   | 与一次 push 的原计量及解析结果完全一致。合法诊断固定字段/值不为测试引入新 Unicode 自由字段；多字节计量用现有合法通用 JSONL 帧，或明确属于非法诊断的输入验证，不放宽诊断 schema。 |
| 非诊断 hello/业务帧介于 1025B 与原通用帧限之间                           | 不因本专属预算被拒；仍由原完整 shape、hash、版本、限额和通用 parser 决定。原通用帧限边界另保留，不能被 1024 替代。                                                               |
| 失败记录与成功 hello/notification/第二记录在同一 chunk                   | 合法或非法首个诊断均同步 terminal/stop；后续帧不消费。无 hello pending 时也直接拒启动 promise；EOF/close 等后续事件不覆盖首错。                                                  |
| 已合法 ready 后再来记录、旧 generation、错误 hash/shape/profile/metadata | 不作为合格启动诊断；同步终止受影响当前连接时保留实际 ready 历史与 generation 隔离，不由旧 generation 伤及新 child，不覆盖 accepted/committed。                                   |

转义 fixture 只改变 JSON 表达，不能改有限 code/key/params 的 decoded 值。边界空白允许用于接收端反例，不授权真实 producer 输出填充。完整 fixtures 还须穿过启动 catch、task-service 和最终呈现门，保留无原异常/路径/实际 format 值泄漏的 oracle。

## 4. 精确错误链与 owner 前置

| 路径/接口                                                                                                                                                         | 本合同的精确职责与授权边界                                                                                                                                                                                                                                                                      |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `apps/desktop/src/main/jsonl.ts`                                                                                                                                  | **I05 尚未生效交接的既有路径**。只提议现 reader 的只读 raw payloadByteLength metadata，不改 parser 语义。须 I05 精确 offer、T01 接受、独立核验、root 登记有效后才可施工；engine.ts 写权不能外推，也不要求整 I05 先合并。当前不修改该文件。                                                      |
| `apps/desktop/src/main/engine.ts`                                                                                                                                 | T01 已有路径；未来在获批原字节接口及 canonical 合同上实现优先分派、profile/hash/长度同步核验、startup deferred/first-cause 与同 chunk terminal。不用私有双 parser 绕开前一门。                                                                                                                  |
| 唯一 canonical / contracts index 的严格 schema、safe-error helper、taskUpdateSchema                                                                               | T01 责任内仍须 root 批准精确 local-startup-safe 定义及有限新码后才改。保留普通 error2/error3，不能由 helper 接纳任意 code/params。预期 hash 来自 main 同 build 可信资源 bytes，不是 child 自报；未交 resources 不施工。                                                                         |
| `apps/desktop/src/main/task-service.ts`                                                                                                                           | **I06** 必要接线意向：现 connection 入口的 validateV2(error)、recovery/catch、connectionUpdate 等门按 main 私有来源/profile选择批准分支。never-ready 经真实启动 catch，ready 后事件绑定实际 generation/session；保留真实 Job/claim/receipt 对账，无写入重放。仅共享 helper 改动不证明这层已通。 |
| `apps/desktop/src/main/index.ts`                                                                                                                                  | **I06** 必要接线意向：可信 factory 内部 profile 与命名 handler 的初始 catch/最终 SafeError 投影；原 sender/mainFrame/可信文档校验不减，不新增 generic invoke，不让 renderer 指定 profile。                                                                                                      |
| `apps/desktop/src/preload/index.ts`、`apps/desktop/src/renderer/src/App.tsx`、`apps/desktop/src/renderer/src/env.d.ts`、`apps/desktop/src/renderer/src/style.css` | I06 其余四路径先核共享严格类型重建及最终 DTO/显示是否足够；足够则不机械改源文件。preload 命名调用/onTaskUpdate、App health/task 入口仍须在最终同版实际链路核验，不以“没有源码改动”省略证据。任何确需改动仍由原 owner 精确接线。                                                                 |
| `apps/desktop/src/renderer/src/task-presentation.ts` 的 `explainError` / `safeError`                                                                              | **I05 尚未生效交接的既有路径**，不是 I06 App 写权或已列六路径的附带授权。新固定文案/有限错误呈现会经过此门，须同样完成 I05 offer、T01 接受、独立核验、root 登记后才可施工。不能在 App 中复制另一套解释器或旁路 safeError 伪称前门完成。                                                         |

实际链为：受信 producer 原单行 bytes → 原 reader 严格解析及只读原长 metadata → engine 优先验证/first-cause → startup promise 的真实 catch 或已 ready 的绑定事件 → task-service / main-index 的各自严格 SafeError 门 → 命名 bridge / 共享 taskUpdate 过滤 → App 实际入口 / task-presentation 固定文案。初次失败和已 ready 事件是各自真实路径，不强造一条携带旧 session 的 disconnected。新 local-safe 错误仅在来源/profile 可认证的有限入口接受，renderer 不提供这些认证标志。

I06 两条 main 路径的接线意向不等于授权已完成；I05 两个精确路径也仍待双实体交接、独立核验及 root 生效。无需把整 I05/I06 或其他未交方法合并作为前置；也不能以本页扩大 protocol/resources/build/锁/旧测试/CI 权限。

## 5. 关闭条件与证据边界

本页补全 P2-RAW-1024 的原长来源、LF/CR 口径、预算时机、完整字节 fixture 计划和两个待交 I05 路径；原 R1–R4 继续按 r2 闭合。是否接受本补充由独立设计复核与 root 统一，不自行标记原字节接口已实现或移交已生效。

后续只有实际路径生效、精确 canonical/new local-safe 审批、同候选真实源代码/启动/清理/错误全链验证及原指定双审/CI/正常合并等门完成，才能分别登记相应能力；不由文档通过登记业务3-ready或发布完成。真实 no-window Python 子进程和 Node 监督计划保留，本次没有运行产品、测试、GUI或桌面操作。
