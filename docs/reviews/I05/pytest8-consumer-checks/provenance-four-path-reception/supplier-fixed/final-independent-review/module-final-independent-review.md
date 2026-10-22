# T03 四产品独立实现审查：32d943

结论：本次四路径完整静态审查发现 **F2 / P2**，当前候选尚不能签收为严格符合合同的完整实现。distribution Python 文件的源码身份与编译指纹来自两次独立读取，且首次读取放宽了合同的 2 MiB 源文件读取上限。已用纯临时合成 distribution 定向复现。其余已审关键边界未发现新的必修矛盾；这些静态结论与主控 96 项定向单元通过均不构成真实构建、runtime/native 或 semantic parity 证明。后续修订必须另做 delta，本报告不追认未来版本。

## 固定输入与独立性

审查候选是 `32d9434d78abda25f7b6f8693725de83200e887e`；不是后续工作区文件的浮动版本。全文审读以下四个产品文件；本 agent 未参与其实现，未修改任何产品源码或测试：

| 路径                                                                | bytes / lines | SHA-256                                                            |
| ------------------------------------------------------------------- | ------------- | ------------------------------------------------------------------ |
| `scripts/build-engine.mjs`                                          | 8437 / 252    | `738f55ef056c3326f812ab9e4ed272a11a332a21a23a78c72fd07b510d31a8ff` |
| `packages/engine/entrypoint.py`                                     | 976 / 30      | `aaf9f85b59f115ae0646fd31f5305ee588c2bd58a0fbb28d9714c707c9035ef3` |
| `packages/engine/src/ontolearn_engine/semantic_build_provenance.py` | 46499 / 1257  | `7b115b5e8ee7c4215f69216634b321bb952aad8accdf60587341d1d08feaedd2` |
| `packages/engine/tests/test_semantic_build_provenance.py`           | 42607 / 1170  | `c7311d084fbe377de311e97c31df07e0c2eeccea2353159bd7f32a964100df59` |

以上身份再次由 `git show 32d943:<path>` 的原字节独立计算。合同为 36587 B / 906 行，SHA-256 `9d97a6a233b47abc23064a9a8f8330080d62f39b3db981de14a148880e202a04`。沿用已读的指定 root preaudit；未扩大读取其他 private 控制文件。AGENTS 受保护 overlay 不纳入实现签收，也未改动。

保留此前合同首审、合同 delta、builder/entry 首审和两路径 delta 原件。本报告扩大到四产品实现，既不改写首审发现，也不将早期局部审查冒充四路径签收。

## F2 / P2：distribution 源码身份与代码指纹没有共用同一受限快照

位置：冻结 reader 的 `_dist_inventory`，`row = _identity(site_root, relative)` 到 `.py` 分支再次 `_read(..., CODE_CAP)`。

实际行为是先以 `_identity` 默认 `FILE_CAP=134217728` 读取整个 `.py`，计算 `bytes/sha256`；之后第二次以 `CODE_CAP=2097152` 读取并编译计算 `codeSha256`。这存在两个可观察问题：

1. 2 MiB + 1 B 的 Python 源文件已被首次读取到内存，之后才因第二次受限读取拒绝。因此最终拒绝是 fail closed，但并未履行合同 `strictParsing.sourceFileBytesMax` 的私有 verifier 读取上限。
2. 文件若在两次读取间改变，两次各自的 before/after stat 都可以稳定；结果 row 的源码 SHA 属于旧内容，代码指纹属于新内容。单文件 `_read` 的稳定性检查不能使两次独立读取成为同一快照。这直接影响源码身份与代码绑定的准确性，不能仅用最终 manifest schema 或 archive 比对补回。

本 agent 以 `/Users/kyle/.local/bin/python3.12 -B`、`git show 32d943:...` 原字节加载 reader，并在 `TemporaryDirectory` 创建 fake html5rdf distribution。仅替换 stdlib metadata/site-root 查询与 `_read` 观察器；没有调用 prepare/finalize、PyInstaller 或任何语义模块。第二个 case 在第一次 `_read` 返回后把临时 `VALUE = 1` 改为 `VALUE = 2`，再允许第二次真实 `_read`。最终工具输出：

```json
{"case":"source-cap","reads":[{"cap":134217728,"returnedBytes":2097153}],"eventualRejection":"BUILD_PROVENANCE_LIMIT_EXCEEDED"}
{"case":"split-source-code","reads":[{"cap":134217728,"returnedBytes":10},{"cap":2097152,"returnedBytes":10}],"sourceHashIsOld":true,"codeHashIsNew":true,"codeHashMatchesRecordedSource":false}
```

首次 mock 的观察器因 macOS `/var` 与 `/private/var` 路径别名而未命中，并未提供复现证据；将 fake 根先 resolve 后重跑得到上述明确输出。该验证修正不涉及产品改动。

精确最小修订：先判断文件 kind；`.py` 只用 `CODE_CAP` 读取一次 raw，从相同 raw 计算 bytes、SHA-256 和 `_compiled(raw)` 指纹；保留原来的其他类型身份路径。增加两个针对性回归：超过 CODE_CAP 时首次读取就拒绝；正常 `.py` 只有一次读取且 source/code 身份共用同一 raw。主控已收到本发现；此处尚未审签其后续修订。

## 已核对的实现边界

- **严格解析与角色约束。** JSON 禁重复键、NaN/Infinity、非法 UTF-8、BOM、NUL、孤立 surrogate；层数、节点数、manifest/contract/binding 长度有固定上限。schema 精确类型拒绝 bool 充当 integer，typed object 缺键/额外键拒绝。22 supplier、4 public resource、2 fixed input、lock、固定 8 distribution 的名字/顺序/唯一性均校验；private2、entrypoint、contract、metadata/license 所属目录和 file kind 的 null 规则另做约束。F2 是本次发现的读取上限缺口，不能被本项概括为全部 caps 已符合。
- **代码比较域。** `_compiled` 固定 flags=0、dont_inherit=True、optimize=0；递归只替换 CodeType.co_filename，marshal 第 4 版序列化。精确 CPython sys.version/cache_tag/SOABI/MAGIC_NUMBER 和 optimize=0 受验；测试覆盖保留常量、flags 和行信息的差异。entrypoint 未被冒充普通 PYZ 模块 loader 身份。
- **前置与后置接口。** `load_frozen_provenance` 只做 bounded 文件/JSON/anchor/metadata 检查；anchor 用 standalone find_spec/get_code 和两赋值模板比较，不 import/执行 anchor。两个后置 verifier 只检查已经存在的 canonical sys.modules 对象；不主动 import supplier、distribution 或 native target。真正 audit observer 的安装与调用次序仍由 I05 集成负责，本四路径不自行安装 observer，不能据此宣称实际 observer 次序已验证。
- **opaque evidence。** exact class、私有 seal、不可变 manifest/expectations bytes、已 resolve root 和原 interpreter 身份绑定；后置调用重验 frozen/root/interpreter，并再次读取 actual loader code。它用于隔离误用，不构成抵御拥有同进程 Python 反射能力的攻击者的安全 capability。
- **source / PYZ / 外部批准。** prepare 用 literal AST 读取 I05 原 tuple，仅采集选定源文件和实际 distribution 字节，验证选定输入等于 Git HEAD，拒绝 tracked runtime dirty。anchor/provenance/PYZ/binding 没有循环 hash。finalize 从实际 archive reader extract 22+private2+8 distribution Python code 和 anchor；不执行这些目标代码。全目录 proposal binding 在 artifact 外以 xb 新建且 rootApproved=false；外部 verifier 要求调用方给出冻结的 expected SHA，并核对实际完整文件/目录/内部相对 symlink、mode 和可执行 launcher，没有将包内自述升级为 root 批准。
- **native 与 Python shared library。** native 后置检查要求 exact ExtensionFileLoader、sys.modules identity 与 artifact 内 origin，报告实际 artifact hash；installed-source 与签名后 artifact 的 hash 域分开，equivalence 保持 unknown。fake ModuleType + ExtensionFileLoader 测试只能证明验证分支，不能证明真实 native 已加载。Python shared library 同样只识别实际文件并保留 source-byte-equivalence unknown；完整外部 inventory 负责绑定最终字节。
- **resources / inputs / distribution。** 四份 public resource、两个固定 input 与 provenance/uv.lock 的路径域和身份分别校验；metadata exact Name/Version，所有记录 license 及声明 License-File 与 data 字节受验。runtime 已加载的固定八包 Python 模块需出现在各自 files 记录并通过实际 get_code 比较。实际 wheel RECORD、collect-all 与最终 PYZ 的完整可达性仍待一次获准真实 finalize 证明。
- **builder / 旧产物。** fresh UUID 隔离 dist/work/spec/cache；8 包 collect-all 与 metadata、optimize0、reader/anchor hidden-import、anchor generated path 及固定 data 参数存在。helper 字段和路径必须精确匹配，失败不会进入发布。复制到临时 stage 后才 archive 旧 stage 并 rename；发布失败尝试恢复旧 stage，独立 unique artifact/binding 不被清除。恢复本身若失败，保留 archive/unique 原件，不应把“尝试恢复”表述成所有 I/O 故障下必然恢复。dangling/普通祖先 symlink 使用 lstat 拒绝。
- **entrypoint。** 新固定 FLAG 分支保留 selector/argv 并传播 main 返回的 0/1/2/130；五条旧 dispatch 行为有合成模块单元覆盖。未执行真实 full-v1。此前 F1/P3 的非规范绝对 root 祖先循环已由同步规范化 guard 关闭；N1 的 reader 可达性已显式 hidden-import，但实际 PYZ 尚待真实构建/finalize 证据。

## 测试与原始证据的准确范围

本 agent 全文审读 1170 行测试。fixture 为合成模块、合成 loader、合成 metadata/native 字节与临时文件；Node subprocess 使用 stub prepare/packager/finalize；entrypoint 使用 fake canonical modules。未把这些单元转换为真实 engine、native 或 semantic 结果。

独立核对 `main-integration-evidence/manifest.json` 的 35 个文件，实际 bytes/SHA 全部匹配。复读主控 `receipt.json` 的受限命令及 stdout：12 轮为 10 failed / 86 passed；17 轮为 1 failed / 95 passed；18 轮为 96 passed in 1.73s，stderr 为空，命令 exit0。主控修正了 runpy argv0、嵌入 JS URL 和 Node reporter；早期失败原件仍在。19 轮命令记录支持当时 Python format、JS syntax/eslint/prettier 和纳入 raw 之前的 diff check 通过。本 agent 没有重复执行这 96 项，也未执行全仓 pytest；新增的两项私有 mock 仅用于 F2 验证。

04/05 Node source 副本为主控从其自身 exact tool output 恢复，明确是 recovered，不能称原始备份。恢复的 04 SHA `4077d4372ed4cf5c2b2299981e635926e4eb216af739992d83f8e57ee27cde73` 与 05 SHA `92f4ea00ef7c6a96e45eba82f5d6457028800bb964518ae2c38ff45ba8dba28c` 与先前审查记录一致；05 真正创建全部 source ancestors，修正了 04 缺少 engine 目录导致的错误路径假阳性。后来的格式化副本和永久 Python 内嵌 JS 是独立身份，不替换上述历史输入。

分别独立执行了相对合同基线 `2fdd85375300bfbfa797588c348a205e1030ef6c` 的 `git diff --check`：四产品路径 exit0、无输出；整个 32d943 提交 exit2、64 行输出，指向 12 轮原始 pytest stdout 自带尾空白。保留 raw 空白是证据完整性要求，这不是产品源码 whitespace fail，也不能声称整个提交 diff check 无瑕疵。另核对 56c234→32d943 四路径 diff check 亦为 exit0。

## 签收限制

F2 需修正并对新固定候选另做 delta；32d943 的 96 项单元不覆盖该缺口。本报告没有运行真实 prepare、PyInstaller、semantic/full-v1、full pytest、GUI、native 或 parity；未接触 STOP native-location-N0-build。没有修改 I05 唯一拥有的 probe/tests。T03 四产品局部实现审查不能替代 I05 最终 observer 集成、root 执行前外部冻结批准、actual PYZ/完整 artifact、真实 native loader 和 semantic parity 的各自证据。
