# I01 Round 3 双通过与意见处理

固定base e628f5e7b6c09e10e15644552a6171c4a9a3072e → 受审head 1e3b179de1e1f9f7ad4b6556f292ef769c113d18。两项新独立UI任务实际结束，完整报告已读回；来源/实际路径/分支/版本/执行命令/未验证/历史逐项判断/明确结论均完整。原报告不改写。

| 应用/任务 | 每轮实际核验设置 | 实际收尾 | 结论/报告 |
| --- | --- | --- | --- |
| ZCode I01-R3-ZCode-GLM53-20261020-0643；最终标题“I01 Round 3 存储失效spike对抗性复审” | 原生目录选择器精确仓库、GLM-5.3/最高 | 24分37秒；UI无停止生成、发送disabled | 通过；zcode-glm53.md |
| MiniMax I01-R3-MiniMax-M31Flash-20261020-0643；标题“I01 Round 3 存储失效 spike 对抗性审查” | 侧栏完整目录、新任务本地/feature分支、M3.1-Flash/xhigh | 10分19秒；UI无停止生成、发送disabled | 通过；minimax-m31flash.md |

双方声明未读另一模型本轮内容，仅ls确认文件名；本开发会话未向仍运行的一方披露另一结论。双方均重新全量审查原base→新head，旧轮通过未沿用。首轮两项阻断及Round2所有权定位/输入缺失标记/文档精度重点项均独立确认关闭，S1六条退出条件均明确成立。

## 本轮新意见（保留全部编号与原严重度）

当前Python存储是内部spike接口，正式注册能力仍仅health。以下均由原报告明确判为低/P3、允许后续处理，不构成S1退出门槛阻断；本会话接受问题事实，记录具体后续，不改写为已修复。I03严格能力/身份/ChangeSet契约及I04服务接入前必须处理相应项，不能把本次集成当作可直接向UI/Agent开放的产品存储API。没有实施后续功能或越过原边界。

| 来源编号 / 原严重度 | 决定 | 事实、边界与后续验收 |
| --- | --- | --- |
| ZCode N-R3-1 P3；MiniMax F3-01低：kind未守卫 | 采纳、延期I03 | 非字符串kind可被接收；MiniMax更具体复现None会写重复NULL当前键且current无法寻址。不能概括为“零写入”；受影响是非法调用产生的派生指针，正式事实/历史未损坏且无业务调用路径。I03接入前为publish/current统一非空字符串kind守卫，拒绝None/空串/int/bool且results/current零写入，必要时以新格式迁移拒绝NULL键；对合法身份复跑唯一当前指针。不得以类型注解代替边界校验 |
| ZCode N-R3-2 P3：current非dict实现来源静默None | 采纳、延期I03 | 读取无写入；非法provenance会伪装“无当前结果”。I03统一身份与来源schema，并区分形状错误/无结果；复用publish守卫并覆盖None/list/int及缺键 |
| MiniMax F3-02低：旧非对象config写轮次裸AttributeError | 采纳、延期I03/I04 | history已诚实false，新start_run已拒非对象；模拟旧记录commit_round失败且事务回滚。I03/I04接入前补对legacy config的对象检查并输出受限形状错误，不让AttributeError越过服务边界；验证无轮次/标记副作用。此前ADR列举错误面不是穷尽所有内部误用异常，本报告附加记录该事实，不承诺已有完整协议错误契约 |
| MiniMax F3-03低：collect_cache全库范围 | 部分采纳、延期I03契约 | 当前无project参数，确为全库可重建载荷清理；未固定载荷清后再pin失败，须先固定报告。已固定报告、当前指针及历史轮次仍安全，不损坏正式数据/保存定义/历史。I03明确全库维护与项目清理的接口区别、pin顺序和并发预期；若新增project参数须带跨项目反例与新候选审查 |
| MiniMax F3-04低：删除受管人工值后仅前置快照追溯 | 采纳说明、延期I03/FR-804契约 | 显式remove后活动值变墓碑，人工值仍完整保存在同事务commit_evidence.before_snapshot。恢复managed_value并不恢复人工值；恢复人工值须读取历史证据并形成新的显式edits/预览确认。I03撤销/ChangeSet契约须写清，不能声称已有产品撤销UI |
| MiniMax F3-05低：同批remove+edits固定恢复语义 | 采纳说明、延期I03契约 | 当前实现固定definitions→remove→edits→manual→mapping，与字典书写顺序无关；同id remove+edits净效果是edits值，既有净零回归有意锁定此行为。I03必须显式采用该顺序或禁止同id多类操作，不允许调用方假设按字典顺序执行；选择变化须新候选审查 |
| MiniMax F3-06低：facts依赖仅项目级 | 保留已登记延期I03 | facts:asserted是现有唯一事实范围，项目内任意主语变化可保守使该范围结果过期；细粒度facts键未实现，不能伪造键维持current。I03能力契约决定真实数据范围/实际依赖映射与是否升级规则schema，按完整正反例验证；本次不新增领域原因或宣称细粒度已实现 |

## 历史意见与报告口径

首轮17条与Round2全部正文编号均有原处理记录（round-1/processing.md、round-2/processing.md）。双方本轮逐项重验，无未关闭阻断。两报告对F-07/F-11“按登记语义关闭/允许延期”、R4部分关闭、N-03/N-04“文档化关闭/延期”和N-08确认项的汇总计数不同，以逐项表与真实状态为准，不将计数分歧改成遗漏或伪造关闭。原R4锁错误/N-06/N-07统一I03/I04处理；R6历史增长留真实负载/Q5目标后设计；严格revision发布和可回收载荷的选择已实证且文档化，后续契约必须知晓。

报告中GLM把非字符串kind称为“无写入副作用”与其probe的accepted结果并非同义；MiniMax补充NULL实际写派生指针，本记录明确保留更具体反例。正式数据未损坏不代表派生视图完全无写入。报告原文不改写。

## 推送门禁与证据提交边界

- 本机check 198Python（187S1+11协议）/4TS、verify:sources、e2e、实际package:dir与12条app-resource/开发测量通过；独立agent复核通过。双方本轮各自独立运行并明确通过固定候选。
- 61项预存文件逐项SHA-256未变、不stage；4组冻结输入原件/副本SHA一致。
- 后续提交仅docs/reviews/I01纯流程证据，不改实现、测试、配置、依赖、ADR/acceptance。以git diff核对受审1e3b179→待推送HEAD只含该目录；完整源码/验收与受审候选一致。本轮通过有效性不以“新实现未审”替代。
- origin/develop须仍为原base；若变化或CI修复改变实现，则新候选重新双审。实际Windows/Linux/macOS CI须PR后核验，当前不冒称已通过；不绕过任何检查。

## 原始报告 SHA-256

- zcode-glm53.md: bc9c90be4382508e44a217056dc801c3ea15d6d7f807c03982b5d7802f856c51
- minimax-m31flash.md: 2b3a25037b57f8fa856b09cb651c870201e3c3e93b40825e7c11e828eb242712
