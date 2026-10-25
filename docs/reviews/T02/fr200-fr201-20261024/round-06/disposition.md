# T02 R06 全意见事实处置与阶段边界

本轮固定 base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` → head `831813c60a32155a579a69fc9e2cbc879b8139bb`，tree `944724a8d0e2d03502de3cf6551e0cde97e5e2f4`。所有处置限报告事实与既有门禁；没有修改实现、测试、配置、依赖或标准，没有产品重跑，没有远端授权。

作者结论各自保留：ZCode 为 ConditionalPass（仍有合并条件）；MiniMax 为 verification-incomplete／不放行合并。不能汇总成无条件双 Pass，也不能把本地检查、作者结论、ROOT 阶段接收、push、CI、merge 混为一事。最终版本针与自然终态见 VERSION-MAP.json；Z 原稿和所有修订、MM 原稿＋两版附录均原封保留。MM 附录本身不重载160项，必须和完整首稿组合阅读。

## R06 ZCode P1–P8

| 项 | 事实处置 | 阶段、归口与时点 |
|---|---|---|
| P1 新8318 Windows缺证／旧79F全因未证 | 采纳。O041/O042是macOS本地同源证据；O040是父934新事实，三者不互相替代。旧CI36进度79F没有完整首栈；只定因934首败发生于断言前trace写出，不追认其业务断言通过或旧79F全同因 | 合并前真实CI门禁；ROOT按正常精确票另行安排。旧未知残留可据现原件登记，不须补造原因 |
| P2 诊断参数与完整验收 | `-vv/--tb=short`日志参数、`--maxfail=1`仅失败早停，无筛选；不能凭标签判“绿”即验收，也不能凭标签永远否认真实全集零失败。ROOT已明确3769全收集、逐项通过或有据原条件skip、无失败/早停/取消/超时/NOTRUN，ruff/check/format及后继type/build/E2E/package/verify全部真实success、三job成功才接收。当前尚无该运行 | 未来证据接收标准；不必为标签自动改CI或新增用户政策前置，不提前放行 |
| P3 definitions早期坏wire | 采纳原OPEN，限早期preview预演内Store校验的未分类异常，不能说clean Diff后confirm才坏；manual/edits守卫不等于definitions已全守 | T01既有核心维护归口；原始triples／Agent接线前处理，非本轮必改源码 |
| P4 ownership通用定位 | typed Manual/SingleDeclaration均有witness；裸旧detail会INVALID_STATE→unavailable。Conflict类缺ownership键不代表_application实际业务最终INTERNAL_ERROR；两分支均OWNERSHIP_CONFLICT | T01详情合同＋T02消费；新增相应家族接线前按真实出口处理，现非阻断延期 |
| P5 错误码集合 | UI17／契约26／交集10／额外7／缺16成立；未证16全在当前路径可达，不一次性泛加白名单 | T01契约＋T02方法出口；对应方法接线前核对并补针对性证据，非阻断延期 |
| P6 SQL无ORDER BY | SQL事实采纳，未给稳定排序合同或构造性反例；不升级已证跨运行产品缺陷，不新增本轮排序验收 | T01 Store维护；下次触及witness选取时考虑确定顺序，当前未确认观察 |
| P7 canonical | 既有精确term(value).n3政策继续；en-001/de-ch正控与混合大小写受控拒绝分开。未来改政策才新人类决定 | T02／ROOT沿既有决定；当前不重新询问、不静默规范化 |
| P8 规模／EOF／边界／状态／PATH | 按下方逐项旧意见和MM对应项，不用集合标题掩盖差异；行数不推正确性，当前状态只能追加新时点 | 各原归口；不为非阻断信息重构、重包、重跑或无限改稿 |

## R06 MiniMax D1–D12

| 项 | 事实处置 | 阶段、归口与时点 |
|---|---|---|
| D1 新head未CI | 采纳合并条件，非新源码缺陷。作者最终§7.2明确整个base→8318无必须push前修复的技术阻断。旧79F以新绿不能追溯全定因；保留原缺栈残留清单 | ROOT正常票／新CI后合并前核，不使用未答复fast-track例外 |
| D2 状态／历史manifest | 作者已撤回“伪装当前／与远端相反”。历史aff manifest永久绑定aff；status末aff快照也属当时记录。真实缺口是当前8318/O040/R06追加节，非重写历史 | ROOT指定唯一文档维护者，在收到本轮归档票后追加；下节给具体方案 |
| D3 definitions时序 | 作者撤回晚提交分歧，正确为transactions.preview内Store.commit→_definition先抛，之后才会supported；既有早期坏wire→UNKNOWN/HOLD继续OPEN | T01原归口，原始wire／Agent接线前；本轮静态链，不冒实际新反例 |
| D4 ownership最终码 | 作者更正当前_application两分支最终均OWNERSHIP_CONFLICT；旧detail无witness/unavailable成立。码表缺键只在逃出包装的条件下可能相关，不外推当前路径 | T01＋T02，随对应家族接线处理；非本轮源码前置 |
| D5 无序查询 | 不因作者Top10保留“中·产品”标题就宣称不稳定已实测。维持SQL事实＋未确认观察 | 同Z P6，T01下次触及选取时维护 |
| D6 standalone EOF | 两处裸索引残余属实；作者已撤回当前用户必可触发。` .`封装与未构造反例不是任意恶意输入形式化不可达证明；仍保OPEN，不泛捕IndexError | T02 vendor补丁／T01入口；新增不经现封装解析入口前复核，不能写已修或无风险 |
| D7 缺16码 | 集合事实成立，不等于16条当前可达缺陷 | 同Z P5 |
| D8 两TS PATH python | 两处真实代码仍在；R05“作者已改正”是报告表述更正，不是源码已修。O035 ENOENT与后续正确UV调用并存，不冒Windows79F根因 | T01原测试维护者；下次授权触及两测试或新环境适配前处理，当前非阻断维护 |
| D9 Ruff369/379/380/386 | 分别真实运行计数，无差因结论；旧aff文档不含未来计数不是历史错误。本轮当前节可引用380/386并保原件 | 文档唯一维护者，归档票后追加，不覆写旧数 |
| D10 D/E/G与失效联动 | 接受本轮映射未覆盖D/E/G以及FR200 GUI编辑→推导/保存查询/SHACL/报告具名下游未验。作者已确认ontology/facts规则、同事务版本递增/_invalidate以及test_storage九行正负例，不能说全无证据。C不是每行未执行，已测层级/domain/range/type/metadata不能后移 | T01公共失效＋T02编辑和各下游owner，整条父FR／对应消费链验收前逐项核；本轮只披露未验，不扩功能、不冒全部附录完成 |
| D11 4299/4300 | 应用层缺这两边界断言是未来最小维护建议，4301拒绝和合法后继已有实证；vendor边界不冒应用边界。未做mutation不保证未来任意改坏必失败 | T02输入边界原归口，下次授权触及整数守卫时考虑；当前不升cap、不自动新跑 |
| D12 正面结论 | 六keyword AST、已通过本地运行、旧包身份等按原资格保留，不外推全部安全/全平台/法律。供应链哈希和内容差异与体积计量分开 | 已完成证据与独立HOLD分别保留 |

## 历史35意见逐项承接

R04与R05原稿、原处置保持字节；下表是8318/R06当前处分，不回写旧时点。每条详情及源码位置见两份terminal01独核和MM最终附录独核。主题合并不删除位置，也不把35位置称为35个缺陷。

| 位置 | 当前处置／归口与事件时点 |
|---|---|
| R04 Z01 | 无序查询观察未确认；T01下次触及witness选取，同D5 |
| R04 Z02 | 43692分页信封的误因果撤回；262144整文档/16MiB预算另保原边界，已有round05独立行，不复活已撤回缺陷；T01详情预算下次授权维护 |
| R04 Z03 | definitions早期wire OPEN，T01原始triples／Agent接线前；同D3 |
| R04 Z04 | typed witness/裸旧detail分开，T01/T02对应家族接线前；同D4 |
| R04 Z05 | 集合差与可达性分开，T01/T02对应方法接线前；同D7 |
| R04 Z06 | 既有canonical继续；未来真改政策才新人类决定 |
| R04 Z07 | 2993/1887/1748规模信息，不新增重构 |
| R04 M01 | 从原归档待ROOT到最终状态追加完成是历史演进，不互相矛盾；新8318当前节另追加 |
| R04 M02 | 不采无hash前提；uv/PROVENANCE哈希保留，不删.1/.2/upstream审计件 |
| R04 M03 | 4299/4300未来维护，4301已证保留；同D11 |
| R04 M04 | standalone残余OPEN，未证当前UI可达；同D6 |
| R04 M05 | 早期definitions不受后置catch覆盖，T01原始wire接线前；同D3 |
| R04 M06 | schema形状与Store内容身份分层，真实双端ID校验/原IDedit已有证据，非当前绕过漏洞 |
| R04 M07 | 桶导出兼容信息，未证冲突，不直接缩导出面；契约owner下次API整理时评估 |
| R05 Z P1 | O040首败定因，不追认旧79全因；新8318完整Windows仍缺，ROOT合并门禁 |
| R05 Z P2 | 934 Quality718s含recovery成功为新阶段证据，旧CI36取消留历史；不迁移成8318 CI绿 |
| R05 Z P3 | 早期definitions OPEN，同D3 |
| R05 Z P4 | 通用定位合同OPEN，同D4 |
| R05 Z P5 | 缺16按出口延期，同D7 |
| R05 Z P6 | canonical语义观察，不新增当前批准 |
| R05 Z P7 | 当时有效pytest诊断选项已变，不能说有效命令完全未变；规模信息；P2由ROOT实际全集口径处理 |
| R05 Z P8 | 历史aff状态永久保留；当前时点按归档票追加，同D2 |
| R05 MM01 | 首败假设被O040一个真实栈部分超越，旧79全部原因仍未知；新CI门禁保留 |
| R05 MM02 | 934两success/Windows failure是新阶段事实，旧两cancelled不抹除；8318待新CI |
| R05 MM03 | 无8318新包，原094持续有界桥接；不强制重打旧包制造新口径 |
| R05 MM04 | 当前入口追加和原Ruff差因未知分别承接，同D2/D9 |
| R05 MM05 | 缺码非阻断延期，同D7 |
| R05 MM06 | definitions早期OPEN，不采晚确认分歧，同D3 |
| R05 MM07 | Manual/SingleDeclaration真witness与裸族分开，同D4 |
| R05 MM08 | SQL事实维持未确认观察，同D5 |
| R05 MM09 | 整wheel/payload/解压量及压缩方式分层；保历史vendor原件，见下方计量限定 |
| R05 MM10 | AGENTS为保护的未提交overlay，链接维护非候选新产品缺陷，不据此重开实现 |
| R05 MM11 | locator无object是最小定位信息边界，正常授权完整Read不因此禁止对象值，不新增显示需求 |
| R05 MM12 | 两TS仍PATH python，报告更正不是源码修复；同D8 |
| R05 MM13 | 核心规模信息，不据LOC推正确性 |

## 160项与残句的证据限定

Z首稿为表格1–160、MM首稿为独立编号1–160，均已完整读回且纯文本核无缺重；修订只对相关事实有优先效力。清单适用性不等于160功能运行，也不据组织角色不适用取消实际因果调试、模型声明核验、数据不外发或法律责任。

- Z扫描正确口径：39 write_text=19显式UTF8+20默认；12 ensure_ascii=False均显式UTF8，其中6本次新增。窄模式残留0，不代表全部API、动态别名、TS/SQLite/C扩展/未来数据无编码风险，更不证明79F全因关闭。
- 产品/依赖/锁自cb8未变；cb8→aff有10行CI诊断变化，aff→934纯文档，934→8318两测试六keyword。不能总写CI自cb8未变。980PASS在首失败参数之前，language:47是调用行，不是47个用例，也不证其后语言全过。
- #16单写者/启动期迁移不证无锁；#31受控拒绝FullRead不变和preview围栏不证四连点去重；#32只证明实际已测页，非400页。#41用户值参数化和标识符转义分开；#42只读示例安全非任意上传扫描；#71失败终态非完整DLQ重放。#47/#80测试trace不是完整生产审计/可检索日志平台。
- MM #82/#140的旧ADR health/README骨架不能作当前feature能力事实；当前App接Ontology页、business3/O042实际业务存在。尚未整体合并2/17仍保留，不相互抵消。
- MM wheel计量：upstream整件615416B/142成员/解压2358325B/压缩payload596328B/DEFLATED；fr201.3整件2379774B/142成员/解压2360506B/STORED。原稿2358909不采；透明parser补丁确改内容，体积主要源于压缩方式，非“内容完全相同／仅压缩”。
- Dependabot实际weekly npm/actions存在；该yml无pip/uv条目，不能只凭一份yml断言平台安全告警绝对不存在。限定本轮未证漏洞扫描配置且通过。
- Z“成功概率显著提高”只是修复已证原因后的定性预期，没有概率测量或统计显著性；不量化，不当Windows已绿。
- MM原稿35历史处分“缺失/相互矛盾”中的若干是原稿/最终版历史演进。R05已承接Z02整文档预算、有效pytest和mutation未做的限制；不为无实质新问题重复设门。
- MM最后列目录看见Z文件名/大小/mtime，未读正文的声明与归档保持；不能写完全未见peer元信息，也不能从metadata反推已读同行意见。MM自选额外r2报告文件已披露，不能说整个R06仅写指定一文件；原件和附录均保留，不擅删。
- 最终round06目录列表另见隐藏`.mimosa`目录；未打开、未读取内容、未删除，创建者未独立归因。最初“目录恰三个报告”的静态假设因此失败，核对后仅三份明确报告逐字节等封存副本；该私有状态目录不得纳入归档/commit。1363受保护源、5build、index与旧App守卫仍通过，不把该目录假设失败称产品测试失败。

最终Z作者已在原SID实际采纳计数/CI分段/ownership与#16/#31/#150/#159更正，仍保ConditionalPass；P2明确接受ROOT显式未来全集条件并入P1，整个候选无push前技术阻断。§7开头仍合称P1/P2阻断、Top10仍保旧ownership“无错误码映射”残句，以最新具体P2/P4及§11优先；不重新向作者往返。窄扫描、未测概率、生产日志与组织/产权泛项仍按上方证据范围限定，不扩验收。

Z独核自身曾漏读status末aff节并误说只有cb8；主agent定点指出后，独核保留12476B原版为`independent-zcode-terminal01-review-original.md`，更正当前稿为13262B，并在最终增量独核全文记录错误与修订。实际status末aff节存在，“最新入口停aff”主旨成立；新8318/O040追加尚待票，不将独核误读当外审缺陷或源变动。

## 当前状态追加方案（尚未执行仓库写入）

待ROOT明确归档票后，由唯一维护者仅追加`docs/reviews/T02/status.md`及`docs/m0-checklist.md`当前时点；不改R04/R05历史前缀或manifest。追加应记录8318/tree9447/31提交79叶1363源5build；O040父934远端三job两绿一败及旧79缺栈残留；O041实际执行Git934+精确物理修订的151PASS/fullcheck自然0与提交后源桥接；O042实际8318原6GUI通过；R06两个新SID、完整报告/修订原判、20新意见与35旧位置处分；额外r2命名及元数据可见性边界；ROOT是否接收本轮技术阶段和随后另票动作。新head当前无CI，不能预写push/CI/merge通过。

旧79F残留记录：CI36只有language6/manual72/read-work1进度标记，没有每例完整首栈/最终pytest表，故其逐例原因未证。O040实际只复现一个language-first-digit-manual调用，在manual486追踪写先报cp1252 UnicodeEncodeError，业务拒绝/Read/身份/HOLD/合法后继断言尚未执行；新编码修复是对此类触发的静态窄修复。未来新绿只证新run，不倒填旧逐例原因。

所有开放项依原分工的事件时点具名登记；以上归口不冒负责人已新ACK或新开发授权。ROOT签收时可将归口和后续事件窗口写入正式票。任何真需要新增代码/测试/配置/标准的处理，须新候选按原门禁；本处置不自行执行。

## 保留边界

签名/公证/wholeApp法律/_distutils、跨OS/参考设备/macOS15/Win11、Q5/D2容量/旧超限库恢复、损坏SQLite物理资源保护、unknown parser/N3/Store/坏快照、Undo GUI/未验ownership家族、native engine/named App未知退出码均保留。FullRead逻辑相等不证物理DB零写，已知PID缺席不证所有自然0或未知后代全部回收。旧0e7/O027/093/text001/R03 ZPass/MMFail、O022被拒probe缺raw均保原件，不复跑或改写。整体合并可用仍2/17，Goal/发布未完成。
