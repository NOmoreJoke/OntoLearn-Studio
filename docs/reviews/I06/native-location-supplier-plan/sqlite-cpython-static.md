# SQLite / CPython 官方来源静态补充

2026-10-21。仅官方只读网页/固定源码定位及文本分析；未下载源码包、import sqlite3、探测运行库、编译、执行 SQL、运行产品或原生实验。这里记录读到的事实与据此提出的路线，不把网页source ID当本地/包内库身份。

## 来源与准确结论

| 官方来源（实际只读访问）                                                                                                                       | 读取定位与可支持的事实                                                                                                                                                                                                     | 不支持的推断                                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| [CPython v3.12.12 Modules/_sqlite/connection.c](https://github.com/python/cpython/blob/v3.12.12/Modules/_sqlite/connection.c)                  | 定位初始化 `sqlite3_open_v2` 和 `connection_close`：open flags为READWRITE/CREATE及可选URI，VFS参数NULL；close调用close_v2。GitHub呈现带行号源码，非本轮下载/哈希归档的完整原始文件                                         | 未取得本地Python `_sqlite3` 与该源码对应关系，不读其私有内存结构；版本声明不认证同image  |
| [SQLite VFS说明](https://sqlite.org/vfs.html)                                                                                                  | VFS可显式选名/URI选择，未选时有默认实现；不同连接/ATTACH可有不同选择                                                                                                                                                       | 另一个SQLite库注册同名VFS不证明Python实际实例可用；同名不认证能力                        |
| [SQLite VFS object](https://sqlite.org/c3ref/vfs.html)                                                                                         | xOpen/xDelete/xAccess/xFullPathname、类型flags及临时名存在；只拦主文件不完整                                                                                                                                               | 未证明当前T01已请求过所有角色或存在安全filename解析                                      |
| [SQLite io_methods](https://sqlite.org/c3ref/io_methods.html)                                                                                  | 文件层包括read/write/truncate/sync/lock/file-control、SHM、可选fetch；failed-open也可能需close                                                                                                                             | SHM内部open未必独立经过VFS xOpen；必须审真实所选OS后端                                   |
| [SQLite close](https://sqlite.org/c3ref/close.html)                                                                                            | close与close_v2对未结束statement/BLOB/backup处理不同；后者可留zombie                                                                                                                                                       | Python close返回、native Promise完成不证明真实资源已销毁                                 |
| [SQLite3.51.3发布记录](https://sqlite.org/releaselog/3_51_3.html)                                                                              | 2026-03-13补丁含WAL-reset修复；官方sourceID `2026-03-13 10:38:09 737ae4a34738ffa0c3ff7f9bb18df914dd1cad163f28fd6b6e114a344fe6d618`；sqlite3.c的SHA3-256 `32d5424f97e0a7fc5ed2f6335afbb58be4e0298bd7117a34e39d345ff13d859e` | 非最新/完整安全评估，也非源码包SHA256或项目已采用版本；T03还须固定实际来源/补丁/编译选项 |
| [SQLite版权](https://sqlite.org/copyright.html)                                                                                                | SQLite交付代码public-domain；构建脚本可能另有许可                                                                                                                                                                          | 不能将所有构建工具/SDK/CPython都写为public-domain                                        |
| [Python3.12许可](https://docs.python.org/3.12/license.html)                                                                                    | 受控分发/修改仍保适用许可和第三方notice                                                                                                                                                                                    | 不取代实际打包依赖的逐项许可清单                                                         |
| [Node24 Node-API](https://nodejs.org/download/release/v24.0.0/docs/api/n-api.html#implications-of-abi-stability)                               | Node-API ABI保证只适用其自身边界；不用V8私有ABI；实际Electron支持版本另核                                                                                                                                                  | 不涵盖SQLite/CPython/C++runtime，也不证明Electron44.9.0内嵌Node版本                      |
| [Apple acl_get_fd_np](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/acl_get_fd_np.3.html) | 可从已持有FD取指定类型ACL，结果需acl_free；这是对象ACL快照                                                                                                                                                                 | 快照不参与OS后续访问控制，也不防并发ACL变更；归档文档不是macOS15 SDK/runtime实测         |

上表为小范围事实摘述，没有复制整篇源码/文档。现行网页读取日2026-10-21；CPython/SQLite固定tag是分析锚点，动态网页可能更新，未伪造其内容SHA。

## 精确路线差异的处置建议

平台报告优先“自有CPython连接适配”，能避免依赖stdlib链接，但须完整实现T01实际DB-API面。主方案优先“受控重建 `_sqlite3` 与注册扩展同一SQLite共享image”，保现有Store事务/Row/exception/backup兼容，增加T03受控Python构建负担。两者不是同时采用，也不以一个路线的通过证明另一个。

主方案所选仍需要：T03实际原始源及SHA256、稳定私有install-name/DLL名和依赖图；显式cap VFS、内部opaque URI/模式；无系统库/默认VFS fallback；真实Store连接的trace及实际注册/查找函数来自同一loaded image；OS后端所有相关open/SHM/lock/file-control围栏。只比sourceID字符串或给Node链接另一lib不足。没有实件则选择仍是方案，不可接入现有uvPython声称完成。

已尝试 SQLite Fossil 的固定version-3.51.3 os_unix.c/os_win.c页、官方GitHub镜像与Raw入口。Fossil/Raw读取失败，GitHub页面只得到部分展示且函数定位未匹配；**未获得完整两文件原文，不声明已审完整后端或已找齐每次syscall**。本轮不为补齐读取去下载包。精确可审核补丁和锁/SHM同版复用仍是N1/T03取回固定源后的硬输入，不能从接口文档推导stock xOpen能adopt任意fd/HANDLE。Apple xnu固定tag的sys/acl.h尝试404，未依赖该文件；ACL依据为上述Apple官方归档手册。

## 当前结论

C++17/Node-API控制面和同库注册可作为明确源码设计路线；跨进程持续围栏、SQLite物理对象backend、真实释放与安装耐久仍须实际供应和目标证据。本报告不认可Node双检查、路径重开、同UUID/同hash、close_v2返回或B-M通过作为替代。无本地运行验证。
