# T03 四产品独立审查限定 delta：830cdd

结论：**F2 / P2 在 `830cdd1d198bf549b563925a3a47f7f9444710bd` 关闭。** 结合保留的 32d943 四路径全文首审，当前四产品实现范围内未发现其他必须修正的合同矛盾。这个结论限于静态实现与私有合成单元/定向 mock；实际 PyInstaller/PYZ、observer 集成、真实 native、root 执行前冻结批准及 semantic parity 继续待证，均未获本报告签收。

## 身份与本次增量

基线为 `32d9434d78abda25f7b6f8693725de83200e887e`。产品修订固定在 `830cdd1d198bf549b563925a3a47f7f9444710bd`；后续证据文档固定于主控报告的 `8363c29c`。合同仍是 36587 B / SHA-256 `9d97a6a233b47abc23064a9a8f8330080d62f39b3db981de14a148880e202a04`，本次未改变合同。

| 产品                                                                | 新身份 bytes / lines | SHA-256                                                            |
| ------------------------------------------------------------------- | -------------------- | ------------------------------------------------------------------ |
| `scripts/build-engine.mjs`                                          | 8437 / 252，未改     | `738f55ef056c3326f812ab9e4ed272a11a332a21a23a78c72fd07b510d31a8ff` |
| `packages/engine/entrypoint.py`                                     | 976 / 30，未改       | `aaf9f85b59f115ae0646fd31f5305ee588c2bd58a0fbb28d9714c707c9035ef3` |
| `packages/engine/src/ontolearn_engine/semantic_build_provenance.py` | 46602 / 1259         | `c96f0630b97c02049b9ee2f62f0b44946962b14c0a2ab5c9094eaaa3fa3b7b0c` |
| `packages/engine/tests/test_semantic_build_provenance.py`           | 44315 / 1214         | `0def6d7da0bdc2353c6f524fe8d86d40ab18936b58d58d1cc06bae713f7a3ec8` |

以上字节身份均由本 agent 对 `git show 830cdd:<path>` 独立计算。产品 delta 仅 reader 的 8 行局部差异及测试新增 44 行；同提交另有两份候选身份/原始日志空白补注文档，不属于产品行为修改。未重写任何首审或旧证据。

## F2 修订与独立反例复验

`_dist_inventory` 现在先识别 `.py`，用 `CODE_CAP` 调用一次 `_read`，同一 raw 同时生成 bytes、SHA-256 与 `_compiled(raw)` 的代码指纹；非 `.py` 保留原 FILE_CAP。原来的 `_identity` 默认宽上限与第二次源码读取均已从该 `.py` 路径消除。没有扩大 API、schema、错误码、native 等价域或 root approval 权限。

本 agent 对冻结 830cdd reader 重做首审反例：临时 fake html5rdf distribution；对超限 `.py` 记录首次 read 的 cap；对正常 `.py` 在第一次读取返回后替换临时文件，再检查成功 row。没有运行 prepare/finalize、PyInstaller 或目标 package 导入。实际输出如下：

```json
{"case":"source-cap","reads":[{"cap":2097152,"returnedBytes":null}],"rejection":"BUILD_PROVENANCE_LIMIT_EXCEEDED"}
{"case":"same-source-code","reads":[{"cap":2097152,"returnedBytes":10}],"sourceHashIsOld":true,"codeHashIsOld":true,"codeHashIsNew":false}
```

这分别证明首次读取即采用 2 MiB 上限且未返回超限字节；成功记录只有一次源码读取，source SHA 与代码指纹来自同一原始快照。即使临时文件随后变为另一份内容，该 row 也不会混合新旧身份。后续真正构建仍由 PYZ 与外部完整目录绑定检查实际产物；这里没有提出动态 filesystem 对任意并发攻击的额外安全能力。

新增参数化测试的两条分支与该错误直接对应，既断言 cap/读取次数，也断言同一原始 bytes/SHA/codeSha。已审主控原件：20 轮在旧 reader 上实际 2 failed / 96 deselected in 0.38s；修复后 23 轮为 98 passed in 1.94s、stderr 空、exit0；21 Ruff 和 22 format check 为 exit0。首次失败与修复后成功未混用候选，也未把首候选的 96 项改称 98 项。本 agent 没有重复运行 98 项或全仓 pytest，而是独立运行上述两条直接 mock 反例。

## 原始证据和恢复件

独立校验 `reader-snapshot-fix/manifest.json` 的 11 个文件，bytes/SHA 全部相符。已读其 commands.json 两条实际命令的 argv、exit、时间，以及修改说明、产品身份和测试输出。首次归档发生 stdin 编码 SyntaxError、未写目标目录的事实有主控补注；这属于归档失败历史，不影响已有实际回归结果，不能把后补证据目录冒称当时已成功备份。

按主控要求，本目录额外保留本 agent 自己的三次 mock 输入和输出恢复件：

- `00-initial-alias-miss.py.raw` / `.stdout.raw`：首次观察器比较未 resolve target，macOS `/var` 别名导致没有命中；reads 为空，这一轮不作为 F2 正向复现。
- `01-32d943-confirmation.py.raw` / `.stdout.raw`：resolve 临时根，明确从 git show 固定旧 reader，复现 128 MiB 首读及 source/code 混合身份。
- `02-830cdd-confirmation.py.raw` / `.stdout.raw`：固定修后 reader，确认 2 MiB 首读与单快照。

这些文件都是从本 agent 自己的 tool-call input / tool output **恢复的新文件**，不是原来就存在的脚本或原始磁盘 stdout 备份；没有回填时间或伪造执行。`recovery.json` 对应各次 tool output chunk、解释器 argv、cwd、exit 和局限。复制脚本仅额外做静态 compile，没有在恢复步骤补跑生成“原始”结果；未分离取得历史 stderr，因此没有造一个历史空 stderr 文件。旧 00 脚本按当时工作区 reader 加载，若要重现该历史状态须使用 32d943，不能对当前修后文件执行并冒充旧结果。

## 检查范围与保留限制

32d943→830cdd 整个增量 `git diff --check` 为 exit0；合同基线 2fdd853→830cdd 的四产品 `diff --check` 为 exit0。首候选完整提交因保留 12 轮原始 pytest stdout 尾空白而为 exit2 的事实仍在首完整报告，本次只证明增量和四产品路径干净，没有把旧 raw 空白“修掉”或据此声称整个历史证据提交无空白错误。

此前 F1/P3 已由 root guard 关闭；reader 显式 hidden-import 已加入，实际 PYZ 可达性继续等待真实 finalize。F2 此次关闭后，首审中关于 strict schema、code normalization、immutable evidence、无主动 target import、native/source hash 分域、完整外部 binding 与 fixed FLAG/selector 的静态结论适用于新候选未变路径。

未运行真实 prepare/PyInstaller、engine/semantic/full-v1、full pytest、GUI、native 或 parity；未触碰 STOP native-location-N0-build；未修改 I05 独占 probe/tests、产品源码或永久测试。reader 的 post-observer API 不能单独证明 I05 实际按正确顺序安装 observer。root 仍须在实际执行前冻结并独立批准 expected binding SHA 与实际完整 engine 目录；build proposal 的 rootApproved=false 和 reader 的 unknown 均保持原义。
