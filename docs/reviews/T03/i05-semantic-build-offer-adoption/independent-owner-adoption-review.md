# T03 I05 设计接收候选：提交后独立静态复核

2026-10-22。结论：**固定候选有限静态 PASS，可将原 T03 的纯设计接收及 A1–A4 作为后继 D0 文档窗口的依据；原两份 schema 原样实施仍为 needs-change。** 未发现阻断本次设计接收的新问题。本报告由提交后的新独立审查作者撰写，不是 helper 拟稿作者的自审，不代 root 批准实际组合，也不授予实施、安装、构建、外部见证生产、consumer 或任何运行权限。

## 固定对象与完整性

- 唯一工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-i05-semantic-offer-owner-review`；branch：`docs/T03-i05-semantic-offer-owner-review`。
- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`；实际受审候选及读取时 HEAD：`3b22196e468c3a7d8b99a1717f9526c07d9e78b7`。
- 独立核本候选 7 payload / 62,975 B，逐件 current = 固定候选 Git = candidate-manifest；清单自身 1,832 B / SHA-256 `a30aa2021104f1820595eecef27faca755a47b76a2f564c682e89d191b8d3294`，也与固定 Git 相同。base→candidate 恰新增本次 adoption 与 review 前缀的 8 件，无产品路径变化。
- 四 writer `packages/engine/pyproject.toml`、`uv.lock`、`scripts/build-engine.mjs`、`packages/engine/entrypoint.py` 各自 current = candidate Git = base，逐 byte 核同。AGENTS 仍为唯一既有保护 M，15,852 B / SHA-256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`；index 空。
- 固定 offer candidate：`6ba273a892b18a5ebaedc07aea6f36584999adcf`；process：`21f9d4d288e8bd462b2252018578590110c08691`。offer 主文实核 55,286 B / SHA-256 `9a48791f24e3b9149d3416a82284248092bce113d9c0f269a62b5887a2fb4c09`。原 offer 47 件不写、不复制改造；总控 47 件的 current/Git/manifest 核同沿用固定限定 closure，本轮没有重复该全量审计。

## 实际阅读与证据边界

先全文读取当前 AGENTS、仓库外 `T03-i05-semantic-offer-owner-review-window.md`、`I05-semantic-build-offer-limited-root-closure.md` 和 `T03-i05-semantic-offer-owner-review-setup-proof.json`。全文读取当前候选 8 件：adoption、owner-acceptance、owner-design-review、input-evidence、旧 helper final-manifest/final-validation、owner-candidate-static-checks 和 candidate-manifest。

全文读取固定 offer 主文 O（L1–266）、descriptor P（L1–540）、build provenance schema B、final receipt schema F（L1–262），以及固定 process 的 delivery、R1、R2、final-manifest。B 从完整 Git JSON buffer 解析后，显示并阅读所有顶层字段、全部 17 个 properties 与全部 6 个 `$defs` 的完整结构和值；未把解析成功当 schema validator 或协议实现。主文和 descriptor 使用有界连续片段补齐；初次合并输出曾截断，delivery/manifest 和 descriptor 均重新单独显示补全，候选 adoption §4–末尾也补读，没有把被截断内容当全文。

有限源码抽核仅为固定 `2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64` probe 的 L1–115、L572–706，以及固定 `6891a5842302859a531cf82767c5a482417bc274` resources 的全文 L1–97；只读取文本。没有本轮重读 helper 所引 M0/ADR/合同全部原文，也没有把 helper 的抽核范围扩大为本人的阅读证据。106 命名来源、43 guard（30 同 / 13 异）、33 路径和 417 有序清单采用固定 R1/R2 的独立结论，不再审计完整源集、旧 binary、tool payload、SDK 或 witness。T05 3d8f4ee 的 417/37、280 specified / 137 pending 与未独审状态来自本窗口及 owner 明示，不是本人读取新 oracle 后的接收结论。

## 接收范围与逐项复核

### 1. owner 接收确实存在，且没有转移维护权或发执行票

owner-acceptance 开头及“全部发现的 owner 处置”明确采用 adoption §2 与 §3 A1–A4。adoption、owner-design-review、旧 final-manifest/final-validation 的“尚未接收 / 未提交”是 helper 阶段历史，owner-acceptance 明示其历史身份且不覆盖原件。candidate-manifest 将它们作为原字节保全输入；owner-candidate-static-checks 明示提交后独审尚待本轮完成。因此历史记录不是当前接收状态的第二个终态，也没有被伪称为本次独审。

原 T03 仍是四 writer / 唯一锁维护者；T01 公共资源、I05 probe/消费 delta、T05 oracle 仍归原 owner。实际组合沿 dependency → consumer → wrapper → root/owner 审实际 composition 的顺序冻结，不取任意 HEAD、不跨树拼绿。D0 先冻结新 schema/descriptor/consumer 规范的精确版本、路径、hash 和责任；D1–D3/E0–E4 均需各自精确新窗。本件独立于 R7 native 票，不以本设计 PASS 解除原写锁、HOLD 或计量限制。

### 2. AD-01 / A1：bootloader 与两根路径域的反例有原文支持

O §3.2 的 executable 位于 bundle 根，`_internal` 对应 `_MEIPASS`；O §4.1 的 runtime resource/data mappings 却为 `_MEIPASS` 相对。B `properties.runtimeComponents.items.properties.kind` 包括 `pyinstaller-bootloader`，其 bundleFiles 只是受限 file；F executable 才另含 bundle 根文件。根 executable 不能由禁止 `..` 的 `_MEIPASS` 文件域真实指认，副本也不是实际启动体。该反例是字段可表示性的静态推理，不假称检查过实际包。

A1 固定所有最终普通文件为 bundle-root、payload 为 meipass-root，同文件跨账要求 `_internal/` 前缀和 bytes/SHA 核同，bootloader 指向 F 中同一 executable；不造 bootloader 独立文件。源、installed、外部证据路径另域，拒绝逃逸及平台别名；probe 固定资源/资产/锁路径能力不扩大。该改动足以指导 D0 修订，当前原 schema 并未因此自动修复。

### 3. AD-02 / A2：实际容器链、第四函数与 checker 阶段分域可成立

B archives 仅 path/kind/bytes/SHA/inventory，`$defs.module.actualArchiveCode` 仅 archivePath/archiveSha256/memberName；对 executable CArchive 内的 PYZ member，缺父容器关联，不能以虚构普通文件或 `exe!PYZ` 任意 locator 填补。A2 采用封闭 archiveId、已列父容器和 exact member、先父后子 / 无环 / 唯一 / 受限深度 / 完整 TOC，并区分实际普通文件与外部 raw witness。actual 布局超此批准范围必须先报版本 delta，不自动扩成任意递归定位器。

四函数条目的原 schema 有 moduleName、索引和 expected/actual fingerprint，却没有对 `pyshacl.validator` 的独立强制实际 archive module 绑定。probe L652 附近确从该模块导入 Validator 并观测 `Validator.run.__code__`，不属于 descriptor 的 23 canonical。A2 单列 distributionCodeBinding，再让四 function 引既有 module binding、按同一 co_consts 索引分别遍历 source-compiled / actual-extracted module，能补足此关联，不扩 canonical 集或把 source SHA 填为 code。

resources L14–20 确使用原 `resources.CONTRACT`，未注册 sys.modules。A2.5 保 checker 为 bundle data：构建期只比较批准源与 bundle data bytes/source compile expected；真实 loader 观测属于后继 caller/header/runtime。B 原 `dynamicChecker.loaderCode` 的 builder 阶段歧义因此被明确标为新版本修订，不能用 builder completion 预签 runtime/cache。`marshalReferenceStability`、CodeType/get_code、同 Python build/cacheTag/optimization 和 cold/warm/cache 的稳定性仍待获准真实证据，未以本次静态审收件。

**非阻断澄清 N-01。** adoption §5 E0 将“sourcecompile↔actual archive 所有23/bootstrap/四函数/checker”压在一句，单读会把 checker 也理解为必须存在 archive code。该简写须按同件 §3 A2.5 及 owner-acceptance 的明确分域解释：23/bootstrap/四函数核 actual archive；checker 核批准源↔bundle data 的 expected code，actual runtime loader 在 E1。建议 D0 在实际新规范中拆成这两句，不要求 checker 凭空进 PYZ，不声称构建时已观测 runtime。由于当前候选已明确采纳 A2.5、没有实施授权，此处不阻断纯设计接收，也不允许据该简写降低后继证据门。

### 4. AD-03 / A3–A4：安装行保全与收据无环约束适当

B installedRelativePath 缺安装根与原 RECORD 行的明确关联；A3 将原行完整保全为证据数据，另用批准根 ID 与根内规范路径，只允许解析到该批准环境内的实际文件。所有行逐项 disposition，runtime 必需不得 omit，bundled 非空 mapping，非 runtime/build-only 理由仍需 owner 审。该约束没有把原 RECORD 数据变成 probe locator。本轮没有读取 installed 环境或真实 RECORD，不据此断言某已安装库发生缺件/逃逸。

F runtimeValidation / nullable runtimeEvidenceManifest 原本无充分跨字段闭口；A4 将 build receipt 固定 not-executed/null，后出的 validation receipt 引原 build receipt hash、完整 runtime manifest 和 comparator/oracle，compared 与 matched 分判。后置 provenance → 包外全目录 manifest → 包外 build receipt → 过程 commit 无反向自身 hash；后续运行不回填已批准 build receipt/provenance。D0 仍须定义实际新 schema/version/path/hash，当前不存在已实现 validation receipt 的承诺。

### 5. actor、exact argv / 错误码、代码域与原验收没有缩减

O §4.3.1、P verificationActors 与 adoption §4 保 T03 产真实来源/归档/安装/许可见证，root 审批准组合，caller launch 前核批准 receipt 与完整目录、launch 后回绑 header，probe 只核声明/bundle/actual loader，保持 external-unverified。外部路径只作受限数据，probe 不读原 Git、installed、log、receipt，不自签批准。source 第23自身 bytes/code 由 caller 对批准 pin 核，不嵌自 hash。严格三个 exact selector/argv、前置 exit2、未知异常 INTERNAL_ERROR/exit1、不完整/真实 signal 均保留；新增 exact code 明示尚未实现，不擅改公共 errors catalog。

Git source、installed artifact/RECORD、actual archive raw member/code、runtime actual loader/function 四域独立；eight distributions 和 Python/stdlib/bootloader/native/platform runtime 分账，完整 marker/extra/各平台 artifact 与原字节许可/NOTICE/COPYING 不由版本或字符串替代。parent 默认入口/旧 flag/43 guard 保留，独立 profile 不代 parent package:dir。

完整 source / 独立包 / parent suite、417 全有序观察 / 320 datasets、83数学 / 106操作 / 54checks / 50产品上下文、typed 费用与库分类缺口、T05 137 pending 与未独审、原失败/未执行状态均未升级。source=package 与独立 oracle/原操作通过分判；另12 B1 fresh 不填原12 S1 snapshot 指标。SQLite 损坏输入 HOLD、被拒物理方法、whole-H/owner、正式 Job/Store/selected、57P0/C–G/PRD10–12/六迭代、指定同版双审、CI、两 OS、真人、develop 和远端门全部保留。

## 验证、限制与交付

本轮仅普通文件/Git、stdlib JSON/hash/算术与已有 Prettier 文档格式。实际 bytes/hash、candidate 精确路径集、四 writer 与 AGENTS 身份、index 和 whitespace 结果记录在同名 proof。没有运行 JSONSchema validator；没有 import/执行产品、probe、builder/spec/reader/helper/局部函数/fixture/模拟、pytest、业务 compile/py_compile、archive 解码、安装/version/capability 探针、network/DB/native/GUI；没有执行候选里的 static-verify 等资料脚本，没有读旧 binary/tool payload/SDK/witness。没有写别树、stage/commit/push/PRmerge、新 Goal 或用户 chat。

PASS 只覆盖固定文档候选的设计接收一致性、最小增补合理性和保留边界，既不把未运行本身判为设计失败，也不产生产品运行、source-package 等价、实际 loader/cache、许可入包、性能或发布通过结论。原两 schema needs-change 和后继 D0 独审条件继续有效；本报告不维护项目完成度、不代指定双方外审。仅新增本报告及同名 proof，报告最终 bytes/SHA 由 proof 及回报给原 T03 的结果绑定，避免报告自 hash 循环。写定后停止新增写入，等待原 T03 逐项处置及过程交付。
