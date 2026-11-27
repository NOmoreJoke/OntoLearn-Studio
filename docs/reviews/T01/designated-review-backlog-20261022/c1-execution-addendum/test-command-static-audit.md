# C1 命令及测试静态审计

结论：原 C1 的普通 `npm run check`、128 专属功能用例与真实临时事务反例均可由另行执行作者在本树独立环境运行。root 已明确原 check 包含未改 I04 libproc/resident_bytes/worker guard 及其传递调用，不人工排除，不修改 guard 求绿。未改 I01 固定负载 measure 也按原普通 check 范围保留。已拒 C2/S1 SQLite/heap/OS 物理接口研究、HOLD 与新 caller/producer/native 票继续禁止。

两个审查树均实核 HEAD `c0b61fd245c1b3bd2a84e488f00a742a1942fd8c`、detached；初核clean，末核仅 `M AGENTS.md`（外部同步保护规则，本审未改）。固定产品 `423b7e4c799f188cf2ce6e8e7121893ce85624cd`，批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，adoption `ba2c6c293f9fd9e1742c9ab352dae5e3c951f6a4`，过程 `a33cc80e82475e54d74b4e48c1fd32f32979983a`。423b 后 packages/apps/tests/scripts/配置锁无产品差异。

静态遍历 34 个 pytest 测试模块、1 个支持模块、402 个 test 函数定义和22个Vitest文件。Python每个函数/夹具/decorator/import/调用及可解析嵌入子程序、TS测试/子进程入口与逐文件 SHA 均在JSON。C1 专属777行全文读取，24函数参数静态展开128；未collect确认运行数。

本审没有运行测试/collect、import产品、DB/SQL、产品或测试子进程、GUI/native/安装依赖；未改源码/配置/锁/Git。仅使用Git、rg、文件读取、stdlib AST/JSON/hash并写本/tmp两件。

## 原授权与验收

原授权：`/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/T01-project-create-core-C1-implementation-authorization.md`。仅五writer（project_lifecycle.py、storage.py、job_store.py、project/format3.py、test_project_create_contract.py），完整交付52项、47只读。原文明确可信临时Store3/JobStore3、写边界异常/SQLite失败/自有子进程退出重开、全部预算/旧hash/旧reader拒新namespace/损坏逻辑原件零修复，要求受影响新旧专项、完整check、verify:sources及固定候选独审。

正式 create/resolution/位置权限/首IO/公开wire/I06/真人OS/父FR/CI/指定双审/合并仍是独立门。历史validation记128专项、1125TS/2969Python/44skip、source12及实际工具exit；本轮仅读文档，无新运行Pass。原“无native”总结不能解释为旧check无OS调用；本静态清单把既有调用与新native票区分。

## 可执行计划（交执行作者；本审未执行）

```sh
.venv/bin/pytest packages/engine/tests/test_project_create_contract.py -q
UV_CACHE_DIR=<this_review_owned_cache>/uv npm run check
npm run verify:sources
```

每个命令独立保留argv/cwd/真实终态exit/stdout/stderr/首失败和自有进程收尾。不得以随后Python成功盖掉npm失败。保持原suite，不加按native/RSS/SQLite字符串的deselect；不替换guard。Node24/Python3.12/锁定依赖由独立环境作者准备；uv frozen可能同步，Node helper有硬编码.venv/bin/python。清除外国树ROOT_SOURCE_PATH/ONTOLEARN_TEST_ENGINE与外部pytest注入，不借环境/可变DB。

## 具体允许入口及功能边界

- **C1 target 128**：C1 authorization lines 11-19 five writers and lines 37-43 genuine temporary transactions; exact line map in controlRefs；test_project_create_contract.py:45 fixture creates only tmp_path/create.sqlite; 214 child exit fixture only tmp_path/exit.sqlite；CHILD 197-210 hooks os._exit(77), timeout20; no Coordinator/worker/native guard；696-777 old reader reads four fixed a816 Git blobs with git show and starts owned Python against same temporary test DB；`.venv/bin/pytest packages/engine/tests/test_project_create_contract.py -q`
- **lint/format/typecheck/build**：root package scripts do not route build through engine:build/test:e2e；desktop build is electron-vite build; static compilation, no Electron launch；format:check uses --check; do not use format --write
- **ruff**：
- **source archive hashes**：verify-sources.mjs only readFileSync+SHA256 over12-manifest entries, no DB/child/network；`npm run verify:sources`
- **ordinary temporary Store/JobStore tests**：SQLite itself and lease locking are required by C1 original transaction acceptance, not physical-interface research；authorizer fault denial, fixed fixture corruption via SQL/trigger removal, migration/reopen, PRAGMA max_page_count for actual SQLITE_FULL are functional bounded temp fixtures; no blanket sqlite ban；ordinary git/Node/Python runner children do not imply sensitive producer/worker authorization
- **misleading native names are test doubles**：tests/unit/native-driver.test.ts:3-5 mocks spawn, 21/50/64 supplied EventEmitters; WebSocket stub; never launches Electron；test_memory_guard_exit.py:30 _darwin_library replaced with Python SimpleNamespace(proc_pidinfo=read); os._exit replaced; no actual libproc；test_worker_owner_bootstrap.py kernel fixture51 patches ctypes.WinDLL with Kernel double; fake handles only. Darwin invalid owner tests196 reject before worker._execute/install_memory_guard; Windows actual owner case must remain OS-specific pending if Windows execution proposed.
- **formal ChangeSet stdio regression**：test_project_changeset_stdio.py:1-5 explicitly no test worker; Session96+ONTOLEARN_TEST_MODE0; changeset.commit routed to Coordinator.execute_changeset at551-554, bypasses native worker branch；tests/unit/t01-changeset-runtime.test.ts:135 business3 supervisor and changeset.commit; owned temp db/Python helpers, no test.* worker guard

C1 child 214–244 是19个阶段的 tmp_path/exit.sqlite + os._exit(77)，timeout20；696–777 是4条 a816固定Git只读取源与临时旧reader Python，对同自有临时DB验证拒绝。fixture的SQL authorizer/trigger与坏claim/receipt是逻辑事务边界，不是raw畸形Btree实验。

## 已定位且保留的旧 guard/测量回归

以下全部属于原未改 suite，root 已明确允许正常check；列出是为揭示真实执行效果，不作为排除清单。旧数据仅证明自己的回归断言，不证明新 whole-H/SQLite损坏保护。

### I01 heap/RSS固定负载

- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_storage.py:383`：test_fixed_rdflib_query_and_two_independent_scales calls storage_probe.measure(1),measure(10); actual tracemalloc and getrusage measurement, allowed unchanged I01 baseline measurement in ordinary check; never a new physical bound proof.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_storage.py:867`：test_missing_unix_probe_module_cannot_break_health_or_measurement[resource] embeds measure(1); only resource parameter does measurement. [ontolearn_engine.storage_probe] is ordinary health-import failure regression and can remain.

### I04直接guard

- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_i04_lifecycle_boundaries.py:211`：test_actual_memory_guard_supports_normal_worker_and_denies_known_oversize: install_memory_guard in owned Python; actual platform adapter
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_i04_lifecycle_boundaries.py:236`：test_darwin_guard_observes_real_rss_growth_and_stops_only_that_process: actual libproc RSS and touched 32MiB allocation
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_i04_lifecycle_boundaries.py:262`：test_memory_failure_isolated_from_other_project_real_worker: allocateBytes=1GiB request to actual guard, two workers
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_i04_lifecycle_boundaries.py:296`：test_parent_rss_monitor_unavailable_fails_only_the_target_real_worker: actual worker plus native_rss for other PID
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_i04_lifecycle_boundaries.py:344`：test_actual_memory_worker_exit_precedes_asyncio_returncode_delivery: allocation worker/native_rss loop/real errno race

### I04 worker传递guard

- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_i04_lifecycle_boundaries.py:92`：test_actual_worker_has_no_inherited_credentials_or_coordinator_authority: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_i04_lifecycle_boundaries.py:123`：test_complete_waiting_for_worker_exit_cannot_extend_total: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_i04_lifecycle_boundaries.py:144`：test_cancel_while_worker_exit_waits_remains_cancelled: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_i04_lifecycle_boundaries.py:167`：test_round_after_complete_in_same_chunk_never_commits: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_i04_lifecycle_boundaries.py:189`：test_unread_worker_stdin_is_bounded_and_cancellable: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_i04_lifecycle_boundaries.py:391`：test_busy_worker_still_allows_heartbeat_and_cancel: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_i04_progress.py:106`：test_real_worker_phases_share_sequence_and_do_not_increment_durable_version: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_i04_progress.py:153`：test_real_worker_failure_removes_phase_cache_and_never_publishes_terminal_progress: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_i04_progress.py:178`：test_raw_stdio_late_subscription_cancel_and_other_job_remain_isolated: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_resident_runtime.py:267`：test_busy_worker_cancel_ping_and_other_worker_crash_isolation: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_resident_runtime.py:290`：test_real_rounds_summary_stable_paging_and_no_formal_changes: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_resident_runtime.py:376`：test_real_atomic_completion_cancel_does_not_rewrite_commit: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_resident_runtime.py:408`：test_real_worker_summary_corruption_is_safe_at_runtime_read_boundary: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_resident_runtime.py:454`：test_coordinator_kill_reconciles_partial_round_without_replay: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_resident_runtime.py:487`：test_real_round_cancel_preserves_exact_last_committed_boundary: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_stdio_session_shutdown.py:155`：test_actual_request_budget_closes_cleanly_and_new_session_preserves_committed_history: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_project_startup_stdio.py:247`：test_real_job_receipt_retry_and_restart_bindings: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/packages/engine/tests/test_worker_parent.py:42`：test_worker_exits_after_its_actual_coordinator_is_killed: pre-existing functional worker regression; Coordinator.execute can use resident_bytes on Darwin. Not equivalent to rejected C2/S1 physical-interface research. Allowed by explicit root interpretation of ordinary check ticket; do not deselect.

### Vitest实际worker

- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/tests/unit/task-runtime.test.ts:530`：All 8 test functions in this file invoke runtime/disconnectRuntime with test.read/test.rounds/test.atomic; each real coordinator starts actual worker guard. Allowed ordinary regression ticket; preserve all tests.
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-c1-zcode-review-423b7e4/tests/unit/t01-startup-supervisor.test.ts:459`：Only test titled runs a real3 atomic Job through TaskService events, immutable results and one receipt across restart starts test.atomic worker; all Node protocol/Python startup tests and this existing guard regression remain in normal check scope.

`test_memory_guard_exit.py` 替换 `_darwin_library` 与 `_exit`；`test_worker_owner_bootstrap.py` kernel fixture替换WinDLL；`tests/unit/native-driver.test.ts`mock spawn/WebSocket。它们也允许，不能凭文件名误当真实原生验收。Darwin invalid-owner worker在memory guard之前拒绝；若另跑Windows，真实owner分支应如实记录为该既有回归的OS运行效果。

## 明确排除的工作与命令

- **rejected SQLite/heap/OS physical research and common-physical HOLD**：SHACL-date-and-SQLite-user-decisions-20261022.md:7-11: keep malformed-input protection/HOLD; rejected SQLite/heap resource-interface analysis remains stopped. New C1 test ticket does not authorize B/C/native/provider/owner interfaces or restart research.
- **Electron/native/e2e/HMR/dev/package**：Original C1 authorization final paragraph expressly excludes GUI/Electron/e2e/native/HMR/Keychain/model/user-location IO; test:e2e installs Electron and runs real Electron; package:dir invokes PyInstaller+electron-builder; verify-i01 invokes --storage-probe. None is in npm check chain. 命令：`npm run dev`, `npm run test:e2e`, `npm run engine:build`, `npm run package:dir`, `python scripts/verify-i01.py ...`, `python scripts/verify-i04-package.py ...`, `python scripts/prepare-i04-fixture.py ...`, `python -m ontolearn_engine.storage_probe ...`
- **new/custom evidence producer plugin**：scripts/i04_matrix_evidence.py:221+ explicit plugin only, not root pytest config. It adds DB snapshots/metadata recorder; plain pytest does not load it. No new custom runtime ledger/producer supplied by this audit. 命令：`pytest -p scripts.i04_matrix_evidence ...`

固定 C1 树没有 C2 operation_evidence.py/test 或 S1 ontology_projection.py/test，不会因完整check自动恢复这两线。普通生成固定测试数据、正常Store事务/迁移/重开、既有lease锁和测试worker只在原suite fixture范围；不访问真实项目/新位置，不外延成新N0、生产producer、权限或物理资源接口。

## 尚未运行验证的事项

- No dependencies/environment installed or runtime versions/provenance tested here. uv run --frozen alone can sync missing env; Node unit helpers use .venv/bin/python or uv, so environment author must provide exact own compatible runtime.
- No pytest collect was performed. Static test definition/parameter enumeration is not runtime collection or a pass. External/site plugins are outside this source inventory; executor must isolate plugin autoload/PYTEST_ADDOPTS.
- Original check record has22 Vitest files1125TS and3013collected Python/2969passed44skip. New counts, failures/skips and elapsed times require actual execution; do not prefill historical numbers.

本审不替代指定模型实际设置/task/session/turn、真实执行与独立审查结果。完整JSON：`/tmp/t01-c1-execution-prep-20261022/test-command-static-audit.json`。
