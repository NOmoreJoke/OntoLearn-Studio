# I05 源码／包同输入合同独立首审

结论：当前设计候选**不通过**，有两项 P2 阻断（R1覆盖、R3测量调用合同）及一项 P3 静态证据精度问题（R2）。除所列问题外，六项窗口的来源、纯输入隔离、单一调用、四 writer、资源／许可、原 S1 方法与后继接收门已形成可审查合同。这里审的是设计是否完整，未把未运行项目本身列成泛化阻断，也未重审旧组件算法。

## 范围、方法与固定输入

唯一工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-source-package-contract`，分支 `docs/I05-source-package-contract`，Git HEAD/base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。AGENTS 保持受保护未暂存 M：15852B、SHA-256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。只新增本报告，不修改主合同、附件、源代码、规则、依赖或旧过程，不 stage/commit。

全文阅读当前 AGENTS、inputs 中 window/setup/common、相关四份收件、T03 准备及固定 offer、原 B1/S1 条款、主合同和两份调查；完整解析三份 JSON 及后追加的来源／需求索引。以命名 Git 对象、文件和 stdlib AST/hash 作静态核对；未导入产品／第三方库，未运行测试、CLI、网络、构建、包、数据库、native/GUI、计量或格式化。没有扫描旧493过程包或库环境。

| 本次所审输入 | 字节 | SHA-256 |
| --- | ---: | --- |
| `docs/iterations/I05/source-package-parity/contract.md`，231行 | 54679 | `8cc6f527232d575028a5ba4e12912bc8f4a2b6eef350de929a296205d7c86cf1` |
| `case-catalog.json` | 237913 | `05388de09b1def4b12949b0de263090a586a2054d0842f4c69d3660e08f8ec57` |
| `static-import-closure.json` | 20710 | `c6d04d3b3eb8e3a380fd55cf1165e3128038cab2ea0b914b2faf9a44c3b0ac9a` |
| `guard-delta-audit.json` | 28734 | `ddf76c4e2f463e7f84c99b4482911fa46391a9a0c3d92248bb6ad731cbbd80d2` |
| `inputs-and-coverage-investigation.md` | 27883 | `86674cd731df246854d5e267181c7e4ad0c44e38a7de8683b24d72aa9432d7c6` |
| `packaging-resource-investigation.md`，补正版 | 24423 | `20c318873bf43194328b2aeef6bdf5e90de2a3ae8bf0b7f3d0ce5eac2d1b9420` |
| `inputs/packaging-resource-investigation.initial.md.raw`，首版保全 | 23511 | `e4d9e0c983cef206ed8160a27b4afd33e17049a821b49c942e1b3477e7dfcf99` |
| `source-provenance.json` | 11541 | `0425a2915d3b85bc40064623c5933dfc1cf2cd566e5f614d2e52258fd4a2fbeb` |
| `requirements-mapping.md` | 2307 | `eddadeadd6c16e4a68ec6db8fc8f7f8f496b061025473081677c5c77726853a8` |

供应产品固定 `6891a5842302859a531cf82767c5a482417bc274`，过程 `f79a29f596b2444cba542a906c91727869014886`。T03 offer 固定 `4fa5d62eb13269351384527b1f84761c08811e79`；T05 date 产品／运行／过程分别为主合同所列完整10720885／8e6f469／525c917引用。它们只是本轮命名依据，不是新包或新运行通过。来源索引24份命名 Git 文件和12份 raw 均逐 bytes/SHA 核同；不以来源清单自报替代核对。原架构文档在本树／供应 Git 不存在的边界已准确披露，按 raw 原件使用，没有伪造供应 ref。

## R1 · P2 · scope 真实入口未进入支持／拒绝矩阵

位置：主合同第37–54行的完整矩阵、第99–103行的观测／hook及第132–136行的闭包；coverage调查第86–98行。该问题先由 root 自查提示，本独审随后根据固定实际源码独立确认并判断为阻断。

实际供应 `semantic_scopes.py:234–298` 有 `project_validation_scope(asserted, ontology, *, include_derived, reasoning_result=None, reasoning_source=None, rules=())`，第301–326行有另一入口 `prepare_validation_scope(asserted, ontology, *, include_derived, rules=())`。后者在 include_derived=True 时真实 reason 一次再投影；前者只验证、投影既有给定结果，不重算缺少的结果。二者返回 facts、ontology、reasoning_result 及完整 provenance，影响后续 query/SHACL 的实际数据范围。

**具体反例：** 同一 asserted 事实、带 subclass/domain 的 ontology 和合法 legacy Rule，在 asserted-only 与 fresh derived 选择下，query／SHACL 可出现不同的事实／违规；现矩阵只要求分别 reason、query、check_shapes、profile fullview，没有要求调用这些 scope helper。一个 source／包即便保留了完全未调用的旧 scope 分支，仍可能满足现有各行。22模块被收集不证明其 scope 功能已被同样例调用，这正是旧83“数学调用存在但原query/validate未执行”缺口的同类遗漏。

**最小修订建议：** 增加独立 `scope-*` 行和纯输入来源，至少明确 asserted-only、fresh prepare(include_derived=True)及同次真实结果再 project。投影后分别用真实 query/SHACL 消费 facts，完整保存 facts/ontology/provenance，包括 selectedRuleIds、warnings、selectedFacts、derivedAxioms、两个 view digest；覆盖缺／错 reasoning_source、缺结果、非 exact include_derived、unselected rules/result/source、facts混公理等原前门。

此处必须保持实际 **legacy Rule／legacy reason 五字段结果域**：不能把 profile `/2`、DAG `/3` reasoning JSON、已有 expected 或预计算 derived 结果装入输入。可先 fresh prepare 得到真实 `reasoning_result` 和 `provenance.reasoningSource`，再将其与原 asserted/ontology/rules 给 project，不构造第二份推理结果。若声明 prepare reason=1、project reason=0，应把第101行目前只计 Validator 的只读 hook 域明确扩为真实 `semantic.reason.__code__`，分别计数、finally恢复；不把函数名或预填次数当运行证据。

这仅是私有组件选择投影验收，不建立正式 selected/Store/Job 权威，也不认证调用者自报 provenance。现 `semantic_scopes` 已在22模块中；增加这些调用在不使用 build_request/execute_request 的前提下，不应顺带采用 dependencies/states 或扩大四 writer。

## R2 · P3 · 静态 import 逐边证据遗漏相对包导入

位置：`static-import-closure.json` 的 method/edges，主合同第132行及 requirements-mapping 的“每条import”声明。

独立 AST 重算得到相同22个模块，逐模块 bytes/SHA 均核同。但126条边表遗漏两个实际依赖位置：

- `semantic_profile_production.py:291`：`from . import semantic_execution`。
- `semantic_profile_restore.py:10`：`from . import semantic`。

这两个目标已由其他边进入22模块，所以**不扩大采用闭包，单项不阻断设计可行性**。影响是“所有分支逐边”证据不完整，后继若依据边定位执行路径，会缺少实际 production/restore 的依赖来源。

建议修正空 module 的相对 `ImportFrom` 解析，补上两条有意义的模块边，并明确父包／self-edge是否另外记录。quality 根 `__getattr__` 里的旧 definitions/planning 懒导出依然是刻意不调用／不采用面：不能为追求字面 all-branches 就暗中收集，也不能在证据算法描述中把未解析／未采用边静默说成不存在。补正后模块集合仍应22，不借修表增加源码采用。

## R3 · P2 · 仅全 suite 的单 flag 无法执行两档独立 fresh 测量

位置：主合同第78–80行的唯一 argv/main/dispatch、第206、210–214行的 First/Warm 方法。此矛盾由 root 另行自查提出，本独审按本版合同确认。

目前 source 和独立包只接受一个 flag，随后必须 `run_fixed_suite()`，没有获准的有限子集选择入口。但第212行将 cold 定义为 fresh process、没有先跑 suite/validator/query，并要求两档分别记录真实阶段的 First/Warm。一个全suite进程内先执行1×或其他语义案例后，10×已被预热；反序则1×被预热。即使重复启动全suite，也不能让两档分别成为该进程的第一个固定测量集。把后一个 First 写成库冷或临时添加未规定参数都会违反现合同。

最小修订可以保留同一 canonical probe，改成三组精确枚举 argv，例如 `[flag,"full-v1"]`、`[flag,"s1-1x-v1"]`、`[flag,"s1-10x-v1"]`，source/package/parent dispatch与main同步，单flag／未知selector／extra／`flag=...`均拒。两后缀只选择sealed的纯语义固定set，不接受任意case/path。每trial单独fresh进程，Warm为该进程内第二遍，source和package使用同set/原输入/次序；header和terminal须分开selectedCaseSet、selected inventory和full inventory，不将子集采集完整写成full coverage通过。

名称中的s1只能定位原18/180纯输入，**不是已执行Store snapshot阶段**。真实12原S1试验仍须T01/物理/H准入后另票；子集自己的B1语义trial不可填入S1 snapshotLoad。每个sealed set还须明确所选4或10 ontology那一套及实际总图数，不能在1×/10×间换suite。此修改只是文档中的有限调用设计，未授权启动这些进程。

## 已核可成立部分与六项窗口完整性

1. **来源与上下文。** 原83 JSON已按固定 Git读取，1839011B／SHA `6c6ffc3a1a57d1817583c0a71d24e2847cc5d2d673848878c6e6e72dfe6c39de`。metadata逐83／106原操作／54check／50product与原共有字段核同；82 eligible、79 full、交集78，以及repair77和四E.5 fragment的区分正确。C13原ID顺序核同，确为2query+11SHACL。全部原非图操作仍false／not-executed，完整正文按case setup/steps源引用而非末图代替；缺span、无selected subject、late-V1缺物料等没有被数学成功填补。
2. **支持与拒绝。** 除R1外，Turtle/query/RDFS/受控规则、profile83、真实production/restore、DAG与全部roots、SHACL、整数、date、逻辑预算和offline均有实际canonical入口、完整输出及拒绝界。typed发行必须各端真实生成，restore不重reason、扰动只改本次接收副本、原caller-held premises保持；不把foreign对象／MemoryError当JSON public输入或真实OOM。C原golden与独立executor expected不喂业务，新输入无oracle保pending；source=package与数学正确性分判。
3. **单一probe。** 唯一新路径／精确flag／source和独立包同canonical main、两件sealed asset的单一路径、无fallback及header/item/terminal均有具体合同；调用选择须按R3修正。输入只含原文／records／规则／政策及有限扰动，剔除expected、bindings、closure、native结果和allocation。逻辑cap、退出0的有限含义、取消请求与实际终态分离、opaque调用不能被边界检查打断、首错／unknown／半行原bytes保全均明确。具体hook实现、完整投影schema/tally、caller/hard-timeout资源票是明确后继接收件，本报告不把它们当已有运行功能。
4. **四writer与包闭包。** 43个旧guard按旧sourceRef和6891分别核实，30相同／13不同；独立profile逐项retain/omit，增加6个命名supplier项且不借guard修正采用parent所有服务。22模块AST集合、28个现有supplier文件的计数成立。production/restore实际签名和同次捕获链可对应所拟编排；需要required error_catalog/error_schema及实际ledger，不能从JSON造发行类。独立artifact不经旧entrypoint／worker／Store，parent以后同suite另验，原B1 parent门未被取消。
5. **资源／owner／license。** 明确不调用resource_manifest的三JSON选择有真实源码依据，详见下一节；T01逐文件采用仍是实施前门，不是默认采用。八个运行distribution、完整lock/extra/marker、installed文件与许可、Python/PyInstaller/平台runtime分别绑定。没有用版本号、hidden-import声明或源码SHA替代实际archive／license／canonical身份；pyc与源码不同域，后继须冻结编译对照规则。
6. **S1与下一实施路径。** 主合同保原seed20261019、独立namespace、18/180、两行query与原hash、source/package×两档×三fresh trial的12原件，warm／RSS高水位／import启动域分开。静态阅读storage_probe实际证明其measure会创建Store/SQLite，主合同没有以纯图数组伪装snapshotLoad，也明确不调用它绕HOLD。历史4ontology与新10ontology样例区别明确，旧C4数值不沿用。下一票路径、I05/T05/T01/T03职责、组合ref与冻结／双审／CI／OS／真人／远端门均具体；设计可先完成，不自动取得runtime或四writer权限。

## 动态资源选择与附件补正核对

固定 `resources.py:14–20` 通过文件加载唯一checker；checker `contract_v2.py:13–16` 顶层只读 schema/registry/errors，resources另读registry和lock。checker第724行的 dependencies 是 derive_dependencies 内延迟读取，第818行的 states 是 permits_transition 内延迟读取；resource_manifest第67–73行则 glob全部 v2 JSON。固定 Git实际有八件，不是五件。

主合同第140–154行选择不调用 resource_manifest/build_request/execute_request/derive_dependencies/permits_transition，而使用原CONTRACT目录及semantic_identity，并让新probe只hash固定白名单。**在这个调用限制下，三JSON+checker+lock可作为最小静态提议；不需修改resources，也不能把这一静态闭包叫资源runtime已验证。** 若后继真实调用越界，应先列owner/resource delta和新身份，不能临时读取缺件、另造checker或fallback。

包装报告原五JSON说法已由作者保首版raw后定点补正为八件，并补两个延迟读取点及上述三件选择；本独审全文核补正diff，与当前主合同一致。此历史事实错误已关闭，不将其再列未闭合问题；首版hash仍保留，未倒改。共享契约、依赖、许可证、包archive仍待各owner精确供方采用及未来实际证据，属于已明确的供应／实施门而非本轮静态Pass。

## 交付判断与复核界面

R1关闭前不能把当前矩阵称完整支持／拒绝合同；R3关闭前不能声称既定唯一argv可承载所列两档fresh测量。请同批保全本版主合同和首审，补scope调用／纯输入／输出／拒绝／真实reason计数及必要资产字段、有限case-set调用合同，并修正R2边表。修订不应更改已收组件、旧golden、T03四writer或资源采用权。之后只需针对实际文档delta及受影响上下文复核，无固定第三轮、无旧组件重测。

本次没有source/package运行、新build、许可入包或性能结论；没有将这些尚未执行事实泛称设计失败。实际失败原件、SQLite损坏保护／whole-H HOLD与被拒分析停止、正式Job/selected及指定双方外审等原门保持。报告完成后停止写入，等待root统一修订和精确delta任务。
