# T09-S1 验证与历史意见索引

固定审查区间：5f910b52c69d86a1076b2032e5d3c63e715947f3 → 76596656908ed84e577e8202a602e3256d5febcc；既有流程证据固定d96924e715a1b2139a75b70aea40fc30ae1129fe。此索引只组织既有证据，不是本轮指定模型结论；不得以旧Codex内审代替本轮独立完整审查。

## 权威读取顺序

1. `input-manifest.json` 列完整产品diff、全部当前流程证据与policy/prompt hash；产品代码和验收输入取product commit，现有报告/验证摘要取d969流程快照。
2. `docs/prd/PRD-本体学习与落地Agent工作台.md`：FR-003、100–105；9.4、11.2、12.1；附录C/D/E/G。完整原P0保留，S1只独立验收总控登记的有界范围。
3. `tests/fixtures/product-baselines/manifest.json`（aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e）；逐17输入、50计划、source PRD SHA核对，不能把计划当真实领域通过。
4. 当前同版总证据 `docs/reviews/T09/evidence/learning-ui-verification.json`、`npm-check-ui-final.txt`；backend/I04再读 `jobstore-verification.json`。完整独立内审链为 `independent-review.md`、`jobstore-integration-review.md`、`learning-ui-independent-review.md`。
5. `docs/iterations/T09/{handoff.md,learning-ui-contract.md,user-acceptance.md}`。旧product快照中的recovery/status/旧summary是当时历史，不覆盖d969当前证据或本轮任务身份。

## 原验证与证据强度

| 固定阶段 | 原件/摘要 | 实际结果及边界 |
| --- | --- | --- |
| 51cdc0e早期内容/Store | verification-summary.json；learning-pytest-final.txt；npm-check-final.txt | 35学习、630TS/1087Python的历史结果；不能当修后873或765验证 |
| 873c8c0 seed修复/真实I04 | jobstore-verification.json；learning-42-pytest.txt；npm-check-jobstore-final.txt | 42学习（含7真实I04）、630TS/1094Python。真实rollback预览/stdio coordinator/隔离worker/收据页/重开；test.atomic明确测试专用，不能当正式业务确认 |
| 7659665当前S1全量 | learning-ui-verification.json；npm-check-ui-final.txt，SHA210d3d9bc7254e059f9bc031988226f946251f9d359a577b8a54470a996241e5 | exit0；664 Vitest（18学习纯+16显式headless）、1094Python、lint/format/types/build/ruff通过。该fullcheck覆盖整个当前代码，不只UI |
| 765 UI可视证据 | evidence/ui/desktop-course.png、mobile-behavior.png；摘要中的hash | 1440×1050及viewport390×844，手机文件390×1932。实际查看、窄屏无页面横向溢出。只证组件；sandbox仅launch配置及成功，无当次argv/OS状态/binary hash证明 |
| 默认浏览器开关 | tests/unit/learning-workspace.test.ts、d969摘要/交接 | 未设T09_HEADLESS_UI=1始终skip；设1缺匹配runtime是launch失败。默认skip不得报浏览器通过 |
| package/native | 没有对应通过原件 | 本S1未改依赖/锁/打包配置，无新增package触发；课程资源入包、双平台/native和真人验收仍待，不从build外推 |

UI的Synthetic callbacks与Python SyntheticTools仅测reducer/组件拒绝和归类；固定expected不是实际领域输出。RDF真实解析/查询输入探针与I04真实基础设施的范围分别保留。test.atomic预览内部confirmation记录不是人类点击确认。E.5源JSON可含oracle expected，但正式seed计划不写oracle/预置推导。

## 历史意见逐项处置索引

| 编号 | 触发/历史问题 | 修后对象、证据与现状 |
| --- | --- | --- |
| CONTENT-01 | 迁移题正文泄露答案，第4提示跨题泄露 | course/transfer-inputs内容与test_retracted_mapping_object_keeps_manual_fact_and_transfer_has_no_answer_in_body；independent-review已关闭 |
| CONTENT-02 | G-list-09 CSV与M-04同版源不一致 | equipment-updated.csv在M-04/G-list-09共用、字节SHA固定；已关闭 |
| CONTENT-03 | E.5行为版本不匹配 | cases与E.5固定e5-behaviors-1；已关闭 |
| CONTENT-04 | M-03人工备注放001无法检出误删002 | manual备注改到被撤回002，完整预期保留它、只撤受管事实；已关闭 |
| CONTENT-05 | E.5轨迹/未来排程证据不完整 | 补完整八轮actionTrace/scheduledFutureEvents，G-list-01/06同步；新manifest aaaef2c…；完整重审关闭 |
| INFRA-01 | 冒号包装ID违反dependencyKey，提交后project.get超时 | baselines.py改G-base.ontology/G-base.initial等点号ID；7真实通道含canonical Project和依赖向量/重开；jobstore-integration-review关闭 |
| UI-01 P1 | 高版本降辅助/同版本冲突可洗成独立 | observeRecord/projectionRecord单调水位及冲突拒绝，newer-lower/same-version-conflict测试；已关闭 |
| UI-02 P1 | 真context缺保存能力仍先显示提示 | 先recordHint匹配回执才揭示；无context迁移四级都拒；保存失败/能力缺席/预览负例；已关闭 |
| UI-03 P1 | 同attempt换input洗白 | currentFloor按project/task/attempt聚合，完整context隔离结果；hint4→input2独立记录拒绝；已关闭 |
| UI-04 P1 | 丢弃矛盾新版后旧独立通过仍计当前 | 保留新版矛盾令投影不可用，不回退旧pass；contradictory-newer；已关闭。修前为静态推导，修后有独立探针，不能声称修前独立运行 |
| UI-05 P2 | maxHint5污染水位，后续合法4永久不可用 | 只采有效范围辅助水位，无效最新仍fail-closed，合法新版本恢复；已关闭 |
| DOC-01 | 旧873 recovery仍指初始51摘要 | 6f6264b恢复定位修复，当前d969明确765/新摘要，旧记录保留；总控已核闭合 |
| DOC-02 | opt-in/runtime skip措辞、截图尺寸/sandbox范围 | d969明确未设开关恒skip、显式1缺runtime失败；viewport/file分记、sandbox仅配置和成功；总控已闭合。旧内审更强措辞不能扩大证据 |
| PARENT-01 保留 | 多阶段历史Q01/修复前后不能重贴终态标签 | 765未实现T00/T01阶段契约，正式接线门保留；独立树12699cc/e651原型不在本轮，禁止拿来补S1能力 |
| PARENT-02 保留 | G-list-02 exactFile/exactPointer不是完整round DTO比较器；A-10仅三个固定反例 | 当前课程scenario用展开G-list-01/06；正式G-list-02需批准owner完整输出比较，完整指定Agent评估集仍T08依赖；未宣称关闭 |
| PARENT-03 保留 | 跨窗口/重开/跨attempt辅助不可洗需真实账本 | T01/T08受信持久来源未接；renderer临时floor和纯reducer不是权威账本；不登记父功能通过 |

## 首失败和中间记录

- first-ruff.txt保留首格式问题；first-npm-check.txt.gz保留初期运行时改fixture未刷新manifest的27 digest mismatch（不当最终结果）；原raw SHA/归档SHA见verification-summary。
- jobstore-first-pytest.txt.gz保留4failed/3passed原始超时；根因由旧ID/schema/修后diff及复现共同支持，原件并非直接打印dependencyKey错误。
- ui-first/second/third-vitest.txt.gz分别为入口解析、匹配浏览器缺失、JSX开发/生产混搭；第三次16纯pass/13组件fail，不能算UI通过。第四次30项pass是中间候选。
- npm-check-ui-first.txt.gz为浏览器自带脚本被lint扫描；type-failure为Vite8选项类型错误；intermediate-661是中间全check。无损raw/压缩SHA、字节与最终全量在learning-ui-verification逐条列明。
- 不补造旧过程的taskID、执行输入、argv、原生证明或真人数据。所有范围内历史问题需由本轮审查者重新判定关闭，不能只复制旧结论。
