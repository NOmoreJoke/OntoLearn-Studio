# O15 W1/W2/W3 独立实施审查

2026-10-23，上海。审查基线 `a570cd2b5e2edd53fd5e8be09ae29f271583df43`；受审工作树为 `.worktrees/T05-source-package-oracle` 当前四个自有源文件及正常生成物。**本次局部实施审查有一项待修复的 W2 有限索引拒绝域缺口，不能据此签“计划全部落实”。固定 417 项当前生成物未发现业务 expected 退化。** 本报告不是完整工程双指定模型审查或父门签字；不关闭原 15 条意见。

## 待处理发现

### [P2] W2 只封住四个索引分支，其余 indexed 拒绝分支仍接受未批准索引

位置：`scripts/build-i05-source-package-oracle.py:551-572,598-599`；新增 guard 入口在 L495-505，新增测试在 `scripts/test-i05-source-package-oracle.py:659-670`。

最低修复计划 L62 要求“不在固定 family 索引集合的值明确 ValueError”，当前 field-policies 也声明未批准 family 索引明确失败。实现只将 `turtle/front-`、`integer/other-datatype-`、`integer/bound-front-`、`shape/front-` 接入 `finite_fixture_index`。其余 indexed 拒绝入口仍使用范围比较或前缀默认值。独立 stdlib 内存反例：从 sealed observations 各取对应合法观察，保持 dataset/parameters 不变，仅复制后改 ID，再调用真实 `business_expected`：

| 原 ID → 未批准 ID | 实际结果 |
| --- | --- |
| `utc-date/lexical-0/value` → `utc-date/lexical-100/value` | 返回 `known-rejection/RDF_TERM_INVALID/date-value`，`pending=[]`，还带旧 6891 L275–313 的 declaredRegressionAuthority |
| `utc-date/incompatible-0/bound` → `utc-date/incompatible-100/bound` | 返回 `known-rejection/INVALID_SHAPE/check-shapes`，`pending=[]` |
| `integer/lexical-0/strict` → `integer/lexical-100/strict` | 返回 `known-rejection/INVALID_LITERAL_LEXICAL/parse-data`，`pending=[]` |

固定原语料中三类索引分别只有 0–16、0–4、0–5；上述 ID 不在其中。第一个反例把未授权 index100 套入只涵盖 7–10/15–16 等有限旧断言的权威声明。它不是当前固定 417 生成失败：完整资产 pin 阻止外部新增 ID，因此当前 build/check 正常。这是本轮已经承诺的有限拒绝域没有完全闭合，不能宣称未知 indexed 输入全被拒绝。

最小修复：在这些 indexed family 的真实业务入口，显式验证固定合法 index、side/policy 组合；不扩 417、不生成新 pending、不修改旧合法 expected。增加针对真实 `business_expected` 的内存负例。现有测试只调用四个 helper，并 mock `construct` 直接抛错；后半只能证明 main 先 construct 后写，无法证明未批准业务 ID 真会抛错。应以真实 mutated observation 触发拒绝，再验证没有产物写入。

复现核心（只在内存改对象；无产品执行）：

```python
row = copy.deepcopy(next(x for x in asset['observations']
                         if x['id'] == 'utc-date/lexical-0/value'))
row['id'] = 'utc-date/lexical-100/value'
builder.business_expected(row, asset['datasets'][row['datasetId']], golden)
# 实际返回 known-rejection + []，没有 ValueError
```

## 实际审查覆盖

读取了本树 AGENTS、root 精确授权 JSON、最低修复计划、四个自有文件完整 delta 及相关原有调用上下文、C goldens 全部 13 case、explanation 的保留/pin/消费策略、两个七池规范精确行段、私有输出 schema 和 source registry。未进入两棵外审树，没有修改任何实现、输入、共享契约、忽略配置或生成物。

- **13→17 及字段角色**：13 case ID 和 17 observation ID 完整相等，date 四组合及 illtyped 两组合分开。另写独立 stdlib N3 有限解析和六字段映射，直接比较固定 C golden 与生成物：14 个适用 query/report 分支的 rows/conforms/components/完整 requiredResultRows 成立；3 个入口拒绝分支 report 为 null。没有将历史 currentEntryGap、reason/derivation 当安全错误码。valueNodeCount、coreOnlyExpectedReport 明记 reference-only。`explanation-goldens` 没有可批准精确映射时保留 reference-only，没有伪造消费。
- **来源**：27 行 registry 对应 19 个唯一 local；8 个同字节 local 的重复行保留原历史身份/本地 pin 角色。local 规范化限定获准 evidence 输入或 guidance，读取字节与尺寸/SHA 校验，source-identities 自身加入 DOC_PINS。111 条 canonical 唯一 origin literal 与完整 sealed sourceRefs 集合相等，包括 523c 历史 ref；origin 仅 provenance-only，未读取 producer 算法补 expected。缺 ref 明示未提供，未把本地同名件当历史来源认证。当前重复行没有互相冲突的 bytes/SHA；不同角色保留，未任意去掉历史条目。
- **七池**：两段固定规范使用的 input/input_bytes、output/output_bytes、trace/trace_items 别名均显式，七值与 DECLARED_POOLS 相等，DOC_PINS 先验证规范字节。该关系是外部声明政策，不能认证实际 OriginalAllocation 或生产费用。
- **raw 私有域**：完整比对所有 25 数组与原 sealed records，计 96 个三元记录行、288 个 term occurrence。五键形状、完整 source 对象或 null、language 原拼写、顺序、multiplicity 和尾项均保留。**288 是 term occurrence 数，不是三元记录行数。** canonical graph/typed term 不把五键 raw 当第四种公共 RDFTerm；未修改 public schema。验证中的 raw 绑定使用 exact type/结构比较，不只比较数量。
- **blank/scope**：新增 list role 开关只在 shapes 调用设 true；data/ontology/合并 graph 使用默认 false，未新建跨图 blank 域。scope rule basis 由完整 matches/heads 求候选，重复同 basis 可保留，distinct basis fail-closed；并未扩为 all-proofs 承诺。
- **W3 recorder**：子进程始终使用记录的同一 sys.executable；完整 version/versionInfo 与五项明确白名单环境记录，旧流未重写。历史 verify-i01 只加适用范围说明；无共享工具适配。未将解释器版本记录当产品通过证据。

## 生成物与保护面核验

用 Git 基线 JSON 与当前完整 JSON 逐项比较，而非只看报告：417 IDs/顺序、320 datasets 绑定、全部 observation 的 expected/parameters/sourceRefs/contextStatus、contextLedger 均无业务 delta。17 C observation 仅 expectedSourceRefs 增加分支/用途说明；oracle 顶层改动为 builderSha256、expectedAuthorityConsumption、fieldPolicies 和上述 refs。

`coverage.json` 和 `budget-gaps.json` 与基线逐字相等：

| 文件 | bytes | SHA256 |
| --- | ---: | --- |
| coverage.json | 154032 | `95d7395761fbabe97c1fd81d1d05eb44bb8094f7266d977de42fdff349d28bd9` |
| budget-gaps.json | 362492 | `e68188ddefae4488fa6cf7762549508b78a3d87551f27cb24b9c9998f7948e9d` |

280 specified / 137 pending、26 declared-allocation pending、wholeOracleComplete=false 均保留；没有刷绿。sealed 原资产、描述、独立金标继续由原 PINS 检查。原 15 finding 和指定模型判断没有被本报告改判。

## 实际验证及边界

独立执行：

1. `python3 -B scripts/test-i05-source-package-oracle.py`：exit 0，57 tests，4.554 秒。
2. `python3 -B scripts/build-i05-source-package-oracle.py --check`：exit 0，五个完整输出字节相等。
3. 上述三项未知索引反例：真实 `business_expected` 均接受，构成本报告发现。
4. 独立 stdlib 解析/完整新旧 JSON 对比、14 适用 golden 分支比对和 25 raw 数组比对：通过。

本独审系统 python3 是 3.9.6，仅执行 O stdlib 工具；同时核读 owner 保存的 build03/test01/check01 invocation/result，实际为该树 venv Python 3.12.14 且 exit 0。没有重写 owner 命令记录。未运行产品、native/GUI、网络、DB、安装、Goal 或包内/生产验证。

owner 的完整 `npm run check` 记录 exit1：ESLint 后在 Prettier 对 16 文件告警而停止，其中含旧 receiving 文档、正常生成 JSON 和当时 field-policies。不能签全工程 check 通过；本独审未替 owner 修改 ignore、生成字节格式或共享旧资料，也未重复运行完整 check。组件独立验证的后续结果由 root 保留，不能自动替代整体命令结果。

## 四源 before/after 身份

before 为固定基线 Git blob，after 为本次审查读取的当前 bytes；本独审只写本报告，未改这四源。

| 路径 | before bytes / SHA256 | after bytes / SHA256 |
| --- | --- | --- |
| scripts/build-i05-source-package-oracle.py | 89455 / `024b352964880f57154ee2f49b31fce9dea368e29d5cd3112ffbad7497b06610` | 104806 / `5ae874c517a890d19f7249916f6d515dbc4214e7b6d99f900d6865330af2f734` |
| scripts/test-i05-source-package-oracle.py | 32188 / `601ca5b48b2cc1422ca7a956907b3da1b63b8f450a414ad5fa1dc47261cabb4d` | 41041 / `ecfb434afb4379180a42251d19a4b4fc3bab9b5b922514c5a47253ef2cfce275` |
| docs/reviews/T05/source-package-oracle/record-command.py | 1933 / `261842d5d6ced67fa3f25f7ff590edab4b4c8f58eb778587e3da2ee2bf3aa91d` | 2227 / `46e780ca3ae0a6ca48bb5a3fb955337cb19b5d14dddd149a081cc9d90994ebd9` |
| docs/iterations/T05/source-package-oracle/field-policies.md | 6324 / `9abaab883296b6085e82eb3b5a44216611a3cdf6d10c0e1589f14ed728684c34` | 11719 / `b1af685230e759adea3de8a549772f48f0853ad47931237cac926f7fa2f4fcbd` |

本次是获准 W1/W2/W3 实际补丁的局部独立审查，未声称逐行重读整个工程/两锁/PRD全篇。上述未批准索引缺口修复后需按真实新 delta 复核并冻结新身份；全工程完整输入、原五项静态阅读缺口、全新同候选双指定审查和父/发布门继续由 root 执行。
