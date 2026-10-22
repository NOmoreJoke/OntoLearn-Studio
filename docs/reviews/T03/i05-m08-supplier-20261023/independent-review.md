# M08 三路径供方独立终审

结论：冻结产品 `4e752177f3e350d0be94ed063aca2e866dbf7970` 相对 `2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64` 的三路径依赖声明、锁闭包及实际包文件收集可作有限通过；未发现这三路径需要阻断交付的静态缺陷。整体验证未通过，不能据此宣布 I05 完成、frozen runtime 可用或源/包 parity 通过。

## 审查范围与方法

独立审查仅读取固定产品 diff、指定原始证据及最终补充证据、所引实际日志和实际安装/包文件；使用 Git 只读查询、stdlib TOML/JSON/邮件头解析及字节哈希。全文读取验证 receipt、包审计 JSON、审计 helper 源码、pytest 首失败日志、正常 package:dir 日志和修订接口方案；其余日志核记录的 bytes/SHA，不声称全文诊断。未执行 resolver/install/build/engine/pytest/GUI/parity，也未执行该审计 helper。唯一写入是本报告，未修改、暂存或提交产品、I05、旧 6891/2cf 或 AGENTS。

运行证据对应当时 HEAD 为 2cf、三条已授权产品路径尚未提交的状态；独立核其记录字节与随后 4e752 的 Git blob、当前文件完全一致。不能改称所有命令是在已提交 4e752 上启动。受保护 AGENTS 为 15147B，SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。

## 产品与实际供应证据

冻结 diff 恰为 `packages/engine/pyproject.toml`、`uv.lock`、`scripts/build-engine.mjs`；未改 probe、expected、guard 或样例。

- manifest 显式增加 pyparsing 3.3.3、pyshacl 0.30.1，保留 rdflib 7.6.0。pyparsing 之前已通过 rdflib 传递可达，本次修复其直接消费声明，不能再称原来缺包。
- activated extras 闭包为 engine + 八外部包：pyparsing 3.3.3、pyshacl 0.30.1、rdflib 7.6.0、owlrl 7.6.2、packaging 26.3、prettytable 3.18.0、wcwidth 0.9.2、html5rdf 1.2.1。pyshacl 激活 rdflib 的 html extra，指向 html5rdf。
- lock 总条目从 18 增至 23，仅新增 html5rdf/owlrl/prettytable/pyshacl/wcwidth；既有条目仅 engine 声明和 rdflib html edge 改变，其余既有条目及非 package 顶层结构相同，无删除或其他版本升级。总 23 条不等于运行八包，也不等于全产品许可结论。
- receipt 保留了 wcwidth 0.9.3 的被拒中间尝试和后续实际固定八版本 resolver、lock check、最终 frozen sync 的 exit 0，未将中间安装冒充最终供应。当前两 pin 的字节身份与此前允许读取的旧两文件一致；锁同 hash 本身不是生成过程证明，生成过程依据实际命令日志。
- build 保留 rdflib 收集、engine data、原 contracts、provenance/uv.lock；补 pyshacl/owlrl/html5rdf collect-all 及八包 metadata。正常 package:dir 实际 exit 0，产出未签名 macOS arm64 目录包。

独立重算最终 v2 包审计中的全部 65 个文件身份记录（首审计 63 个记录也已核），并解析八份包内 METADATA 的 Name/Version，均吻合。31 对 source/package 文件逐字节一致：八 metadata、十一份实际许可证/notice（包括 html5rdf 的 AUTHORS.rst）、两原 JSON、九份 contracts 和 lock。首审计只按 LICENSE/COPYING 文件名计十份，本独审额外检查 METADATA 声明的 License-File，确认 AUTHORS.rst 也实际同字节入包；root 随后仅补强文档审计 helper，逐 header 声明验证并产出 v2，保留首审计不变；wcwidth 本次存在真实 LICENSE，不继承旧例外。此为这些供应文件的收集核验，不作法律许可批准。

额外按安装目录独立枚举非代码数据（排除 .py/.pyc/.pyo/.so/.dylib 与 **pycache**）：pyshacl 十份、rdflib 一份全部实际同字节入包；owlrl/html5rdf 无此类安装数据。八包 PYZ code inventory、wcwidth `_wcwidth_c.abi3.so`、Python cookie 312/共享库由静态包审计提供；本审查再核实际 launcher、native 文件和共享库的记录字节哈希。文件和目录存在不能升级为 frozen import、native 加载或 loader code 与源字节的运行绑定证明。

两原输入分别为 21202B/SHA `0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a`、8205267B/SHA `47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa`；未解析大样例内容、未重生成 oracle。

## 实际失败与未完成边界

receipt 的全部 17 条原日志及新增第 18 份声明许可证静态审计日志 bytes/SHA 均与实际日志吻合；两版文档包审计各与对应原始输出 JSON 语义完全一致，格式化导致不同文件长度/hash。最终 helper 源码已全文复核，仅新增声明 License-File 解析、安装路径内约束及真实包字节比较；本独审没有运行 helper 或任何产品。

- npm check exit 1，停于三文件 prettier；其链后续项没有因此执行。engine:check exit 1，189 条 ruff 错误使其 && 后续 format/pytest 未执行。相关产品文件未在本三路径 diff 内，未在本审查重跑基线证明具体因果。
- 分开的实际 typecheck、npm test（15 文件/630 测试）、build、verify:sources（12 输入）及 package:dir 记录通过；不能替代失败的整体 check。
- root 后续明确允许既有 pytest 自然结束；原日志 1175 collected，1167 passed、8 failed、204.47s，exit 1。八 fail 全在固定 `test_semantic_source_package_probe.py`，包括 full_run status 1、unexpected-failure、缺少 observation、未产出 fullview/dag、restore 期望失败及 dict.kind AttributeError。没有重测、改 probe/expected/guard 或把失败回填为通过，也不能仅据三路径 diff 判定失败已修复或根因已证明。
- canonical/full-v1 确已实际执行，失败轨迹给出 status 1。B1 mandatory fixture 在已执行测试文件内，但默认 dot/F 日志缺少逐 selector 独立 exit；两 B1 selector 结果保持 UNKNOWN，不凭八个失败名中未出现它们而签通过。
- frozen supplier import/loader、完整同固定输入源/包 CLI parity、最新 401a 集成后的完整候选、新 native/GUI/physical 证据均未建立。本三路径授权不要求擅扩 reader/entrypoint 或为补证而启动 parity；后续需要各自授权和真实结果。

本报告不关闭 417 observations / unresolved 5、平台、producer、mapping/protocol WIP 或其他既有门。

## 修订接口方案评审（仅方案）

以最终修订的 7518B 方案为准：T03 的既有 build 追加行为与三个额外产品路径（既有 entrypoint、新 reader、新 reader tests）和 I05 唯一 probe writer/test 路径已分清；I05 测试明确为 `packages/engine/tests/test_semantic_source_package_probe.py`。不得据本报告实施这些路径。

信任方向现在明确：真正运行批准来自 root 在运行前冻结的外部 binding SHA 与完整实际产物清单；包内 provenance/anchor 一致本身不能证明 root 批准。方案已关闭先前两处歧义：精确测试路径已列出；运行后只追加 receipt，原 binding 不覆盖不回填，代码/输入/产物改变必须先冻结新候选与不可变 binding 版本再验证。

当前没有新的方案阻断发现，但这仍是待实现、待授权的本地 hash 绑定方案。正式实现前仍须共同冻结严格字段/caps、具体外部冻结记录的交付与读取方式、最终 postintegration commit/全部路径身份、源与 frozen code 指纹归一化规则及负例测试。真实 loader/native 校验、运行前外部 inventory 校验和失败拒绝均需实测；不声称已有签名/PKI 信任根，不可沿用 2cf 的 probe 指纹作为 401a 集成后最终 pin。完整新候选仍按指定双审门禁执行。

## 输入身份

| 文件                                  | bytes | SHA-256                                                          |
| ------------------------------------- | ----: | ---------------------------------------------------------------- |
| packages/engine/pyproject.toml        |   398 | bcc8825b1f2902a66ae539e687df57e5b2554247f48a48a65215601a77958365 |
| uv.lock                               | 28440 | 86dfe82d952e2c88edcfc5658f488f6e1f0d04b4ec3b1e6f5c5d3bc4f57e8b73 |
| scripts/build-engine.mjs              |  1574 | 0b999721e7ab2dde7ebbc831982cd398cb7d4af7219a49802a0f82c77b1d332c |
| validation-receipt.json（最终）       | 17783 | fc249e62f858cb26ba58bb73428a6d2c546b56ab4deed904ab120b793be46746 |
| actual-package-static-audit.json      | 30244 | 90141de0853d5f93f90724a510aa78333d185b8ff6185cb19f5c4f4065a12715 |
| actual-package-static-audit-v2.json   | 30823 | d6ced45a36890560d537e06ffaeabb3c704c9e68fd0cf9882e38e4dbf68e9bde |
| pytest-first-failure.log              | 15886 | 62b3e3989a16dc19787686af7debc81d04aa05d8045577f3e4f28d4f927f139e |
| audit-packaged-supplier.py（最终）    |  5293 | 37bed088e4d5e4569804f50b90863db705d8cba9ca9c04832dbd2ab477f91781 |
| provenance-entrypoint-plan.md（最终） |  7518 | 03539597bd42bb333526851cd73a6388e632deff84b034a804ab5944692ea16e |
