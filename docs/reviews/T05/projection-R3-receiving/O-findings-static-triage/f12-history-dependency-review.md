# F12：I01 历史脚本与当前验收依赖静态核查

结论：`scripts/verify-i01.py` 的旧协议健康步骤与 O 固定源码中的 v2 常驻入口不兼容，F12 的失配事实成立。已检查的 npm、CI、常用开发命令和 I04 验收链没有执行该脚本；尚未证实它是当前 O 验收的执行依赖。它仍是 O 的 149 件完整工程覆盖对象，不能删清单、删原件或用“CI 未调用”宣布意见关闭。原 MiniMax final-v2 的 NotPass 与完整覆盖账保持原样，本报告只提供 F12 的有限静态处置依据。

## 范围与方法

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-source-package-oracle`。
- O source：`77852d27a3c4e84867a42f243e0f4e0f32b8df67`；过程：`86df64a2c707355ed177d536ef5975a1986c0f0b`；base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 本次读取时 HEAD：`c00e10be2a9a778bd73d814ff9898f5dc6d5b617`。不以 HEAD 替代固定 source。下表逐项用 `git show <ref>:<path>` 取字节，与当前文件直接比较并计算 SHA-256。
- 只读取本树 AGENTS、相关 S1/S2 规则、固定源码、配置、验收文档、I01 历史记录和指定 F12 原报告。AGENTS 所列 `docs/architecture/m0-review-and-update-plan-2026-10-19.md` 在本树不存在；相关原 S1/S2 规则读取其 I01 冻结副本 `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`，不把副本路径误报为现存架构文件。
- 使用文本检索、Git 元数据/原件读取和哈希比较；未运行 `verify-i01.py`、产品入口、pytest、npm 验证、打包、GUI、模型、网络或 Goal，未进入两份冻结模型审查工作树，未新建运行探针。
- 唯一新增文件为本报告。共享 README、矩阵、清单、原报告、实现及历史脚本均不改动。以下路径行号为固定字节核对后的本树文件行号；历史版本另标 ref。

## 固定版本与当前字节

下列 16 个文件分别与 source、过程、base 三个固定 ref 的字节全部相等。仅对本表下结论，不声称全工程无变化。

| 路径 | 字节 | SHA-256 |
| --- | ---: | --- |
| `scripts/verify-i01.py` | 4595 | `b1f4118a65369190e6f34a599e219ee3a641d59a42206af621fbd155be848e11` |
| `scripts/verify-i04-package.py` | 3290 | `fa0d5d6e134bd0205b1c9bc65bfa6a12aa45e56144d3b3745fe7028b45fb7ef1` |
| `package.json` | 1953 | `be16490f2fcddad19fdffec0b3efc63ae3f887dc40dc2146293c86cbc93b9c32` |
| `apps/desktop/package.json` | 491 | `35f077bf29fc15fee1c9785bd89b01b9059edc30c185bd45affdfde0681235ae` |
| `packages/contracts/package.json` | 291 | `2bdce0f15eb195ddbdfcf75e7c43262bb1ff934c588b285f3e3c749750d72bcc` |
| `.github/workflows/ci.yml` | 6860 | `b5d92d19383ef12adf9b96764b9eaf16d3ae9ffa9c88a3a678ec2b24454a05f4` |
| `packages/engine/entrypoint.py` | 787 | `979b65e5efc3d19ad9851cc2a97255594591626fbed2efbecd8713723e9f2f60` |
| `packages/engine/src/ontolearn_engine/__main__.py` | 489 | `1fa0f9711a4d90db6fe8ef6c0948aebd93c910526838d6d41fac8a00a568c1d9` |
| `packages/engine/src/ontolearn_engine/coordinator.py` | 29559 | `597d74e318645d0ae4e7152acc29487efc37cb23b501404e60b21f5ed87fc7cb` |
| `packages/engine/tests/test_coordinator_control.py` | 5103 | `51e6c1c729e2c9995cfd608d2299a9dd0a3dc7359f1dbc526b16a247ef48c8ea` |
| `packages/engine/tests/test_resident_runtime.py` | 20364 | `ba9ab70b7d29d232f2e02f68c95ba75387577d8e44086bfe9c5348be0a419062` |
| `packages/contracts/v2/schema.json` | 122889 | `9215266523f539c81282bbc96ca88de52b79c99ef39f7696b3a49c58fa7a2b79` |
| `docs/iterations/I01/acceptance.md` | 14801 | `c62e1a9c94f9ec6a7572f16b62ceefa09af0e3e0a3f6bb916390d354288db732` |
| `docs/iterations/I04/acceptance.md` | 11805 | `4f2d8654f350f7b2f9967b1bbcd8ffa493c92f37c143b6701b320160ee6a10de` |
| `pyproject.toml` | 494 | `55674b4f13c4185b5db8629db363aed3e506df836ed0d7e67dcfe7db8154ea63` |
| `scripts/build-engine.mjs` | 1234 | `2a9036fd76ed32f8df52d7ffa7afee2213c00008986269cd2d1cf66f1857aa81` |

## 来源、用途与历史证据

1. `git log --follow -- scripts/verify-i01.py` 显示脚本在 `6d8e4b3021b368661247c03c47f01e4d32ebf6e1`（`feat(I01): spike transactional storage and dependency invalidation`）加入，随后在 `3e787fb7f8923a0848c173215af2747861e4b35a` 修改包内规则文件断言，从 `invalidation-v1.json` 改为 `invalidation-v2.json`；未改健康协议。此处失效规则文件的 v2 与传输协议 v2 是不同事项。
2. `scripts/verify-i01.py:1` 自述为 S1 开发与实际 app-resource 可执行文件证据工具。`:24-50` 运行开发/包内 × 1x/10x × 三次存储样例并比较完整结果关联；`:51-69` 是包内旧 health 步骤；`:70-110` 继续检查规则资源、许可证、包清单和 Darwin 动态链接。不能因健康步骤失配就推断每个存储探针本身已坏；本轮也未单独执行它们。
3. I01 最终候选 `1e3b179de1e1f9f7ad4b6556f292ef769c113d18` 的脚本 SHA-256 仍为 `b1f4118a…848e11`，与本次 O 脚本一致；但该历史候选的 `packages/engine/src/ontolearn_engine/__main__.py:1-13` 是“一次读取、handle_request、写一行、退出”的旧入口。脚本没变不意味着其运行目标协议没变。
4. `docs/reviews/I01/status.md:5-9` 明确 I01 范围为 S1、非目标包含 v2 任务协议，并指向上述 I01 固定 head；`:29`、`:88`、`:114-118` 保存当时 package/probe 的运行记录及冻结背景。`docs/reviews/I01/round-3/minimax-m31flash.md:78`、`round-3/zcode-glm53.md:40` 是该历史候选上独立运行的归档声明。本轮只读它们，未再次证实这些历史运行，也不把它们当 O 上刚运行通过的证据。
5. 原 S1 的“两档测量、原始记录”要求仍须保留：`docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md:55-62`，及 `docs/iterations/I01/acceptance.md:13,54-58`。未发现这些条款点名必须在每次后续 O 审查执行这个特定脚本；同样不能从此推导后续改动一概无需复验 S1 要求。

## 当前执行依赖核查

| 层面 | 精确依据 | 有限判断 |
| --- | --- | --- |
| npm 执行链 | `package.json:13-28`；`apps/desktop/package.json:8-12`；`packages/contracts/package.json` scripts；`scripts/build-engine.mjs:5-36` | `check`、`engine:check`、`package:dir`、`engine:build` 无调用 I01 脚本。PyInstaller 以 `packages/engine/entrypoint.py` 为入口，不自动执行验证脚本。 |
| Python 测试发现 | `pyproject.toml:16-17` | pytest 的 testpaths 为 `packages/engine/tests`；未将 `scripts/verify-i01.py` 注册为测试入口。它仍可被 lint/format 作为开发文件扫描，这不等于执行其健康步骤。 |
| CI | `.github/workflows/ci.yml:30-39,48-72,123-130` | quality 执行矩阵、check、sources、e2e、打包后明确执行 `verify-i04-package.py`；desktop 亦明确执行 I04 验证器。两个 job 均无 I01 脚本调用。 |
| I04 现行验收指向 | `docs/iterations/I04/acceptance.md:3,7,16` | 当前追踪要求同 PID 多次 health、严格 v1 拒绝，并点名 `verify-i04-package`。旧 S1 存储故障要求另在 `:12` 继承；这不能解释成继承 I01 的 v1 wire health。 |
| I04 包验证器 | `scripts/verify-i04-package.py:32-59,60-79` | 验证资源/公共例后，以包内 executable 跑 resident runtime、worker、owner bootstrap 测试；未委托 I01 脚本。 |
| v2 运行输入 | `packages/engine/tests/test_resident_runtime.py:19-76,252-264` | 源码/包内共享 Session 先 hello，再同 PID 重复 health；这里是现有测试定义与调用链的静态事实，本轮未运行。 |
| 常用文档 | `README.md:22-27`；`docs/development.md:9-18` | 常用命令不含 I01 脚本。开发指南 `:31` 仍保留“一次请求后退出”的旧叙述，这是文档时效线索，不证明 I01 脚本被当前验收调用；不在本子任务顺手改写。 |
| O 工程清单 | `docs/iterations/T05/projection-R3-receiving/review-packages/O/full-engineering-inventory.json:6,960-974,1201` | 149 件中明确包含 I01/I04 两个验证器。清单 scope 是源码/工具/测试/配置/authoring 对固定 Git 与 SHA 的覆盖；没有声称每个列入的工具均是当前必须执行的命令。 |

补充检索：对 source 固定 ref 执行 `git grep -n -F 'verify-i01'`，排除本轮 T05 流程材料时，命中为 I01 历史候选清单、历史审查和状态文档；在源码、scripts、测试、npm、CI、README、architecture、I04 和 T05 当前验收/authoring 路径的定向检索未发现调用。当前接收包的其他命中是完整工程 inventory 和 preflight 中的路径记录。此类路径记录证明覆盖/携带，不证明执行依赖。未据此声称仓库外总控、未来人工命令或未检查系统绝无依赖。

因此，“当前自动执行依赖已排查为无”仅适用于上述具体链；“当前 O 原验收依赖该脚本”未被证实。若总控拥有尚未提供的明确验收命令引用，应按其固定来源补充重新分类，不能用缺引用替代需求决定。

## v2 失配的实际静态边界

原报告为 `docs/reviews/T05/projection-R3-receiving/O-launch-dispatch/normal-recovery-progress/minimax-final-v2-original.md:343-353`。

- 定位须更正：旧请求、解码和断言在 `scripts/verify-i01.py:51-69`，不是原报告写的 `:100-115`。`:100-115` 属清单 scope/文件输出和打印段。原报告不改写，本处保留更正对照。
- 构建入口链可静态追到：`scripts/build-engine.mjs:36` → `packages/engine/entrypoint.py:23-26` → `packages/engine/src/ontolearn_engine/__main__.py:7-11` → coordinator `serve`。`--storage-probe` 则仍走 entrypoint `:6-10` 的专用分支；健康子进程在 I01 脚本 `:52` 无该参数，因此会进入 resident v2。
- 旧 health 的 id 为 `I01-packaged-health`（I01 脚本 `:56`），还先于信封形状触发 `coordinator.py:168-169` 的 UUID 校验失败；id 规则见 `packages/contracts/v2/schema.json:6-9`。原报告列出的缺字段仍是独立失配，但对未改脚本而言，首个拒绝点更早。
- 即使换成合法 UUID，`coordinator.py:176-178` 也拒绝缺 `kind/engineSessionId/params` 的请求；即使补齐信封而仍用 version 1，`:187-190` 会返回版本错误，或在未 hello 时拒绝非 hello。v2 hello 的协商和会话创建位于 `:193-208`；后续请求还必须带匹配的会话 `:210-216`。
- 对原始旧请求，`serve` 的 `coordinator.emit(coordinator.request(value))` 在 `:649` 先求 request；ProtocolFault 在 `:652-653` 被捕获并进入清理 `:654-659`。在成功启动、可读取该帧、无其他初始化/环境故障的限定路径下，该旧帧没有成功响应，脚本 `:67` 对空 stdout 解 JSON 会失败。这是静态推演，未观察本轮进程退出码、异常文本、耗时或日志，不能写为本轮“确定性运行复现”。更早的探针、包资源或启动失败也可能使整脚本先退出。
- 仅换 v2 信封还不足以恢复工具：`coordinator.py:239-241` 的 health result 是 `status/engineVersion`，capabilities 由 hello 返回（`:202-208`）；脚本 `:69` 仍期待 health result 内 `capabilities == ["health"]`。新的用途必须区分产品能力声明与 v2Runtime 基础设施方法，不能机械复制旧断言。
- `packages/engine/tests/test_coordinator_control.py:42-49` 已明确写有无隐式 v1 fallback 的断言；I04 验收 `:7` 也要求严格 v1 拒绝。为迁就旧工具重新开放旧协议会改变现行边界，不是最小修复。

原计划冻结副本 `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md:81-83` 已明确 v1 health 无外部兼容承诺、v2 双端同步且不长期维护两套协议；ADR-0003 `docs/architecture/0003-resident-coordinator-and-jobs.md:7,15,17` 对当前常驻、有限生命周期和同源契约给出决定。历史工具失配不能直接认定产品违反 v1 兼容要求。

## 最小必要处置计划与 owner

F12 唯一处置 owner：T05 O 总控 `/root`。本静态核查 agent 只负责本报告；不认领源脚本、入口、契约、CI 或共享清单的修改权。

1. 总控先在独立处置记录接收以上事实：F12 = “历史 I01 验证工具与现行 v2 不兼容；当前已检查执行链无调用；当前 O 特定验收依赖尚未证实”。保留中优先级原意见与 NotPass，交由原有意见处理/指定审查门禁裁决，不以本报告自行降级或宣告关闭。
2. 以现有证据，最小处理是追加该工具的历史适用 ref、当前手动调用限制与现行 I04 验证入口说明；保留脚本原字节、历史原始产物、原报告和 O 149 件覆盖账。无需为“让149件都能执行”机械更新所有历史工具，也不能从清单移走该脚本规避本项。若标识说明影响 authoring 受审范围，作为新候选交付并按现行门禁审查，不回写已冻结原件。
3. 仅当总控补充固定需求证明当前必须继续执行该特定工具，才由同一 owner 单独授权一个维护者，在新候选增加现行工具或显式版本分派。设计需保留开发/包内存储两档三次、结果关联、资源与许可证要求，采用合法 UUID、真实 hello/session、正确能力字段和有界常驻清理；先核对现有 I04 测试是否满足该需求，避免重复实现。不要修改 v2 接受面来兼容错误信封。
4. 后续若有实现或验收改动，再执行对应实际反例、成功路径、包内样例、适用 check/打包及同版指定审查。新增工具需证明其没有跳过原 S1 要求。该步骤本轮未授权执行，不能登记为已完成或已验证。

未解决限制：当前脚本对 v2 的失配仍在；历史工具适用范围尚无现行明确标识；本报告没有提供当前 O 的运行/包内/生产通过证据，也不裁定其他 F 项、O 包或父模块验收完成。
