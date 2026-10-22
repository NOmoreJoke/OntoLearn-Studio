# T03 mapping-S1 指定模型独立完整审查报告 — 续审第 1 轮（MiniMax Code / M3.1-Flash / xhigh）

- 报告写面：`build/review-session/reports/mapping-S1-minimax-followup-1-full-report.md`（本树授权写面）
- 前序报告：`build/review-session/reports/mapping-S1-minimax-full-report.md`（49079 B / SHA256 `827c8c1a9e026f503a40aa3df4e0cb2b0470e82d31b97c169421efb6e3ca928d`）——**原样保留，未改动、未回填**
- 本轮元数据：`build/review-session/metadata/task-followup-1.json`
- 本轮 raw（新建轮次）：`build/review-session/raw/review-m31flash-followup-1/`
- 前序 raw（保留）：`build/review-session/raw/review-m31flash-round1/`
- 本轮逐路径覆盖登记：`build/review-session/raw/review-m31flash-followup-1/path-coverage-register.json`（866 行全覆盖）
- 本报告未读取、未搜索、未推断另一指定模型（ZCode / GLM-5.3）本轮的任何任务、意见、进度、状态库、报告、raw 或 metadata。

---

## 0. 结论先行

**判定：T03-S1 私有映射服务候选 `30319412daf8ae4745987babf7bbed93c53b6b42` 在续审第 1 轮完成全范围独立审查，判定维持 Pass（附明确边界），并对前序报告的覆盖口径与包级缺口措辞作出两处更正。**

| 项 | 判定 |
| --- | --- |
| 阻断性缺陷 | **0 项**（未发现实现级阻断） |
| 前序 F-01—F-04 | **全部复核成立**，处置意见不变（见 §6） |
| 前序 F-05 / F-06 | **确认为验证观察（verification observation），不是待修缺陷**（见 §7） |
| 逐路径覆盖 | **866/866 全部登记**（173 engineering + 693 documentation）；标签按实际读取方式分 5 级，含 18 个未读二进制载荷与 1 个刻意未读文件（见 §4） |
| 本轮新增发现 | F-07 — F-11（低/信息级，均非阻断；见 §8） |
| 本轮新增证据 | **无新的执行证据**；因产品字节与 HEAD 完全未变，按「无变更不机械重测」未重跑 check/sources/package/probe（见 §3.3） |
| 未运行 | `npm run test:e2e`（GUI/native/focus 仍须待根协调窗口）、两 OS、签名安装、生产 |

### 0.1 两条必须分开的表述（对前序报告的统一更正）

前序报告在 §0 与 §10 同时出现了「唯一包级缺口已收口」与「形式缺口仍存续」两种表述。本续审把该缺口**拆为两个独立登记项**，二者不可互相抵消：

| 登记项 | 内容 | 本轮状态 |
| --- | --- | --- |
| **P1（已执行的固定包 probe）** | 11 组固定 CLI case 在**本树新构建的 303 候选包内二进制**上的执行证据 | ✅ **已关闭**（前序轮实测：exit 0、stdout 与冻结期望逐字节相同、11/11 case、额外参数拒绝精确、包内锁/许可证一致、引擎 SHA `5f40a565…`） |
| **P2（303 新增边界）** | 303 新增的**外部 WEBSERVICE 公式 / 外部 hyperlink 的 socket 零调用** 与 **CSV 文件/列/单格/行四类超限定位**，在**包内二进制**上的执行证据 | ⛔ **仍然开放** —— 这两类行为自始至终**只有源码级测试证据**，**从未在包内二进制执行过** |

因此：**不得**称「唯一包级缺口全关闭」；也**不得**称「包级缺口仍整体存续」。准确表述是：**P1 已关闭，P2 仍开放**。P2 的实质风险低（0ad→303 工程差异仅一个测试文件、包内引擎与 0ad 逐字节相同），但**形式缺口客观存在**，本轮不将其宣称为已通过。

前序报告 §0 的「补齐候选自述的唯一包级缺口」与 §10 的「唯一包级缺口已由本轮本树新包复跑收口」两处措辞，其「唯一」一词不准确——实际存在两个不同层级的缺口。本续审以本表为准；前序报告**原文保留不改**。

---

## 1. 本轮真实任务、模型与设置（均为实际读回，未伪填）

| 项 | 实际值 | 来源 |
| --- | --- | --- |
| 应用 | MiniMax Code（桌面） | `build/review-session/metadata/owner-ui-settings-followup-1.json` |
| 模型 | M3.1-Flash（订阅限免） | 同上 |
| 思考等级 | xhigh | 同上 |
| 权限模式 | 始终授权 / Full access（bypassPermissions） | 同上 |
| 权威性 | **原会话 `mvs_10d369cf314843fab6f3d0bc5e213dd6` 的正常续审**，非新任务 | 同上 `authority` 字段 |
| cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping-S1-minimax-review-3031941` | 同上 `cwd` 字段 + 本轮实测 `pwd` 一致 |
| 续审附件 | `mapping-S1-minimax-followup-1-input.md`，3457 B / 12 行 / SHA256 `d48e5e73bc6f02891cba9e5e325b91f88025b85fb5c029818b7ea041823fca50` | 收据记录 + 本轮实测 `wc -c` / `wc -l` / `shasum -a 256` **三值全部一致** |
| 新 turn ID | **收据记录为 `null`**，附注「short startup not yet submitted at receipt creation」 | 收据原文；**本轮不伪填** |
| 原生 task / session ID | `mvs_10d369cf314843fab6f3d0bc5e213dd6` | `build/review-session/metadata/owner-native-task-id.json`（owner 经原生 Session 菜单 Copy 读回） |
| 全局配置 / 全局日志 | 未读（`globalConfigurationOrLogsRead: false`） | `owner-native-task-id.json` |
| 另一模型本轮意见 | 未读、未搜索 | 本轮遵守 |

### 1.1 两个 turn 的终态分别保留（不合并、不覆盖）

| turn | 官方终态 | 说明 |
| --- | --- | --- |
| 原 turn `9c66220e-50d5-403a-b43b-d7bdb35de586` | **failed**（公开 error `UNKNOWN`，末 assistant stop 为 toolUse） | 该 turn **未成功完成**。其自判「有限 Pass」的报告**不等于**该 turn 成功。原始终态**原样保留**，本轮**未**回填、**未**改写、**未**追全局日志找原因 |
| 续审 turn（本轮） | **本轮完成全范围审查并落盘报告 + 元数据 + 逐路径登记** | 与上表分别记录；本轮不因上轮 failed 而 reset、不付费、不自动重放任何写入 |

> 说明：本轮是**正常续审**，不是对失败 turn 的重放。续审输入明确「不要覆盖/回填旧 failed 或追全局日志找原因」，本轮严格遵守：未查询任何全局表或日志来补身份或追错误原因。

---

## 2. 固定身份核验（本轮实测）

| 项 | 要求 | 本轮实测 | 结论 |
| --- | --- | --- | --- |
| 工作树 | 唯一物理树 | `pwd` = `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping-S1-minimax-review-3031941` | ✅ |
| HEAD | detached `0fb8e045ec776da6e8dc1b306c72212982114cd8` | `git rev-parse HEAD` 一致；`git symbolic-ref -q HEAD` 无输出（detached） | ✅ |
| 产品候选 | `30319412daf8ae4745987babf7bbed93c53b6b42` | `git cat-file -t` 确认存在 | ✅ |
| base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | 同上 | ✅ |
| 固定输入 | `mapping-S1-fixed-inputs.json` 241447 B / SHA `ddbeeb2177a5ca9a3f070f50db15239e12dab760c7f85f8bc58aab7c98476995` | 本轮复核存在且字节一致 | ✅ |
| 候选清单 | `candidate-manifest.json` 4301 B / SHA `60c52bd13dac43bb9685b5233db817118dda10341357794d9f27500f07301e6c` | 同上 | ✅ |
| 共享源 | `/Users/kyle/.../.worktrees/T03-mapping` ref `ed9cef968b17a1edefc0977b509906fb9f81a336` | 共享固定包 5 文件按该 ref 逐字节一致（前序轮实测） | ✅ |
| manifest blob | 866/866 与 HEAD 一致 | 前序轮实测 866/866 匹配；本轮 HEAD/tree/product OID 未变（§3.3） | ✅ |
| 工作树洁净 | 零修改 | `git status --porcelain` 末态仅 ` M AGENTS.md`（本轮前既有状态），无 staged、无 commit、无 push | ✅ |
| `.venv` 解释器 | 如实披露 | `.venv/bin/python` → `~/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12`（**符号链接到系统 CPython 3.12 基础解释器**，非自建解释器） | ✅ 已披露 |

### 2.1 共享固定包 5 文件按 ref 逐字节一致（前序轮实测，本轮未变更）

`candidate-manifest.json`、`mapping-S1-fixed-inputs.json`、`coverage-matrix.json`、`coverage-summary.md`、`historical-stage-inventory.md` —— 本树副本与共享源仓库 ref `ed9cef96…` 的对应 blob 逐字节一致。

---

## 3. 本轮实际执行的命令与结果

### 3.1 本轮实际执行的命令

本轮**未执行任何产品构建、测试或打包命令**。本轮执行的全部为只读核查与本方写面内的登记/报告生成：

| # | argv | 目的 | 结果 |
| --- | --- | --- | --- |
| 1 | `wc -c` / `wc -l` / `shasum -a 256` on 续审附件 | 附件完整性三值核对 | 3457 B / 12 行 / SHA `d48e5e73…` **三值一致** |
| 2 | `shasum -a 256` on 前序报告 | 确认前序报告未被改动 | 49079 B / SHA `827c8c1a…` **与前序声明完全一致** |
| 3 | `git rev-parse HEAD` / `git status --porcelain` / `git diff --name-only` / `git diff --cached` | 无变更核实与洁净核实 | 仅 ` M AGENTS.md`；无 staged、无 commit |
| 4 | `git cat-file -t` / `git ls-tree -rl HEAD` | 固定身份与 903 条 tracked 路径对账 | 903 = 866 manifest + 37 审查包文件 |
| 5 | `Read` / `cat` over 全部 64 个 T03 验收/失败/缺证原件 + 64 条 T03 目录文件 | 补齐「全部原验收/失败/缺证」的**实质**逐路径覆盖 | 全部实读（§4.2） |
| 6 | 7 个只读 `explore` 子代理（engine core 17 / engine tests 20 / desktop 22 / contracts+root+CI+scripts ~60 / 34 docs 驻留工具 / evidence I03 283 / evidence I01+I02+I04+其他 376） | 继承面实质逐路径审读并回传逐路径登记 | 7 个全部 succeeded，逐路径登记已取回 |
| 7 | `python3 build/review-session/scratch/build-register.py` | 生成本轮 866 行逐路径覆盖登记 | exit 0；**首次失败已原样保全**（§3.2） |

### 3.2 本轮唯一首次失败（保留，未覆盖）

```
### FIRST FAILURE of the follow-up-1 turn (reviewer-side tool defect, NOT a product defect)
### command: python3 build/review-session/scratch/build-register.py
### argv: ['python3','build/review-session/scratch/build-register.py']
### ---- original error output (verbatim) ----
Traceback (most recent call last):
  File ".../build/review-session/scratch/build-register.py", line 21, in <module>
    base = json.load(open(REG))
FileNotFoundError: [Errno 2] No such file or directory: '.../build/build/review-session/raw/review-m31flash-followup-1/path-coverage-register.json'
### ---- end original error output ----
### cause: ROOT computed with one dirname() level too few (build/build/...)
### fix: ROOT = dirname x4 instead of x3; no other logic changed
### product code executed: none
### exitCode: 1
```

原件：`build/review-session/raw/review-m31flash-followup-1/register-build-first-failure.log`。这是**审查者自写工具的路径缺陷**，非产品缺陷，**未执行任何产品代码**。前序轮首次失败（`probe-h2-first-failure.log`）**原样保留、未覆盖**。

### 3.3 为何本轮不重跑 check / verify:sources / package:dir / probe

按续审输入「依原 prep、实际必要性及『无变更不机械重测』判断」，本轮先核实无变更前提：

```
HEAD:      0fb8e045ec776da6e8dc1b306c72212982114cd8
HEAD tree: 与 product tree 30319412 的 tree 相同
git diff --name-only 30319412 HEAD | grep -v '^docs/'   →  (none)
git status --porcelain                                   →  仅 " M AGENTS.md"
```

产品字节与 HEAD/blob OID 与前序轮**完全一致**，因此前序轮的运行收据（`runs-ledger.json` 7 条 run，全部 exit 0）**仍绑定同一候选**，继续有效。**无变更即不机械重测**——重跑只会消耗额度与时间，不会产生新信息。

**该决定不等于「本轮重新验证过」**：前序轮的运行证据在本轮被**引用**，不是被**重演**。前序轮 7 条 run 的 argv、原因、起止时间、exit、stdout/stderr 与首失败均完整保存在 `build/review-session/raw/review-m31flash-round1/runs-ledger.json`，本轮未修改、未覆盖。

---

## 4. 逐路径覆盖登记（866/866，全覆盖）

完整登记：`build/review-session/raw/review-m31flash-followup-1/path-coverage-register.json`（schema `T03_MAPPING_S1_FOLLOWUP1_PATH_COVERAGE_V2`）。

### 4.1 标签定义与分布

| 标签 | 含义 | 数量 |
| --- | --- | --- |
| `READ-FULL` | 文件内容逐行/全文读完 | **749** |
| `READ-SECTIONS` | 只读了文件的头部、grep 结果或特定小节 | **93** |
| `READ-STRUCTURAL` | 以 JSON 键/字段/标题方式结构化解析（未作为连续散文通读） | **5** |
| `NOT-READ-BINARY` | 二进制/图片/归档载荷未检视（PNG 像素未看；.zip/.gz 未解包）；其外围 AX 文本、日志与清单均已读 | **18** |
| `NOT-READ-BY-DESIGN` | 刻意未读（另一指定模型本轮的提示材料，属禁区） | **1** |
| **合计** | | **866** |

**路径对账**：866 manifest（173 engineering + 693 documentation_or_evidence）+ 37 审查包文件（`docs/reviews/T03/designated-review-backlog-20261022/**`）= HEAD **903** 条 tracked。已用 `git ls-tree -r HEAD --name-only` 与固定输入 manifest 双向差集验证：manifest 路径集合与登记路径集合**完全相等**（无遗漏、无越界）。

### 4.2 本轮补齐的实质覆盖（相对前序轮）

前序轮的覆盖登记是**叙述式**的（§3.5 按区域清点 + 抽查）。本轮补齐为**逐路径可机读登记**，并据此实际补读了前序轮未实读的路径：

| 组 | 路径数 | 本轮动作 |
| --- | --- | --- |
| T03 验收/失败/缺证原件 | 64 | **全部实读**（含 `check-first.txt` ruff E501 首失败、`candidate-package-first-run-stderr.txt` PyInstaller 缺 `invalidation-v2.json` 首失败、`ui-state-after-review.txt` 3 failed 首失败、`package-verifier-first-lint.txt` 5 errors 首失败、`candidate-package-build-with-resource.txt` ERROR 首失败、`root-artifact-recovery.json` 归档恢复记录、`round-1/preparation-checks.json` 与 `preparation-manifest.json`） |
| T03 check 日志族全链 | 6 | **全部实读**（`check-first` → `check-final`/`check-after-fixes`/`check-latest`（1088+4 skip）→ `check-recovery-supplement`（1097+4 skip）→ `check-project-xlsx-first`（1107）→ `check-registered-scope`（1110 / **0 skip**）） |
| T03 证据索引 | 1（`round-1/evidence-index.json`，33 KB） | **结构化解析 + 60 条 trackedEvidence 逐条展开**（ref / bytes / sha256 / currentEqualsFrozen / purpose）+ recovery 审计 + `importantBoundaries` 6 条权威表述 |
| T03 固定输入登记 | 1（`round-1/scope-and-identities.json`，41 KB） | 结构化解析 |
| 继承工程面 | 173 | **全部实质逐路径审读**（见 §4.3） |
| 继承证据档案 | 640 | **全部实质逐路径审读**（I01/I02/I03/I04 + 各 iteration 目录） |
| PRD | 1（93584 B） | FR-300—304（L336–370）与附录 D.1 M-01—06（L1183–1190）实读；其余章节未逐行读，**如实标注为 `READ-SECTIONS`** |
| `.pen` 设计稿 | 1（1457069 B） | 以 JSON 解析全量节点树（468 节点 / 最大深度 7 / frame 200 / text 136 / ref 68 / icon 63），**非**逐字节散文通读，标注 `READ-SECTIONS` |

### 4.3 继承工程面的逐路径核验结果（摘要）

7 个只读子代理的逐路径登记已全部取回并复核，关键结论：

- **engine core（15 路径）**：`Store.commit` 原子性（`storage.py:316` `BEGIN IMMEDIATE`/`COMMIT`、`synchronous=FULL`）、旧基线拒绝在写事务内（`storage.py:324-329`）、事实/定义写入点全部在 commit 内（`:358-361`/`:381-388`/`:398-405`/`:421-424`/`:444-447`/`:722-723`）；RDF 图只从不可变快照重建、无回写（`rdf_snapshot.py:51-66`，唯一消费者是 `storage_probe.py`）；`staleReason` 只源自 `invalidation-v2.json`；无 socket/http/凭据/遥测/端口（grep 0 命中）。
- **engine tests（19 路径）**：继承套件**恰好 3 处 Darwin-only skipif**（`test_i04_lifecycle_boundaries.py:235,295,343`）；候选 `test_mapping_source.py` 的 5 处 `importorskip("openpyxl")` 因项目依赖已装而**不 skip**；**无任何继承测试 import `ontolearn_engine.mapping`**。
- **desktop（22 路径）**：`csp.ts` 是唯一策略源（生产变体无 `unsafe-inline`/`unsafe-eval`）；preload 12 个具名方法、**无通用 `invoke`**；IPC 校验两处调用点覆盖全部处理器；私有页**确实未挂载**（`main.tsx` 只渲染 `App`，全树无 `./mapping` import）。
- **contracts（16 路径）+ root/CI/scripts（~60 路径）**：35 处 `mapping` 全部是既有通用族名/能力设计位，**候选零改动**（`git diff 5f910b5 3031941 -- packages/contracts` 为空）；`mapping.commit` 仍为 `implementation: design-only`；CI 会自动拾取候选三处新目录，无遗漏。

### 4.4 刻意未读与未检视（明确登记，不谎称已读）

| 路径 | 原因 |
| --- | --- |
| `docs/reviews/T03/round-1/zcode-glm-5.3-prompt.md` | **另一指定模型本轮的提示材料**，属禁区；刻意未读 |
| 14 个 `docs/reviews/I02/native-dialog-probe/run-{1,2}/*.png` | PNG 像素未检视（外围 AX 文本已读） |
| `docs/reviews/I02/round-3/round-2-linux-artifacts/.../trace.zip` | 归档未解包 |
| `docs/reviews/I02/round-3/round-2-linux-artifacts/desktop-{1024,1280}.png` | PNG 像素未检视 |
| `docs/reviews/I02/round-3/round-2-windows-job.txt.gz` | gzip 未解包（同名未压缩孪生文件已读） |

### 4.5 对前序覆盖声明的一处更正（前序报告自身的不精确）

前序报告 §3.5 称继承面「以只读方式清扫并逐项核验」。本轮以**逐路径登记 + 会话级 ground truth 复核**（对本会话全部工具调用做路径提取，反查每条路径的实际读取方式）核实后确认：前序轮对继承证据档案（I01/I02/I03/I04 共 640 路径）**并非逐条全文读**，而是**区域清扫 + 抽查 + 代理分发**。本轮已把这部分补为**逐路径实质审读**，并对前序轮遗漏的 T03 路径（6 个 check 日志、6 个 build/stderr 证据、3 个 JSON 恢复/准备记录等）**实读补齐**。

该更正属**本方审查方法学的口径更正**，不影响前序轮的任何产品判定（结论均未改变）。

---

## 5. 前序轮结论的继承与重述

| 前序结论 | 本轮复核 | 状态 |
| --- | --- | --- |
| 阻断性缺陷 0 | 本轮 866 路径实质审读未发现实现级阻断 | ✅ 维持 |
| 架构不变量逐条实测无违反 | 本轮逐路径复核七项不变量，无违反 | ✅ 维持 |
| M-01—M-06 逐项通过 | 本轮复核 `plan.py` / `storage.py` 对应断言点 | ✅ 维持 |
| FR-300—304 在 S1 服务与私有页面子范围内逐项通过 | 同上；正式接线项仍为未完成 | ✅ 维持（边界不变） |
| P1 已关闭 / P2 仍开放 | 本轮按 §0.1 拆分为两项分别登记 | 🔧 **措辞更正** |
| 「唯一包级缺口」的表述 | 不准确，实际为两个层级 | 🔧 **措辞更正** |

---

## 6. 前序发现 F-01—F-04 的完整处置（本轮逐条复核）

### F-01 — 低 — 证据生成脚本会静默改写受跟踪证据文件 → **复核成立，处置意见不变**

- **位置**：`docs/iterations/T03/verify-packaged-probe.py:15-16`、`:66`
- **本轮复核（实读源码）**：`:15` `(root / "docs/reviews/T03/product-package-probe-first-stdout.json").write_bytes(result.stdout)`；`:16` 同法写 `product-package-probe-first-stderr.txt`；`:66` `(root / "docs/reviews/T03/product-package-verification.json").write_text(...)`。**三个受 Git 跟踪的证据文件，路径由 `root` 写死，无输出目录参数** —— 与前序轮结论一致。
- **影响**：同一包字节下幂等（内容相同），当前不构成内容错误；但**换包重跑会静默替换已归档的包级证据**，使「某次包证据对应哪个包」的审计链依赖单一可变文件而非不可变回执。对只读审查者而言，运行该脚本即构成对受跟踪证据的修改。
- **本轮处置**：**仍未运行该脚本**（本轮 `runs-ledger` 无该条目）。其全部断言由只读等价脚本 `build/review-session/scratch/verify-packaged-probe-readonly.py` 复现（前序轮已建立，本轮沿用），只写本方 raw/scratch 区。
- **建议**（不变）：输出目录改为调用方入参（或新增 `--out`），默认写入证据轮次目录；已归档证据只读。属流程/工具改进，**不阻断本候选**。

### F-02 — 低 — 私有页 `draft.fields` 顺序随编辑历史漂移 → **复核成立，处置意见不变**

- **位置**：`apps/desktop/src/renderer/src/mapping/MappingPage.tsx:41-45`、`apps/desktop/src/renderer/src/mapping/model.ts:65-68`
- **本轮复核（实读源码）**：`MappingPage.tsx:43` 为 `fields: [...draft.fields.filter((item) => item.column !== column), { ...field, ...change }]` —— 被编辑字段被**追加到数组末尾**，数组顺序随编辑历史变化；`model.ts:66-68` 的 `draftKey(draft) = JSON.stringify(draft)` 对数组顺序敏感。与前序轮结论一致。
- **影响**：方向为 **fail-closed**（等价草稿被判为不同草稿 → 旧预览被拒 → 需重新预览），**不会**造成越权提交或错误提交；但产生「未改映射却提示预览失效」的可用性偏差，且等价编辑顺序产生不同草稿指纹。
- **建议**（不变）：按字段名稳定排序，或 `draftKey` 基于字段名排序后的规范化副本计算。低优先级，**不阻断**。

### F-03 — 信息 — `mapping.commit` 同时标注 `agentEligible: true` / `effect: formal-write` 与 `implementation: design-only` → **复核成立，处置意见不变**

- **位置**：`packages/contracts/v2/registry.json`（`mapping.commit` 条目）
- **本轮复核（实读该条目）**：`effect: "formal-write"`、`requiresChangeSet: true`、`requiresConfirmation: true`、`agentEligible: true`、`implementation: "design-only"`、`dependencyPolicy: "mapping.commit"`、`dataScopes: ["asserted"]`。**该条目继承自批准 base**：本轮实测 `git diff --name-only 5f910b52 30319412 -- packages/contracts` → **0 条**，T03 **未引入也未修改**。
- **实际安全性（不构成可派发路径）**：`coordinator.py:249-254` 的 `job.create` 只接受 `test.read|test.atomic|test.rounds` 且要求 `test_mode`；`packages/contracts/src/**` 无 mapping 桥方法；preload 12 个具名方法无 mapping；IPC 路由表无 mapping 通道。
- **影响**：无当前功能或安全影响；属**契约目录与实现态之间的一致性观察**，归属 contracts owner。
- **建议**（不变）：由 contracts owner 择期澄清是否应把 `agentEligible` 降到 design-only 阶段。**不在 T03 责任范围，T03 正确地没有触碰它。**

### F-04 — 信息 — `docs/reviews/**` 的活扩展名 `.mjs` 落在 ESLint 目标集但被 Prettier 排除 → **复核成立，处置意见不变**

- **位置**：`eslint.config.mjs:8-16`（`ignores` 不含 `docs`）、`.prettierignore:12`（含 `docs/reviews`）
- **本轮复核（实读两份配置）**：ESLint `ignores` 列表为 `**/out/**`、`**/dist/**`、`**/release/**`、`build/**`、`.venv/**`、`playwright-report/**`、`test-results/**` —— **不含 `docs`**；`.prettierignore` 含 `docs/reviews`。3 个归档 `.mjs`（`docs/reviews/I02/round-2/minimax-runtime/i02-r2-mavis-{extra-probe,nav-probe,nav-probe2}.mjs`）因此受 ESLint 门禁但不受 Prettier 门禁。与前序轮结论一致。
- **前序轮实测**：`npx eslint docs/reviews/I02/round-2/minimax-runtime/ --max-warnings 0` → exit 0；`npx prettier --check docs/iterations/T03/` → exit 0。
- **影响**：**策略不对称**而非缺陷（当前全部通过，无 CI 风险）。
- **建议**（不变）：统一 `.prettierignore` 与 ESLint `ignores` 对 `docs/reviews` 的处置，或在 ESLint 配置中显式排除归档目录。低优先级。

---

## 7. 前序 F-05 / F-06 的定性（验证观察，非待修缺陷）

按续审要求明确如下：

> **F-05 与 F-06 是「验证观察」（verification observation）——即通过核验得到的正面结论/被推翻的假设——不是待修缺陷，不进入缺陷清单，不要求 owner 修改任何代码。**

### F-05 — 验证观察 — preview 层与 Store 层在所有权判定上完全一致

- **位置**：`packages/engine/src/ontolearn_engine/mapping/plan.py:289-329` vs `packages/engine/src/ontolearn_engine/storage.py:608-633`（`_check_slot`）、`:635-652`（`_replace_mapping` 人工漂移）、`:692-699`（单值槽多值）
- **性质**：**核验通过**的正面结论。前序轮探针实测：单值属性+他人不同值 → preview 报 `OWNERSHIP_CONFLICT` / `ready=false` / `checked_plan` → `PreviewRejected("MAPPING_BLOCKED")`；**绕过 preview 直接构造 plan 提交** → Store 抛 `Conflict: Ownership conflict: slot=urn:example:equipment/001 urn:example:name, other=manual` → **Store 层独立设防成立**；同槽同值双 owner → `OWNERSHIP_CONFLICT`；非单值属性+他人不同值 → 不报冲突（多值语义正确）。
- **结论**：两层判定等价，且 Store 层具备**独立纵深防御**；未发现 preview 与 Store 的判定分歧或可绕过路径。**非缺陷，无需修改。**
- **附**：两条无源码测试覆盖的路径（`empty="literal"`、单值+不同值）已由前序轮探针补测通过。

### F-06 — 验证观察（被推翻的假设）— XLSX `UNSAFE_XML` 闸不误伤合法单元格文本

- **位置**：`packages/engine/src/ontolearn_engine/mapping/source.py:181-188`
- **假设**：`text = value.replace(b"\x00", b"").upper()` 后的 `b"<!DOCTYPE" in text` 子串匹配，可能把**合法单元格文本**中的 `<!DOCTYPE` 误判为 `UNSAFE_XML`。
- **实测（前序轮 probe-h1，exit 0）**：单元格文本 `<!DOCTYPE html>`、`<!doctype html>`、`<!ENTITY x>` 三种变体**全部正常解析**。
- **原因**：XML 文本节点中的 `<` 必然转义为 `&lt;`，故单元格值在 part 字节中**不可能**出现字面 `<!DOCTYPE`；闸门的 `\x00` 剥离正确覆盖 UTF-16/32 编码的 part。
- **结论**：闸门**正确且无假阳性**。**假设已被推翻，不是缺陷，无需修改。**

---

## 8. 本轮新增发现（F-07 — F-11）

### F-07 — 信息 — 开发态 CSP 校验失败会形成未捕获 rejection 且不创建窗口（继承、仅 dev）

- **位置**：`apps/desktop/src/main/index.ts:78-88`、`apps/desktop/src/csp.ts:14-18`
- **触发**：以 `ELECTRON_RENDERER_URL` 指向非 `http://127.0.0.1:5173` 的地址启动开发态，或 nonce 非法。
- **事实**：`index.ts:84` 的 `contentSecurityPolicy({ nonce, origin: devURL })` 位于 `void app.whenReady().then(async () => {...})` 内；`csp.ts:15-18` 对 origin ≠ `http://127.0.0.1:5173` 或 nonce 不匹配 `^[\w+/=-]+$` 时 `throw new Error('INVALID_DEVELOPMENT_CSP')`。该 throw 发生在 `then` 回调内 → **未捕获的 promise rejection**，且位于窗口创建（`index.ts:72` 的 `loadURL`）**之前** → 窗口不会被创建。
- **影响**：**继承缺陷，不由 T03 触发**。仅影响开发态启动失败时的可诊断性（表现为无窗口 + 未处理 rejection，而非一条明确报错）。生产路径（`csp.ts:4-13`）不含该分支。
- **建议**：把该校验移到启动前的显式检查或捕获后给出可读诊断。归属 desktop owner，**不阻断本候选**。

---

### F-08 — 信息 — 「0 skip」是 macOS 主机观测，CI Linux 上继承套件仍有 3 处跳过

- **位置**：`packages/engine/tests/test_i04_lifecycle_boundaries.py:235`、`:295`、`:343`
- **触发**：在 Linux 上运行 `npm run check`（即 CI `quality` job，`ubuntu-latest`）。
- **事实**：继承套件**恰好 3 处** `skipif(sys.platform != "darwin", ...)`（Darwin libproc RSS 采样证据 / Darwin 父进程 RSS 采样失败 / 实际 libproc 与子进程监视器退出竞态）。前序轮在本机（macOS）实测的 `1110 passed / 0 skipped` 是**主机相关**观测；CI 的 Ubuntu runner 上这 3 项**会被跳过**。候选自身 `test_mapping_source.py` 的 5 处 `importorskip("openpyxl")` 因项目依赖已装而**不 skip**，故跳过数与候选无关。
- **影响**：**不影响候选正确性**（3 项均为继承的 Darwin 专属平台证据，与 T03 mapping 无关）。但「1110 / 0 skip」这一表述若被当作跨平台属性引用会失真。
- **证据**：`grep -n "skipif" packages/engine/tests/test_i04_lifecycle_boundaries.py` → 恰好 3 处，全部 `sys.platform != "darwin"`；CI `.github/workflows/ci.yml:16` `quality` job 为 `ubuntu-latest`。
- **建议**：在引用检查结果时明确标注主机平台；如需跨平台 0-skip 声明，须在 Linux 上单独取数。

### F-09 — 信息 — 继承测试套件对 mapping 服务零覆盖，`1110 / 0 skip` 不可作为 mapping 服务证据

- **位置**：`packages/engine/tests/`（19 个继承测试文件）
- **触发**：以 `npm run check` 的通过结果作为 T03 mapping 服务的质量证据。
- **事实**：**无任何继承测试文件 import `ontolearn_engine.mapping`**（本轮实测：`grep -rn "ontolearn_engine.mapping" packages/engine/tests/ | grep -v test_mapping_` → **0 命中**）。mapping 服务的全部保证只由候选自带的 4 个新测试文件承担。
- **影响**：`1110 passed` 是**继承套件**的通过数，其中**不含** mapping 专项。mapping 专项实际为 **58 项**（`test_mapping_source` 21 + `test_mapping_plan` 22 + `test_mapping_recovery` 9 + `test_mapping_entrypoint` 6）加 8 项 TS 状态测试。
- **证据**：候选 4 个新测试文件与本轮 grep 结果。
- **建议**：引用检查结果时把「继承套件通过」与「mapping 专项通过」分列，避免以总数掩盖专项覆盖。

### F-10 — 信息 — `dependencyKey` 字符集缺口对 T03 不可达（假设已消解）

- **位置**：`packages/contracts/v2/schema.json:23`（`dependencyKey` 正则）、`packages/engine/src/ontolearn_engine/mapping/plan.py:102-108`
- **事实**：契约 `dependencyKey` 正则要求身份部分为 `[A-Za-z0-9_.-]{1,128}`；`plan.py:104` 的 `_validate` 已强制 `re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", mapping.identity)`，并在不匹配时抛 `ValueError("Versioned mapping identity required")`。因此「含 `:` 等字符的 mapping identity 会进入 `versions` 后在 `coordinator.py:235` 触发 session-fatal `ProtocolFault`」这一假设**对 T03 不可达**。
- **残留事实（不同问题、归属不同）**：`storage.py:344-350` 只校验定义 id 非空，**不**校验字符集——这属于**继承的宽松性**，其风险面是「非 T03 调用方提交的任意 definition id」，**不是 T03-S1 引入**，也不是 T03 的缺陷。
- **影响**：无当前功能或安全影响；属**契约层与存储层校验粒度不一致**的观察，归属存储/契约 owner。
- **建议**：T01 接线时让存储层与契约层对 definition id 使用同一字符集；**不要求 T03-S1 修改**。

### F-11 — 信息 — `Store.commit` 与 `JobStore.commit_job` 的所有权冲突上报形态不同（接线约束）

- **位置**：`packages/engine/src/ontolearn_engine/mapping/plan.py:1`、`:365`；`packages/engine/src/ontolearn_engine/storage.py:38-48`；`packages/engine/src/ontolearn_engine/job_store.py:99-110`、`:372-373`
- **事实**：`plan.py` 的模块 docstring 明写「Trusted T01 owns all confirmation and Store.commit calls」——**T03 不自行提交**。但 `plan.py:365` 的说明要求调用方「在 `Store.commit` 内原子校验 base revision」。而 `storage.py:38-48` 的 `Conflict` 携带 `category="ownership"`，而该 category **不在** code 映射表中（`identity/revision/state/rounds/dependency/input` 之外）→ 降级为 `INTERNAL_ERROR`；其 `message` 文本含 slot / predicate / owner / `source_row`（内部诊断用，跨边界不得回传）。相比之下，`job_store.py:99-110` 的所有权冲突路径产出**有界**的 `OWNERSHIP_CONFLICT` + `detailRef`（`{category, resource, projectId}`，不含原值），且 `job_store.py:372` 的 `writing` 集合 `{test.atomic, changeset.commit, mapping.commit}` 表明正式写入能力被识别为 JobStore 路径。
- **影响**：**当前无影响**（T03 不提交；`mapping.commit` 仍 design-only 不可派发）。这是**T01 正式接线时必须遵守的约束**：正式 mapping 写入若走裸 `Store.commit`，所有权冲突会退化为 `INTERNAL_ERROR` 且错误文本含内部来源信息；若走 `JobStore.commit_job`，则得到有界的 `OWNERSHIP_CONFLICT` + `detailRef`。
- **建议**：T01 接线时**经 `JobStore.commit_job`** 路由正式 mapping 提交（与 F-10 的定义 id 字符集一并处理）。**不要求 T03-S1 修改**。

## 9. 各门判定（分列，不以静态代替运行，不以局部代替整体）

| 门 | 判定 | 依据 |
| --- | --- | --- |
| **静态（源码/契约/锁/构建配置）** | ✅ **通过** | 866 路径逐路径审读完成（§4）；75 条 base→product delta 全部实读；866/866 blob 与 HEAD 一致；产品→HEAD 仅 docs 差异；无公开契约/bridge/IPC/App 越界；锁差异恰为 3 个新包 |
| **运行（单元/集成/恢复）** | ✅ **通过**（前序轮实跑，本轮引用） | `npm run check` exit 0：638 vitest + 1110 pytest / 0 skip（**macOS 主机观测**，见 F-08）；mapping 专项 58 项 + 8 项 TS 状态测试与登记数一致；本轮因**无变更**未重跑（§3.3） |
| **打包（unsigned 目录包 CLI）** | ✅ **P1 通过**（前序轮实跑，本轮引用）；⛔ **P2 开放** | `npm run package:dir` exit 0；本树新包内 `--mapping-probe` exit 0、stdout 与冻结期望逐字节相同、11/11 case、额外参数拒绝精确、包内锁/许可证一致、引擎 SHA `5f40a565…` 与记录一致。**P2**（303 新增的外部公式/hyperlink socket 零调用 + CSV 四类超限定位）**从未在包内二进制执行**（§0.1） |
| **父业务（FR-300—304 正式接线、T00/T01/T02、正式 UI/bridge/job）** | ⛔ **未通过 / 未完成**（**非本 S1 子范围**，候选已如实声明） | 无公共契约条目、无 preload 方法、无 IPC 通道、`mapping.commit` 为 `design-only` 且不可派发；`integration-request.md` 完整列出待接线项；F-11 记录正式提交路径的接线约束 |
| **两 OS（Windows 11 / macOS 15 干净设备）** | ⛔ **未验证** | 仅 macOS-27.0.1-arm64 **本机未签名目录包 CLI**；不得据此宣称双平台通过 |
| **GUI / 浏览器交互 / 真实原生恢复** | ⚠️ **无法验证**（资源未交接 + 非本子范围） | `npm run test:e2e` 未运行；本轮**独立核实**三条干扰面：① Playwright `_electron.launch` **不注入** `--user-data-dir` → 启动的应用会使用共享默认 userData `~/Library/Application Support/@ontolearn/desktop`（已有数据）；② `tests/e2e/csp-lifecycle.spec.ts` 执行真实 renderer 崩溃 + 无限循环挂起 + `app.focus({steal:true})` + `window.focus()` + 合成鼠标输入；③ `tests/e2e/i04-jobs.spec.ts` 在 `I04_TEST_FIXTURE` 未设时**整片 skip**（`:22`、`:99-102`、`:317-320`）→ 未备夹具的运行只会报 skip，在 0-skip 标准下**不能计通过** |
| **签名安装 / 生产** | ⛔ **未验证** | `electron-builder` 明记 `skipped macOS code signing`；生产发布门不在本轮 |
| **父 57 P0 / 其它 FR 族 / 跨模块验收** | ⛔ **未关闭** | 本 S1 通过**不**关闭其中任何一项 |
| **同版本双审（另一指定模型）** | ⛔ **不在本轮范围** | 本轮未读、未推断另一指定模型本轮的任何材料 |

> 依提示要求：需要 e2e 缺证才能判定的门**明确记为未通过/无法验证**，未以「除未验部分外通过」的整体通过掩盖。

### 9.1 e2e 精确重跑合同（移交总控，本轮未执行）

- **Linux**：需 `openbox` + `xdotool` + `xvfb-run`（CI `ci.yml:46-48,52-58`）；`I04_TEST_FIXTURE` 须为本树**新建**目录（`uv run --frozen python scripts/prepare-i04-fixture.py <新目录>`，CI 传 `--background-rounds 12` 用于 reload 例）；第 3 例另需 `I04_NATIVE_ISOLATED=1`。
- **macOS**：**仅第 1 例**（reload 重查）可跑；第 2、3 例按 `:99-102`、`:317-320` 跳过，不得表述为 Linux 门通过。
- **必须 unset**：`I02_HMR`（HMR 探针会临时改写受跟踪源文件，评审冻结期间禁止运行）。
- **不得**用隐藏窗口、禁用 hang monitor 或 stub 原生提示冒充真实原生验收。

---

## 10. 未验边界（逐项明确，不谎称已全文审读）

1. **未运行**：`npm run test:e2e` 全部（C1 真实 CSP/崩溃/挂起/焦点、desktop 交互与最小窗口、I04 job/bridge/取消对账）。原因与精确合同见 §9.1。
2. **未在包内二进制执行（P2）**：303 新增的外部公式/hyperlink socket 零调用与 CSV 四类超限定位（仅源码级证据，§0.1）。
3. **未验证**：Windows 11 / macOS 15 干净设备、签名安装、GUI 视觉与浏览器交互、正式 I04 job/operation/取消对账、正式 T00 文件/工作表选择与公共分页、T01 正式确认与 ChangeSet、T02 真实本体定义语义、T08 模型增强草稿、T10 迁移、离线课程、Agent 与完整产品同候选验收。
4. **未读 / 未解码**：未获当前读取授权的 SDK、受限身份载荷、原 witness/descriptor/index 身份 payload 及归档载荷；历史 `native-current` 组的 native caller 首审未关闭状态**不因本报告而改变**。
5. **未读（本方刻意）**：`docs/reviews/T03/round-1/zcode-glm-5.3-prompt.md`（另一指定模型本轮提示材料，禁区）；18 个二进制/图片/归档载荷（§4.4）。
6. **未逐行通读**（已实读相关小节并如实标注）：`docs/prd/PRD-本体学习与落地Agent工作台.md` 的 FR-300—304 与附录 D.1 之外章节；`design/prototypes/OntoLearn-Studio-Prototype.pen` 的散文语义（仅全量节点树解析）；继承证据档案中的部分大体积 raw 日志与历史 peer 报告（按各子代理自报的读取深度登记为 `READ-SECTIONS`）。
7. **未修改**：本轮**零产品文件修改、零 commit、零 push、零 PR、零 stage**；`git status --porcelain` 末态仅 ` M AGENTS.md`（本轮前既有状态）。
8. **未继承**：任何历史 Pass。本报告判定仅适用于 `30319412daf8ae4745987babf7bbed93c53b6b42`（+ base `5f910b52…`）在 reviewHead `0fb8e045…` 上的字节。任何实现/测试/依赖/验收/基线变化后须重新验证并重新双审。

---

## 11. 最终判定

- **T03-S1 私有映射服务候选：通过（Pass）。** 阻断性缺陷 **0**；866/866 路径逐路径实质覆盖完成并留有可机读登记；前序 F-01—F-04 全部复核成立、处置意见不变；F-05/F-06 明确为验证观察而非待修缺陷；P1 已关闭、**P2 仍开放**；架构不变量逐条实测无违反；M-01—M-06 与 FR-300—304 在**本 S1 服务与私有页面子范围**内逐项通过。
- **本报告不构成**：push/PR/CI/合并/远端核验放行，不关闭父 57 P0、跨模块验收、双 OS、GUI 与生产门，不替代另一指定模型（ZCode / GLM-5.3）的独立同版审查。
- **待运行项移交**：`npm run test:e2e`（§9.1 含精确 argv、夹具准备命令、环境变量与平台前提），须待根协调窗口。
- **建议移交事项**：F-01（证据脚本参数化输出）、F-02（草稿字段稳定排序）—— T03 owner；F-03（注册表 `agentEligible` 与 `design-only` 表述一致性）—— contracts owner；F-04（ESLint/Prettier 对 `docs/reviews` 的处置统一）—— 工具链 owner；F-08（检查结果须标注主机平台）—— 报告引用方；F-09（继承套件与 mapping 专项分列引用）—— 报告引用方；F-10 + F-11（定义 id 字符集与正式提交路由）—— T01 接线 owner；F-07（开发态 CSP 校验失败的可诊断性）—— desktop owner。
- **说明**：本报告为独立外部审查结论；setup 独审与既有内审（`/root/t03_service_review`）均不构成本候选的指定模型 Pass。

---

### 附 A：本轮写面清单（全部在授权范围内）

| 路径 | 性质 | 说明 |
| --- | --- | --- |
| `build/review-session/reports/mapping-S1-minimax-followup-1-full-report.md` | 新增 | 本轮续审报告 |
| `build/review-session/metadata/task-followup-1.json` | 新增 | 本轮任务元数据 |
| `build/review-session/raw/review-m31flash-followup-1/path-coverage-register.json` | 新增 | 866 行逐路径覆盖登记（V2） |
| `build/review-session/raw/review-m31flash-followup-1/register-build-first-failure.log` | 新增 | 本轮唯一首次失败原件 |
| `build/review-session/scratch/build-register.py` | 新增 | 登记生成脚本（本方工具，非产品） |

### 附 B：前序产物保留清单（未改动）

| 路径 | 字节 / SHA256 | 状态 |
| --- | --- | --- |
| `build/review-session/reports/mapping-S1-minimax-full-report.md` | 49079 B / `827c8c1a9e026f503a40aa3df4e0cb2b0470e82d31b97c169421efb6e3ca928d` | ✅ 逐字节保留，与前序声明一致 |
| `build/review-session/metadata/task-actual.json` | 7426 B | ✅ 保留 |
| `build/review-session/raw/review-m31flash-round1/`（9 文件，含 `runs-ledger.json` 与 `probe-h2-first-failure.log`） | — | ✅ 保留，未覆盖、未回填 |
| `build/review-session/metadata/owner-ui-settings.json` | 1033 B / `e076e6bb…` | ✅ 保留 |
| `build/review-session/metadata/mapping-S1-minimax-followup-1-input.md` | 3457 B / `d48e5e73…` | ✅ 保留（固定输入，不改） |

### 附 C：原 turn failed 终态保留声明

原 turn `9c66220e-50d5-403a-b43b-d7bdb35de586` 的官方终态为 **failed**、公开 error 为 `UNKNOWN`、末 assistant stop 为 toolUse。该事实**原样保留**：

- 本轮**未**回填该终态，**未**将其改写为成功，**未**查询全局表或全局日志追查其失败原因；
- 本轮的完成状态是**本 turn 独立产生**的，与该 failed 终态**分别记录**（§1.1）；
- 前序报告的「有限 Pass」自判**不**被当作该 turn 成功完成的证据，也**不**因本轮完成而被追认。
