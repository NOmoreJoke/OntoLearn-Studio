# I05 真实物料、单次计算捕获与完整只读恢复

2026-10-22。本窗口交付三个内部组件：有界 data-only producer/consumer U/D codec、唯一原计算发生点捕获、同一严格 decoder 生成完整只读视图。它们为后续真实 Job/selected 链提供组件，不认证 producer 来源，也不代替 Store、worker、准入、H 租期或父 I05 验收。

## 固定输入与候选

- 独立树：`.worktrees/I05-formal-profile-integration`；分支 `feature/I05-formal-profile-integration`。
- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 135 项逐原 Git 字节 adoption：`e4460763890cf9550f359395df83260d75fe2e0a`；根已独立核同 126 项实际差异及 9 项与 base 相同。
- 最终修复产品候选：`6c1eec41091a997f898cb448bfc7d4000c154307`，完整139/current=Git清单为 `candidate-6c1eec4.json`。
- 首个冻结产品候选：`f677d8a3a642ef7ac7bf389218d43564762bcd9a`。完整受控 139 项见 `docs/reviews/I05/profile-production-fullview/candidate-f677d8a.json`，其中 130 项继承只读保持原 SHA；相对 base 产品实际差异 130 项，另 9 项同 base。四个新增路径已纳入，不把九 writer 当完整工程。
- 原授权、135 清单、最新 AGENTS/common 原文在过程前缀 `inputs/*.raw`；新树 AGENTS 保留 base 字节，最新外部规则全文读回而不覆盖。原 restore 树、160 路径、44 最终过程原件及归档不写入。
- resources 只采用明确批准的原 3ef 私有 `semantic_identity(profile)`；全局 i04 IMPLEMENTATION、manifest、LIMITS 不变，不能据此声称正式 per-capability 注册完成。

所有本轮实现仅改五个继承 writer 和四个新增 writer。T01 Store/canonical/coordinator/worker、T05 七机制及 16c、restore_budget、probe/samples、T03 依赖/锁/build/CI、selected/scope 全部只读。

## 实际接口与数据来源

`prepare_profile_material` 接收原 Turtle text 或 exact ordered tuple 三元组，以及原 typed RuleSpec、disabled tuple 和 source reference/revision。输入 UTF8、source occurrence、raw definitions 与 flat typed definition wrapper 都在计算前固定。保留 TermInput 五字段、SourceRecord 四字段、None/空串、语言原拼写、原顺序、比较/heads/disabled/revision/digest/policy。producer parser identity 必须等于实际原 parser 与固定版本。codec 不创建 PV，不执行 matcher/compile/evaluate，不从图 set/N3 重建原文，也不打开路径。

consumer `prepare_selected_material` / `decode_selected_material` 保存 assertedRecords 与 ontologyRecords 两层各自 domain/content/parser/source；层可 Turtle 或 structured，可明确空、混型。两层 U 的 input/source 分别最多 8MiB，不能借 producer 输入填图。consumer D 只包现有 query `{text,references?}` 或 constraint `{turtle,enabled,references?}`；保留可选字段缺省状态，不执行 query/SHACL，不冒充 T01 canonical。consumer parser identity 是待真实 owner 认证的数据。

`execute_admitted_profile_job` 只调用原 `_execute_profile` 主体一次。实际 `_profile_definitions` 返回点捕获 ordered `(ordinal,spec)`，原 disabled 校验后捕获原 tuple，`_profile_catalog` 返回点捕获实际 Catalog；每个真实 ProfileLimits 创建后、Budget/compile 前保留同一对象。没有第二次 divmod、reason 或从保存 JSON 反推 allocation。

完成同次原 parser/core/projection/rows 后发布唯一 `ProfileComputation`：material、native_result、实际 definitions/Catalog、原 allocation、payload/rows/source/definitions/Catalog bytes、旧四键 wire 与 C 收据。外层 frozen record 中的 native_result/wire 仍是原 native 容器，只有新恢复接口承诺完整深层只读。记录名不授予真实 Job、origin、H 或 formal authority。

旧 reason/execute facade 保持原 wire/错误及 legacy 分支。旧 capture 测试改用新实际 producer API，原输入和断言保留；调用 instrumentation 只观察真实 core，不提供替身结果、L 或 expected。

## 完整恢复及容器语义

`restore_profile_result` 和旧 `restore_profile_batches` 共享 `_restore_operation` / `_restore`，一次 strict decoder、每原 child 一次 `check_firing_batch`。原 rows 逐原 bytes 校验。新视图直接来自仍可达的完整 native 与已验证外层字段，不从旧 RestoredChild 或 allocation 补造，不重跑 reason/matcher/PV。

完整外 7 字段为 format、implementation、reasoning、inputDigest、inputDigestDomain、sourceDigest、definitionsDigest。reasoning 15 字段保留 rdfs/rules/warnings/evidence/rdfsEvidence/firingGroups/mechanismBatches/definitions/catalog/proofLeaves/termSources/graphBudget 及三个版本字段。child 11 字段保留 ruleId、definitionOrdinal、disabled、planDigest、batch、originalMatches、definitions、catalog、limits、budgetLimits、budgetUsage。

`ReadonlyObject.entries` 为原位置有序 tuple 对，`ReadonlySequence` 同时保存原 list/tuple 的 `native_kind` 和只读 items；因此 list 变视图是明确的容器身份变化。exact immutable canonical records 直接保留，数字有理数/负零、Calendar 原分量、SourceRecord、原 17L、None/bytes 不重建或归一化。旧 RestoredBatchSet 及其 flags/字段不变。

## 新费用与持有映射

C 沿批准合同，A=Q+D+24MiB≤48MiB，N 为原实际槽数（consumer data N=0）：traversal 128A+65536N；scan_copy 64A+65536N；hash 16A+65536N；scalar 16A+131072N；objects 8A+2048N+4096。固定八 stage 各有 ≤16J traversal 上界；overrides 只能降低，ledger 一次 begin。实际逐 helper/新循环/UTF8/hash/encoder/持有与作者自列未决点见 `producer-implementation/source-and-retention-map.md` 和 `new-loop-inventory.json`，独审必须逐源码裁决，作者报告不是通过证明。

R 的原预算文件完全只读。新 freeze 位于旧 safe_reason/safe_payload/encoded_payload 实际释放之后，在已有 A16 prepay 与固定 metadata 预留之后，先 reserve 普通 objects 2J、scalar 4J，再构造新容器。每 node 先 traversal1；dict 再付 keys 遍历和 16m+32 copy；sequence 付 12n+32 copy；canonical exact-class dispatch 先付固定 whitelist 长度。dict/sequence 使用已知长度 builder，转 tuple 后立即丢 builder；不使用无法说明容量增长的 append 链。

对象逻辑单位包括容器和槽：m-field dict 的构建峰值 ≤5m+2 加固定 wrapper，n-sequence 的 builder/tuple 或 tuple/wrapper 峰值 ≤max(2n+2,n+4)，每个字面 key/JSON delimiter/值有原 J 字节负担。空 tuple 共用不可变单例；八层 frame、外层 7-key 临时 dict、projection/result/receipt 元数据在 A16 固定 256N+256 objects 与 1024N+1024 scalar 中。完整 native schema 的容器深度不超过六，另以 depth8 拒绝意外增长。canonical leaf 内部已由原 decoder 校验，不再递归复制或重发 PV。

原 cap 余量采用保守上界，不能把数值当 RSS：原 object cap 8J+16M+2048N+4096（M=131072）；旧 safe 释放后加 view 的峰值粗界 5J+16M+固定上下文，低于原 cap。普通 scalar 的原 source/PV 宽界、原输入前像、固定上下文和新增 4J 均保持原 scalar cap 内。新增遍历及 exact-class 分派由 A16 及实际 traversal 账共同承担；需独立核实完整上界而非将一次 walk 当一次指令。

成功结果 `retention` 记录返回前全部 `ledger.live` 的保守预留上界，涵盖原 native/issuer/context 与新 view。某些 parse 临时对象在返回后会消失，保留其票是有意高估。结果接收者负责仍可达的 native/PV/view/rows；纯组件不签 H/lease。ledger cleanup 为本次逻辑账终止，不称物理释放。成功测试确认 live0 时新 PV 仍可达且合法，删除唯一返回结果后再检查 weakref registry 回收。

失败统一丢 projection、children、parse_usage、caps、inner_batches、retention、outcome、decoder 及其缓存；退出原 except/finally 后才抛有限新错误，原异常链不传出。专项注入 mid-freeze、last-child、projection/batch/result constructor、usage/peaks/live property 故障；检查实际 `_restore_operation` frame 新 locals 全 None、无半结果、无新 PV registry 残留。注入是受控故障，不冒 OS OOM。

## 运行证据与首失败

独立锁定 `.venv` / node_modules，缓存为本任务唯一临时目录，未借原树环境、升级锁或跑 GUI/native/e2e。安装命令及双流在 `environment/`。

- 六文件初版新专项 50 passed，相关回归 1024 passed；它们先于根三文件 fullview 变动，不能作为最终九文件同版证据。
- 根四文件专项首轮 238 passed；随后前票测试加强为精确 reserve 故障注入，单项通过。`root-runs/01-pytest`、`03-prepay` 完整保留；修复前票顺序后 `07-delta-tests` 同版242通过。
- 根 Ruff 首次 import 排序失败在 `02-ruff`，仅修测试 import，后续正常检查独立记录；未删首失败。
- 实际新 producer 原 83 例：78 success、4 原 ProfileExecutionFault、1 原缺输入未执行、0 新 MaterialFailure。round1/2 为 RULE_INPUT_BUDGET semanticInput，round3/4 为 WORK_LIMIT semanticWork；不补空规则或把四故障算成功。完整逐例原 allocation/bytes/hash/C receipt 在 `producer-implementation/11-producer83.stdout.txt`。
- 正常check两次首失败均原件保留：04为根过程run.py格式，05为author producer83.py格式；相应脚本已格式化。05实际TS1125及build通过，不能把整命令exit1记成功。独立 `06-verify-sources` exit0核12源。
- 首次独立预算审不通过，BR-F01为stage6三hash已执行而stage7才预扣4M，BR-F02为控制容器/ids/slots先分配后留票。完整首审和真实反例在 independent-budget/。来源/schema/受控Exception分工首审有限通过，整体仍待两项修复，详 independent-origin/。
- 6c1eec4仅修四writer：hash同额4M前移stage6；构造函数直接保原exact overrides tuple，不复制checked列表；begin在任何计数dict/stage list前核objects有效下限≥64，然后以64初始化live/peak；ids/slots现先reserve。新增objects0/63/64和低hash真实委托0调用反例，242专项通过，不扩cap/阶段。
- 最终同版 `09-final-npm-check` exit0/no timeout：ESLint/Prettier/类型检查、TS1125、build、Ruff及Python4887 passed/44 skipped；本轮四test writer无新增skip/xfail。完整双流保留，44跳过未算通过。
- `10-final-producer83` exit0，同版仍78成功/4原资源/1缺输入未执行；`11-final-verify-sources` exit0核12归档源。
- 同版38个真实fresh Python子进程（23旧batches API+15新fullview）均exit0/无timeout/stderr空，fresh issuer0，所有slot真实API观察与原L签名通过。完整stdin/stdout/stderr/supervisor及原allocator100资源失败另件全部进入 `root-runs/12-final-child-execs.zip`，zip CRC及逐原文件SHA核同，独立清单含153个原件。
- 两独立delta报告均绑定6c1eec4：预算 `independent-budget/delta-6c1eec4-report.md` 关闭BR-F01/02，独立54测试/原反例0委托；来源/schema/生命周期 `independent-origin/delta-6c1eec4-report.md` 19有界案例通过。它们不是指定外部双模型或父I05验收。首审和第一次自适应hash诊断均原样保留。
- 原树160+44共204路径逐当前=原a359 Git/原SHA，受控新树130只读逐原adoption，base AGENTS及12唯一归档/原型路径逐base/旧树核同。其他历史阶段原件不写入。封存脚本首个静态错误是把allocator100资源JSON当目录，保留失败说明，按目录过滤后将该原JSON也单独纳入zip；未修改测试或原失败。
- `14-staged-diff-check` 因原pytest首失败stdout五处原生行尾空格exit2；完整原件及引用它的diff stdout保持原字节。仅明确排除这两原始输出后 `15-preserved-raw-diff-check` exit0；九writer实际product diff独立 `16-product-diff-check` exit0。此保留例外不冒全路径diff检查绿色。

旧 145/23exec 仅原阶段证据，不充本次新通过。本轮新完整 view 增加所有九 PV 域、false/true/disabled/dummy/空 batch、多 child、多 head 的全字段签名、深只读和 17 个 R 域实际上界/差1，跨进程由真实自有 Python 子进程验证，未冒 T01 owned worker。

## 仍需真实供方的工作

T01 S1–S5/typed admission/Store/origin/worker/cache/reader/selection 租期及 T/S/H/Σ 监督尚未供应可采用源；T05 M1 新数学输入合同仅只读参考，未授权 runtime 采用，golden/oracle 绝不能供生产输入。完整89/40/M1、所有K selected、真实query/SHACL、双OS/真人/指定模型新审、CI和正常develop推送合并仍由后续窗口完成。本窗口不 push/PR/merge、不改 Goal 状态，也不把父 I05 标为完成。
