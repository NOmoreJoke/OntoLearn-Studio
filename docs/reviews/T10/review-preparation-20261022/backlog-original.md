# T10 全量指定双审积压（2026-10-22）

依据人类“把之前没有通过zcode和minimax的审查都补上”的最新授权盘点。**本线从未创建指定双方实际任务，没有指定Pass、Fail报告或可沿用的旧Pass；所有已实现产品及技术工具均在本积压内。**下列拆项用于完整盘点，不另造阶段/Goal或把同一S1拆给两模型各审一半。未来双方各完整审同版全部登记范围；新任务创建仍由root短lease内部串行协调，后台推理不占用整个桌面lease。

## 固定身份与唯一owner

- 全部本线实现的实际base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-transfer-export`；分支：`feature/weekly-t10-transfer-export`；原owner为本T10聊天 `01a15bce-0a94-7870-9694-f100e78f406a`。
- 产品恢复点D：`d3546af3b6fe895957f9626fd4de28bf59dc600a`；产品当前点C：`c3c7e90f721344113c4279d663127f9c8d5bda59`；技术工具/原生证据点N：`66eeedd735370576b49eb39cd4b14cdef9c0d55b`。
- 当前统一固定受审输入A：`a1e7efef4bd47c97b630753c0e7c4dc34de1d8ae`，完整141delta+6不变上下文；本次盘点前实际process HEAD：`f00e1b74213a76ba573dd38bde20191eb39d1cfa`。D1/D2流程点：`ede09f02b1e82680dc0d498d51142ad6238ecf71`。本盘点追加本身仅流程材料，不更换A或解冻C。
- 实查C→盘点前HEAD的apps/packages/tests/scripts/锁/CI没有变化；工作树仅受保护AGENTS未暂存。147项固定Git长度/hash均匹配既有manifest。
- 原授权写面：engine transfer、test_transfer_*、main/project-transfer、renderer/transfer、t10-* tests、fixtures/transfer、docs/{iterations,reviews}/T10；不含公共Store/canonical/main/index/task-service/preload/App/锁/CI。后续共享接线由root按当时唯一owner协调，T10不抢写。

## 全部已实现及保留的技术子阶段

每行均：ZCode taskId=null、MiniMax taskId=null、实际模型设置未读回、完整指定报告不存在、指定结论=未审。计划设置和报告位置统一见下节。

| 盘点项及提交关系 | 全部实际写面（仓库相对路径） | 当前完整有界验收与内审 | 双审就绪缺口/可独立下一行动 |
| --- | --- | --- | --- |
| S1-A 候选ZIP信封检查；D引入且仍为当前源码 | `packages/engine/src/ontolearn_engine/transfer/{__init__.py,inspection.py}`；`packages/engine/tests/test_transfer_inspection.py`；`tests/fixtures/transfer/inspection-expected.json` | 60Py；严格draft/version/role/选项/hash、有界ZIP局部/中央布局、隐藏成员/重叠/路径/保留名/symlink、实际长度/CRC/deflate EOF与尾部反例；初内审2P2及延伸已闭。只是只读信封，不证明业务语义，不开放import/restore/rerun/replay | 已包含登记S1及A全量输入。待root短lease/最终冻结核验后双方完整审；不等待正式迁移全部实现才排此独立积压 |
| S1-B 安全HTML与独立未接线页面；D引入，C修report首LF及攻击fixture | `apps/desktop/src/renderer/src/transfer/{report.ts,TransferPanel.tsx}`；`tests/unit/t10-report.test.ts`；`tests/fixtures/transfer/{report-input.json,malicious-texts.json}` | 当前18TS；FR1001栏目、逐attempt辅助/证据、纯文本/CSP/离线、12攻击文本及中文/引号/前导LF；页面默认选择及禁用状态。初内审及C增量内审覆盖；真实Chrome检查旧3900B/26af实物。未取得真实T09/T08可信投影 | 同S1-A；没有另一个遗失/未登记的产品候选。真实业务报告联验列父门，不能以合成投影关闭 |
| S1-C 不可变报告文件服务；C引入后未改 | `apps/desktop/src/main/project-transfer/prepared-report-file.ts`；`tests/unit/t10-report-file.test.ts` | 43TS；固定bytes/hash、排他0600暂存、句柄/实际字节与路径身份、原子不覆盖、竞态/取消/并发、不明发布协调、fsync/清理pending及单飞；3P2实际修复并复核。Linux真实picker保存/取消原件另属下行，非正式产品接线 | 同S1-A。当前FS自持实现不是生产能力lease；未来适配须真实新delta/验证/双方新同版完整审，不能拿本S1审查先覆盖未来实现 |
| T-A 合成报告/SSR准备脚本；D引入且保留 | `docs/iterations/T10/render-probe.mjs` | 实际合成HTML/panel/invalid输出、CLI不启动应用；原内审明确覆盖该脚本。browser完整脚本/结果及首失败、HTML原件在legacy归档，不是只留截图或计数 | 已在A清单，必须随S1完整审，不因位于docs而排除。无需无变化重跑；需要额外运行证据由原owner按当时授权执行 |
| T-B 隔离Linux构建/编译/直接native工具；N引入后未改 | `docs/iterations/T10/isolated/{Dockerfile,prepare-native.mjs,native-hook.cjs,native-driver.mjs,run.sh,run-container.py}` | 独立工具内审推动补隔离硬断言/超时/固定容器ID/PID/controls读回。attempt1创建前检查失败、attempt2真实保存窗口Enter后超时、attempt3真实GTK保存Alt+s/取消Escape成功，原运行0600、3896B/ad367、exit0；额外SYS_ADMIN/短时inspector等边界公开。61TS/60Py为容器定向，不能冒充容器全check | 亦已在A清单、全部进入待审，不以“仅工具”永久排除。不是正式package或目标双OS；原失败版本不作为现行可执行候选，精确后继见下节 |
| T-C 保留的编译副本/归档证据 | `docs/reviews/T10/evidence/native-compiled-postrun-readback/{csp.cjs.raw,report.cjs.raw,prepared-report-file.cjs.raw,index.json}`；native55/legacy40索引原件 | 三份为同一已停止attempt3容器的事后原字节副本，不是另写实现；输入源码hash不冒充运行时输出hash，Git副本权限不冒充原运行权限。当前A完整包含，旧snapshot两项missing明确保留 | 连同T-A/T-B供双方追证，不另注册运行能力。现存原件已保全，无缺件需以新测试伪造补回 |

实际可执行/产品/tests/fixture作者路径总数18＝11非docs产品/tests/fixture＋7工具（本表T-C是原件副本，不重复计作者实现）。没有本线其他已实现正式迁移器、生产guard、共享bridge、Store writer或独立被撤回的功能线。

## 验证、继承与历史后继

- 当前稳定全check：691TS/1112Python及lint/format/type/build；原日志 `evidence/isolated-native/check-isolated-retry.txt`。一次既有TIMEOUT、单文件8通过和完整retry原件均保留，原因未明。S1尚无正式package/e2e/目标双OS证据；Linux源码native不是包内证据，不把这些父门删掉。
- D初始产品后继为C：inspection/页面/报告测试脚本保留，report及攻击fixture按C更新；旧内审/11攻击文本证据只保留其原范围，当前12例与首LF以C的增量内审及新原件为准。没有指定旧Pass可沿用，也不把旧内审直接推广到新文件服务。
- C的文件发布3P2及更早ZIP/访问器2P2均在最终提交前修复；提交前中间稿仅有实际保存的失败/哈希/工具原文历史，不承诺每个未提交中间源码都可重建。当前可恢复快照为D/C，不隐藏这些首失败。
- native attempt1/2的失败控制版本由attempt3/N替代；失败不撤销或改记通过。现行六工具以N为准，旧out控制副本只作失败溯源，不作为另一个未来生产候选。3900B/26af浏览器与3896B/ad367 native是两实物/两运行。
- 66之后仅文档/原件/政策/输入准备，未使指定Pass失效（因为从无指定Pass）；纯流程追加不触发不变产品复测。以后任何产品/tests/依赖/验收或base变动，必要验证后双方各新任务完整审新同版，不继承任何旧Pass。

## 两指定模型的实际记录与提示入口

- 两应用实际任务ID、会话、终态、实际设置均未创建/未读回；不存在完整指定报告或指定结论。计划：ZCode GLM-5.3/最高+yolo；MiniMax M3.1-Flash/xhigh+bypassPermissions。计划不是实际设置证明。
- 完整提示：`docs/reviews/T10/external-review-task-packet.md`（SHA `6efa041ac48794574f06cc76ac8afdf27d48f603f18ea16de8fda553f7d86f5b`），固定输入manifest（SHA `b2c17f448608370b86ac0549e4f72312e3c8542afa2835138f9fd3b1a4f80623`）。本次未改两旧文件或147项身份。
- 新任务必须同时附 `external-review-current-policy-addendum-20261022.md`，覆盖旧操作政策；双方仍完整审同一全部S1-A/B/C、T-A/B/C，不拆范围、不互泄本轮意见，每轮各新对话/独立任务。
- round-1计划唯一可写MD：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-transfer-export/docs/reviews/T10/round-1/zcode-glm53.md` 与 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-transfer-export/docs/reviews/T10/round-1/minimax-m31flash.md`。目录/报告尚不存在，未造占位Pass；新轮另建新路径。

## 纯方案和未实现父门（不能充当指定通过）

| 材料/阶段 | 实际状态、内审与明确缺口 | 下一行动 |
| --- | --- | --- |
| `i06-trusted-transfer-contract-request.md`，b39 | 纯合同r1；独立内审2P2修闭，见trusted-contract-review.md；无runtime/API。a1已有此提案仅说明其未批准设计，不当已实现guard | 等各唯一owner/root批准正式payload/coverage/引用JSON/错误/能力接口，再沿授权面实现和新验证/指定双审 |
| `t01-transfer-design-acceptance-r1.md`，156838c；`i06-transfer-response-acceptance-r1.md`，f00e1b7 | 纯接受/比对回执，本线未为这两份另开独立内审；所读T01/I06方案有原线/root独立设计审查，不能冒称这两份有指定Pass。生产inventory/原子退役/FS能力/receipt均未交付 | 保留相容方向和具体caller适配缺口；维护责任变化按当前root记录，不能消费未批实现 |
| interface-needs/private-preparation/report-file-publication/isolated-native-validation说明 | 随对应私有实现/工具的上下文，非另一个可调用实现；相应实现内审存在，不另造文档“指定通过” | 未来实际接口delta到位更新当前对接记录，冻结历史仍保留 |
| packet/manifest/D1D2/E1/blocked审计 | 纯流程/证据材料；root独立预检及针对性D1/D2读回已闭；未派发，不是模型外审 | root短lease后按当前政策核新base/head/实际模型、创建两完整任务；已存在真实任务按ID等待，不重复建 |
| 正式格式/投影/原子新project导入/来源能力/学习证据/生产IO guard/桥接/G.6/包内双平台 | 本线尚未实现；仅方案/精确缺口，不伪登记已开发候选或永久排除未来积压。I06 metadata/token核心等是其他owner阶段且未获本线消费批准 | 正式批准接点/实现到位按独占写面推进；形成代码后加入积压、必要验证和双方完整新审。全部57P0/父门与PR/CI/正常合并/远端要求不减 |

当前可独立下一步是补齐此全量盘点及新任务政策addendum，并交root形成总队列；已完成前置无变化不重跑。实际新任务创建等root短lease，后台推理不占整个lease。完整T10仍未完成；已批准桌面可直接computer use，旧“无GUI许可/待用户时段/CLI登录”不再是当前阻断，当前只按内部互斥及真实依赖/写权/运行边界执行。
