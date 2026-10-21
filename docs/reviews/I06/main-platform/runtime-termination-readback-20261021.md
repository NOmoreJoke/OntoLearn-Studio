# I06 原运行终态只读核验（2026-10-21）

观察时间：UTC 2026-10-21T01:19:47.227608+00:00—2026-10-21T01:23:07.699116+00:00。仅查询原句柄与原件并新增本文/md配套JSON；没有新测试、容器、GUI、构建、恢复或终止。

**三个原容器均仍可查且已退出，当前Running=false、State.Pid=0；原执行session均返回终态，未发现对应活跃宿主等待客户端。** 结论只覆盖下表原句柄，不覆盖其他任务或全部宿主/VM进程。

| 原运行        | container完整ID                                                    | 当前exit / FinishedAt(UTC)         | 原exec session终态 |
| ------------- | ------------------------------------------------------------------ | ---------------------------------- | ------------------ |
| aria1         | `469b6fae55437be19832cf5c4e471af8fe3abac7a015f8964fd34ebf8c97885c` | 1 / 2026-10-21T00:13:42.716048552Z | 96217 → 1          |
| aria2         | `0d3a9bb534db31ec2390739b5b4e14cff47b8108bee0a80e0b3af672d73b69b4` | 0 / 2026-10-21T00:40:08.175443377Z | 62110 → 0          |
| native-retry1 | `ecc6a6287606655422343400a08b4c86ace69bb463a6f92666f952966d4e70a1` | 0 / 2026-10-21T00:44:56.902532594Z | 5804 → 0           |

`docker top`对三者均返回“container ... is not running”（查询exit1，不是测试失败）；Docker inspect同时给出exited/Running=false/Pid0。空输入查询原96217/62110/5804会话，分别返回实际final exit1/0/0，非活动yield句柄。只读ps按这三个精确容器名和docker start/attach/wait/exec归属筛选，除去本次观察自身祖先，匹配0；没有清理或重启进程；也没有恢复、取消或重分类任何持久化fixture job行，不据容器退出断言全部数据库job行终态。

原日志中可直接读取历史Linux-container Electron main PIDs（例如aria2 source full的121/406/520，packaged full的1455/1737/1847；JSON列出每份日志）。它们不是宿主PID或当前存活证据。原I04 native observer未持久化main PID，未猜测或启动容器追溯；当前容器终态为独立直接证据。

## 原10门与唯一复验

| 原门                | 原test/helper exit | 结果                       | 原明文退出记录                                                                                                                                                                                            |
| ------------------- | ------------------ | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| source              | 0                  | 3 passed / 3 fixture skips | [source-exit.txt](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-aria2/evidence/results/regression/source-exit.txt)                           |
| source-aria         | 0                  | passed                     | [source-aria-exit.txt](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-aria2/evidence/results/regression/source-aria-exit.txt)                 |
| source-native       | 1                  | 1 failed / 0 skip          | [source-native-exit.txt](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-aria2/evidence/results/regression/source-native-exit.txt)             |
| source-reload       | 0                  | 1 passed / 0 skip          | [source-reload-exit.txt](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-aria2/evidence/results/regression/source-reload-exit.txt)             |
| source-disconnect   | 0                  | 1 passed / 0 skip          | [source-disconnect-exit.txt](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-aria2/evidence/results/regression/source-disconnect-exit.txt)     |
| packaged            | 0                  | 3 passed / 3 fixture skips | [packaged-exit.txt](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-aria2/evidence/results/regression/packaged-exit.txt)                       |
| packaged-aria       | 0                  | passed                     | [packaged-aria-exit.txt](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-aria2/evidence/results/regression/packaged-aria-exit.txt)             |
| packaged-native     | 0                  | 1 passed / 0 skip          | [packaged-native-exit.txt](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-aria2/evidence/results/regression/packaged-native-exit.txt)         |
| packaged-reload     | 0                  | 1 passed / 0 skip          | [packaged-reload-exit.txt](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-aria2/evidence/results/regression/packaged-reload-exit.txt)         |
| packaged-disconnect | 0                  | 1 passed / 0 skip          | [packaged-disconnect-exit.txt](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-aria2/evidence/results/regression/packaged-disconnect-exit.txt) |

唯一复验：[source-native-retry-exit.txt](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-native-retry1/evidence/results/regression/source-native-retry-exit.txt) = 0；原report为1passed/0skip，真实verified原件记录crashed+unresponsive、三窗、两次可见GTK提示、inspector关闭。容器inspect镜像身份与aria2同为 `sha256:948721a324bcfa8a219271f5b886830bf8c41ab6d4d0f209c55d1dc8581c0e9a`，inline原命令按冻结Config.Cmd保存。

**保持首次9过1失败＋唯一同镜像定向复验通过；不改写为一次10门全绿。** source/packaged基础全量各3pass/3默认fixture skips，六项fresh-fixture定向实际非skip执行；仅source native经过一次独立复验。

## 首失败与未产出项

- 旧9fc原e2e：source/packaged各1pass/3skip/2fail，新增status段落导致全局locator歧义；旧明文报告与原件索引保持。
- e2c aria1：source基础3pass/3skip、exit0；新增最小helper漏传strict `{}`，helper exit1；随后runtime空UVcache在offline editable build缺hatchling，wrapper/container exit1，余下门未运行。JSON明确标记缺失，不推断未运行门exit。
- e2c aria2 source-native：原exit1，真实hang原生提示未观察到，原test:446断言失败。首次只记录crashed/两窗及第二窗焦点；首次失败trace与明文log均保留。原代码每phase为`Date.now()+30000`（30秒），report总耗时约13.315秒，trace单调间隔约12.25秒；差异原因未知，不猜测时钟/环境或flake根因。
- 更早source/native驱动和package首失败仍在原`source-and-native-review.md`、`packaged-and-regression-review.md`及其冻结archive；本次没有重跑、修改或用新hash覆盖。

## 可直接读取的原件

- 主收口receipt：[aria-regression-receipt.json](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-aria2/evidence/aria-regression-receipt.json)。
- aria2完整日志目录：[regression](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-aria2/evidence/results/regression)；首source-native失败：[source-native.log](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-aria2/evidence/results/regression/source-native.log)。
- 唯一复验：[verified evidence](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-native-retry1/evidence/results/regression/source-native-retry-traces/i04-jobs-I04-native-render-1f7bc--dialog-retain-durable-jobs/i04-native-verified-evidence.json)、[report](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-native-retry1/evidence/results/regression/source-native-retry-playwright.json)。
- 三份原wrapper日志：[aria1](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-aria1/run.log)、[aria2](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-aria2/run.log)、[retry](/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-main-platform/tests/i06-main-platform/out/e2c269ad78a7-native-retry1/run.log)。
- 原archive仍为`f13d9a6f0cb06b39703a91bfd76e85266c87583c0123f5c31a92ee8ccb1afa34` / 154,270,058B，当前只读hash匹配；index `f29eecfe97648e650f5c896095f4a9695d64d101b873212e4408b5cb86356205`。所有原路径/hash与当前inspect选定字段在配套JSON。

## 判读与政策边界

aria2 wrapper/container/session exit0仅说明顺序采集脚本结束，不是全部测试通过；原source-native退出记录仍是1。aria2与retry的generic S3 binding.result=failed是未执行其专用probe/receiver/leak-scan的非适用门，不当回归测试结果，也不宣称完整S3通过。948721a3仅称Docker inspect镜像身份，不称独立config blob证明。

最新共同指南全文实读/核SHA `b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39`；根保护AGENTS `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`生效。本worktree仍保留旧db1快照 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，未修改/stage；冻结输入原样。T01已交八文件/Python四/storage与T03构建四均停止未来编辑，本次不消费其未批实现、不做产品检查、不重开Goal/计算/外审。当前handoff正文实际hash为`eea3eefe86555d585236f603b2ebb01ecac49c1350193c6d83c262b6209f1030`（不冒称仍等于早先通知add988）。

本次提交仅新增这两个只读观察文档；没有修改旧receipt、脚本、测试、archive或既有结论。
