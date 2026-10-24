# 业务3 ready / 启动诊断：独立设计复核

结论：受限 stdout 启动失败记录可复用现有 raw JSONL，不必放宽业务信封或修改 protocol.py。两层 ready、typed 分类、受信 opt-in 与无窗口真实子进程方向成立；实施前仍需关闭下面4项合同歧义。它们是设计/接线要求，不是已运行的新代码缺陷，也不批准新增公共码、canonical 或业务3-ready。

## 固定输入与范围

- 本树 HEAD：`b35cb4e21d375386775e5fc0431a8089a47195da`。
- 草案：`docs/iterations/T01/business3-ready-startup-contract-r1.md`，初读 SHA256 `ec4c0e5de98077759264464ef25013d80cba688d073e05f96d981e494699c40f`；后续追加完整四帧 JSON 示例及清理/退出边界后，全文重新读回并核验 SHA256 `f715934e6a8bfd130fbb0c01c62d33026b6f19f990bc4268eb66a0ee6a3673ed`。以下处置判断包含新增段，不把两个版本混成同一冻结输入。
- 实际只读核对：`__main__.py`、coordinator 的 classify / Constructor / serve、Python raw protocol、main/engine.ts 的 start / receive / finish、main/jsonl.ts、contracts index/v2/error catalog，以及 main/index.ts 和 task-service.ts 的错误接收门。没有读取未批准 I05 候选。
- 仅新增本报告；未改产品、测试、b35、旧报告或其他 owner 文件；没有运行产品、子进程、测试、GUI、打包或审查应用。

## 已支持的决定

1. raw JSONL 负责严格解码/重复键、Unicode、深度和帧限，decoded value 的业务 schema 在后续选择。新增一种精确本地启动记录不必改变 JSONL framing；必须在 main 的 decoded-value 分派处明确识别。
2. catalog 实际为 `STORAGE_BUSY/storage.busy/retryable=true`、`STORAGE_FAILURE/storage.failure/retryable=false`、`INTERNAL_ERROR/engine.internal/retryable=false`，草案三值正确。STORAGE_FAILURE 的原参数允许可选 operationId；startup 专用分支收窄为精确 `{}` 合法，不需要反向收窄普通业务错误。
3. PROJECT_FORMAT_UNSUPPORTED 仍是未注册提案，不能借 VERSION_INCOMPATIBLE 表达数据库格式，也不能通过异常文本或 stderr 识别。SQLite 分类读取受信 errorcode 的 primary code；未知异常保留 INTERNAL_ERROR/通用退出，不能猜成版本或存储失败。
4. Store3 失败拒 hello；Store3 已提交而 Job 第二层失败可以保留有效 Store3，但必须关闭实例/租约、不授 session，重开按明确层级恢复。裸 Store3 或没有 pending 不足以宣称 ready。
5. 实际子进程验证可用临时 SQLite、真实 Python stdio 和 Node/Vitest 监督，无需启动 Electron。源码机制验证不替代实际包、native、平台、双审和父验收。

## R1 — P2：冻结启动记录的优先分派与首错保留链

草案位置：§“精确记录与错误边界”、第9/24/26行。实际 main/engine.ts 的 receive 当前先尝试 notification，然后仅接受 validateV2(response)；startupFailure 会在这里被作为 invalid response 关闭，新增 schema 定义本身不会使记录进入预期错误路径。

需在实施合同写清：仅对当前受信 child/generation，且尚未 hello 成功的显式受信 profile，在业务 response/notification validator **之前**识别 startupFailure；精确 schema、1024B、expectedRegistryHash 和有限错误全部通过才接受一次。不能将该类型加入普通业务 response union、null-session 通配或 anomalies 容忍路径。合法记录同步 terminal + reader.stop，再处理待定启动/业务请求；同 chunk 后续 hello、notification、第二记录均不得继续分派。

首个已验证的启动错误应被锁定为该 generation 的启动失败原因，直接结束启动 promise，不依赖恰好存在 hello pending。当前 finish 主要拒 pending，child close / stdout end 另有通用 ENGINE_EXITED 路径；新实现须防 close、stdin error、startup timer 或 finally 的次生异常覆盖首错。没有合格记录时仍返回原通用失败，不从 child 退出来反推新格式码。

错误往上还经过 engine.finish 中的 validateV2(error)、contracts/index.safeError、taskUpdateSchema，以及 task-service.ts 的事件 validateV2(error) 与 main/index.ts 的 catch/safeError。应逐门固定“批准本地 startup-safe / 业务3”与旧2分支；只改 index.safeError 不足以通过 task-service 的先验拒绝。所需 I06 六共享改动仍须其 owner 精确接线，不因本设计自动授予。

最小独立 fixture 应比较入口记录、启动 promise 的最终 SafeError、close/timeout 后保留的同一首错及 bridge 最终投影；不能只断言进程关闭或 pending 清空。还须明确初始未 ready 失败经启动 promise 路径送达，不能假造一个带旧 engineSessionId 的 disconnected 事件。

## R2 — P2：默认2与 supportedFormats:[3] 的适用条件须一致

草案位置：第19/30/43行。固定 `{supportedFormats:[3]}` 与 opt-in Store3 相容，但默认生产2遇到实际格式3也会因“不支持格式”失败；若同样发送该记录，就会谎报该进程支持3。原2 error 合同又没有新格式码，不能靠当前 table 的“明确无法支持”笼统覆盖两个 profile。

建议选择最小边界并明确写出：PROJECT_FORMAT_UNSUPPORTED 启动记录仅由显式 Store3/profile3 发出，实际目标格式为3，固定支持列表[3]；默认2保持现有通用启动失败，不发送这一新码。若将来要求默认2也精确呈现，必须另行冻结 profile2 的受限本地诊断分支及[2]，不能沿用[3]或静默扩旧业务error2。

opt-in 来源只接受 main 受信配置/入口，不从 renderer 参数、child 报告或任意继承环境自动开启。未知/非法 profile 配置属于受控配置错误，不作为“数据库未来格式”的证据。3App/2Engine、2App/3Engine 的协商不兼容与 Store 格式不兼容分别给 oracle。

## R3 — P2：区分“失败前不 ready”与“ready 后失效”

草案第45行将 ready 后非法记录、双记录、失败记录后 hello 等并列为“统一无 ready”。其中 startupFailure 在合法 hello **之前**被处理，可以保证从不 ready；但合法 hello 已被接受并发出 ready 后，无法撤销已经发生的 ready 通知或业务提交。

应改成两组：

- 失败记录先到 / 假hash hello / 非法 hello：不发 ready，同 chunk 后续帧不消费。
- 已经合法 ready 后出现 startupFailure、错误 session/version 或重复 hello：立即使当前 session 失效，停止同 chunk 后续帧和新调用；允许实际已经发生的 ready→disconnected 历史，不覆盖之前的 accepted/committed。

当前 JsonlReader 在 frame callback 后检查 ended，finish 同步 stop 可阻止同 chunk 后续帧，这一机制可复用；不需要为了文档的“从未 ready”承诺去改未交接 raw reader 或缓冲未来未知数据。实际真假hash/session、限额和 terminal 更新继续在 promise 回调之前同步完成。

## R4 — P2：资源逐项清理与最终 schema / fixture 仍须冻结

草案已正确指出 serve 的构造后/主循环 try 前窗口。实际临时目录、JobStore、reconcile、allowed 配置、Coordinator、signal 和 thread 安装跨多个可能失败点；当前 finally 中 await coordinator.stop、store.close、signal.restore、temporary.cleanup 又是顺序调用，前一步抛错可能阻断后续释放。

需固定按资源取得情况执行的嵌套 finally / 独立受控清理：未取得的资源不清理；已取得的 store/lease、已安装 signal、自有 temp 和已启动 reader/worker 必须分别收尾。清理的次生异常不能替代原 typed 启动原因或产生原始 traceback；主动取消/信号/正常退出也不应被伪造成成功诊断或存储损坏。不能广泛结束用户进程，reader 的受控 fd/daemon 与旧 worker fence 仍按原边界处理。

新增末节已给出四类完整 JSON，且明确示例 hash 仅属于 b35、不是运行原件；原“完整 JSON 形状尚未给出”的缺口据此关闭。新增清理→单条记录→flush→非零退出和 EOF/close 不覆盖具体错误也支持 R1 的方向，但尚未取代 R1 的启动 promise / 上游多层错误门要求。

唯一 canonical 后续仍须接受精确 schema 与有限新码，冻结各字段上界、独立1024B检查、profile/expectedHash来源及起点/失败终点；针对未来实际 candidate 生成单行 UTF8 golden 并实算其 hash。排版后的 JSON 代码块是完整值示例，不能直接当逐行 JSONL 输出。资源加载尚未成功或不能取得可信hash时，继续固定 stderr+exit，绝不取 child 自报hash作为 expectedHash。这不要求现在修改受审实现，也不能把草案示例当作 schema 已可执行或运行已通过。

无窗口后续 fixture 至少逐点覆盖：JobStore 构造、对账、allowed 配置、Coordinator 构造、signal 安装、thread 启动及清理步骤失败；第一处真实原因保留、租约可重取、自有资源有界清理、无成功 hello。fixtures 只能在产品变更获准并冻结同版合同后实施，本报告未运行。

## 结论及边界

R1–R4 明确后可交唯一 canonical/main owner 统一具体实施合同；仍需新码接受、同版两端 fixture 和 I06 实际 bridge/UI 接线，不能登记业务3或安全启动诊断已运行通过。既有三个 catalog 值无需重命名，startup STORAGE_FAILURE 精确{}可保持。

本次无产品验证、无性能/容量/生产结论，不替代 root 固定b35审计、指定双审、CI、包内/native 或完整发布门。

## 修订复核：r2 对 R1–R4 的处置

本节仅追加，不改写上述初审记录。追加前本报告 SHA256 为 `d869a4542da0419d07ad673fa9d2b694f8db9291272e28c6124fb7d10dbf8628`。本次全文读取 `docs/iterations/T01/business3-ready-startup-contract-r2.md`，实际 SHA256 为 `e18a4ee8ec4fe32fe4d6df7b900f73aa4ee350723e8f1923109a7d3d925da281`，与提交审查值一致。r1 原件和初审结论仍保留为历史；本节给出当前设计处置结论。

结论：R1–R4 的设计要求均已关闭，未发现新的设计阻断或越权承诺。可以交 root / 唯一 canonical owner 独立统一合同；不等于新 schema 已获批准、I06 已接线或 runtime3 / ready 已完成。

| 原意见 | r2 实际处置 | 定点结论 |
| ------ | ----------- | -------- |
| R1 | §R1 明确 pre-hello 受信 profile3 优先分派、精确有限验证、同步 terminal / reader.stop、直接拒 startup promise 与 pending，并闭锁首错；登记 receive/finish、safe-error、taskUpdate、task-service 及最终 bridge 全链和 I06 责任。新格式码只提议进入 local-startup-safe，不扩普通业务 error2/error3。 | 设计关闭。来源/profile 依 main 私有状态而非 renderer 标志，且完整值跨各门的 oracle 已列入计划；实际接线仍待批准实施。 |
| R2 | §R2 将 `{supportedFormats:[3]}` 限于显式 main profile3 / target_format=3；默认2继续原通用失败，不发新码或[3]。协议协商与 Store 格式 typed 原因分开，禁止文本推断。 | 设计关闭。未将默认2能力虚报成支持3，也没有借 ValueError 兼容性扩大可分类来源。 |
| R3 | §R3 明确从未 ready 与 ready→disconnected 两组，后一组的 startupFailure 属无效帧；同步停止后续帧，不抹除 ready、accepted 或 committed 历史。 | 设计关闭。原 r1“统一无ready”已被明确替代，不再存在回溯撤销 ready 的承诺。 |
| R4 | §R4 从首个取得资源起登记，逐项有界 cleanup、失败继续其余释放，首错不被次生错误覆盖，也不伪造 settled；收尾尝试后才单条 flush / 非零退出。独立 schema、有限码、单行 UTF8 golden 与可信 hash 另留 canonical 批准。 | 设计关闭。完整 JSON 示例与实际单行 golden 的证据边界明确，未把一次诊断当资源清理成功或运行通过。 |

保留的实施门是合同中已准确登记的后续工作：root / canonical 接受新本地安全分支与严格 schema、受信 profile 入口、I06 逐门接线及同版无窗口实际链路验证。它们不是本轮需要补写全部实现才能关闭的设计意见，亦不能被本次关闭记录自动豁免。

本轮仅阅读 r2 并追加本报告；没有修改其他文档、产品或测试，没有运行产品、测试或 GUI。
