# I05 源码／包同输入合同独立 delta 复核

结论：**R1 closed、R2 closed、R3 closed；修订设计候选静态有限通过。** 本结论针对下列文档字节和受影响上下文，不表示新 probe、源码／包等效、资源 runtime、构建、S1 或生产已经通过。首审不通过原件保持原字节，不倒改其结论。

## 范围与输入身份

唯一树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-source-package-contract`，分支 `docs/I05-source-package-contract`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。本轮只读首版→修订的实际文档差异、逐项处置及所需命名固定源码；只新增本报告。没有重审旧组件算法或重跑产品／测试，没有导入产品／第三方库、运行CLI/native/GUI/DB/network/build/heap/OS计量或改Goal。

| 固定输入 | 字节 | SHA-256 |
| --- | ---: | --- |
| 主合同 `docs/iterations/I05/source-package-parity/contract.md` | 60953 | `d2cdc2e6017ad0257f30611d2928a60a116f4dc389cacdfc977c17efe13e2a23` |
| 首版 `inputs/contract.rc1.md.raw` | 54679 | `8cc6f527232d575028a5ba4e12912bc8f4a2b6eef350de929a296205d7c86cf1` |
| 首审 `independent-review.md` | 14650 | `a2807b1c166addaf308516043214aebfa45a187211d389cd92ed8a2a16da3b1a` |
| 修订 `static-import-closure.json` | 19811 | `861f4c79cee8ceb92acd656482bdcc2c095f1cc094e869595af7ab29f763af2a` |
| 首边表 `inputs/static-import-closure.initial.json.raw` | 20710 | `c6d04d3b3eb8e3a380fd55cf1165e3128038cab2ea0b914b2faf9a44c3b0ac9a` |
| `source-provenance.json` | 13626 | `e885e3a3fd5315fb84eef590668f4dfe8127edec50a2f9a7cd495f7b80331350` |
| `dispositions.md` | 3089 | `fcfbe345a9b9d9f6c5846bfb5adc18e23373abaafb1b3a67e527152885dbc4e6` |
| `validation-static.json` | 1291 | `0a352cceb4cb67dd5606599523e7897bd2b651c2ac655e593aac47f45cae9ac1` |
| `doc-process-history.json` | 3428 | `0e711a808608da64a0b21203240bd3c6ad96a8a7de4c2a4f6b9a6e1add245b85` |

AGENTS仍为受保护未暂存M，15852B／SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。供应产品仍固定 `6891a5842302859a531cf82767c5a482417bc274`，没有因修文档采用新的运行库、资源或产品。来源索引新增的历史方法仅为固定 `523c478d5f39671c4ac7c1ea6997e51d3047d58e` 的 semantic_probe.py，13873B／SHA `63f575302cf0796ab279d7a970cd8a9c62344fbc39128c7f60a3d204038a418d`。

## R1：scope 调用覆盖 · closed

主合同第46、57行增加独立 scope 族，明确以固定6891 `semantic_samples.scope_suite`（第449行起）及原Q/V字段作纯输入来源，只取asserted/ontology/legacy Rule/query/shapes文字和明确bool，不import该helper或带入其expected／已有result。静态对照该命名源码，确有subclass链、显式与推导target差异和实际约束输入，不是从oracle反造新图。

新增合同与实际 `semantic_scopes.py:234–326` 的两种签名及行为相符：asserted-only独立观测；fresh prepare(include_derived=True)真实reason一次；再用同次返回的 `reasoning_result`、`provenance["reasoningSource"]` 和原asserted/ontology/rules调用project，project不另reason。后续真实query／SHACL消费各自facts；完整facts/ontology/reasoning_result/provenance及selectedFacts、selectedRuleIds、warnings、derivedAxioms、view摘要均保留，不以同一末图替代两种范围。

缺／错source、缺result、非exact bool、unselected rules/result/source及facts混公理等原拒绝已列。第106行把只读hook明确扩到真实 `semantic.reason.__code__`，fresh prepare/project分stage分别计数，未实测次数标unknown；不读参数、不改返回、finally恢复和已有hook前置失败的限制保留。这样关闭了“模块被收集但scope分支未调用仍满足矩阵”的首审反例。

legacy五字段result不与profile `/2`／DAG `/3`混用，输入JSON不携带derived结果。组件provenance仍只比较输入一致性，不升级为producer／历史selected认证，不建formal selected/Store/Job。该修订使用已在22模块内的scope helper，不借此调build_request/execute_request或扩公共资源采用。

## R2：两条 import 边及解析政策 · closed

首126边保全；当前128边恰补production:291→semantic_execution、restore:10→semantic，两份文件及22模块的原bytes/SHA未变。

最终edgePolicy已收紧：空module的 `from . import child` 仅把显式child作为目标，不把隐含parent/self再造一条literal边；必要父包仍在module集合，其他静态明确module目标按声明规则记录。quality根第8、12行的definitions/planning是潜在**literal懒分支**，现分别列入 `unresolvedInternalLiteralTargets`，准确说明不在固定supplier module map且禁止调用／采用／收集；不再误称它们不存在或已经收集。resources的动态checker仍另外列资源闭包，不由AST“未见”推出不存在。

本独审用stdlib AST和固定6891 module map，按该明确政策重新计算：22模块、128边与附件逐项完全相同；未解析internal literal目标恰上述两条。这里核的是静态候选依赖证据，不是PyInstaller archive或真实导入结果，也没有扩大采用面。

## R3：两档 fresh 的调用合同 · closed

第81、83、85、94、102、172、188行同步为同一probe的三组exact argv：`[flag,"full-v1"]`、`[flag,"b1-semantic-1x-v1"]`、`[flag,"b1-semantic-10x-v1"]`。单flag、未知selector、额外args、`flag=value`、任意path/case及环境隐藏选择均拒。source／独立包／parent dispatch传同一完整argv，manifest固定三个有序set，header/terminal分selectedCaseSet、所选inventory与full inventory，子集fullSuiteCollectionComplete固定false；外部equivalence仅对同selector全项成立，不能合并子集充作full覆盖。

第215–219行固定两个B1测量set使用历史523方法的**四ontology版本**，而非笼统“18/180事实”或十ontology套件。本独审静态读原semantic_probe.py:229–259：先保原asserted给SHACL，graphBuild对每份equipment/001作CriticalPump类型替换，再加CriticalPump→Pump→Equipment及alarm domain/range四条ontology。修订的同序Graph输入构造与该方法相符，仍为18/180 facts、22/184合并图；不是推导结果输入，原fixture摘要不冒充改型／合并图摘要。十ontology的28/190套件只在full另行覆盖，不在两档间混用。

每trial分别以对应selector起fresh进程，B1测量instrumentation=false，不先跑full、另一尺度、query或validator，Warm在同进程第二遍。于是两档分别First的要求不再与全suite单入口冲突。新增source/package×两档×三trial的12份是**另12份B1纯语义原件**，不填入原S1 snapshotLoad，也不进口旧带Store helper。真实S1 snapshot、设备／工具／物理准入及T01/H票仍另行保留。

## 受影响上下文、过程原件及剩余门

完整差异没有改动原83/C13/106操作上下文的false状态、旧golden、组件政策或四writer所有权。资源仍以不调用resource_manifest/build_request/execute_request/derive_dependencies/permits_transition为前提，固定checker startup三JSON+lock；新增scope和selector未绕开这个前提。新probe未实现时不声称runtime资源已证明，独立artifact也不替代parent package:dir、正式Job/selected或原S1。

已独立核新增来源索引25份命名Git与18份raw的实际bytes/SHA，未见差异。首版provenance保全件11541B／SHA `0425a2915d3b85bc40064623c5933dfc1cf2cd566e5f614d2e52258fd4a2fbeb` 与首审读取身份相同；过程记录明确它是按原24+12及原serializer重构并核hash，不冒充当时捕获，故本报告也不补造其捕获时间。

`validation-static.json` 只陈述stdlib metadata/Git/AST/hash结果，与本独审关键核对吻合；不是运行／包／S1证据。doc-process-history诚实保留原C无kind、隐含parent/self边解释、边表格式等文档命令失败及处置，没有把它们记为产品失败或删去首失败。作者报告的文档formatter修正没有改变本轮核定module/edge内容；本独审未自行运行formatter，也未运行旧产品以制造通过。

当前未发现受该delta引入的新设计阻断；R1/R2/R3均可在**文档设计层**关闭。后续具体输入asset／完整投影schema/tally、hook实现、owner逐路径采用、T03实际lock/archive/license、进程／hard cancel／S1物理票及真实source/独立包/parent同输入证据仍须各自冻结和验证。SQLite损坏保护／whole-H HOLD、已拒分析停止、指定双方外审／CI／目标OS／真人／develop与远端门不变。报告写定后停止写入，首审及主合同不修改。
