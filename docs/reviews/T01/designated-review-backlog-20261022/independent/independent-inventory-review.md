# T01 全阶段双审盘点与完整发审包独立静态审查

结论：**准备包静态可接收，未发现仍需阻断备包的错误。指定双模型审查尚未派发，实际任务为0；实现、运行、父功能与生产验收均不因此通过。** 早期授权缺件、旧执行账缺口、未验运行等事实继续保留。报告只审盘点、身份、范围和发审输入，不是重新审查旧offer或全部产品实现。

## 范围与固定输入

独立审查者为 `/root/i05_resource_offer_independent`，未修改任何候选、旧报告、输入包或源码。本次只写 `/tmp/t01-dual-review-backlog-20261022/` 下独立报告与证据。原Goal blocked、damaged-input保护HOLD、whole H、owner/native与被拒SQLite/heap/OS线保持不变。

最初输入为该临时目录下 `build_inventory.py`、`backlog.json`、`backlog.md`；全文静态读取生成器并核其登记逻辑，未运行生成器作为独立证明。随后审查最终持久输入包：

`/Users/kyle/Documents/工作/知爻/本体/outputs/20261022_review_backlog/T01-complete-engineering`

基线为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。最终冻结身份：

| 输入 | bytes | SHA256 |
| --- | ---: | --- |
| backlog.json | 189018 | 47381bf0396fd07a8c6e8b1ec0fd6d6660129293fc4eebd0b0b041fc4598689d |
| backlog.md | 37762 | ad0781dd344605ad7c9aa83c0bb53a62b9196ccc6be158d877954b1c271c40eb |
| submission-index.json | 20414 | b292c93a634cf9259f5023c27e96b5287b35d71a21c63a80377f7ed5c87f6ea3 |
| README.md | 2695 | 1f6096b1c7da49395d68b364fa348c0651223b4e0ea3067ec37111c3fbcb9f01 |
| coverage/coverage.json | 5113270 | af6b79061d48d20d8372591e6e8e70f7e66494925b1f692f5898a398d3ca65de |
| coverage/coverage-summary.json | 1377 | 3cab5ee21717f811ab652fc0f46fd1e14aea368abcbe6cb68554a9c499c1346c |

18份prompt及其余元数据的最终逐件身份见独立 `independent-persistent-check.json` 的 `finalInputIdentities`。持久矩阵内 `/private/tmp` 是保留出处，README已有明确位置映射，不据此假称文件缺失。后续新独审、payload manifest和Git封存收据可追加；任何受审输入变化须重新绑定身份。

## 登记、来源与权限

47个阶段ID唯一，分组为E01–E13、C2-0–2、D-1–2、S1-0–3、P1–8、N01–N15、W01、FULL。六入口覆盖45个不同阶段，无重复冒领；余下N13是root政策依赖、FULL是原父范围未完成登记，不能为它们伪造独立可审产品。这不是遗漏两项实现。

核过18个product ref、各树保留过程ref和当前WIP描述，未发现仍存在错SHA或把adoption/文档commit冒充WIP产品commit。S1和producer分别是当前固定WIP包；其adoption HEAD仅作来源。E12的最后commit可能带累计50件而授权仅2路径，C2-2/D-2最后commit主要测试变化，但实现存在祖先，均不能把immediate delta误作完整候选或未来写权。

E01–E08原逐路径授权未定位，在 `backlog.json:968` 起相应writeBoundary、授权空值及缺口中明示。Git变化路径不等于授权，这是**仍存在的原证据缺口**，不妨碍只读审查，不授予后续修复权。E09以后与C2、dispatch、S1、producer已区分原owner、实际变化与明确授权/只读路径；后续源码修复仍由原唯一owner及新精确窗口处理。T01原owner维持 `01a15bba-0884-7401-b24f-f50c1fcf60aa`。

所有47阶段指定模型字段保持本地未检出可核证据的限定措辞，未宣称全应用历史从未发生任务。原内部审查、历史测试数字、root限定收件与指定双模型Pass分列；准备包12份task record实际ID/session/turn/settings/report均为null，status为prepared-not-dispatched。预期GLM-5.3/highest/yolo、M3.1-Flash/xhigh/bypassPermissions不冒充实际设置。P5未定位adapter单独完整实质内审：现存helper审查范围只到profile budget/material及对应测试，不能转移其Pass给adapter。

W01撤回patch仍是无产品提交，`backlog.md:53`保留原patch SHA `ffdde792d12ed63705dc715e005cf7574af261dbfdc6b3cd487c2c48712c5845`、未跑45golden、准备稿不可采用及由E09后继替代。S1、producer阶段失败/后继和费用账缺口没有被当前Pass抹掉；不能重建缺失旧账并称当时已验证。

## 精确覆盖与分别发审

矩阵采用每个历史product ref的完整base→ref产品/测试/配置改动集，排除docs、iteration-control、AGENTS；不是仅最后一commit的delta。18历史×7目标共126组，只有8组完整逐字节覆盖，包含自身：

| 历史 | 完整覆盖目标 |
| --- | --- |
| E11 | early-5de、host-a816 |
| E12 | host-a816 |
| E13 | C1-423b、C2-ab792、S1-current54 |
| C2-2 | C2-ab792 |
| D-2 | dispatch-7dfa |

这里“覆盖”仅指矩阵范围所有路径的存在性、bytes/SHA吻合；不证语义、原需求覆盖或运行。E01–E12的完整累计候选没有一个与当前C1完整52件全同。若只看各阶段自己的最后提交范围，E03的2路径、E07的2路径和E13的5路径在C1逐字节全同，不能把这个窄结论改成旧累计工程全同。

独立从Git原始blob抽取18个历史候选，并与C1/C2/dispatch三个目标比较；得到54组逐路径same/changed/missing集合，与交付矩阵全部一致。此前沟通所称51组为计数口误，实际脚本和本报告均为54组。当前几条边界：

- C1 product `423b7e4c799f188cf2ce6e8e7121893ce85624cd` 完整52件是首审主候选；不能仅审5件E13末提交。E11/E12→C1分别45/48、47/50相同，其余均须追旧失败、修正及变更，不能跳过。
- C2 product `ab792c494db09ada1f20d0a598c3e0c96c338992` 完整54件包含C1全部52件原字节；仍须完整审其独立证据模块/测试与验收。C2-0/1相对C2当前均52同、2改，保留失败修正追证。
- dispatch product `7dfa9c8008727d469935181fc20beebb5ba4419a` 对C1只有51/52相同：`apps/desktop/src/main/engine.ts`不同，另有自身模块/测试。D-1→D-2为51同、3改，不能借C1/C2或D-1结论关闭当前独立候选。
- S1当前54路径packet保留C1的52原字节及2件projection WIP；projection与其对象/资源门必须另审，adoption `3f5fe...`不是产品SHA。
- producer当前149路径packet对C1为46同、6改，变化为 `coordinator.py`、`job_store.py`、`project/domain_changesets.py`、`project/format3.py`、`project/transactions.py`、`storage.py`（均在 `packages/engine/src/ontolearn_engine/`）。须独立完整审149路径范围及其完整工程；不能拼C1共享文件或把adoption `b054b...`冒充产品SHA。
- N14是固定71件owner-offer文档候选 `79d63cc1f403ee857a3af2a98f8870db9a6a910d`，受审53件为 `dd972b79adf4d378636a7d41a6b0e3e08c0d5ca1`，无WIP/产品候选。可限定文档审通过，不能传播为实现/父功能Pass。

最新prompt明确当前主候选完整审源码、工具、测试与原验收；历史完整树用于必要失败/修正/变更追证。无需机械重读重跑全部被替代版本，仍独立保留的当前分支分别完整发审。该限定不降低原57P0、C–G、PRD10–12、真实Store/Job/Host/来源/Agent/全恢复、两个OS/真人、CI/PR/develop/远端等父范围。

## 本轮发现及修复保留

以下均是本轮首次发现后由主线修复，审查者没有代修候选。最终无未关闭P1/P2备包问题。

| 编号/严重度 | 首轮问题、反例与影响 | 最终核验 |
| --- | --- | --- |
| INV-01 / P2 | prompt把H对象计数写成8MiB/16MiB，无法约束对象数量，会错误改写验收 | 全18prompt含每actor≤8388608对象、同库active/retired/failed/unknown加parent≤16777216对象；scalar字节另列。主prompt:15，关闭 |
| INV-02 / P2 | N14套用运行不足必不通过，会使合法纯文档范围无法通过 | N14 prompt:7、15固定文档ref/71件与允许限定文档Pass，父/运行另记未验；关闭 |
| INV-03 / P2 | Git导出目录被称为可直接核branch/HEAD的工程，N14又套WIP描述；在导出目录运行git会128且可错认来源 | 所有prompt:3明确无.git、原sourceTree/ref追源、WIP不伪造commit；N14无WIP。实际抽核导出目录git身份返回128，符合新描述；关闭 |
| INV-04 / P2 | 原owner/write surface泛化，会把commit delta误当写授权 | 明确原owner、逐路径授权与只读表；E01–08未知保持未知；关闭“冒授权”缺陷，历史缺件仍保留 |
| INV-05 / P3 | W01 patch SHA文本中分裂/错拼 | 最终backlog.md:53为完整ffdde792…，与原件核同；关闭 |
| INV-06 / P2 | 无精确覆盖矩阵时按阶段名批量继承Pass/拼互斥共享文件 | 126组矩阵完整保留；54组由本审独立Git结果核同；6逻辑入口分离；关闭 |
| INV-07 / P3 | 新备包文档格式检查首轮2文件不符 | 主线40件文档check首exit1保原双流（backlog.md、index），write0、末check0；本审读日志与argv，不冒称亲自运行formatter；关闭 |

冻结后不得仅修改计数或路径而维持旧manifest身份。实际模型任务仍0、同版设置未读回、WIP docs-only Git封存收据尚待追加，均是明确的派发前后手续，不是已取得证据。本审不替主线生成产品commit。

## 实际静态核验及边界

实际执行普通Git `show`/`diff`/`rev-parse`等只读身份和blob检查；Python标准库JSON、hashlib、pathlib与tarfile字节核验。没有运行主线inventory生成器作为独立证明。独立提取脚本完整结束exit0；缺失路径的Git show非零被捕获并按missing记录，不把这些子命令称全成功。固定导出目录无.git的128结果同样是预期观察。

持久包再次逐件重读：20工程、16793源文件、340464684源bytes；476证据文件；104控制文件。文件集、bytes/SHA均无差异。原临时包与持久包分别做过独立核验；最终18prompt关键边界检查全部通过，47→45+2映射与12任务空值全部吻合。

两WIP完整tar.gz实际内部逐件核对：S1含820个project文件、producer含901个project文件，另各含原source-manifest.json；所有文件集/bytes/SHA和嵌入manifest均与对应完整工程一致。归档身份分别4188913B/`6aa013bf525c0631f80280c16df76c4b945d9e25785e122bab2fa4930094ee14`、4560386B/`57d70e5fc9ab2ec92cf5cb0b9af6c714a1cb38de56b3d6845ee05aa8e4386080`。首个归档检查小脚本曾错误把独立metadata也套project前缀，产生“anifest.json”伪差异；读真实成员后修正检查器，未改归档，最终断言通过。

独立小证据：

- `independent-inventory-check.json`：148112B，SHA256 `ed378d9aa26a5030c5a30297354a0339091f1f69aa1f890bcb76aa513495f831`；直接Git身份与逐路径覆盖结果，绑定当时188982B backlog，不冒充最终排版版。
- `independent-submission-check.json`：4521B，SHA256 `0ed61123ffdebc6bb795e814ca6eef831398a406eb82c0d87f2ab7d32cf2c4d2`；原临时提交包逐件核验。
- `independent-persistent-check.json`：37959B，SHA256 `6b65b02b2874885eed5f0b94156bdaafdf0307df6365ae1eb7d2129fe6c6ff15`；最终持久输入身份、逐件核验、54组矩阵核同、18prompt/12task/47阶段核验、归档核验及读到的formatter结果。

未执行产品imports、测试、build、依赖安装、DB/SQL/native、业务child、GUI、网络或指定模型。未逐个解审476证据内全部嵌套ZIP的每一member；旧运行数字只作为原报告记载与证据关联，不独立重跑背书。未测性能、whole-H物理资源、两个OS/真人或生产链路。此准备包静态接收不关闭这些门，也不恢复原blocked Goal。
