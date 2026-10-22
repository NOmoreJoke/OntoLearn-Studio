# T02-S1 round-1 冻结范围与证据入口

2026-10-22。仅总控授权的双提示、输入与历史索引准备；尚无本线外审lease、真实指定任务或通过结论。原产品与父Goal不变，不将准备提交当新产品候选。

## 三个固定身份

- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- product：`49321221733ea927484647352e05e7d833cebc86`。
- 原证据process：`d597b3c00980652042163d250c875d660d4d371e`。
- 原树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-ontology`；分支 `feature/weekly-t02-ontology`。

`input-manifest.json` 列出base→原process全部58个tracked变更：19个产品/测试/fixture、5个独立headless harness文件和其余流程证据；另有10个未变批准依赖/PRD/配置引用、3个保护未暂存项和5份操作政策来源。没有从中挑选UI或若干阶段拼接替代完整S1审查。后续typed ChangeSet十文档仅为已冻结方案背景，无产品实施或T01 runtime采用。

审查者必须核19项产品在product、process和实际review树相同，并读完整base→process变化/原S1全部证据。此round-1只追加流程文件；最终准备manifest将固定本轮提示/输入的精确docs ref及哈希。任何新隔离工作区须单独记录根批准映射、base/product/input hash和报告实际输出位置，不能改写原提示或伪称新树已经存在。

## 可审有界能力与原父缺口

完整S1包括不可变实体/事实编辑、全RDF与metadata Diff、复制/引用删除影响、旧project/revision/content守卫；批准Store2只读完整RDF来源证明、原ID/归属/人工覆盖/墓碑/全部重叠支持；独立表格/类树/局部图页面、多语言/多行/迟到/跨项目/失败状态；所有专属测试、固定G-base/Turtle正反样本与UI harness。

实际本体可保存/正式产品入口不在当前实现中：T01可信完整domain/metadata与当前scope、canonical/named桥/真实项目会话、人类确认、唯一原子commit/receipt/undo；I05批准Turtle/模板/支持检查与完整往返；I06 App/bridge/生命周期；T08真实草稿/模型、完整FR200–204/附录C/F/G/12.1/12.4、目标双平台/真人和父发布仍待。不能用S1通过改写为这些能力通过，也不能把这些既知父缺口误称本轮已实现。

## 原验证索引

| 证据 | 固定归属与实际结果 | 本轮处理 |
| --- | --- | --- |
| `../verification-c3.json` | C3来源专项13；完整check exit0，633TS/1091Py，本线39Python | 只读原件/hash，不复跑 |
| `../verification-c2.json` | C2完整check633TS/1078Py、本线26Python/3TS；11项真实headless合成callback探针 | 页面/harness未变，有据沿用；不称C3新运行或正式IPC/Store |
| `../verification.json` | C1历史check633TS/1075Py；sources-first12归档源；原失败 | 保留历史身份，不混当最新结果 |
| `../independent-review-c1.md` | C1不通过，多行input丢换行；此前四项问题已独立关闭 | 原件不改写，处置见历史索引 |
| `../independent-review-c2.md`、`../independent-review-c3.md` | 各固定候选内审通过，C3有非阻断文档指针意见并已读回 | 不代指定模型结论 |
| `original-log-index.json` | 32份被原索引引用的日志逐项路径/bytes/hash及候选索引 | 首失败全部保留；本轮只读 |
| `../evidence-archive/archive-index.json`、manifest/readback/git-readback/独审 | Git封存41日志、2当前C2截图、4索引+内嵌清单共48成员；548417B；SHA `43d9e20533885828a03c34392e8ae42ada23663c1cc338986c795c236f2a6b86`；实际Git恢复读回已记录 | 原C1两图不可恢复，只有原hash，明确缺口，不重造、不拿C2替代 |

本候选没有依赖/锁/打包配置改动，不需要为本轮重做无变化package；没有新增包内、Electron/e2e/native/HMR、Win/macOS安装、真实模型或生产证据。正式双审、push/PR/CI/正常合并/远端门均尚未通过。

## 启动与报告门

两份独立完整提示为 `zcode-glm53-input.md` 和 `minimax-m31flash-input.md`。对应GLM-5.3/max/yolo及M3.1-Flash/xhigh/bypassPermissions，均须全新真实任务、同base/product完整范围、逐任务实际provider/model/思考/权限读回，不互传本轮意见。只写各自 `zcode-glm53.md`／`minimax-m31flash.md`，这些最终报告当前尚不存在。

T06是当前唯一后台入口恢复owner；T02只准备输入，等待总控独占lease，不自行启动协议服务、CLI、模型任务或GUI。后台支持方式以root `T06-supported-background-external-review-window.md` 为准；昨日短时GUI答复不能沿用今天。真实taskID、正文接收、设置读回、前后source hash和完整终态须实际产生后记录，不能根据草稿或文件名预填。

默认静态审查与原证据读回。没有变化不复测；确需具体独立产品复现时，先给未验原因/精确命令和隔离需求，待root另授，不能自行改测试或执行原生/界面探针。完全访问权限不改变只读审查职责。

## 准备期间操作来源更新补充

初次冻结后台窗口为4792B/SHA `5fd7ef28089c6dde7efffaadaf1adca77c249f4e76670d8a9b53a28db7085433`；root随后在原文件插入诊断纠正，实际全文读回5446B/SHA `9a2d722dc86c64d66929cadd12631cc85042bdd820aba9ec76de882fa3ed5de4`。已从新文档扣除该新增段精确恢复旧全文，大小/hash与初读记录相同，保存在 `background-window-at-freeze.txt`，不宣称此前已有备份。

`input-manifest.json` 的operationalPolicies为捕获时快照，旧后台窗口hash按上述快照读回；绝对控制文件是可变路径，不能因其后来操作纠正就篡改原manifest或假称产品变化。具体绑定见 `policy-readback-update.json`。两份93c原提示保持原字节；未来启动须再核root最新政策与实际T02独占lease，必要追加独立hash附录，不继承旧GUI时段，也不把T06入口诊断/认证metadata当T02真实任务。
