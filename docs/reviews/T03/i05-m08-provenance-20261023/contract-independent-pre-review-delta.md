# I05 私有 provenance 合同差异复核

结论：**CONTRACT_DELTA_PASS_ONLY，原 C1、C2 已关闭，无新增合同阻断。** 当前严格合同可供已授权四路径实施；这不是实现、loader/native 正例、root 运行批准或 source/package 语义等价通过。

## 固定输入与方法

本次按 owner 指定的最终输入一次全文读取 906 行、36587B，SHA `9d97a6a233b47abc23064a9a8f8330080d62f39b3db981de14a148880e202a04`，路径 `docs/reviews/T03/i05-m08-provenance-20261023/private-contract-v1.json`。读取后再次核 bytes/SHA 一致，未把正在写入的中间版本当最终输入。

原前审报告 `contract-independent-pre-review.md` 保持 6862B / SHA `ee43b677f048ffabb92793cf4be28bd8d2c13d0565250c945370c98d4908f063`，本次未覆盖或格式化它。原报告绑定的首次合同为 25545B / `9a6f88a7ea0273f05a2fec706c5ae4745d449f76ffbbfb6c2ac66f42d09d8c11`；本复核针对当前完整合同中对应 C1/C2 的新定义，不声称已用旧合同副本作全字节 diff。

只做读文件、stdlib JSON/集合一致性、SHA 和 Git 路径差异检查；没有安装、运行 build helper、engine、pytest、GUI、native 或 parity。复核时已授权四产品路径没有 tracked diff，新 reader/test 文件也尚不存在；唯一新写是本报告及其格式检查。

## C1 关闭：路径根与转换已唯一化

`pathDomains` 已逐域定义 source root、artifact root 与字段含义：

- supplier/private code 的行路径统一为 `ontolearn_engine/<relative.py>`；源根为 `repository/packages/engine/src`，frozen 根为 `_MEIPASS`。I05 原四元组明确前缀转换，保留有序 22 项。
- 四项 public resources 统一转成 `contracts/<original-path>`；源根为 `repository/packages`，frozen 根为 `_MEIPASS`；原三元组保序转换。
- 两输入从 contract 的 fixedInputs 原样复制，源根与 frozen 根明确，原名/顺序/内容不改。
- lock、私有 contract、entrypoint 分别给出固定源行路径与冻结位置；entrypoint 只作源身份及外部 launcher/PYZ 绑定，明确不假设脚本 loader。
- distribution metadata/licenses/files 以当前独立环境的 site-packages 根为源域、以 `_MEIPASS` 为 frozen 域，另约束实际 resolved path、dist-info 归属、Python/native 模块名推导；完整 artifact entries 另以实际不可变引擎目录为根，内部 symlink 与越界/特殊文件规则分离。

这消除了原“inside-declared-root 未声明 root”及 I05 tuple 转换歧义。实现仍须按完整 resolution 复验边界，不能只进行字符串前缀拼接；合同已明确这一政策，不由本次静态复核替代其负例实测。

## C2 关闭：严格输入、错误与证据接口已定型

`schemas.expectations` 明确只有 suppliers/publicResources/inputs/lock/distributions 五个必需键并拒绝额外键；22、4、2 的形状及 lock 身份固定。distributions 为固定八名称的严格对象，各版本为精确 const。独立静态检查确认 required/properties 五键相同、八版本与 fixedDistributions 一致；不是仅凭数组长度推断完整性，原 orderedUnique/完整无替换规则继续适用。

`runtimeApi.exactSignatures` 冻结了 keyword-only `expectations` 参数、`FrozenBuildEvidence`、两个 post-observer verifier 的参数，以及 builder/外部 verifier 的私有 programmatic 入口。没有新增通用路径 CLI。`errorCodes` 显式列出 29 个唯一固定错误码，不再留下未定义 whitelist。

`bindingKindRules` 明确 file 需要 bytes/SHA/mode 而 target 为 null；directory 仅 mode 非空；symlink 仅 target 非空且相对、非空、受限长度、禁止 NUL/backslash/absolute、resolve 后在目录内且目标存在；launcher 必须是带执行位的 regular file。独立检查每个 kind 的 null/non-null 集合互斥且覆盖四个角色字段。schema 的 nullable 结构必须与这些语义条件共同强制，不能只按 nullable schema 放行全部 null 的 file。

opaque evidence 已限定 exact class、module-private seal、不可变 canonical manifest/expectations bytes、固定 resolved `_MEIPASS` 与原解释器身份；post-observer 调用重新核同一 root/interpreter/实际 loader，不缓存运行成功。`loadedModulesArgument` 明确 exact dict 的 22 名称及真实 current ModuleType，module/spec/sys.modules/origin、两个已加载私有模块和八 distribution 已加载 Python 代码分别核；缺项或未知 loader 拒绝。seal 明示只是防偶然误用/变异，不被夸大为抵抗同进程任意 Python introspection 的安全 capability。

## 追加澄清及未改变边界

anchor preflight 已进一步明确不 import/执行 anchor，而取 frozen spec/get_code，与两个 SHA 赋值的限定模板按同一 compile/marshal 规则比较。这样不会为读取 anchor 提前执行目标模块代码；包内 anchor/manifest 自洽仍不构成 root 批准。

原正确方向均保留：递归只改 co_filename、marshal4 与完整 Python/optimize=0；observer 前只作有界预检，之后才实际 runtime/native 导入；固定 22/4/2/8 与两原 JSON；native installed-source/签名后 artifact hash 分域，未证保持 UNKNOWN；root 在运行前冻结外部 binding SHA 与完整实际目录，运行后只追加 receipt；旧 UUID 产物和旧 binding 不覆盖；固定 FLAG+selector 与 `SystemExit(probe_main())`。

当前合同只是实现依据。仍须在四路径实际实现后核其 strict/caps、角色限额、anchor/source/loader/Python/native/外部 binding 负例；最终来自 I05 最新完整修复源的集成身份不能由旧 2cf/6891/401a 代替。实际 source/package full-v1/B1、root 外部执行与 physical HOLD 继续执行各自前置和专门运行窗口。此补审不关闭原八项 pytest 失败或整体 check，不改 I05 唯一 probe/test，也未授权任何额外产品路径。
