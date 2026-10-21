# T03 数据映射状态

2026-10-21（Asia/Shanghai）。Owner：功能开发聊天 `01a15bcd-f838-75a2-b2c3-692915cc91c3`；本功能 Goal active。

## 身份与责任

- 工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping`；分支 `feature/weekly-t03-mapping`；批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 启动仅 ` M AGENTS.md`，初始指南 SHA `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`；总控政策追加后 SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759` 已实查匹配，保持未暂存，不进入产品提交。
- 独占责任：`packages/engine/src/ontolearn_engine/mapping/`、`packages/engine/tests/test_mapping_*.py`、`apps/desktop/src/renderer/src/mapping/`、`tests/unit/t03-*.test.ts`、`tests/fixtures/mapping/`、`docs/reviews/T03/`、`docs/iterations/T03/`。现存共享文件、锁/CI和root tasks/state未改。
- FR-300–304、D/G M-01–06 与 PRD11–12/跨模块/迁移原门保留；私有实现验证完成，父模块未验收。

## 已交付与验证

- 真实CSV解析、候选XLSX已保存公式值/稀疏空格解析；稳定单/复合身份及引用、明确转换、全部RDF/来源/增删改/人工冲突/旧预览重检；只输出批准Store计划，无第二写入通道。
- 私有三步受控页面、完整预览分页、冲突返回路径、显式确认；未接入回调时禁用正式操作。项目/版本/选择/工作表/编码/代次隔离，取消迟到不能复活旧预览。
- `npm run check` 最终exit0：638 TS tests；1088 Python passed、4明确XLSX skip（项目依赖未批准）；lint/格式/类型/构建/ruff均通过，原件 `check-final.txt`。
- 精确隔离候选 openpyxl3.1.5/et-xmlfile2.0.0/defusedxml0.7.1：40解析/映射测试通过；页面状态8通过；React SSR标记/样本转义探针通过，不声称CSS/浏览器交互通过。
- 真实PyInstaller候选CLI包已构建并执行CSV/XLSX精确四事实探针exit0，含双工作表选择。首跑缺现有invalidation JSON及下一次相对add-data失败原件保留；最终沿用现有build同类collect-data/collect-all成功。该包不是正式产品包或目标平台验收。
- 独立agent `/root/t03_service_review` 明确只读内审通过，发现5项全部关闭；详见 `internal-review.md`。不替代指定双外审。
- T09固定 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 输入获总控批准后，manifest SHA及17项逐一核对通过；本线equipment.csv与获批文件字节相同。不消费其服务、变化HEAD或旧helper，不用expected填充Store；无变化不重跑产品。
- 实现/测试逐文件SHA及候选exe SHA见 `validation.json`，验收范围见 `../../iterations/T03/acceptance.md`。

## 下一交付与当前缺口

精确请求已实际发给总控：`../../iterations/T03/integration-request.md`、`parser-dependency-candidate.json`。等待owner批准项目依赖/唯一锁与正式打包探针；T00/I06受信文件与sheet选择、唯一公共契约/错误/分页/bridge/App；T01复用已批准snapshot/load_snapshot，正式确认/Store.commit/job取消与标记对账；T02正式定义语义；T08增强草稿与T10迁移保留来源。

不消费未批准候选。最终刷新获批develop和依赖、真实联验、冻结base/head、同候选ZCode GLM-5.3最高与MiniMax M3.1-Flash/xhigh各新完整任务实际通过/读回/意见处理后，才能push/PR/实际CI/正常合并/远端核验；均尚未执行。资源仍由总控预约，当前不操作审查应用。本机GUI/e2e/native/HMR/凭据/付费/对外联系均未执行，正式双平台与父功能完整验收仍待。

## 操作政策接收

已在安全边界全文读取总控透传第九节及无桌面段，实际透传独立agent。第九节SHA `1f57a08e909e9d49a6e2c2d6e7012beec3e22b8e3c9e8eacad22c84dfb2d4b54`；无桌面SHA `5215df2ead4745e7d74f137c4fa6ac837a54114590b5dee2d83cd16bb728551d`。已有权益仅官方已核实方式/唯一负责人；Codex reset逐次本人确认/阈值/幂等，无新增付款权限。

ZCode默认yolo完全访问、MiniMax默认bypassPermissions始终授权新政策亦已全文接收并透传；各审查任务仍须实际读回模式，完全访问不改变只读职责/指定模型/无桌面/付费密钥边界。Goal/分支和归档输入不重建，仅操作政策不触发无变化产品重审。

启动读取异常：本树缺少AGENTS引用的M0架构更新计划，已只读主checkout对应全文；没有复制或改写共享文件。
