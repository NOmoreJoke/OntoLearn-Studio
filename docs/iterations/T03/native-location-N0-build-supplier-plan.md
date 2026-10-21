# T03 N0 原生对象底座构建供方方案

2026-10-21。**接受 N0 三条新构建路径由 T03 提供，当前可进入方案审查；尚不具备已批准、可执行的构建输入闭包。**N0 可以独立于 SQLite／CPython／VFS 推进。下一窗口的具体前置是 I06 固定九文件及 ABI／测试契约、获准离线 CMake 和 Node-API／许可输入、根授予编译与受控运行窗口；Windows 另缺实际工具链／Electron import library。当前只读版本信息、源码／文件／Git／hash 与官方文档，没有安装、下载 headers／源码包、编译、addon 加载、native／FS／child／产品测试或打包。

D2 产品 `a4d1457fc6a1f1d1832296a8dcdb2ef42da75b98`、原交付 `2a0cfdf87fc9c59bb111cb0add5c9e08d03f8af9` 和收口 `4ff877de23b66c7c491d620d8630872ff4ce5fb4` 冻结。本轮在现有 T03 树只新增本主稿与 `docs/reviews/T03/native-location-N0-build-supplier-plan/`。不创建产品树，不改 AGENTS、D2、产品／依赖／锁／包或原 manifest，不重测 D2、不重建原 Goal；无 push／PR／merge。下面所有 writer、接口与运行命令均为后续具体授权的申请。

## 1. 固定依据与接受范围

| 固定依据       | 身份及用法                                                                                                                                                                                                                            |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T03 准备授权   | 3420B／SHA `eb27c36a54ad383863389317fb30b085c0f318184dc3d6fbfaecb3697e76b945`，已全文读；原字节 `authorization.md.raw`                                                                                                                |
| I06 固定主方案 | `9ff1c92e78cc0bed1e37b71ea7f00a57ad231f7c:docs/iterations/I06/native-location-supplier-plan.md`，49472B／`34c4307e42c349b5d4fc40d0960655454727570eb565c4fc1c3d521663c57624`，全文及 §8／9 N0；原字节 `i06-fixed-supplier-plan.md.raw` |
| I06 源码窗口   | 控制侧 `I06-native-N0-source-implementation-authorization.md`，6089B／`fc4a74b81530197a3aa38d0bcc5027d952d83c64d7f0a6cd5be2abdd3c9ce4ee`，全文；只授 I06 六产品／三测试，未授编译运行                                                 |
| 控制独审       | 18419B／`1f26965e9ef6f3f6dac02210afbb6f24b85be9dc4ac237290183799bf64ae558`，已全文读；不把 N1 缺口扩大成 N0 停工条件                                                                                                                  |
| 构建基线       | `5f910b52c69d86a1076b2032e5d3c63e715947f3` 的 package、Node 锁、desktop package／builder、Vitest／TS unit 配置六件，逐项 current=Git；精确 bytes／SHA 在 `inputs.json`                                                                |

I06 九个将来采用输入准确为：`include/location_abi.h`；`src/capability_core.cc`、`platform_macos.cc`、`platform_windows.cc`、`node_binding.cc`；`apps/desktop/src/main/security/native-location-owner.ts`；`tests/location_core_test.cc`、`location_child_probe.cc` 和 `tests/unit/i06-native-location-owner.test.ts`。前五及两 C++ 测试位于 `packages/native-location/`。计划来源树 `.worktrees/I06-native-location-N0`／branch `feature/I06-native-location-N0`／base5f；本轮检查时 ABI 头尚不存在，**没有可采用的固定源码 ref，不消费可变 WIP**。

| T03 拟新 writer，唯一维护者不转移              | 最小责任                                                                                                                                |
| ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `packages/native-location/CMakeLists.txt`      | 明确源码集合／平台选择、C++17、addon／两个 C++ 测试目标、输出／链接／CTest；不用目录 glob 吞未来 N1                                     |
| `packages/native-location/toolchain-lock.json` | 固定九源码与 ABI、外部 headers／hook／许可、工具／SDK／目标／flags、输入摘要与产物映射；缺项显式 incomplete，不能自称已锁               |
| `scripts/build-native-location.mjs`            | 只用已有 Node 内置模块读锁、逐 bytes／SHA／路径核验、固定 argv 离线 configure／build 与日志；不安装、不联网、不偷偷回退到全局另一个工具 |

下一构建实现应另建 5f 独立树／branch，名字由根登记；只按根批准的 I06 九字节清单逐件采用并只读，再写这三个 writer。本轮不创建。新源需要额外私有头／第三方代码时，必须作为精确新输入交根；不能临时生成未登记业务 helper 绕过九文件／三 writer 边界。

## 2. 已观察工具与真正缺项

`toolchain-metadata.json` 保十条实际只读 argv／cwd／双流／exit；`local-inventory.json` 与 `licenses-and-sdk-observations.json` 保有界文件库存、原长度／SHA。此为当前开发主机观测，不是目标 OS、native 构建或 Node addon 运行证据。

| 项目                | 本轮直接观察                                                                                                 | 限制／后续输入                                                                                                           |
| ------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| 开发宿主            | macOS27.0.1，build26A434，arm64                                                                              | 不替 macOS15 arm64；SDK 的 ValidDeploymentTargets 含15.0也不证明该系统运行                                               |
| Node                | `/usr/local/bin/node` 24.15.0，Node-API10、普通 modules ABI137                                               | 仅宿主 metadata；不能推 Electron 内嵌 Node／API、SQLite 或 Python ABI                                                    |
| 工程声明            | 5f `node >=24 <25`，packageManager npm11.12.1，Electron44.9.0，`@types/node`24.19.2                          | engine 范围不是精确编译器 pin；types 包不是 Electron runtime                                                             |
| Electron npm 元信息 | 实际 package44.9.0，MIT LICENSE；`abi_version` 为149                                                         | 149 是普通模块 ABI 标识，**不是 Node-API149**；未运行 Electron，内嵌 Node／NAPI 未证                                     |
| Apple 工具          | Xcode27.1／27A9275；Apple Clang21.0.0（2100.3.34.2）；SDK27.0                                                | 版本命令已成功；完整工具／SDK输入摘要、实际使用 header／linker／runtime 依赖闭包待固定及首构建核验                       |
| Make                | `/usr/bin/make` GNU Make3.81                                                                                 | Unix Makefiles 候选，尚未由 CMake／实际构建验证；Ninja不是本方案必需依赖                                                 |
| CMake／Ninja        | PATH 未找到；七个明确常见候选路径均不存在                                                                    | 只作有界库存结论，不声称全盘无工具；须根批准提供精确离线 CMake executable／版本／SHA／许可。不会自动 brew／pip／npm 安装 |
| 本机 Node headers   | `/usr/local/include/node/` 的四个 Node-API 头齐；`node_version.h` 为24.15.0，runtime支持1..10，默认模块 API8 | 观察原件和 SHA 已封；尚非批准离线供方清单，也未核成某个官方 archive 的字节身份                                           |
| Windows hook        | 现有全局 npm 所含 node-gyp12.2.0 的 `src/win_delay_load_hook.cc`、MIT LICENSE 真实存在                       | 外部只读构建输入候选，不把它放进未登记新 helper；还须源 pin／HOST_BINARY／直接链接闭包批准                               |
| Windows 工具        | 当前无 Windows宿主／MSVC／WindowsSDK／匹配 import library 的实际证据                                         | 不编造版本、路径、SHA、CRT 或可运行状态；不以 Mac 交叉产物代 Win11x64                                                    |

`observed-local-headers-and-hook.zip` 只保存十个已有文件的观测快照，逐成员读回；不是下载的官方 headers 包，不是依赖 adoption。Node 四 API 头的相互 include 与标准 C 头构成最薄表面，不需要 V8／`node.h`／libuv include／node-addon-api。Node 自身完整 LICENSE 在三个已查常见位置未找到；`node_version.h` 有 Node MIT notice，不能把 npm／node-gyp 的许可证冒充 Node 全发行许可闭包。下一窗口可由根明确批准当前原字节及适用许可来源，或另供带完整许可证、archive SHA 的合法离线输入；本轮不下载补齐。Apple SDK／MSVC 许可按各自合法安装工具链处理，不把开发工具 SDK 大包拷进产品仓。

## 3. ABI 请求：版本不能由构建供方猜定

以下精确请求已交根转原 I06 owner；收到固定头／源码 ref 前只能标 pending。Node-API 稳定性不替自有 C ABI 的结构布局、内存所有权、系统 ABI 或资源寿命保证。

| 要求的原件／契约                          | 必须冻结的内容                                                                                                                                                                                                             |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `location_abi.h` 与九文件 bytes／SHA／ref | 实际全部符号及 typedef；ABI版本和 size/alignment/offset；int固定宽度、mac dev／ino与Win完整volume+128bitID无损；调用约定／visibility／Windows导出宏；enum宽度；C/C++可用性。不能将 `long`／JS Number／裸HANDLE当跨平台身份 |
| 所有权及异常边界                          | 谁创建／持有／关闭 registry、记录、FD／HANDLE／map／child／work；分配与释放必须成对留在同一供方；没有C++异常／STL对象穿 C ABI；失败的 retained／unknown 与 cleanup仍有限可调用。不能靠 CMake 的 flag代替这份合同           |
| Node binding 实际调用清单                 | 所有 `napi_*`／`node_api_*` 及其最小 API 版本；实际注册宏与导出方法／参数／返回；每 env 的实例归属、GC finalizer与显式close、同步接纳点、queue／running／完成／异步cleanup钩子真实完成条件；不向renderer导出裸数值能力     |
| C++ 核心测试／child probe                 | 两文件的 `main`／argv／exit／超时和真实child路径契约、哪些库或core符号需要链接；测试 fixture锚点来源、受控temp上界和清理失败的真实归属；不能自创 `--child` 参数当现有接口                                                  |
| TS 单测／真实addon模式                    | `i06-native-location-owner.test.ts` 如何接收私有binding、实际addon路径与expected exports、哪些是stub单测／哪些触真实OS；固定Node/Electron加载入口、cleanup等待及有限日志，不让mock通过冒充addon通过                        |
| Windows 后端 imports／Mac availability    | 实际 include／动态符号／system import列表及不支持时finite拒绝。若用NT内部API，明确 `winternl.h` 签名、系统模块／查符号／缺失处理，不能默认一个未核的 `ntdll.lib` 足够，也不能用kernel-mode库链接用户态addon                |

**候选显式 `NAPI_VERSION=8`，不是先宣布未知源码的绝对最小值。**目前设计需要无损 BigInt／env实例与异步真实cleanup；已读本机头中 BigInt／instance_data属API6，async_cleanup_hook与type_tag属API8。若 owner不用8功能，可以按真实清单另定更低版本；若使用9／10／experimental，必须交具体调用与两个runtime支持依据，不能仅因宿主napi10就接受。构建禁 `NAPI_EXPERIMENTAL`，显式 `NAPI_VERSION`，用 `node_api.h` 的C接口；不引 `node.h`／V8／内部libuv。[Node24 Node-API稳定范围与版本矩阵](https://nodejs.org/download/release/v24.0.0/docs/api/n-api.html#implications-of-abi-stability)、[async cleanup API](https://nodejs.org/download/release/v24.0.0/docs/api/n-api.html#napi_add_async_cleanup_hook)。

正常 `NAPI_MODULE`／`NAPI_MODULE_INIT` 生成的标准注册出口可从固定头核：`napi_register_module_v1`、`node_api_module_get_api_version_v1`；不由此虚构 I06 自有 C API 名。最终检查实际 export／undefined／import 集与 owner 清单一致，拒意外第二 Node addon入口、V8或未批准native库。

## 4. 最小 CMake 目标和平台链接

拟 `cmake_minimum_required(VERSION 3.25)` 是工程支持底线提案，**不是 C++17 的绝对最低版本，也不是已存在的 CMake pin**。真实供应binary版本／SHA待交。启用 C／CXX（仅ABI头的C兼容性与C++17对象），CXX_STANDARD17、STANDARD_REQUIRED ON、EXTENSIONS OFF，关闭不必要的LTO／全局自动依赖发现。不得添加下载式 FetchContent／ExternalProject。C ABI静态布局检查只能在实际头冻结后按其契约加入现有C++测试／生成构建探针，不新增产品头。

| 目标                         | 固定源与边界                                                                                                                                         |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `i06_native_location` MODULE | core + **当前平台一个**platform源 + node_binding；PREFIX空、SUFFIX `.node`、PIC。Mac不编Win源，Win不编Mac源；未编分支的unsupported不记平台通过       |
| `location_core_test`         | 核心／本平台实现 + 原测试源，独立exe；不依赖Node runtime。core可作为OBJECT或STATIC仅链接进本进程目标，不新增shared-core DLL／dylib或第二registry服务 |
| `location_child_probe`       | 原child测试源；是否链接core／platform以固定调用契约决定；不自动spawn/运行。只用于后续受控测试，不成为第二业务Python／生产broker                      |
| CTest                        | 在原测试main／argv固定后注册真实可执行目标与 `$<TARGET_FILE:location_child_probe>`；执行目录和受控fixture仅后续窗口批准，不自造未知flags             |

addon目标显式定义 `BUILDING_NODE_EXTENSION` 与已确认的 `NAPI_VERSION`，前者使Windows `node_api.h`按addon使用Node-API import声明，不能只改后缀；不向核心／测试无谓传播Node宏。若core复用OBJECT／STATIC目标并链接进MODULE，该core目标也显式PIC，不能假定MODULE的属性会反向传播。

拟输出统一为 `build/native-location/n0/<target>/<inputDigest>/artifacts/`：`i06_native_location.node`、两个测试exe及必要PDB／debug符号。target分 `darwin-arm64` 与 `win32-x64`，不同锁／配置／架构不共用缓存；不向D2 engine／release写入，不覆盖原package。

**Mac。**configure 时在首次 `project()`／`enable_language()`前显式传 arm64、具体 SDK绝对路径、deployment target15.0，清理未批准的SDKROOT／MACOSX_DEPLOYMENT_TARGET／CPATH等隐含覆盖；当前SDK元数据的默认是27.0，不能靠默认值。addon对 Node-API符号使用明确宿主解析链接政策，候选 `-undefined dynamic_lookup` 与本机固定node-gyp/addon.gypi的darwin政策一致；这不是允许所有未知符号通配通过，必须在产物上核 undefined集合为允许Node-API及实际system/runtime符号。libSystem／libc++与所用ACL／spawn等来源以真实backend和依赖图为准，不加Linux式`-lacl`或凭名字签支持。构建15.0标记不证明SDK新API可在mac15调用；须audit availability、实际Mach-O最低系统／arch及mac15实机。较新flag／符号缺失须明确unsupported，不静默削弱policy。[CMake deployment target](https://cmake.org/cmake/help/v3.25/variable/CMAKE_OSX_DEPLOYMENT_TARGET.html)、[sysroot](https://cmake.org/cmake/help/v3.29/variable/CMAKE_OSX_SYSROOT.html)、[标准不能静默降级](https://cmake.org/cmake/help/latest/prop_tgt/LANG_STANDARD_REQUIRED.html)。

**Windows。**仅在实际Win11x64工具链 tuple冻结后配置；具体VS／MSVC／link／Windows SDK版本、host-tools与target架构、系统headers／libs、CRT策略和license须可核。拟RelWithDebInfo／Release `/MD`，显式 `MSVC_RUNTIME_LIBRARY=MultiThreadedDLL` 与CMP0091 NEW；不默认发布debug CRT或跨模块 `new/free`。Node-API addon手工CMake仍需**匹配Electron来源的 `node.lib`、直接编入 `.node` 的delay-load hook、`delayimp.lib` 和相符 `/DELAYLOAD:node.exe`／`HOST_BINARY="node.exe"`**。本机node-gyp12.2.0已有hook候选可按原文件SHA及MIT许可交根，不另造helper；不能以通用Node的lib或同扩展名证明Electron加载。实际imports还含ACL的Advapi32等时逐backend列，不照抄node-gyp全系统库列表。[Electron Windows hook要求](https://www.electronjs.org/docs/latest/tutorial/using-native-node-modules#a-note-about-win_delay_load_hook)、[CMake CRT](https://cmake.org/cmake/help/v3.31/prop_tgt/MSVC_RUNTIME_LIBRARY.html)、[GetSecurityInfo来源](https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getsecurityinfo)。NT内部API若被选用，按真实动态来源／不支持策略审，不把文档接口名外推为稳定系统ABI。[Microsoft内部API说明](https://learn.microsoft.com/en-us/windows/win32/devnotes/calling-internal-apis)。

## 5. 离线锁、许可与输入／产物闭包

锁应拒绝null／incomplete项进入对应构建分支，不能因“工具在PATH”即默认采用。至少包含：schema版本；批准base、I06 source ref、九文件逐path／bytes／SHA；ABI版本和实际symbol/API集合digest；T03三个writer自身字节承诺（外部回执记录其Git，不让锁自hash循环）；每目标工具绝对realpath／版本／binary hash、CMake generator／make或MSBuild、编译器resource／linker、SDK root/version/build与必要内容清单；四NodeAPI头／适用LICENSE；Win import library／hook／license及CRT；所有define／flags／linkpolicy／deploymentTarget；输出路径和实际依赖／符号预期。

SDKSettings／版本字符串及单个compiler SHA不是完整SDK锁。第一次获准构建需从实际compile_commands／依赖文件／链接输入核齐真实使用的headers、C++runtime、system stub／import libs和产物依赖，并与供应的SDK／工具chain来源摘要关联；结果不足则保持该目标incomplete，不倒填未采的字段。使用当前合法已安装工具链原件还是根交付的离线archive，须明列来源与接受方式；本机文件SHA不冒充官方tarball SHA。CMake工具许可、Node MIT、hook MIT、LLVM／Apple工具条款、WindowsSDK／MSVC及可再分发CRT分别登记，license file实际字节与需随产品分发的notice清单不混同。

驱动只用Node标准库 `fs/path/crypto/child_process`，固定可执行路径与shell:false argv。先verify九源、writer干净状态／外部输入／工具metadata，再configure，后build；原始stdout／stderr、exit和first failure都保存。不能尝试npx下载、node-gyp自动headers下载、npm rebuild、package锁升级、CMake自动网络取源、PATH fallback或将Win缺件默默当Mac通过。CMake配置本身可能try_compile，**也是编译窗口内动作**，本轮不执行。

## 6. 将来最小命令及尚待填实的位置

以下是**后续三个writer实现后的CLI合同／参数化命令**，不是当前已存在脚本，也不是已经执行的验证。`<...>`必须来自批准锁的真实值；任何未填项都拒绝执行，不猜路径或换工具。core可先独立构建，缺Node／Electron输入不阻止核心源码准备；真实运行仍单独授权。

拟驱动最小入口：

```text
node scripts/build-native-location.mjs --target darwin-arm64 --component core --verify-only
node scripts/build-native-location.mjs --target darwin-arm64 --component core --build
node scripts/build-native-location.mjs --target darwin-arm64 --component addon --build
node scripts/build-native-location.mjs --target win32-x64 --component addon --build
```

`--verify-only`只读清单；各 `--build` 分支分别按分支验证必需input，不能从core成功自动开addon或Windows。锁文件固定是 `packages/native-location/toolchain-lock.json`，不接受任意source路径／任意CMake define通道。未实施前不把以上命令作为工具存在的证据。

Mac core最小实际工具argv提案，源固定后由驱动生成：

```text
<OFFLINE_CMAKE> -S packages/native-location -B <BUILD_DIR>
  -G "Unix Makefiles" -DCMAKE_MAKE_PROGRAM=/usr/bin/make
  -DCMAKE_C_COMPILER=/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang
  -DCMAKE_CXX_COMPILER=/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang++
  -DCMAKE_OSX_ARCHITECTURES=arm64
  -DCMAKE_OSX_SYSROOT=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk
  -DCMAKE_OSX_DEPLOYMENT_TARGET=15.0 -DCMAKE_BUILD_TYPE=RelWithDebInfo
  -DI06_BUILD_ADDON=OFF -DI06_BUILD_TESTS=ON
<OFFLINE_CMAKE> --build <BUILD_DIR> --config RelWithDebInfo --target location_core_test location_child_probe --parallel 2
<OFFLINE_CTEST> --test-dir <BUILD_DIR> -C RelWithDebInfo --output-on-failure
```

这是argv分行展示，不要求用shell换行拼接；底层调用shell:false。CTest在实际测试契约冻结并根批准受控fixture后才运行，当前没有其固定argv。addon分支把 `I06_BUILD_ADDON=ON`、明确四头目录和 `NAPI_VERSION=8`（owner实清单确认后）传入，target是 `i06_native_location`；不能在未知ABI时声称此CMakeLists已能生成。

真实加载最小探针可以用已有Node，**仅检加载／注册元信息**，不能代资源操作测试：

```text
/usr/local/bin/node --eval 'const a=require(process.argv[1]); console.log(JSON.stringify({versions:process.versions,exports:Object.keys(a).sort()}))' -- <ABSOLUTE_ADDON_PATH>
node_modules/.bin/vitest run tests/unit/i06-native-location-owner.test.ts
```

第一条依赖实际frozen expected exports，后者需owner给“真实addon模式”的路径／注入契约；普通stub单测不能记真实load。核心/Node可在批准开发宿主取得局部证据，不宣称Electron／两目标OS通过。

Electron44.9的实际binary及fuse证据另冻结。只有先静态确认该binary的 `runAsNode` fuse启用，且根明确授权headless运行，才允许 `ELECTRON_RUN_AS_NODE=1 <固定Electron> --eval <同类加载代码> -- <addon绝对路径>`。fuse禁用时变量可能被忽略，不能冒险启动GUI当headless；不给自动回退。必须分别记录Electron实际process.versions、Node-API与模块ABI、addon路径／hash／真实加载和cleanup；宿主Node24 load不替代它。[Electron环境变量及fuse限制](https://www.electronjs.org/docs/latest/api/environment-variables#electron_run_as_node)。

Windows最终命令必须在root交付实际MSVC x64环境、固定SDK／CMake generator／toolset tuple后生成；用 `-A x64` 的VS generator或固定Ninja＋MSVC环境二选一锁定，不混generator，不假填某个VS版本。随后同样CMake build／CTest、Node与Electron分别load，dumpbin实际imports／exports／dependents与hook直接链接回证；缺字段时当前Windows命令表保持pending，不把模板标可直接执行。

## 7. 首个真实窗口的验收和证据

先由根选择“宿主core”“宿主Node addon”“目标Electron／Win”等精确子窗口，并给受控独占临时fixture边界；不因为计划接受就全部运行。未来每个首次configure／build／test／load保全部argv／cwd／环境差异、OSbuild／CPU／FS、源码与输入hash、SDK／工具／flags／依赖图、完整双流／真实exit、未完成／首失败、产物hash与签名状态。已有产品或用户目录不作为fixture。

I06负责功能反例：单组件acquire、ancestor/root/member普通rename／replace、symlink／reparse／hardlink／新inode、ACL／identity、reserve-before-dispatch、旧epoch／取消／晚返回、真实close／unmap／child终态；不把逻辑timeout或Promise完成当释放。T03提供固定binary及测试入口与实际链接证据，不自改ABI语义、调高预算、屏蔽失败或用注入mock冒充OS终态。未围住的publish／namespace分支保持unsupported。I06 source-ready／core编过／Node load各有不同结论，不汇成完整N0通过。

同目标两次干净构建是后续可重现性检查，记录真实源／工具／SDK／flags和原产物，再解释路径／debug／UUID／签名等差异；不能沿用D2的精确wcwidth binarypair裁定当通用native归一。源／产物／代码或段／签名字节分域，任何规范化必须另定清单，保原hash。未运行的性能不量化。

## 8. 最小下一步与独审

可接受三writer的实现申请；当前明确未齐：I06九原件／ABI／test argv、离线CMake实际版本／binary／许可、选用Node headers完整许可／来源接受、Electron内嵌Node/API与headers/runtime来源、Win Electron node.lib／hook／delayimp／MSVC／SDK／CRT。按所选子窗口验证真正必需项，不用Windows或Node addon缺件阻止无关core源码工作；也不把这份条件接受写成已有构建就绪。

N0目前无需 `package.json`／npm lock／pyproject／uv.lock／build-engine／entrypoint／desktop package／builder／verify-sources delta：脚本可直接 `node`调用，source核验在新driver，addon与测试只进独立build目录。将来要把addon放入真实App，最少另申请desktop builder的明确extraResources或asarUnpack／装载路径delta；要自动串入check/package脚本才另申准确package.json delta。当前不借三个writer申请整个旧构建维护面。

N1另待完整CPython／SQLite source/archive SHA／LICENSE、实际os_unix/os_win、I06精确patch、flags和私有同image `_sqlite3`／VFS依赖图；本轮不取源、不建SQLite/Python、不用其缺项无限等待N0。B-R／fresh／历史／持续namespace／跨main旧holder、生产bootstrap／T01消费／公共LocationLease／首数据库IO／目标双OS／包内GUI／父I06与57P0、指定两模型同版双审／CI／正常合并仍保留，原Goal不重建。

独立agent审本固定主稿的构建／ABI／来源／两平台错误假设，报告与逐项处置仅在本review目录。官方页调查只提供设计规则，不提供本机tool hash或目标通过；初次四页CMake并行open连接失败保留，后官方检索成功与独审各自读取来源另记。固定主稿snapshot、input、审查／处置、证据manifest与真实Git ref交根后，再决定三个writer／九文件采用／运行窗口。
