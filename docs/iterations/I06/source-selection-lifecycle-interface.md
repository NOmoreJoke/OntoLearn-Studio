# 来源选择 → 预览确认 → 正式Job：生命周期接口提案

2026-10-21。仅设计子任务，不注册产品能力、不采用未批准T03/T01实现、不运行测试或GUI。批准消费基线仍为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`；其中Job/operation生命周期可复用，mapping.commit仍design-only，不能因来源模块存在就说正式映射Job已可用。共同指南实核 `b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39`，根AGENTS实核 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`；T01十二共享+storage、T03构建四及其他未交路径不写。本文只给待T01/root正式冻结的生命周期选择，不代替根的字节传输细表。

## 1. 固定读取来源与现有满足项

历史读取为T03流程提交 `2f7a4daf7cd32408b4ea6e87b93f3298c0c2569e`，产品提交 `f2c7deb8139255bc11e44c5b4a958ecbdae6a373`。`design-and-handoff.md` SHA-256 `0007a137d6439cbdf67fda59377a68ecc6fa8301dbc51afe8758542a6c48cd7f`，`validation.json` SHA-256 `af83f8ee93c03a6f3ad064953e1f6d043cf02153a45a70488f4fbaf2b00fdb9a`；source-selection.ts在两提交为同一Git blob `7faaf7a1246ecf87f8bdf3561a171955251b0402`，validation记录源码SHA `25a340ce7d8e0f2f3cdd4659c06c0a5ae3139cb3b44fde7812b1e782122f2fa3`。当时只读其设计/验证记录与导出types/方法，旧29项记录保留历史。

当前新增读取固定产品 `8c904b57b7c5aac7b2b19273e679e7e36304dd1c` / 流程 `b86833dc40ae9f5e3b975e1e23c9af254d6ec431` 的完整design与validation，实核SHA分别为 `5ac818da2cc702e2899fb9f10fcc0f0bcdb8a1420b9bf1d71ccc199e055a66cc` 和 `8619d28e8ba9a9cacfbc9ffddae4c92821f6ecfc2b5f23986c3e694e1c12e30f`。新validation记录source-selection.ts SHA `700337e055974708fe848edf58187fe161c2af2a0feb908bd41241abfea9e989`，owner记录32项专属/662TS/1052Python通过及私有范围独立复核；root已报告独立读回，本子任务不重验原测试/日志、不读取或采用新实现。以上均未批准为实际依赖，也未证明真实parser枚举、transport、IPC、Job、Store或native链。

已声明的私有接口是：`TrustedPicker(signal):Promise<string|null>`；`openProject(projectId):SourceScope`；`pick(scope,encoding)`；`configure(scope,selectionId,SourceOptions)`；新固定设计中的 `readForInspection(scope,selectionId)` 返回main-only summary+bytes、无proof；`readForPreview(scope,selectionId):SourceSnapshot`；`readForCommit(scope,proof):{summary,bytes}`；cancel/closeProject/dispose。SourceScope有projectId/lifecycleId但按实际对象身份核验；SourceProof虽有sourceProof字符串，也必须是broker登记的**同一个对象**，不能序列化后再造。SourceSummary含selectionId/project/lifecycle/generation/format/encoding/sheet/byteLength/sha256；SourceSnapshot另外含main-only bytes/proof。

固定设计已涵盖可信picker返回绝对路径、摘要不带路径/文件名/内容、8MiB真实字节界、CSV枚举编码、XLSX显式sheet、重读SHA及有界文件/类型/读前后指纹、失效先于abort重入、同broker最多两个实际未settled操作。记录明确未验原生picker、正式IPC/解析/Job/Store/平台；这些不是本次消费可宣布通过的证据。

旧 f2c7/2f7a 的 XLSX 初次pick后sheet=null，readForPreview要求先有显式sheet，**不能用它取得首次xlsx_sheets枚举所需字节**。当前8c904/b868固定设计与validation已记录main-only `readForInspection` 在私有层实现，保留scope/selection/fingerprint/字节上限/abort/真实两槽，返回summary+bytes但不签发preview/commit proof。新候选已交付但仍待批准/实际接线验证，尚未验证真实parser的xlsx_sheets枚举；不把旧候选称为最终可用，也不把新增inspection私有方法称为完整XLSX链通过。

## 2. 建议的宿主权威与最小绑定账本

建议由I06受信main持有一个长期broker/宿主调度器，按可信项目打开创建scope；renderer不能传路径、原始bytes、SourceScope/SourceProof、picker回调或任意方法。摘要/不透明selectionId可经最终具名契约展示，但即使renderer回传相同UUID/代次，也只用于main查当前记录，不能成为权限。main调用前仍核sender/mainFrame/可信文档，Agent/模型不取得原生选择或确认权。

宿主的每份可确认预览至少绑定以下**概念身份**，字段名/公开DTO待唯一canonical冻结：

- main持有的实际scope对象、项目公开UUID、lifecycle与当前generation/selectionId；原proof对象留main，不进入wire/持久包。
- 实际原字节SHA/长度、format/encoding/sheet、不可变已seal snapshot的同源引用/实际SHA；不只绑定文件名或stat。
- 真实parser/实现版本、解析表摘要、规范mapping定义/变更计划摘要、domain base revision及实际依赖、预览完整Diff/身份。
- 用户实际看到并确认的preview身份、确认主体/用途、一次正式operation/Job身份与受信确认记录；重试/取消/重开有可对账状态。

这些必须由真实来源和main/受信服务产生，不让renderer上传一个“confirmed=true”或自报表摘要作为依据。T03 proof只证明选择/复验，**不等于**人类确认、domain revision、Job/operation授权、真实parser成功、模型外发grant。选择本地文件/上传本地engine不会把模型privacy从local改为minimal/project；即使将来模型要解释该表，也必须走其自身来源范围和外发预览确认，不从picker或Job确认继承。

## 3. 建议流程与正式Job的唯一输入

| 阶段               | 当前可复用项                                                                      | 尚需冻结/交付                                                                                                                                         |
| ------------------ | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| 首次选择           | broker.openProject/pick；CSV编码和main对象身份                                    | XLSX初次summary.sheet=null，仅表示已选文件，尚不能readForPreview                                                                                      |
| XLSX受限inspection | 8c904私有候选已实现main-only readForInspection返回summary+bytes、无proof          | 新方法已固定交付，仍待批准与真实parser/正式接线验证；T01仅以inspection用途受限lease交真实parser枚举xlsx_sheets，不做映射preview/确认/Job admit        |
| XLSX用户选sheet    | 用户从该实际来源的真实sheet列表明确选择，再configure                              | list须绑定实际source SHA/lifecycle；configure重读并换新generation/selectionId，源变或旧列表回调拒绝，不虚构sheet/空字符串绕关                         |
| 预览取源           | 配置真实sheet后才可readForPreview重读并签main私有bytes/proof；CSV沿原显式编码路径 | main固定自身字节副本/实际SHA；必须新建当前预览权威，不能用inspection结果替代                                                                          |
| seal与解析         | broker不提供这项；原Job基础可读取不可变输入                                       | 倾向T01单一canonical有界分块上传并seal实际同SHA immutable snapshot，真实parser只读该snapshot给表/映射摘要；inspection与正式预览用途分离，不另造协议   |
| 展示/确认          | 原可信frame/人类确认边界可复用                                                    | preview绑定全部上节身份，main仅对当前preview记录接受明确确认；inspection/proof/seal均不等于确认                                                       |
| 正式启动前复验     | readForCommit(scope,实际preview proof)返回本次复验字节副本                        | SHA/长度/真实sheet与编码仍对应正式预览/已seal同源snapshot，domain base/计划/确认仍有效；每个await及最终发送前复核；inspection lease不得用于admit      |
| 正式Job/提交       | 已批准job.create/job.get/job.cancel/operation.get及Store唯一提交/对账原则         | mapping真实capability、源snapshot引用/实际SHA进入完整计划/幂等指纹/确认及Job输入；Job仅取该已seal快照，**不按原path重新打开**；Store仍检真实base/冲突 |

根倾向的64KiB raw分块/每帧仍低于原上限可作为待冻结传输选择；本文不复制chunk/offset/base64/帧预算细表。8MiB不能塞单帧，原path不传engine。upload/seal引用如何跨session存活、如何项目授权/关闭/取消/过期/pin/回收，以及正式Job如何保留输入，均由T01同一canonical/Store合同给出；本提案不假定一个字符串blob hash就是可读/可提交权限。canonical的inspection用途lease不得用于admit，也不能因原字节SHA相同升级为正式预览或Job授权；底层内容去重不合并用途/生命周期权威。必须在真实sheet配置后的readForPreview取得新proof，并在readForCommit复验和全部计划/人类确认绑定通过后，使用正式用途的授权引用；具体同源引用关系由T01/root冻结。

预览可解析已seal快照A；确认后readForCommit复验磁盘字节B必须与A的实际SHA/长度及选项一致，然后正式Job消费A，无需为同字节再造一份来源权威。读取B成功后原文件仍可能再变；本流程承诺Job处理明确确认的不可变A，不承诺Job执行瞬间磁盘仍最新。若B已不同则必须撤销旧预览/确认，不能改用B悄悄沿用A的Diff。SHA相等也不能跨项目/lifecycle/选项/计划自动复用权限。

## 4. 必须显式处理的失效与竞态

| 触发点                            | 旧记录必须怎样失效                                                              | 易错边界/后续动作                                                                                                             |
| --------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| 重选开始、configure编码/sheet开始 | **先**撤销旧preview/确认/待发送启动资格，再调用异步picker/配置；更新main代次    | 字节SHA可能没变但解释语义已变，不能按SHA恢复旧预览；配置失败/busy也不回滚为旧选项。T03后发配置生效，宿主按同代次接结果        |
| 用户取消选择/配置/关闭项目        | 撤销当前source证明、UI预览及未发送启动资格，调用broker相应失效/abort            | 取消返回null不是“继续使用旧来源”；旧异步成功/失败/同步abort重入不能清掉或覆盖新选择                                           |
| 复验检测源变/删/变大/读错         | 当前proof、preview、确认全部失效；要求新选择/新预览/新确认                      | 不因后来恢复原字节而复活旧证明；broker无已批准实时watch接口，不能声称外部编辑瞬间UI已感知。明确提交前复验及观测窗口           |
| domain revision/实际依赖变化      | 原计划/preview/确认失效或按正式冲突规则拒绝                                     | 文件proof可能仍真实，但不能代替Store base。反过来，应用-only CAS不应伪造领域revision变化；真实计划用到的应用状态则按其CAS绑定 |
| upload/parse/readForCommit晚返回  | 只允许当前scope/selection/generation与当前preview承接；旧上传结果不安装为新选择 | 已seal旧snapshot可作为孤儿资源按T01策略回收，但不是可自动提交的旧授权；未seal输入不得拿来预览或提交                           |
| main发送Job前与取消交错           | 同一main调度边界串行查当前记录/确认并发出正式请求，已失效记录不发新请求         | 一旦请求已写入跨进程传输，不能声称取消选择保证零Job；进入创建/提交待对账，不盲重发                                            |
| Job创建/提交响应丢失              | 保留原operation/Job/计划指纹，先按原全局身份查询真实持久记录                    | 只有相同原计划的真实对账可认定已接纳/已提交；不能重新选择后复用旧确认换新输入，也不能用broker.cancel伪造Job cancelled终态     |
| Job已被正式接纳后重选/关页        | 撤销未来使用旧preview的资格；已接纳Job按原Job取消/提交边界处理                  | Job仍使用原被授权snapshot；若用户要取消须进入正式job.cancel/对账，已提交保留成功事实与历史，不能用文件选择取消抹掉            |

原生picker/FS的逻辑abort不等于实际结束。**两个真实在途操作，任一个abort但未settled都继续占槽**；不能清Set、立即换broker、renderer重挂或重复cancel来释放。建议同main broker跨普通页面重建及项目scope切换存活；如确需替换broker，宿主须保留旧未settled操作的全局接纳计数或等其真实终态，T03现导出没有drain/whenIdle保证，不能伪称已经排空。source host/FS槽位只覆盖这些实际操作，已settled后正确释放；上传/解析/Job的独立预算与取消由其owner定义，不能混成同一个“2 Job”配额。

TrustedPicker忽略signal时可持续占用槽位；I06宿主要按Electron真实可用API给出取消/父窗口销毁策略及事实，不能将Promise逻辑拒绝写成原生对话框已关闭。本任务不启动原生对话框。

## 5. 冷启动、普通页面恢复、同进程升级

- **冷启动/真正新main**：broker scope/proof/未确认预览不能持久恢复为权限，尚未创建Job的旧预览需重新选择/读取/确认；不从旧路径自动重开。已有正式Job则按持久Job/operation与pin住的源snapshot只读恢复和对账，不需要重开原文件，也不自动重放job.create。
- **普通renderer重建/刷新**：不等于新项目lifecycle。main保留单一broker/当前账本，UI只查询真实摘要/预览/Job状态；不自动pick/confirm/start，也不重建broker绕过两槽。旧frame失去受信身份；新UI若继续操作须仍是main当前记录和明确动作。
- **同进程项目替换、明确关闭/重开或受控DB/协议迁移**：先关闭旧scope/预览/未发送确认并abort旧操作，再按T01真实lease/任务/连接边界升级。相同项目UUID也必须新scope/lifecycle；新engine session对旧upload/snapshot handle的可用性须由T01明确重新验证，不能据同SHA假定仍授权。新项目/engine/同源canonical及实际ready/项目读取通过后才允许新选择和新确认；普通engine瞬断不擅自认定为项目替换。

若同进程更换EngineSupervisor对象，I06宿主及任何固定持有旧engine的服务须重建/安全重绑，不能只替换TaskService继续向旧engine上传。模型context/grant按其受控升级边界另失效；source proof、Job确认、模型grant各自处理，不拼成通用授权token。上述选择仍须T01/root确认，不将状态字段写着ready当运行通过。

## 6. 精确owner交付与路径责任

| owner / 路径                                                                              | 待交付内容与边界                                                                                                                                                                                                                                                  |
| ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T03 source-selection：`apps/desktop/src/main/mapping/source-selection.ts`                 | 固定broker公开接口/安全failure kind、实际两槽与abort终态边界；8c904新readForInspection私有实现已固定交付但待批准/实际接线，仍明确无preview/commit proof并保留全部来源检查；本提案不改模块或采用其工作树后续改动。若宿主确需drain接口，另提精确变更，不猜已有方法  |
| I06 main：`apps/desktop/src/main/index.ts`、`task-service.ts`                             | 可信picker/项目scope与升级回调、实际engine服务生命周期及明确Job对账交接；不因来源选择改写普通renderer恢复语义。可候选新增 `apps/desktop/src/main/mapping/source-selection-service.ts` 持有main账本，但须root登记精确owner，当前未授权实施                         |
| I06具名bridge/UI：`apps/desktop/src/preload/index.ts`、`renderer/src/env.d.ts`、`App.tsx` | 只接最终canonical已冻结具名选择/配置/预览/确认/状态/取消；renderer不传path/proof/bytes，不允许旧回调覆盖新选择。style.css仅实际UI布局需要时改，不默认有diff                                                                                                       |
| T01 canonical7、`main/engine.ts`                                                          | 单一摘要/安全错误/分块上传/seal/preview确认/Job输入引用合同，inspection用途lease仅供枚举、不得admit；真实registryHash与bootstrap/业务session；不向renderer开放通用RPC，不将SourceFailure内部字符串当已批准公共错误                                                |
| T01 `storage.py`、`job_store.py`、`coordinator.py`及已交Python adapter/`__main__.py`      | immutable source snapshot的真实权限/寿命/pin、预览和实际确认/计划/base/全局operation绑定、跨kind/重试/取消与Job-ready；不从main另开第二Store writer                                                                                                               |
| 真实parser/映射消费者：root协调T03及当前实际owner                                         | 本次只知需交parser版本、实际表摘要/规范映射及从sealed snapshot读取；路径/导出尚未由本任务确认，不猜SQL/API或宣称已集成。若正式worker须改 `packages/engine/src/ontolearn_engine/worker.py`，该路径仍属原owner，需精确代改/交接，不从T01十二文件或T03构建四推导写权 |

T03构建四是另一交接，不因本文变为source broker或worker授权；protocol reader/resources/旧测试/CI均不自动扩权。根负责字节传输细表和最终合同集成，本文件不再造schema或另一份上传协议。

## 7. 必要验证与待授权新测试提案

以下均未创建、未运行、未获写权；原测试不改，不重复旧e2c回归证明新链。根先逐路径登记owner，最终只以获批同候选真实来源记录结论。

| 提议精确路径                                                                          | 必验生命周期                                                                                                                                                                                                                                                           |
| ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/unit/i06-source-selection-lifecycle.test.ts`（拟I06）                          | main实际scope/proof对象与当前ledger绑定；伪造同值对象/跨项目/跨broker拒绝；重选/configure/cancel/close先失效、旧成功/失败/abort重入不覆盖新代次；字节相同但encoding/sheet改变也拒绝旧preview；初次sheet=null不能readForPreview，inspection无proof且不能绕过真实选sheet |
| `tests/unit/i06-source-selection-job-binding.test.ts`（拟I06与T01固定真实fixture）    | preview解析与Job只用同一个已seal实际SHA快照；readForCommit源变拒绝；domain base/计划/表摘要/人类确认/operation不一致拒绝；最终发送前取消、发送后丢响应对账、正式Job取消与已提交事实区分；模型仍local且无外发grant；inspection lease即使同SHA也不得admit                |
| `tests/i06-main-platform/source-selection-lifecycle-probe.mjs`（拟本线隔离平台owner） | 真实可信picker与CSV/XLSX/显式编码/sheet→预览→确认→实际Job/Store；两个操作abort未settled仍busy且不能靠页面/项目重开绕过；原生dialog是否实际结束单列；同进程与冷重启只读对账，无原path重开/自动确认/自动重发                                                             |

两槽负例必须有真实未settled的host/FS操作证据，而非仅看UI busy或Promise标签；全链需要T01受信adapter/真实parser/Job的完整输入和持久结果，不能用mock Job成功或假seal receipt替代。实际传输/帧限/坏块/seal hash等由根字节合同与T01测试负责，这里只断言它们的输出引用在正确lifecycle被消费或拒绝，不复制细表。

当前可执行结论：保留T03私有broker事实，先由T01/root冻结源snapshot、确认、Job接纳/取消分界及宿主scope合同，再由各owner按精确路径接线。本文不是原生picker、正式映射Job、Store写入或首版通过。
