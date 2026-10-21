# 格式 3 八文件：正式生效接收回执

2026-10-21。已实际接收总控正式生效通知，并全文读取权威 `iteration-control/2026-10-21-weekly-release/I06-T01-format3-ownership-handoff.md`，SHA-256 `add9884ab9a0cda3a8a562f26a3b7c515255919d65eb0487d6c254681ed4991d`。原 I06 释放、T01 逐路径/双基线接受、独立复核及总控登记均已完成；八文件未来唯一维护现为原 T01。

精确范围仍是原 [八文件机读回执](../../iterations/I06/format3-maintenance-handoff.json) 的 canonical7 与 `apps/desktop/src/main/engine.ts`。本线再次逐项核对：八文件均 clean，实体 SHA 与冻结回执相符；产品内容仍与 `e2c269ad78a78e1a042cadc93b1c81a874707153` 一致。本次未修改产品、测试或 AGENTS，未重跑产品检查。

I06 继续停止这八文件的未来逻辑修改；确需修改时先由总控逐文件返还。其余六文件（main/index、task-service、preload/index、renderer/env.d.ts、App.tsx、style.css）仍归 I06。既有 tests、CSP/window、构建锁/CI 不随之交出；T01 已获专属 `tests/unit/t01-*.test.ts` 与 `test_project_*` 新增范围，未扩大为既有测试写权。T03 构建四文件和 T01 Python 四文件的生效交接分别保留。

T01 仅从批准 `5f910b52` 实施，不复制未批 I06 gateway/I05 semantic；原 I06 字节与证据仍可读取/构建。后续实际采用已合并格式3时，按真实 develop 与当时唯一 owner 协调，保留 main-only 模型方法不发 Engine 的 guard 及严格绑定，不机械覆盖任何一方文件。

默认2/显式内部3隔离、精确 DDL/API/完整同源 JSON/真实 registryHash/receipt/退出分类先冻结并独立审计的要求保留。本次生效不代表格式3 ready、runtime 能力或父模块验收通过；原整候选联验、指定双审、PR/实际 CI/正常合并/远端核验仍待实际完成。

原 offer、独立审查和 wire 提案的 hash/字节不改；其中“待登记/接收”为生成时状态，当前责任以本回执及总控权威协议为准。
