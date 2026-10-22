# 四路径普通命令 runner 定点复核 r2

结论：首审 P2-R01 在本次静态代码层关闭，未见新增必须阻断本票准备的 P1/P2；精确七命令 plan 与票内范围、依赖和 operational deadline 一致。没有执行 runner、payload、子进程、格式化、检查、测试或产品。此结论不替代未来 actual env/freeze 的生成和核符，不是 runtime 已完成或运行授权升级。

## 固定输入

- 授权：6465B/SHA-256 `73b70587ff0a1301ab9ecba6ccf56ccd3fc96c4b452650175d2c6ed5b49d2612`，沿本轮已全文读取精确四路径 START 票。
- 最终 runner `outputs/20261023_I06_C01_service_repair/run-command.py`：7021B，SHA-256 `de1c939e110e923bf9e0363229879af827b7d665d0878c9c83fdd83039e020f2`。
- 最终 `runtime-plan.json`：6079B，SHA-256 `c544aad84b1f4cb939c8c60e42025ba17bf469fd7425d86134707e7142f499c4`。
- 首审 `runner-static-review.md`：3633B，SHA-256 `354b08159eb23dfd494979af42c60328f28fe0145af46b3bcb8432fc2df51f02`，原文未改。
- 四路径非作者报告 `independent-four-path-review.md`：8909B，SHA-256 `979f3409d0a76c8534352207f4d519e0abf50811b92024a56f205dbdd504afe4`。本报告没有重审或改写该四路径实现。

## 首审问题的实际修正

runner:95–136 逐段静态回读：

1. capture异常后的 poll/terminate/wait 自身被独立try捕获，不能因该cleanup异常跳过后处理；只操作原 Popen 对象。poll得到真实退出码先存 `exit_code`，仅仍为None才terminate/wait，保留已取得的child终态。
2. after-read异常生成显式UNKNOWN对象、captureErrors，runtimeHEADAfter用get回退UNKNOWN；sourceUnchanged必为false。after-write异常另记录，不冒称文件已确认。
3. 两流digest分别捕获；缺预期流也记captureErrors。任何post-child捕获错误都会使launchOrCaptureError非空，因此即使child=0也不能wrapper0。
4. terminal receipt以独占写尝试；写失败保留可能partial原件、不覆盖，追加错误并通过stdout给fallback，wrapper非0。磁盘和stdout同时不可写不可能保证持久回执，本实现没有承诺此物理保证；后继须把缺正式receipt当失败/未知，不能用child0替代。
5. 未修改原claim重用规则、等待预算、Popen argv或清理对象；没有新增命令重试、进程发现、组信号、foreignkill、native探针或全局drain承诺。

首审后定点回读曾指出“poll已结束但未回填exit_code”和“缺流只记NOT_CREATED仍可能绿”两处尾项；上述最终代码已分别处理。此为纯静态修正核对，没有实施真实异常注入，没有把建议当实际运行验证。

## 精确命令链

所有cwd固定新树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-C01-service-repair-20261023`。

| 顺序 | command id / argv要点 | wallMs | dependsOn | freeze |
|---|---|---:|---|---|
| 1 | format-check-four：own prettier --check，只四授权路径 | 120000 | 无 | false |
| 2 | lint-four：own eslint四路径 --max-warnings 0 | 120000 | format-check-four | false |
| 3 | target-mf02：own vitest run 新MF02测试文件 | 300000 | lint-four | true |
| 4 | target-zn2：own vitest run i06-gateway.test.ts | 300000 | target-mf02 | true |
| 5 | target-zn3：own vitest run i06-stored-result.test.ts | 300000 | target-zn2 | true |
| 6 | ordinary-check：/usr/local/bin/npm run check | 600000 | target-zn3 | true |
| 7 | verify-sources：/usr/local/bin/npm run verify:sources | 120000 | ordinary-check | true |

依赖必须已有正式receipt，且exitCode=0、launchOrCaptureError=null、sourceUnchanged=true；任一失败不能放行下一命令。每项独占claim保留，不能重复“attempt-001”绕过首失败。formatter是check而非write；plan没有allowsFormattingOnly豁免，没有授权自动修源码求绿。三target是三份完整既有unit文件，不是额外e2e/package/native矩阵。

## 环境、源冻结和运行边界

plan环境完整枚举为独立own HOME、TMPDIR、XDG/cache/config、npm offline/ignore-scripts、UV_NO_SYNC/OFFLINE=1/下载never/keyringdisabled、own .venv/PYTHONPATH。PATH前两项是own node_modules/.bin和.venv/bin，之后.local/bin，再系统工具路径；无I06 addon gate、HMR、ROOT_SOURCE_PATH、真实provider/key或用户session变量。Popen使用该env dict替换继承环境，stdin=DEVNULL、stdout/stderr各独占文件。它不是对全OS网络或后代的物理隔离承诺。

source_vector读取947 before路径+新增MF02测试及runtime Git HEAD；target/check/verify执行前要求与source-freeze.sourceVector精确相等，并逐条核independentReviews bytes/SHA。可行的冻结流程是：先保留两项四路径静态检查结果，在所有必要产品修正和非作者delta审查闭合后，由主线生成实际freeze；其中必须列出正确的四路径独审报告及pin，而不能空列表/错报告冒称已核。本runner按列表逐项核符，**尚未存在的freeze内容不能由本报告替其确认**。

此次读取时 `runtime-environment.json`、`source-freeze.json`尚未创建；一次只读元数据脚本因前者不存在返回FileNotFoundError，未运行runner或目标命令。runner在读取env/required freeze失败时会在Popen之前拒绝；因此准备态尚缺文件不是已经发生的目标失败，也不能标成已run-ready。实际生成后，主线仍须按原票核env与plan一致、freeze含本轮正确源向量/独审pin，不能沿用旧版本输入。无需为静态收口新增异常注入票。

超时仍只对保留child handle做terminate/kill并有界wait；child descendants未独立发现，不能据leader退出签全部drain。Popen构造、文件/Git同步读取等没有syscall级硬时限；原票operational deadline不包含新物理保证，本轮未增设后者门。

本报告只新增本r2原文，首审及作者runner/plan均未改。报告冻结后停止写入；后续真实结果另按原票保存firstfailure、actual child exit与wrapper/capture层级。
