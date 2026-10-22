# M08 后续私有 build-provenance / entrypoint 最小接口方案（待授权，未实现）

当前三路径修复只解决声明、锁及打包收集。不能把锁文件、metadata 或 PYZ 中打印的 source hash 当作实际运行身份，更不关闭 full-v1 / B1 或 frozen guard。源/包最终候选应在 I05 的 401a6844d25b8990606ae82fc85f932cac352d40 后集成，禁止沿用本树 2cf probe 指纹作最终 pin。

## 精确责任与额外路径

| 路径                                                                      | 唯一负责人            | 最小改动（本次未写）                                                                                                            |
| ------------------------------------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/build-engine.mjs`                                                | T03 supplier          | 在已有收集基础上生成严格私有 provenance、临时 anchor、实际产物清单；不改公共 schema。此新增行为仍需 root 精确授权。             |
| `packages/engine/entrypoint.py`                                           | T03 supplier          | 只在现有 dispatch 前增加 `--semantic-source-package-probe` 路由，延迟导入同一 canonical module，传原 argv，其他分支原样。       |
| `packages/engine/src/ontolearn_engine/semantic_build_provenance.py`（新） | T03 supplier          | 有界读取与 strict 私有字段校验、固定目录解析、loader code/资源/分发版核验；不实现通用 runner。                                  |
| `packages/engine/tests/test_semantic_build_provenance.py`（新）           | T03 supplier          | 实测 strict 拒绝、source/code/lock/metadata/resource/anchor 错配及失败不产生成功身份。                                          |
| `packages/engine/src/ontolearn_engine/semantic_source_package_probe.py`   | I05 唯一 probe writer | 消费上述 reader，更新最终 supplier/lock/probe/profile pins；在真实核验全部通过后替换 frozen unavailable guard，绝不无条件删除。 |
| `packages/engine/tests/test_semantic_source_package_probe.py`             | I05                   | 保留 M06 counter=None 修复，补 reader 失败映射及 source/package 同固定 selector 验证；T03 不代写。                              |

T03 新增产品路径共三个：entrypoint（已有文件）、私有 reader（新）、reader tests（新）；既有 build 文件追加行为另审。临时 anchor 与 provenance 均为 `build/` 产物，不写 source/WIP；不改 contracts、资源内容、descriptor public schema 或 N0 caller。

## 私有冻结格式与真正绑定

拟定 `i05-private-build-provenance/1`：严格 JSON，拒绝额外/重复键、非有限数、越限字段和重复路径。生成输入只来自 root 冻结的最终 postintegration Git commit、固定路径及真实 resolver 环境，不用 cwd 显示、日志自述或模糊最近文件。字段至少包含：最终 commit/tree、三 supplier 路径身份、entrypoint/probe/reader 身份、22 项 SUPPLIER_PINS、4 项 PUBLIC_RESOURCE_PINS、两原 JSON bytes/SHA、uv.lock bytes/SHA、八项实际 distribution 版本及 wheel 安装文件与许可证清单、Python implementation/version/cache_tag/SOABI/编译 optimize 与实际构建解释器及共享库 hash、每个目标模块 compile-code 的既有文件名归一化 marshal 指纹。格式和 caps 由双方冻结测试后才用，不把方案中的数值/字段当现有运行事实。

build 在独立 `build/generated/` 生成仅含该 provenance SHA 的私有 anchor 模块，经明确 hidden-import 打入 PYZ；frozen reader 从 `_MEIPASS/provenance/i05-private-build-provenance-v1.json` 读取并比对 anchor，然后从实际 loader.get_code 得出同 Python/optimize 的规范指纹，逐项匹配 build 输入源字节编译所得指纹。不能以 source 中声明的 SHA 代替实际 loader code。source 分支仍核真实源字节，并使用同一冻结输入身份；两者返回同一身份字段，frozen/source 差异显式保留。

构建后在包外生成 `build/m08-validation/i05-artifact-binding-v1.json`：真实最终 launcher、PYZ、Python shared library、provenance/anchor、全部资源及第三方运行文件的 bytes/SHA，连同命令、退出状态和 provenance SHA。root 在运行前冻结其 SHA 与实际完整产物目录清单；运行前由被授权执行方核实际产物匹配该外部冻结记录。运行后只能追加验证 receipt；原 binding 不覆盖、不回填。输入、代码或产物变更必须另建不可变 binding 版本并重新验证。未核、缺项或错配均阻断，运行 reader 单独成功不得冒充 root 的 artifact 批准。这里是本地 hash 绑定，不声称已有签名或发布者证书；如需签名，应另定真实签名方和验签信任根。

## 八项运行闭包与消费约定

固定实际版本为 pyparsing 3.3.3、pyshacl 0.30.1、rdflib 7.6.0、owlrl 7.6.2、packaging 26.3、prettytable 3.18.0、wcwidth 0.9.2、html5rdf 1.2.1。reader 对实际 metadata 和分发文件/许可证逐项核，native extension 要有真实导入/加载证据；锁存在和文件存在分别只作对应静态证据。两原 JSON 和原 contracts 精确 bytes/SHA 保留，不重生成 oracle。

I05 reader 消费必须先完成旧 precondition 全部既有检查，再核 frozen provenance/实际 code/实际资源/八版本，全部通过才允许原 fixed selector 进入观察。`packageCodeBoundToSource` 只在上述实际绑定成立时标为已验证；外部产物冻结未完成继续 unknown/拒绝。I05 更新自己的唯一 probe 与相应测试，T03 提供实际冻结 supplier commit/lock/构建证据，root 确定整体验收候选，不让两线同时改 probe。

## 固定运行及最终 pin 更新顺序

1. 当前三路径 supplier 冻结后，I05 从自身最新 401a 候选显式集成；新完整候选生成新的 source 与 probe/entrypoint/reader/lock 身份。原 manifest 的 320 datasets / 417 observations / unresolved 5 不因依赖修复改变。
2. root 授权额外路径后实现并独审本接口，冻结私有格式、真实生成器/reader及完整候选，执行正常 check/source/package；首失败保留。
3. source 固定 argv 为 `[own Python3.12, -m, ontolearn_engine.semantic_source_package_probe, --semantic-source-package-probe, full-v1]`；package 对应 `[实际包内engine, --semantic-source-package-probe, full-v1]`。两个 B1 selector 原样为 `b1-semantic-1x-v1`、`b1-semantic-10x-v1`；不新增随意路径/命令接口。
4. root 另授运行窗口后才执行 source/package 同输入 full-v1/B1。若实际语义失败，记录失败，不改 oracle、不回填历史通过。运行结果只追加独立验证 receipt，原外部 binding 不改；如需修改候选，先冻结新的 I05 candidate pins 与新版本 binding，再进行对应验证，整个新候选按现行指定双审门禁处理。

当前状态：本方案未实施，三个额外产品路径零修改；本轮既有 pytest 的 canonical/full-v1 已真实执行；B1 fixture 的独立结果仍 UNKNOWN，完整 source/package CLI 对照未执行，native/GUI 未执行。完整 source/package 证明仍待上述真实产物、接口批准与实际运行。
