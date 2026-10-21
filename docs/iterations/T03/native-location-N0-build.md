# T03 N0 三构建源码与官方工具材料交付

2026-10-22 metadata窗口追加：仅三writer与新非执行JSONL metadata修复候选，原JSON/28来源/33464+9308全pin保留；最终静态完整映射、有限反例及预算详host-core-build/metadata-optimization/index.md。第二次configure/build尚未授权；首轮失败7bfd原件保持，静态优化不记N0通过。

2026-10-22 首轮真实结果：c80cbcd固定输入的唯一core构建尝试driver exit1；0–10 Git命令全0，11 configure在600000ms ETIMEDOUT/status=null/SIGTERM，12 build未派发。没有两个目标产物/编译命令，tests NOT_RUN。85原日志与首次失败详host-core-build/first-build-summary.json；静态复杂度嫌疑与未实施修复提案另列，不认定唯一根因、不原样重试。

2026-10-22 构建窗口追加：f6e9f42完整12候选与实际环境/直接GNU make独审已固定；仅Darwin工具链和core执行按真实归档授权ref开启。批准后完整输入见host-core-build/approved-input-manifest.json，下一条仅原13命令的一次core构建；尚未记构建成功，所有产物执行及Node/Windows门仍关闭。

2026-10-22 源采用追加：九原件独立采用a026322，授权/回执ac37，源与静态合同锁产品6614837；完整产品/tests为12，实际12API最高门3仅获静态接受，详source-adoption/summary.md。后续7961/1879另授固定DEVELOPER_DIR和精确GNU make后薄宿主core，当前实际环境/供方复审及构建证据另见host-core-build；下文旧阶段原件保留，不混阶段结论。

2026-10-22 追加状态：控制侧在 c7 静态预审中新增 R5 日志异常路径问题，现已最小修订 driver 并另交同候选独审、静态及只读 incomplete 校验；详 review 下 `logging-fix-disposition.md`。另获准的工具提取/版本/供应清单窗口由独立材料 agent 执行，真实出口与读取 guard 缺口详 `tool-supply/index.md`。所有 source/toolchain/execution/binding/testAssembly 审批仍 false，API3 仍待完整 binding 固定源证明。以下原章节及原 manifest/报告记录 c7 首轮静态交付，保留其原始证据和阶段边界。

2026-10-22（授权日期 2026-10-21）。本轮完成三份真实构建源码及官方材料静态准备，**未进入 configure、try_compile、编译、CTest、native/child/FS 测试或 addon/Electron 加载；N0 不记构建通过。**锁中九源码采用、工具链供应、实际 binding 最低 API 和执行窗口均明确 pending。没有用假头、业务 stub、猜测 exports 或临时 helper 凑出可执行闭包。

源码树 `.worktrees/T03-native-location-N0-build`，branch `feature/T03-native-location-N0-build`，从批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3` 新建。产品改动只含 `packages/native-location/CMakeLists.txt`、`packages/native-location/toolchain-lock.json`、`scripts/build-native-location.mjs`；过程仅本稿和 `docs/reviews/T03/native-location-N0-build/`。没有切换旧树、采用 I06 WIP、修改旧配置/依赖/锁/入口/打包/CI、重测 D2、push/PR/merge 或改变原 Goal。

## 实际源码与拒绝边界

驱动只依赖现有 Node 内置 `fs/path/crypto/child_process/url`。CLI 严格接受 `--target darwin-arm64|win32-x64`、`--component core|addon|fixture-addon`、恰好一个 `--verify-only|--build`；拒绝未知、重复、任意 source 路径、任意 define 和额外参数。锁 schema 对所有层次的字段、枚举、类型、精确九文件顺序、审批 ref、绝对 path/realpath、bytes/SHA 作有限校验，JSON 重复 key 也拒绝。三 writer 自身身份由只读输出和外部 manifest 记录，锁不自 hash。

`--verify-only` 不 spawn、不写输入或日志、不执行版本探针。它读取三 writer、获准材料 index；只有相应 supply/adoption 已批准时，才读取那些固定输入。目前未批准的九源和工具路径均不读取。报告区分 `rejected`（exit1）、准确 `incomplete`（exit2）及满足输入的 `complete-readonly`（exit0）；后者仍不是构建或运行通过。当前实际只读检查返回 incomplete。

未来 `--build` 只有完整输入、对应 target/component 执行审批和宿主架构一致时才可达。当前没有运行该入口。未来先拒缺项，再创建独占、禁止复用缓存的 `build/native-location/n0/<target>/<inputDigest>/<component>/`；inputDigest 纳三 writer 身份，锁本身又纳源码和工具 pins。固定 Git executable 必须也获批且逐 bytes/hash 校验；运行后保产品三 writer/九源 clean 状态、真实 HEAD、源 ref 的逐 Git blob 比对。configure/build 使用固定绝对 CMake、`shell:false` 的 argv、最小或批准的固定环境，不承接用户的 CFLAGS、CXXFLAGS、CPATH、SDKROOT、CMAKE_TOOLCHAIN_FILE 等隐含覆盖，不自动安装/下载、找 PATH 工具或回退 generator。完整双流直接写文件，记录真实 status/signal/error、环境、首失败；一旦开始 dispatch，异常报告保留执行事实。既有目录、首失败和日志均不覆盖成新成功。

CMake 在 `project()` 前检查 source/工具链/该执行窗口，所有对应 addon/Windows pins、版本及审批门；未齐时不进入 compiler probing。精确列出九源身份，只编 core 和当前平台 backend，禁 GLOB/FetchContent/ExternalProject/自动取源。C++17、STANDARD_REQUIRED、EXTENSIONS OFF、PIC、私有 C++ hidden visibility；Mac 在 project 前固定 arm64、批准绝对 SDK、最低15.0；Windows 固定 Ninja+MSVC 环境、64bit、`MultiThreadedDLL`，实际工具链和 system library pins 缺失时保持拒绝。未提供任意交叉编译入口。

三个 component 各自对应：

| component     | 固定构造                                                                                   | 额外前置                                                                                                              |
| ------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| core          | `location_core_test` = core+当前平台+原 core test；`location_child_probe` = 原 child probe | 原测试拼装契约；不检查 Node/Electron/Windows addon pins                                                               |
| addon         | `i06_native_location.node` = core+当前平台+原 binding，普通 addon 无 fixture bootstrap     | 实际 binding 最低 API、四官方 API 头和完整 Node LICENSE；Win 另需匹配 Electron node.lib、原 hook、hook 许可、delayimp |
| fixture-addon | `i06_native_location_test.node` = core+当前平台+binding+原 core test 四 TU                 | 同一 registry，另启 `NL_NODE_FIXTURE_HOST`；不在独立 host/static core 间传 registry id                                |

addon 显式 `BUILDING_NODE_EXTENSION`、`NL_WITH_NODE`、候选 `NAPI_VERSION=3`。Mac 链接宿主 `dynamic_lookup`，最终 undefined 符号审计待实际产物；不把链接政策当任意 native 依赖白名单。Win 直接编入批准原 hook，`NL_BUILD_SHARED`、`HOST_BINARY="node.exe"`、`/DELAYLOAD:node.exe` 和批准绝对 import libraries；不猜 ntdll.lib 或系统 import 清单。core 的 CTest 只注册原测试 `<absolute child target>` 和外部15秒 timeout；驱动没有运行 CTest/测试/加载的代码路径。timeout 不是 native release/cleanup receipt。

## 只读 ABI 契约与九源仍待采用

根交 `6a7789bf0c1e5e7b0f25f37c86e0c9d64c6dc20d` 两件只读契约已全文读，未复制或采用其产品头：

| 原件                                                       | bytes | SHA-256                                                            |
| ---------------------------------------------------------- | ----: | ------------------------------------------------------------------ |
| `packages/native-location/include/location_abi.h`          | 13296 | `fc3f7983d62b0ef4f5a3a056198c00a0b971d2ae722acc33bc6f61937ec8e172` |
| `docs/reviews/I06/native-location-N0/abi-build-handoff.md` | 17562 | `8b3ba7c43935fac973a550944f6c2f5f69c94623162b31a75e0da26053ac7134` |

按该交接，自有 C ABI=1，core 11 个 public 函数及 NL_WITH_NODE 的第12个 `nl_node_bind_fixture`；C++17、固定宽度布局、Win __cdecl/export 宏及私有 backend 隐藏由原头定义。驱动/CMake 均要求将来采用头摘要与本固定契约一致，不能默默换头后沿用旧合同。交接的11个同步 Node-API 候选调用最高是同步 env cleanup hook 的 API3；旧计划的8已被这份具体候选清单替代。尚未用全九实际 binding 源核定最小值，approval=false；禁据宿主 NAPI10 或 Electron 普通模块 ABI149 推 Node-API 版本。

普通 addon 只允许交接的 abiVersion/fixtureBound/productionAdmission 标志，不能由标志自证授权；八个同步 bound 方法仅由原 fixture native bootstrap 绑定。CMake 只组装固定源码，不新增 JS opener/bind 方法。真实 TS addon 注入约定是 `I06_NATIVE_LOCATION_TEST_ADDON`，child 只接受 `--hold-until-eof`；这些是固定交接，不是本轮执行证据。资源限额、terminal/revoked、retained、唯一 child reaper 和 cleanup 语义仍归原 I06 实现及后续运行验证；本构建供方不改它们。

完整九文件固定 ref/逐 path bytes/SHA 和根精确只读采用仍缺。锁的 source.ref=null、source.approval=false、九项 bytes/hash=null 是有意保留的事实；没有从可变 WIP 补齐。未成熟 N1、CPython/SQLite/VFS 不作为当前 N0 三源码工作的停工理由。

## 官方离线材料实际结果

独立材料 agent 只写受控 `/tmp/T03-native-location-N0-tool-inputs/run-20261021T154556Z-9de064fe` 和本 review 的 tool-materials 目录，未改产品或提交。`tool-materials/source-index.json` 记录完整原始 URL、实际重定向/终态 HTTP、时间、限额、bytes/SHA、许可/版本依据和首失败；锁 pin 该来源 index。二进制没有 stage 入仓库。

- 官方稳定 CMake **4.4.4**，macOS universal，官方 minimum macOS12；选择依据为官方 stable 下载区，另列 4.5.0-rc1 未选。归档 89,454,352 bytes（小于250MiB），SHA `4b7b73704b1db9b374e5c9ab8e17ac6148b817b6396ee75cd94a852cbac9d305`，与完整官方21行 checksum 清单的唯一 basename 项一致。
- 归档静态检查9,041成员：8,839 regular、189目录、13 symlink；路径、重复、类型、累计尺寸、逐段链接最终目标检查通过。cmake/ctest 静态 Mach-O 头均含 arm64；同版 CMAKE_ROOT 1,686个 Modules 文件、必要模块和 plist4.4.4 均保全。主 BSD 许可和附带许可原字节在 tmp 保留。没有解压安装树或运行 archive 代码，未以静态 plist 冒充 `--version`。
- Node **v24.15.0** 只取完整 LICENSE156,926 bytes和指定四 API 头合计52,569 bytes；全部 HTTP200，均在授权限额内；四头与本机 `/usr/local/include/node` 对应原件逐字节相同。不是 types 包、npm/node-gyp MIT 或新 Node runtime 替代。
- 保留 web restricted-URL 首失败（无 HTTP终态）、首轮审查器对 framework 间接 symlink 的误报原记录；修正为归档内不落盘的逐段解析后通过。没有失败 partial，不抹首失败。

材料静态通过不等于批准安装/执行或供方已齐：归档尚未提取供应，CMake executable/CMAKE_ROOT真实安装 pin 尚 null，Node 材料采用也仍待根核验。tmp 保留性有限；材料丢失必须按原来源/身份另开授权恢复，不能自动重下。没有 PGP 验签结论。

## Apple 供应对象与后续观测分开

前一固定56a方案直接观察了合法安装的 Xcode27.1/27A9275、Apple Clang21.0.0、SDK27.0、`/usr/bin/make`3.81。本轮没有重跑这些元信息命令；它们是已知候选供方，尚非本锁已批准输入。可供根后续固定的对象是 `/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/` 与 `/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk` 原安装树，按真实 root/version/realpath、有限供应 inventory 摘要、设置和适用许可 pin 记录，不复制整个 SDK。

SDKSettings 候选原件7948B/SHA `7b93ad7e534cc4b31c6a4e39d19b5e0288acf2168c2649479a796d1cb51939fb` 来自前轮直接观测，当前未将其填作批准供应。工具锁的 resourceInventory/SDK inventory 仅是供应对象清单（schema 为 roots+逐 file 的path/realpath/bytes/SHA），不是声称已观察的实际编译依赖。首构建后的 compile_commands、depfiles、真实 used headers/stubs/libs、Mach-O/import/export/undefined 与资源运行终态均是待产生输出，不要求在首次 configure 前伪造它们。build log 即使成功也保 `PENDING_POST_BUILD_AUDIT`，不能自动关闭依赖/目标OS/N0验收。

## 实际验证、独审及下一窗口

实际命令/双流/exit 见 review 的 `static-validation.json` 及 `verify-*.stdout/.stderr/.json`。Node `--check`、Prettier格式检查、JSON及静态源码清单/门顺序检查只证明当前静态范围。只读 core/addon/fixture-addon 各分支返回 exit2/incomplete，core 输出无 Node/Windows addon 缺项；Win 宿主不匹配明确另列，不冒充 Windows 运行。未通过改变输入锁、造 fake fixture 或调用 --build 来试验分支。

独审 `independent-source-review.md` 与逐项处置 `review-disposition.md` 保留首版问题和最终候选身份。外部 manifest 记录产品和过程文件逐 bytes/SHA，自身不循环收录；固定源码 ref、最终状态及核验 receipt 通过本地提交回报根。

下一步由根分别核验九源、三构建源码和所选 component 的真实供应输入，再精确批准只读采用、工具提取及宿主 core configure/build。受控测试还需原 fixture/main/cleanup 条件与单独运行授权；addon/目标 Electron、Windows 分别独立。当前不执行下一窗口。N0资源真实终态/mac15/Win11、生产 LocationLease/同库SQLite/VFS/B-R/fresh/跨崩溃 holder、T01全消费/父57P0、指定同版双审、CI、正常develop合并和原Goal均未闭；D2数字不能充 N0 证据。
