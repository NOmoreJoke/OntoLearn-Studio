# 7d30 / package085 指定双审意见处理

本记录用于后继新候选的全新独立复审，不更改本轮原报告，不将 owner 处置当作模型 Pass。原报告均已实际完成并由 parent 全文读至 EOF；当前未推送、未 PR、未 CI、未合并，0/17 不变。

- MiniMax：`mvs_6fe598b15ada40019194d6bb7b231d9f`，M3.1-Flash/xhigh/始终授权；原报告50711B，SHA256 `8d6c72a6f3dbe99ce21d3936cdf8ae42c8cebca7a15282f81d693a56e583f52a`，结论 BLOCK。
- ZCode：`session_6501d56fe8cb85086247e5c8dace96b8`，Start Plan/GLM-5.3/最高/完全访问；原报告33258B，SHA256 `540dbaa4325f3047cf71a34a0a58b0babfb39a3fbe98c4f07a35945dbc59634f`，未发现新的实现级阻断，保留流程/发布欠项。实际终态20分46秒。首次错绑MEM的`session_6603f72f7d097979966a17fe8684c84d`已Stop，无有效审查结论，历史保留。
- 两份原报告位置：`../20261024_t01_7d30_package085_designated_dual_review_001/{minimax,zcode}/report.md`。本轮事先未互传发现；后继复审可对称读取双方历史报告及本记录。

## 当前授权范围和流程

`iteration-control/2026-10-21-weekly-release/goal-objective.md:3,17–19,25–30` 已采用macOS 15 arm64未签名目录包，“非正式分发，仅限内部演示”；无证书不推定采购。正式签名、公证、安装、legal/_distutils、干净设备、跨平台/参考设备、HOLD、D2及真实模型等义务独立保留，不用内部包关闭。

最新human续接授权要求实际运行后依次完成：同版指定双审→push→PR→CI→merge→远端复核。未发生的后续流程不能冒称完成；但它们位于双审之后，不能因当前尚未push/CI而将审查前置任务变成循环等待。C4–C6/888旧决策书及轮次事实保留，不重置、不追认；按最新续接授权处理当前候选，不重复把旧待选字段当作新缺失授权。该说明不要求模型预设通过。

## MiniMax四项代码阻断逐项处理

### M1 uncertain单向闩锁：部分采纳，缩小影响范围

同一live engine session发生timeout/UNKNOWN后，原record确无复位，`mainlineProjectClient()`继续复用该record，主project/query受拒；见engine.ts原7d30:702–716,1119–1123,2456–2459。保留此限制，不能简单清uncertain、丢UNKNOWN或自动重放。

不采纳“整个App永久不可用/任何只读对账不可达”：原session失效后1124–1129创建新owner，1363–1472通过原可信principal进行真实open与只读恢复；TaskService325–435接该路径。已选中P且仅前端超时时，TaskService541–551,1058–1059的operation:get/job:get经engine.request，不经mainlineReady。创建前清空P且尚无principal，是更窄的未知创建恢复限制。本次不新增恢复授权接口。

### M2 跨session原操作必冲突：不采纳全局High结论，保留创建专属限制

create/example原origin全等重取约束确存在（project_lifecycle.py原:465–470,1027–1032），新握手重提会拒绝；测试test_mainline_named_example_dispatch.py:187–201明确要求如此。不能推广到所有Job/marker：job_store.py:1398–1413按当前许可P/op读marker，现有恢复白名单含job.get/operation.get。

创建resolution原合同位于`.worktrees/T01-project-host-read-services/docs/iterations/T01/project-create-and-resolution-contract.md`，39602B/SHA256 `ff725f2c0ee40cbdf61c9c4d27dfea1be3ccd2068df4399878b037976de4a5f3`，43–45,167,182,239行要求跨session重新证明原dispatch物理绑定；缺证明保持UNKNOWN，当前许可/同UUID/同正文不能替代。该合同是边界依据，不表示其未来resolution接口已经接入。保留当前诚实未知提示和真实目录核对，不删origin，不造持久意图账本或公开lookup。

### M3 16未ACK投递：部分采纳可达耗尽事实，不采纳FIFO修复

desktop-ipc.ts原103–104明定timeout/navigation/newsession不得删除未ACK责任；engine.ts原937–958只在精确receipt可消费时退原delivery。accepted是已消费ACK去重缓存，不能类比未ACK容器。旧frame/session丢ACK可累计耗尽，但health/tasks/job/result/operation不经过该主project/query容量门；原有效ACK仍可恢复。保留16及UNKNOWN/未ACK责任，不因Map消失假作ACK，不将可达资源上限改称“全App砖死”。

### M4 第17个正常新commit被拒：采纳并实施最小生命周期修复

原service #intents只set不退休；16次成功且各自正常ACK后第17个新operation仍INVALID_STATE。原id accepted仍可返回，因此“所有提交失效”表述缩小。

ROOT已明确批准两层方案：保16个inflight/UNKNOWN/未ACK完整责任；每次缓存返回登记当前真实delivery，全部精确consume且无active使用后才清service完整Job缓存alias、退它独立的payload holding。callback失败保原receipt/holding/完整责任，可按原handle重试；已完成callback不重复退款。compact保原request/op/jobId/owner/session，预先依既有128MiB/1048576objects预算计费，不FIFO忘记，不改预算数字。旧id严格原绑定后只读job.get并校全Job身份/confirmationRef/input，绝不回退job.create。无公开协议/schema/renderer/origin变更，无新增持久账本。

修改四叶：engine.ts、project-mainline-service.ts、t01-mainline-real-runtime.test.ts、t01-mainline-reply-lifecycle.test.ts。独立agent四叶固定hash只读差分审查未见新增P1/P2；这不替代指定双审。专项真实stdio/SQLite/finite worker已记录red17失败→green；新增duplicate ACK依赖、cleanup失败重试、UNKNOWN边界通过。3目标文件合跑49pass/1fail的首失败原件保留，S环境导入pyshacl确实缺失。随后仅四源机械同步至原隔离N，新的完整check-full-086自然0：35个TS文件/1694测试全过（含旧query与新17提交真实用例），332Ruff、3445Py过/44原skip，source1270不变。已仅提交四叶，HEAD dd21ab12480c8a9e5245a3768a033fae7b943fb3，parent7d30；新包/对应真实运行/双方新独立复审尚待，不沿用085证据。

## MiniMax其余建议与清单登记

原报告§3问题1–18、§5全部160引用行（147产品+13人员角色）和§5.3全部16未核/未满足项均以原件及上述hash完整保留；下列登记不删除其任何观察或未核限制。

| 原项 | 处理 |
| --- | --- |
| M5 签名/公证/dir | 采纳实际产物状态，正式外部分发义务保留；当前已批准内部未签名目录包不擅改builder/采购证书。 |
| M6 每页物化载荷 | 登记规模/性能风险；未实测规模不量化，不以小样本外推百万行；交D2/查询owner按原口径。 |
| M7 全量导出 | 当前页CSV事实采纳；不自动增全量/JSON/XLSX新功能，按T04原FR与范围另验。 |
| M8 重复撤销no-op建议 | 不自动采用。原operation幂等与以新operation再次撤销不同；ABA/后续修改冲突必须保留，不能用无条件no-op掩盖。 |
| M9 重启createIntent持久化 | 记录限制；原resolution合同禁止新增main意图账本，缺原物理绑定继续UNKNOWN，名字非归因。 |
| M10 probe内部直写API | 记录潜在误用风险；当前协议不可达，未证明当前越权路径，不新增范围清理。 |
| M11 内部异常含原值 | 保留潜在风险；当前受限分类未泄露，不把内部字符串当已发生外泄。 |
| M12 独立redo/用例命名 | 保留观察。FR-804的撤销与独立redo/历史选择器分开，不由任务书列名自动扩产品范围。 |
| M13 workspace星号 | 本地workspace解析事实，低风险维护项，未改依赖/锁。 |
| M14 并发主链拒绝 | 保留有界单飞约束，不改为无限队列。 |
| M15 撤销历史扫描 | 登记性能风险，无量化改善承诺，交规模口径验证。 |
| M16 Python更新策略 | 保留手工冻结uv升级政策与自动扫描缺口，不自行升级依赖。 |
| M17 changelog/terms/privacy | 登记文档义务，未假称已建立正式文档；不因清单扩当前功能。 |
| M18 ABA保护 | 保留为优点，不能与M8建议混同后移除。 |

M§5.3的静态加密/失窃、正式流水线、跨平台/老设备、D2、a11y、查看审计、全屏状态、表单保留、i18n/RTL、changelog/terms/privacy、组织命名、超大文件、备份恢复、DLQ、合同保留期、远端分支保护逐项留账：尚未核实的仍无法确认。账户/支付/邮件/SaaS/API等不适用项不新增无关实现，人员事实不从代码推断。模型网关未接入与真实LLM欠项分开处理。

## ZCode Top10及其余清单处理

Z原报告§4全部10项、§5逐类适用性和所有无法确认项、§6全部历史/验收缺口完整留账：

| 原项 | 处理 |
| --- | --- |
| Z1 child exit/close观测及活体leaseBusy | 观测UNKNOWN保留；原native方法已按原合同完成且ROOT接受局限，不把有限ps变成完整reap。活体挂起风险为推断，未证实新故障；不单为原不要求的child事件重跑或扩优雅收尾工程。 |
| Z2 签名/公证 | 同M5，正式分发义务保留；内部演示范围照已批准目标。 |
| Z3 独立redo/历史撤销 | 采纳当前UI观察，登记T02/FR-804范围核对，不自动增历史选择器/新功能。 |
| Z4 全量导出 | 同M7，原页面CSV与全量导出分开，不能自动扩授权。 |
| Z5 损坏SQLite修复入口 | HOLD/B/C未授权状态原样保留，不碰受保护物理库。 |
| Z6 用户备份/恢复 | 登记能力缺口/恢复实测义务，不把迁移备份当完整用户备份，不自动加新入口。 |
| Z7 键盘/树形aria | 登记原合同适用性与未测边界；无合同事实不虚称合规，也不扩当前修复。 |
| Z8 i18n/messageKey | 单语目标下登记维护建议，不自行增多语言；错误可行动性按原条款。 |
| Z9 大文件/死代码/import | 维护项留账，不混入本次私有生命周期修复。 |
| Z10 跨平台/参考设备/基线 | 原义务保留，按D2等已定口径验收，不用本机/CI代参考设备。 |

Z的Ruff332逐文件计数、README一小时、307过程文档、框架补丁节奏、导航历史等无法确认项不洗绿。静态加密“接受项”、GDPR等不适用判断仅是该审查者依据当前形态的判断，不替代用户产品/法律决定。历史C4–C6、D8、HOLD和first full001首败保留，当前新human续接按上节执行。

## 后继验收

必要新完整check→新候选HEAD/JS→T11新包→对应真实运行→双方各新建全新独立复审任务。双方对称附原清单全文、双方历史报告、本处理依据、最新采用范围和真实证据；不复用终态任务改旧结论。只有实际适用双审通过后才push→PR→CI→merge→远端复核，报告当前欠项不改变为完成。
