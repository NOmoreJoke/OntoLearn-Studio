# 既存结果材料与应用服务：内部独立审查

2026-10-21；独立只读 agent `/root/i06_design_review`。批准基线 develop5f910b52，阶段起点4ace4c4；没有读取 I05 未合并候选作为批准接口。来源/应用服务/私有取消修改及专属 Store/worker 测试接受复核；完整 S3 与指定双方审查状态见 [status](status.md)。

## 接口审查与采用

reviewer 核对 coordinator._authorize、JobStore.result_get/result_page/get_job、EngineSupervisor 与当前 schema/registry，确认 main allowedProjects 是项目级读取许可；DTO scope 仅图层，不是字段外发权。结果的输入/参数/实现摘要不是正文 hash，当前没有字段 provenance 或 live-current lease。采用其约束实现整份结果读取器：固定 main 项目和 supervisor；全页及 producer/job/版本校验；复制后真实字节摘要、读完完整复核；明确历史选择、回收拒绝、会话/项目关闭失败；授权另行确认，不由读取自动授予。

当前 runtime-only 默认不接纳 test.*；专属合成模式只用于本线真实 I04 coordinator/worker/Store 验证。批准业务 producer 仍 design-only，不能据此声称查询/推理/SHACL 材料已贯通。原始 scope/依赖与实际字段来源差异保留于 [精确接口草案](../../iterations/I06/narrow-interface-draft.md)。

## 首次失败与处置

首轮16项中10通过、6失败；原因是测试在常驻协调器持有 lifetime writer lease 时重新打开 JobStore 或另一个同 DB supervisor，真实 STORAGE_BUSY 拒绝了错误夹具。reviewer 独立跑历史 collect 反例得到相同失败；没有把它登记为预期回收成功。

修正后额外参数与确认计划在启动前准备；跨项目检查用同一写者的明确 allowlist。历史回收在旧 engine 正常停止并等待租约释放后使用实际 JobStore，再开新 engine/source。分页间回收使用专属 coordinator-fixture.py 的一次同写者 hook：原 result.page 返回后调用 self.store.collect_cache，不新增 RPC、不修改生产 coordinator、不绕过 writer lease；该用例明确属于故障探针。

模型等待期间的本地保存改走同一真实 coordinator/worker 的 approved test.atomic，通过真实 Store.commit、operation.get 提交标记和 projectRevision 验证；停机后重新读取 Store snapshot 确认定义已保存。它证明基础设施保存路径与模型等待独立，不冒充正式产品保存 UI、导出或窗口失败隔离。原失败日志及对应源码快照保存在 tests/i06-stored-material/out/r1-source，不覆盖或隐藏。

修正后首批16/16；之后新增实际内容字节变化、第二真实 worker 在分页间更新 current、释放 leaf 取消关联 derived、整批实际5秒 deadline 与三类伪造来源输入反例，总23项。旧网关/持久门组合91项通过。完整 check793TS/1052Python通过；之后只补预览集合128硬界，必要 lint/typecheck/23项通过，不重跑无关 Python 或平台。具体日志/source/test hashes 见阶段 manifest。

## 最终只读复核

- reviewer 实际重跑最必要三个修正用例，3/3通过：历史回收恢复、同写者原子提交、释放来源终止关联派生调用。没有重跑全库或旧平台。
- 私有应用服务有整批5秒复核预算，读取许可与显式外发确认分开；每次调用独立 AbortSignal，只取消命名调用，其他调用/未变化 grant 可继续。释放来源使关联活动调用取消，晚到结果不能创建新权限；无新增外发绕过。
- 草案最初“替换选择仍后台继续”和当前释放即取消不同，已统一为当前安全取消语义；批次原子替换/reusable 投影/终态 ledger 仍是未实现扩展。表格 union 已转义或移为命名类型，精确参数列可读。
- 最终回执：“未发现新增阻断”；预览集合128检查与新增之间无 await。此是内部阶段审查，不是公共 schema 批准或指定双模型通过。

A-03 可信字段映射与其他列零外发仍未由此整份结果链验证。最后读取与 socket 之间没有 Store 原子 lease，源正文摘要不替代许可/来源证明；当前只能解释明确选择的不可变材料及读取时状态。正式 main/窄 bridge/UI/保存与可用导出日志排除/窗口联验、I05真实语义、跨平台事实缺口和指定双方全范围新审均保留。
