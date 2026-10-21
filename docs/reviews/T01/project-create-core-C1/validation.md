# C1 最终验证与交付边界

结论：本候选完成已授权的内部空白创建事务机制；创建专项128项与完整检查通过，两份独立内审按同一五文件候选关闭。正式创建服务、resolution、真实位置/原dispatch绑定及父功能发布仍未交付。这里的内部内审不是指定双外审，也不是生产验收。

## 候选与接收

批准base为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，分支 `feature/weekly-t01-project-create-core`。先按14299B固定清单接收50项a816原Git字节，单独采纳提交 `ba2c6c293f9fd9e1742c9ab352dae5e3c951f6a4`。三项既有产品获准后续修改，其余47项原字节只读；新module/test使相对base产品及测试完整52路径。完整逐路径bytes/SHA和采纳核同见 source-manifest.json，不能把完整交付缩算为五项。

当前五文件冻结身份（主线工具2e0b92，随后全量检查与独立核验未改变）：

| 文件                                  | bytes | SHA256                                                           |
| ------------------------------------- | ----: | ---------------------------------------------------------------- |
| project/project_lifecycle.py          | 20932 | a43365c1615082a0229de0d8e48569227fa930a7c3a7f869360975d72f30d104 |
| storage.py                            | 76042 | fbef0d0ace0a01b9ced5eaecaf83aeb9306258c0cbfa5fd98a6d79e46bc5a39a |
| job_store.py                          | 87227 | 8896c3e30007e1dec04eaf47ae5bb5c33a1e9b3a1d016cb9165f99d8b4deeacc |
| project/format3.py                    | 32169 | 505d0beb124534b2ab2e6c1716df53ef7b8108bedb57f5300fcb79a68e955782 |
| tests/test_project_create_contract.py | 27843 | de02dcf022da0784e2d5d31dc0d29f8b2ca5cf0691cd2ca19835cd136c91020a |

前四项相对于packages/engine/src/ontolearn_engine，测试相对于packages/engine；manifest使用完整仓库相对路径。受保护AGENTS仍15852B/SHA78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759，不stage。

## 实际运行结果

每项启动命令的最后且唯一检查命令直接对应终态工具exit，未在npm后以另一条Python成功遮盖其退出码。

| 命令及完整日志                                                                                    | 启动/终态                             | 实际结果                                                                             |
| ------------------------------------------------------------------------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------ |
| `.venv/bin/pytest packages/engine/tests/test_project_create_contract.py -q`，target-pytest-06.log | b50a2c / session98989 / 53abda，exit0 | 128 passed，4.81s                                                                    |
| `UV_CACHE_DIR=/tmp/t01-create-core-runtime-cache/uv npm run check`，check-01.log                  | 79a7dd / session96986 / 3b62e4，exit0 | lint、format、typecheck、build通过；1125 TS通过；2969 Python通过、44既有跳过，85.97s |
| `npm run verify:sources`，verify-sources-01.log                                                   | 7c9c20，独立exit0                     | 核对12个归档源文件                                                                   |

以上日志均在原件安全包logs目录保留完整stdout/stderr。最终三个日志依次为180B/SHAf3e954e07c05a2ae600a53f52a9c1334a4579c5ec29cd01bdc435f1ad37d4298、8667B/SHA897bd1596e9f61a55baa2a07531208c9adce8a488f22644bbd723f474a1bc2a7、111B/SHA1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536。日志正文不自含exit字段；实际exit来自上述原工具终态，包内原始tool call/output记录保留关联。

专项覆盖真实10行/一外层事务/genesis读回、原request名称与UUID、后续metadata/domain后原回执重试、19个写入边界异常与19个真实自有子进程退出/重开、SQL INSERT拒绝、全库和全部页/最坏editor预算±1、旧格式/旧hash/旧reader拒新namespace、纯Store3/缺Job3/未知外层事务拒绝、异来源/namespace/损坏原件零修复。44项跳过保留原样，未计作通过。运行时长只登记实际结果，不据此推导性能提升。

## 首失败与独立发现

保留全部初次失败和中间日志：target01为81通过/2失败（metadata阈值fixture选错及旧对照包漏静态资源）；target05为127通过/1失败（新domain反例误用domainRevision键，实际键为domainAfterRevision）。修正均在唯一新测试文件内。ruff初次未用import/长行失败与后续修正日志同样保留。中间通过不充作最终候选通过。

独立事务审查原4f7fc8真实库复现P2-C1-01：自洽创建claim能借旧项目合法domain receipt，缺创建afterCheckpoint仍被Job-ready/重开接受。修复在creation_context直接核三种真实不可变行及Job3实际receipt比对，不调用递归history、不放宽旧validator。独立修后a29141实际重放确认creation_context、Job-ready和重开拒绝、authorizer写尝试空、完整dump不变；正常创建/后续历史/原回执/重开均成功。新增回归已进入最终128项及完整2969项。原反例和修后定点记录都在原始工具包，非重构摘要。

事务/兼容与全部接收路径由 independent-review.md 负责；完整写前预算另由 budget-model-review.md 负责。预算审查仅实际静态读取/独立算式与读取运行原件，未声称亲跑数据库或测试。两审均不是GLM-5.3最高与MiniMax M3.1-Flash/xhigh的真实同版双外审。

## 剩余门

无GUI/Electron/e2e/native/HMR/Keychain/模型/付费或用户位置IO，无公开wire、权限/位置capability工厂或默认格式更改。没有push、PR、CI、合并或生产证据。正式create_project_request、resolve_operation、I06实际物理绑定/current_scope、首位置IO、真人和两个目标OS仍保留前置；FR-001–006/804、44与57P0及完整原Goal未关闭。提交及安全包仅供根读取并决定本内部子阶段收口，不自行授权正式集成或发布。
