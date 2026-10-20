# I06 / S3 状态

日期：2026-10-20（Asia/Shanghai）。阶段：独立核心实现、无窗口验证和内部只读复核已完成，等待真实依赖接入；完整 I06 未完成。本次恢复后重新累计三次核验，I03/I04 接线依赖仍未满足，正式 update_goal 已再次返回 blocked。完整目标、同一开发会话和既有实现保留；不标为 paused 或 complete。

## 身份与保护

- 开发会话：`01a15746-c2e2-7ee0-836b-c8c92346ddd4`；总控/额度唯一负责人：`01a154de-843b-7a00-8a80-51ba1c0aebce`。
- 唯一可写 worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-model-gateway`，分支 `feature/I06-model-gateway`。
- base/启动 HEAD：`1b6df7a220fc9a67d7046133a340085f03f0a96c`；origin `https://github.com/NOmoreJoke/OntoLearn-Studio.git`。尚未冻结完整候选。
- 初始核心检查点：`8336559c65b8d8ece3fcb15ea3dc224c398b7d9c`，流程追加为 `56de8312c72d8ec2dd7a6739ac01f5737e5914fe`。续跑发现凭据密文与主体/版本绑定缺口，已修复并完成新版内部复核和验证，后续检查点记录于本文件末尾；旧检查结果仅对应旧版，不作为新实现通过依据。以上均不是完整验收或指定双审候选。
- 当前核心实现源码检查点：`637e0e6869091610141b0b9b9ebf01545205e648`；此后有流程文档与超时/容量专属测试追加，五个实现模块哈希未变，完整候选尚未冻结。每次新版验证均保留独立证据，不沿用旧版测试通过替代新增反例。
- 已完整读取 Goal（含第九节）、scope、transition policy、parallel coordination、state 和 before-I06 两清单。最新指南与原仓库 SHA 均为 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`。AGENTS.md 是唯一启动时 dirty 文件，保护、不暂存、不混入功能。
- 仅写新 `apps/desktop/src/main/model-gateway/`、`tests/unit/i06-*`、`docs/iterations/I06/`、`docs/reviews/I06/`。未写 main/preload/renderer/CSP、公共契约、storage/protocol/失效表、依赖/锁、总控 state 或其他工作区。
- `npm ci --ignore-scripts`、`uv sync --frozen` 建立本 worktree 独立 node_modules/.venv；未链接他线环境。无 Electron/GUI/native/HMR 启动、无凭据提示、无真实模型/真实密钥/业务外发。

## 交付与验证

- [ADR-0004 草案](../../iterations/I06/ADR-0004-model-gateway.md)：进程归属、授权身份/失效、发送竞态与凭据适配器。
- [完整验收和接口需求](../../iterations/I06/acceptance.md)：向 I03/I04/总控提供精确依赖，当前私有形状不作公共协议。
- 当前专属测试：77 项（网关 55、凭据边界 22）通过，含真实 loopback 假接收端、定向取消、响应上限、字节复制、密文身份/严格信封及超时/容量反例。测试边界不等于实际 OS safeStorage 或接入运行证据。
- 新版 `npm run check` exit 0：lint/format/typecheck、81 TS（77 I06 + 4 既有）、生产构建、ruff、198 Python 全通过。构建不包含尚未接线的 I06 模块，其 TS 检查及专属测试单独覆盖；未启动 Electron。
- `npm run verify:sources` exit 0：12 项既有归档源文件一致。I01 归档 M0 更新计划与原仓库当前只读文件 SHA 同为 `c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96`。
- 独立内部只读审查 agent：`/root/i06_design_review`，两项实现意见已修复并获关闭，最终未发现新增阻断，独立重跑 50 网关测试通过；见 [内审记录](internal-review.md)。不替代指定双审。
- 首次 check 仅被 no-control-regex lint 阻断；已等价改为字符码检查，最终完整 check 通过。验证摘要和文件哈希见 [evidence](evidence/validation.json)。
- 续跑新增的四项凭据绑定反例在旧实现上实际失败；密文改为封装并核对 ref/主体/版本，新增严格格式反例。独立 agent 再次实际验证 72/72，并确认绑定问题关闭、未发现新增阻断，见 [记录](credential-binding-review.md)。本轮 check 先后遇到测试变量 lint/格式错误，均修正后完整通过；新版文件哈希和日志摘要见 [证据](evidence/credential-binding.json)。
- 依赖已通过正式 `wait_threads` 重新核验：I03/I05 的实际 turn 为 inProgress；I02 为 inProgress，尚无 I02/I03 合并证据，I04 在总控清单仍 pending。未把对 I02 的审查应用授权扩大到本会话桌面操作；本会话继续无 GUI。
- 2026-10-20 总控请求受限错误需求：已整理 [11 类公共错误映射输入](../../iterations/I06/public-error-requirements.md)，含建议 messageKey、严格空 safe params、禁止透传集合和 retryable/禁止自动重放边界；供总控转交 I03。未修改公共 contracts 或提前接线。远端 develop 本次只读核验仍为 `1b6df7a220fc9a67d7046133a340085f03f0a96c`，正式依赖尚未合入。
- 已实际只读核对 I03 的 `docs/reviews/I03/handoffs/I06-error-disposition.md`（SHA-256 `25910655ff5f03e20509393a45863af0093a0d7d0436cceb72ff1603deaee50a`），[承接读回](../../iterations/I06/public-error-requirements.md)记录了通用错误仅安全兜底、新契约版本/公共正反例/双审后才精确接线、独立 cancelled 结果分支、网关新错误空 params/false、retryable 不授权自动重放及写任务先对账。现有 INVALID_REQUEST 的固定 `{field:"params"}` 兜底按实际源文件明确保留，没有误写为空参数。未修改 I03、共享契约、实现或测试；Goal 仍为 blocked，原待验不变。
- 超时/容量续跑追加五项验收反例，未修改实现：凭据等待超时后零外发及恢复复用、审计等待超时零外发、第五个请求不排队且取消释放容量、持续 503 最多两次尝试、真实无响应本地接收端超时不自动重放。前两项以受控时钟验证等待边界，最后一项使用真实 Node socket/计时；见 [本轮证据](evidence/timeout-capacity.json)。此类测试追加仍属于未来完整冻结候选的受审范围，不能沿用指定双方旧版通过（当前也无指定通过）。

## 依赖、双审和下一步

### 本次恢复：I02 合并已核验，I03/I04 仍待就绪

- 本次已直接核验远端 develop 为 `c2f9b038b23f9f48cdbb8f433a89b55a00edc9d3`，PR #3 实际 MERGED 到 develop，原 base 是该 merge 的祖先；PR run39364497557 的 Quality/macOS/Windows 三项 SUCCESS。合并后 push run39364825646 同一 head 也 completed/success，三个实际 job 均 success。没有沿用总控陈旧 state 中 I02 merge=null 的值。
- I03 的实际任务已 terminal（idle/completed，cursor `4e760116-fc4e-44e4-82df-053fdee3eaa5:91`），不是仍在运行的等待句柄。已观察到本地候选 `8305d204bb132eb8e695b2122ecbf48f67120f2a` 仅在 feature/I03-protocol-contracts；开发者回执指定双审未创建、未推送/合并。I04 在总控清单仍 pending，无线程 handle。依赖门未全部满足，不能提前接线或把本地冻结当已合并。
- I06 保持原分支/实现基线，没有 rebase、产品接线、依赖或测试修改。本轮只追加 [真实依赖核验证据](evidence/dependency-resume-20261020.json)，不重复无变化检查；已有实现/测试哈希仍匹配上次完整验证。I02 依赖已解除，剩余为 I03/I04 合并与后续隔离运行条件；本次恢复按新一轮核验处理。

### 本次恢复后三次核验：再次 blocked

- 第一次：I02 实际合并已核验，I03 处于本地冻结、未双审/合并状态，I04 pending；没有把 I02 完成当成全部接线依赖完成。
- 第二次：正式句柄确认 I03 已恢复新 turn，正在刷新基线且审查应用时段只预约给 I03；执行一次 45 秒实际等待，cursor 到 `4e760116-fc4e-44e4-82df-053fdee3eaa5:98`，仍 inProgress。没有把 I03 的 UI 许可扩大到 I06。
- 第三次：对同一活跃 turn `01a15763-b232-7132-b72f-d23b8b7c3baf` 再完成 45 秒等待，cursor 到 `4e760116-fc4e-44e4-82df-053fdee3eaa5:105`，仍 active/inProgress；远端 develop 仍 `c2f9b038b23f9f48cdbb8f433a89b55a00edc9d3`。总控清单 I03 merge=null、I04 pending/无线程。观察超时不等于任务停止，没有重启或打断 I03。
- 连续三次相同的 I03/I04 依赖门未满足；当前 I06 可独立实施及验证的授权工作已收口，无法在不提前复制未批准契约/接线或违反平台环境限制的情况下继续必要实施。正式工具已返回 blocked；不是因为实现困难、额度不足或单纯等待一次。
- 当前保全点为 `ca59135c4abc137290440f148357445e021dcef6`，后续仅追加本记录；未改实现/测试/依赖，未 push。由总控核验 I03、I04 真实合并后恢复同一会话，刷新包含 I02/I03/I04 的基线并继续原全验收及指定双审。实际平台/外部审查环境仍按原约束安排，不因恢复自动取得 GUI 许可。

### 此前阻塞核验与恢复条件（历史快照，I02 状态以上文为准）

- 同一“正式依赖尚未合并、平台/指定审查缺少本会话可用环境”条件跨初始交付及后续多次 Goal turn 持续存在；期间仍完成凭据绑定修复、I03 接口交接和超时/容量反例。当前未发现仍可在授权阶段内独立推进的必要工作，不能用新文档/重复测试或提前复制未批准协议替代实际依赖。
- 本次 `git ls-remote origin refs/heads/develop` 实际返回 `1b6df7a220fc9a67d7046133a340085f03f0a96c`；核心/测试哈希与最新已通过验证一致。检查点为 `208f48bf9888a78b19e4a8049eb29772b3f10f24`，后续仅追加流程记录。
- 对同一实际任务执行 45 秒 `wait_threads`，均仍 inProgress：I03 cursor `4e760116-fc4e-44e4-82df-053fdee3eaa5:49`，已明确收到 11 类需求，尚在形成新候选；I02 cursor `72c9322d-f0e9-4b8f-bd47-081efdc63a8c:638`，正在核对 GLM 报告勘误，未合并。总控清单 I04 仍 pending、无任务 handle。观察超时不等于任务终止，没有重启他方任务。
- 正式 `update_goal(status=blocked)` 返回 blocked；未缩小完整目标，也未声称全验收、指定双审或远端集成已完成。
- 恢复：由同一开发会话在总控核验 I02/I03/I04 实际合并后继续；刷新包含依赖的 develop，按 I03 冻结公共契约映射并接线。实际 safeStorage/native 与指定双外审须有不干扰用户的隔离环境或用户明确时段；当前仍无本会话 GUI 许可。语义特定来源仅在需要时等待 I05。之后按原全验收 → 同版双方独立通过 → PR/实际 CI/正常合并/远端核验完成，不能沿用阶段内审作为指定通过。

正式主进程/bridge/窗口/任务联验等待实际 I02/I03/I04 合并；语义相关材料等待相应 I05。然后刷新 develop 基线，核对契约与唯一权限/存储边界，补齐真实持久审计、私有凭据仓库与平台 safeStorage，验证失败不影响本地保存、导出排除与重连。原生/平台行为仅在隔离环境或用户明确时段实测，不在当前桌面启动。

ZCode GLM-5.3/最高、MiniMax M3.1-Flash/xhigh：均未新建正式审查任务、无通过报告。不得以阶段提交或内部审查当作完整冻结候选；实际依赖和全验收后，同一完整 base/head 各新建独立任务并核验真实完成。变更受审代码/测试/配置/依赖/验收/基线即新版双方新审。

push：未执行。PR：未创建。CI：未执行远端候选。合并/远端 develop 核验：未完成。仅完整验收+双方同版本明确通过+意见处置齐后才预约总控串行集成、推送与 PR→develop（创建后 attach_artifact）；实际 CI 及远端核验通过才完成 Goal。当前无实际额度告警，不兑换重置、不新增支付、不擅自换模型。
