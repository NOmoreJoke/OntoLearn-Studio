# 私有 Store3 Stage A 内部审查

范围：storage.py、project/format3.py、test_project_format3.py。施工基线5f；默认2/FORMAT_VERSION2不翻转，显式3仅临时DB/副本。独立只读审查为 `/root/store_interface_audit` 全范围与 `/root/recovery_design_review` 定点设计/反例；不替代指定ZCode/MiniMax双审。

## 全部意见处置

| 问题 | 实际修复与复核 |
| --- | --- |
| WIP仅凭hash/coverage接受缺载荷、额外键和伪序号checkpoint | 精确键/严格类型/完整application、domain行引用、不可变origin与真实operation/receipt来源；原反例独立均拒绝 |
| 原域不可变trigger/完整结构未验 | 当前domain/app精确SQL、约束、immutable trigger、integrity/FK/旧snapshot hash一并只读核验；缺失拒绝不修 |
| head序号、metadata和当前状态互不对应，learning可非法JSON | 当前head/真实origin/marker/receipt/CP/domain/application互校，完整记录合法性；原反例独立拒绝 |
| 取lease前exists竞态漏备份（P1） | 同OS lifetime lease之后重新stat，actualVersion/schema亦要求备份；前一合规writer在锁边界创建库后无backup请求拒绝，源2不变 |
| 合法旧v1缺操作历史被拒（P2） | origin实际domain revision与已知sequence分开，known历史严格递增但不补造，coverage明确partial；批准make_legacy用于全部v1矩阵及1/2升级重开 |
| 单独load接受legacy/phantom伪receipt来源（P2） | 非递归精确receipt/真实marker/plan hash/域快照/序号核验；legacy不能提供完整应用receipt，StageA app只能源自真实genesis；两独立反例关闭 |
| MAX域revision新提交成功后库不可重开（P2） | 已提交精确幂等返回优先，新操作在旧base检查后/修改前拒超限；MAX-1→MAX成功、精确重试、下一提交整库不变/CP/重开均独立通过 |

全范围审查最终明确支持保存本内部阶段候选，未发现新增阻断。其独立新边界测试2 passed、525 deselected；此前33定点和三文件ruff/格式/diff通过。定点设计审查后续独立16 passed；更正原表述：修前26项pytest通过旁边的附加探针曾输出ACCEPTED_FAKE_RECEIPT forged，不能称“26反例均拒绝”。伪receipt加载缺口其后修复，16定点及最终2项MAX边界复核分属后续源码，不能倒改修前历史。各轮源码匹配实际给定SHA，不用修前结果替代修后。

## 实际验证与原件

- 初pytest3失败/9通过为夹具误写不存在的create_run，改为批准start_run；原失败保留。WIP首次格式/SQLite schema归一化探针失败保留于聊天工具原始输出，未冒充通过或伪造日志。
- 原候选474 passed/44 skipped，相关T01/Store/JobStore990 passed/44 skipped；其后内审发现边界问题，均为被替代候选证据。
- 修后481 passed/44 skipped，修MAX后最终483 passed/44 skipped。44为源格式不存在对应阶段（如v1_created），不计通过。
- 全仓首次因新增handoff文档格式失败而停止，已仅格式化该文件；其后修前源码1697 Python通过仍被MAX修正版替代。最终check-format3-revision-limit.log实际退出0：lint/格式/typecheck/构建/ruff，630 TS、1699 Python通过，44上述skip。
- 全部8份已生成原始log与失败/被替代版本一起封存 `evidence/format3-stage-a-raw-logs.tar.gz`，逐成员重新读取核验；完整大小/hash及最终source SHA见 `format3-stage-a-logs.json`。

最终三个源码hash：storage `81ae013df9cfd22f06800c961a4239e5ed4711322e8e237b637f63b52d2bef4b`；format3 `6ea7d16e9219865f8ab528e607a0fbf3ac68ab4580e1b68c780f30a238c06261`；test `748321022904f1238e7d1ce4da879144c188e7f137efeb9428183c6dcb91e8da`。实际完整JSON样例与schema hash在format3-stage-a-sample.json，唯一DDL仍在源码。

本机无GUI/Electron/native/e2e/HMR/应用外审/密钥/真实用户库。未运行项目包、远端CI或生产。StageA有app结构而无app mutator，完整应用状态当前只能为真实genesis初值；Job-ready、真实全局claim/CAS/学习/恢复/公共3/业务adapter/指定双新审/PR/CI/合并与父功能门仍开放。
