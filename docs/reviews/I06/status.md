# I06 / S3 状态

日期：2026-10-20（Asia/Shanghai）。阶段：独立核心实现、无窗口验证和内部只读复核已完成，等待真实依赖接入；完整 I06 未完成。完整 Goal 已于本会话建立，保持 active。

## 身份与保护

- 开发会话：`01a15746-c2e2-7ee0-836b-c8c92346ddd4`；总控/额度唯一负责人：`01a154de-843b-7a00-8a80-51ba1c0aebce`。
- 唯一可写 worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-model-gateway`，分支 `feature/I06-model-gateway`。
- base/启动 HEAD：`1b6df7a220fc9a67d7046133a340085f03f0a96c`；origin `https://github.com/NOmoreJoke/OntoLearn-Studio.git`。尚未冻结完整候选。
- 已完整读取 Goal（含第九节）、scope、transition policy、parallel coordination、state 和 before-I06 两清单。最新指南与原仓库 SHA 均为 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`。AGENTS.md 是唯一启动时 dirty 文件，保护、不暂存、不混入功能。
- 仅写新 `apps/desktop/src/main/model-gateway/`、`tests/unit/i06-*`、`docs/iterations/I06/`、`docs/reviews/I06/`。未写 main/preload/renderer/CSP、公共契约、storage/protocol/失效表、依赖/锁、总控 state 或其他工作区。
- `npm ci --ignore-scripts`、`uv sync --frozen` 建立本 worktree 独立 node_modules/.venv；未链接他线环境。无 Electron/GUI/native/HMR 启动、无凭据提示、无真实模型/真实密钥/业务外发。

## 交付与验证

- [ADR-0004 草案](../../iterations/I06/ADR-0004-model-gateway.md)：进程归属、授权身份/失效、发送竞态与凭据适配器。
- [完整验收和接口需求](../../iterations/I06/acceptance.md)：向 I03/I04/总控提供精确依赖，当前私有形状不作公共协议。
- 实际最终专属测试：62 项（网关 50、凭据边界 12）通过，含真实 loopback 假接收端、定向取消、响应上限与字节复制反例。测试边界不等于实际 OS safeStorage 或接入运行证据。
- `npm run check` exit 0：lint/format/typecheck、66 TS（62 I06 + 4 既有）、生产构建、ruff、198 Python 全通过。构建不包含尚未接线的 I06 模块，其 TS 检查及专属测试单独覆盖；未启动 Electron。
- `npm run verify:sources` exit 0：12 项既有归档源文件一致。I01 归档 M0 更新计划与原仓库当前只读文件 SHA 同为 `c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96`。
- 独立内部只读审查 agent：`/root/i06_design_review`，两项实现意见已修复并获关闭，最终未发现新增阻断，独立重跑 50 网关测试通过；见 [内审记录](internal-review.md)。不替代指定双审。
- 首次 check 仅被 no-control-regex lint 阻断；已等价改为字符码检查，最终完整 check 通过。验证摘要和文件哈希见 [evidence](evidence/validation.json)。

## 依赖、双审和下一步

正式主进程/bridge/窗口/任务联验等待实际 I02/I03/I04 合并；语义相关材料等待相应 I05。然后刷新 develop 基线，核对契约与唯一权限/存储边界，补齐真实持久审计、私有凭据仓库与平台 safeStorage，验证失败不影响本地保存、导出排除与重连。原生/平台行为仅在隔离环境或用户明确时段实测，不在当前桌面启动。

ZCode GLM-5.3/最高、MiniMax M3.1-Flash/xhigh：均未新建正式审查任务、无通过报告。不得以阶段提交或内部审查当作完整冻结候选；实际依赖和全验收后，同一完整 base/head 各新建独立任务并核验真实完成。变更受审代码/测试/配置/依赖/验收/基线即新版双方新审。

push：未执行。PR：未创建。CI：未执行远端候选。合并/远端 develop 核验：未完成。仅完整验收+双方同版本明确通过+意见处置齐后才预约总控串行集成、推送与 PR→develop（创建后 attach_artifact）；实际 CI 及远端核验通过才完成 Goal。当前无实际额度告警，不兑换重置、不新增支付、不擅自换模型。
