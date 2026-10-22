# O15 实际组合配置独立静态审查

2026-10-23，上海。**实际组合配置 delta 未发现阻断项；可按已授权的精确档案例外范围接收。** 本结论只审查组合后的两个配置文件及其保护面，不代签完整 npm check、新同版双指定审查、原 15 finding 的最终处理或父/发布门。

## 固定范围与身份

T01 来源提交 `a982df8e63cc43ff0d52ed914dbe9003fa48fae9` 的 parent 是 `a570cd2b5e2edd53fd5e8be09ae29f271583df43`。本线实际组合提交为 `0de7c2fa7774fddb9366e029d01a8f6a86830670`，parent 为 `17b7917a5423f457defbe5cd0ee5b74ef9665bee`。独立 `git diff-tree` 确认本次组合仅修改 `.prettierignore`、`pyproject.toml`，两者当前 bytes = 组合 Git blob = T01 来源 blob。

| 配置 | before bytes / SHA256 | 当前 bytes / SHA256 |
| --- | --- | --- |
| .prettierignore | 442 / `82535615400927072d276a731f4c3f1869d882b45d826f3dd569132b04387b4c` | 1538 / `d3b8fe262361e4bdb5fa0950d91b45974ea08853d0fb52e2f8cab5ba799969ef` |
| pyproject.toml | 494 / `55674b4f13c4185b5db8629db363aed3e506df836ed0d7e67dcfe7db8154ea63` | 2593 / `4920e570bf5adb5fccb135bbc9ee5c3000279fb4896f126f182a888005724d3d` |

已阅读 root 的 `.private/T05-O15-exact-config-scope-controller-audit-20261023.md` 及本树实际配置/命令和八份历史 Python 文本。该先行报告的 oracle 旧 proposal hash 不用于冻结本候选；本审独立核当前 oracle 的 `374f223f...` 身份如下。

## 精确 Prettier 范围

新增恰为以下 15 个唯一根锚文件路径，没有新增 glob、目录或否定模式；全部对应实际文件。前 10 个历史文档当前 = a570 = 组合前 Git = 组合后 Git。后 5 个正常生成 JSON 完整解析后按现有 stdlib `ensure_ascii=True/sort_keys=True/indent=2/LF` 序列化，逐字还原当前 bytes。此项只证明保留既有存储字节的范围，没有重跑 builder 或从 actual 补 expected。

- `/docs/iterations/T05/projection-R3-receiving/137-gap-ledger.json`
- `/docs/iterations/T05/projection-R3-receiving/37-receiving-matrix.json`
- `/docs/iterations/T05/projection-R3-receiving/85-graph-slot-index.json`
- `/docs/iterations/T05/projection-R3-receiving/candidate-coverage-matrix.json`
- `/docs/iterations/T05/projection-R3-receiving/designated-review-backlog.json`
- `/docs/iterations/T05/projection-R3-receiving/designated-review-backlog.md`
- `/docs/iterations/T05/projection-R3-receiving/full-review-packages.md`
- `/docs/iterations/T05/projection-R3-receiving/gap-table.md`
- `/docs/iterations/T05/projection-R3-receiving/receiving.md`
- `/docs/iterations/T05/projection-R3-receiving/source-authoring-dependencies.json`
- `/tests/fixtures/quality/i05-source-package-oracle/budget-gaps.json`
- `/tests/fixtures/quality/i05-source-package-oracle/coverage.json`
- `/tests/fixtures/quality/i05-source-package-oracle/oracle.json`
- `/tests/fixtures/quality/i05-source-package-oracle/schema.json`
- `/tests/fixtures/quality/i05-source-package-oracle/sources.json`

原有 `.prettierignore` 部分完整保留，既有 `docs/reviews` 排除不是本次新增。活跃 `docs/iterations/T05/source-package-oracle/field-policies.md` 未被新增排除，仍按现行格式规则处理。五个生成物的格式例外不改变 builder/test/--check 的执行命令和完整语义字节检查。

## 精确 Ruff 范围及已知风险

TOML 成功解析。`[tool.ruff.format].exclude` 恰八个精确历史文件，`[tool.ruff.lint.per-file-ignores]` 恰同八个 key，共 26 个规则 membership：

| 精确相对路径 | lint 规则 |
| --- | --- |
| `docs/reviews/T05/projection-R3-receiving/O-launch-dispatch/complete-scope-result/check-protected-stat-only.py` | `B023`, `E501`, `I001`, `UP017` |
| `docs/reviews/T05/projection-R3-receiving/O-launch-dispatch/final-followup/check-protected-stat-only.py` | `B023`, `E501`, `I001`, `UP017` |
| `docs/reviews/T05/projection-R3-receiving/O-launch-dispatch/normal-recovery-dispatch/check-protected-stat-only.py` | `B023`, `E501`, `I001`, `UP017` |
| `docs/reviews/T05/projection-R3-receiving/O-launch-dispatch/official-minimal-readback/check-protected-stat-only.py` | `B023`, `E501`, `I001`, `UP017` |
| `docs/reviews/T05/projection-R3-receiving/O-launch-dispatch/post-intake-terminal-readback/check-protected-stat-only.py` | `B023`, `E501`, `I001`, `UP017` |
| `docs/reviews/T05/projection-R3-receiving/O-launch-preparation/minimax/verify-launch-input.py` | `E501`, `I001` |
| `docs/reviews/T05/projection-R3-receiving/O-launch-preparation/verify-launch-input.py` | `E501`, `I001` |
| `docs/reviews/T05/projection-R3-receiving/O-launch-preparation/zcode/verify-launch-input.py` | `E501`, `I001` |

五个 checker 均 4472B / SHA256 `58807b1a72415745e6f542b816d8922e593cd26cec4d1c91e426e0b673075647`；三个 verifier 均 7383B / `5edd9178273d9b47e7e15cf8243a287ef3c84915e00a0e834d94741bf7799ef0`。八份 current bytes = a570 = 组合前 Git = 组合后 Git，AST 全部可解析。只读取文本/解析 AST，没有运行旧 helper，也没有访问它们指向的两棵模型审查树。

移除新 TOML 的 format 节点和 lint.per-file-ignores 节点后，整个 TOML 解析结构与组合 parent 完全相等：没有全局 ignore、全目录 exclude、规则 select/target-version/line-length、pytest 选择、依赖或 workspace 改动。配置 key 没有通配符，active builder/test/recorder、environment-setup/run-full-check 及产品源码不在这八项例外中。

先行审计记录的原 77 条静态诊断（含 15 条 B023）本审未重跑，也不称已修复。五份 checker 循环内闭包引用 root 的原代码保持，B023 是语义风险规则；本次只按已授权档案身份保留其历史字节与 15 条显式例外，不能将“lint 不再报这几条”称作闭包修复或安全执行证明。未来执行复用需活跃副本和对应验证。其余 F/B 规则继续适用。

## 与已审自有源码/数据的实际组合保护

下列四源及五 JSON 均逐字核为 current = 组合 parent Git = 组合后 Git；与上一独审最终 hash 一致。本次配置没有改它们或重建数据。

| 路径 | bytes | SHA256 |
| --- | ---: | --- |
| `scripts/build-i05-source-package-oracle.py` | 129742 | `5f6c18e305ac1f6355b6cc89c7761082b6dca8c74479908db6ff305c0860a2bd` |
| `scripts/test-i05-source-package-oracle.py` | 46930 | `927a8336174c6b71cdb70271c898238ba2d47ab12338776dfb2d6918472a8076` |
| `docs/reviews/T05/source-package-oracle/record-command.py` | 2424 | `03b196afb1027fc9c9642a21be379798d962ac48ef5c79a2cdc7e607b6c4517a` |
| `docs/iterations/T05/source-package-oracle/field-policies.md` | 11719 | `b1af685230e759adea3de8a549772f48f0853ad47931237cac926f7fa2f4fcbd` |
| `tests/fixtures/quality/i05-source-package-oracle/oracle.json` | 5938727 | `374f223f7348ee982077ba75c8a0403a2edf71fab373612ea29b4e325b2014b7` |
| `tests/fixtures/quality/i05-source-package-oracle/schema.json` | 10220 | `2c1fefc9a675cf685bb7c31545ca1070dadd3845ce093c648f1c59dbc08a9f6f` |
| `tests/fixtures/quality/i05-source-package-oracle/sources.json` | 79253 | `b06bef47a15fde1953b638d5a233a054d139b4fa844a89395c510434c2522402` |
| `tests/fixtures/quality/i05-source-package-oracle/coverage.json` | 154032 | `95d7395761fbabe97c1fd81d1d05eb44bb8094f7266d977de42fdff349d28bd9` |
| `tests/fixtures/quality/i05-source-package-oracle/budget-gaps.json` | 362492 | `e68188ddefae4488fa6cf7762549508b78a3d87551f27cb24b9c9998f7948e9d` |

`package.json`、`package-lock.json`、`uv.lock` 当前 = a570 = 组合 parent = 组合后 Git；实际 full check、format:check、engine:check、测试及构建命令未改，没有 skip/deselect 或锁/版本绕过。

完整 JSON 静态解析确认 417 observations/320 datasets、280 specified/137 pending、declaredAllocation 88 specified/26 pending/2 not-invoked，wholeOracleComplete=false。coverage/budget-gaps 与原基线字节不变。原 15 意见、137 pending、26 声明缺件的门未被此配置“刷绿”；旧局部独审原文及结论未改。

## 实际方法与结论边界

本次只做 Git diff/blob/parent/path 核对、SHA/bytes、JSON 完整解析及序列化关系、AST 解析、TOML 结构比较。没有重新运行原 oracle、产品测试、完整 npm check、旧 helper、native/GUI、模型、网络、安装或 DB。owner 当前完整 check 的结果须由其实际流另行记录，本报告不提前宣布它通过。

精确 15 根锚路径、八历史 Python 的 26 规则 membership 与已授权范围一致；原 77/15 B023 仅作为保留的档案风险，活跃语义检查与四源/五 JSON 未改变。组合配置未发现新的越界或业务 delta。全新同候选完整输入双指定审查、原 finding 最终处理、包内/生产及父/发布门继续按各自实际证据执行。
