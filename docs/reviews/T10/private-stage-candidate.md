# T10 私有服务阶段候选（待总控登记）

建议名称 `T10-S1 私有包检查与安全报告文件服务`。此为已实现能力的可审候选，不改写 T10 的完整 Goal，不批准内部包格式、不开放迁移，也不关闭父功能验收。

## 可独立审查的范围

产品候选固定源自实现提交 `d3546af3b6fe895957f9626fd4de28bf59dc600a`、`c3c7e90f721344113c4279d663127f9c8d5bda59`；随后提交仅证据及隔离验证工具。完整 diff 限于本线启动授权的 transfer/project-transfer/renderer-transfer、T10 tests/fixtures/docs。未改公共协议、Store、writer、App/preload/共享配置/锁/CI。

1. Python 只读、有界 ZIP 候选信封检查：拒绝危险路径/保留名/符号链接/隐藏成员/结构重叠/长度和压缩尾部异常，核对严格角色、选项和内容 hash。内部 draft 版本未批准，始终不承诺 import/restore/rerun/replay 可用。
2. 严格输入、纯文本转义和固定 CSP 的内部 HTML 报告、未接线页面：覆盖 FR-1001 所需报告栏目，逐 attempt 区分证据/辅助/独立表现；当前页面没有产品客户端输入通道。实际可信投影尚待 owner 接入；合成输入不等于真实学习验收。
3. 私有主进程报告文件服务：不可变 artifact、固定 hash/长度、main-owned picker、排他暂存/实际字节与路径身份核验、原子不覆盖发布、取消、发布不明状态及显式协调、耐久性/清理状态，禁止把发布后的错误误报成未发布。
4. 无 host GUI 的独立 Linux arm64 native 保存/取消探针，以及真实文件 HTML 安全显示的独立浏览器证据。两者的证据范围分别记录，不冒充通用 e2e、正式 App 接线或双平台验收。

## 验证及审查入口

- 整仓 `npm run check`，稳定结果 691 TS/1,112 Python，与lint/格式/类型/构建通过；最后工具增量复测的原始日志另存。
- 定向 T10：60 Python、18报告TS、43文件服务TS；Linux 容器内61TS/60Python。
- 报告文件服务内审实际3项P2修复并复核；前次2项P2历史保留。隔离验证工具独立审查及真实native读回见 `isolated-native-review.md`。
- `verification.md`、`report-file-internal-review.md`、`evidence/verification-summary.json`、`evidence/browser-summary.json`、`evidence/isolated-native/`；原生失败attempt1/2及成功attempt3均保留，`manifest.json`固定原件hash。

## 完整 T10 尚需完成

批准正式格式/schema与完整checkpoint、可信且排除vault/凭据/发送授权的业务投影、唯一writer原子导入、真实学习与重放语义、公共同代次/项目/窗口接线、FR-1000/1001/104、A-06–08、G.6、12.4/12.5、全部父功能及跨模块门、包内与双平台验收。完整包未选原文件/推导/历史/会话不应误降模板；无原文件仅影响直接重跑，缺相应运行输入仅影响对应重放。

目前无指定双方新任务外审、push、PR、CI、合并或发布。阶段候选须总控明确登记后才进入共享 GUI 队列；只有对应真实审查任务及全报告、问题闭环和读回才算外审。即使阶段获准正常合并，也不代表上述完整 T10 已通过。
