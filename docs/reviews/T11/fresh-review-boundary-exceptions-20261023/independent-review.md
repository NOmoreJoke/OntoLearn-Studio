# Input-only 越界收据独立意见

2026-10-23。仅阅读本目录 `input-only-incidents.json` 与 Z 本方冻结提示第44、46、154行及必要相邻规则；未访问 native 日志、消息返回、全局配置、GUI 或模型报告，未运行测试或改变候选。本意见仅判断收据内容和规则关系，不认证未重读的输入采集过程。

两条记录均应保持 **OPEN，待根处置**。第44行允许必要普通工程验证，不覆盖第46、154行的显式禁令：Z 的提交命令包含临时空仓 `git commit --allow-empty`，临时仓和缺873探针目的不构成 no-commit 例外；M 的提交命令包含两次 `bash scripts/release/collect-macos.sh` 与 `/usr/bin/sw_vers`，预期参数/OS门早拒绝也不将真实 collector/native 调用变成获准的 `bash -n` 或静态检查。完全访问/始终授权不扩大任务范围。

有一项措辞建议：两条 `violation` 当前使用 “invoked”，容易读成动作已实际执行；input-only 证据只能确认“提交的命令包含/请求执行”这些动作。尤其 Z 的 `&&` 链可能在到达 commit 前终止，不应据命令文本认定 commit 成功、hook发生或候选被改；M 命令里的预期退出码、“correct”和系统版本也只是输入标签，不能当观测结果。建议仅改叙述，不改原始 `input`。实际执行到哪一步、成功与否及所有返回保持 UNKNOWN。

其余文档边界准确：原命令完整保留；未将返回、测试结果或正式终态写为通过；actions 明示未读/复制越界返回、未重跑或发新提示；原 owner context 导出异常仍 OPEN。`qualification` 明示仅提交输入，不能称全过程合规。原 M NotPass、18项 open、无 dual Pass/门禁关闭继续保留；根需分别裁定过程影响，不能由本意见自行关闭或恢复指定审查资格。

## 措辞修正最终核对

同日仅重新阅读当前收据：两条 `violation` 已改为 “Submitted command requests”，明确 Execution/results/hook effects UNKNOWN；对照此前读取的两条原 `input`，命令内容未变。上述措辞残留已修复，无新增文档不一致。

新增 `reportExposureQualification` 明确 owner 已在分类这些输入前收件 Z 完整报告，报告含审查者自行写出的 hook 断言；“未读/复制对应原始工具返回”不等于零暴露，收据明确不作 zero exposure 主张。该段只是披露既有报告暴露边界，不认证 hook 实际发生或执行结果；本审者没有读取该报告、返回或 native 源。

两项输入越界及既有 owner context 导出异常仍 OPEN，继续待根分别裁定过程影响；本次仅关闭措辞问题，不关闭原 M NotPass、18项或指定双审门，也不恢复/认证本轮审查资格。原独审段落作为修正前记录保留。
