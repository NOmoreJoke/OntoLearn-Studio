# e37cc2b 实际四路径限定 delta 独立审查

结论：**F1（P2）与N1（P3）已在此固定delta静态关闭；未发现新blocking P1/P2。可由主控另发精确单文件unit START。** 这不是unit运行通过，也不是prepare/finalize/PyInstaller、A/B、parent运行或I05 scratch guard已执行。d4686b首报及其8成员原样保留；首报当时阻断结论不追改。

## 冻结身份及实际阅读

本次仅审 **e37cc2b161b53a6250a4085104ee955c423fb149** 相对parent **d4686b1769b5925190a9e7afcc23b92d5db04d4d**，tree **71b99b1ca0408a604c36742d0e3f3b90a5ec2ff1**；作者已停写。四文件工作区bytes、固定Git对象与delta-freeze逐一相等：

| 路径 | bytes / 行 | SHA-256 |
| --- | --- | --- |
| scripts/build-engine.mjs | 22318 / 686 | 36a2255c2e3e908f1b0421f042d5613843dc9ab5ece0f5b09b2a0a465544965b |
| packages/engine/src/ontolearn_engine/semantic_build_provenance.py | 83012 / 2165 | 1ff966ada91525a86f280f5e57d9a719f869986a1adafb90acfd6e8eedf6730d |
| packages/engine/tests/test_semantic_build_provenance.py | 120578 / 2958 | ee09707ab895bdfa8e831f38a200e5445d0a37d12c1fb8a603987efd4700edc9 |
| docs/iterations/T03/i05-semantic-parity-profile/private-profile-contract-v1.json | 55577 / 1270 | a93a5dc5b0b002482db8e99e072aab6d27d3a0cf58f59bfd9b0a7643305ead0d |

实际delta-product.patch **37482B / 625行 / SHA8ddcb70f4e8221f5c2604871fd99499da4bfe371ed3cdc26960ee637ed059cd9**，已分1–280、281–455、456–625全文读到EOF，并独立比较等于固定Git diff。已读全部newcontract改动、六个新增Python测试及新增/更改Node字符串；必要上下文承接首轮已全文审过的不变块，没有用方案审计或静态计数替actualcode审查。

process delta-manifest实际为 **9106B / SHA5941ee8b043356abd646d5c70d8c8b631d5fe17fe45fcdf5b57b0fa784c92032**。派发消息中的另一缩写/笔误不作身份依据。files[].path按process总根定位，46成员实际bytes/SHA均匹配；未执行其生成器或作者审计脚本。delta-freeze为6281B/SHA925cbeb631613631d180040182dd1fee607cd4f2c1260d76814c1013f9a2ecd2。

## F1 关闭：合同适用域与来源/权限/验收一致

新增合同已经同时修正整个相关域，未仅改几个字符串：

- inputs明确sourcePaths、frozen rowPaths、sourceRoot/frozenRoot与inputMappings关系；同字节pin保留，不把frozen路径拼回source根；
- contract源路径、bundle位置与fixedLayout/reader常量一致；
- entrypoint改独立canonical probe target，列canonicalModule、runtime canonical PYZ域、外部CArchive/fullbinding域、exact targetCode四键，与schema常量及archivePolicy一致；
- provenance、anchor、licenseMirrors及artifact root域明确；launcherRule为ontolearn-semantic-parity；
- finalPins区分c706实施基线、a633 M08采用和2cf/6891/401a历史组件，实际候选commit/tree不自动授采用或root批准；
- noRuntimeExecutionNow明确四源静态范围、0新blocking后controller独立START的条件unit，以及禁止actual helpers/build/target/OS；API存在不授执行，permit digest不代替后继票；
- requiredNegativeTests扩为16个明确类别，覆盖profile、source域、合同关系、mirror、loader/native、CArchive、PYZ、marshal/ref/展开预算、binding、三个child原流、控制JSON、scratch及parent兼容，不遗漏首审要求。

新增六Python测试逐字段断言上述关系、target/launcher/schema/runtime-external域、历史/当前/批准分域、conditional unit与不授build、16类必需负例、scratch外部账面。sourceHash/bytes常量均更新到55577/a93a；reader除此两常量外AST完全不变。新contract不嵌自身SHA或reader源hash，没有引入循环摘要。F1在该固定delta可静态关闭；这些测试文本尚未执行。

## N1 关闭：已知原流引用不随哈希IO失败消失

builder仅在parityChild receipt新增 **stdoutPath、stderrPath、receiptPath** 三个无条件字段，其余代码逐字节相同。对应成功验证断言新增三字段；原单个prepare hash IO失败用例扩为prepare/PyInstaller/finalize三个阶段。

这些负例文本要求：该阶段后无额外child；首原流物理文件仍存在、bytes保留；complete=false、ioError=EIO；失败channel identity与captureRange仍null，不能捏造hash或范围；两个已知path及receiptPath保留，未失败stderr仍有真hash/range。没有通过重跑child补流，没有合并channel或改变helper4/公开6返回。N1静态关闭。

## 新root buildScratch要求与实际实现映射

contract `/buildScratch`、process `build-scratch-map.json`（2950B/SHA7008eeeef08a981bb05fe239487a72cdc20f28663268e05a71410e161a581efe）及delta-freeze.machineMap完整对象相同。map的基础是 **runRoot=build/i05-semantic-parity/<fresh-uuid>**，占位符没有冒实际UUID。

| 真实实现使用面 | runRoot相对映射 |
| --- | --- |
| --workpath / --specpath / --distpath / --paths | pyinstaller / spec / dist / generated |
| 实际artifact | dist/ontolearn-semantic-parity |
| UV_CACHE_DIR / PYINSTALLER_CONFIG_DIR / TMPDIR | evidence/cache/uv / evidence/cache/pyinstaller / evidence/tmp |
| generated anchor | generated/_i05_semantic_parity_build_anchor.py |
| 两prepared文件 | provenance/i05/source-package-parity-build.json；provenance/i05/source-package-parity-private-contract-v1.json |
| mirror、binding、build request | licenses/；artifact-binding-v1.json；evidence/build-request-v1.json |
| 三阶段原流/receipt | evidence/<phase>.stdout.log、.stderr.log、.receipt.json |
| helper控制结果 | evidence/prepare.control.json、evidence/finalize.control.json；PyInstaller无control文件 |

逐项与已审未变builder的env、argv、data、返回路径和reader输出路径核对，一致。新增Node unit用相同run/io/uuid stub取得实际参数/临时文件，逐map关系断言；Python新测试另明确固定map/policy值。没有执行stub或实际child来证明这张表。

sampling明确 **8589934592 bytes**，只由 **I05 external caller** 对整个own runRoot及所有后代递归采样为一个账面域；不重复加work/dist/cache子域。不只是统计最终artifact而漏raw/receipt/tmp/cache/generated/notice/provenance/binding。`builderEnforced=false`、`osHardLimitImplemented=false`、`runtimeGuarantee=false`，没有把文本mapping说成OS quota、磁盘实测或容量保证。

executionGuard明确guardRequired=true，缺失结果 **BUILD_SCRATCH_GUARD_REQUIRED**，permitDigestMayBypass=false。**T03 builder没有因此实作I05外部采样或绕过其fail-closed；本轮接受的是映射/责任和不得绕过的合同，不是I05 guard行为已实测。** 未来实际A前仍须I05自己的已审guard/资源与命令票；unit或binding摘要不能代替。

## 不变范围与回归风险核对

- 此commit仅四产品路径；reader仅新contract SHA/bytes两常量；builder只增加三receipt字段。CArchive/PYZ/marshal/loader/prepare/finalize实际约束及parent实现未借本修订放宽；
- 新contract保35/sourceGuard及5buildInputs，32个非本次产品guard的Git blob与d468一致；两sealed资产正文未读；entrypoint、旧M08 contract、root/engine pyproject、uv.lock固定对象均不变；
- 原BUILDER_UNIT字串完全不变；原Python定义除新Node单文件包装测试的预期计数28→31外AST相同。原c706 58个定义的保留结论继续成立；
- Node字符串新增一项机械map测试，单个hash IO用例展开为三阶段，31只是文本预期，尚无实际通过数；
- 首报review-d4686b.md及其manifest8成员逐字节再核不变，没有改旧审意见时态，也没有将旧阻断追认为通过。

本次没有发现需扩大writer、修改I05/原资源/旧合同或放宽strict/caps的必要。若单文件unit暴露新失败，仍按首失败保存与唯一作者精确fix/独立受影响delta复核处理。

## Unit门建议及未验边界

本actualdelta达到 **0新blocking P1/P2**。主控可在own环境/缓存/TMP及精确票条件满足后，另发唯一单文件unit START：`/Users/kyle/.local/bin/uv run --frozen pytest packages/engine/tests/test_semantic_build_provenance.py -q --maxfail=1`，UV_NO_SYNC=1/UV_OFFLINE=1等遵精确票。只有受控mocks/temp fixtures/Node run/io/uuid stub，不能使该命令触发真实prepare/PyInstaller/target或扩大为repo全测。

审查者没有运行该命令、Node --check、Node stub或任何产品；静态审计脚本exit0仅表示固定Git/AST/JSON/hash复核完成。真实unit结果、I05 consumer及完整loader join、外部scratch guard、A一次、root完整artifact/binding批准、fresh source/frozen B各一次、parent/平台/GUI/业务/发布全部仍未验。本报告不授这些运行权。
