# MiniMax R05 十三项及十四项旧意见：独立事实处置核验

结论：保留作者 ConditionalPass 原结论及完整验收/授权门禁，不代 ROOT 改判。需纠正 R05-01 的“不可能绿”、R05-12 的文件/调用事实；R05-03/04/10须划清既有桥接、历史快照和未提交指南范围。其余多为可采非阻断 OPEN、观察或信息项，不能转成新增实施授权。

原稿完整读取并复算：548行／65672B，SHA-256 `26d4dbe2b39348e89b3cbd7c7307b98c33e0dd199e96e101f94adfe7fd4c9951`。核对固定aff源码、旧R04处置/独核、O032/036/037及ROOT接收、choice-A记录；未读本轮ZCode报告/结论，未联系任一外审。本次没有重建wheel、运行哈希算法对拍或复验产品；原稿自述的这些运行不等于本审亲测。

## 十三项新意见建议

| 项 | 建议处置及必须保留的限定 |
|---|---|
| **R05-01** | **部分采纳、纠正确定性推断。** 79个F先于取消、六处默认编码写Unicode的源码、aff只增诊断未修实现均成立；Windows整链未完成是未关闭门禁。报告§3与末532“本候选仍不可能为绿”却从高可信未确认假设跳成确定预测，与§6.1自认无实际栈/编码且aff未执行相矛盾。改为“aff尚无Windows实际通过证据；原79F未定位，不能宣称已修；若原原因重现，maxfail只会提前终止”。保留诊断需求与合并前完整Windows门禁，不能宣布必然失败或UnicodeEncodeError已确认。所谓“不存在任何Windows通过证据”也应限本候选整链，不抹去历史基线成功。 |
| **R05-02** | **事实可采、程序性边界须分开。** CI36 Quality/Windows cancelled、macOS success；verify打印pass不是step success、recovery skipped；aff未push/未运行均可采。CI36实际merge checkout681ff与API head58c9分开正确。合并前必须取得真实完整CI；但“尚未授权/尚未执行aff CI”本身不是新实现缺陷，不能把正常“指定双审→获准push→PR/CI→merge”倒置成先有aff CI才可审查或允许push。诊断早停即使绿也非全套验收；何时给受控远端票由ROOT/用户按现有门禁裁定。 |
| **R05-03** | **部分采纳范围披露；不默认新增打包前置。** aff无自产新包/包内运行属实，cb8→aff为12证据文档+1CI，产品/测试/依赖无diff，O036 build四项逐字一致、main仅dev nonce差异，O037真实新build6GUI与原094包912成员不变的桥接成立。ROOT O037接收已明确`packageBoundary: Original unchanged094 artifact prior runtime retained; no new packaging or packaged runtime ataff`，不是“尚无人登记桥接”。应引用该既有登记并保留“未制造/未运行aff新包”，不得自动要求再包或把原O036`newHeadGUIActuallyExecuted:false`当成O037之后仍无新GUI。登记是否满足现有同版包门禁由ROOT核既有授权，独审不赋予新豁免或rebuild授权。 |
| **R05-04** | **部分采纳当前状态入口易误读，纠正历史覆写建议。** status首段“尚未PR/CI”若作为当前状态已过时；但其固定受审实现明确cb8、证据明确O029，Ruff369是该轮历史真实值，不是因O036379而变成错误。27/58/1344也是真实旧实现口径，不应简单改成29/71/1355覆盖历史。由ROOT唯一维护者在正式后续状态更新中标日期/新head/PR16/CI36与O036/037，保留原历史段和冻结身份；当前审查期间不为“刷新文档”擅改受审树。原M-01历史完成不应倒记为未完成。 |
| **R05-05** | **可采非阻断延期。** 独立集合重算UI17/契约26/交集10，额外7、缺16与报告完全一致。缺集不等于16项全当前可达，不一概加入白名单或删额外码；按能力真实方法出口由共享维护者对齐。 |
| **R05-06** | **可采延续OPEN，不扩大异常归一。** domain_changesets:448–465只守manual/edits；471 transactions.preview只捕MetadataError，474–477后置supported catch不包先前Store._definition:1125–1129。定义早期TermInputError/非canonical ValueError不能由后置catch证明受控，旧wire OPEN保留；不能概称每个definition路径都必然HOLD，也不能补broad ValueError吞未知故障。原T01原始triples/Agent接线责任不变。 |
| **R05-07** | **部分可采非阻断合同边界，收窄标题。** job_store:617–634对裸ownership Conflict构造旧三字段detail，header读取拒绝，UI unavailable成立；但typed支持包括ManualOwnershipConflict与SingleDeclarationConflict，storage:1147–1173还可为含受管记录的singleDeclaration生成真实witness。只能说“其余裸Conflict回退族未提供新typed定位”，不能说所有受管ownership均无可读定位，也不能说所有ownership映射INTERNAL_ERROR。不得伪造detailRef/从诊断文本反推witness。 |
| **R05-08** | **维持未确认观察。** 无ORDER BY为源码事实，无构造性反例且承诺actual首阻断行，不等于跨运行字典序第一。不得升级已证缺陷/强制新排序验收。 |
| **R05-09** | **可采依赖pin/许可/ZIP信息，校正计量文字。** uv.lock:258确有fr201.3 SHA99fab7…和2379774B；本审stdlib实读三本地wheel为STORED(0)，upstream为DEFLATED(8)。上游**整文件615416B**，596328是ZipInfo压缩成员payload总和；上游与fr201.3含补丁/metadata差异，不能称“同内容压缩后596328B”。作者称可复现重建属其运行，本审只核脚本/针，不另背书重建实测。保留历史wheel/上游为审计及repack来源，不增供应链阻断或授权删除。 |
| **R05-10** | **可采工作环境指南问题，不归aff候选缺陷。** 工作树未提交AGENTS含失效architecture链接；git show aff:AGENTS是旧10行版、没有该链接。报告前文已披露非候选，最终处置也须一致；归指南唯一维护者，不能要求混入aff或因该overlay单独重开产品验收。归档两副本可作为实读依据，不把任务票的FR007/008引用偏差扩成产品缺陷。 |
| **R05-11** | **维持非缺陷信息边界。** 新typed witness/schema确无object，页面给id/owner/sourceRow/S/P；用户仍有输入及已授权完整domain Read，不等于产品完全不能看对象值。错误定位最小化与正常业务Read不同，不得把“不得泄露任意异常/单元格值”泛化为所有已授权RDF object均禁止跨边界。是否本地补显是未来产品选择，非本轮前置。 |
| **R05-12** | **部分采纳环境依赖，需纠正两个具体事实。** 不存在`tests/unit/t02-mainline-contract.test.ts`；实际是`t01-mainline-contract.test.ts:656`，与`t01-ontology-metadata-contract.test.ts:168`均为`execFileSync('python',…)`，不是报告所称spawnSync。`t02-manual-fact-id.test.ts:66–68`已经`spawnSync(resolve('.venv/bin/python'), ['-I',…])`，并不依赖PATH找python，不能要求把此处改成它已采用的方案。O035两ENOENT/O036授权uv环境纠正为真，保留首败；非阻断维护建议交对应共享维护者，不将正确环境调用说成产品回归。 |
| **R05-13** | **维持信息级。** 本审实际行数2993/1887/1748吻合；文件大不是当前正确性缺陷，不在冻结候选做重构。 |

## 十四项旧意见：逐项延续核对

| 原意见 | 建议保留的真实状态 |
|---|---|
| Z-01 | 未确认观察不变；无反例不升级缺陷（对应R05-08）。 |
| Z-02 | 作者撤回维持；43692是分页base64信封长度，不是解码witness字段限。262144整文档保守预算及16MiB manifest边界保留，未做50K GUI。 |
| Z-03 | OPEN非阻断延期不变；definitions早期异常不被后置supported catch兜住。 |
| Z-04 | 部分OPEN不变；ownership原Conflict.code缺类映射不等于_application最终都回INTERNAL_ERROR。typed与旧detail族分开。 |
| Z-05 | 17/26/10/额外7/缺16真实，未证明全可达；逐方法对齐延期。 |
| Z-06 | 既有canonical政策继续，未新增human选择。choice-A requirements[1]明确“保持既有canonical输入政策、不静默规范化”，ADR27要求精确n3；base已有language.lower。语法合法与canonical可提交分开，不把未来可选政策变更新增当前前置；更不把本报告当新批准。 |
| Z-07 | 文件行数信息级不变。 |
| M-01 | 历史状态文档/引用确已完成；最新远端状态需后续ROOT维护，不能据此覆写旧轮次数字或宣称原工作未做。 |
| M-02 | 维持不采“无hash/删除审计wheel”；正式lock段258有hash/size，日期列非压缩证据，三STORED/上游DEFLATED已独核。 |
| M-03 | 维持4299/4300应用边界可选建议、非阻断；4301已有owned/stdio/new/edit及真实GUI，不能抹去现有覆盖，不自动补测或改cap/canonical。 |
| M-04 | standalone EOF既有OPEN保留；不把它升级当前UI/term补句号入口的已构造反例，不泛捕全部IndexError。 |
| M-05 | 维持部分观察及早期definitions OPEN；与R05-06相同，不采后置catch已全面受控的因果。 |
| M-06 | 维持校验分层事实、非当前漏洞；Store._fact权威内容校验，现有TS→真实Python与golden测试已存在；edit不重算原ID，无新写入口。 |
| M-07 | 桶导出组织形式是事实，无同名冲突反例；兼容性维护建议，不直接缩减既有/v2导出面。 |

## 必须保留的门禁及授权限制

1. 旧CI36不是aff实际运行；Windows79F根因及其真实失败栈/有效编码仍未知，Quality cancelled及包恢复skipped不得变绿。诊断首败早停只能定位，不能替代完整Windows或三平台验收；合并必须满足现行门禁。
2. “仅增加诊断且产品源码与cb8相同”不关闭原F，也不使它必然重现；R04审查结论不自动继承。作者模型结论保留原字节，事实纠正由ROOT逐意见处置，必要反馈须另按授权，本审不向外审传结论。
3. ROOT O037接受了真实新build6GUI、原包桥接与边界，不等于新包运行或新的用户门禁豁免。Windows/完整CI、同版包条件、fresh双审与逐意见处置由ROOT核实，当前报告不批准push/CI/merge、repack/package、测试修复、预算或新诊断执行。
4. 状态文档/AGENTS维护不得冒充只读审查即可写源。当前仅新增此outputs独审；签名/公证/法律/参考设备/容量与旧库恢复/UNKNOWN-HOLD/Undo GUI/全部ownership家族等原限制全部保留。

另：报告§6.1(5)“macOS/Linux均UTF-8环境”也须限已有被观测运行，不能泛化所有机器/语言环境；本审不新增平台编码探针。报告清单与统计不是13项之外新增功能/验收清单，原“仅真正相关门禁待闭合”的范围原则可保留。

本次仅静态Git/源码/JSON/ZIP元数据及已封证据读取与hash；未读本轮ZCode、未访问其任务、未运行产品/tests/build/install/GUI/旧probe/DB/远端，未写S2或修改原稿。ROOT独占总控状态/后续授权和意见接收裁决。
