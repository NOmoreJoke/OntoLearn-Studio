# 历史处置与原件索引

历史均按原候选保留；下列关闭仅指既有内部审查，不代替本轮指定模型判断。完整原文读取product中的internal-review.md、selection-v2-review.md、first-failure.json、verification.json和approved-fixed-baseline-probe.json。

| 历史项                      | 既有处置及本轮复核点                                                                                                                             |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| P1 expected/actual数量自证  | 绑定T09完整expected/E.5与独立freeze每项预期hash，保留拒绝例；复核仍无旁路                                                                        |
| P1 空或任意等值恢复快照     | 身份/唯一id/完整payload及外部snapshot pin；v2只对固定丰富冲突fixture要求当前必需层，不能强制未选历史                                             |
| P1 冻结时间可回填           | 独立freeze固定时间和模型/评估版本，过期与漂移拒绝                                                                                                |
| P1 文本或当前安装器冒充旧版 | PE/DMG结构、独立旧资产版本/来源/hash/签名绑定及反例                                                                                              |
| P2 真人core与迁移完成矛盾   | 80%计入者必须迁移完成，区分口头/示范/Agent代做                                                                                                   |
| E.5引用新增回归             | exact/replay真实展开；缺对象/索引、漂移、同数量错对象拒绝；45专项历史结果不代最新65                                                              |
| v2 P1 未选旧undo泄漏        | priorUndo选择记录，未选必须空；精简包正例及泄漏反例                                                                                              |
| v2 P2 零提交运行可重放误拒  | 不要求已有rounds非空，但需完整原始输入/配置和受支持语义；真实重放仍待产品                                                                        |
| 固定873/SPO新增续审         | 17文件hash、重复事实数保留、仅完整SPO指定集合无序，事件/动作/轮次保序；actual仍oracle构造                                                        |
| CLI同名首次38失败           | 旧first-failure.json记录digest import冲突；更名verify-release.mjs。无独立完整首跑raw file，只有摘录/原会话transcript，明确无法从归档完整重建首跑 |
| 声明误删失败                | unit-third-run/check-first-run保留；修复后既有重跑通过，不追改失败                                                                               |
| Python环境ENOENT            | check-second-run保留；独立uv sync --frozen后既有重跑，不当产品错误或目标设备通过                                                                 |

raw-logs-index.json列出全部48个现存原始日志及旧记录SHA；raw-logs.tar.gz仅包含这些文件，无新执行输出。最新命令为T11_FIXED_BASELINE_PROBE=1专项65/65零skip及全仓695TS/1052Python；显式lint/format现存日志完整。sources为此前12份检查且归档未改，Mac为此前bash -n；Windows未运行。不以历史窄检查或旧41/45/60计数覆盖最新候选。

父功能缺口：正式T01/T10接口/全产品候选、实际双目标平台/签名/公证/渠道/下载实装、凭据/故障/迁移、真实模型评估/五真人、指定双方审查、CI/正常合并/远端。当前工具无法认证现实证据真实性；外部freeze和独立操作者验证不可省。缺口不由更多合成fixture、默认skip或本准备目录关闭。
