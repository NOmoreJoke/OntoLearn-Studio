# T10 私有准备实现

范围：基于批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，不修改公共契约、SQLite、writer、网关或 App 接线。

## 只读包检查

`transfer.inspect_candidate(bytes)` 是内存只读检查器，不接受系统路径、不解压落盘、不创建项目、不加载任意代码。`t10-envelope-draft-1` 只供本线样例预验，不是正式迁移格式，公共能力注册表没有发布该方法。

清单严格限定版本、声明类型、四个选择项和文件 path/role/size/SHA256。文件名采用可移植 ASCII 相对路径，拒绝穿越、盘符、反斜杠、NUL、Windows 保留名、重复、符号链接、目录、加密、未知压缩/角色/字段及清单外文件。检查 EOCD、连续本地成员、中央目录、实际压缩流终止/大小/CRC 与 SHA，拒绝隐藏成员、前后缀、间隙、压缩流尾随字节和被声明大小截断的额外输出。

防御预算为 40 MiB 包、32 MiB 解压内容、8 MiB 成员、64 KiB 清单、256 个成员；这是私有解析边界，未经业务容量测量，不是 Q5 产品通过线。ZIP64、多磁盘、注释、extra 和流式 data descriptor 当前明确拒绝，后续正式格式由 owner 取舍。

`declared_kind` 仅保留清单声明。声明完整但缺定义/断言/来源所有权/checkpoint 的草案被拒绝；即使角色齐全，也不能据此证明 payload 覆盖或支持版本。所有结果均返回 `import_allowed/restore_current/rerun_mapping/replay_runs=false`，原因固定为格式未批准及 payload 未验证。选择项与实际包含项分别列出。没有原文件、推导、历史或会话不自动降为模板；不强加未选历史或独立 undo 文件。正式完整包判定仍以 FR-1000 当前状态要求为准。

禁止 vault、credentials、audit、authorization 等角色，仅证明未知/私有角色不会作为已知成员通过。**不证明允许业务 payload 的自由文本没有凭据，也不证明已实现 A-06 端到端排除。** 此前置条件由批准投影与最终导出链落实；不能读取真实密钥来扫描或直接导出整个数据库。

## 报告与页面

私有 `parsePreparedReport/renderPreparedReport` 采用 zod strict、总文本/节点预算、普通数据对象/数组限制，拒绝未知键、重复 task/attempt、通过却没有证据、与当前版本矛盾的结果和访问器；错误统一为固定文本。报告涵盖 FR-1001 全部栏目，结果显式绑定输入版本、执行语义、范围及当前/过期/历史/失败/取消状态。

动态内容只进入经过编码的 HTML 文本节点；无脚本、样式、链接、图片、外部字体或远程资源。CSP 复用现有 `csp.ts`，不创建第二策略源。中文、引号、标签字面量、实体和换行按文本保留；静态 span 避免 pre 吞掉首个 LF。报告有固定内部预验标识。

学习分类按每次尝试的检查、操作、提示和 Agent 辅助记录计算；未检查/失败不等于掌握，完整示范或完整代做不计独立迁移，旧尝试不被新尝试覆盖。**该 DTO 尚不是可信学习记录来源**；真实证据由 T09/T08/T01 投影，不能把客户端自报字段当正式掌握证明。

`TransferPanel` 是未接 App 的独立组件：四个选择项默认关闭、三项能力分别显示未验证、导入/导出按钮禁用，投影错误有恢复说明。它不读取 Node/文件路径，不调用通用 IPC，不执行 innerHTML，不对外请求。

私有主进程报告文件服务固定一份已渲染产物后，经过 main-owned picker 适配器向新文件发布；真实文件系统与异常收尾设计见 [report-file-publication.md](report-file-publication.md)。不替代可信投影或正式文件选择授权。

## 可复现预验

```sh
uv run --frozen pytest packages/engine/tests/test_transfer_inspection.py -q
npx vitest run tests/unit/t10-report.test.ts
npm run check
node docs/iterations/T10/render-probe.mjs
```

最后一条只生成合成 HTML 与组件 SSR，不启动浏览器。浏览器预验使用 Playwright CLI 的独立 headless Chrome 会话；最新报告文件服务产物的 12 个恶意字符串及首 LF 完整出现在文本、危险 DOM 为零、脚本哨兵未触发、外部请求为空。独立组件另有四个默认未选项、两项禁用动作和错误路径证据。原始命令与结果保存在本线 evidence，运行时 HTML 可随脚本重建。

完整接点请求见 [interface-needs.md](interface-needs.md)。正式 schema、批准 checkpoint、业务投影、原子发布与跨设备操作未就绪，不注册生产能力、不承诺迁移或发布完成。
