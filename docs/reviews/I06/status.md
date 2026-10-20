# I06 / S3 状态

日期：2026-10-20（Asia/Shanghai）。阶段：独立核心实现、无窗口验证和内部只读复核已完成，等待真实依赖接入；完整 I06 未完成。完整 Goal 已于本会话建立，保持 active。

## 身份与保护

- 开发会话：`01a15746-c2e2-7ee0-836b-c8c92346ddd4`；总控/额度唯一负责人：`01a154de-843b-7a00-8a80-51ba1c0aebce`。
- 唯一可写 worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-model-gateway`，分支 `feature/I06-model-gateway`。
- base/启动 HEAD：`1b6df7a220fc9a67d7046133a340085f03f0a96c`；origin `https://github.com/NOmoreJoke/OntoLearn-Studio.git`。尚未冻结完整候选。
- 初始核心检查点：`8336559c65b8d8ece3fcb15ea3dc224c398b7d9c`，流程追加为 `56de8312c72d8ec2dd7a6739ac01f5737e5914fe`。续跑发现凭据密文与主体/版本绑定缺口，已修复并完成新版内部复核和验证，后续检查点记录于本文件末尾；旧检查结果仅对应旧版，不作为新实现通过依据。以上均不是完整验收或指定双审候选。
- 当前受检核心检查点：`637e0e6869091610141b0b9b9ebf01545205e648`；之后仅追加本引用和证据的 SHA 对应，不改变实现或验收。工作区仍只保留 protected AGENTS.md dirty。
- 已完整读取 Goal（含第九节）、scope、transition policy、parallel coordination、state 和 before-I06 两清单。最新指南与原仓库 SHA 均为 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`。AGENTS.md 是唯一启动时 dirty 文件，保护、不暂存、不混入功能。
- 仅写新 `apps/desktop/src/main/model-gateway/`、`tests/unit/i06-*`、`docs/iterations/I06/`、`docs/reviews/I06/`。未写 main/preload/renderer/CSP、公共契约、storage/protocol/失效表、依赖/锁、总控 state 或其他工作区。
- `npm ci --ignore-scripts`、`uv sync --frozen` 建立本 worktree 独立 node_modules/.venv；未链接他线环境。无 Electron/GUI/native/HMR 启动、无凭据提示、无真实模型/真实密钥/业务外发。

## 交付与验证

- [ADR-0004 草案](../../iterations/I06/ADR-0004-model-gateway.md)：进程归属、授权身份/失效、发送竞态与凭据适配器。
- [完整验收和接口需求](../../iterations/I06/acceptance.md)：向 I03/I04/总控提供精确依赖，当前私有形状不作公共协议。
- 当前专属测试：72 项（网关 50、凭据边界 22）通过，含真实 loopback 假接收端、定向取消、响应上限、字节复制及密文身份/严格信封反例。测试边界不等于实际 OS safeStorage 或接入运行证据。
- 新版 `npm run check` exit 0：lint/format/typecheck、76 TS（72 I06 + 4 既有）、生产构建、ruff、198 Python 全通过。构建不包含尚未接线的 I06 模块，其 TS 检查及专属测试单独覆盖；未启动 Electron。
- `npm run verify:sources` exit 0：12 项既有归档源文件一致。I01 归档 M0 更新计划与原仓库当前只读文件 SHA 同为 `c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96`。
- 独立内部只读审查 agent：`/root/i06_design_review`，两项实现意见已修复并获关闭，最终未发现新增阻断，独立重跑 50 网关测试通过；见 [内审记录](internal-review.md)。不替代指定双审。
- 首次 check 仅被 no-control-regex lint 阻断；已等价改为字符码检查，最终完整 check 通过。验证摘要和文件哈希见 [evidence](evidence/validation.json)。
- 续跑新增的四项凭据绑定反例在旧实现上实际失败；密文改为封装并核对 ref/主体/版本，新增严格格式反例。独立 agent 再次实际验证 72/72，并确认绑定问题关闭、未发现新增阻断，见 [记录](credential-binding-review.md)。本轮 check 先后遇到测试变量 lint/格式错误，均修正后完整通过；新版文件哈希和日志摘要见 [证据](evidence/credential-binding.json)。
- 依赖已通过正式 `wait_threads` 重新核验：I03/I05 的实际 turn 为 inProgress；I02 为 inProgress，尚无 I02/I03 合并证据，I04 在总控清单仍 pending。未把对 I02 的审查应用授权扩大到本会话桌面操作；本会话继续无 GUI。
- 2026-10-20 总控请求受限错误需求：已整理 [11 类公共错误映射输入](../../iterations/I06/public-error-requirements.md)，含建议 messageKey、严格空 safe params、禁止透传集合和 retryable/禁止自动重放边界；供总控转交 I03。未修改公共 contracts 或提前接线。远端 develop 本次只读核验仍为 `1b6df7a220fc9a67d7046133a340085f03f0a96c`，正式依赖尚未合入。

## 依赖、双审和下一步

正式主进程/bridge/窗口/任务联验等待实际 I02/I03/I04 合并；语义相关材料等待相应 I05。然后刷新 develop 基线，核对契约与唯一权限/存储边界，补齐真实持久审计、私有凭据仓库与平台 safeStorage，验证失败不影响本地保存、导出排除与重连。原生/平台行为仅在隔离环境或用户明确时段实测，不在当前桌面启动。

ZCode GLM-5.3/最高、MiniMax M3.1-Flash/xhigh：均未新建正式审查任务、无通过报告。不得以阶段提交或内部审查当作完整冻结候选；实际依赖和全验收后，同一完整 base/head 各新建独立任务并核验真实完成。变更受审代码/测试/配置/依赖/验收/基线即新版双方新审。

push：未执行。PR：未创建。CI：未执行远端候选。合并/远端 develop 核验：未完成。仅完整验收+双方同版本明确通过+意见处置齐后才预约总控串行集成、推送与 PR→develop（创建后 attach_artifact）；实际 CI 及远端核验通过才完成 Goal。当前无实际额度告警，不兑换重置、不新增支付、不擅自换模型。
