# 跨设备、升级与回退比较规范

T01 的 SQLite/Store 与 T10 的项目包是唯一项目权威；T11 只比较只读证据，不直接写数据库，不实现第二种项目导入、恢复或迁移器。

准备 A/B 两台受支持干净设备、两个独立数据目录和同候选安装资产。每次运行从 T09 固定 manifest 指定的基线/重置操作开始；不能继承上一个用例状态。完整案例至少包含手工事实、映射事实、受管人工修改、来源/行/managed value/墓碑、当前和过期结果、不可变运行与已提交轮次、撤销依据、模型辅助标记。记录项目 revision、输入 snapshot、依赖向量、规则/行为/执行语义/引擎与锁版本。

A 导出前通过唯一正式读接口取得源快照，按用户明确选择的范围形成 `t11-comparison-v2` 只读比较投影，再由 T10 导出相同选择的项目包。完整源快照另存，不把未选择的推导、原文件、历史或会话塞入包中。B 导入后先比较清单核心内容和所选内容的完整规范数据，再实际继续编辑、查询、重新关联同一源文件后映射重跑、确认相同人工冲突、执行新编辑的撤销；沙盘重放另以实际输入版本是否齐全判断。按 PRD 固定语义比较全部应携带对象、事实、来源和轨迹，不只核对数量或界面截图。

`t11-comparison-v2` 必含 projectId、sourceSnapshotId、projectRevision、executionVersions 及逐项 selection/capabilities/dependencies。集合行仍为唯一稳定 `{id,payload}`，保留所属领域完整内容；固定G.6人工冲突案例的 facts/definitions/ownership/mappingState/queries/results（明确范围的查询核对结果）不得为空。derivedResults/history/rounds/rawSources/agentSessions/undo 可以为空：未选择内容必须为空，不能把未选历史或先前撤销记录强塞给用户。选择历史也不自动证明可重放，失败运行或不完整历史仍可保留供查看。

selection 分别记录 currentDerived/historicalRuns/rawSources/agentSessions/priorUndo；priorUndo只记录本次证据中是否明确携带先前撤销依据，不新增T10产品UI选项或改变权威格式。未选择时undo必须为空，不能夹带旧操作before/after；导入后新编辑的撤销由继续操作check另验。capabilities独立记录 restoreCurrent/rerunOriginalMapping/replaySandbox：当前状态恢复比较要求restoreCurrent为true；未嵌入原文件时rerunOriginalMapping为false，后续实际重关联/重跑由独立check记录；选择了对应历史运行且输入/配置/语义版本齐全并受支持，才能标replaySandbox为true。首轮提交前失败/取消、rounds为空的运行也可从完整初始输入独立重放，不能把已有输出轮次作为前提，更不能静默续跑。dependencies记录mappingSources（embedded/missing）、replayInputs、replayConfiguration、replaySemantics（supported/missing/unsupported）。版本声明不能替真实引擎重放或文件验证。

独立冻结记录分别pin恢复和两方向的选择投影SHA；前后必须匹配同一selection及全部实际内容，不能用相同假快照自证相等。所属领域负责人按稳定身份排序并保留轮次/动作顺序，仅规范化设备路径等无关项，不能删除必要来源/所有权/版本/冲突来取得相等。原始导出保留，投影/只读适配器待T01/T10正式接口交接后实现；此v2是T11审计证据格式，不是新项目格式、Store或第二份可变权威。旧v1证据留在历史提交中，当前核验器不静默升级接受。

正反例分别真实执行：仅当前必需内容的完整包可恢复且不必有历史/原文件；不含原文件但含齐全历史的包可恢复并重放、不能直接重跑映射；包含原文件但历史输入缺失的包可恢复并重跑映射、不能声称重放；只含定义/缺事实或来源的包标模板。重新关联同源文件后须恢复重跑并识别相同人工冲突；未选历史/会话/推导不得泄入；缺配置/行为规则/语义版本或不支持语义不得标可重放。缺依赖必须提示，完整Agent代做不得计独立学习成功。均保留完整expected/actual，不能用三项能力的单一总布尔替代。

升级前用正式备份接口生成新路径备份并实际恢复检查；失败迁移必须保持之前完整已提交数据。卸载确认安装文件、项目、应用私有凭据设置各自边界，记录保留/删除选项及用户确认；不能默认删除项目。回退先停止写入并保留新版本数据副本，核对旧版能读的格式，再用真实上一版签名安装器和兼容备份恢复。旧版不能读取新格式时应拒绝直接打开，只能恢复兼容备份；不能用破坏性降级或覆盖唯一项目模拟成功。

双向 Win→Mac 与 Mac→Win 分别留完整报告，绑定实际源/目标设备、candidate/T09/安装包 SHA和时间。`RECOVERY_*`/`MIGRATION_*` checks 在核验器中是强制覆盖，不代表其中任何真实验收已经执行。
