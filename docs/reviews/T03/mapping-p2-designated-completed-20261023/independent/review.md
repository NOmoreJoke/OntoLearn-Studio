# P2 两份新指定终稿：独立静态复核

结论：不能据这两份终稿签“完整同版双审通过”。两方确实完成了固定17项与历史意见的部分静态审查，但都自行用“继承面/无diff/其他owner/既往读过”缩减了本次明确要求的完整审查。MiniMax已明确写整体未通过；Z的静态通过标签与其自报未读范围冲突。保留两份原稿、自判和终态，不改写为通过或重构原文。这里没有发现要求立即修改两处P2产品的新增阻断缺陷；覆盖缺口和具体意见仍需分别处置。

## 身份及方法

- 固定工程HEAD `c1e44f81723f9c616f669f56481d1b1ada7e57f2`，产品 `da1795b20c3c0d47ae975fe3371e802092a4b429`。
- Z原稿：`T03-mapping-P2-zcode-review-da1795/build/review-session/reports/mapping-P2-zcode-full-report.md`，27632 B / 150行 / SHA `bbe0d321270f4eb40ffdac3cc508077f35bceb7a935f9d498bfe1493d12fc6a1`。
- M原稿：`T03-mapping-P2-minimax-review-da1795/build/review-session/reports/mapping-P2-minimax-full-report.md`，42120 B / 320行 / SHA `886d6934b6c35a7acb4a37836a00aa5fc99972731813c39183bf3fde5bb6f178`。
- 两原稿均分段全文读完，读取各自冻结提示的本轮任务条款、同HEAD完整索引、M逐路径登记和必要源码；没有查询应用/任务API、GUI、全局状态或终态后台。两正式completed由主控已核；本复核不把报告写作时的UNKNOWN反写为新后台验证。
- N01只读取M树精确已安装openpyxl文件，未导入/执行库、未查看实际进程sys.modules/环境、未重跑source或包。文件路径、size/SHA、关键原文片段和29项原文台账见`static-evidence-and-ledger.json`。归档脚本后缀`.py.raw`，仅文本/AST/JSON/文件哈希处理，无产品执行。
- 唯一新增写面为本目录；产品、tests、依赖、原报告和受审树均未改。STOP/native/SDK/身份载荷没有读取或扫描。

## 完整覆盖没有达成

两冻结`dispatch-prompt.md:17–26`要求：全部tracked源码、tools/tests/fixtures/config/locks/CSS/公共契约/构建CI及docs工具；完整历史固定输入继续有效；继承I01–I04不能因owner不同免读；docstring/grep/metadata不是全文语义审查。部分覆盖可如实登记，但实际无法完成须记无法完成验证，不能用局部Pass代替。

**Z，原稿48–78、144–148行：**

- 第59行明确其余14 unit和5 e2e未逐行读，理由为零diff、其他迭代责任及既往已审；正好违反本次范围约束。
- 第57–61行：两锁仅身份级；schema/fixtures/binding-regressions/frame-fixtures仅键/枚举/关键defs抽验；约25个历史docs工具只登记；task-presentation及i04_matrix_evidence等结构级。
- 第74、78行：ADR未重读，大量I01–I04历史文档（约640件）未逐件读，用旧M749全文登记引用替代。原历史M本身也有93节读、5结构及未读例外，不能由其旧数量推本轮完整覆盖。
- 因而其第15行“完整工程语义审读通过”和第148行“全新完整……通过”只能保留为模型自判，不能升级为本次完整范围验收；第76–78行的诚实缺口登记并未自动关闭这些缺口。

**M，原稿89–117、263行及逐路径登记：**

| 范围 | FULL | PARTIAL | METADATA | UNREAD |
| --- | --- | --- | --- | --- |
| 全1028 | 44 | 19 | 964 | 1 |
| engineering 180 | 27 | 8 | 144 | 1 |
| documentation/evidence 848 | 17 | 11 | 820 | 0 |

上述是本复核将登记逐条与完整索引join后重新计数，非只抄报告总计。1028路径集合及blob/bytes可对齐；但身份齐不是语义读完。144个工程METADATA包括engine.ts、jsonl.ts、task-service、preload、公共契约及非mapping tests等允许文本；不能借合法二进制/受限身份载荷例外跳过它们。964条METADATA中962条逐项note为空，其分组理由也没有满足“逐项实际范围/未读理由”。M原稿第117、263行自行承认缺口，第16、320行明确整体未通过，应原样保持。

本结论不要求把合法禁读载荷强制标FULL，也不否定适当的完整结构化语义解析；这里的关键缺口是大量明确允许且本轮必须审的工程/工具/历史文本只做身份或抽验。静态补读及报告口径纠正可以独立于新运行完成，当前没有为了这些缺口重跑check/package的必要。

## N01：局部import执行点不等于首次导入

M原稿196、208–214行将`probe.py:39`局部from语句及`source.py:236`的iterparse语句，推成“defusedxml首次在guard内导入”；其中位置栏`:236`还误标成probe.py，而真实iterparse在source.py。局部语句确实位于guard包裹调用内，但首次模块初始化时刻不能由这一点推出。

本次精确读取M已安装openpyxl 3.1.5的静态链：

1. probe `run():349`先`import_module("openpyxl")`，350行才进入guard。
2. `openpyxl/__init__.py:6`先导入`openpyxl.xml`。`xml/__init__.py:29–35`的`defusedxml_available()`会执行`import defusedxml`；42行`DEFUSEDXML = defusedxml_available() and defusedxml_env_set()`先求左边，即使环境最终禁用，探测也先尝试导入包。
3. `openpyxl/__init__.py:7`再导入Workbook；`workbook/__init__.py:4`→`workbook/workbook.py:33`→`packaging/core.py:11–14`→`openpyxl.xml.functions`。可能有更早的同模块传递导入，此链已足以证明存在guard前的加载路径。
4. `xml/functions.py:41–42`在`DEFUSEDXML is True`时导入`defusedxml.ElementTree.iterparse`；其37–38行在非LXML分支也导入fromstring。iterparse条件位于LXML分支外，因此LXML可用本身并不能取消这条提前加载路径。

处置：N01“仅凭probe局部from认定首次在guard内”不成立，应更正为**局部语句执行点在guard内；历史实际首次导入时刻UNKNOWN，当前已安装链为提前导入提供静态反证**。默认环境且这些模块成功正常初始化时，ElementTree可在guard前已加载；实际冻结包/历史进程的环境、先前sys.modules状态及该次导入轨迹未在本轮观测，不冒称已实测全部依赖首次导入时刻。也不能反向把原文泛称“所有依赖import均在guard前”提升成已证明事实。无需据N01自动改文案为其错误建议，更无需为迎合该建议预导入依赖、修改产品或开新候选。

## Z Obs-3：执行顺序与JSON排序须分开

Z原稿98、135行称row-limit快照“不是最后”，这一理由与当前源码不符：`probe.py:280–295`先执行两个外部引用；296–322行CSV tuple顺序明确file→column→cell→row；323–340行依序解析并保存快照，所以row-limit是**最后一个解析case之后**的快照。返回后346–364行仅装配cases/evidence/limits并退出guard，没有后续固定解析case。verifier214行读取该快照作为累计计数。`json.dumps(sort_keys=True)`带来的键顺序不是case执行顺序。

处置：不采纳“不是最后case快照”这一事实判断。其精确边界可保留为“最后一个解析case后的累计值”，不把它扩成可监测任意未来新增后续代码的通用终点计数。当前不需要靠全零数值巧合来解释它，也没有因此发现产品错误。

## 18项历史台账（两新稿均逐项列出，旧原件不改）

完整原文、双报告行号及静态处置见JSON；此表只给本轮处置摘要。18编号不是18待修缺陷。

| 项 | 原性质与本轮独立处置 |
| --- | --- |
| Z1 | 首P3→P4历史保留；两新稿确认preview也拒同ID墓碑，旧残余说法属报告纠正，不改产品。 |
| Z2 | P3维持；重复predicate预检不足、后端fail-closed。M补充普通checkbox流程不主动产生重复referenceColumns；其不等于validator已显式拒重，也不证明任意注入state不可重复。旧“维持P3/终段无P3”矛盾保留且待对齐。 |
| Z3 | P4私有openpyxl API升级观察，当前未证不兼容。 |
| Z4 | P4 I/O概括，未测性能不量化。 |
| Z5 | P4工具计数口径，两新稿未复跑，不追认旧全体计数解释。 |
| Z6 | P4 CSV严格宽度/XLSX补空差异，未证数据错位。 |
| Z7 | P4所有权错误适配约束，与F11同一责任，不重复制造缺陷。 |
| F01 | 低；旧脚本仍回写固定原件，不执行/覆盖。新verifier采用新目录并不修复旧脚本本体。 |
| F02 | 低；草稿顺序导致fail-closed UX，未证越权；未改产品。 |
| F03 | 信息；design-only注册元数据不等于可派发能力，正式启用前由契约owner处置。 |
| F04 | 信息；工具策略不对称，不推为实际CI失败。 |
| F05 | 正面验证观察，非待修缺陷，只限已核输入/分支。 |
| F06 | 验证观察；两新稿纠正普遍XML论断，保已测普通转义样例；CDATA仍未运行，不能据静态边界宣称已证产品误拒或改闸。 |
| F07 | 信息；继承开发配置诊断路径；未实测宿主rejection表现，不证明CSP绕过。 |
| F08 | 信息；当次macOS零skip不升级到Linux/目标OS。 |
| F09 | 信息/报告更正；旧1110含58mapping，新总1116/专项64分列，不能写1110继承另加58。 |
| F10 | 信息/假设消解；T03已有identity约束，非T03存储面由正式owner评估。 |
| F11 | 信息；有界错误链不等于mapping.commit已正式接线；正式事务仍待T01。 |

## 11项新增意见台账

| 项 | 本复核处置 |
| --- | --- |
| Obs-1 | 登记建议成立：binding未单列engine pyproject，Git字节未变可独立证明；非当前完整性破坏。不补写旧收据。 |
| Obs-2 | 静态docs oracle依赖成立，移动文件会影响测试输入；可以维护文档说明，当前不是必改产品缺陷。 |
| Obs-3 | “不是最后case快照”不成立，见上节；保精确时间边界，不要求改产品。 |
| Obs-4 | 证据来源确认成立，原P2树实测不改称新审树fresh包；非缺陷。 |
| N01 | 首次导入结论证据不足且有guard前静态链反证，见上节；首次实际时刻UNKNOWN。 |
| N02 | B2已知坐标非独立parser列定位，已声明限制，非新增缺陷。 |
| N03 | 原303已有四CSV单元级语义，P2升级为包CLI固定执行和完整定位；不声称首次语义覆盖。 |
| N04 | 实际391文件+49目录、0symlink；“所有symlink target均核”在空集合下没有新增对象证据。引用宜写实际数量，不推成产品缺陷/测试失败。 |
| N05 | 与F06同一报告纠正/CDATA边界，不重复计产品缺陷，未运行fixture。 |
| N06 | 实测HEAD303+与候选同字节的dirty两文件，候选后提交；适用于候选字节，不称提交后HEAD上实测。 |
| N07 | 与Z2同一历史报告矛盾，原件保留，由主控决定按模型分别纠正方式，不代改历史。 |

## 交付边界

完整静态双审状态应记“覆盖未完成，完整双Pass未获得”，并保留模型实际局部判定。旧报告、首失败、正式completed与本次复核分别记录；不因纠正N01/Obs-3而将其余覆盖缺口清空。未新运行check、package、source/包CLI、GUI、API、native或CDATA fixture，也没有续接发送或创建审查任务。本报告只供主控读回处置，不是给另一模型互传本轮意见的授权。
