# M1 真实数学组件观察

本轮在根精确授权下新增纯输入fixture和测试，149项采用输入保持只读。真实链为prepare_profile_material → execute_admitted_profile_job → restore_profile_result；名称不提供正式T01 Job/Store/worker/selected权限。输入只来自固定9333的1331 operands；四golden只在计算完成后选择独立断言，没有用于RuleSpec、材料、L、allocation、生产payload或恢复输入构造。

新树为`.worktrees/T05-profile-M1-math`，branch `feature/weekly-t05-profile-m1-math`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。149按sourceRef原字节采用固定为`6eb4d6bfd209d06682fbfb9bd666ae54b4982e08`，实际base delta140、另9项同base。目标AGENTS保1056B/1b3c0291…，执行最新15852B/78df及common17891B/e437；全文携带于本轮reviews/guidance，原第九节、无桌面和指定双审/CI/推送门继续保留。原Goal没有操作。

两个新路径为`tests/fixtures/quality/profile-M1-math-inputs.json`与`packages/engine/tests/test_profile_M1_math_explanation.py`。纯fixture490953B/SHA9f198fcefa50ca30a87acfa3cef021360100a9dea3fb5ed829c5f62fc02b0d9f，与原1331输入逐字节同一。受控151=149只读+2新增；实际相对base delta142，不混计数。

## 实际执行和边界

每个输入由真实typed规则常量进入真实producer，绑定一次真实anchor事实。main是该单比较规则的实际接受/不接受；false没有ComparisonEvidence，不能把单比较acceptance布尔冒充持久false trace。独立标记的eq-self操作分别观察两operand，提供完整Number分子/分母/负零、Calendar全部分量、domain/language、原TermInput的None/空串/language_raw/source。source引用实际fixture pointer/摘要；无法取得原token时text=None，不造字节span或来源认证。

真实producer返回的payload/rows/preimages、原allocation和完整11字段child用于strict fullview恢复；RestoreExpectation只绑定这次真实produced字节和实际输入，不自签origin。外7/内15/child11以完整类型化结构逐字段比较，batch/heads/basis/source同样完整比对；不只比较hash。每次原L、C准备/生产及R费用、保留和live计数留在实际观察中。返回引用保留责任与R逻辑live0并列，不宣称物理释放、H租约、RSS或容量通过。

独立依赖由本树现有npm/uv锁及独立缓存建立；未升级依赖或借别树可变venv。npm安装使用offline/ignore-scripts；没有Electron产物启动、e2e/native/HMR、模型或凭据调用。实际argv/cwd/双流/exit逐尝试见`docs/reviews/T05/profile-M1-math-observation/commands/`。

## 首跑与处置

首候选`b0fcb7dc1dd8b4ebe3436e996926dba55f9e19d6`新增测试20670B/e1780f94…；1331项实际观察全部完成。针对测试结果为1330passed/2failed（包含额外1项输入完整性测试）；数学case本身1329pass/2差异。

| 集合                     | 首跑独立观察                      |
| ------------------------ | --------------------------------- |
| 九域分类                 | 486通过                           |
| 六numeric三关系实例      | 648通过（216细化槽，各三关系）    |
| Number/IEEE边界          | 38通过，含非有限/溢出合法受限失败 |
| Calendar                 | 15通过                            |
| 混型比较/有符号零        | 30/24通过                         |
| term比较/语言ABNF        | 54/4通过                          |
| 词法、类型与operator错误 | 30通过、2入口层级差异             |

error/28的relative IRI在实际producer返回ABSOLUTE_IRI_REQUIRED，而原pure golden为INVALID_RULE；error/31的operator=1在材料准备阶段返回MATERIAL_INVALID，而原pure golden为INTERNAL_ERROR。两项均无生产payload/restore结果。实际私有诊断、公开error和C/R状态在first-counterexamples.json及原件中保存；这不是先行判定I05组件bug，也没有把任意error视为通过。根另行完成规范层级独审并给出固定决定（2461B/SHA c10a07b1ad4da626ca005d5ee2b2bd62db5a72d811680f0b1085e4a322f85faa）：只准两个固定ID使用完整admitted入口合同，原pure golden继续保留且明确未由此入口执行验证；四golden、149输入不改。

首正常check实跑：1125前端测试通过，Python6217passed/2failed/44既有skipped；两失败仍为上述两项。没有新增skip/xfail。lint、格式、类型、构建和ruff阶段完成，normalcheck整体exit1，不能称通过。verify:sources实际通过。

独立审查另发现新测试自身1P2：main=true时原先只核Boolean/fullview自洽，可能漏掉错误左右typed PV。仅增12行将main左右完整PV分别对照已独立验证的对应eq-self PV，unary两边亦全相等；新候选`e686a112fdbffdcc2b2bd042e5c131c1e2d586b1`、21143B/SHA5ec7206ee82d4b6a29604f670fc8cbced68c5685e1fe6de291dc1b596472f868。独审已局部核Git/字节与149不变，关闭该P2；该候选全量仍为1330passed/2failed，实际1331条归档为p2-full；只关闭测试覆盖缺口，不关闭两项层级差异，不覆盖首跑。

## 最终候选与实际结果

最终两路径候选`051ae4cb9b5e58560c8e45cdc56fd98522777b5c`。测试24239B/SHA `250a760bd1c0f2710a9585a67650c3d0b743f376c1ecdd308fdf0d3d8aaf6047`；fixture仍为原490953B/9f198fce…，149来源仍逐项同批准字节。仅errorOperandCases/error/28和error/31启用固定入口合同，精确核status/stage/exception/reason/diagnostic/public DTO、无产出/恢复及main比较器计数0；不动态从actual生成预期。error/31左右operand仍作为独立eq-self成功操作观察，不混为其main到达比较器。

对真实比较器仅以wraps调用原函数并记录阶段调用次数，无替换返回值或注入expected；所有3821次操作均有真实计数。两个前门的`pureReasonExecutedByThisEntry=false`在完整原件和索引中保留：error/28纯层INVALID_RULE、error/31直接比较器INTERNAL_ERROR均不能据本入口通过声称已执行验证。

最终专项1332passed（1331逐ID观察+1纯输入完整性），194.17s；九组计数分别为486/648/38/15/30/24/54/32/4，全部本入口独立断言通过。最终正常`npm run check`整体exit0：lint/格式/类型/构建/ruff通过，前端1125passed、Python6219passed/44既有skipped，303.35s；本测试无skip/xfail。最终`verify:sources`核12源通过。原失败日志保留，未把历史exit1改称通过。

| 实际观察口径                          |        数量 |
| ------------------------------------- | ----------: |
| 唯一family/id                         |        1331 |
| main操作                              |        1331 |
| 单独operand eq-self操作               |        2490 |
| 全部真实组件操作                      |        3821 |
| 成功生产并完成restore                 |        3329 |
| production拒绝 / material拒绝         |     491 / 1 |
| 实际比较器调用 production / restore   | 7116 / 6658 |
| 到达比较器的操作 production / restore | 3787 / 3329 |
| main到达比较器 production / restore   |  1297 / 839 |

以上列不可相加为唯一案例数；材料阶段比较器调用0。3329成功恢复包含单独operand操作，main成功恢复839。false main有真实接受/拒绝结果但无持久false ComparisonEvidence，独立operand观测不伪装为false trace。

## 原件与未覆盖范围

first-full-actual-index.json按1331 family/id列完整actual/expected/错误，first-full-archive-members.json绑定17976个原件member；first-full-actuals.zip保完整观察、生产payload/rows和preimages。首轮共有3329次成功组件恢复、491次生产拒绝、1次材料拒绝；这些是独立组件操作次数，不是不同原产品场景数。

最终final-full-actuals.zip为120953467B/SHA `65d81a465c2551fee9dbdb6c6be42383efb326439c8bbc86a955d5362af707ef`；17976成员、未压缩1696398994B。三版ZIP均全量验证每成员字节数、SHA-256及CRC，索引按1331逐ID绑定完整原件；first/p2/final原始ZIP保留于同一reviews目录。ZIP为本地原件，不纳入Git对象；其精确路径/字节/摘要及索引纳入过程映射。源fixture/test和可审核过程、双流/argv/exit、索引均固定本地提交。独立审查记录与最终交付回执见同目录。

正式T01受理、Store保存/重开、ownedworker、新selected、directstep、SHACL/query13格、date支持政策、E5/repair/真实中间状态仍不在此窗口。现schema只有leaf basis；不从expected补directstep，不变carrier/实现版本、原L/Q6或锁。原83状态和父FR/57P0/目标OS/真人/指定双审/CI/上线门没有因此关闭。
