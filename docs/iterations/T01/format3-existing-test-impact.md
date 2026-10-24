# 格式3既有测试路径影响核查

仅静态范围核查，不是写权交接或运行通过。当前批准基础5f，T01实现恢复提交d9d7138；新格式未启用。通过 `rg --files`、`rg -l` 和定点读取发现以下既有逻辑路径包含版本2。这里的“包含”不表示全部必须改；bootstrap2、旧端拒绝样例、旧格式迁移与独立health兼容应分别保留，禁止机械替换所有2。

## 可确认的类型/运行入口

- `packages/contracts/src/index.ts` 的 ProjectView.formatVersion 固定2。
- `packages/contracts/src/v2.ts` 的 hello matchesResponse 检查 supportedVersions 包含2。
- `apps/desktop/src/main/engine.ts` 的 selectedVersion、hello supportedVersions、请求/通知相关帧版本均有固定2。
- `packages/engine/src/ontolearn_engine/coordinator.py` 实际请求/响应/通知及协商2，需要明确bootstrap2与业务3分派。
- `job_store.py` 的 project_get 直接报告 Store FORMAT_VERSION；Store层和Job-ready必须同候选。

## 既有测试潜在交接清单

TS精确路径：

- `tests/unit/contract.test.ts`
- `tests/unit/engine-connection-state.test.ts`
- `tests/unit/supervisor.test.ts`
- `tests/unit/task-progress.test.ts`
- `tests/unit/task-runtime.test.ts`
- `tests/unit/task-service.test.ts`
- `tests/unit/view-navigation.test.ts`

Python精确路径：

- `packages/engine/tests/test_contract_v2.py`
- `packages/engine/tests/test_coordinator_control.py`
- `packages/engine/tests/test_handshake_deadline.py`
- `packages/engine/tests/test_i04_lifecycle_boundaries.py`
- `packages/engine/tests/test_i04_progress.py`
- `packages/engine/tests/test_resident_runtime.py`
- `packages/engine/tests/test_runtime_bounds.py`
- `packages/engine/tests/test_session_page_limits.py`
- `packages/engine/tests/test_stdio_session_shutdown.py`
- `packages/engine/tests/test_storage.py`

新基础反例优先放T01专属 test_project_* / tests/unit/t01-*。现有文件只有当实际受接口升级影响时由原owner代改或逐路径交接，不能依据此列表自动获得整包测试所有权。

## 已核对的差异，避免错改

`test_i04_lifecycle_boundaries.py` 的同一用例既含hello请求2，也含成功握手后的业务请求2；未来前者保留bootstrap2并支持[3]，后者应随业务session3，不能一次搜索替换。其他resident/session/helpers同样逐用途分派。

`test_storage.py` 的包/资源探针实际启动hello并断言selectedVersion2，需要同版资源与包内验收设计；这个文件不只测试SQLite。旧格式0/1/2迁移和未来格式拒绝断言也需保留真实旧/新含义，不能为绿灯删除旧覆盖。

`tests/unit/contract.test.ts` 的protocolVersion2用于独立healthSchema；它未必等于新业务会话3。须由canonical owner明确health是否维持旧兼容，再决定是否改此处。不得因Project/业务3升级而无依据改变独立health行为。

旧固定5f reader拒绝DB3需使用真实固定旧代码/构建，不能用新Store常量改成3后继续冒称旧reader已测。当前未执行该矩阵。
