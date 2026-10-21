# 草稿CAS纯计划器独立内审

范围：新增 `project/draft_plan.py` 和专用 `test_project_draft_plan.py`。不涉及schema、SQLite writer、公共DTO或权限授予；Store3 adapter后续仍须在事务内重新载入真实header/CAS/claim/receipt。UI本地编辑token不等于持久header generation。

独立审查者 `/root/store_interface_audit` 已实际全文读更新共同指令，SHA `9717f699e14b5941e15d90269f33cbebc32ef9bec6e7439739be848753419880` 匹配，回执第九节及无桌面全文约束。只读审查，无GUI/文件修改。

首轮14项测试通过，但独立探针发现P2：孤立Unicode surrogate在构造时被接受，随后fingerprint/content_hash严格UTF-8编码失败。身份字段也有同型问题。

修复：身份和canonical内容构造边界严格验证UTF-8编码，固定ValueError明确拒绝，不替换字符。新增嵌套值/键、project/editor、直接DraftHead及正常中文/emoji/组合字符完整保留反例。

最终独立复核：**P2关闭，无新阻断，支持冻结纯计划器阶段。** 独立20 passed，ruff/格式和git diff --check通过；来源版本、旧CAS、删除墓碑、恢复代次向前、JSON null与删除区分均保持。

受审源码SHA-256：`8543f36dbdd480f22ace7cc2dba9bfda511d03db0d8fbd4c1eff0d123da7d2f3`。新全仓验证结果以status及本阶段日志manifest为准，不能引用上一版全仓代替。

此结论不覆盖持久Store3、真实双连接并发、checkpoint来源/coverage/确认、人类授权或公开桥接；没有把纯函数模拟当数据库成功。持久化启用与格式3基础候选仍由同一T01聊天继续。
