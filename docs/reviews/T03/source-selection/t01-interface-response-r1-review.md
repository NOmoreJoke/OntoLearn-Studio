# T03 对 T01 来源合同 r1 答复的独立设计复核

2026-10-21（Asia/Shanghai）。结论：**通过，限于“方向接受、六缺口冻结前不可装配”的设计答复**；下述一处确认语义意见已关闭，无未处置问题。没有批准运行、公共协议、依赖消费或恢复原 blocked Goal。

## 固定输入与操作范围

- 首读主稿：`docs/iterations/T03/source-selection/t01-interface-response-r1.md`，SHA-256 `f1cffb280f2cef9fc896b65df993fd7c9648959955da028e608d4ae2ea7da1b2`。意见修订后的最终复核 SHA 见下文。
- T01 依据：固定 `f51dd38dbdfd2fbb1b9923efee666a19d5b415cc` 的 `owner-interface-responses-r1.md` §2；全文 SHA 独立核对为 `0f3ab7e539b9b69c6a602f4eabd089936a37afd9d842fa836748793031df6768`，与主稿一致。只接受本节设计，不消费该提交运行实现。
- 对照固定 broker `8c904b57b7c5aac7b2b19273e679e7e36304dd1c`、S1 parser/plan `30319412daf8ae4745987babf7bbed93c53b6b42` 的静态接口，以及批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3` schema、main envelope、coordinator/worker 输入路径。
- 仅 git/文本读取和哈希核对；未 import 或运行产品，未运行测试、构建、GUI、模型或网络操作；未修改主稿、实现、测试、依赖、共享文件或 Goal。仅新增本报告。既有完整操作规则继续适用。

## 六个缺口核对

1. **帧预算准确。** 65536 原始字节的 base64 长度为 `4 × ceil(65536/3) = 87384`；128 个完整原始块覆盖 8388608 字节。批准 schema 的 `maxFrameBytes` 为 1–262144；main 检查实际协商上限下的完整 JSON 请求字节，coordinator 也独立检查发往 worker 的 envelope。接受分块方向不保证该 profile 可用于所有协商值，主稿要求 begin 前拒绝/明确小块 profile 及重定块数是必要缺口，没有擅自扩大 MAX_FRAME。
2. **inspection/配置引用分离准确。** 固定 broker 的 inspection 不生成 proof，configure 入口换代并在成功时换 selectionId，即使内容与选项相同也不能静默复用旧绑定引用。重新封存或可信 owner 明确签发新引用是待决策略；未要求重复拷贝同 hash 数据。
3. **表摘要缺口准确。** 固定 parser 接 bytes；Table 保存 source_hash/sheet、顺序 fields/rows 和 cell.text/kind。现有 Preview 的三项哈希不等于完整有序表及 encoding/sheet 摘要。主稿要求版本化规范、全部表内容与明确选项、跨语言 fixture，且未复制第二 schema，范围合理。
4. **资源/授权区分准确。** broker 两槽只限制实际未终态 picker/FS 操作，不限制上传块、已返回字节、持久 blob、并发 Job 或 pin。对象身份不是可序列化上传授权；归属、容量、TTL、seal、受理/pin/回收及重启收尾需要 canonical/运行 owner 冻结。主稿没有把项目名或 sourceRef 当成用户授权。
5. **worker 与大结果缺口真实。** 批准 coordinator 在实际 Job 路径启动 worker，只写一次 parameters 后关闭 stdin；worker 读取首帧。因此当前并未具备分块输入接线。主稿明确 worker 责任尚未交接，并保留内存/超时/取消、完整结果和分页/分块合同，未越权采用未批准代码或截断正式计划。
6. **复验到提交的边界准确。** readForCommit 是当次源字节复验，不是用户确认或 Store 提交；后续磁盘变化不能使 worker 改按路径读取。主稿要求封存快照、未受理前上下文失效拒绝、真实确认、Store 原子基线/冲突门及 operation/receipt 对账，保留了当前 broker/plan 不负责的真实集成缺口。

## P3：将“已确认快照”的 Job 明确限定为最终写入 Job

位置：主稿第11行，以及缺口5的后续合同范围。

“Job 仅消费已确认的封存快照”容易把 inspection/preview 的只读解析任务也纳入人类写入确认门。XLSX 必须先枚举、选表和解析，才能提供最终映射预览/确认；如果沿批准 Job→worker 路径承载这些只读阶段，笼统要求所有 Job 先获得最终写确认会形成循环。主稿整体已经区分 inspection 无 proof、确认在提交前，因此本项不阻断方向接受，但在对外冻结精确合同前应明确。

建议：第11行写为“最终映射写入 Job 仅消费经用户确认且绑定输入的封存快照”；缺口5明确 inspection/preview 的只读执行类型、可信授权、取消和结果归属也由 T01/worker 唯一 owner 冻结。seal 的字节完整性确认不能替代人类写入确认；本报告不自行指定新 capability、schema 或旁路 worker。

### 关闭复核

已全文读回修订主稿，最终 SHA-256 为 `7376353f6230d35a1fc931e096dab8310eae38de015f75a333e3998ec6df761b`。第11行已限定最终映射写入 Job；缺口5明确枚举/预览在人类写确认前按独立只读执行语义运行，实际 capability/授权/取消/结果由 T01/worker owner 冻结，不能以测试 Job 或伪造确认绕过。缺口4同步将受理/pin边界用于每个实际消费者，最终写入另绑确认；空文件与 EMPTY_SOURCE 的文字明确限于 CSV parser。原意见关闭，未引入新实现或公共协议授权。

## 验收边界

主稿列出的分块边界、小帧、错序/缺块/冲突重传/SHA、跨项目/代次、选表新代次链、pin/回收/受理竞态、完整大结果和历史/原子性检查是后续待合同冻结及实际执行的要求，不是已通过结果。没有发现无端扩大为整套 M0 串行前置，也没有把旧 32 FS 或 S1 包内证据拼接成端到端通过。原生 picker、实际多段传输、worker/parser/Store 联验、目标平台及指定双新审门继续保留。
