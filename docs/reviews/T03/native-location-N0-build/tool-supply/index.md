# T03 N0 固定工具提取与宿主供应清单

**完整CMake提取核同与13条获准版本/元信息探针成功。SDK/编译器资源逐文件清单完整；整体供应仍未闭合。** 系统runtime cache对象受8GiB累计读取guard阻止，独立组件条款仍有明确缺口。全部审批维持false；未改toolchain-lock或任何产品源码。

受控run：`/tmp/T03-native-location-N0-tool-supply/run-20261021T163000Z-75ffc442`。原下载目录保持只读。完整候选值：[candidate-pins.json](candidate-pins.json)；完整原argv/cwd/精确传入环境/预执行真实path和SHA/双流/exit/signal/timeout：[probe-index.json](probe-index.json)及probes目录。每条timeout30s，13条各仅运行一次，均exit0、无timeout/signal。探针环境为明确列出的继承元信息环境子集，PATH沿用原值，没有更改PATH或系统配置。

## CMake原件与提取

原官方归档89,454,352B/SHA `4b7b73704b1db9b374e5c9ab8e17ac6148b817b6396ee75cd94a852cbac9d305`、原source-index及官方完整checksum唯一basename已重核。按目录、普通文件、已核链接顺序提取；未用extractall。9,041原成员（8,839 regular、189 directory、13 symlink）与实物path/type/mode/link/realpath/bytes/SHA全部一致，声明文件总尺寸252,707,197B。另记录归档未显列的1个必要外层容器，实际共9,042对象；合法0B `Modules/IntelVSImplicitPath/hello.f`保留。原结构/完整CMAKE_ROOT/CTest/许可和dylib都保留。

首轮安全脚本在提取第一个目录前因归档缺省外层容器停止，未写普通文件或运行探针；[首失败](first-failure.json)、原脚本与空目的地保留。第二个全新目的地显式声明隐式容器后完成，未复用失败目录。完整记录：[cmake-extraction-report.json](cmake-extraction-report.json)。仅核同后，固定CMake与CTest各一次`--version`实际均4.4.4；两binary大小/SHA也核同授权固定值。

## 供应清单覆盖与边界

完整声明与范围：[supply-declaration-final.json](supply-declaration-final.json)；清单分片：[inventory-parts.json](inventory-parts.json)，共53,092宿主/精确工具记录，含目录/符号链接/realpath及所有已读取常规文件完整SHA。与CMake及隐式容器合计62,134项，未触200,000项guard。分片没有截断；每片有数量、bytes、SHA。

- SDK整个canonical树52,590项，常规文件931,393,813B；所有headers、modules、framework stubs、SDK库和settings都在树中，逐文件已hash。xcrun观察到的MacOSX27.0.sdk是指向MacOSX.sdk的链接，别名身份也记录。
- compiler resource/runtime整个`usr/lib/clang/21`树380项、80,801,250B；toolchain完整`usr/include`与其指向SDK的C++头链接、固定clang/clang++/ld、make/git、Apple wrapper实际对象及静态Mach-O解析到的落盘dylib都列入并hash。所有被列链接的realpath均在已声明合法供应roots内，无悬空例外。
- 当前实际版本为Xcode27.1/27A9275、SDK27.0、AppleClang21.0.0、GNU Make3.81、Apple Git2.54.0。只证明获准元信息，不代表macOS15或宿主构建行为。
- 外部系统依赖按静态Mach-O load commands逐边列出：[runtime-load-edges-final.json](runtime-load-edges-final.json)。21个系统install names在具体安装的dyld cache.map里逐名命中：[runtime-cache-map-evidence.json](runtime-cache-map-evidence.json)。map仅为身份/地址文本依据，不代替cache实物hash或其内部传递依赖清单。

## 尚未闭合的精确缺口

[unhashed-system-cache-objects.json](unhashed-system-cache-objects.json)完整列出 **81个** 未读cache对象，共 **7,046,515,706B**。其余当前供应常规文件SHA均完整（含map）。已计供应读取 **2,699,211,379B**，8GiB guard剩 **5,890,723,213B**；仅再hash该全部候选cache集就至少还需 **1,155,792,493B** guard增量，尚不含后续cache嵌入image依赖解释的额外读取。因此本窗未读取这些cache实物，未把部分cache清单冒称完整runtime闭包。未自动扩大guard、重新下载或重算旧对象求绿。

已保存本机适用Xcode and Apple SDKs Agreement原始RTF及LicenseInfo（EA2002/GM）、CMake原始BSD许可位置，见[terms-index.json](terms-index.json)。独立GNU Make/Git等组件完整copying notices和系统cache各image适用条款未在本次有界本机文档查找中独立收齐；保留为条款缺口。没有替用户接受许可，也不把安装/版本探针解释为法律采用批准。

未运行configure/try_compile/编译器输入/link/CTest测试/native/child/FS/addon/Electron/GUI/网络；未改全局安装、代理、证书或安全政策；未commit/push/PR/merge或改Goal。只有版本/元信息探针获得运行实证，完整供应采用及后续构建仍等待根审查与授权。

[evidence-manifest.json](evidence-manifest.json)给出本目录全部证据（自身除外）的路径/大小/SHA；工具二进制仍仅在tmp，SDK未复制。
