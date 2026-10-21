# 唯一第二次 Darwin/core 构建结果独立审查

2026-10-22。结论：未发现阻断本轮成功构建归档的新增问题。证据支持固定输入 b65751963a8c1f0c35e6ef680e816a99c4026e24 的唯一第二次 driver 构建退出 0、13 条计划命令均 status 0、两产物存在且静态身份吻合。接受状态仅为 **built-unverified / tests NOT_RUN**；不是 N0、目标 OS、运行行为、Node addon 或生产闭包通过。原 source fixture 的普通 rename 覆盖风险已交 I06，仍是后续执行前的源夹具阻塞，本轮不采用修复、不第三次构建或执行产物。

## 实际构建与证据固定

只读 Git HEAD 与 driver 命令 1 的归档 stdout 均为 b65751963a8c1f0c35e6ef680e816a99c4026e24。`input-closure-manifest.json` 为 4757B／SHA-256 `c392e900d3804e6678ee20e014dd8a83c822ae9d41c0ec463fc047cb861e32f7`，保 228815f1f4f2bad005f21faffd8676c8713431c8 授权、5d7a 过程基线、22 项固定输入和 onlySecondAttemptAuthorized=true／artifactExecutionAuthorized=false。本轮不重做此前完整 12／42772 映射审查。

`build-once.result.json`（1149B／`fc70fac16fdd67bce49e537819d4a8466692c9954d9627c653f89cfb7ff20e4b`）记载一次真实 driver 调用、dispatchAttempted=true、driverExitCode=0、outerDispatchOutcome=returned，起止 UTC 18:52:15.599487 至 18:53:01.100463。这里使用真实 driver 退出码，未以包装工具退出码替代。stdout 的 complete-readonly 是最初 build-preflight 阶段；随后独立 built-unverified 输出及命令记录说明构建实际发生，不能把 preflight 的 processExecution=false 当整次运行无子进程。

最终 `driver-raw/supplier-log.0065.json`：21061B／`ac2bc783be0fc10eea24479e2feda1d7ed22c330950ae7ea0633c13980e67fe5`。13 个 index 0–12 均 completed，有 positive PID、run.status=0、signal/error=null、failures/cleanupErrors 空；firstFailure=null、persistenceFailures 空。0–10 为 Git 状态／HEAD／九源 blob；11 为 configure，12 仅构建 location_core_test 和 location_child_probe、parallel 2。未见第三次构建或产物执行命令。

11 stdout 明确记录 resource 9308 和 SDK 33464 的 metadata 映射及每个 physical pin 完成，然后 AppleClang 21.0.0.21000334 的 identification／ABI 检查、配置和生成完成；11 stderr 为 0B。12 stdout 记录四个 TU 的编译及两个目标的链接、Built target；12 stderr 为 0B。不能把这些输出量化为实测 I/O 或性能提升，也不以第二轮成功倒推首轮 ETIMEDOUT 的唯一原因或进程树已释放。

## 冻结产物与静态检查

本审仅对获准的两个产物读取一次静态字节并计算 SHA；共 378008B，低于 393KiB 限额，与 `artifact-pins.json` 的冻结身份完全一致：

| 产物 | bytes | SHA-256 |
| --- | ---: | --- |
| location_core_test | 343888 | ce1a3a365df426d4d57e8b5cade83b2b6e82e5cd438bcccc6e4c358af7ea203a |
| location_child_probe | 34120 | 3900ebc3f31a8def12d8f6bd4eedf866543d94e9412dd1d37706e68e0159c15e |

产物目录为 `build/native-location/n0/darwin-arm64/95ab1538f20fce33132dc179b738fec780d9e1b1d4eecc5061cb04fccddfd109/core/artifacts/`。两者是既有 file 输出所记 Mach-O arm64；已读 otool load-command 原文均为 platform 1、minos 15.0、sdk 27.0，导入 libc++.1.dylib、libSystem.B.dylib，loader 为 dyld、无 rpath。core 既有 symbol table 归档列出 11 个 `_nl_*` 外部符号。以上是构建／静态 load-command 证据，未证明 macOS 15 实机可运行或任何 addon ABI。

`artifact-static-summary.json`：4657B／`ae58989f15155271a99d30e19cbd9e571febdd03d6a133e53e8f1686e7d91ae7`；`artifact-pins.json`：1493B／`df852c673651f54e9facbc0069bde62e0e6b24aebf58a8d0041aa766b8a5dfef`。本审不重跑 file／otool／nm；只核原结果及双流。原两次成功 inspection 与 continuation 八次的实际 indices 合为 0–9、均 exit 0，20 个实际 stdout/stderr 输出名按大小写折叠后仍唯一。

原 inspection 第三项在 exclusive stdout open 时发生 FileExistsError：otool-L 与 otool-l 名称在该文件系统冲突。`inspection-output-open-failure.json`（738B／`53dcd61542bb2bae82211da90715a490192d1e00da8bbaa3a085c1254b8b5c0f`）及旧 results 保留错误；failedCommandActuallyDispatched=false。旧 attempted 只是 open 前的 wrapper 意图，不能算启动或一次失败的 otool 子进程。前两次未重跑，其余八项在独立语义文件名下完成。不能宣称所有过程操作均成功。

## compile／depfile／link 证据边界

四份已归档 depfile 的 bytes／SHA 与 used evidence 全部吻合；本审一次静态分词复得 1798 literal token。独审最初未经词法归一化的集合为 878，不能直接拿它否定归档 877 normalized 路径。已静态读 collector 的 normpath 与相对 source-b1c witness 规则；小型 `depfile-normalization-witness.json` 进一步明确唯一合并 pair：`src/../include/location_abi.h` 与 `tests/../include/location_abi.h` 均归到同一 include/location_abi.h。没有为此重新全量解析 source／sidecar 或再跑 collector。

`used-dependencies.json`：1426993B／`07f92387c78b99a7c9f8ddb359bcaa9573c91e38a9bc6aa6c811d415d6f43be9`。875 条 direct witness 是 collector 对既有 resource／SDK／九源 pin 的词法绑定结果，本审读取该归档，未重新读取 42772 原清单独立再证每个 source index。剩余两个 literal 恰与 catalog receipt 的 pthread.h、sched.h alias 集合相等；alias realpath、常规目标 bytes／SHA 与 receipt 中 approvedRegularRecord 内部一致，原 fb40 part/ref/byteOffset 及 sidecar witness 位置有记载。`sdk-alias-catalog-bindings.json`：7811B／`3ef23e895b84449cf1b5007fff00856da6e9f15c0341f11e1c5829c751158453`。本审未重读旧大清单或当前物理 alias；因此 875 direct + 2 catalog 表示既有清单来源覆盖，不冒称独立观测全部实际 compiler open 或当前 symlink 状态。

四条 compile command 与已保存 compile_commands.json 原文逐项一致，两条 link-driver command 与已保存 link.txt 原文一致；均仅 Darwin core TU，arm64、C++17、SDK27、min15，无 Node 定义。`compile-and-link-evidence.json`：14014B／`4b405583464553d9783665bd9e59bf7f80a90bafcf1096fe449a3fff884b2f35`。显式四个 object 输入的 pin 在归档中保留，本审未重 hash 这些对象。CMake compiler-probe 的 implicit libraries/directories 不等于最终 linker 选中跟踪；最终 stub／archive／member、嵌入第三方、运行时与目标 OS 闭包继续 PENDING。不能据 depfile、nm undefined 或 artifact imports 关闭它们。

collector 执行回执明确是从原工具结果事后记录的 exit 0，未虚构 wall clock、未重跑。本审仅读 receipt 与脚本静态逻辑，不把它变成新的原始结构化 subprocess 结果。

## 账、原件与本审限制

已读 delivery-summary、read-account、outcome-closure-plan、index 和现有 generated／driver／external 清单；本审没有重复 owner 的最终全 Git 索引字节闭包。`read-account.json` 当时读取为 1836B／`568c6fb0d442c06d35b0ba81ef2439a319fbe66bb099e3524de6c7e4a83a4d65`，声明构建阶段含两个 64MiB 预留后 37178693256B，距 40GiB 尚 5770979704B；实体保守171088，metadata含关闭预留1053668，小于1100000。旧供应阶段9745727085B独立保留；实际 OS／compiler／loader I/O 均未知。当前账不是实际全 IO 测量。

本审主记录为两次 877 依赖对象读取与一次 1798 depfile token，共3552；按宽口径加过程 manifest 对象297、命令39、inspection33、compile12、alias6、whitespace62，已知4001；小 receipt/top 对象保守49，总4050。原4000预留不足事实保留，不能宣称始终满足。owner 已在协调消息明确从自身6000关闭预留转50给独审：独审4050、owner5950，总1053668不增，并将保初始值与 adjustment；本报告不倒写此前小账。本审应用读取保守上界小于6MiB（保留原8MiB预留），含重复小证据和 used JSON 纯摘要字节扫描；不是 OS IO/RSS 实测。

全量 cached whitespace 原回执为 exit 2：62 处、7 个 generated 原始文件；filtered exit 0 只代表排除精确原件后的范围。`whitespace-check.json` 当时15787B／`2ddd296cea61ab47edcf5fb7b5aac6e8e1bb6987d85898507b34eb0399770f80`。本审读取回执，未重跑或逐条重取生成物空白诊断，不签全量 whitespace 0，不建议 trim 原始 CMakeCache／ConfigureLog／make／CTest 文件。

除一次获准静态 hash 两产物外，未读取或 hash 供方实体、SDK／cache／archive，未重做42772映射、工具探针、构建、测试、native／child／addon／GUI 执行。首轮失败、inspection 输出初始化失败、源夹具执行阻塞和各项 PENDING 必须连同成功构建记录保留。最终完整索引 bytes／SHA 校验由 owner 后续单独完成；本报告不预签尚未发生的闭包结果。
