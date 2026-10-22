# I05 私有 provenance 合同独立前审

结论：信任链与四路径分工可行，尚需补齐两项私有接口定型后作为实现合同冻结。以下是合同歧义，不是已实施产品的新缺陷；不要求扩大产品范围、恢复任何旧测试或等待母 M0。

## 固定输入与范围

- 候选 HEAD：`7abab04b223b0c6ca9c290b5b6bd8a702971d2e9`；独立新树 `T03-i05-private-provenance`。
- 本轮合同全文读取 645 行、25545B，SHA `9a6f88a7ea0273f05a2fec706c5ae4745d449f76ffbbfb6c2ac66f42d09d8c11`。前一次组合输出截断后，已按 1–210、211–440、441–645 三段重新全文读取，未以截断阅读替代。
- 指定总控前审全文：`iteration-control/2026-10-21-weekly-release/.private/T03-M08-provenance-entrypoint-plan-controller-audit-20261023.md`，5866B，SHA `f8ce6a80474938619e1737708eec4576a8f9a62924cd7358a9e137dc67f95d7e`。未扫描该 private 目录其他文件。
- 已读实际 entrypoint/build 全文，以及 probe 的 precondition、code fingerprint、runtime import、observer 顺序和 main 返回值局部。没有读完整语义实现或大样例内容，不据局部阅读诊断原 8 项 pytest 失败。
- 当前 AGENTS 为 15147B / `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，受保护 overlay 未修改。

## 必须补齐的定型项

### C1：逐字段路径根与 source → artifact 映射未确定

`schemas` 内所有文件记录共用“relative POSIX、inside-declared-root”规则，但合同没有逐字段定义 declared root。`suppliers[*].path` 从旧 SUPPLIER_PINS 取到的值如 `semantic.py` 是包内相对路径，而 `fixedInputs[*].path` 明确为 `ontolearn_engine/probe_inputs/...`。`publicResources`、distribution metadata/licenses/files、contract、entrypoint 和 lock 的根及包内映射也没有一份完整对应表。

因此两个符合字面描述的实现可以分别把 supplier path 解释成 repository-relative 或 package-relative；I05 现有 pins 转为 expectations 时也无法唯一确定合法路径。相同 SHA 不消除读取错误目录的歧义。应由唯一 owner 在本私有合同中列 `pathDomains`：每种字段的源根、artifact 根、精确前缀转换、固定文件名/集合和符号链接政策。跨根拼接后仍须做边界与实际文件校验，不能只检查字符串没有 `..`。这是冻结前必要澄清，不需要新增 CLI 或公共 schema。

### C2：private API 与 binding 的 role 条件尚非完整严格定义

`load_frozen_provenance` 仅用文字写“keyword-only expectations object”，没有精确参数名、expectations 的键/类型/排序与 22/4/2/8 形状；`BuildProvenanceFault` 称固定 whitelist，但没有列固定错误码。I05 与 T03 的唯一 writer 会据各自理解实现接口，容易在集成时才发现不兼容。

同时 `artifactBinding.entries[*]` 的 schema 允许 `kind="file"` 而 bytes、sha256、mode 全为 null，也允许任意 target；`identityRules` 的“对应字段非空”未列具体 kind 对应表。调用者不能仅按当前 schema 得出完整文件绑定成立。

建议补最小私有定义：精确函数签名、严格 expectations 字段形状、有限错误码 whitelist，以及 file/directory/symlink 各自必填非空值与必须 null 的矩阵（含 symlink target 必须非空、相对且 resolve 后留在 artifact 内）。若 evidence 保持 opaque 类型，明确该类型只由 preflight 构造、后续两个 verifier 仅接受该类型，不将可变/任意 dict 当已验证证据。返回的 rootApproval/代码验证域/未知 native 状态也应有固定键与值域或明确 opaque 属性接口。无需扩成通用 validator 或新的公共协议。

## 已满足的前审方向

1. 无循环 hash：最终源、provenance、anchor、PYZ/实际产物、包外 binding、root 预冻结 SHA、运行后 receipt 分层正确；provenance 不反含最终 anchor/PYZ/binding hash，binding 不含自身或后出收据。
2. 独立 root 批准：builder 的 rootApproved=false 只是提议；外部执行方须在启动前核 root 冻结 SHA 与整个实际 engine 目录，reader 的包内自洽不签 root 批准。运行后只追加 receipt、新版本 binding，不回填；独立 UUID build 与原实际对象保留要求明确。
3. 代码归一域：只递归改 CodeType.co_filename，保留 constants/flags/行与 exception 信息，marshal4；精确 CPython sys.version/cache_tag/SOABI/magic、flags=0、dont_inherit=True、optimize=0 明确。entry script 身份与可导入 PYZ module loader 已分域。实现仍须显式约束实际 PyInstaller 编译优化，不能只声明 manifest 为 0。
4. 导入顺序：preflight 只作有界数据/anchor/metadata 检查；observer 安装后才实际 runtime/native import，随后 verifier 检查既有模块而不自行导入。这保留旧 probe 的安全次序；T03 不修改 I05 的 guard 或唯一 probe/test。
5. 完整性：22 supplier、4 public resource、2 不变原 JSON、8 个精确 distribution 的唯一完整要求写明；未用总 23 条锁代替运行闭包。所有变更后的最终身份仍须来自 I05 最新完整修复源的显式集成，旧 2cf/6891/401a 不是最终批准。
6. native 保守性：要求实际 wcwidth._wcwidth_c 的 loader/origin/模块归属及包内 bytes；缺失或 fake loader 失败，不以 import wcwidth 或文件存在代替。安装源 native SHA 与 ad-hoc 签名产物 SHA 分域，等价性未证保持 UNKNOWN；不继承旧例外。
7. 严格与资源边界方向：重复/额外/缺键、非有限、bool-as-int、NUL/surrogate、深度/节点/文件/集合上限均列出；输入 8MiB 上限未扩大原输入 cap，其他 audit caps 明示不是 Q5/whole-H/RSS 或硬 OS timeout。实现必须按角色使用更窄 cap，不能用通用 identity 的 128MiB schema 上限放宽 input/metadata/license 限额。
8. 入口要求：保留 FLAG+selector，lazy import 同一 canonical probe，`raise SystemExit(probe_main())`，其他 dispatch 原样。需在私有单测真实验证非零 SystemExit 与导入次序，但该测试不能冒充语义或 frozen 运行证明。

## 验证与结论边界

本前审仅使用读文件、Git 身份查询及 stdlib/哈希；唯一新写是本报告并做格式检查。未安装依赖、未执行 build helper、engine、pytest、GUI、native 或 parity；没有实施新模块、改入口、builder、I05 probe/test 或原 7abab 工件。

C1/C2 补齐后可在已授权四路径实施并完成对应私有负例/单元验证，不需要额外扩围授权。实际 loader/native 正例、root 外部运行前 inventory 核验、完整 source/package full-v1/B1 对照仍须最终完整候选和另定实际窗口；本报告没有解除现有 frozen refusal，也不签原整体 check 或语义等价通过。
