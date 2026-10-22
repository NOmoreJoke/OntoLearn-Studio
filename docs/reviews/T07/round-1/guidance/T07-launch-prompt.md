# T07 沙盘：独立开发启动

全文读取 developer-common-instructions.md、plan.md/tasks.json中本项、requirements.csv/acceptance-baselines.csv、decisions.md及原PRD FR-700–705、附录E.2–E.5/G.4/G.6及D、第11–12节全文。唯一功能为T07，对应父功能所有P0与跨模块验收保留；不以纯模块或页面完成关闭父功能。

工作树 /Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-scenario；分支 feature/weekly-t07-scenario；base 5f910b52c69d86a1076b2032e5d3c63e715947f3。总控已独立创建，先实查身份/分支/base/状态/指南SHA，建立本功能Goal及docs/reviews/T07/status.md，保留保护AGENTS未暂存。

独占新增路径：`packages/engine/src/ontolearn_engine/scenario/`、`packages/engine/tests/test_scenario_*.py`、`apps/desktop/src/renderer/src/scenario/`、`tests/unit/t07-*.test.ts`、`tests/fixtures/scenario/`、`docs/reviews/T07/`、`docs/iterations/T07/`。先核对无冲突；没有列出的现存共享文件不得改。storage.py后续owner为T01，其他Python/锁/CI仍I05，14共享contracts/main/preload/App仍I06，任何具体新需要先向总控精确交接。不能创建第二公共契约/可变权威/网关来规避。

实现固定轮次状态机/资源阶段/指标/比较/运行详情纯服务与页面，严格事件→真实行为前推理→冻结行为/冲突→资源→真实轮末推理/指标→单轮commit边界。现可实现轮次控制/有界取消/消费/稳定ID/资源FIFO/完整E5预期反例，T06行为和T05推理均等实际批准接口，不复制未批实现或用给定推理结果宣称真闭环。E5四轮每轮4事件/产能3和4，全部W001–W016创建/完成/积压/队列/指标/重放集合与原文对齐；T09公共fixed manifest后只读消费，本线专属测试fixture可先建不争写。达到max轮保留未处理事件、未提交取消零效果、历史轮保留、V1晚到不当V2、独立重放重置消费/显式续跑沿用消费。正式data不受场景修改，实际轮次写入T01/I04，最终跨设备重放T10另联验。

现在就实质实施可独立验证的服务、错误与边界、完整样例和必要测试/独立agent内审，形成可恢复本地提交；不只写计划，不全量等待M0。真实依赖缺口按具体接口/路径提出；总控会协调基础格式/公共接线的单一候选，避免整模块循环。正式集成只消费实际批准基线，最终同候选更新实际develop并必要联验，指定ZCode GLM-5.3/最高与MiniMax M3.1-Flash/xhigh各新完整任务实际通过/读回/逐项处理后才push/PR/实际CI/正常合并/远端核验。当前外审资源I05预约，不自行操作应用。开发与最终父功能均继续本聊天。

本机只跑无窗口CLI/unit/Python/build/unsigned目录包，不开Electron/e2e/native/HMR/凭据提示，不读取或输出secret、不新增付费或对外联系。按实际改动跑AGENTS要求，首失败保留；未执行的包内/真实运行/生产只记待验。状态/原件只写本线目录，不改root tasks/state。及时向总控回执真实owner/文件责任/命令/下一交付及共享缺口。
