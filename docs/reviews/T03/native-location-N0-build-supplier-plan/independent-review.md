# T03 N0 构建供方静态方案独立审查

2026-10-21。**接受最终主稿作为 T03 三条新构建路径的受限静态供方方案，未发现剩余 P1／P2 阻断。**这不是已取得完整构建闭包，也不批准 writer／采用／安装／下载／configure／编译／addon加载／native或目标平台运行。I06 ABI、具体源码及工具输入未齐，主稿准确保留这些待决项；N1 的 SQLite／CPython 缺口不阻止独立 N0 源码准备。

## 受审候选与实际审查边界

实际树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-profile-build`，当前 Git HEAD `4ff877de23b66c7c491d620d8630872ff4ce5fb4`，branch `feature/T03-profile-build`。D2产品和过程不改。

全文读取本轮准备授权3420B／SHA `eb27c36a54ad383863389317fb30b085c0f318184dc3d6fbfaecb3697e76b945`、I06源码授权6089B／`fc4a74b81530197a3aa38d0bcc5027d952d83c64d7f0a6cd5be2abdd3c9ce4ee`及首稿；核固定9ff1设计的N0相关§2／3／8／9与逐字来源身份。控制侧18419B报告仅核固定原件／hash及其权限角色，不把“根已全文读”冒充审查者亲跑产品或重审全部N1设计。

| 受审对象 | bytes | SHA-256 |
| --- | ---: | --- |
| 首稿／`main-plan-review-input.md.raw` | 27663 | `08a7361228c8604781f50bda5db2d6a1e5e9a1808c0bd1c2d6b5df4bf7cd70a5` |
| 最终主稿／`final-plan-review-input.md.raw` | 28008 | `50cddad30ed8c7302cb0c007ccab8fa2bd71967389897d44ad3bfeee03277124` |
| 固定I06原设计49472B | 49472 | `34c4307e42c349b5d4fc40d0960655454727570eb565c4fc1c3d521663c57624` |

首稿全文审查后，只对`revision-for-review.json`所列三处修订作精确diff复核；最终主稿与final snapshot逐字相同，未重复探索或复跑无变化产品。当前Git改动仅保护AGENTS既有dirty及本轮允许的新主稿／review目录。审查者只写本报告，不修改主稿／产品／其他证据，不提交。

本审实际使用Git、文件读取、Python标准库JSON／ZIP／hash／diff及官方文档浏览。未import产品，未运行工具链版本命令或重新采集十条metadata，未配置／编译／链接／执行addon／测试／FS／child实验，未下载headers／源码包／安装或调用GUI／Keychain／模型／付费／push／PR／merge。负责人metadata是既有实际原件，下面的独核指文件／原字节核验。

## 固定来源、实物库存与证据独核

1. 四份只读设计／授权snapshot均按`inputs.json`核长度／SHA及原文件或固定Git blob；六份5f构建／测试配置均current=Git=清单。准备授权只授本主稿和review目录，未偷换为三writer实施权。
2. 首稿／最终snapshot／两版bytes及SHA精确吻合；`requested-owner-inputs.json`准确列九个唯一来源路径，固定source ref与最终NAPI版本仍null，没有把I06可变WIP当已采用源码。
3. 观测ZIP十成员无重名，每件长度／SHA均实读核验，并与实际本地headers、node-gyp包／hook／MIT许可证一致。`observed-node-gyp-addon.gypi.raw`与实际全局node-gyp12.2.0文件逐字相同；未执行gyp文件。
4. 八个已选工具指纹逐当前文件实算长度／SHA吻合。`/usr/bin/clang`等工具mux与真正Xcode compiler分开；clang++ realpath归clang不当第二编译器证据。此核验不把八文件提升成完整SDK／toolchain lock。
5. license／SDK观察中存在文件的bytes／SHA逐当前原件核同，三个Node完整LICENSE常见路径及一个Apple许可候选确实缺失。SDK27元数据含macOS15.0及默认27.0；这只是元数据，不能当macOS15运行或所有availability通过。
6. 已读十条实际工具只读metadata的完整argv／cwd／双流／exit0。Node24.15／NAPI10／modules137与Electron包44.9／`abi_version`149分开；没有Electron runtime运行记录，149不是NAPI版本。PATH和七常见候选找不到CMake／Ninja只支持有界缺项，不支持“全机不存在”。

## 三writer与构建／ABI判断

**路径和阶段。**三条拟新writer恰为`packages/native-location/CMakeLists.txt`、`packages/native-location/toolchain-lock.json`、`scripts/build-native-location.mjs`。九文件采用和独立5f树均等根另授；当前不建树、不拷WIP、不改既有package／锁／build-engine／entrypoint／builder。CORE、addon、两个测试exe及平台选择可在这三条路径中表达，无需为N0引入SQLite／Python、第二broker或shared-core服务。未来App装载／打包delta仍需单列授权，未借本轮泛化旧构建维护权。

**ABI与Node表面。**候选API8明确是待owner实集确认的设计提案。实际四头与官方定义支持env实例／BigInt在6、异步cleanup和type-tag在8；不能以Nodehost NAPI10代Electron支持，也不能用types包或普通模块ABI推断。实际Node头可生成标准`napi_register_module_v1`与`node_api_module_get_api_version_v1`，主稿没有伪造I06自有函数。Node-API只承诺其C表面；V8、Node C++、libuv、外库与自有C ABI布局不在该保证内。主稿请求固定宽度／size-align-offset／调用约定／分配释放／线程／真实cleanup，不让CMake flag替资源语义。[Node24官方ABI边界](https://nodejs.org/download/release/v24.0.0/docs/api/n-api.html#implications-of-abi-stability)、[版本与cleanup](https://nodejs.org/download/release/v24.0.0/docs/api/n-api.html#napi_add_async_cleanup_hook)。

**CMake与core。**3.25是工程floor而非虚构安装版本或C++17绝对最低值；CXX17＋REQUIRED＋EXTENSIONS OFF避免降级。MODULE、空prefix和.node suffix、当前平台唯一backend、core／测试不依赖Node、生成物隔离及禁止网络FetchContent均合理。只有最终冻结头后才生成布局／C兼容性构建探针；本轮不以CMake configure名义绕过编译禁令。显式core PIC补充正确：MODULE自身PIC不自动反向设置其OBJECT／STATIC依赖。[CMake库类型与PIC](https://cmake.org/cmake/help/latest/command/add_library.html)、[CXX标准要求](https://cmake.org/cmake/help/v3.31/prop_tgt/CXX_STANDARD.html)。

**Mac。**arm64、具体sysroot、15.0 deployment须在project前配置；现有SDK27／宿主27／工具指纹不等于mac15目标通过。原gypi的darwin dynamic_lookup确有对应设计依据，但主稿另要求逐产物核undefined允许集、真实依赖／最低系统和实机，不把该选项作为任意未知符号豁免。受控core可先获取开发证据，未来addon／Electron另验，不以N1缺件阻它的源码工作。[部署变量](https://cmake.org/cmake/help/latest/variable/CMAKE_OSX_DEPLOYMENT_TARGET.html)、[架构变量](https://cmake.org/cmake/help/v3.31/variable/CMAKE_OSX_ARCHITECTURES.html)。

**Windows。**CMake MODULE本身不会安装Electron所需hook。方案保留匹配Electron的node.lib、直接进入.node的hook、delayimp、HOST_BINARY／DELAYLOAD、实际MSVC／SDK／x64／CRT和许可来源；当前缺物件即pending，不以Mac产物替Win11。实际本地hook／gypi与官方说明一致，使用全局Node通用importlib替Electron的反例已排除。NT内部API若使用，必须核实际user-mode声明／动态加载及缺失策略，而不是默认有ntdll.lib；ACL系统库须随真实backend列出。`/MD`及CMP0091显式选择不能替代DLL间内存所有权合同。[Electron Windows hook](https://www.electronjs.org/docs/latest/tutorial/using-native-node-modules#a-note-about-win_delay_load_hook)、[CMake CRT](https://cmake.org/cmake/help/v3.31/prop_tgt/MSVC_RUNTIME_LIBRARY.html)、[Microsoft内部API](https://learn.microsoft.com/en-us/windows/win32/devnotes/calling-internal-apis)。

**输入和许可。**本机头文件hash不是官方archive身份；node_version.h notice、npm许可和node-gyp MIT也不能互相替代Node全输入许可。方案保留根明确接受当前原件及适用来源、或另交合法离线输入的选择；未自动取源。SDK版本／单个compiler hash不当完整内容锁；首次获准构建的真实depfile／链接图须与已批准供应原件关联，缺失不倒填。还须固定CMake与相应许可、所选子窗口所有必要输入、Windows元件；其余输入只阻对应子窗口。

**命令和真实加载。**示例明确为未来driver CLI／参数化argv，当前不存在`build-native-location.mjs`，未填ABI／测试main和child契约时不会宣称CMakeLists可生成。Node require仅检实际加载／注册exports，不替OS操作／真实close；Vitest stub不替真实addon模式。Electron必须先有指定binary、fuse和明确headless窗口；runAsNode fuse禁用会忽略ELECTRON_RUN_AS_NODE，方案没有GUI回退。Node24成功亦不能记成Electron44.9成功。[Electron环境变量](https://www.electronjs.org/docs/latest/api/environment-variables#electron_run_as_node)。

## 意见与处置

| 项目 | 发现／复核 | 状态 |
| --- | --- | --- |
| R1／P3 | 首稿四条命令含三条build，文字“后两种”可能漏读core前置检查；建议改各build分支 | 最终修订已改“各--build分支”，精确diff核过，关闭 |
| 作者自查增强1 | addon显式BUILDING_NODE_EXTENSION／确认NAPI_VERSION，仅作用addon | 实际node_api.h5–10在Win用该宏选dllimport；NAPI_MODULE_EXPORT另管注册出口。补充准确，未扩大Node C++／libuv表面 |
| 作者自查增强2 | 复用进MODULE的core OBJECT／STATIC也显式PIC | 合理且未增加writer，已核对应三处修订之外无变化 |

以上是一次完整首稿独审及三处修订的定向复核，不是虚构两轮native测试。无剩余需改主稿的P1／P2；已准确暴露的供应／ABI缺口不是“实现已就绪”，也不构成拒绝全部N0源码的理由。

## 来源读取记录与保留门

本审实际联网成功读取Node24 Node-API；Electron native模块、fuses／环境变量；CMake MODULE、CXX_STANDARD、OSX_ARCHITECTURES／DEPLOYMENT_TARGET、MSVC_RUNTIME_LIBRARY／LINK_OPTIONS／PREFIX／SUFFIX；Microsoft CRT、内部API说明及GetSecurityInfo官方记录；Node／node-gyp官方LICENSE页面与CMake许可说明。CMake部分URL为v3.31／latest文档，只提供本文规则，不pin一个已安装版本；主稿选floor3.25不被改成我浏览页面的4.5-rc版本。未下载源码archive或headers。

审查者一次Microsoft三页并行open连接失败，后官方域搜索成功取得内部API／ACL库来源；未将首失败当成功。负责人CMake四页连接失败与后续检索成功由其独立状态文件保留；我的成功浏览不覆写其失败记录，也不据网页可达性给target Pass。官方许可背景不能补成本机未取得的Node LICENSE／供应授权。

后续仍需根精确授权三个writer、固定I06九原件及ABI／测试契约、对应离线工具／headers／许可和目标tuple，再分核心／Node addon／Electron／两目标OS实际窗口。完整N0功能与所有真实资源终态、生产LocationLease／首IO、SQLite／CPython／VFS／B-R／T01消费／父I06与57P0、指定同版双模型、CI／正常推送合并均未通过。本审不改Goal或给下一阶段自动授权。
