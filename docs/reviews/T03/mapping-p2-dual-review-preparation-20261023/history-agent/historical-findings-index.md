# 历史 finding 索引（供主控准备）

真实 Z1–Z7、F01–F11 共18项；不存在已核“原15问题”集合。F05/F06 是验证观察，P1/P2 是证据登记ID，均不能当待修缺陷或严重度。主控处置来自固定3df399草案，不改原模型原文、严重度历史，不代签Pass。

## 固定输入

- `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-zcode-followup-1-full-report.md`：11685 B / 79行 / SHA `54c0c04189fd88b8ff3cd26de4597cfd8e86c2c060cfd0616c589546453a8cdd`。
- `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-minimax-followup-1-full-report.md`：42204 B / 392行 / SHA `4ab6e2c685dcc50a0a8e0c864c84a0a4cfd9a6585723b1ac060486894fcafd7a`。
- `docs/reviews/T03/mapping-followup-1-completed-20261023/technical-disposition-draft.md`：18890 B / 58行 / SHA `20c5c393f4223977ec5329afe8766988936b885b74c58f2e4caec2cf80740c98`。

## Z1 — 首报P3；续报改判P4

性质：原P3→P4观察，残余报告判断待纠正。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-zcode-followup-1-full-report.md:39–44`；草案第16行。

Store 对跨 owner 同值墓碑保留 ID 拒绝成立：`storage.py:620–627` 比较 reserved_id。**但续报残留的“preview 不预显，直到commit才发现”不成立**：`mapping/plan.py:310–317` 的 `candidate.id == fact.id` 在 `fact.object is not None` 分支之外，同样命中墓碑。两层都有同 ID 冲突判定。

处置与未验边界：原严重度与重判历史原样保留；残留说法是报告纠正项，无需为它改产品。让原 Z 引用该分支复核并明确纠正，不由本草案代其签 Pass。

## Z2 — P3，维持

性质：P3私有UI预检局限，后端fail-closed。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-zcode-followup-1-full-report.md:46–46`；草案第17行。

`model.ts:119–144` 检查列存在、IRI形式及引用列存在，但确实没有重复 predicate／重复 referenceColumns 的唯一性预检；`plan.py:118–119,130–138` 会拒绝这些形状。原首报说的是**重复引用列**，不是没有列存在性检查。

处置与未验边界：私有 UI 的预览前提示局限，后端 fail-closed；没有证明越权/错误提交。保留 P3 与 T00/T01 正式 wire 字段级错误映射待办，不以此伪造已完成接线；若 root 决定改当前候选 UI，则须新候选及原双新审。续报“Z2维持P3”与终段“无P3遗留”必须由原 Z 对齐。

## Z3 — P4

性质：P4升级维护观察。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-zcode-followup-1-full-report.md:48–48`；草案第18行。

`source.py:268` 使用 `fs._worksheet_path` 为事实；当前精确 openpyxl 版本和已有回归限定了依赖面，未出现本次实际不兼容证据。

处置与未验边界：可维护性观察；T03 将其留作以后 openpyxl 升级断点。当前不机械改解析逻辑／重测。

## Z4 — P4

性质：P4资源/性能观察，未测量。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-zcode-followup-1-full-report.md:50–50`；草案第19行。

`parse_xlsx:258,261,268` 有两次 workbook 打开和一次选中sheet缓存扫描；`_open_xlsx` 各自也做容器检查。所谓“三遍”是概括性 I/O 描述，不是精确性能测量。

处置与未验边界：资源/性能观察；保留既有上限、Q5未知，不量化时延/RSS或改称容量通过；确有性能问题再测。

## Z5 — P4，报告称闭环

性质：P4工具计数观察，原报告称闭环。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-zcode-followup-1-full-report.md:52–52`；草案第20行。

ruff 计数是被报告的工具输出口径，没有由此发现产品差异。本次不复跑 ruff，也不独立追认其182/207全体解释。

处置与未验边界：报告引用方保留命令、版本、目录与当次文件清单；不把计数差当测试数量或业务缺陷。

## Z6 — P4

性质：P4有意格式解析差异。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-zcode-followup-1-full-report.md:54–54`；草案第21行。

CSV `_table` 要求实际行宽等于标题宽，XLSX `source.py:283–286` 补稀疏尾空值；两种格式的宽度处理确实不同。

处置与未验边界：已声明的解析差异，不自动判数据错位。T03/交互文档说明；本次无新增失败，未要求改 CSV 严格规则。

## Z7 — P4（新增信息）

性质：P4信息/正式错误适配约束。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-zcode-followup-1-full-report.md:56–57`；草案第22行。

`storage.py:41–48` 的 code 映射确无 ownership，原始 Conflict 文本只应留内部；`JobStore._application:95–110` 会将 ownership 冲突转成有界 `OWNERSHIP_CONFLICT/detailRef`。

处置与未验边界：与 F11 同一接线约束，不重复制造第二缺陷。当前私有服务不提交；由正式写入 owner 保持受信应用服务错误转换，T03 不自行新增公共 schema。

## F01 — 低

性质：低；证据保存工具问题。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-minimax-followup-1-full-report.md:217–223`；草案第28行。

`docs/iterations/T03/verify-packaged-probe.py:15–16,66` 确会回写三份固定受跟踪证据；即使同包时幂等，也不是适合只读外审直接运行的保存方式。

处置与未验边界：证据工具可复查性问题，非已证当前包语义错误。T03 未来新候选可将输出写到新轮次／显式输出目录；本轮不执行它，不覆盖旧原件。外审方原先等价只写 raw 的验证不因此被抹去。

## F02 — 低

性质：低；草稿顺序fail-closed UX。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-minimax-followup-1-full-report.md:225–230`；草案第29行。

`MappingPage.tsx:41–43` 编辑字段时移至数组尾；`model.ts:65–67` 用 JSON.stringify 作本地草稿等价比较。等价字段集合可能因顺序而产生不同 key；`currentPreview:69–81` 因此拒绝旧预览，方向为 fail-closed。

处置与未验边界：当前私有 UX/规范化局限，不是授权 token 漏洞。T03 若修规范化，必须保留字段实际转换次序的语义并新候选/双新审；不静默接受旧预览。

## F03 — 信息

性质：信息；设计态注册元数据。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-minimax-followup-1-full-report.md:232–238`；草案第30行。

固定 registry 的 mapping.commit 同时有 agentEligible=true、formal-write 和 design-only；`coordinator.py:248–254` 实际仅允许 test.read/test.atomic/test.rounds，未开放该业务。所引 registry、coordinator 在 base→303 上无差异。

处置与未验边界：设计态注册元数据观察；不能把 agentEligible 单字段当可派发能力。公共契约 owner 在正式启用前统一，不属本次 T03 私有服务修复。

## F04 — 信息

性质：信息；工具链策略不对称。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-minimax-followup-1-full-report.md:240–246`；草案第31行。

ESLint ignores 无 docs/reviews，而 `.prettierignore` 有 docs/reviews，策略差异为事实。

处置与未验边界：工具链策略观察，非已证执行失败。归工具链 owner；不为“统一”批量格式化冻结原件，也不凭不对称推 CI 已失败。

## F05 — 验证观察，非待修缺陷

性质：验证观察/正面结果，非待修缺陷。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-minimax-followup-1-full-report.md:256–261`；草案第32行。

原同槽/所有权若干探针正面结果可以保留；源码也支持 Z1 所述同 ID 墓碑拒绝。

处置与未验边界：保留为被测构造的正面观察；“preview与Store完全一致”只在已核输入与对应分支内使用，不扩大到所有可能状态。无需按正面观察制造产品修改。

## F06 — 验证观察，非待修缺陷

性质：验证观察/正面样例，非待修缺陷；普遍论断待纠正。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-minimax-followup-1-full-report.md:263–269`；草案第33行。

原三个普通单元格样例的正面结果可保留。**不能采其普遍证明**“合法XML文本中的 `<` 必然转义，所以 part 中不可能出现字面DOCTYPE”：XML CDATA 可承载字面文本，例如 `<t><![CDATA[<!DOCTYPE html>]]></t>`；而 `source.py:181–186` 对原始part字节作无上下文子串拦截。

处置与未验边界：本次仅提出静态编码边界，未制作/运行 OOXML fixture，不宣布该具体文件已被产品误拒。要求原模型纠正普遍结论，区分已测普通转义样例与未测 CDATA；是否属于必须接收的合法输入及是否需一次最小验证由 root/T03 决定，不能据此自行改安全闸。

## F07 — 信息（新增）

性质：信息；继承开发配置诊断边界。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-minimax-followup-1-full-report.md:275–281`；草案第34行。

`csp.ts:15–17` 在非法dev origin/nonce抛错；`main/index.ts:78–84` 的 whenReady 回调调用它且至`:184`无 catch，创建窗口在`:180`。静态可达的失败路径成立。上述两文件 base→303 未变。

处置与未验边界：继承的非法开发配置失败诊断问题；未发现 CSP 绕过，未实测 Electron 的宿主未捕获 rejection 表现。交当前 desktop/main owner 评估显式诊断；T03 不抢写。

## F08 — 信息（新增）

性质：信息；平台引用边界。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-minimax-followup-1-full-report.md:285–292`；草案第35行。

固定 `test_i04_lifecycle_boundaries.py:235,295,343` 三个 Darwin-only skipif，CI quality为Ubuntu；mapping source另有5处openpyxl importorskip。固定 check 原件确为 Darwin/零skip。

处置与未验边界：平台限定引用正确。说“macOS当次1110/0skip”成立，不能据此发 Linux/目标OS零skip证书；没有新增跨平台执行，不推算最新CI运行总数。

## F09 — 信息（新增）

性质：信息；报告总数/专项统计错误。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-minimax-followup-1-full-report.md:294–301`；草案第36行。

**报告统计错误已证实。** 固定 `check-registered-scope.txt:90` collected1110；`:112–115` 明列 mapping entrypoint6/plan22/recovery9/source21；`:130` 总1110passed。故1110**已含58 mapping**，不是“继承1110不含mapping”；按该日志分组算术其余1052。

处置与未验边界：仅报告更正，不改产品/测试。保留“其他继承测试未直接import mapping”的独立观察，也不能用该观察推出全量测试没收集 mapping。总数与专项应分列为“总1110，其中mapping58”。

## F10 — 信息（新增、假设消解）

性质：信息；T03假设消解，正式契约边界。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-minimax-followup-1-full-report.md:303–309`；草案第37行。

`mapping/plan.py:102–108` 限定映射identity为相同的 `[A-Za-z0-9_.-]{1,128}`，故该非法identity经T03映射路径被拒；`storage.py:344–350` 对内部定义id只校验非空的较宽输入面也为事实。相关存储基线未变。

处置与未验边界：对当前 T03 假设消解；非T03调用方的 id 约束属于存储/契约正式接线边界，不能凭内部API宽松就宣称当前暴露漏洞，也不由 T03 扩写共享文件。

## F11 — 信息（新增）

性质：信息；正式写入错误适配约束。原文 `docs/reviews/T03/mapping-followup-1-completed-20261023/mapping-S1-minimax-followup-1-full-report.md:311–316`；草案第38行。

`JobStore.commit_job:716–735` 确经 `_application` 调 `super().commit`，与`:95–110` 有界ownership转换形成真实代码链。裸Store Conflict 的 code映射和文本不可跨界，见Z7。

处置与未验边界：正式写入/错误适配约束成立；未证明 mapping.commit 已正式接线。由 T01/当前受信应用服务 owner 集成并验证，不把现有 test.atomic 路线等同正式 mapping 事务验收。

## 新候选与独立性边界

原报告P2开放按当时输入保留。da1795新增固定六项后已有source/实际包17项证据与独立复核，仍待两个全新完整指定外审。其余UI、Store、Job、公共契约和工具问题没有被probe/test两处改动自动修复。

本合并索引为主控准备，不替代完整原报告。新审间不得互传当轮意见；若各方只获自身历史意见读取权，应按originalReport分开提供，范围由主控裁定。

本次仅静态读/文本处理，无产品/mock/测试/打包/安装/GUI/网络；未碰STOP树或SDK/身份载荷。
