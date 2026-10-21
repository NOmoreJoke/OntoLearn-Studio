# 第二次 Darwin/core 构建归档

本次唯一第二次构建成功，状态仍为 `built-unverified`，所有产物冻结、测试 `NOT_RUN`。这不是 N0 通过、运行行为通过或生产证据。

固定输入 `b65751963a8c1f0c35e6ef680e816a99c4026e24`；授权 `228815f1f4f2bad005f21faffd8676c8713431c8`；元数据优化产品 `95f07d931eeffd3bdcd52cb21e9fa2d8a1db12bd`，完整保真过程基线 `5d7a143f2c100c5ca4ed6b36f7fa8fc2df611a34`。源仍是 `b1c54c3de840e657aba07906587681f6415085d6` 的已采用九文件；本次仅更新锁中两个批准引用，没有再次修改源、CMake 或 driver。

执行一次 `/usr/local/bin/node scripts/build-native-location.mjs --target darwin-arm64 --component core --build`，driver exit 0；最终 `driver-raw/supplier-log.0065.json` 的 13 条命令均为 status 0，firstFailure 为 null。配置日志明确完成 9,308 resource 与 33,464 SDK 实体 pin 核验。原始 66 版 supplier log 与 26 个命令流共 92 文件按字节归档；生成证据另存 17 文件。外部构建目录 144 文件、3,019,120B 的路径/大小/SHA 清单保留原输出位置，二进制与对象未放入 Git。首轮超时与归档 `7bfd7c493698107fc70913e249d164cdb6515205` 保持不动，不将优化推定为超时唯一成因，也不据两轮量化性能。

| 冻结产物 | bytes | SHA-256 |
| --- | ---: | --- |
| location_core_test | 343888 | ce1a3a365df426d4d57e8b5cade83b2b6e82e5cd438bcccc6e4c358af7ea203a |
| location_child_probe | 34120 | 3900ebc3f31a8def12d8f6bd4eedf866543d94e9412dd1d37706e68e0159c15e |

10 次实际 file/otool/nm 只读调用均 exit 0，静态前后产物 pin 不变。两者 Mach-O arm64，LC_BUILD_VERSION minos 15.0 / sdk 27.0，导入 libc++ 与 libSystem、loader 为 dyld、无 rpath；core 外部 `_nl_*` 符号 11 个。未执行产物，未验证目标系统兼容性、动态加载、Node addon ABI 或运行行为。

检查过程保留一次输出初始化失败：大小写不敏感文件系统将 otool-L 与 otool-l 标签认作同名，第三项在 exclusive stdout open 阶段失败，没有子进程；旧 attempted 字段是包装器意图。前两次成功调用没有重跑，其余八次改用独立语义文件名完成。原结果与更正记录均保留，不能把它写成所有过程操作均成功。

四个 depfile 共 1,798 token、877 个唯一词法路径，875 直接命中已批准 pin。pthread.h / sched.h 两个别名在原供方 fb40bde92cc35269c25c11a8628a71d5f750be4e 的全类型清单中，分别指向已批准常规目标 pthread/pthread.h（28093B，9d621c730d1d96b600893b0e3e4c45822a24d565e7b6b166973c41a6a2eb02e7）与 pthread/sched.h（1410B，07d65b8d135be978a33579b5a333bd4576a8c6b36351ef510e0cca2aa0987020）。原 symlink 身份、linkname/realpath、常规目标及 sidecar 位置见 `sdk-alias-catalog-bindings.json`。877 条均有既有清单来源；没有打开未知 header，也未重新核验物理 alias 或独立追踪编译器实际打开的目标。

四条 compile argv、两条显式 link-driver 命令、对象 pin 与 CMake 探针 implicit 信息已归档；探针不能代替最终 linker 选中记录。最终选中 stub/archive/member、嵌入第三方与运行时闭包仍 PENDING；本轮没有为此新增 -t/-map 或重构建。

总控已将原 core test 的 Darwin 普通 rename 可能覆盖已有目标的问题交 I06 修复；这是后续执行前的源夹具阻塞，本次成功构建结论不变。本轮不采用修复源、不第三次构建、不执行测试。任何新源、构建或运行需新的精确窗口。

读取账见 `read-account.json`：守住原 40GiB 构建阶段及 200,000 实体 / 1,100,000 元数据记录护栏；声明上界、预留和应用读缓冲均不是实际 OS / compiler / loader IO 测量。

Git 全量 whitespace 检查实际 exit 2；仅原始生成文件的 62 处空白诊断按精确 path/line 记入 `whitespace-check.json`，其余改动 filtered 检查 exit 0。未修剪任何原始生成证据，不能表述为全量空白检查通过。最终归档以 Git 索引逐文件 bytes/SHA 校验为准。
