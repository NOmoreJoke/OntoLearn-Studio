# T06-S1 R2 流程补正（MiniMax Code M3.1-Flash / xhigh，2026-10-23）

本文件是**流程补正文**，不改写、不覆盖、不追认原报告。原报告 `docs/reviews/T06/round-2/minimax-m31flash.md`（36822 B / SHA-256 `18302fc1f3c267025b0a1435931792301c63140134a1dd03197587e0e1d22b6a`）及其原 out 证据保持原字节不动；原会话终答亦不改写。本补正文与原报告并存，**凡两者表述不一致，以本补正文的更正条目为准**。

审查者：MiniMax Code M3.1-Flash（xhigh，bypassPermissions 始终授权）。

---

## 0. 结论（先行）

1. **产品结论不变**：本独立 S1 范围（私有行为计划算法 + T09 固定输入只读适配）**通过（Pass）**，**0 项 P1、0 项 P2、4 项 P3**。独立流程审未提出任何针对产品实现的新 P1/P2，其 6 项要求全部落在**审查流程与报告表述**上。因此本补正**不推翻**原报告的产品裁决。

2. **原报告有 8 处事实/描述性表述须更正**（见第 3 节），其中 1 处是**要求未完成的实质缺口**：原 turn **未**读取完整 base→产品 diff（76 文件 patch 全文），冻结输入的该项要求在原 turn **未被程序事实证明**。本轮已补读并给出逐文件行段闭合账目（第 6 节）。**这是后续新事实，不回填原 turn**，原 turn 的完成状态按当时实际记录。

3. **原 turn 的首败记录不完整**：原报告第 9 节只登记 3 类；实际至少 **8 类**首败/未完成事件（含 2 次 `KeyError`、1 次口径性 `diff` exit 1、1 次过早 `grep` 返回 1、1 次 `IndexError`、1 次主动取消且 **child exit 未知**、1 次崩溃且**无结果 JSON**、1 次 7 FAILED exit 1）。全部在第 4 节按实际发生登记。

4. **独立流程审 6 项要求的处置**：**5 项全部接受**，**1 项部分接受**（第 2 节）。唯一不接受的是其"在 wrapper 内再 `_state` 成本可忽略"这一**未经测量的量化暗示**——事实是每次 setup 一次 O(facts) 的复杂度描述，"可忽略"是未测量的判断，不予采纳。

5. **P2-1 / P2-2 裁决维持并加限定**：P2-1 维持"所指向的可避免机制关闭"，但**限定为本次所测的精确输入族的观察，不外推生产**；P2-2 **维持 P2 容量风险，不关闭**；**Q5 / PRD 10.2 未批准任何规模、参考设备、时间、内存或磁盘阈值，因此不存在被违反的已批准验收线**；FR-600–604 父模块、完整 G.3、B-07/B-08、Q5 容量门与 T06 整体验收**保持开放**。

6. **本补正只写两处**：本文件，以及新目录 `out/minimax-r2-process-addendum-20261023/`（2 个新证据文件）。未改实现、测试、依赖、锁文件、配置、公共文件或 AGENTS；未切分支、未提交、未 push、未 PR；未运行被拒脚本；未重跑无变化且原证据完整的 check/139/probe/helper/测量/34 对抗。

---

## 1. 本补正的身份、依据与不变量

| 项 | 实际值 |
|---|---|
| 补正依据（官方附件全文） | `out/environment-prep/process-correction-20261023/own-process-correction-full-input.md`，**603 行 / 101720 B / SHA-256 `b82693f1a5cd90d41665d5fb2f0e8180eee2a0e787c1dda2e2cfac0ecb38fa38`**；与本方副本**逐字节一致** |
| 同目录支持文件（只读本方副本，未全局搜索） | `independent-process-review.md`（与附件内嵌块内容基本一致，仅尾部分隔差异）、`evidence-audit.json`（39026 B，**本轮全文读取**）、`reviewed-evidence-index.json`（12 条原件路径/bytes/SHA） |
| 工作树 / HEAD / base | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-s1-minimax-review-3be0397`，detached HEAD `3be0397faf03de6520c47bf7d86f3dc2fd004287`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`（本轮 `git rev-parse HEAD` 复核一致） |
| 候选 / 范围 / 原门 | **不变**。本补正不产生新候选、不改受审范围、不替代任何既有评审门 |
| 后续新事实原则 | 本轮补读所得一切均为**后续新事实**，**不得回填为原 turn 已执行**；原 turn 的完成状态按当时实际记录 |
| 独立过程审性质 | 它是对**本方原 turn 过程**的审计，不是另一指定模型的产品审查；本方**未读取**同轮另一模型（ZCode GLM-5.3）的本轮提示/会话/报告/意见 |

### 1.1 本轮明确未做、未读、未跑

- **未读**：同轮另一模型的当前提示、会话、报告与意见；`private/`；完整 system/header/thinking/auth/memory/llm-call 正文；unknown `.mimosa` 正文；别线（UI）历史块的模型意见正文（仅取类别/metadata）。
- **未跑**：任何被拒脚本（ZCode 四次 PreToolUse 拒绝所涉脚本一律未执行）；旧 131 秒基线；已无变化且原证据完整的 `npm run check` / 139 专项 / 九例 probe / helper / 测量 / 34 项对抗。
- **未写**：原报告、原 out 证据目录、receipt/脚本、已封原件；`out/reviewer-verify/` 未被覆盖或清空。

---

## 2. 独立流程审 6 项要求的逐项处置

### 2.1 ① 补记全部真实首败与纠正 —— **接受**

独立流程审指出原报告第 9 节的首败清单不完整。本方**已按自身工件逐条复核并接受**：原 turn 实际发生的未完成/失败事件见第 4 节，共 8 类，其中被原报告记错成员的是"首次完整跑出 7 项 FAIL"那一类（原报告拆 A4 为两项并**漏记 C15**）。

### 2.2 ② 精确更正 34 项分段与 B 段输入族/断言范围 —— **接受（已用本方工件独立复核，非照抄）**

本方直接读取本方工件核对：

- `out/reviewer-verify/adversarial-result.json`（8397 B / SHA `9572ff45ab90924041ab2b0ab9b737d265accd1ba8c825d0bd52d8d8d6972628`）记 `total=34`、`failed=0`、`crashes=[]`，并逐条列出 34 个 check 名称：**A1–A4（4）、B1–B2（2）、C1…C17 及其子项（28）**。原报告"**C 段：定向负例（23 项）**"不成立。
- `out/reviewer-verify/adversarial.py`（33126 B / SHA `424269a5c64e5a9b2c266ee7e4a9dae384ba7ed18518ae49f6097437ed67a979`）的 `random_request`（`:357–421`）证实 B 段实际输入族：`edits` 恒为 `[]`（`:367`）；事件 ID 为 `E{index}` 逐 index 唯一（`:362`），**无重复投递**；`trigger` 恒为 `{"event_type": "test"}`（`:416`）、`conditions` 恒为 `[{"op": "always"}]`（`:417`）；**仅 `enabled`（`:414`）与 `priority`（`:415`）随机**；typed 值集合为 `["a","b",1,True,False,1.0]`（`:380`），**无 `0`、无 `"x"`、无 `"雪"`**；add 值集合 `["t2","Z","X"]`（`:389`）；create initial 值集合 `["a","b","c"]`（`:400`）。
- B 段**无请求不变性断言**：`original = copy.deepcopy(req)`（`:448`）是**交给旧基线模块的第二份输入**（`:450`），不是不变性比较；请求不变性断言只存在于 C 段 `expect_error`（`:526–538`，`req == original`）。
- A 段 oracle 比较**仅为冲突对的 intent 序号对**（`:137–140`、`:178–181`、`:231–234`），不比较同一 create 多个 initial 的写值/槽位。
- B 段比较用 `canonical(...)`（`:459`、`:463`），即**规范化 JSON 相等**，不是任意 raw 字节相等；"全相等"只覆盖该 1,500 例输入族，**不是所有行为的全称证明**。

原报告相应表述的逐条更正见第 3 节 C-2 ~ C-6。

### 2.3 ③ 分清 native isError / 外壳 exit / 真实 child EXIT / 主动取消 / pipe-tail 裁流 —— **接受**

原报告"全部验证命令的完整 stdout/stderr 与真实 child exit 均保存在本方 `out/`"过宽。本轮建立五层退出码语义并逐条落到具体命令，见第 5 节。关键点：**主动取消的那次运行其 child exit 未知**，既不能记为通过也不能记为失败；**对抗脚本的 stdout 只保留 49 B 摘要**，不是完整 stdout。

### 2.4 ④ 补完 owned base→product diff 全文与 binary metadata —— **接受**

独立流程审指出的"完整 base→产品 diff 已读"在原 turn **未被程序事实证明**（其 `evidence-audit.json` 的 `diff_Read_requests` 字段独立记录：原 turn 的 diff 类 Read 仅 2 次，路径**均为** `out/reviewer-verify/planner-613-vs-3be0397.diff`，20608 B）。本方据此**承认原 turn 未完成该项**，并在本轮补读完成：

- 已逐行读完 **plain `git diff base product` 全文 24034 行 / 1215620 B / SHA-256 `fa879b62a675c9a6410e25b657f3d3dc195ce22bff4bfac6e26e3bed747bb397`**（本轮独立重算一致），落盘为 `out/minimax-r2-process-addendum-20261023/base-to-product-full-text.diff`。
- `--binary` 口径 **6075356 B / SHA-256 `569b98c2b6f16a18593fc3c3c8b17580f8df21672d04188549d7946cda9c916f`**（本轮独立重算一致），其中含 4 个 binary 文件的字面载荷；该载荷为二进制，**本轮未逐行读取**，只核总量 SHA 与各 blob 元数据（第 6.2 节）。
- 76 文件逐文件行段闭合表见第 6.3 节（76/76 行，无缺口）。

### 2.5 ⑤ 4 项 P3 按"现边界 / 未来风险"独立评估 —— **接受**

本方**不**因非阻断 P3 改动冻结候选，也**不**把未实施的未来改进写成已修。第 7 节对 4 项 P3 分别给出"现边界（当前是否可观察为缺陷）"与"未来风险（若边界变化会发生什么）"，并标注处置为"不改冻结候选"。

### 2.6 ⑥ P2-1 机制关闭与 P2-2 仍 P2 容量风险 / Q5 / 父门继续明确 —— **接受（附一处限定与一处拒绝）**

- **接受**：P2-1 维持"所指向的可避免机制关闭"的裁决；P2-2 **维持 P2 容量风险、不关闭**；Q5 与 PRD 10.2 未批准任何阈值，故**不存在被违反的已批准验收线**；父门保持开放。
- **接受其限定**：P2-1 的关闭结论**仅对本次所测的精确输入族成立**，**不外推生产**；不据此宣称任何生产速度、容量、倍数或正确性全称保证。
- **拒绝其量化暗示**：独立流程审称"在 wrapper 内再 `_state` 成本可忽略"。本方**不接受**该措辞：`_state` 对 facts 的校验是每次 setup 一次、复杂度与 facts 数成正比的 O(facts)；"可忽略"是**未经测量的判断**。原报告该处写"成本是每次适配器 setup 一次 O(facts)，可忽略"，本补正把"可忽略"改述为"**复杂度 O(facts)/每次 setup，未实测**"（见第 7 节 P3-1）。

---

## 3. 原报告须更正的事实条目（逐条）

下表 8 条均为**原报告的原表述与其正确表述**。原报告本身不动；本表为更正依据。

| 编号 | 原报告位置 | 原表述 | 更正 | 依据 |
|---|---|---|---|---|
| **C-1** | §3"完整读取范围"第 4 项 | 以"**完整 base→产品 diff**"为标题，称"我独立生成 `out/reviewer-verify/planner-613-vs-3be0397.diff`（旧 613 planner 与当前 planner 的逐行差分，207 插入 / 112 删除），并完整读取；另核 76 文件 diff 统计" | **该标题下所述的实为"单文件 planner 差分 + 76 文件统计"，不是 76 文件 patch 全文**。字面未谎报，但**置于"完整读取范围（全文，非摘要）"标题下，读者必然读成冻结输入要求的"读取完整 base→产品 diff"已满足**。该要求在原 turn **未被程序事实证明**（原 turn 的 diff 类 Read 仅 2 次，路径均为 planner 单文件差分）。本轮已补读完整 76 文件 patch 全文（24034 行 / 1215620 B），见第 6 节。**此为后续新事实，不回填原 turn。** | `evidence-audit.json` 的 `diff_Read_requests`（2 条，均 `planner-613-vs-3be0397.diff`）；本轮 `git diff` 两种口径独立重算 |
| **C-2** | §4.1 小标题 | "**C 段：定向负例（23 项，含我在本轮新增的自建用例）**" | **C 段不是 23 项**。34 项的真实分段为 **A = 4（A1–A4）、B = 2（B1/B2）、C = 28**。原报告 §4 表"34/34 全过"的总数正确，分段计数错误。 | `adversarial-result.json`：`total=34`、`failed=0`、`crashes=[]`，34 条 check 名称逐条枚举 |
| **C-3** | §4.1 B 段 | "1,500 例随机请求（随机 set/add/create/notify、随机 typed 值含 `False/0/1/1.0/"x"/"雪"`、随机 trigger/priority/enabled/conditions、随机事件编辑 set/add/remove/delete_object/declare/create、含重复事件投递）" | **随机覆盖面被写大了**。实际：B 段事件的 `edits` **恒为 `[]`**（无任何事件编辑）；事件 ID `E{index}` **唯一、无重复投递**；`trigger` **恒定** `{"event_type": "test"}`；`conditions` **恒定** `[{"op": "always"}]`；**仅 `enabled` 与 `priority` 随机**；typed 值集合为 `["a","b",1,True,False,1.0]`（**无 `0`、无 `"x"`、无 `"雪"`**）；add 值 `["t2","Z","X"]`；create initial 值 `["a","b","c"]`。 | `adversarial.py:357–421` |
| **C-4** | §4.1 B 段末 | "…；并断言调用方请求未被修改。" | **B 段没有请求不变性断言**。`original = copy.deepcopy(req)` 是**交给旧基线模块的第二份输入**，不是不变性比较。请求不变性断言只存在于 **C 段 `expect_error`**（`req == original`），且仅在证据含 `stage` 的分支附加 `committed=false`/无 candidate/无 consumption/`executed_actions` 为空。 | `adversarial.py:448–450`、`:526–538` |
| **C-5** | §4.1 A 段 | "A1 单槽穷举…**271,453 例，不一致 0**"、A4"均与 oracle 一致"（作为"首次冲突对等价性"证据） | 比较**仅为冲突对的 intent 序号对**（`(expected[0]["intent"], expected[1]["intent"])`），**不比较同一 create 多个 initial 的写值/槽位**。"首次冲突对等价"在 intent 对粒度上成立；若被读成"写值/槽位全等价"则过宽。 | `adversarial.py:137–140`、`:178–181`、`:231–234` |
| **C-6** | §0、§4.1 B 段、§7.1 第 1 点 | "与冻结 613 基线**完整输出或完整 reason/location/evidence 逐字节相等**"、"完整输出/证据逐字节相等" | 实际比较为 **canonical 后的 JSON 相等**（`canonical(new_out[1]) != canonical(old_out[1])`），**不是任意 raw 字节相等**；且"全相等"**只覆盖该 1,500 例固定种子输入族**，**不是所有行为的全称证明**。plan 侧比较完整 plan，error 侧比较完整 `reason/location/evidence`（802 plan + 698 error，合计 1500）。 | `adversarial.py:459`、`:463`；`adversarial-result.json` 的 B2 detail `plan=802 error=698 mismatches=[]` |
| **C-7** | §9 末条 | "全部验证命令的完整 stdout/stderr 与真实 child exit 均保存在本方 `out/`；未用展示用 `tail` 或管道状态替代真实退出码。" | **过宽**。实际：`adversarial.stdout.log` 仅 **49 B** 摘要行；`pytest-behavior-reviewer.log` **187 B**；`npm-check-reviewer.log` **5724 B**（另 final **5723 B**）；`measure-current.stdout.log` **3540 B**；两个边界探针 stdout 197 B / 276 B。**并非每条命令的完整 stdout/stderr 都单独保全**；且**主动取消**那次运行的 **child exit 未知**，不属"真实 child exit 均保存"。原句后半"未用展示用 tail 或管道状态替代真实退出码"就我方自身命令而言成立，但**不能推广到未保全完整 stdout 的那些命令**。 | `out/` 实测字节数；第 5 节退出码分层表 |
| **C-8** | §9 第 2 条 | "首次完整跑出 **7 项 FAIL**：A4a/A4b/C9a/C9b/C9c/C12/C14" | **成员记错**。真实 7 个 FAILED 为 **A4（整体一项，其 detail 内含 A4a/A4b/A4c 三个子情形）/ C9a / C9b / C9c / C12 / C14 / C15**。原表述把 A4 拆成两项（A4a/A4b）且**漏记 C15**（`C15 consumption scope mismatch rejected`）。个数 7 不变，成员不同。 | `evidence-audit.json` 的 `seven_fail_group_output`（7 条 FAILED 原文）；`adversarial-result.json` 现存 C15 check 名 |

---

## 4. 原 turn 真实首败与未完成事件全量登记

以下均为**原 turn 实际发生**的未完成/失败事件，逐条按实际记录，不写成首轮全绿。**其中没有任何一条指向产品实现缺陷**；除 C-8 那条的 7 个 FAILED 外，其余均为本方脚本/提取/口径问题。

| # | 事件 | 真实终态 | 性质 | 纠正 |
|---|---|---|---|---|
| F-1 | 提取 owner 证据时两次 `KeyError`：一次取 `verification.failureHistory`，一次取某份 owner cost receipt 的 `result` | Python 异常，命令非零退出，**无产品调用** | 本方临时提取脚本缺陷 | 自验：`validation-3be0397.json` 的 `verification.failureHistory` 是**246 字符的字符串摘要**，不是结构化子表；owner cost receipt 的 `result` 键并非每件都存在。改为按实际类型读取后成功。 |
| F-2 | 作者脚本复现件与受审 `counterexamples.json` 的 raw `diff` | **exit 1** | **比较口径差异，不是语义差异** | 双方全量解析后，9 个 case 的 request/expected 规范 SHA 全等；差异仅在数组展开/收拢的排版。规范化 JSON 完全相等（`f84c378881ab56646e1e3cf88c7ca7c2b6e8a3e18e486b8841c657057390d20d`）。原报告已按规范化口径表述，**须在此补记该 exit 1 的存在**。 |
| F-3 | `npm run check` 尚未产出完整日志时过早 `grep EXIT` | **grep 返回 1** | **误读风险，非失败** | grep 无匹配返回 1，不能读作 check 失败。实际 `npm run check` **exit 0**，日志内含真实 `EXIT=0` 与 `All checks passed!`（`out/npm-check-reviewer.log`，5724 B）。 |
| F-4 | `adversarial.py` 首次运行 | **exit 1（`IndexError`）** | 本方脚本缺陷 | 穷举组合维度写错（`itertools.product` 未分块）。修正后重跑。 |
| F-5 | A2 组合空间达 72⁶ | **主动取消；child exit 未知** | 本方主动中止 | **既不能记为通过，也不能记为产品失败**；该次无终态退出码，无结果 JSON。已改为限定规模的穷举（14,425 例）。 |
| F-6 | 后继运行：`C3b`/`C4` FAIL，且 `C8` 的 `action_limit` 分支崩溃 | **exit 1，无结果 JSON** | 本方脚本缺陷 | `action_limit` 分支未捕获预期异常类型导致崩溃；`C3b`/`C4` 的期望值口径与实现不符。修正后重跑。 |
| F-7 | 首次完整跑出 7 项 FAILED | **exit 1** | 本方预期错误（逐条复核后确认实现符合旧语义与现合同） | 真实成员见 C-8：A4（整体）、C9a、C9b、C9c、C12、C14、C15。逐条复核后确认**全部是我方预期写错**（例如 A4a 旧语义报 (1,2) 而非我最初写的 (0,2)；C9a/b/c 我把"整请求级门无 `stage`"错误套用了计划阶段断言；C12 我未真正传入矛盾的推导事实；C14 我漏算通知记录进入 diff；C15 我漏写该负例）。 |
| F-8 | 我的 `expect_error` 辅助函数最初把整请求级错误误判为失败 | 断言口径错误 | 本方辅助函数缺陷 | 改为按证据字段是否含 `stage` 区分（`adversarial.py:532–538`）。 |

另有**一次报告改写**：同一 turn 内曾存在报告初稿 36775 B / SHA `257935efd00b32983c6c08d5218bd4fb7c5045a1d58e485d89a00150a0e5bd68`，最终封存版为 36822 B / SHA `18302fc1…`。**封存版为准**；初稿保留在证据留档中，不作为结论来源。

---

## 5. 退出码与输出保全的五层语义（③ 的落实）

| 层 | 含义 | 本轮/原 turn 的具体实例与实际终态 |
|---|---|---|
| **native `isError`** | 工具调用自身的成功/失败标志 | 原 turn 的工具行；独立流程审据以逐条复原 |
| **外壳 exit** | 承载命令的包装进程退出码 | `bash -c` / 工具外壳；不可与被测进程混淆 |
| **真实 child EXIT** | 被测进程自身退出码 | `uv run --frozen pytest packages/engine/tests/test_behavior_*.py -q` → **exit 0，139 passed**（`out/pytest-behavior-reviewer.log` 187 B）；`npm run check` → **exit 0**（`out/npm-check-reviewer.log` 5724 B / `…-final.log` 5723 B）；九例 T09 probe → **exit 0**，输出 JSON 77789 B / SHA `d18e5059394b11f6f783d4247c8e4f074a102a58d5ef3d48c3272fc248339c9e`；`adversarial.py` **终态 exit 0（34/34）** |
| **主动取消** | 我方主动中止，**无终态退出码** | F-5（A2 组合过大）。**child exit 未知**，不计入通过也不计入失败 |
| **pipe-tail 裁流** | 管道只保留尾部输出，管道前完整 stdout 未保全 | 共同历史 owner 链中的 122 专项命令自身 `tail`（其 179 B 原返回完整，但**未保留管道前全 stdout**）；就我方自身命令：`adversarial.stdout.log` 仅 49 B 摘要，**不是完整 stdout**；`npm run check` 因重定向落盘而保全较完整（5724 B） |

**结论**：原报告"全部验证命令的完整 stdout/stderr 与真实 child exit 均保存在本方 `out/`"**不成立**（C-7）。准确表述为：**已终态的真实 child exit（139 专项 / npm check / 九例 probe / 对抗脚本终态）有明确记录**；**完整 stdout 并非逐条保全**；**取消的那次无终态退出码**。

---

## 6. 本轮真实新增读取与覆盖账目

### 6.1 新读取的输入与支持文件

| 文件 | 处置 |
|---|---|
| `own-process-correction-full-input.md` | **分段全文读**：1–120、121–235、236–335、336–455（后半为原冻结输入后缀，前轮已读同源内容）、456–603 |
| `independent-process-review.md` | 全文读 |
| `evidence-audit.json`（39026 B） | **本轮全文读**（673 行）：`sources13`（13 项读取方法与 read_calls）、`adversarial_final`（total 34 / failed 0 / section_counts A=4 B=2 C=28）、`seven_fail_group_output`（7 条 FAILED 原文）、`diff_Read_requests`（2 条，均 planner 单文件差分）、`verified_files`（97 项产物/脚本版本路径与 SHA）、`safety` 声明 |
| `reviewed-evidence-index.json` | 全文读（12 条原件路径/bytes/SHA） |

### 6.2 完整 diff 的两种口径与 binary metadata

| 口径 | 规模 | SHA-256 | 本轮处置 |
|---|---|---|---|
| plain `git diff base product` | **24034 行 / 1215620 B** | `fa879b62a675c9a6410e25b657f3d3dc195ce22bff4bfac6e26e3bed747bb397` | **逐行读完 24034/24034 行**；落盘 `out/minimax-r2-process-addendum-20261023/base-to-product-full-text.diff` |
| `git diff --binary base product` | **6075356 B** | `569b98c2b6f16a18593fc3c3c8b17580f8df21672d04188549d7946cda9c916f` | 独立重算一致；**含 4 个 binary 文件的字面载荷，未逐行读取**（二进制），只核总量 SHA 与下列各 blob 元数据 |

4 个 binary 文件的 Git blob 元数据（`git rev-parse <product>:<path>` / `git cat-file -s` / `git cat-file blob | shasum -a 256`，三者交叉一致）：

| 文件 | blob | bytes | SHA-256 |
|---|---|---|---|
| `evidence/minimax-original-tool-evidence-20261022.tar.gz` | `8bf6ef3be905ab5b98d688a437f4550a8a0ffc9a` | 629906 | `c68ba2b7663b2533f87e729030e04e5292e7533cd503a90560ac32db001298bc` |
| `evidence/ui-original-artifacts-20261021.tar.gz` | `83b0de3bcbf5b2756c5dc7af1fa0f482fc9400a4` | 2232198 | `a51bfec8089f9a7db1578ebbfcc3570e1591beda51b956f2d8bf165a0cfab433` |
| `evidence/ui-session-tool-records-20261021.tar.gz` | `b4e028cdf5fa88e057f2a8dae0c7b9f205258539` | 6698 | `06d2e8636bbef29c6bb131bb3605c4f15e679d784137a2bffec5e58d472f5a3b` |
| `evidence/zcode-original-tool-evidence-20261022.tar.gz` | `834afab3e4d0584216162d71550391202184446a` | 918318 | `32c7b83753b572d085ce0703208e2f82f587c05d695cbd3509cb16234cb330c4` |

### 6.3 76 文件逐文件行段闭合覆盖表（76/76，无缺口）

**读取方式图例**：
`L` = 本轮逐行读原文行；`L*` = 前轮已逐行读（本轮复核区间）；`P` = **全量结构解析 + 逐成员字节校验**（非逐行 dump，方法差异在下方显式声明）；`B` = 二进制，仅 Git blob 元数据；`M` = 别线历史块，仅类别/metadata。

| # | 文件 | diff 行段 | 行数 | 方式 |
|---|---|---|---|---|
| 1 | `docs/iterations/T06/interface.md` | 1–62 | 62 | `L*` |
| 2 | `docs/iterations/T06/probe_t09_baselines.py` | 63–291 | 229 | `L*` |
| 3 | `docs/iterations/T06/t09-adaptation.md` | 292–332 | 41 | `L*` |
| 4 | `docs/reviews/T06/baseline-compatibility-audit.md` | 333–355 | 23 | `L` |
| 5 | `docs/reviews/T06/blocked-audit.md` | 356–391 | 36 | `L` |
| 6 | `docs/reviews/T06/evidence/minimax-original-facts-and-differences-20261022.json` | 392–575 | 184 | `L` |
| 7 | `docs/reviews/T06/evidence/minimax-original-tool-evidence-20261022.tar.gz` | 576–579 | 4 | `B` |
| 8 | `docs/reviews/T06/evidence/minimax-original-tool-evidence-readback-20261022.json` | 580–1518 | 939 | `P`（184 成员逐字节校验）+ 头尾逐行 |
| 9 | `docs/reviews/T06/evidence/t09-candidate-probe.json` | 1519–3652 | 2134 | `P`（9 cases 全量结构解析，canonical SHA `0e6d1a210b593c9689612eb56b58ae3ff98a1d4a84ee83dec97fb42c451dbd66`） |
| 10 | `docs/reviews/T06/evidence/ui-571b4d6-negative-probes.mjs` | 3653–3690 | 38 | `L`（工具脚本，非模型意见） |
| 11 | `docs/reviews/T06/evidence/ui-archive-20261021.md` | 3691–3716 | 26 | `L`（归档 metadata） |
| 12 | `docs/reviews/T06/evidence/ui-archive-index-20261021.json` | 3717–3889 | 173 | `L`（归档 metadata） |
| 13 | `docs/reviews/T06/evidence/ui-original-artifacts-20261021.tar.gz` | 3890–3893 | 4 | `B` |
| 14 | `docs/reviews/T06/evidence/ui-session-tool-records-20261021.tar.gz` | 3894–3897 | 4 | `B` |
| 15 | `docs/reviews/T06/evidence/ui-validation-da37709.json` | 3898–3993 | 96 | `L`（UI 线验证 metadata） |
| 16 | `docs/reviews/T06/evidence/validation-61396a5.json` | 3994–4165 | 172 | `L` |
| 17 | `docs/reviews/T06/evidence/validation-e81cfc9.json` | 4166–4248 | 83 | `L` |
| 18 | `docs/reviews/T06/evidence/validation.json` | 4249–4334 | 86 | `L` |
| 19 | `docs/reviews/T06/evidence/zcode-original-tool-evidence-20261022.tar.gz` | 4335–4338 | 4 | `B` |
| 20 | `docs/reviews/T06/evidence/zcode-original-tool-evidence-readback-20261022.json` | 4339–6550 | 2212 | `P`（439 成员逐字节校验） |
| 21 | `docs/reviews/T06/external-review-backlog-20261022.json` | 6551–6820 | 270 | `L` |
| 22 | `docs/reviews/T06/external-review-backlog-20261022.md` | 6821–6843 | 23 | `L` |
| 23 | `docs/reviews/T06/local-review-1.md` | 6844–6873 | 30 | `L*` |
| 24 | `docs/reviews/T06/local-review-2.md` | 6874–6906 | 33 | `L*` |
| 25 | `docs/reviews/T06/local-review-3.md` | 6907–6941 | 35 | `L*` |
| 26 | `docs/reviews/T06/local-review-4.md` | 6942–6971 | 30 | `L*` |
| 27 | `docs/reviews/T06/local-review-5.md` | 6972–6993 | 22 | `L*` |
| 28 | `docs/reviews/T06/local-review-6.md` | 6994–7020 | 27 | `L*` |
| 29 | `docs/reviews/T06/operating-policy-ownership-update.md` | 7021–7065 | 45 | `L` |
| 30 | `docs/reviews/T06/review-readiness.md` | 7066–7117 | 52 | `L` |
| 31 | `docs/reviews/T06/round-1/desktop-approval-receipt.json` | 7118–7154 | 37 | `L` |
| 32 | `docs/reviews/T06/round-1/dispatch-addendum-20261022.md` | 7155–7175 | 21 | `L` |
| 33 | `docs/reviews/T06/round-1/dispatch-entry-check.json` | 7176–7211 | 36 | `L` |
| 34 | `docs/reviews/T06/round-1/dispatch-progress-20261022.json` | 7212–7336 | 125 | `L` |
| 35 | `docs/reviews/T06/round-1/frozen-inputs.json` | 7337–7362 | 26 | `L` |
| 36 | `docs/reviews/T06/round-1/minimax-completion-receipt-20261022.json` | 7363–7418 | 56 | `L` |
| 37 | `docs/reviews/T06/round-1/minimax-m31flash-dispatch-20261022.md` | 7419–7491 | 73 | `L` |
| 38 | `docs/reviews/T06/round-1/minimax-m31flash-input.md` | 7492–7547 | 56 | `L` |
| 39 | `docs/reviews/T06/round-1/minimax-m31flash.md` | 7548–7881 | 334 | `L*` |
| 40 | `docs/reviews/T06/round-1/minimax-owner-audit-20261022.md` | 7882–7911 | 30 | `L*` |
| 41 | `docs/reviews/T06/round-1/minimax-start-receipt-20261022.json` | 7912–8012 | 101 | `L` |
| 42 | `docs/reviews/T06/round-1/resource-remediation-independent-review-20261022.md` | 8013–8182 | 170 | `L*` |
| 43 | `docs/reviews/T06/round-1/resource-remediation-plan-20261022.md` | 8183–8223 | 41 | `L*` |
| 44 | `docs/reviews/T06/round-1/zcode-cli-login-readiness-20261022.json` | 8224–8304 | 81 | `L` |
| 45 | `docs/reviews/T06/round-1/zcode-completion-receipt-20261022.json` | 8305–8599 | 295 | `L` |
| 46 | `docs/reviews/T06/round-1/zcode-desktop-start-receipt-20261022.json` | 8600–8698 | 99 | `L` |
| 47 | `docs/reviews/T06/round-1/zcode-glm53-desktop-dispatch-20261022.md` | 8699–8779 | 81 | `L` |
| 48 | `docs/reviews/T06/round-1/zcode-glm53-dispatch-20261022.md` | 8780–8852 | 73 | `L` |
| 49 | `docs/reviews/T06/round-1/zcode-glm53-input.md` | 8853–8908 | 56 | `L` |
| 50 | `docs/reviews/T06/round-1/zcode-glm53-process-addendum-20261022.md` | 8909–8971 | 63 | `L*` |
| 51 | `docs/reviews/T06/round-1/zcode-glm53.md` | 8972–9104 | 133 | `L*` |
| 52 | `docs/reviews/T06/round-1/zcode-owner-audit-20261022.md` | 9105–9150 | 46 | `L*` |
| 53 | `docs/reviews/T06/round-1/zcode-process-correction-request-20261022.md` | 9151–9176 | 26 | `L` |
| 54 | `docs/reviews/T06/status.md` | 9177–9339 | 163 | `L*` |
| 55 | `docs/reviews/T06/ui-integration-handoff.md` | 9340–9367 | 28 | `L` |
| 56 | `docs/reviews/T06/ui-local-review-1.md` | 9368–9427 | 60 | `M`（仅标题与结论行作类别/metadata） |
| 57 | `docs/reviews/T06/ui-local-review-2.md` | 9428–9487 | 60 | `M`（仅类别/metadata） |
| 58 | `docs/reviews/T06/ui-round-1/dispatch-preflight.json` | 9488–10193 | 706 | `M` |
| 59 | `docs/reviews/T06/ui-round-1/minimax-m31flash-dispatch-20261022.md` | 10194–10370 | 177 | `M` |
| 60 | `docs/reviews/T06/ui-round-1/minimax-m31flash-input.md` | 10371–10494 | 124 | `M` |
| 61 | `docs/reviews/T06/ui-round-1/minimax-start-receipt-20261022.json` | 10495–10533 | 39 | `M` |
| 62 | `docs/reviews/T06/ui-round-1/owner-readback-20261022.json` | 10534–10573 | 40 | `M` |
| 63 | `docs/reviews/T06/ui-round-1/prepared-environments.json` | 10574–12109 | 1536 | `M` |
| 64 | `docs/reviews/T06/ui-round-1/zcode-glm53-dispatch-20261022.md` | 12110–12286 | 177 | `M` |
| 65 | `docs/reviews/T06/ui-round-1/zcode-glm53-input.md` | 12287–12410 | 124 | `M` |
| 66 | `docs/reviews/T06/ui-round-1/zcode-start-receipt-20261022.json` | 12411–12449 | 39 | `M` |
| 67 | `packages/engine/src/ontolearn_engine/behavior/__init__.py` | 12450–12460 | 11 | `L*` |
| 68 | `packages/engine/src/ontolearn_engine/behavior/baseline_adapter.py` | 12461–13049 | 589 | `L*` |
| 69 | `packages/engine/src/ontolearn_engine/behavior/planner.py` | 13050–14039 | 990 | `L*` |
| 70 | `packages/engine/tests/test_behavior_baseline_adapter.py` | 14040–14395 | 356 | `L*` |
| 71 | `packages/engine/tests/test_behavior_creation.py` | 14396–14562 | 167 | `L*` |
| 72 | `packages/engine/tests/test_behavior_failures.py` | 14563–14895 | 333 | `L*` |
| 73 | `packages/engine/tests/test_behavior_planner.py` | 14896–15390 | 495 | `L*` |
| 74 | `packages/engine/tests/test_behavior_resource_equivalence.py` | 15391–15713 | 323 | `L*` |
| 75 | `tests/fixtures/behavior/build_corpus.py` | 15714–16165 | 452 | `L*` |
| 76 | `tests/fixtures/behavior/counterexamples.json` | 16166–24034 | 7869 | `P`（全量结构解析 + 9 case 规范 SHA 比对；**未逐行读 7869 行原文**） |

**闭合性**：76 文件全部登记，行段首尾相接、无重叠、无缺口（1–24034）。

### 6.4 方法差异的显式声明（不冒充逐行读）

三个大型证据 JSON 与 `counterexamples.json` 采用**全量结构解析 + 逐成员字节校验**，**不是**逐行 dump：

| 证据 | 规模 | 本轮方法 | 结果 |
|---|---|---|---|
| `minimax-original-tool-evidence-readback-20261022.json` | 34623 B / **184 成员** | 全量结构解析 + 逐成员字节校验 | **184/184 逐字节相等**；归档 SHA/bytes 与声明一致（`c68ba2b7…298bc` / 629906 B） |
| `zcode-original-tool-evidence-readback-20261022.json` | 98570 B / **439 成员** | 同上 | **439/439 逐字节相等**；归档 `32c7b837…330c4` / 918318 B |
| `t09-candidate-probe.json` | 77195 B / 9 cases | 全量结构解析 | canonical SHA `0e6d1a21…dbd66`；raw `7a868b4d…8595` |
| `counterexamples.json` | 213042 B | 全量解析 + 作者脚本复现规范比对 | 9 case 的 request/expected 规范 SHA 全等（见 F-2） |

**归档只读校验**：仅做字节与哈希核对，**未执行任何归档内脚本**。UI 的两个归档（`ui-original-artifacts-20261021.tar.gz` 2232198 B、`ui-session-tool-records-20261021.tar.gz` 6698 B）**仅登记 metadata**，未展开成员。

---

## 7. 4 项 P3：现边界 vs 未来风险（⑤ 的落实）

**统一处置原则**：4 项均**不阻断**本范围，**均不改冻结候选**；未来改进只登记为建议，**不得写成已修**。

### P3-1 `_edit` 兼容包装器对未校验状态静默去重

- **现边界**：**当前不可达，无可观察缺陷**。唯一调用方为 `baseline_adapter.adapt_case`，其状态来自 `model_state()`，已由 `_state()` 校验（`baseline_adapter.py:211`）。本候选无可达路径触发该行为。
- **未来风险**：若新增调用方或适配器改动传入未校验状态，`_Workspace` 的字典键索引会把 `_state()` 本会拒绝的重复事实"修好"并静默丢弃，而非按 `duplicate_fact` 拒绝 —— 属"验证先于索引"不变量的**潜在回归入口**。
- **未来改进（未实施）**：在 `_edit` 内先调用 `_state(state, schema, classes)`，或在 docstring 中把"传入状态必须已通过 `_state`"写成可执行断言。
- **本补正对成本的更正**：原报告写"成本是每次适配器 setup 一次 O(facts)，**可忽略**"。本补正把"可忽略"改为"**复杂度 O(facts)/每次 setup，未实测**"——"可忽略"是未经测量的判断，**不采纳**（含独立流程审同款措辞）。

### P3-2 失败的 `create` 编辑的部分效果未列入 `discarded_event_edits`

- **现边界**：**符合现合同**。`interface.md:50` 只承诺"事件准备失败的**先前编辑**标为 `discarded_event_edits`"，失败编辑本身不属"先前编辑"；该列表只收录先前成功编辑（`planner.py:441`）。实测该次失败：对象已登记且一条 initial 已写入工作区，随后整体丢弃，**无 candidate、无新 consumption、输入未改**（`input unchanged: True`）。
- **未来风险**：读者可由 `edit_index` + `initial_index` 定位失败点，但**无法从证据重建"失败前已临时创建对象并写入一条事实"**；若后续需要严格区分"丢弃模拟"与"正式执行"，该信息缺口会显现。
- **未来改进（未实施）**：在失败证据中一并记录失败编辑本身及其部分效果摘要（例如 `discarded_event_edits` 增加带 `partial_effect` 的记录或新增独立字段）。属诊断增强，不改语义。

### P3-3 `before` 是规范化后的行为前状态

- **现边界**：**符合现合同，无正确性影响**。`planner.py:358` 的 `_state` 会就地排序规范化 `objects`/`facts`；`interface.md:28` 要求输出保持规范排序，diff 基线也建立在同一规范化状态上。既有等价断言之所以成立，是因为私有 fixture 本身已排序。
- **未来风险**：若调用方以"提交状态的字节副本"理解 `before`，在**未排序输入**下会观察到列表顺序差异 —— 属**接口文档表述**风险，不是实现风险。
- **未来改进（未实施）**：在 `interface.md:34` 补一句"`before` 为规范化后的行为前状态（对象与事实按规范序），不是提交状态的字节副本"。

### P3-4 整请求级形状/有限 JSON 失败没有 `stage`

- **现边界**：**整请求被拒是安全的** —— 无输入修改、无部分状态、无 candidate、无新 consumption。实测三类：未知顶层字段 → `invalid_shape / input`；事件载荷 `NaN` → `invalid_json / input`；孤立代理项 → `invalid_json / input`；三者 evidence 为空字典。`interface.md:48/54` 列举的阶段集合（`event_preparation`、`definition_validation`、`condition_evaluation`、`intent_limit`、`intent_validation`、`conflict_check`、`candidate_simulation`、`event_validation`）**确不含整请求级门**。
- **未来风险**：诊断上无法区分"请求形状错误"与"某具体字段错误"，且该层缺 `committed=false` 语义位。**扩展 `stage` 或 `committed` 属接口语义变更，需版本决定**，不在本候选擅改。
- **未来改进（未实施，二选一）**：在 `interface.md` 补写整请求级门的位置约定（`location=input`、无阶段），或给该层一个固定阶段名与 `committed=false`。

---

## 8. P2-1 / P2-2 裁决维持与限定（⑥ 的落实）

### 8.1 P2-1：所指向的可避免机制关闭 —— **维持，但限定为精确输入族的观察**

**维持的裁决**：本候选对应 `planner.py:167–288`（编辑索引）、`:688–726`（按槽冲突搜索）、`:781–789`（推导事实键集一次生成）、`:927–955`（增量 effect 与边界排序）的可避免重复工作**已消除**，且**未改变任何可观察语义**。

**限定的范围（本轮明确接受独立流程审的限定）**：该结论**仅对本次所测的精确输入族成立**，即：

- A 段穷举族：单槽长度 0–5（271,453 例）、双槽长度 0–3（14,425 例）、随机 40,000 例；
- B 段固定种子族：1,500 例（`random.Random(2026102207)`，802 plan + 698 error）；
- 规模族：creates 200/400/800、800 create × 10 个不同单值属性、1000×1000 零动作矩阵。

**不外推**：**不**据此宣称任何生产速度、容量、倍数、并发或正确性全称保证。测量是本机（macOS-27.0.1-arm64、Python 3.12.12）上该精确合成输入的一次测量，未控制其他桌面负载，**不是生产指标**。严重度事实保留；"成本被优化掉"的表述不采用。

### 8.2 P2-2：完整 B×E 决定输出 —— **维持 P2 容量风险，不关闭**

- **合法反例仍成立**：1000 个不匹配行为 × 1000 个接受事件 = **零动作、1,000,000 条完整决定**。源动作上限不限制这些记录（`interface.md:28` 明写"源动作 1000 不是事实量、字段量或字节量上限"），**不能**被称为绕过动作限额。
- **本方独立实测**（`out/reviewer-verify/measure-current.json`）：traced peak **340,522,087 B**、wall **10.184 s**；owner 同口径 340,522,343 B / 11.710 s；旧 613 为 345,860,759 B / 11.622 s。**成本与旧候选同量级，本候选未使其变差**（峰值略降约 5.3 MB / 1.5%），但 **Ω(BE) 下界未变**。traced peak 是 **tracemalloc 跟踪的 Python 分配峰值，不是 RSS**；墙钟测量开启了跟踪，**不是**无跟踪常规耗时。
- **是否阻断本范围**：**当前私有 S1 范围内不阻断**，理由为——(a) 现合同要求完整决定集合且明写"不截断或分页"（`interface.md:28`），而 **PRD Q5 / 10.2 未批准任何规模、参考设备、时间、内存或磁盘阈值，因此不存在被违反的已批准验收线**；(b) 成本来自输出合同本身的 Ω(BE) 材料化，不是本候选引入的实现缺陷，本候选也未使其变差；(c) 该模块目前只是显式调用的私有纯函数，无公共注册、无 Store、无真实运行、无并发与端到端持久化路径，**实际容量主张尚不存在可被违反的正式对象**。
- **同时明确不成立的**：不能据此宣称"适合生产规模"、"取消可响应"、"内存/RSS 预算合格"、"同事务序列化/持久化可靠"。**Q5 的规模/设备/时间/内存线仍未批准**，正式容量门与父模块验收**保持开放**。本方**没有**替 Q5 填任何默认答案，也**没有**用"装配前再说"代替本轮判断。

---

## 9. 未验事项与本补正明确不做的事

**未验（不得据本补正文视为通过）**：真实推理服务接线与真实推导（当前推导为 **MANUAL GOLD**，`product_runtime=not-executed`、`formal_acceptance=false`，`expected` 不代表实际 Store payload）· 通用 RDF codec 与附录 C 完整 literal 语义 · Store 原子轮次提交、回滚、取消、迟到投递与恢复（`Store.commit` 未接入）· 完整 E.2/G.3 轮次正式验收、资源 B-07 与轮末推理/指标 · Agent B-08 真实工具失败表达 · 公共业务方法/受限错误映射/权限/取消/分页与轨迹交接 · UI 正式接线（另树 `T06-behavior-ui`，本方未读取其模型意见）· 公共注册 / IPC 暴露 · 设备规模、并发、RSS、端到端持久化容量与 **Q5** · GUI / native 两 OS / Electron / e2e / HMR / Keychain / 模型 API / 密钥 / 新增支付 · 打包（`package:dir`）、CI、远端核验、push/PR/正常合并/生产 · 指定审查过程门（ZCode 四次 PreToolUse 拒绝、首 stdin 20PASS/2FAIL/exit1、修正 5PASS、合计 27 条计数等）仍归总控/指定流程裁定。

**本补正明确不做**：不修改实现、测试、依赖、锁文件、配置、公共文件或 AGENTS；不切分支、不提交、不推送、不开 PR；不写入原开发树 `.worktrees/T06-behavior`；不读取同轮另一模型的提示/会话/报告/意见；不执行任何被拒脚本或归档内脚本；不重跑无变化且原证据完整的 check/139/probe/helper/测量/34 对抗；不改写原报告、原 out 证据、原会话终答；不把未实施的未来改进写成已修；不把后续新事实回填为原 turn 已执行。

---

## 10. 当前产品与流程结论

1. **产品结论**：本独立 S1 范围（私有行为计划算法 + T09 固定输入只读适配）**通过（Pass），0 项 P1、0 项 P2、4 项 P3**。独立流程审提出的 6 项要求**未产生任何新的产品缺陷**，因此本补正**不推翻**原报告的产品裁决。
2. **原报告更正**：第 3 节 8 条（C-1 ~ C-8）为**唯一**需要更正的内容；其中 C-1 是**要求未完成的实质缺口**，其余 7 条为描述性/计数/口径偏差，**均不影响原报告的结论方向**。
3. **历史问题处置不变**：LR1/LR3/LR5 全部 P1/P2 关闭且未回归；Round-1 MiniMax 2×P2 按第 8 节分别裁决；4×P3 关闭为合同已明确；Round-1 ZCode 2×P3 已在本候选实施、关闭；1×信息项确认为有意行为。
4. **父门与 Q5**：**不关闭** FR-600–604 父模块、完整 G.3 轮次、B-07/B-08、**Q5 容量门**或 T06 整体验收。
5. **流程结论**：原 turn 在"读取完整 base→产品 diff"一项上**未达要求**，本轮已补读并闭合账目；该补读为**后续新事实**，**不追认**原 turn 已完成。本方原报告的其余过程事实（首败、34/34、139、npm check、九例 probe、规模实测）经本轮独立复核仍成立，除第 3、4 节所列更正外无变化。

---

## 11. 本轮写入与结束状态

**本轮只写两处**：

| 路径 | 说明 | 字节 / SHA-256 |
|---|---|---|
| `docs/reviews/T06/round-2/minimax-m31flash-process-addendum-20261023.md` | 本补正文 | 本文件；最终字节数与 SHA-256 由结束时的独立读回给出（自引用不可内嵌） |
| `out/minimax-r2-process-addendum-20261023/base-to-product-full-text.diff` | 完整 base→产品 plain diff 全文（24034 行） | 1215620 / `fa879b62a675c9a6410e25b657f3d3dc195ce22bff4bfac6e26e3bed747bb397` |
| `out/minimax-r2-process-addendum-20261023/large-evidence-full-parse.json` | 三个大型证据 JSON 的全量结构解析与逐成员字节校验结果 | 4775 / `42d97d4482e585d719a55cca4bd0048d4d00f80671c4f8c99f5ff2b129a4f33c` |

**保持原字节不动**：`docs/reviews/T06/round-2/minimax-m31flash.md`（36822 B / `18302fc1f3c267025b0a1435931792301c63140134a1dd03197587e0e1d22b6a`）、`out/reviewer-verify/` 全部工件、`out/pytest-behavior-reviewer.log`、`out/npm-check-reviewer.log`、`out/npm-check-reviewer-final.log`、`out/T06-REVIEWER-3be0397-probe.json`。

**结束状态**：工作树 detached HEAD 仍为 `3be0397faf03de6520c47bf7d86f3dc2fd004287`；受审 13 路径未改；`git status --porcelain` 仅 ` M AGENTS.md`（既有保护 dirty，未暂存、未还原）与本轮新增的 `docs/reviews/T06/round-2/`；未提交、未推送、未开 PR。

**本补正到此结束。** 原报告与原会话终答保持不变；后续处理以本补正文与原报告并存为准。
