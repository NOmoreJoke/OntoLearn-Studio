# D2 同输入源码/包组合独立内审

2026-10-21。**两处 writer 实现与下述实际验证范围通过，未发现剩余实现阻断；D2 整体收口仍待总控精确接受 wcwidth 原生签名域差异。** 不能将 archive-audit 的 pass 解释为所有发行二进制原字节相同。本报告不是指定 ZCode/MiniMax 双外审，不是两目标平台、完整 I05/T03 或父 B1 验收。

## 受审身份与执行边界

实际树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-profile-build`，分支 `feature/T03-profile-build`。产品 base 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，批准精确起点 `b34158977bcfefdc8d218131d00cfe68d4415003`；只读接收提交 `fbf36723a29bb19b0337b78a492c46620c9bd590`，首实现 `418b5288014d3b7285c8b67b4d82086ed6541d2f`，修复后最终产品为 **`a4d1457fc6a1f1d1832296a8dcdb2ef42da75b98`**。

已全文核读根实施授权 8088 B / `5c9739565b5df031f8bf663616ba451fed1c86aabae56dd3cf1d38ade50cf2d5` 及控制清单 20169 B / `7778309e8beec0f5ff8ac89531f1a70282f12f257beebae4ff8d7899f393e4b1`。当前 AGENTS 15852 B / `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`、common 17891 B / `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0` 与已全文读取版本相同，完整第九节和无桌面约束继续适用。

审查者只作 Git/文件/AST/JSON/ZIP/二进制结构与哈希静态核验，另以同 Python 3.12 对已固定源 compile/marshal 结构比较，**未执行编译所得 code、import 产品或执行 matcher**。未代跑正常 check/package/83 计算/CLI 矩阵，未安装、联网、启动 GUI/Electron/e2e/HMR/native、使用凭据/模型/付费入口。只写本报告；不改产品、测试、配置或其他文档，不提交/推送/PR/merge，不恢复 blocked Goal。

| 最终对象 | bytes | SHA-256 |
| --- | ---: | --- |
| `scripts/build-engine.mjs` | 13264 | `5dab9850ba97e3c5e916ac45386a05f540c671f342f5ebf5c911ccc5e4772894` |
| `packages/engine/entrypoint.py` | 1232 | `9abf0c22943cfae9f6f43893586626027bf9f4fc7318100465c0179aba69fe31` |
| 最终 App 内 engine | 6077232 | `99adbd67fe7f1cfdb07684bc09165d6b4eda29e42b631a09574f7a95ba2e9ba7` |
| 包内 `provenance/d2-build-inputs.json` | 128700 | `c2b914cf6ceeda72cb831e33aefd0a32be6f9c7b327c85a75fa30100e5fa7ed6` |
| source 原 stdout（05） | 14006950 | `a16699f47c5fc8de6658d1dc5a1c422796daf0f3bb4dbed520ffce0577ed74e0` |
| 最终 App engine 原 stdout（10） | 14006514 | `dddc3a8183d8ecccfb8b52e218831dbceed207ddff69057f228c20c85a395055` |
| `archive-audit.json` | 829115 | `a5878ca164d57996bf4bcd25c63b0386621b875f0ae1dbcc0db423449afcba65` |
| `cli-resource-suite.json` | 8047 | `6511a3e1a95ac0caaf11bc095af93e568afcec45ea17515f5ad91b534eb11b5d` |
| `wcwidth-native-difference.json` | 13850 | `cfbb849bc93ea4e3cb146a3d669fff9923a5dcb72b756d4199f4ec30edcb3419` |
| `final-inputs-and-executions.json` | 54366 | `842f45378ff13a5e9c1d82117a2f36258a4d970a455b101ae73d93d8c509a9cd` |
| `docs/iterations/T03/profile-D2-package.md` | 16047 | `9711f76df876e5f1d3ef86870a73d43f40701afee1dc3d438909d6f6cc552e3f` |

当前运行原件位于本树 `build/profile-d2-evidence/`，外部脚本在 `build/profile-d2-external/`。已封本目录 `runtime-evidence.zip`，3707625 B / `51e628ca57615123df296601605f2081f6bb261935fc192bf938f6b2afe593fc`，158成员；本报告另逐成员核manifest的bytes/SHA及完整执行记录。实际 App engine 为 `release/mac-arm64/OntoLearn Studio.app/Contents/Resources/engine/ontolearn-engine`，不是仅测 build 目录副本。

## 只读接收与两处实现

独立逐项对照控制清单的固定 Git 和 checkout：18 源/资产、24 验证文件、D1 两文件、23 基线源/data 共 **67 项 bytes/SHA 全同**。adoption 提交恰接收 18+24，并附三份本线授权/接收证据；首实现提交只改两处 writer，修复提交只加两个优化参数。相对 5f 的完整功能范围确为 **46 路径**（2 D1 +18 运行/资产 +2 D2 +24 验证），其余新增均属本线 docs，未将整个功能差异说成两文件。

JS 的 43 个 fixedInputs 与 18 运行/资产 +2 D1 +23 基线控制条目逐字一致，构建前验证每项原 bytes/SHA、writer/固定输入相对 HEAD 的干净状态并记录组合 ref。D1 仍是 fd87 原 pyproject/唯一锁，无 resolver、XLSX 或公共 schema/Store/worker 新改动；只读测试/机制/业务源均未被修绿。

17 个 canonical 模块由明确固定路径转换；实际 `/\.__init__$/` 正则正确，String.raw 内 Python 反斜杠/换行正确，不产生第二模块身份。八 distribution 的 copy-metadata、rdflib 既有收集和 pyshacl/owlrl/html5rdf 收集、三个禁止 quality 模块的 exclude 符合合同。没有 collect-all quality、第二 probe/matcher、任意输入入口或 Store/Job 写入。八库实际许可证均位于 dist-info；已静态核 PyInstaller copy_metadata 会收整个 metadata 目录，包内实物另行核验。

entrypoint 在全部旧路由前扫描准确 profile token 或 equals 尝试；只有完整单 token 才 import canonical main、移除 flag 并调用 `main([])`，保真实返回值。额外/混用/equals 拒绝固定 32 B stderr、stdout 空、exit2，不落旧 stdio/worker；其余原分支保持。固定 probe/locator/预算源字节未改，输入无 expected 回填、frozen 无 checkout fallback。

## 原始终态、全量输出与独立静态复核

以下运行由负责人实际执行，审查者核原 execution 与 stdout/stderr 的 bytes/SHA、真实退出及对应候选；没有重复运行产品矩阵：

| 原件 | 实际结果 |
| --- | --- |
| 01–03，首 418 | normal check 630 TS/2582 Python、零 skip 通过；源完整 probe exit1；source12 通过。首候选证据保留，不当作 a4d 新包证据。 |
| 04–06，最终 a4d | 正常 check exit0，lint/format/types/build、630 TS/2582 Python、零 skip；固定源 probe 完整 exit1；source12 exit0。 |
| 07 | 外部验证器 `-O` 真实负例 stdout 空、固定 `EVIDENCE_PYTHON_OPTIMIZATION_INVALID`、exit1。 |
| 08 | 正常 unsigned `npm run package:dir` exit0；实际 PyInstaller 日志目标优化级别 0，App macOS arm64；未启动 Electron。 |
| 09/12 | 新 source/package 分别调用固定外部 checker，均真实 exit1，78 数学字段一致、4 failure、1 not-executed；完整明细分别保留。 |
| 10/11 | 最终 App engine 固定 probe 完整 exit1、未 timeout；严格源包对比 exit0。 |
| 13 | 旧源 CLI 采集首次失败，空输出/JSONDecodeError 原件保留；见下节处置。 |
| 14 | 修正外部源命令后 suite exit0：6 旧源包探针、12 参数拒绝、3 隔离资源副本负例，共21条。 |
| 15 | 静态 archive audit exit0；其 pass 范围和 native raw 差异分别解释，不能合并为全发行原字节通过。 |
| 16–18 | 实际递归目录查看exit0、archive auditor优化拒绝exit1、native有限静态观测exit0；均属外部证据，不执行产品计算。 |

04–06 使用的是较早 capture 版本，原记录尚无 headAtStart/selfSHA/collectorOptimize；本报告不声称这些字段存在。其实际命令/终态、修后 Git 顺序、冻结产品字节与后续 a4d build provenance/源 artifact hash共同绑定候选。07 后记录明确带 a4d、collectorOptimize=0、collector SHA，并清除/重设 PYTHONOPTIMIZE=0；原件未被补写成新版格式。

审查者另以独立 JSON 读取拒绝重复 key/NaN/Infinity，逐原生类型、字段集合、数组顺序/重复深比：**211961 节点，恰9个已逐值核预期的允许路径**（两 frozen 布尔、七 sourceSha→null），其余全部相同。83 case 顺序/唯一性、78 success/4 resource failure/1 not-executed 均保持；源 raw 与固定 0475 历史原件恰同 SHA，但这是实际新运行结果，不是复用旧进程通过。

strict validator 的完整 payload/rows 拼接、canonical digest、batch hex/SHA逻辑已静态核读，未做第二计算器。外部 checker 三成员 hash仍固定，expected留产品外；执行输入资产和 projection manifest只按 JSON值相等校验。源/包等价和外部数学对照分别记录，四 E.5 资源拒绝与 transfer 缺规则仍不算业务成功。

独立核21条子命令原 stdout/stderr、退出与 timeout。12 参数拒绝均精确空 stdout/32 B stderr/exit2，三资源副本为 missing/bad hash/2097153 B over-cap，均精确空 stdout/21 B stderr/exit1。原最终包及资产未改。旧 contract 源包除无差异外比较10节点；resources只 frozen差异、17节点；storage去除实际 measurement观测后20节点完全同，18 triples、精确 A01、快照与输入/查询 hash一致。耗时/RSS等仅保各自观测，不量化提升。

## 实际归档、资源、许可与代码身份

已全文静态读 archive_audit.py，其运行对应文件 32414 B / `315c47607c16e13689f49442b3bfd3330cfd45fcb24d7ac7fdc134250df47604` 与 JSON auditor 自身身份一致。脚本只 import 归档工具，产品 compile/marshal 后未 exec；优化级非0显式拒绝，不靠 assert。PKG/PYZ 原始有序 TOC先计重再核 reader映射；仅递归规范化 co_filename，其余 Python 3.12代码/常量/行表/异常表/qualname等保留。

负责人正式结果为 CArchive 12条、PYZ 749条；engine canonical模块恰30（17采用+13继承源），quality恰7，无禁止服务/重复名/质量代码别名。30源包模块及入口核全代码字段，含693个模块内代码对象、2个入口对象，另查406个 loose/base-library代码项。部分库开发/类型提示/非使用模块未收明确列出，没有声称八库全部接口都已收集。

审查者独立使用 stdlib解析最终 engine 原始 CArchive/PYZ（未 import/运行 PyInstaller 或产品）：12 TOC无重复、原 TOC SHA吻合，749 PYZ 名唯一；对30份实际源及入口 compile(optimize=0)，除递归 co_filename外逐全部代码结构比较，**无差异**。此核验把原 .py、实际marshal/PYZ和最终engine不同字节域连接，未要求原SHA相同。

另独立对实际最终 engine与build副本逐字比同；包内provenance确为a4d、optimize0、17名、两个writer hash和显式优化argv。固定资产+九contract+完整锁11项原字节相同，八dist-info 55个文件（含10许可）逐项正确；原 inv-v2亦由正式audit作为第12资源核回。整个实际engine目录343文件再次独立逐字核对audit收据，全部吻合。provenance是输入承诺，实际文件树/TOC/资源是外部实物证据，二者未相互冒充。

## 意见与处置

1. **P2，已关闭：优化级 provenance不准确。** 首418的 `build-engine.mjs` 硬写 pythonOptimize=0，实际未传优化参数而继承环境；PyInstaller makespec/build_main默认取解释器 optimize，存在实际PYZ与记录不一致触发。a4d只新增 `--optimize 0` 两参数，已核diff、实际日志/provenance和代码字段；最终check/包以新候选重新执行，未沿用首包。
2. **P2，已关闭：外部断言可被 -O剥离。** strict validator核心assert在优化解释器下会失效，旧capture未清PYTHONOPTIMIZE。现capture与validator以非assert分支拒绝非0，capture清除/设置0并记录自身/候选；07真实-O拒绝原件已核。固定oracle不改，在无优化进程运行。
3. **P2验证命令，已关闭：旧模块 `-m` 不调用 main。** 13的 source contract stdout为空，批准5f的 contract_probe/resources.py只有main定义无模块入口。我前轮文档静态审查也遗漏此命令细节，现明确纠正。只改外部argv为直接调用原canonical main；storage仍用其真实 `-m`入口。13原件保留，14用新v2标签重跑必要suite通过；未改只读产品或历史合同，不能把原空输出exit0当回归通过。

## 仍待总控精确接受：wcwidth 原生二进制

此为**未关闭的包接受门**，不是已确认算法错误。原 `.venv/wcwidth/_wcwidth_c.abi3.so` 为1389136 B / `385bccbd2efdcf0e0d4288d8f4ae5586b7ac5797965b8f79268188ae5b5e8d62`；最终App为1381184 B / `f5e36bc58a9605c02f499e9622b6af4c6a430fe66eb3b007e7a5f3d588f5e31e`，**原始bytes不相同**。archive audit只将其记录为otherDataObservation，不能以其pass跨过本门。

已独立读取两份Mach-O的header、14 load commands及10 section：descriptor/payload逐字hash与观测JSON、既有otool文本所列结构吻合。10section内容相同；签名偏移同为1378224，签名区从10912 B变2960 B，另 `__LINKEDIT.filesize`/`LC_CODE_SIGNATURE.datasize`两字段相应变化。仅将这两个已观测长度字段清零后，签名前1378224 B前缀实际相同，SHA为 `2399d98dc25e3b73aecedb7cdd3c1351767fa920e000b080200e587ebe09c4f9`。这是一项具体观察，不是本报告新增native规范化白名单或声称整个原生二进制相同。

建议总控仅就本固定source/package hash、两字段/签名区事实与PyInstaller实际行为作精确接受或要求补证；若扩大规范化/实现/平台范围，另走批准与受影响复验。此报告不因总控另作的签名审计存在，就推断已经获得接受决定。

## 补充静态闭包：未收34模块、动态分支与optional warnings

此处纠正审查期间两次不准确口头表述：先将PrettyTable路径简述为普通wcswidth，后又把wcstwidth的term_program=True误读给width。两项均撤回；未据此扩包或运行产品。最终实际导出、调用与环境依据如下，不能用83一致来替代这组静态依据。

`dependency-closure-static-evidence.zip` 为57442 B / `a5f05699f38b0b6fd6e24a7e6b3f8c9f0723578b6784c6eec3a19df0016baf0f`，15成员（14源码/pyi和native声明记录）。审查者核14成员与实际安装原字节相同，源/包NUL声明的offset/长度/文本也与实际二进制相同。以下行号均对应该固定发行源或已批准I05源。

- **固定产品调用**：semantic_profile_probe通过execute_profile_records→semantic.reason的显式profile分支（semantic.py1122–1134），没有PrettyTable/第三方CLI路由。legacy `check_shapes` 在semantic.py1254–1279直接以本地Graph调用 `Validator(...).run()`，固定ont_graph=None、inference='none'、advanced/use_js/iterate_rules/sparql_mode=False；samples.py480–495同样固定none/False。validator.py75–80只有use_js才启JS，191–204仅非none才预推理，273–285仅advanced才启AF，103–137/323直接生成字符串+RDF report。pyshacl CLI在cli.py10导入PrettyTable、379–400的format='table'分支使用，但上述调用不经过cli。PYSHACL_USE_FULL_MIXIN（validator.py36）只影响ont_graph非None的mix分支，本固定路径无该图。semantic_offline.py24–30/46–51在当前Context拒绝socket/urllib/subprocess外发，且不把此guard当作任意extras可用的证明。
- **PrettyTable确切API**：prettytable.py3078–3080调用 `wcwidth.width(val)`，506–513调用ljust/rjust/center，2485–2487调用wrap，均未传term_program。Python `_width.py74–80`、align.py17/82/153、textwrap.py541默认False；`_constants.py155–158`的False直接返回None，只有True才读TERM_PROGRAM/TERM。故不能说设置环境变量本身会给这些未传参调用打开override。
- **C与Python必须分开**：wcwidth.__init__.py51–85依据WCWIDTH_PYTHON是否非空、C扩展能否import，决定导出C或Python函数；不能只凭Python函数证明实际C行为。实际 `_wcwidth_c.pyi`24–58的width/align默认False，源/包C的NUL声明（width@65794）也声明False；wcstwidth@65614/pyi17–23才声明True，wcswidth没有term_program参数。这是静态声明证据，不是本轮额外执行C API。C缺失/显式WCWIDTH_PYTHON的Python fallback分支已按源读取，不声称两种实现的任意API全面验过。
- **动态表确实存在能力边界**：`table_grapheme_overrides/__init__.py24–37`用registry hash动态import `_known_*`，ImportError正常回退{}；`_width.py179–192`/`_wcswidth.py245–258`只有解析出终端才读取。显式 `term_program=True`、已识别终端字符串或直接wcstwidth的其他调用可以触及该边界，缺表会失去终端专用校正，不能称其与源完整终端API等价；此类调用没有在本D2固定入口/上列默认PrettyTable路径开启。

安装但未归档的完整34模块，及其源path/bytes/SHA，见archive-audit.json各distribution的uncollectedSourceModules；20个 `_known_<hash>` 名逐一完整列在wcwidth项，不省略该证据。本报告核该清单与实际749 PYZ及安装库存一致。分类依据如下：

| 未收集合 | 实际静态用途/可达边界 |
| --- | --- |
| pyshacl.assets.make_builtin（1） | make_builtin.py8–35在顶层读TTL并写pickle，是资产生成工具；assets父包为空，已收运行源码无到该模块的import。Validator运行用既有baked assets，实际所需data已原字节核验，未依赖运行时重生成。 |
| pyparsing.ai、ai.show_best_practices、ai.show_best_practices.__main__、tools、tools.cvt_pyparsing_pep8_names（5） | 三空包/独立CLI及PEP8源码重写工具；show_best_practices.__main__1–2调用指南显示，cvt文件79以下为CLI。主__init__.py206–237的显示API读ai/best_practices.md，缺文件会回退内嵌文本；它是明确不同的非产品API边界，固定semantic_query只取解析核心，不调用指南/改名工具。 |
| prettytable.__main__、prettytable.colortable（2） | __main__是演示CLI并导入ColorTable，colortable.py11另需colorama。父__init__.py3–32只导出_version/prettytable，68–69仅委托旧常量deprecation处理；无到这两模块的运行import。本产品不提供该CLI/彩色表入口。 |
| wcwidth.table_grapheme_overrides._known_*（20） | 如上完整动态表清单与True/string条件；不能由“无静态import”或“捕获ImportError”直接抹平可达API差异。当前固定路径限制的依据是实际调用参数和导出声明，不是83恰好通过。 |
| packaging._structures、dependency_groups、direct_url、errors、metadata、pylock（6） | 分别为旧Infinity兼容、dependency group解析、direct-url、后几API所用错误聚合、发行metadata解析、pylock支持。父__init__.py仅声明版本/版权；已收packaging核心及其他实际已收依赖源码中没有到这六模块的静态import或按这些名动态加载。errors由缺省不收的dependency_groups/metadata使用；本构建取metadata用stdlib importlib.metadata，不能混称调用packaging.metadata。任意调用这六API不在本轮闭包保证内。 |

独立AST核对八库实际已收308源码模块，未发现通往上述34缺省模块的静态import边；此事实只配合明确动态分支使用，未据此宣称一般Python动态行为全不可达。developer/type-hint data和源console scripts的完整缺收观测亦保留在archive JSON，未删warn修绿。

**尚未安装的extras与“安装了却未收模块”不同。** 正式warn全文已封存，以下按实际源分支解释，未把所有missing都记成必需或全部无影响：

| warn类别 | 当前固定路径依据与保留边界 |
| --- | --- |
| html5rdf lxml/genshi/chardet | treebuilders/__init__.py76–84按显式lxml/etree选择，treewalkers/__init__.py49–56按genshi/lxml/etree选择；_inputstream.py482–487的chardet为可选try/ImportError。I05严格Turtle用自有LexicalSink/SinkParser（semantic_turtle.py95），profile用结构化记录，不选择这些HTML builder/walker。未保证所有HTML后端或编码猜测选项。 |
| pyshacl sanic/sanic-ext/sanic-cors，JS pyduktape2/regex | sh_http.py6–14只在独立HTTP组件import时要求server extras；本dispatcher不调用此入口。Validator的use_js=False使75–80 JS启用分支不入，advanced=False禁AF；不将其解释为提供HTTP/JS服务或任意JS形状支持。 |
| owlrl pyoxigraph | graph_abstraction.py1–13缺包设has_oxigraph=False，47及66以下按RDFLib backend；当前源构造本地RDFLib Graph，未选Oxigraph Store。`owlrl.RDFS` warn不能仅据文本推断一个新必装distribution。 |
| rdflib isodate/typing_extensions/annotationlib | xsd_datetime.py44–50仅Python<3.11才import isodate，当前实际3.12走stdlib日期解析；typing等warn含版本/类型检查条件。未把其他Python版本也标通过。 |
| rdflib lxml/orjson/simplejson、berkeleydb、graph_tool/networkx、httpx | xmlresults.py36–42的lxml有stdlib XML fallback；可选JSON加速器有其各自fallback；BerkeleyDB/外图工具/HTTPX contrib是另选store、转换或远端client分支。I05固定内存Graph、严格Turtle/结构化record、Validator非SPARQL远端和不启外部client，不暴露任意parser/store selector。未保证这些未安装extras或所有序列化/数据库API可用，offline guard也不能替代其实现。 |

这些静态依据足以支持本固定入口及明确采用范围中34缺收不构成新增实施阻断；未扩充库API、预算、输入资产或产品矩阵。总控对原生签名pair的接受权仍单列，不能从闭包限定结论推导已接受。

两处实现和已列实际运行/静态证据范围已通过；wcwidth接受门之外无剩余修码要求。Windows/另一目标平台、干净设备、GUI/native窗口/B1、正式公共runtime/领域父验收、指定同版双新审、CI/正常合并/远端门仍未完成。本次不作D2无条件整体通过、不授权push/PR/merge或恢复Goal。
