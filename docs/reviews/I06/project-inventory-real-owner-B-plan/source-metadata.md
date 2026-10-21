# B 源码事实：私有资源 metadata、初始化与关闭供方

2026-10-21，仅静态读取。按根本轮授权只新增本文，不修改主方案、产品、测试或冻结原件。全文读取准备指令 4183B，SHA256 `869e9c9568a52776b212238506700735b58de3b15cd709941b99d294cd8264c9`；当前树 `feature/I06-project-inventory-lifecycle` / `6a38fcb8135343ba5e62a8a8effe57b18c3de00c`，protected AGENTS 为 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，共同指令 `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`。未采用或改写 6a38/e2c/961 产品。

结论：现有仓库能提供准确的资源布局与内容恢复规则，但**没有独立于模型初始化的完整 metadata owner、先于所有 FS 操作的 reserve/mutation gate、可靠的资源释放回执或跨重启 retired 权威**。三仓库的内容 scan/recover 不能用于 metadata-only 观察；现有 fulfilled/close 也不能直接转换为真实 FD 已释放。

## 1. 固定来源及引用约定

本文所有 `e2c269ad:路径:行` 均精确指向完整固定提交 `e2c269ad78a78e1a042cadc93b1c81a874707153`，使用 `git show <ref>:<path>` 静态读取；不是当前工作树运行结果。下表前八项为资源供方及其直接运行时依赖，后续项仅核对初始化与配置仓库引出的传递依赖，不构成采用/编辑授权。

| 固定路径                                                          |  bytes | SHA256                                                             |
| ----------------------------------------------------------------- | -----: | ------------------------------------------------------------------ |
| `apps/desktop/src/main/model-gateway/private-directory.ts`        |  15060 | `40a9a5d52488a25d3958c171ac3e5df4272eed5d42a97f51a76ee5baeb015a88` |
| `apps/desktop/src/main/model-gateway/configuration-repository.ts` |   5292 | `535c66d17ac5172eaee4a5c4781f7e84af1bcad64eb522baa33bb14ad199b19d` |
| `apps/desktop/src/main/model-gateway/ciphertext-repository.ts`    |   4225 | `31e4bed54746529cecbdd1100db6ccb19840ef1d5367090a5334964a2f01e41d` |
| `apps/desktop/src/main/model-gateway/persistent-audit.ts`         |   4665 | `62d77f33293770b3c72a0ede6ab796115ac10ebad8def1e534790015c562f5a8` |
| `apps/desktop/src/main/model-gateway/credentials.ts`              |   3366 | `8a56addc33468467a733614a96ff4f24489d06144afe44f4dafe873dbc10482f` |
| `apps/desktop/src/main/model-gateway/electron-safe-storage.ts`    |    653 | `724462829544f8c51b0fe1c6ed5335c7b1168cb9379baa7daf69641cf11e9b0e` |
| `apps/desktop/src/main/model-gateway/policy.ts`                   |   2486 | `dd09203ebe7e7f655cee40e01c84149a8c121e48ece916fa816cbc2c320d1ced` |
| `apps/desktop/src/main/model-gateway/stored-result-source.ts`     |  10155 | `b77f2acf2e93af1e212fa7d3539b63f0090800a86dcb4587d347c3fde0d8e2d3` |
| `apps/desktop/src/main/index.ts`                                  |  12088 | `d88c1df806dc913b85a719026640ee6502762153c82c148e57aa32d5dbd9c60b` |
| `apps/desktop/src/main/engine.ts`                                 |  18609 | `d1e8a6a55b718861809570864745d49ef0e9bec3271f49cc2bc4945c8cfdf8ca` |
| `apps/desktop/src/main/jsonl.ts`                                  |   4774 | `12c0437f66b73b0aa88617b551394f6771529d2e5f307a5ab2765feb1fc05357` |
| `packages/contracts/package.json`                                 |    291 | `2bdce0f15eb195ddbdfcf75e7c43262bb1ff934c588b285f3e3c749750d72bcc` |
| `packages/contracts/src/index.ts`                                 |  11668 | `76c44e3465b5ad5c76b9b1bb6ad5ad61a206531ec8717455286a95f7665ffa28` |
| `packages/contracts/src/design-v2.ts`                             |    153 | `0e9adaaa1d5f2b55e9ecf793cc9e3cb9a39ceb3dd91b599d4b58741c7ca17ce1` |
| `packages/contracts/src/v2.ts`                                    |  29806 | `60018b5825ebb4cbc46f49d9a94d975d521687d00c0078fa3e7375f8b4b6e013` |
| `packages/contracts/src/dependencies-v2.ts`                       |   2205 | `7080ac623b1a19b9e4958dd47d071ffd3f7df38c8a85a0ce6166aea43067c17a` |
| `packages/contracts/src/states-v2.ts`                             |    578 | `cb82e8e5a047c875c93c4807b8a5f32f4174584d6d2e7b06b17d0f9f0e02b601` |
| `packages/contracts/v2/schema.json`                               | 158948 | `062ca21a1553dfa4a0c259929813003dd88616b085f1d9be728afaeb34e8ff98` |
| `packages/contracts/v2/registry.json`                             |  19352 | `730613e019f49e19d834c1eced78c16b188488e8fd3ca4c1161b1734381f753f` |
| `packages/contracts/v2/errors.json`                               |  17014 | `689083823785ed40b7e175dae0f205673dd9a5fb16545015da403b3ac1cabe68` |
| `packages/contracts/v2/dependencies.json`                         |   1438 | `dee118b368915df4172a77b875d31ce29ad8374cb5fce3915678f7f950cedad4` |
| `packages/contracts/v2/states.json`                               |    716 | `ab54cac024f0f6b31a8a229198ae1c4ab13f63ff88184cdcef78113b9e893416` |
| `apps/desktop/electron.vite.config.ts`                            |   1202 | `c535cec85be6e0a37a09fa36ba42497ecee40cdeb8b38b5ec2197354afb86c2d` |
| `apps/desktop/tsconfig.json`                                      |    396 | `158bae6a063f36d687307f0a117a4f5f88f4e4632088ad086be191c2ae0a7186` |

## 2. 实际资源布局与保留范围

| 资源           | 固定事实与来源                                                                                                                                                                                                                                                                                        | B 必须保护/观察的范围                                                                                                                                                         |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 路径输入       | `e2c269ad:apps/desktop/src/main/model-gateway/private-directory.ts:7–14`：userData 为绝对路径、无 NUL、1–4096 字符；excludedRoots 1–128。`e2c269ad:apps/desktop/src/main/index.ts:96–104`：实际 main 取 app.userData，仅排除真实 DB/-wal/-shm，依次打开三个 bucket                                    | 输入数组是固定配置，不是完整 inventory、动态位置 registry 或原生能力。不能用它证明 backup、lock、retired、sessionData 或新选位置已覆盖                                        |
| 根与父锚点     | `e2c269ad:apps/desktop/src/main/model-gateway/private-directory.ts:169–216`：userData → model-gateway-private-v1 → credentials/configurations/audit；每个 bucket 实例分别持有这三个目录的 handle/dev/ino                                                                                              | 全 model 根及其后代、缺失但保留的 prospective 范围；userData/其他 profile 根是否整体保护须由 main 真实 owner 提供，不能从本类推断 sessionData。祖先和瞬时目录句柄也有生命周期 |
| 正式文件名     | `e2c269ad:apps/desktop/src/main/model-gateway/private-directory.ts:25–26,230–243`：`[0-9a-f-]{36}.credential/.audit/.configuration`；该正则是文件名准入，并不等价 UUID 内容验证                                                                                                                       | 不能只观察当前配置引用；文件名异常、孤儿或未知子树也不能当不存在。整根路径保护保留；无法完成叶子身份/别名闭合时 completeness 非 complete                                      |
| 配置 journal   | `e2c269ad:apps/desktop/src/main/model-gateway/configuration-repository.ts:29–42,121–133`：format=1，sequence 1–1024，recordId 为 `00000000-0000-4000-8000-` 加 sequence 的十二位补零十六进制；正式名为 recordId.configuration                                                                         | 所有历史序列文件均是私有配置，不仅最后一次 load 的 0–32 个配置。含 endpoint/model/displayName 与 binding 元数据；不是项目内容，也不是 metadata-only inventory 可读取的正文    |
| 密文文件       | `e2c269ad:apps/desktop/src/main/model-gateway/ciphertext-repository.ts:25–29,52–61,73–90`：format=1、binding、base64 ciphertext、digest；正式名 ref.credential。`e2c269ad:apps/desktop/src/main/model-gateway/credentials.ts:44–55`：ref/version 由 randomUUID 产生，principal 由受信调用者提供并校验 | 原件即使是密文也全保护；旧/未引用 ref 不因 config 更换而自动退役。inventory 不读密文、binding、secret，不用内容 hash 寻找别名                                                 |
| 审计文件       | `e2c269ad:apps/desktop/src/main/model-gateway/persistent-audit.ts:68–72,113–120`：format=1、随机 eventId、record/digest，名 eventId.audit；record 包含目标、配置/主体、origin/digest、项目、范围、决策、event/reason/time（40–67）                                                                    | 每份审计及失败/blocked 记录均私有；metadata-only audit 不是可导出 payload。没有按项目清除 audit 的现有 API                                                                    |
| 发布临时名     | `e2c269ad:apps/desktop/src/main/model-gateway/private-directory.ts:365–404`：`.pending-<正整数PID>-<randomUUID>`；独占创建、两段写、file sync、link 到正式名、unlink pending、directory sync                                                                                                          | 登记必须先于临时 open；中间任一失败都可能留下真实对象。link 发布到 unlink 之间，同 inode 两个私有名字是合法内部状态，不能误作外发许可                                         |
| 遗留与失败状态 | `e2c269ad:apps/desktop/src/main/model-gateway/private-directory.ts:271–277,397–417`：list 不删除 pending，但从返回值过滤；失败只尝试删自己 pending，不删可能已发布的正式文件；namespace 不可信时保留 pending                                                                                          | metadata 观察必须含被 list 过滤的 pending、部分写、孤儿和可能成功的 final。没有覆盖写/回收正式旧记录的现有 API；关闭不是删除或解除保护                                        |

权限事实：private 目录要求当前 UID 且精确 0700；userData 要求当前 UID 且无 group/other write；可信祖先允许 root/当前 UID，root-owned sticky 目录是特例。输入的 symlink 只允许 root 所有，随后仍核 realpath/祖先。见 `e2c269ad:apps/desktop/src/main/model-gateway/private-directory.ts:51–105,169–219,246–269`。Windows 在169行固定拒绝；这些是现有 POSIX 有限检查，不能直接转换为跨 OS ACL/句柄能力或任意同 UID 攻击防护。

## 3. 恢复预算与内容读取：不可混成 metadata

| 方法/限额                     | 实际行为                                                                                                                                                                                                                             | 不可作出的推断                                                                                                                                  |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `PrivateDirectory.names/list` | `e2c269ad:apps/desktop/src/main/model-gateway/private-directory.ts:235–277`：单 bucket opendir 最多接纳 11024 项（再有条目即失败），只接受上述两种名字；list 前后 assertSafe，返回时过滤 pending                                     | 不是全根递归观察；未给外部返回根/文件 inode 清单。11024 包括 pending；不能截断后宣布完整，也不能调用 list 后声称 pending 已登记                 |
| `PrivateDirectory.read`       | `e2c269ad:apps/desktop/src/main/model-gateway/private-directory.ts:283–344`：上限1–128KiB，分配 maxBytes+1；读前核类型/UID/0600/同 dev/大小/nlink1–2；两链接须找到受控 pending 对；读后核 size/mtime、名字与 inode、根锚点           | 它实际读取完整内容，绝不能拿来做 metadata-only inventory；也未枚举根外所有硬链接。两个合法私有名字只证明当前恢复形态，不证明外部候选安全        |
| 配置 scan                     | `e2c269ad:apps/desktop/src/main/model-gateway/configuration-repository.ts:73–101`：最多1024个正式配置文件、每份实际读128KiB；校验 JSON/schema、文件名与序列 ID、digest、连续 sequence 与 previous 链；load/replace 再扫描（103–133） | 这是真实配置内容恢复，不能为 inventory 调用 open/load/scan。1024 是此现格式的恢复/序列界限，不是其他仓库的统一上限                              |
| 密文 scan                     | `e2c269ad:apps/desktop/src/main/model-gateway/ciphertext-repository.ts:52–70`：读/parse 每个正式 credential envelope、decode base64、核 binding/ref/digest；密文字节最多65536；write 的4096检查在85–89                               | 4096 是新增写入准入，不是 scan 的损坏阈值；恢复仍受目录预算。listBindings 也调用 scan，读取正文；不能仅因方法名有 bindings 就用作 metadata 观察 |
| audit recover                 | `e2c269ad:apps/desktop/src/main/model-gateway/persistent-audit.ts:94–110`：读取每份 audit，核 schema/name/digest 并按 time/eventId 排序；append 的10000检查在117–119                                                                 | 10000 是 append 准入，不是 recover 损坏阈值；readEntries 同样读正文。没有恢复时重新发送网络的动作                                               |

未知名字/过额/格式损坏可能使内容仓库不可用；B 应保留其真实保护范围与失败来源，不为了 metadata 观察修复内容、删除未知对象、降低内容恢复规则，或把“load 失败/结果为空”变成空 inventory。对常规文件仅可按 metadata 身份观察已知范围；普通文件 linkCount 超过已证明私有名字数等情况保留 unknown，不为找全别名遍历全盘。目录 link count 不可照搬普通文件规则。

## 4. 初始化、操作与关闭：应登记的真实入口

### 4.1 初始化必须另有永久寿命与失败回执

- `e2c269ad:apps/desktop/src/main/model-gateway/private-directory.ts:169–219` 在返回实例之前已经 realpath/lstat、可能 mkdir userData/私有目录、打开和同步目录；constructor 不是 reserve 点。**reserve 必须在调用这段逻辑前**，并覆盖可能被创建的精确根/后缀和临时持有者。
- 三仓库 open 分别在 `configuration-repository.ts:64–66`、`ciphertext-repository.ts:42–44`、`persistent-audit.ts:84–86` 直接 await scan/recover；这些初始化读取**没有经过本实例 PrivateOperations.run**。只包装公开 load/write/append 不会覆盖初始化。
- main 的顺序初始化及失败清理是 `e2c269ad:apps/desktop/src/main/index.ts:102–129`；已成功创建的目录/正式文件不会因后续仓库/模型失败而消失。失败 catch 关闭模型并不提供“从未存在/没有残留”的证明。该入口唯一 owner 为 T01，B 只提出 bootstrap reserve/init receipt 接口需求，不改 index。
- `e2c269ad:apps/desktop/src/main/model-gateway/electron-safe-storage.ts:9–14` 只在真实 Electron browser/app ready 构造既有 boundary；**工厂没有调用 backend 检查**。安全后端检查在 `credentials.ts:35–41,48,65–71` 的实际 store/read。二者都不能作为 metadata 初始化或 inventory 完整性的前置，更不能由模型 unavailable 推断私有根空。

### 4.2 PrivateOperations 有价值，但不是资源释放证据

`e2c269ad:apps/desktop/src/main/model-gateway/private-directory.ts:432–443`：run 在微任务 action 真正开始前把 operation 加入 pending，最多32；close 先关闭新准入，再 allSettled 截取到的 pending，最后调用目录 close。配置仓库另用 tail 排序（`configuration-repository.ts:46–56`）；密文/audit 没有这条配置 tail。该队列不提供跨 bucket/inventory 的互斥、revision 握手或实际 OS handles census。

真实操作供应点是每次 open/opendir/stat/read/write/sync/link/unlink/close 及初始化 lifetime。names 的目录流（235–243）、syncDirectory 的短时目录句柄（109–118）、ensureApplicationDirectory 的创建与父目录同步（121–149）不能只因不在 anchors 数组里就漏登记。具体 native/Node 调用返回、句柄 close 结果及保留对象身份要进入同 owner 事实；不把一个外层 Promise 品牌当“所有资源都已释放”。

### 4.3 三处必须明确保留 close 失败/未结

1. `e2c269ad:apps/desktop/src/main/model-gateway/private-directory.ts:347–348`：read 的 finally 将 handle.close 拒绝吞掉，**read 可 fulfilled 但该句柄释放未知**。open catch 的222行也吞每个 anchor close 失败；publish finally 的408行吞临时文件 handle close，412–415吞清理失败。
2. `e2c269ad:apps/desktop/src/main/model-gateway/private-directory.ts:421–424`：先 closed=true，再 Promise.all(close)。有一个 close 拒绝会先 reject，其他 close 可仍在途；第二次 close 因 closed=true 直接返回，不能以第二次 fulfilled 报 released。需要显式保留实际每句柄 close Promise/失败状态，不能只看对象 closed 标记。
3. 三仓库 open catch 的 `configuration-repository.ts:68–70`、`ciphertext-repository.ts:46–48`、`persistent-audit.ts:88–90` 也吞 files.close；main `index.ts:77–88` 吞 service close、allSettled 仓库 close 后清空全局。后者不是正式 drain receipt，且本子任务不改 T01 文件。

三个仓库的公开 close（配置139–144、密文112–117、audit133–138）会把自身观察到的失败映射固定 GatewayFailure；这个有限错误行为应保留，同时向内部资源 owner 提供不可混淆的 unknown/failed/unsettled 事实，不能仅加一个 released 布尔值。

## 5. 最小采用闭包与不必要的运行时牵连

### 5.1 首个真实 metadata 供方不需要采用内容仓库

新 metadata 观察/注册 owner 可只依赖获批 A 核心接口、Node metadata 原语及明确 main bootstrap 输入；不得导入内容仓库并调用 open/listBindings/readEntries 来“补全 inventory”。当前 A 只处理接收的资源/Promise，一切真实性仍须由这个实际供方证明。A 固定采用路径/源码表由主 B 方案单列，本文不读取或执行 A 产品。

`PrivateDirectory` 自身的直接依赖仅 `node:fs/promises`、`node:fs`、`node:path`、`node:crypto` 和 zod（1–5）。但它公开 open 会 mkdir，其 list 会过滤 pending，因此不是现成 metadata-only facade。重用其输入校验/身份比较语义与采用其内容 I/O 是两件事；不能复制一个同名“安全目录”后产生第二权威。

### 5.2 若采用现有真实仓库的 mutation/init/close 供方，必须逐项登记

| 路径/依赖                                               | 必要性与采用边界                                                                                                  | 唯一责任/不自动包含                                                                                 |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `model-gateway/private-directory.ts`                    | 全部实际 private FS 与 PrivateOperations 在此；未来真实 reserve、mutation、资源 handle/lifetime hook 的最小写入点 | I06 私有模块，现 e2c 冻结；新阶段须明确逐路径批准后在新候选改                                       |
| 三个 repository                                         | open 初始化不进 operations；公开操作/close 的真实调用链需接 owner。原 payload/恢复规则必须保留                    | I06；metadata-only 首阶段不需要读取/采用其内容恢复，后续实际 writer 接线另批                        |
| `credentials.ts`                                        | 两仓库 import credentialBindingSchema，实际凭据 boundary 也持 repository；不能忽略 schema 的运行时依赖            | I06；`SafeStorage` 是 type import，**不因此加载 Electron**。首阶段不需调用 boundary/encrypt/decrypt |
| `policy.ts`                                             | 仓库需要 GatewayFailure/opaqueId，audit 还需 purposeSchema/failureCodes，credentials 需 parse。其运行时只依赖 zod | I06；闭包会包含其他声明，但不必执行模型 endpoint/network 功能                                       |
| `electron-safe-storage.ts`                              | 只有真实凭据 factory 接线阶段才需，实际 runtime import Electron app/safeStorage                                   | I06；不是 metadata 供方必需依赖，不应为 B 临时目录观察引入 Electron/Keychain                        |
| `persistent-audit.ts → gateway.ts`                      | 第3行是 import type AuditRecord/AuditSink，运行时不需要加载 gateway                                               | 类型检查仍要有获批类型来源；不因此授 gateway/transport 运行或编辑权                                 |
| `configuration-repository.ts → stored-result-source.ts` | 第11行为了 materialCanonical 作运行时导入；函数实际定义 source:19–31                                              | 这是重要闭包缺口，不能称配置仓库只需前几项。source 又会牵连 canonical/T01 engine，见下              |

配置仓库的原样运行时传递链是：

`configuration-repository.ts:11 → stored-result-source.ts:3–7 → @ontolearn/contracts + @ontolearn/contracts/v2 + errors.json + ../engine(EngineError) + policy`。

实际 `EngineError` 不是 type；`engine.ts:1–7` 再引 child_process、contracts/v2、jsonl。`packages/contracts/package.json` 的 v2 export 指向 design-v2，后者第2–4行导出 v2/dependencies-v2/states-v2；v2 引 schema/registry/errors/states，dependencies-v2 引 dependencies/registry，states-v2 引 states.json。外部 zod 由该固定 package 声明4.6.7。前述完整源表保留这些传递文件 SHA，但**不申请采用 e2c canonical/engine/jsonl 或其未批准实现**；它们当前 T01 独占，其他共享资源也不随之取得。

若后续 B2 真需最小化实际配置 writer 闭包，建议另申请一个 I06 纯私有 `apps/desktop/src/main/model-gateway/material-canonical.ts`，由 config 与 source 共同使用同一 helper，精确保留 e2c:stored-result-source.ts:19–31 的序列化字节与现有配置 digest/恢复兼容性；不复制两套 helper、不另造公共 canonical。该提案需登记新路径及两处 import delta，现 e2c/6a38 不动；不为 metadata-only B1 提前实施。

## 6. Node metadata 为什么仍不是首内容 I/O 能力

直接反例都在固定代码，而非假想运行通过：

- `private-directory.ts:196–208` 是 lstat 后按 path open，再由219行 assertSafe 补验；`read:288–293` 是 assertSafe 后按完整叶子路径 open，再 fstat。所持目录 fd 没有作为 openat 的实际解析基点。O_NOFOLLOW 不能凭这里的 JS 调用自动闭合全部祖先的 TOCTOU。
- `private-directory.ts:141–145,193–197` 在 mkdir 后再 lstat；事后拒绝不能抹去已发生的创建。`publish:387–399` 也是 assertSafe 后按 path link/unlink，另有 await observer。
- `private-directory.ts:246–269` 复验固定 excludedRoots 与当前锚点；没有把全私有文件 inode inventory 参与任何项目 DB/header/SQLite VFS 真实读取，更没有跨进程 native admission fence。

因此 B 的真实 Node metadata/temp-directory 观察可证明有限名字/身份、实际调用计数和生命周期，但 productionAdmission 与项目首内容 I/O 继续 unsupported。原生 broker、同 build SQLite VFS/ABI、Windows ACL/fileID/reparse/句柄实现是另外精确授权阶段；不以本轮新增供方解除 gate，不把 Windows 永久改成 POSIX-only，也不以固定 userData 代可选位置。威胁范围仍不扩大为任意同 UID 对抗/DLP。

## 7. 持久 retired：当前没有，fresh 也不能自报

六个供方文件没有 retired registry、profile epoch 持久格式、跨重启 owner locator 或退役删除 API。现 format=1 的 configuration/credential/audit envelope 是内容仓库格式，不能悄悄塞 retirement 记录；PrivateDirectory 的 bucket union/recordName 也不接纳任意新 journal 名字（private-directory:25–26,162–165）。新增持久 metadata 是独立维护面，不能宣称现三仓库已提供。

主方案至少须冻结：

1. 唯一 record owner 与稳定 bootstrap locator。可提案当前私有整根下专用 `model-gateway-private-v1/resource-inventory/retired-v1/<recordUUID>.retirement`（仅候选、现不存在本格式），但若 profile/userData 迁移，必须有受信 locator/移交协议定位旧记录。把记录只放在被搬走的旧目录、新目录查无即 fresh，不能恢复历史保护。
2. 版本化、有限 metadata schema：owner/profile epoch、严格序列/前序摘要、实际根及旧别名定位、可靠 OS 身份和持有/退役阶段；不含 key、密文、endpoint/业务正文、grant 或 Job/operation 权威。路径/身份亦是私有 metadata，不向 renderer/普通日志发布。记录自身也必须加入保护范围。
3. 写入前 reserve、不可覆盖发布、耐久确认与未知发布读回规则；只有持久事实已建立才可完成相应生命周期转换。该发布 primitive 与受控 FS/native 能力未落地时，可先做纯格式/故障设计，不虚报跨 OS 原子性。
4. 丢失、损坏、超额、断链、未知版本、权限/owner/定位错误均 unknown，保持根/别名保护；不删记录“修复”、不回退 complete+[]。0个在途句柄也不自动解除持久残留路径保护。
5. fresh 必须来自真实受信创建流程：实际排他创建的目录/锚点身份、完整有界 metadata 观察及历史 locator/record 状态证据，不能由调用方传 fresh=true，不能由一次 ENOENT 或空 configurations[] 推导。若没有能证明 fresh/既有历史的供方，生产保持 incomplete；隔离测试只能证明自己真实新建临时目录的事实。

这份持久记录不能变成第二项目/Job账本；格式、唯一位置、owner、重启恢复与原生发布依赖需根另冻结。没有新格式/locator不是已有内容库空的证据，也不能为进度放宽首 IO gate。

## 8. 建议独立子阶段及最小验收（均未实施）

| 子阶段                           | 候选写责/路径，均待根逐项登记                                                                                                           | 可独立证明及后置边界                                                                                                                                                                                                                                                      |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B1 真实 metadata 观察供方        | I06 新 `apps/desktop/src/main/security/private-resource-metadata-owner.ts`；新 `tests/unit/i06-private-resource-metadata-owner.test.ts` | 仅受控新临时目录，实际 metadata/有界枚举/已持有目录与文件身份；完整根、未知成员、pending+final、静态硬链接、替换、超额/失败/close 未结/late settle 反例。可复用获批 A 接口但不自报 complete；不读内容、不调用 repository.open、无 Electron/Keychain。通过不授 SQLite 能力 |
| B2 实际 private writer/init 供方 | I06 private-directory、三仓库；credentials/policy 仅按上表真实必要性；material-canonical.ts 仅需解耦时精确批准                          | reserve 发生在首次真实 FS 之前；init 与每次实际操作先登记；mutation/revision 与 A 一致；close 的内部失败/未结不吞。必须保存每个实际调用与资源释放证据，队列清零不算。内容恢复另获合成夹具权限才验证，不碰用户内容                                                         |
| B3 持久 retired 供方             | I06 可提案新 `apps/desktop/src/main/security/private-resource-retirement-records.ts` 及专属新测试；真实磁盘目录/schema/发布依赖另批     | 独立格式/恢复拒绝与实际受控临时目录故障；跨重启进程/两 OS/耐久原件在后续授权阶段。unknown 缺省、真实 fresh 来源、无覆盖发布必须有真实供方，不以品牌或布尔值完成                                                                                                           |
| T01 接线前置                     | main/index 的先 reserve/init/关闭回执消费，实际 DB/child/Store/worker/native 释放供方                                                   | 本任务只提需求；不编辑已交 main/engine/task-service/Store/worker，不创建第二 writer。model/source/network/同 UUID cohort 的其余生命周期由另一专属 agent 回报，本报告不重复扩展                                                                                            |

实施树建议仍从实际批准 5f 建独立 feature/worktree，并显式申请采用 A 的完整最小路径与版本；e2c 如需移入 B2，按本源表逐路径审批准入及依赖 delta，不能整目录复制。新测试/证据路径同阶段登记，原 tests/CI/锁/build 不在授权内。当前 A 树只追加本文，不消费其未批准产品；未来真实测试须分别保留首次失败、固定 source/runner/runtime/真实 OS 原件，普通模块测试不替指定双审或目标平台。

本轮只执行固定 Git 源码读取、stdlib 哈希与文档格式/diff 检查；未 import/执行产品、测试、build/install、网络、native/Keychain/GUI，未修改原产品或主方案，未 stage/push/PR/merge。
