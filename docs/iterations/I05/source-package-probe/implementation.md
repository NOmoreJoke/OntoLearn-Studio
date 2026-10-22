# I05 source/package probe：源码候选

本窗只交新 probe、纯输入资产、生成器和测试源码。没有导入或执行产品／测试；静态结果不代替后续运行、oracle、构建或发布验收。

## 固定组合与入口

新树基线 5f910b52c69d86a1076b2032e5d3c63e715947f3；22 模块逐项原样取自 6891a5842302859a531cf82767c5a482417bc274，过程 f79a29f596b2444cba542a906c91727869014886，单独采用提交 01434e3。T01 四件资源按增补授权在 44f88a5 单独采用，原维护权不变；受审 dd972b79adf4d378636a7d41a6b0e3e08c0d5ca1，过程 79d63cc1f403ee857a3af2a98f8870db9a6a910d。

唯一入口是 canonical ontolearn_engine.semantic_source_package_probe.main；脚本与 -m 的 guard 在类定义前转入该模块。只接收 flag --semantic-source-package-probe 配合 full-v1、b1-semantic-1x-v1、b1-semantic-10x-v1 三种精确 argv。未来包直接以同一文件为 target，父入口及构建配置不在本窗修改。

输入固定 source package-relative 或 frozen _MEIPASS/provenance/i05/source-package-parity/，不按 cwd、环境或用户路径回退。先限额读取及校验 descriptor/input bytes，再严格 JSON／schema／集合／上下文。合法规则 definition.heads 保留；资产不含运行结果或恢复见证。417 个 observation、320 个 dataset；83/106/54/50 上下文分开，83 中 82 可作独立数学输入、79 有完整原上下文、交集 78。第77个 profile不执行，repair before/after 的独立 SHACL 样本继续调用；四个 E5 只作为片段数学输入。

## 输出与真实调用

JSONL 格式为 i05-source-package-observations/1，完整 header、逐项 observation、terminal。包括全部输入参数／来源／投影摘要、真实图／全 rows／SHACL API 返回字段、生产 wire 与五项原 bytes 的 base64/长度/SHA，以及实际 native dataclass 的固定只读字段、allocation、expectation、receipts、恢复 projection 和 roots。wire 保持实际 JSON；native 整数单独以 integerHex 表示，避免损失大整数。没有原始 Validator RDF Graph 返回的 API 不伪造该 Graph。

scope 真 prepare，再把同次 reasoning_result 与 provenance 交 project；分阶段记录实际 reason/Validator 计数，真正 query/SHACL 消费所选 scope。失败保留已完成阶段，不能以预置五字段结果冒充新鲜计算。

生产准备与生产计算分别使用新 CaptureLedger；恢复沿用同次发行的 caller-held expectation 与 original_allocation，各次恢复另用新 RestoreLedger，解释另用新 DirectStepsLedger。九项有限扰动只改 receiver bytes 副本，**不重绑任何 expectation 摘要或 allocation**。本窗只能观察原摘要的 A1 完整性拒绝，深层 DAG、末 child 原子性等原单测属于另域，不能据此新签结论。

full 以只读 profile hook 对实际 semantic.reason.__code__／Validator.run.__code__ 计数，已有 hook 前置失败，finally 恢复。两个 B1 子集不用该 hook，保原四 ontology 和 equipment/001 改型输入步骤，First/Warm 的真实纯语义阶段及全部结果单列。fresh process 是否真的成立由外部 collector 核验；进程 startup、Python allocation、RSS、物理冷读等保持 unknown，不采用被拒的 heap/OS 方法。S1 snapshotLoad 仍未执行并保持 Store HOLD。

离线观察只记录 audit 事件名称，绝不记录 URL／参数；只有本 observer 在 canonical denial hook 之前安装时，attemptCount 才有完整性解释。已提前导入 semantic_offline 的进程标次序不可确认；不能把 hook 配置当作真实拒网证据。

## 失败与限额

descriptor 1 MiB、input 8 MiB、512 项、单项 32 MiB、总报告 64 MiB、terminal reserve 65536 B、边界 deadline 120 秒均是逻辑限额，不是 whole-H。输入当前 8205267 B，尚余 183341 B。逐条完整编码后才写；partial write 继续，半行故障后不追加 terminal 冒充有效 JSONL。超限不截尾、不删样本；真实运行若不能装入完整结果，必须给精确 delta，不能声称完整采集。

exit 0 仅表示所选集合协议采集完整，可包含已知拒绝和未执行；1 为 harness/未知/逻辑输出/边界 deadline；2 为参数、资产、身份前置错误；130 只表示协作 stopping。进程实际停止、硬超时、signal 和 reader join 由外部 collector 证明。oracle／source-package equivalence／原操作通过始终分开且本 probe 不自签。

R1 修复后，同一 monotonic 起点在 preflight 之前取得，首个业务调用前计入该耗时。probe 内 CollectionBoundary 用 ContextVar 传递；每个显式 canonical 调用前后检查，不替换业务 callable，opaque 调用仍不能被其硬中断。返回时已越界会停止下一调用，保当前真实返回与 callCounts，deadline=1、协作停止=130，均不签实际进程停止。

每阶段保 stage/API、开始／结束／实际返回状态；失败 observation 的 partialOutputs 只含已经真正返回的阶段，包括完整图／表／报告、生产接收 bytes、allocation、expectation、receipts 及已完整成功的恢复 view。未返回的恢复只有阶段元数据，不发行部分 view。B1 的 First/Warm 每一阶段分别保留；partial 阶段的 elapsedNs 为 guard 内单次调用计时，完整 B1 phases 为 timed 包住调用及边界检查的计时，两域不混作新性能结论。所有序列化仍受原 cap；编码或运输不能完成即 incomplete，不能删字段凑通过。

## 仍待后续窗口

当前树 uv.lock 仍是 5f 的 20999 B／d5d027da6628a2f4fc2e73730ce3a5e40d85aebba95188b0d4c3801ebdde949e，没有复制或采用 T03 锁／环境。probe 要求的固定供应锁为28440 B／86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73，因此当前组合不能声称可运行。Python3.12／八 distribution 的真实安装也未验证。

没有获授 T03 外部 build-provenance schema，frozen 明确前置拒绝，不用预填 source SHA 充当 PYZ 的真实代码证明。源码未来可将 verified bytes 的编译 code object 与实际 loader code 指纹比较；当前没有执行该路径。源／包同版全 suite、独立 oracle、12 个 B1 fresh 试验、原12个 S1 snapshot 试验、包目录清单、父产物、check/package、指定双模型、CI、目标 OS、真人和 develop／远端门仍需各自完成。
