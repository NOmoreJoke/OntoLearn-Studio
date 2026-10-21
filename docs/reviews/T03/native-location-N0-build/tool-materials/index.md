# T03 Native Location N0 官方工具材料来源索引

静态材料核验通过；运行状态为 **NOT_RUN**。本记录只覆盖免费官方材料下载、归档目录/文本读取和字节比对，不代表 CMake、CTest、编译、addon 或 macOS 27 运行通过。

- 受控材料目录：`/tmp/T03-native-location-N0-tool-inputs/run-20261021T154556Z-9de064fe`
- 完整来源与 HTTP 证据：[source-index.json](source-index.json)、[download-metadata.json](download-metadata.json)。每项含起始/完成 UTC、源 URL、实际最终重定向 URL、重定向链、HTTP 终态、响应头、实际大小与 SHA-256。
- 所有 7 项实际下载终态均为 HTTP 200。未更改代理、证书、PATH 或系统配置，未安装、解压安装树、执行归档程序或写产品文件。

## 选择依据

[官方 CMake 下载页](https://cmake.org/download/) 的稳定版栏目为 4.4.4，候选版 4.5.0-rc1 单列；[官方发布公告](https://discourse.cmake.org/t/cmake-4-4-4-available-for-download/15862) 日期为 2026-10-08。选择的是该稳定版的 macOS universal tar.gz，官网标注 macOS 12+，满足工程 CMake >=3.25 floor。包内 cmake/ctest 的静态 Mach-O 头含 arm64，版本 plist 为 4.4.4；这些是分发/字节证据，macOS27 实际执行兼容性仍未测试。

CMake 源包链接与校验清单链接均取自上述官方分发页的 Kitware/CMake release 资产。Node 只下载 [nodejs/node v24.15.0](https://github.com/nodejs/node/tree/v24.15.0) 固定 tag 的 LICENSE 与指定四个 src 头文件，没有下载完整 Node/source/runtime/Electron。

## 材料字节清单

| 文件（完整原始字节只留在受控 tmp） | bytes | SHA-256 |
| --- | ---: | --- |
| cmake-4.4.4-SHA-256.txt | 2015 | `560231a0064d3f39c078d6b242dab4a93a8ed17a80e997a56851f338a91e9d65` |
| cmake-4.4.4-macos-universal.tar.gz | 89454352 | `4b7b73704b1db9b374e5c9ab8e17ac6148b817b6396ee75cd94a852cbac9d305` |
| node-v24.15.0-LICENSE | 156926 | `4573185d56580da2b890ba34a85a409257640f1c5632eade4300137266194d18` |
| node-v24.15.0-node_api.h | 10370 | `2d4560831e525b47b060ec8a0864ab73993df9e20215ce9f0fe7b24cd31af32a` |
| node-v24.15.0-node_api_types.h | 1930 | `a25356630d3058f0a0c8937d9f297e9471e037fda58c2696d8a505c2bd99cb00` |
| node-v24.15.0-js_native_api.h | 32609 | `eb03b6c850a1cfb593fd03e9e4251db8c82e9a6d9705bca91ac8d1a01fd7037c` |
| node-v24.15.0-js_native_api_types.h | 7660 | `7dd3663630849ada3a30d39abf42a192c9b6e7de63017cd32c41f5371a475b34` |

## 静态核验结果

[static-audit.json](static-audit.json) 与 [完整归档成员清单](cmake-archive-members.json) 记录 9,041 个成员、声明总尺寸 252,707,197 bytes：8,839 regular、189 directory、13 symlink。无绝对/越界路径、规范化重名或异常成员类型；13 个链接逐段解析至归档内部现存目标，未解压至文件系统。包内 cmake/ctest 两个成员的尺寸、SHA 和 arm64 CPU slice 已记录。

同一分发包的 `CMake.app/Contents/share/cmake-4.4` 为静态 CMAKE_ROOT，Modules 含 1,686 个常规文件；`Modules/CMake.cmake`、C++ compiler/system/Darwin 等必要资源存在。版本 plist、主 BSD 3-Clause `Contents/doc/cmake/LICENSE.rst`（1498 bytes）及附带许可等 10 份文本的原始字节保存在 `/tmp/T03-native-location-N0-tool-inputs/run-20261021T154556Z-9de064fe/cmake-static-texts`，索引含各成员路径、大小、SHA。

Node LICENSE 为 156,926 bytes，四头合计 52,569 bytes；分别小于 2 MiB 与 4 MiB 边界。四份头与 `/usr/local/include/node/` 对应文件原字节完全一致；没有用 npm/node-gyp LICENSE 替代 Node LICENSE。

## 首失败与边界

web 工具首次抓取两个 GitHub release 资产报告 restricted URL，未提供 HTTP 终态；该结果保存在 run-config。随后实际受控下载成功，不抹去前述工具失败。第一轮静态审查只做直接目标名查找，误报 framework `Versions/Current` 间接链接不存在；[首轮记录](static-audit-attempt-1.json) 与原脚本保留，v2 通过最多 64 跳的归档内逐段解析消除该误报。没有失败下载 partial；正常传输 partial 在完整 EOF/长度核验后改名为完整文件。

仅静态与 SHA-256 一致性通过；未验证 PGP 签名，未运行任何新工具。未取得目标 OS、编译、CTest、native、权限、设备、I/O 或性能 Pass。二进制不进入产品树或提交，tmp 保留依赖系统临时目录生命周期。

证据文件的大小/SHA 索引见 [evidence-sha256.json](evidence-sha256.json)；下载器与静态审查脚本一并保留供独立复核。
