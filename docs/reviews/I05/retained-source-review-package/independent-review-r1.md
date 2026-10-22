# I05 完整保留源码备包独立审查 R1

结论：**备包发审就绪 Fail，须先关闭两项 P2。** 完整归档、固定 Git 身份、差异载体及逐路径覆盖检查通过；问题在原件指路和实际派发隔离方案。没有产品源码缺失或归档篡改发现。本结论只审材料与发审准备，不是产品正确性或指定双模型审查结论。

审查者为根会话新建的独立备包 agent，仅向根会话交付。实际指定应用任务仍为 0；没有创建外审、Goal、对外消息或产品执行。

## 固定身份与范围

唯一工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-retained-source-review-package`；分支 `docs/I05-retained-source-review-package`。

| 身份                        | 精确 SHA                                   |
| --------------------------- | ------------------------------------------ |
| 批准 base                   | `5f910b52c69d86a1076b2032e5d3c63e715947f3` |
| 主产品 source-only          | `2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64` |
| 产品最终过程                | `61f53dbe76262f5003065900a4e97d9a6130014b` |
| 备包 candidate              | `4de58348f25dc28e2dd18ef928101f2b7293355f` |
| 本轮读取的备包 process HEAD | `2dd91056000c3ff7a6d102eff4a168ec5419bd1b` |

已读主/树 AGENTS、三份现行外部政策、readme、两份完整 prompt、coverage Markdown/JSON、队列、dispatch、全部 guidance 及其 manifest、作者审计/冻结/最终收据和各清单。机器完整解析大型清单，按实际固定 Git 与归档核验；没有把 13 MiB 清单的局部显示当完整验证。全文结构证明在 `independent-proof-r1.json`，首失败原件另存。

新写入仅本目录 `independent-*`；原 candidate、旧 manifest/prompt/归档/源文件、AGENTS、reports 均未修改。不 stage、commit、branch、push 或调用任何产品入口。也未读取费用/D2 WIP、向其作者或审查者传递源码 actual。

## 必须处理的发现

### PKT-R1-P2-01：两份 prompt 的原件路径指空

- 位置：`zcode-glm53-input.md:20–21`、`minimax-m31flash-input.md:20–21`。
- 触发：两份 prompt 要求从主树读取 `docs/architecture/m0-review-and-update-plan-2026-10-19.md`，但主 2cf 的完整 856 路径中没有该文件。两份 prompt 还指 `reference-C4` 的 `round-4/full-review-input.md`，但 `docs/reviews/I05/round-4/full-review-input.md` 在全部 16 快照均不存在。
- 影响：审者按明确指路无法完成必读的 M0 S1/S2/S3/C1/B1/U1 和旧 I05 原审查输入读取；仅凭“全文已保留”无法可靠定位。这个问题不表示原需求字节丢失。
- 证据：主 2cf 中以下两件实际存在且逐 Git/blob/bytes/SHA 相同：`docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`、`docs/reviews/I03/inputs/m0-review-and-update-plan-2026-10-19.md`。均 35,812 B，blob `3672867e50ecc2f359c1dcd7a81db1ae8f9b1d26`，SHA-256 `c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96`。C4 实际保留 I05 `round-1/`、`round-2/`、`round-3/full-review-input.md`，以及 `inputs-c1/` 的 launch、resume、goal-objective 和原规则七件。
- 最小处置：派发前固定一份原件映射补充，明确正确 namespace/ref/path/bytes/SHA 及 C4 应读哪份历史输入；或者生成新 prompt candidate。保留本轮错误指路及首失败，不改旧归档原件。修正后只需对新映射/提示/隔离派发资料做增量复核，无需重压归档或重复产品测试。

### PKT-R1-P2-02：独立任务的输出与自动状态读面尚未具体化

- 位置：`dispatch-requirements.json` 的 reviewer/requiredReadback；两份 prompt 第 3、7–9、43、55–61 行。
- 触发：两份计划任务选择同一工作树、同一 `reports/` 父目录。文本已明确禁读 peer 的本轮 prompt/过程/报告，但没有固定两个独立输入副本、每位任务自己的输出/自动状态命名空间、共享输入允许读面，以及意外发现 peer 自动状态时的停止/报告处置。
- 影响：任务权限为 yolo/bypassPermissions 时，当前材料只表达独立性意图，尚不能逐任务核验实际读写隔离；自动生成状态文件也可能成为 peer 过程信息入口。
- 证据边界：根会话补充要求核此风险；本审查只以本包现有指令和 dispatch 作判断。本包实际指定任务 0，没有观察到本包发生串读或意见泄露。其他线事件不作为本包已泄露的证据。
- 最小处置：派发前由根固定两个独立副本，各自绑定同一冻结输入字节；分别规定本人输出与自动状态允许读写面，仅共同不可变输入可共享。禁止发现/读取另一任务、状态、自动元数据；发生意外跨读应立即保全并上报，由根决定该轮独立性是否失效。创建/设置/任务 ID/完整 prompt hash 均逐真实任务读回，不能只凭用户级默认设置证明。本人报告只本人写。

## 已通过的材料核验

1. `frozen-inputs.tar.gz` 为 84,876,346 B，SHA-256 `4bbbd798e6c7a67153db51e185c8795d9ac3509cc4442a81e2071bf319dfaa12`。顺序解压读取一次，22,492 个唯一安全 member = 3,006 实体 + 19,486 hardlink。没有绝对/回退/反斜线逃逸、重复名、符号链接或设备节点；所有 hardlink 指向包内先前已核的内容，内容身份相同，无循环或错 ref。
2. 每个 member 的 sourceRef/sourcePath/mode/bytes、SHA-256 和 Git blob 身份吻合；3,129 个唯一固定 Git blob 经一次只读 batch 直接读回，其中覆盖归档 3,006 实体及矩阵 211 hashes。大流保留固定 Git 对象原件引用、精确输入 OID 顺序、实际 stdout bytes/SHA；不重复复制源码大流或向工具输出明文。
3. 16 个 namespace 均逐完整 Git pathset 核同。主 2cf 是完整 856 件 Git 树；61f 只有恰六个 docs delta。产品与旧 worker/bridge/native/harness/CI/lock 版本没有被混拼成一棵工程。
4. 主 base→2cf 的 binary/full-index 13,082,467 B 差异和 16 份参考/队列差异，共 17 个 lossless base64 载体，逐原 argv 重取 Git bytes 全同。八额外保留 branch 均有 exact ref 与实际可读 diff，明确后继待审/原 owner 采用或撤回，并未假报已审或永久丢弃。
5. `candidate-git-manifest.json` 精确列全 candidate 的 119 文件、284,042,103 B；current = 固定 candidate Git = 声明 SHA。process 共 124 文件，只额外五件流程资料，candidate 119 件不变。较早 `candidate-complete-manifest.json` 不是完整 Git 成员清单；少 `text-correction-whitespace.json` 的事实由 `final-input-audit.json` 明确披露，旧清单未被擦写成“从未缺项”。
6. 148 路径 × 8 阶段、211 个唯一 hash 全核；每阶段所有非 docs/design/licenses/AGENTS delta 路径与矩阵集合精确相等，无表外遗落路径。6891 的 47 个 missing tests 精确拆为 24 I05/quality + 23 T01，另 task-runtime 字节不同；27 fixture 缺失、13 missing 源码和 11 changed 共享源码均是真实固定原件，已在参考快照可读。13 = 11 T01 project + profile_probe/samples，不能由主 70 新函数替代。
7. supplier22 与矩阵 same22 确为不同集合：前者含同 base 的根 `__init__.py`，后者含 `contract_v2.py`；不能把 22 相等扩大为整工程采用。C4 另 53 件许可原件准确保在 C4 namespace、主树没有，不作为当前 bundle 许可验证通过。
8. shape 最终过程 `a15f1478e398fb3b58fd60b1421a9cad04fdb430` 没有独立同名 cohort，但其相对 43d 的 143 件过程原件全部在 integer/date 产品及过程 namespace 按同 path+blob 保存。逐件 carrier 映射已给 proof，因此没有误报漏原件；后继指路可进一步显式列这条映射。
9. 12 份 guidance 复制件均与声明 bytes/SHA 及现行外部源一致，树 AGENTS 与当前 15,147 B / `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` 相同。历史 AGENTS 不倒改。calculation/lexical/restore-tests 的 26 项仅保 opaque 账，无冻结身份；本审者未去读这些 WIP 来补产品。

## 历史、权限与完整验收

两份完整 prompt 没有把范围缩成 readyS1、22 模块或 70 tests：原 PRD FR/附录 C–G/第10–12节、57P0、M0 S1/S2/S3/C1/B1/U1、ADR、原 I05 launch/resume/Goal、基线上下文、全差异、源码/测试/fixture/config/locks/resources/licenses 和原首失败均被要求保留读取。产品可读与可执行范围分开，允许固定 Git/stdlib JSON/hash/tar/AST 等必要静态核验；没有将未取得 native/HOLD/自动拒绝项目运行权交给模型。当前执行禁令未阻止本轮必要材料静态核验。完整原验收要求保留，运行缺证须明确 NotPass/无法验证。

提示准确保留 C1 原两任务 native UUID unknown、标签非 ID、ZCode 条件 Pass / MiniMax 最终 NotPass；C2/C3/C4 实际 0 新任务，内审仅限定结论。主 source-only R1 Fail 与 R2 限定静态结论不冒指定外审。尚无指定报告不是无法审备包的理由，本轮也没有虚填任务 ID 或 Pass。

供应锁/四 writer 未组合、八 distribution、同 selector source/package、417 独立 oracle/全值首错/费用准入发行、loader/cache 指纹、JSONL/output cap、许可与 parent、S1 12 snapshot+12 B1 fresh、SQLite 损坏输入 HOLD、whole-H、正式 Job/Store/owned worker/selected K0..32/Σ/H、两 OS/真人/CI/develop 远端缺证均在提示中。CI 按双 Pass 后 push/PR、正常合并前核验，没有要求本无 push 任务已具新 CI。无新增付款/凭据/重置授权。

作者历史异常均保留：随机 gzip hardlink 查回中止 exit130/KeyboardInterrupt、NUL 名单修正前 exit1、早期受 ignore 影响的 Prettier exit0 不代表覆盖；后续显式 ignore 九件格式检查 exit0。完整 base→process whitespace 本人复核仍 exit2，恰为 `author-build.py` 与 `author-finish-first.py` EOF 原件；精确仅排两件后 exit0。没有清洗原件或称全量绿。74 条历史命令的已有双流载体按长度/哈希或 base64 解码核验，未运行任何历史作者器。

本轮独立 checker 首次在错误 M0 路径断言处真实 exit1；另一次在错误 I05 round4 指路处 exit1，均保原件。随后队列 descriptor 校验曾误把 decoded raw diff 的 bytes/SHA 当成 JSON carrier，真实 exit1 已留存并明确纠正为审者解释错误；两层身份都通过，没有将它误报为坏包。完成检查 exit0 只代表完成材料检查，报告仍 Fail。

## 分层结论与收尾

| 对象                                       | 本轮结论                                                   |
| ------------------------------------------ | ---------------------------------------------------------- |
| 主 2cf 完整源码材料、61f 六件过程与全差异  | 材料身份/完整性 Pass；不审产品实现正确性                   |
| 固定参考版本/测试/fixture/许可与八后继队列 | 字节保全/关系核验 Pass；原件指路 P2 待修，后继任务未冒已审 |
| 完整原验收、产品 runtime、指定双审与发布   | 未验证/未完成，不能给整体 Pass                             |
| 发审准备整体                               | **Fail：PKT-R1-P2-01、PKT-R1-P2-02 关闭前不得称就绪**      |

静态检查只用固定 Python 3.12 标准库和只读 Git；新 Markdown/JSON 仅按批准的本地 Prettier 显式 `--ignore-path /dev/null` 格式核验。完整 argv/cwd/exit/双流及结构检查见 proof、首失败和最终收据。HEAD、空 index、最终 status 与全部新文件 bytes/SHA 由 `independent-r1-final-receipt.json` 收口，自项以外部实际工具输出绑定。封存后停止写入，交根全文读取与总控预检。
