# I01 状态

会话：01a154e3-d2e8-7200-9a22-36c3590f551b。日期：2026-10-20 Asia/Shanghai。

- 唯一范围：S1 / ADR-0002 存储与失效 spike；验收见 `../../iterations/I01/inputs/scope.md` 及原计划 S1。
- 非目标：完整映射/推理/行为/沙盘业务、v2任务协议、CSP、模型网关、pySHACL；Q5 未定，无容量达标线。
- 依赖：无前置实施依赖；已读取 PRD FR-006/304/604/700–705/804/1000、附录 C/D/E/G 和采纳计划。
- 仓库：/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio。origin https://github.com/NOmoreJoke/OntoLearn-Studio.git。
- 分支：feature/I01-storage-invalidation，base：e628f5e7b6c09e10e15644552a6171c4a9a3072e，head：3e787fb7f8923a0848c173215af2747861e4b35a。
- 阶段：Round 2双方已结束并明确通过；对照原S1门槛主动补齐保留问题，正在Round 3验证，尚未冻结新head。最近fetch时origin/develop仍为base。
- 原有文件：61 项逐个 SHA-256 与外部初始快照一致，均非本次实现，不修改或暂存。来源清单保存在父目录 iteration-control/2026-10-19。必要输入逐字副本及哈希在 docs/iterations/I01/inputs，供远端重现。
- 验证及独立agent已完成，详见下文最终证据；指定第三方Round 1已完成，修复及最终内部复核完成；待Round 2新任务。
- push / PR / merge / origin/develop 核验：未执行，双审前禁止。
- 未决：Q5 容量与设备、Q2平台等产品决定不由 spike 代定。
- 下一步：冻结Round 2候选后，经UI分别创建双方新任务；需Mac保持解锁。

## 2026-10-20 实际进展

- 已实现 SQLite 单事务正式提交/所有权/失效/operation-job 标记及前后快照、迁移恢复、场景轮次和不可变历史；RDFLib从规范快照建图。ADR及完整验收映射在 docs/iterations/I01。
- 最近专项运行：94 项 S1 测试通过；此前完整 check（102项Python及4项TS）与 verify:sources 通过。新增RDF规范词法回归后将重跑最终check及package/probe，结果以最终evidence为准。
- 真实package:dir已成功；开发/包内各两档三次共12条规范快照加载/建图/查询、热重复和内存记录已生成，包内health/新增依赖许可证校验通过。词法修复后重建产物再采最终证据。
- 独立agent /root/i01_internal_audit只读发现并已修复：slot人工覆盖、多值误拒绝、实现版本迟到覆盖、null重放误报、manual无变化失效、round空标记及RDF词法别名所有权绕过。最终复核进行中。
- UI预检：ZCode可见GLM-5.3/最高；MiniMax Code可见M3.1-Flash/xhigh。已通过两应用原生文件夹选择器绑定实际仓库绝对路径，MiniMax显示当前feature分支。尚未发送正式审查任务；正式每轮重新核验。
- 既有61文件再次逐项哈希一致；逐文件来源/保护清单在 preexisting-files.json。没有push、PR或merge。
- 下一步：最终独立复核、必要验证/打包完成后本地提交冻结base/head，经UI启动双独立审查。

- 最终独立agent复核：此前意见均关闭，未发现新增阻断，94项S1专项测试通过；详见 internal-review.md。
- 最终 npm run check 已通过：4项TS、105项Python（其中94项S1），lint/格式/类型/构建通过；verify:sources 实际核对13项通过（包含原有未提交清单状态，不把这些改动混入本次提交）。
- 最终package:dir与verify-i01.py均exit 0：12条开发/包内两档三重复记录，包内health仅声明health，RDFLib/pyparsing许可证资源与开发原件一致，动态链接清单已保存。原有61文件及4份冻结输入逐项SHA-256再核验一致。

## Round 1 候选冻结

- 时间：2026-10-20 00:15 Asia/Shanghai。
- 固定base：e628f5e7b6c09e10e15644552a6171c4a9a3072e。
- 固定head：6d8e4b3021b368661247c03c47f01e4d32ebf6e1。
- 本地提交43文件，候选文件清单在 docs/iterations/I01/evidence/candidate-files.txt（该清单自身在生成后加入提交）；所有实现/测试/依赖/配置/验收自此冻结。
- 剩余未提交：原有61项文档/原型及审查流程证据；无候选实现差异。原有文件未混入提交。
- 候选归档中的原source-manifest与归档源额外独立验证通过：12项（工作区13项来自原有未提交清单，未混入候选）；见 frozen-source-check.txt。
- 正式双审：即将经UI分别启动 I01-R1-ZCode-GLM53 与 I01-R1-MiniMax-M31Flash，新独立任务，同一base/head与需求；报告 round-1/zcode-glm53.md、round-1/minimax-m31flash.md。无push/PR/merge。

- Round 1 UI 实际启动（00:16）：ZCode新任务标识 I01-R1-ZCode-GLM53-20261020-0015（UI标题以该标识开头），GLM-5.3/最高，已在精确仓库运行固定HEAD和diff只读核验；逐次仅允许只读命令。MiniMax新任务“审查 I01 存储与失效 spike 实现”，标识 I01-R1-MiniMax-M31Flash-20261020-0015，UI显示完整仓库路径、feature分支、M3.1-Flash/xhigh并正在执行。两任务收到同一完整审查提示词/需求/base/head，互未披露结论。
- 代码保持6d8e4b3冻结；本轮报告待实际完成/读回，不能据UI工作中或文件存在宣称通过。仅追加流程证据。

## UI 临时阻断

- 2026-10-20 00:20左右：computer use返回“Mac is locked and automatic unlock could not unlock it”，要求用户手动解锁；已向用户发出解锁请求。
- 两个新任务在锁屏前均实际启动并读码；ZCode此前按次授权只读命令，MiniMax在独立运行验证。尚未取得任何一方的正式最终报告或UI完成核验，不登记通过。
- HEAD仍为6d8e4b3021b368661247c03c47f01e4d32ebf6e1，候选实现/测试/依赖/配置/验收无未提交差异，仅追加审查流程证据。无push/PR/merge。
- 恢复条件：用户手动解锁Mac；同一开发会话继续检查ZCode只读授权/任务状态与MiniMax任务状态，双方实际完成后读回指定报告。不得替换模型、降低思考设置或绕过UI。
- 独立后续静态检查还需关注 storage_probe 的 Unix resource 导入与既有Windows CI/包内health兼容；候选审查冻结期间暂不修改，待双方任务收尾后如需修复则新候选并重新双审。

## 锁屏阻断复核 2

自动继续后再次调用computer use inventory，原生应用返回同一“Mac is locked”错误；未重启或替换审查任务。两个指定报告仍不存在，不能认定任务已完成或通过。候选HEAD仍6d8e4b3，受审实现无差异，61项既有文件SHA-256再次一致。无法证明后台任务当前活跃，故本次属于等待用户解除真实阻断，不登记为任务完成的验证等待。解锁请求已发出，保持原请求，不重复请求授权。无push/PR/merge。

## 锁屏阻断复核 3 / blocked

连续第三个Goal回合再次通过computer use核验，原生应用仍返回同一锁屏错误；两个指定报告均未生成。不能证明两任务当前活跃或完成，不能绕过UI核验、修改仍在审查的冻结实现、替换模型、push或merge。上一回合分类为无进展（真实外部阻断复核及状态保存，不是已证实活跃任务的等待）。目前没有不依赖解锁且能安全推进门禁的下一步，按规则将Goal设为blocked；目标未完成。

恢复步骤：用户手动解锁Mac并恢复本Goal，同一开发会话检查原ZCode/MiniMax任务及待授权命令；双方任务实际收尾并读回报告后处理问题，包括已记录的Windows resource兼容风险；任何实现变化需新候选和双方新独立任务重审。候选仍6d8e4b3，受审实现无未提交差异，无push/PR/merge。不启动I02。

## 用户解锁后恢复

用户明确回复“已解锁”，computer use已实际恢复。原ZCode任务仍显示工作中/正在思考、GLM-5.3/最高；原MiniMax任务“审查 I01 存储与失效 spike 实现”已结束（8分36秒），UI显示M3.1-Flash/xhigh、精确仓库路径及feature分支。MiniMax报告已实际读回，base/head与候选一致，最终不通过；F-01/F-02阻断，F-03–06中，F-07–11低，待双方收尾后逐项记录处理。未向ZCode披露MiniMax本轮结论。仍冻结6d8e4b3实现，无push/PR/merge。

Goal工具当前仍返回blocked（工具不支持设置active/resume）；用户恢复授权已明确，本会话继续推进原完整目标，不新建或替换Goal。完成后依实际门禁更新complete；若再次遭遇同一阻断则重新从本次恢复回合计数。

## Round 1 收尾与解冻修复

两项任务已实际完成并通过UI核验：ZCode任务现标题“I01 S1 ADR-0002 存储spike对抗性审查”，已工作26分44秒，GLM-5.3/最高，报告结论通过（R1–R6非阻断）；MiniMax任务已完成8分36秒，M3.1-Flash/xhigh，报告不通过（F-01/F-02阻断，F-03–06中，F-07–11低）。两份MD已完整读回，均对应e628f5e→6d8e4b3，来源/范围/实际验证/未验证/逐项问题/明确结论齐全。双方各自声明未读取另一模型本轮报告。不能把本轮登记为双审通过。

开始修复前复核：受审实现无未提交差异，61项原有文件哈希仍一致；已fetch，origin/develop仍e628f5e7b6c09e10e15644552a6171c4a9a3072e。自此双方任务已结束，允许在同feature修复，形成新候选并双方新任务复审。原报告保留，不改写其结论。

报告SHA-256：
- minimax-m31flash.md: bd4db47e0f273d3a60472d283a9c9d9dc25ead827f1851c61619173a6511cd8f
- zcode-glm53.md: bef4cd676981af743345d62d8a1929db27d133400560f4c6ccbb078a035f5764

## Round 2 修复进展

- 首轮17条意见逐项决定见 round-1/processing.md；原报告不改写。两阻断修复及中等项补强均已实现，本地专项最近147项通过（新加受管净零与空映射依赖2项正在运行）。
- 内部独立agent复核已确认主要修复；额外发现“受管删除后原值恢复净零仍推进mapping版本”，已按前后owner记录与mapping定义净变化修复，补真实sourceHash改变仍推进的反例；等待最终只读复核。
- 原S1范围不变，未启动后续功能。依赖码表升级到invalidation-v2.json并单列发布/实现隔离，不新增领域过期原因。Windows模拟是本机证据，实际Windows CI仍待推送后核验。
- 下一步：完成新专项、check/verify:sources/e2e、实际package:dir及包内同样例，独立复核后冻结新head；两个应用各新任务同版本复审。无push/PR/merge。

## Round 2 最终验证 / 待冻结

- 最终内部只读复核通过，149项S1专项通过。npm run check实际通过160项Python、4项TS及lint/format/types/build；verify:sources核对13项工作区来源通过；桌面e2e 1项通过。
- 新版package:dir exit 0；实际app-resource引擎经verify-i01.py检查开发/包内两档各三次，共12条同样例测量。health、v2失效策略、许可证资源及本机动态链接验证通过；原始证据独立保存 evidence/round-2，首轮证据保留。Windows不可用resource和health惰性导入通过本机隔离进程模拟，实际Windows CI仍待远端，未宣称已跨平台实测。
- fetch确认origin/develop仍e628f5e7b6c09e10e15644552a6171c4a9a3072e；61项既有文件与4组输入原件/副本逐项SHA-256一致。
- 本次恢复收到“已解锁”后，再调用computer use时Mac再次锁定；已请求手动解锁并保持唤醒。新一轮双审尚未创建，不沿用首轮任何通过。先完成本地候选冻结；无push/PR/merge。

## Round 2 候选冻结

base e628f5e7b6c09e10e15644552a6171c4a9a3072e → head 3e787fb7f8923a0848c173215af2747861e4b35a。本地提交已完成，无push。全部实现/测试/配置/依赖/验收均在该提交中；仅后续流程证据可追加。新增提交37项自身文件，61项既有文件无暂存交集且哈希一致。独立git archive验证12项归档来源通过，与工作区13项的差异来自已保护的原有未提交manifest，未混入I01。

Round 1通过不沿用；Round 2任务尚未创建，当前等待Mac解锁。

## Round 2 UI 实际启动（2026-10-20 05:48 Asia/Shanghai）

用户再次明确“已解锁”，computer use恢复。ZCode经原生目录选择器重新绑定完整仓库路径，新空白任务UI GLM-5.3/最高；任务标识 I01-R2-ZCode-GLM53-20261020-0548，已开始固定SHA/分支只读核验，逐次仅授权只读命令。MiniMax新空白任务侧栏完整路径、feature分支、M3.1-Flash/xhigh均重新核验；标识 I01-R2-MiniMax-M31Flash-20261020-0548，UI标题“审查 I01 Round 2 存储失效迭代并输出报告”，已运行固定diff核验。

两任务同一e628f5e→3e787fb完整范围与完整需求/验收，允许阅读历史17条意见及processing，禁止读取另一模型本轮报告；各自输出 round-2/zcode-glm53.md、minimax-m31flash.md。未预设结论，当前不能登记通过。实现保持冻结，无push/PR/merge。Goal工具仍blocked，恢复授权及实际推进已记录，不新建替代Goal。

## Round 2 正式收尾 / Round 3 再补强

ZCode“ I01 Round 2 存储失效spike对抗性审查”19分30秒完成、GLM-5.3/最高，MiniMax“审查 I01 Round 2 存储失效迭代并输出报告”47分50秒完成、M3.1-Flash/xhigh。UI实际终态（发送disabled、无停止生成）与两份完整报告均已核验；双方对3e787fb明确通过，两首轮阻断关闭。原报告保留，SHA及全量新意见处理在round-2/processing.md。未向仍在运行的另一任务披露本轮结论。

但原S1退出2/6要求所有权可定位与缺失输入诚实，本会话选择先修M-01/N-02及关联文档/测试再新候选双审，不沿用本轮通过、不跳过原验收。保留事实ID冲突定位与项目快照集中校验已补，167项专项曾通过，新增旧config为null两项正在运行；内部独立复核已再次请求。下轮证据独立round-3，旧证据保留。无push/PR/merge，不启动I02；origin/develop最近fetch仍e628f5e。

## Round 3 最终内部复核与验证

集中项目快照校验补强到嵌套存储记录后，独立agent最终只读结论通过，187项S1专项独立通过（5.43s）。完整check已通过198项Python（187S1+11协议）与4项TS；verify:sources/e2e后续输出和实际package/probe待本轮最终命令结束后登记。61项既有文件及4组冻结输入原件/副本再次逐项SHA-256一致。当前head仍3e787fb，新实现未冻结；没有push/PR/merge。

Round 3最终命令已全部exit 0：check 198项Python/4TS、verify:sources 13项、e2e 1项、实际package:dir，以及app-resource引擎开发/包内两档各三次12条probe；health、v2规则与许可证校验通过，引擎目录25,123,766字节。原始证据独立evidence/round-3；JSON仅格式整理，不改原始数值。当前准备本地提交冻结，不代表双审或Windows CI已通过。
