# T05 独立内审与处理

独立 reviewer：`/root/t05_internal_review`。只读本功能路径与对应 PRD，未改文件、未开 GUI、不接触凭据/外发。首轮明确不通过，原意见保留；不替代指定外审。

| 严重度 | 原问题及实际反例                                                       | 开发处理                                                                                                                                           | 复核状态                             |
| ------ | ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| P1     | 非法 xsd:integer literal 返回受限错误但 RDFLib 日志包含原值、堆栈/路径 | `quality/rdf_terms.py` 用 ContextVar 限定解析中的 RDFLib term 诊断过滤，不关闭其他线程/普通日志；新增 caplog/capsys 零输出及退出后日志仍工作的测试 | 原反例已由同一独立 reviewer 重现关闭 |
| P2     | 隐藏 maxCount 参数为空，切到 rule 仍阻断生成                           | 抽取纯表单序列化 `draft.ts`，仅约束分支处理模板；增加切换反例断言                                                                                  | 原反例已由同一独立 reviewer 重现关闭 |
| P2     | id 为孤立 surrogate，计划 UTF-8 哈希抛原始异常                         | 所有本地 text 入口统一拒绝 surrogate，返回 INVALID_TEXT；覆盖 id/label 回归                                                                        | 原反例已由同一独立 reviewer 重现关闭 |

首轮 reviewer 实跑 Python 42、Vitest 3 通过，仍发现上述缺口，证明已有测试不等于需求覆盖。首次定向 ruff 有 4 处长行格式错误，经格式化修复；未执行者不记通过。

基线缺口：真实执行器、Store/IPC、失效重算、G.2 完整真实结果和桌面项目切换均未验；不关闭父模块验收。

## 复审新增问题与处理

独立 reviewer 发现同类 Unicode 可从 `dependencyVector` 的 rule/constraint/ontology 键绕入哈希，复审结论仍不通过。现对每个键在 family 前调用 text 并用固定诊断路径；新增 rule/constraint/ontology/facts 四个回归，Python 49 passed。未将首次复审结论改写成通过；等待完整末次独立复核。

复审额外实际探针：非法 literal 日志/stderr 为零；其他线程、独立 Context 保留日志，异常后 ContextVar 恢复。均由 reviewer 只读执行，不是产品真实执行器证据。

## 末次独立结论

同一 reviewer 对最新完整代码/测试重新只读复核，明确“通过，仅限 T05 私有准备范围；未发现新的实质问题”。原四项反例均重现关闭，独立复跑 Python 49/49、Vitest 5/5。reviewer 报告 13 文件组合 SHA256 `a78309a15ead8e66c231b0484fc0a0658287a86bbc6059968904975b0f4a2b60`。

结论不覆盖真实执行、持久化/IPC、完整 G.2、桌面验收、全仓 check 或指定双模型。新增差异报告核对是只读证据补充，未改变受审实现/测试。

最终补齐常见 datatype IRI 后，独立 reviewer 再次全文复核通过；53 Python/5 Vitest，13 文件组合 SHA256 `079d7c74aa463f800f669de156d2291f16daaba22253ecc5dcdf15e2bc0140b2`。本地完整 check 同版本实际 635 TS/1105 Python通过，非reviewer代为声称。

## 获批 T09 输入适配审查

独立 reviewer 再次检查完整本线与新增固定输入：实际用 `git show 873c8c0…` 核对 manifest/17文件/PRD源原字节一致，未消费未批准服务或Store helper；既有实现与 `dcc5ec8` 无差异。同一告警join、字符串001、R-05/06稳定未执行计划保持；50案例均runtime-pending，无actual字段，expected未当作运行结果/存储。独立复跑75 Python通过，明确通过仅限准备与输入适配范围。

32受审文件组合SHA256：`ce69de6c0a52c117807e67033a0e5e6e3ac2f132e9ff7441b6cf472af5e4cbba`。未修改文件、未开GUI，不能替代指定外审和真实执行验收。

## FR-505 代表输入与语义提案复核

独立reviewer全文只读复核，明确通过仅限私有准备和代表输入提案，未发现新实质问题。实际111/111定向通过；12个比较正反例手算一致；两个不同告警未误拼为一条High/Open；多输出共用R-risk-multi/A01四条输入依据；ontology/catalog/reset一致。原13核心文件未变，无第二执行器、Store写入或expected到actual路径。

35受审文件组合SHA256：`06f3d269007858672a0793f7c6ae4180e8ed62d985579ea08dbd076155b021bf`。此结论不证明真实推理、正式集成/公共协议、指定外审或发布通过。

## 具体保存参数与真实 Store 复核

同一reviewer对完整最新本线只读复核通过，仅限私有准备与隔离真实Store探针，无新实质问题。实际导入源与批准5f逐字节一致，格式2/SHA4abf1082...cf6842；临时SQLite、启停修订/历史/旧base、事务内三阶段故障及重开、提交后marker/同operation幂等均成立。未消费未批T01/格式3，未新增生产入口或存推理expected；引用派生/正式接线仍待验。独立118/118；原13核心文件未变。

38受审文件组合SHA256：`ed0a7bf930f0af73ee89489bfcdbadae6ae4a38ddf064a55f0571ee092b928a8`。异常注入不是实际进程崩溃/IPC丢包；不替代指定外审或正式集成证据。

## 总控 R1/R2 后独立复核

此前内部审查没有发现两点比较输入的算子混淆，保留该遗漏事实。总控独立审计后，新增6格保留原12格，独立reviewer逐项复算全部18格及完整输入/输出/依据，确认六真值签名两两不同，30个有向算子替换均可区分，R1/R2在本线修复；实际148项quality Python通过。38个受审源文件组合SHA256 `71021645ca1af60e652a6c6064b59ab10601faed79fb5b06eae77fb1085ebe5b`；固定提交为`fff89f6`。本结论不替代root对新输入的复核或真实执行验收。

## 同一执行器扩展契约复核

独立reviewer全文读取offer报告及契约，未读四个未批实现。首轮发现P2：`__main__.py`被Markdown解释成强调，责任路径含混；已改完整代码路径，并将T00协调与T01/I06当前维护清晰分开。复核最新全文及第9节标准参考后明确通过，可交owner逐项回应，无剩余明确问题。

受审契约SHA256 `1a87a035a6a5da54ce78c19ba107855ab19f080b37c28888e0a7a87a71f470c6`。该结论只审提案，不代表类型政策采用、四路径交接生效、代码实测或指定双模型审查；未改文件或重复运行代码测试。

## SHACL 范围差异独立审查

reviewer实际核对两个差异、上下文、批准5f registry及FR-500/D后通过：范围名一致，未绑定真实已有result时禁用，无计划推导冒充可用输入，完整双范围验收保留。QualityWorkspace.tsx SHA256 `e6e266244a2b04e7b06104b205b7ff0c13f3e85509db3130aa9315249e6b55e7`，interface-proposal.md SHA256 `5f8d0208ac449a112aad4716a44bad48e47204daa10e5e0eeae3cef16c6c24da`，提交`7c94a88`。

本次只读差异审查未重跑代码测试；开发线最新全check退出0（635 TS / 1200 Python，Python 41.55s）。未运行真实双范围或GUI，不替代指定双审和父验收。

## 草稿输入绑定与headless证据

独立reviewer通过固定2fcd36b的三文件实现/夹具：全部editorInput进入source，修改和增删即隐藏旧draft/error，失败替换旧准备结果，表单保留，project key隔离。源码SHA：QualityWorkspace `f4120ffddffcb37e6f56909c7ba48cbc88b15e36187533fc044fbedd6b01d05a`；browser-harness `b590ced2e7aaf53dc2f06503c6ba116dbc24cc6d91809a6ee26b5c40438824b0`；build helper `2a257f40a9b7c9fb8662f0ed08aaa4e647919d32ea5848c9bc5387eb946c3f9c`。reviewer实际读CLI前后原反例、配置及自有实际进程argv，未操作浏览器，不替代真实领域或指定双审。

另独立复核R1/R2恢复归档8载荷长度/hash、四源与fff一致、两raw与原件一致、bundle校验通过；没有重复产品检查，来源明确事后绑定。也承认并纠正先前合同漏查：resources.py在批准5f中已有，只有三个semantic新增；候选增量仍未批。修正合同SHA `392d39e275cd2ccd9d3fbed5a5e4b2ead014e1654854480625a0aac1a40e3e4a`已独立树清单确认，原错误和旧review保留历史。

最终UI封存由同一独立reviewer只读复核通过：715488B/54成员，53载荷内外清单全部一致，6源码与2f及当前字节相等，18个DOM断言均含实际检查代码/成功结果；真实fullcheck635/1200一致。最终关闭回执存在，reviewer另实查PID45676/45677消失；未重复浏览器或全量检查。归档SHA `e046be791bd6336d909365413382b42e10a5cf8dbe85142ea16e71647ea8de56`，仅认可synthetic组件范围。

## C2 确定性依赖事实复核

独立reviewer只读三份报告及本线四文档差异后通过：字节/hash和26实现/2e冻结身份一致；候选manifest31bd、原probe manifest03150、报告manifest57338、findingaa96未混淆。合同不把owner报告当T05重跑，不声称C3获批/四路径生效，旧offer仅历史来源、未来核真正批准身份；不固化旧witness或擅自采用全RDFS证明枚举/类型政策。新增后合同SHA `f1393622622d69c4c60f334a20a0385d45310ae795c4e3cb96e3c59669cf0485`。没有读取未批实现/归档、改代码或重跑测试。

## 固定接口事实后的有限决策表复核

总控明确只要求新事实驱动的最小接口设计，Goal保持blocked。本线全文读4504B owner响应、27634B独立事实及11024B总控读回，哈希均匹配。独立reviewer只读三报告、D/M/P表、主合同和receipt；认可basis/rules分层、graph/FILTER边界、完整多head、纯一致性与Store认证、历史读回/完整implementation新消费分区、现有DTO与待接受候选reason/路径的区别，未发现不必要范围扩大。

首轮发现P2：D6“旧_source仅hash id/when/then”误将规则投影概括成整个摘要。已修18/29行，明确规则投影限制，原图/计划及语义身份绑定保留；独立复核后明确通过，P2关闭。新错误定位段保留真实诊断载体缺口，没有擅加错误参数、借用其他detailRef或把失败伪装成功。

最终决策表SHA `6650363f0195f1a2cb21e2eee2dfe5a072d698275ca3a2f5ef389615fe92a17f`；receipt SHA `e1a83ec955f8c0923ef87dc9a21b334e64b87d8c8eb7bed73210a80826f9961c`；主合同SHA `454cb390040f1511ed20b8bab7e969a427eda48a4ece242dcf32de3e773a2ca5`。12组code/required params/enum仅静态目录核对；未运行adapter/Store校验器、产品/UI测试，未读候选代码/库/归档或改变公共协议。此结论是提案可交负责人回应，不是采纳/实施/解锁或指定双审通过。

## 新I05/T01回复、operator/消费者矩阵及worker责任 r2

独立reviewer `/root/t05_internal_review` 全文只读两份固定owner报告（I05 ffc462b/23281B/723368…fc4e；T01 f51dd38/14185B/0f3ab7…6768，使用仅§1），审查本线r2 D/M/P、operator/consumer矩阵、主合同与来源receipt。确认技术接受和Q6/规范pin/真实运行/阈值/公共包装缺口分开；D2跨域六算子失败、D3直接舍入、D4calendar和graph/消费者门、完整firing/身份/错误origin优先及诊断提案边界准确。矩阵新S/L/I/B和消费者格仍待审，未缩减完整任务或批准新协议。

发现并关闭：M6“非合法subnormal/零”歧义改为“不用于合法”；worker新归T01后D8/合同责任清单同步；C2准备C3句加历史标签；交接协议先前bdacff观察与当前生效指纹不一致，实际重读当前2885B/63c194…50da并更新receipt，旧hash保留历史、不声称持有旧完整字节或精确diff。reviewer亦全文读common/交接协议并核execution-state限定生效项；原b24的15574B逐字前缀、ff5f新common、worker唯T01/从批准5f维护/不消费C3/其他路径不扩权准确。三个T01私有测试仅计划，不授旧tests写权/不算通过。

最终明确“本轮有限文档范围通过，无剩余实质问题”。三个受审文档SHA：决策表 `e2c148d409d881ebab97c497b4d2647d85fdc9f514690b9e5f9109f7dc3d43f1`；矩阵 `0d88c843e77da2f05acd6fd3e439e8c573dcb31024aee0f99cf7d49e657bbc6e`；合同 `889d879c33d7ab0b13f0d1473e42df28957c19328a48a469ec068b05e3128318`。reviewer最终receipt快照SHA `5b1a50daaf4dae3205ce1952f57d64e09cb91e655c8ee4b3ba2f03d224aab3a2`；其后仅在receipt追加本次通过处置，原报告/操作来源字段未变，最终hash见checkpoint。

仅文档格式/差异检查，不读候选实现/库/测试、不运行产品/GUI，不改代码或指定外审。Goal工具再次实际读回blocked且完整objective未变；此通过不替代指定双审、原运行/集成/CI/合并或Goal完成。

封存元数据定点复核另明确通过：三md字节未变；receipt最终 `ba7f93175933d51c305d940e6e78c10c7a7d20ffd41c836e3b9569a7d575fd08` 仅将independentReview还原pending即可逐字恢复5b1a50受审快照，来源字段未变。checkpoint/status/本记录与有限范围一致；无新增问题，无产品复测或C3读取。

## 总控设计挑战R1/R2修正与Q6单独立审查

独立reviewer `/root/t05_internal_review` 全文读总控原报告17603B/SHA `70909867a8786f181639810c3c40d188f92c2849311dd148f6bf55fce044705a`、本轮四份设计文档与disposition，核固定383b96c指纹并查必要官方REC条文。此前383b96c本线内审没有发现SHACL datatype/range目标混列及simple/xsd:string可选合域歧义，保留该遗漏及旧报告，不回写旧通过为已关闭。

本轮明确通过：“无新增实质问题；R1/R2文档歧义已关闭”。R1 K/D/R分别为value-node集合计数/term成员、精确datatype IRI/适用词法、SHACL自身SPARQL范围关系；正常false/type-error产生违规，能力失败另列，不以规则D3/D4/E3覆盖，不宽泛拒绝难值关闭五模板/双范围/定位。R2 simple无lang与同lexical xsd:string同一抽象term固定，标签well-formed/小写value/建议内部表示/source拼写/L算子分层，不造第二term或借数值eq归一词法。Q6单具体可裁决；D3/D4既有技术接受保留，规范pin/勘误、消费者实际合同与运行证据仍待。

后续I05反例仅记owner经总控转告，固定反例尚待总控/独立读回；未冒称T05复现/独立核验/修复通过。C3条件派发撤回，冻结输入保留；不扩大到所有新D3/D4、不读取候选或改变文件权。

受审四doc SHA：矩阵 `46a7435b471f420bb9a787b6577300f3e328295594afe3dfff90434029a7c5db`；Q6单 `a0baa0fef56de1100596b2c1a7892c8fbd85f606f6247d7954cbe3d01d9a2c09`；决策表 `2da94a1e9c2383e1996d79f609262002d64e45604151fa7a3514766367c00a14`；主合同 `0c3d7ecf872ff5bfe82c2669b396e5c6c601244b01cc5dcf03d29bbcf8dca0dd`。disposition受审快照SHA `9dc816d8c511105c7b7044a30f775e780528c4efcb841b8cf93155537ea05035`，其后仅更新R1/R2处置、独立通过及文档检查元数据，最终hash见checkpoint。

仅文档/必要官方规范核对，未读未批准实现/库/测试、运行产品/测试/GUI或修改公共协议。Prettier、diff check及hash/原始报告字节核对通过；不构成标准全符合性、Q6采用、指定双审或产品验收通过。Goal实际仍blocked且完整objective保持。

封存元数据定点复核通过：四doc未变；disposition最终 `5ab91bba3ffa1fea4d4707b71404162ab993d696731cae7351bbb49f93f84f20` 仅还原本次处置元数据即可精确恢复受审9dc816…快照。raw报告仍17603B/709098…705a，checkpoint/status/本记录对应，无新问题或不实采纳/运行/指定双审声明；仅只读核对，未测试/读候选/开GUI。

## T01 TA-C/Q-LIFE包装回复增量审查

独立reviewer `/root/t05_internal_review` 仅核固定b35cb4e T01回复、3906B/SHA `3d300cf1070adf54f97fec45d060273f78d0e29fba9bbef502403466084b8d09` raw与相对46403e3的四doc差异/receipt。明确“本轮有限文档增量通过，无新增实质问题”：T01已接受包装职责与I05逐C格真实契约/接线/Q6/公共格式缺口分开，原f51接受保留，M12当前IDENTITY_CONFLICT未变，未来UNSUPPORTED/M9/诊断未误称实现，无路径授权/修复或运行通过声明，Goal仍blocked。

受审SHA：矩阵 `c9f7752b4b69a17b1b51a4ccbd54e51b584028bdb4dd29591452e91f1aba5192`；Q6单 `bb405d3ccc3e3a87c1dc710a72a8d84cc57a47a7e570d988736543a0a8937faa`；决策表 `d983a8aed06901e871932657bac03a69672d7b3270270b346694cdf2c603edcb`；主合同 `4a822aa9b45885858b013b33242455b63d647031f01a64da8caf4b80a07df1de`。receipt受审快照 `ef9074a3e5c0b8d9e0ae7d83b9b04fc28a7bbdb2884d3cbf6dfb6f1e2763ddd8`，其后仅追加本次独立通过/格式/hash核对元数据；最终SHA见checkpoint，未改受审来源/接受项/缺口/四doc。

reviewer未读报告链接实现/测试/外部规范，未运行产品/测试/GUI或改文件。本线Prettier、diff check、source固定Git/raw与文档hash核对通过；仅文档，不替代实际集成/Q6/指定双审。旧157 Q6单hash作为总控当时受审身份保留，checkpoint当前Q6单hash同步新补记，不将旧闭环报告重签为新技术回复。

## I05新增TA接受与T01联合范围独立审查

独立reviewer `/root/t05_internal_review` 只读指定I05固定96fb597设计报告/inputs（15368B/8bf9e608…942c2、788B/dfec670c…90a74）、自有T01 r2 raw与相对bfd5c19的文档增量。两I05 raw与固定Git逐字/长度/hash吻合；未读其他链接实现/库/测试/独立草稿或外部规范，未复现/运行产品/测试/GUI或修改文件。

明确“本轮文档范围通过，无新增实质问题”。新增S/L/I-B/X与K/D/R目标的I05技术接受和T01包装接受合并准确，D3/D4原答复保留；当前numeric shape五类且not ill_typed、日期shape边界/rdf:langString datatype shape未支持，初始_terms准确R/SYNTAX/U与三个旧literal映射、普通SHACL违规不进adapter及逐C格新异常对表/完整goldens缺口均明确。source要求未冒称S1保存全部原拼写，不私加DTO或重签历史；Q6/pin/实现、C4未冻结/未双审、公共格式/路径权未误报通过或生效。

五doc SHA：联合表 `3d768275379bd272ebea9cf0c86005a9c5cfd1f1e20cfa176fd5e6aa7de1938d`；矩阵 `3705af23adcfc3e4f7cd153ae06f82cccb849cfb1dad7ea68ff08c02b09585e2`；D/M/P `88a454b0a8de58bea0f51d1d19938c916ac98c282f83d670d829e558734dd034`；合同 `d14bba9a059b81096e4bc63ebd825dbeacbf92eb7a5b4b0094f26f2e4e0c3304`；Q6单 `230abb0ec802fe0af9f8944a00759043c7f3c2f8ab23fa34b74d3dd69313b61f`。receipt受审快照 `2974d0d90fb9ae0ce10e1fd7699f7cfc0ffdda03627425572a2c12fdf9352cf9`，其后仅追加审查处置/文档检查元数据，最终hash见checkpoint。

初次文档check仅receipt JSON格式告警，已Prettier修正并复查通过，不是产品测试失败；diff/hash/固定输入核对通过，无重复产品验证。原Goal仍blocked，完整原验收不缩减，本结论不替代Q6采用、真实集成/消费者运行或指定双审。

## Q6 adopted profile and private mechanism stage review

Independent reviewer `/root/t05_internal_review` passed the document scope. The GFM P2 was closed by moving three regex branches into a fenced block and separating three token-to-construct rows. A final clarification makes Budget a per-call, debit-only, unshared mutable accountant; inputs and limits remain frozen, and only safe readonly failure fields are exposed. The reviewer separately passed this delta. No remaining substantive findings.

Final profile SHA256 `ea6e921f0fc21c4cd18a04e835e4bdd4730d7f07821d3e9fdc646f7e5480ffcc`; final stage SHA256 `8008e906c7b20dbd9c9ba2d0a1bce0661ec32336f78d477831103cbc9bc27424`. These are document review results only, not implementation authorization, code/test results or normative full conformance. Root independent stage review remains pending.

Adoption/source hashes and the new common/four-path ownership are recorded in the stage receipt. Historical raw sources and Git snapshots remain unchanged. Existing design documents add current adoption references and the T01 foundation/I06 retained-path boundary. All original FR and integration/release gaps remain open; no code/tests/candidate consumption or product retest.
