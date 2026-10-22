# I05 retained source triage 独立审查 R1

结论：修复准备方向与权限分工可继续；发现 1 条 P3 文档精度问题，须后出登记更正。没有发现要求 I05 越权修改共享依赖或存储面的设计问题。本结论仅覆盖本次静态 triage 与最小修复计划，不是产品验收、完整工程审查或指定双审通过。

## 固定对象与审查范围

- tree：`.worktrees/I05-retained-source-review-triage`；分支：`fix/I05-retained-source-review-triage`；实际 HEAD：`2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64`。
- 六个输入的 bytes/SHA256 全部与派工固定值一致，完整清单见 `independent-triage-r1-proof.json`。六个输入保持原字节。
- 读现行本 tree 的 AGENTS；只新增本目录 `independent-triage-r1-*`。不 stage、不 commit，不改 root 持有的 index、原 source、旧 packet、原报告和状态。
- 旧材料只用授权的两 wrapper 首/续终态 owner 报告与 reviewer-status 共八件；八件身份均核对。M own-input manifest 只用于成员路径/ref/blob/bytes/SHA 元数据核对，未读取其 materialized 源码正文。

## 发现

### R1-P3-01：M08 disposition 混淆锁成员缺失与引擎依赖闭包缺失

位置：`opinion-association-matrix.json` 的 `currentOpinionRows[id=R2-MY-08].disposition`，原句：`2cf lacks pyshacl and5 required distributions`。

该句可能被读为“除 pyshacl 外另缺五个 distribution”，也没有说明“锁成员”与“引擎闭包”的不同分母。固定 2cf 的八包要求中：

| 核对集合                                               | 缺失数 | 精确缺失成员                                              |
| ------------------------------------------------------ | ------ | --------------------------------------------------------- |
| 整份 uv.lock 的 distribution 名称                      | 5      | html5rdf、owlrl、prettytable、pyshacl、wcwidth            |
| 从 ontolearn-engine 出发的 runtime 闭包，含激活 extras | 6      | html5rdf、owlrl、packaging、prettytable、pyshacl、wcwidth |

`packaging==26.3` 在整锁存在，却不在候选 engine 闭包可达；`pyparsing==3.3.3` 经 rdflib 已可达。建议后出 errata 明确写“候选锁缺五个要求成员（含 pyshacl）；引擎 runtime 闭包缺六个（另含 packaging）”，保留本次六个输入原字节。

严重度建议 P3：核心缺口、pyparsing 澄清、T03 owner 路由与执行限制都正确；问题是影响后续验收口径的集合措辞，未证明新增产品运行缺陷。根已确认以独立后出 errata 登记，不修改本次封审对象。

## 独立核验结果

### M08：静态依赖事实成立，extras 更正正确

以 stdlib TOML 解析固定 2cf 与 `6891a5842302859a531cf82767c5a482417bc274` 的 engine pyproject 与 uv.lock；两模块只解析 AST 顶层 import，不研究算法或执行模块。

- 2cf 直接依赖只有 `rdflib==7.6.0`，semantic.py:13 顶层导入 pyshacl.validator.Validator；候选锁没有 pyshacl。semantic_query.py:5 顶层导入 pyparsing，但后者经 RDFLib 可达，不能登记为候选缺包。
- 供应直接依赖为 pyparsing==3.3.3、pyshacl==0.30.1、rdflib==7.6.0。独立闭包传播确认 pyshacl → rdflib[html] → html5rdf：八个要求 distribution 全部可达；闭包另含根 ontolearn-engine，共九成员。
- `m08-static-facts.json` 原始不含 extras 的闭包也可重现；后出 correction 正确替换其闭包口径。原记录保持，解析遗漏不归为产品缺陷。
- 两份 manifest 的 Python 要求均为 `>=3.12,<3.13`。锁/闭包核验不代表环境实际已安装或 import 成功，版本 gate 不代表实际机器解释器错误。
- 计划将 manifest、锁、build/provenance/打包写入归 T03 唯一维护并经根协调，未把旧供应输入自动等同当前正式交付合同，边界正确。

### M09：继承的有限事实成立，正式边界可达性仍未知

独立获取固定 2cf 与批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3` 的 storage.py/job_store.py，确认两文件各与 base 同字节。只解释事实文件指定行段；errors.json 只解释 `/codes/OWNERSHIP_CONFLICT` 项。

- Conflict.code 映射没有 ownership；四个指定 ownership 抛点成立。
- JobStore._application 捕获 ownership 后另铸不透明 identity，持久化受限 detail，并带 detailRef 发 OWNERSHIP_CONFLICT。
- 目录要求 detailRef；仅加映射会漏掉这个必填参数，不能机械修码。
- 未扩大读取其他 storage 算法，也未证明绕过包装的正式跨边界路径可达。计划将判断/必要修复交根唯一路由 T01、保留 SQLite 损坏输入/物理保护 HOLD，处理审慎且充分。

### 矩阵、范围与最小修复计划

- M 的首轮七条、续审九条逐字段与两个原 status 对齐；矩阵保留 M01–M09 共九条及 Z 的 F-1/F-2/O-1/O-2，共十三条，均未被 triage 自动关闭。M 首/续 NotPass 保留。
- 首/续差异、M07 标量身份更正、三处原指纹差、历史 closed/static 与运行门分别保留；Z 首/续报告所示源码级关闭、M 对相同意见仍 open 的差异没有被裁成整体通过。
- Z 旧静态 Pass 的语义中段 550–1203、四 profile 内部、contract_v2 与桌面大文件深度缺口保留。下一轮两全新真实指定模型任务要求完整工程、retained 原范围与 queued diff 正文，不能只审 patch 或以 metadata 分组计数代替实际阅读。
- 完整遍历并逐项比较 inventory 与授权 manifest 的 22,492 个成员元数据、856 个主树成员、16 个 namespace 计数、251 个精确 path/blob/bytes/SHA 代码组和全部 aliases。此为完整元数据比较，不是源码正文通读或新候选实际审查；八个 queued 分支仍列待审/明确后继处置，26 个未冻结项仍 opaque。
- 新候选要求四份正式政策在两输入中逐字节对称，M 1510B 补注仍 prepared/未送，不为它再续旧任务。Q5/F01/F16/Q8 未默认；政策、实现、样例和验收分开。
- M06 只提出自有 guard/失败边界测试方案，精确源文件修改范围尚待根交接；本轮无产品修改与测试执行。M03 不猜 canonical 出口，M04/M05 不以新七十函数替代旧测试，M07 新 lineage 无自嵌未来 hash 要求，均合理。

## 真实验证与限制

`independent-triage-r1-check.py` 为本审查新建的 stdlib 检查器，不运行作者旧 checker。实际 exit 0；stdout 187B，stderr 0B。双流原件与真实 exit 收据分别为 `independent-triage-r1-check-stdout.txt`、`independent-triage-r1-check-stderr.txt`、`independent-triage-r1-check-receipt.json`；固定 git show/rev-parse/branch 的返回码及 stdout bytes/SHA、真实 stderr 保存在 proof 的 commandReceipts。为遵守有限片段范围，不复制完整 storage 源码到报告。

格式仅使用指定 node + 指定 Prettier，范围限定本审查新建 MD/JSON，实际双流/exit 见 `independent-triage-r1-format-*` 与 `independent-triage-r1-prettier-check-*` 收据。

未执行产品、import、runtime、测试、npm/build/package、安装、resolver、网络、DB、native、GUI、Goal、push、CI、PR 或 merge。未向外审模型发送消息。未重查 D2 或无变化测试，未把旧实际材料误称本轮运行证据。此次只读过程中初始路径枚举返回了其他 AGENTS 路径名；未读取其正文，后续仅读本 tree 现行 AGENTS。
