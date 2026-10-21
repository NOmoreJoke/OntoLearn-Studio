# T03 独立内审

审查 agent：`/root/t03_service_review`。只读检查指定工作树私有服务、真实测试、renderer mapping 页面及交接；未改文件、启动 GUI 或消费未批准候选。此报告为开发聊天据该 agent 实际原文整理；不替代指定 ZCode/MiniMax 外审。

## 已发现并复核关闭

| 问题 | 实际修复与回归 |
| --- | --- |
| 合法 XLSX 稀疏尾空格及中间空行误报 ROW_WIDTH | 按标题宽度补空、保留物理行；稀疏测试通过 |
| 公式已缓存空字符串误报无缓存 | 检查选中 sheet 原始 OOXML 中 t=str 和显式空 v；不执行公式；空缓存与缺缓存分别测试 |
| 复合引用错误未定位实际空字段 | 按 reference_columns 每个字段检查，报告实际列与字段 |
| CSV 非法编码用逗号/换行简单计数，忽略引号 | 按引号、转义、CRLF 和多行记录状态定位起始源行/字段 |
| 同文件换 sheet 后迟到旧预览可接受 | 预览绑定 selectionId/sheet/encoding/local generation；改草稿、选源、取消递增代次 |

内审复核实际运行：真实候选依赖解析测试 40 passed；私有页面状态 8 passed；CSV/XLSX 探针核对精确四事实和字符串 001；React SSR 恶意样本转义检查通过。发现 UI 问题后首次回归有 3 failed/5 passed，修正比较条件后 8 passed；保留 `ui-state-after-review.txt` 与 `ui-state-final.txt`。

最终 agent 明确结论：**本轮只读内审通过，已发现的 5 项问题全部关闭；未发现新的明确阻断。** 服务、页面、测试和交接在该结论范围内。

## 未验边界

正式 T00 bridge/公共契约/App、T01 真实应用服务确认/取消/提交对账、T02 定义语义、正式依赖与包内双平台、迁移、指定双新外审、CI 及远端门禁未验。正式接线必须在请求发起时捕获代次，取消时失效，不能在响应到达时用新代次包装旧结果。候选 PyInstaller 验证不等于正式产品包。

## 恢复测试补充复核

继续原Goal新增 `test_mapping_recovery.py`，独立agent实际首跑9项通过；建议加强提交后真实崩溃分支来源精确断言。已改为提交后取消/退出共同核对显式六字段完整预期、映射定义标识/version/全部规则/sourceHash/sheet、mappingState及原历史。agent再次实际复跑9 passed，并明确补强已关闭、本测试范围内审通过、未发现新阻断。仅增加验证，旧实现字节未变；正式job/bridge/UI和包门禁未被该测试替代。

## 四文件生效后的项目依赖/打包候选复核

原独立agent已对本树最新T03候选完整只读复核并实际运行55项mapping测试，零skip全部通过。独立解析锁确认只有三指定新增依赖、engine声明更新，其他旧包记录无变；发行hash/实际许可证hash匹配。PyInstaller collect-all helper实际包含metadata收集；入口仅固定合成probe，拒绝额外路径/脚本/URL；正常、-O、拒绝参数及固定错误真实验证。agent明确代码内审通过、未发现新实现阻断。

其唯一文案收尾意见：integration-request仍有“共享依赖未改/等待旧owner”历史描述。已实际改为四文件已生效交接、T03从批准5f维护的当前状态，T00/T01公共业务请求仍待。只改状态/依据说明，不因此无变化重跑产品。正式应用包内结果后续单独记录；agent未重复打包，结论不覆盖双平台/公共业务接线/指定双新外审/CI。

包内证据最终复核：agent逐项重新hash当前应用670项，entries/bytes/engine/asar/lock/许可证均匹配；源码与包内原始JSON/11cases/版本完全一致，stderr空；日志638TS/1107Py与打包、storage-probe精确结果一致。固定路径脚本scope准确。发现manifest摘要最初只记无末尾LF规范内容hash，未说明实际文件末尾LF；已将actual file SHA `98e2d8478d366d2463681d9232ea56353039a951043f90a911743fd230afc860` 与canonical SHA `9271f6c7b172f6591ec31434cced70ed68b0145c14bc1dc8ed8d08a1f1e28b5c`分列并说明规范化，包字节未变，无需重建/重测。

## 总控登记范围的补充覆盖

登记T03-S1后，新增三个测试实例：缓存外部WEBSERVICE公式及真实外部超链接OOXML，在三个Python socket入口拒绝并计数的条件下仍返回缓存/文本且零调用；CSV文件/列/单格/行上限错误与位置。独立agent实际source suite 21 passed并明确这3项内审通过、无新增阻断。准确政策是“宏拒绝；外部引用只读缓存/文本，不发起网络”，不是拒绝含URL文本的文件；零调用证据仅覆盖两个固定样例和相应socket入口。产品实现与包字节未改变，新增测试/验收另成新候选，旧包不被误称新候选全部门禁已完成。
