# I05 protocol3 完整规范：fresh 独立审查

结论：**NEEDS_CHANGE（仅纯规范）**。固定候选 `d355d384470d6de30c28229945cb77a65cca3dd4` 有一项 **F1/P3**：profile 精确变更索引漏记新增的显式 null 属性。四份 schema、全部字段责任及其余依赖/guard 规范未发现新增阻断；本报告不授予产品采用、安装、构建或运行权，不替代指定双模型审查。

## 固定输入与身份

唯一工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-i05-semantic-offer-owner-review`，分支 `docs/T03-i05-semantic-offer-owner-review`。入口实际 HEAD 为 d355d384，原 base 为 `86d6297a8cac5ad780f1be4416ec9052b82f3aaf`；index 空，已有 tracked dirty 仅受保护 AGENTS.md（全文读取）。本独审只新增本报告和 `independent-review-checks.json`，不修改候选、不暂存或提交。

候选精确增加 45 个路径，全部在授权的两个 protocol-v3 prefix：44 payload 共 3,743,936B，candidate-manifest 自身 9,848B，SHA256 `eb91a976b6807b932b228618a68a35c9ac52e0a8ee4f63670a00471d0a9c5f2d`。全部 payload 均实核 current=固定 Git=manifest bytes/SHA；manifest 自身与固定 Git/SHA 相符。旧 D0 final-manifest 的 65 payload+自身、旧 D1 final-plan-manifest 的 27 payload+自身，共 94 个固定输入，独立核其精确集合、current/Git/原 manifest bytes/SHA 全同。没有覆盖旧 D0 66、D1 28、旧 Fail、产品、四 writer、锁、tests 或 CI。

已全文读取总控限定接收和 fixed-readback、D1 implementation/forward delta/schema 索引/guard 策略及完整独立 delta 报告。已读取本候选 protocol、consumer、guard 迁移与接口合同、作者报告、三个完整文档工具、首失败与全部不同日志原文。四 schema 使用完整 JSON，完整展示所有不同子树；完全相同重复子树以首见 JSON pointer 回指，并独立递归核形状、引用和逐值 delta。field responsibility 全部 1,241 行、依赖和 guard 全表均完整 JSON 解析并逐值核对固定来源；没有把数量或作者摘要当作完整性证明。

初次合并输出超预算产生截断，随后按连续片段和完全相同子树回指补齐；不以被截断部分声称已读。机器身份/结构核验与文本审读分别如上记录，不宣称重新审读原产品、原业务资产或受限载荷。

## F1 / P3：新增 null 属性未进入精确 profile 索引

**位置：** `docs/reviews/T03/i05-semantic-build-protocol-v3/materialize-documents.py:253-255`；生成结果 `docs/iterations/T03/i05-semantic-build-protocol-v3/profile-change-index.json:3` 的 changes 全集；实际新增属性在同目录 `profile-descriptor.json:658`。

**触发与证据：** 新 descriptor 新增 `independentParentProfile: null`，旧 D0 descriptor 不存在该键。生成器使用 `old_profile.get(key) != profile.get(key)` 判断变化；旧版不存在键与新版显式 null 都得到 None，故新增键被漏掉。独立 presence-aware 深度 diff 得 21 个新增或变化的顶层键，索引只列 20 个；唯一遗漏为 `#/independentParentProfile`。其它 20 行可核回相应旧/新值。

**影响：** 本交付要求 profile 的前向变化具有精确可审查索引，且原合同明确区分“缺字段”与“显式 null”。目前索引无法完整描述新 descriptor，有限 protocol-selfcheck 也没有检查索引相对 descriptor 的全集，因此其 exit0 未发现此遗漏。当前 null 没有伪造成实际 parent 批准，未观察到产品或运行权扩张；这是规范可追溯性问题，严重度 P3。

**建议：** 生成条件必须同时比较键是否存在，再比较值。新增行可沿现有结构明确 `pointer=#/independentParentProfile`、`old=null`、`new=null`、`newProperty=true`（或使用明确 absent 状态）；不能仅通过改 null 值来消差。增加有限文档检查：descriptor 的 presence-aware 全部差异与索引精确一一对应，并拒绝遗漏显式 null 新键、未索引的新键及伪称旧属性。保留本首报告和 d355 候选，修复后生成新候选供精确 delta 复核。

## 完整规范核验

四 schema 的独立递归 delta 恰为 D1 提案的 14 个版本 literal，外加 8 处 title/comment 描述元数据；所有其它 JSON 节点逐值同固定 D0。没有新增或删除实例字段、required/type/null/enum/union/refs，也没有扩大额外属性。共 203 个显式 object 节点仍 `additionalProperties=false` 且 properties/required 集合相等；3 个 local ref 均闭合。header/2 去掉文档 metadata 后与 receipt/3 内嵌 headerPayload 完整子树全同。

field responsibility/4 的 property index 精确为 provenance669、build receipt56、runtime receipt366、header150，合计 1,241 个唯一 pointer；全部 required=true、type/const/enum/$ref shape 与新 schema 逐项相等。相对旧 D0 仅 10 处索引 const、format 和 normativeCrossFieldRules 变化；actors、18 个 exact code、其余 index 值与责任均保留。

protocol/consumer 是完整新全文，包含原 CR-S/A1/A2/C/A3/A4/R/H，而非只交 delta 摘要。来源/路径域、真实普通文件与别名拒绝、closed archive 账、完整 TOC/raw witness、source/installed/RECORD/许可、同一 co_consts 路径与 exact CodeType、仅归一 co_filename 的完整 fingerprint、第四函数与 checker 原对象、外部批准先于 launch、无环后出收据、真实失败/false/null/observedPaths 与原 raw 保存都仍明确。build receipt 永久 not-executed/null、unapproved-produced-evidence；compared 与三项真实 boolean、full417 与 B1/S1/parent/正式门的差异没有被合并。

新 profile 对旧 canonical/resource/asset/hiddenImports/collectAll/copyMetadata/exclusions/function/path/code-domain/argv 等完整子树逐值相同。前22供源、第23 consumer 祖先与未来新 pin、23 actual/frozen、8 专用 runtime、33 专用源输入分清；新 lock26 不变成26 loader。现有 2cf、a4d 或历史 Pass 不被当成新 consumer、parent 或运行批准。

## 26 包与 45/33/58 作用域

独立从各 `originRef:uv.lock` 读取原文本并解析 TOML，逐包定位 `[[package]]` 完整原 block：26 个唯一名字/精确版本，所有 profile/mapping origin candidates 的完整原 block、bytes/SHA 及 143 条 artifact 来源 URL/hash/size 均核回；block 中 upload-time、registry、markers/extras/workspace/dev/build 等原字段没有因摘要表而丢失。保 profile 的 rdflib html→html5rdf、openpyxl→et-xmlfile；六直接项精确为 defusedxml、et-xmlfile、openpyxl、pyparsing、pyshacl、rdflib 对应既定版本。此为历史锁文本来源验证，没有下载 artifact 或证明 resolver/安装/许可证。

lock26、canonical23、source22、runtime8、source33 是不同维度；selectedInstalledArtifact、actualCombinedPackagePin、licenseApproved 和实际 dependency/combined lock/pyproject 均为 null。没有将拼接原 block 说成真实新锁，也没有把新三 XLSX 锁来源说成专用 semantic 已打包或获许可。

58 行 guard 完整逐值同已限定接收 D1 全表，包含全部 owner、原身份、作用域决策及停止前置。classification 为 shared-same13、conflict9（7 source/resource+2 dependency）、old-only21、new-only11、mapping-only4。historical45、dedicatedSemantic33、parentDefault58 的 applicable 精确集合与 descriptor 的 sourceGuardPaths 一致。历史 a4d 43+两 writer、23包及原83入口保持独立；新 semantic 不混 old-only/mapping；parent 不删除 old-only、不永拒旧 flag 假称保留，仍须真实 owner 兼容采用、旧83/default/S1/其它入口回归、独立完整 parent profile/依赖/许可与 root 批准。全部 future actual pins 和 scope source/output/env 根仍 null，executionAuthorization=false。

G02/G03 业务 carrier schema 没有被本作者抢写；接口合同只要求 I05 另作者提供同版固定输入、精确字段差异/投影/反例，共同接收后另窗实施。whole-H、SQLite 损坏 HOLD、417/B1/S1、57P0、CI/两 OS/真人/develop 等门保持待验，没有用纯规范关闭。

## 有限检查与首失败

作者的 document-selfcheck 与原 D0 工具逐字相同，唯一变化是新文档根路径；没有移除旧断言。54 旧负例和15有效变体的 id、顺序、mutation pointer/值类型完整保留，15 份 headerRawExamples 的实际 UTF-8 bytes/SHA 独立核同。原值中的新版本和合成摘要更新不冒真实证据。protocol-selfcheck 的26新增反例涵盖依赖删改、计数混用、原 block/artifact/extra 改动、guard 丢项或串域、假 pin/许可/运行权；这些是有限数据关系断言，且未覆盖 F1 的 presence 差异。

作者原日志逐件核 bytes/SHA，所有不同日志原文已读；重复日志以同 SHA 的首原件核同。保留 selfcheck-first exit1 的完整1140B stderr，原因是新合成 header 摘要引用未同步；后续修复仅更新合成引用，没有弱化原 checker。作者的最终有限检查和 formatter exit0 是已封存日志事实，不是本独审重新执行产品、通用 JSONSchema 引擎或真实 loader 的结论。本独审没有执行作者三个脚本。

本独审自身首错及完整 stderr 写入 independent-review-checks.json：默认 python3 无 stdlib tomllib（tool chunk 965d05），随后改用已有 Python3.12 做同类文档检查，没有安装或改变环境。第二次检查在 exact profile delta 比对触发 AssertionError（chunk 299bfe），后定位为 F1；未修改候选，余下独立检查分开完成。其它检查只用普通文件、只读 Git、stdlib JSON/hash/TOML/集合关系。没有产品 import、compile/pycompile、resolver/install、build/archive/collector/loader/DB/native/GUI、外部模型或 caller/fee WIP/SDK/二进制/witness/归档 payload 读取。

F1 修复并独立 delta 关闭前，不应将本候选整体标为规范通过。未发现其它需要产品改动的事项；运行、实际兼容、artifact/许可、批准信任机制及全部原父门仍属后继精确授权和验证范围。
