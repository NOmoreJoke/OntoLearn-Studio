# D2 canonical interface 纯设计独审 R1

结论：**R1 未通过“全部已知字段均有显式桥接落点”的完整性验收，需处理 1 项 P2（两个最小触发）；其余已核身份、原事实保留、提案隔离和权限边界在本限定范围通过。** 未发现 P1。该结论只针对文档设计，不是产品测试失败，也不签发实现或运行权限。M02–M05、原 codec 的完整闭合、实际同 issue/live/source 权威及原有运行总门全部仍为 false/pending。

## 固定对象与独立性

本轮只读本 tree 的固定 R1：候选 `eb5d4017e7dba86b568e879e34531e49d1b79920`，后出过程 `6b94c152a8fca0f0e26d377b0e4d79ff4d64b8b5`，旧 176 件基线 `0841ffbe7a4599fbea96f4ff998808f3f4e00972`。先全文读取 root 的 `I05-canonical-interface-inventory-D2-limited-reception-20261022.json`，然后读取 handoff、八作者设计及其固定 11 输入与来源记录。八作者文件均全文解析；重复字段按全量行映射/共同属性核验，长字符字面按完整序列与无损 run length 核验。

11 输入严格取该接收件的 allowlist，精确比对来源 tree 的 `39a91de416eb2692aea079c637309f9d8770b08a` Git 对象、当前同路径、R1 固定快照、bytes/SHA。文档中的 2cf 产品 pin 只作 provenance，没有跟读源码。未读 inventory 的索引/报告/proof/checker/log/missing-definitions、任何 retained 外审 wrapper/prompt/报告或 native 会话，也未读新 17 类/86 字段补件、type-directory 或 R2 WIP。

初检 `git status --short` 只有既有 `AGENTS.md` 修改；没有修改它。后续 root 已告知作者可在全新 R2 前缀写合法增量，本审不读取、不据此改变固定 R1 结论。本轮仅 exclusive-create 本目录 `independent-r1-*`，未改原 29、旧 176、AGENTS，未 stage/commit/push。

## IR1-P2-01：显式字段覆盖漏了已收到的 wrapper 与可选出口

**影响：** R1 的 52 目录/263 行本身计数准确，已经列出的目录和行均能回溯；但这组清单并非固定纯事实中所有已知嵌套字段/分支的完整覆盖。`acceptance-map.json#/positiveStaticCriteria/2` 声称 “all12 API outer and nested keys”，plan/handoff 又将 52/263 用作完整桥接交付。两个已知路径没有显式落点，使后续按目录消费时只能停在通用阻断，无法区分“已知合法分支尚缺内部值语法”与“未收到的新字段”。

### 触发 A：selectedFacts 每项的两字段 wrapper

- 已授权事实：`fixed-inputs/api-layouts.json#/layouts/1/selectedFacts` 原文 `list of {triple,sources}; asserted source {kind}; rdfs source {kind,basis}; rule source {kind,rule,inputs,basis}`；`fixed-inputs/interface-facts.md` M02 同样明确每项 `{triple,sources}`。
- 候选：`field-codec-bridge.json#/directories/1/orderedFields/8` 与 `#/fieldRows/12` 只落到外层 `selectedFacts`；`#/selectedFactSources/cases` 及最后三目录只覆盖内部 sources 的三个分支。整个 `directories/fieldRows` 没有 selectedFact item 的 `triple`、`sources` 两字段目录/行。
- 最小设计反例：`selectedFacts=[{triple:[<urn:synthetic:s>,<urn:synthetic:p>,<urn:synthetic:o>],sources:[{kind:asserted}]}]`。这是人造声明式结构例，不是 actual、golden、expected 或产品调用。即使只走最简单 asserted source，wrapper 的两个已知字段仍未各有落点。
- 最小修订：只在后出设计 delta 增补每个 selectedFact item 的 `{triple,sources}` 字段落点、每次出现/顺序/重复保留规则，与现有 source 分支接上。三元组/嵌套值语法若未闭合，仍保 pending；无需读新 source、actual 或外部类型补件。

### 触发 B：probe-production-observation 的已知 mutation 可选出口

- 已授权事实：`fixed-inputs/api-layouts.json#/layouts/11/optionalBranch` 明给 `mutation`。`fixed-inputs/interface-facts.md` M05 说明 mutation 分支另存坏副本/原 expectation 与未 reissue 标记；没有给出其完整内层键目录。
- 候选：`field-codec-bridge.json#/directories/16/orderedFields` 只有普通 13 项；无 optionalBranch/variant 记录，也无 mutation 字段行。全桥接只保通用 `onExtraField` 阻断，不能据其宣称已显式覆盖这一已知出口。
- 最小设计反例：只提供声明事实 `knownOptionalOuterName=mutation`，其内层值保持 `not-specified-by-received-pure-facts`。不能伪造该分支内层键或值，也不能把它当普通分支的必有第 14 项。
- 最小修订：在后出 delta 明列 mutation 的条件性入口，普通 13 项顺序保持；内层未给目录继续 layout-blocked，保全本次实际原件并请求原 owner 的最小纯字段契约。更新覆盖口径，加入“合法已知可选分支不得静默裁除/不得冒成功”的声明式例。

**保全边界：** 原 `onExtraField`、RAW、UNREFINED 与 no-silent-drop 规则已经要求可用原件全保并阻断完整导出；没有证据证明已发生数据丢失。因此 P2 针对设计落点/验收声明，而不是原 bytes 被删除或运行行为错误。不能以“raw 存在”代替这两个已知字段/分支的显式覆盖，也不应为消除发现而开放任何源码/actual 读取。

建议 root 把本项路由为新 R2 的文档 delta；R1 固定 29 及旧 176 保持原字节。R2 只需在真 delta 上复核，不把未授权补件偷加成本轮输入。

## 已通过的限定实质核验

1. **固定身份与成员。** manifest 为 6564B、SHA `172984bec405dcba94e1a5d3d0ea17e88b0c0df2902fce161bc5d0185ffffc4b`；receipt 为 51056B、SHA `de490facefe9db1dd613813d76c8ecdfce4ea5bf7903b4c13fa0d7462411ab04`。27 payload + manifest = 候选 28，后出 receipt 为过程第 29；Git 成员与 manifest 精确对应，新旧路径不重叠。旧 176 current=0841 Git=bytes/SHA；新 29 current=6b94 Git=bytes/SHA，前 28 也等于 eb5d Git。11 来源快照均等于精确授权 ref/path/current/bytes/SHA。
2. **已列字段与继承。** 52 目录与 263 行无重复 ID，行顺序等于目录顺序，结构化注解/默认声明逐行等于纯事实。12 顶层 API、9 annotation 目录、15 追加记录均正确；没有造第 13 API。ProfileComputation 14、Explanation 继承 15、DirectStepsReceipt 11（含 retention_owner）、RootRef 5，legacy source4/provenance13/result5 均保留。Explanation 的 version 在原位覆盖，direct_receipt 尾加；ReadonlySequence.native_kind 与 items 均保，kind 仍 str，无旧 enum。
3. **原 codec 与原件。** material input、production flat `recordType+原字段`、probe full-module `recordType+nested fields` 分开；hex/base64/integerHex 与 tuple/list 已折叠事实保留。没有把新 SequenceValue 的 list/tuple enum 追认为旧 native_kind enum，没有给 legacy memory metadata 虚构专用原 byte wire。ProfileValue.value:object、native_result/wire:dict、未细化 tuple、缺失 helper/17 注册仍 pending；禁止反射/repr/str 填洞，未知 observed 值须 layout-blocked，不能裁字段、填 None 或改作 not-reached 求表面成功。
4. **原摘要。** `digest-bridge` 前 16 个 existingRecipe 对象逐值等于固定 digest-recipes；新增 catalog/canonical_string/IMPLEMENTATION 事实另列。scope 没有显式 allow_nan=False；profile 严格选项不倒填 scope。原 N3 triples/规则、payload 七键、wire 四键、material 多个 preimage、catalog bytes 分域保留。IMPLEMENTATION 三键与 finite6/7/8 覆盖只是声明；dependencyLockHash 表达式未求值，实际 null 未补。
5. **字面例和新增摘要。** 8194 Python 字符例完整切为 8192+2，首片 UTF8 16385B，尾片未丢。`[]` 的旧 raw SHA 与新 relation 例分别核算；新前缀后恰一个 NUL，再严格紧凑排序 UTF8 JSON，和完整 base64/SHA 相等。relation 的六个 core 键、排除自身/未来 manifest/receipt/process、先原件再 DTO/relation 再 carrier/manifest/receipt 的无循环顺序自洽；该摘要没有替换旧 digest，也不证明语义、issuer 或权限。
6. **提案与 authority。** 29 个定义逐项标 NEW-PROPOSED-NOT-ADOPTED，引用均解析，exact-record required/fields 对应。NoneValue、false、空 tuple、blocked、not-reached、无原 wire 分开。Q01–Q09 有明确 owner、最小纯材料请求、null actual pin 和 sourceFollowing=false。六键 identity-policy 只收角色/链接：receipt.runId 来自先登记 caller attemptId；child ID 只首受信 context；未读 policy 正文，没有替其余 30 字段发 registry/collector/layout/source/issuer/runtime authority，也没有回填旧冻结 null。旧 strict18/四 schema/1241 仅作为既有固定边界保留，本审没有重新验证这些旧契约的全部内容。
7. **验收与失败历史。** 21 反例始终是声明式设计，不是运行测试。作者初始 parse 失败 outer exit1、语句执行前无写、初始未独立分流限制均保留，后续 minimal static exit0 没有覆盖它；190 bootstrap/43 receipt 的记录流 bytes/SHA 一致。后出 15 命令只由 root 指定 f7b997 转录承载，本轮未读取/重建或声称包含于 self-excluded receipt。

## 实际检查和证据边界

本审新 checker `independent-r1-check.py` 只 import Python 3.12 stdlib；先静态 parse，然后以唯一 pinned Python 和 `PYTHONDONTWRITEBYTECODE=1` 运行。真实 exit0，949 个身份/字段/recipe/grammar/字面/流断言无失败；两处设计发现另列 `designFindings`，**949/949 不等于候选完整性通过**。它没有调用作者旧 checker、第三方 JSONSchema 引擎、RDFLib、原 codec、model、product、probe、tests 或任何算法实现；没有 pytest/npm/build/install/network/DB/native/GUI/Goal/外部消息。

完整命令 argv/cwd/exit 与 Git 输出 bytes/SHA/固定对象引用写入 `independent-r1-check-01.stdout.json`；真实 stdout/stderr 分别保存，执行收据为 `independent-r1-check-01-execution.json`。这些是原流，不 format。counterexamples 文件是本报告两个触发的声明式 fixture，没有冒称产品实际拒绝/接受。

本审也保留自己的 read-only introspection 失误：工具 `96c860` 查询了不存在的 `recipes` 键，真实 exit1/KeyError；未写文件。随后 `aceecd` 改查 `bridges` 成功。该原始交互流只在工具转录中，未事后造初始分离 stdout/stderr。初期若干大显示被截断，后续以完整 JSON 解析、逐字段相等和共同属性/长字面无损归并覆盖，并保留显示限制。详见 `independent-r1-bootstrap-boundaries.json`。

本轮没有独立重跑原 383 源静态项、旧 1241、full417/wholeOracle/父137、JobStore whole-H、SQLite HOLD、实际费用 capture/issuer17L、平台/真人/指定双方/CI/develop/远端门。有限事实已足以判断本轮纯设计，未把未授权 runtime 或真实 source pin 补齐作为通过前提。尚未闭合的旧值语法、helper 全目录、精确 adapter/安全异常、same-issue/live verifier、collector/layout/root 与预算采用仍须原 owner/root 分别接收。
