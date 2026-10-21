# Windows probe CLI P3：原意见与作者处置

2026-10-22。根控制聊天 `01a154de-843b-7a00-8a80-51ba1c0aebce` 在独立静态读取固定九源 `fa1a7e4155f3afee4a1b3409f9ab8804cc620186` 后提出：原 `location_core_test.cc:241–242` 的 drive 分支只检查第二字符为冒号，`C:probe.exe` 盘符相对路径也会通过，并可由 CreateProcessW 按盘符当前目录解析。实际 T03 TARGET_FILE 应提供绝对路径，所以根将其定为测试 CLI 精度 P3，不作 mac/core 源码阻断，不称已运行漏洞；根的完整交付审查报告仍在形成，尚未签完整交付。

根建议在已授原测试 writer 内最小修为严格有根 drive / 明确合法 UNC，拒绝不属合同的 device / 模糊拼写，补同文件纯输入负例，不新增 helper 路径、不做 native 实验，保 fa1/ff0 原件后独立复审新固定版本。根另确认实际 Node binding 是12 API（包括 get_value_string_utf16），固定官方头的最高最低相容要求为3；不得退回早期11项交接。

作者采用修复，不延期。只修改既有授权的 `packages/native-location/tests/location_core_test.cc`：

- 同文件加入 constexpr 纯文本校验，接受 ASCII 字母 drive + 冒号 + 根分隔符 + 非空 artifact；允许 CMake 的 `C:/...` 拼写。普通 UNC 必须为 `\\server\share\artifact` 且至少三个非空组件。
- 拒 drive-relative、current-drive root-relative、非字母 drive、普通 relative、无 artifact/空 share 的 UNC、device/extended namespace、点段/尾点空格、控制符、ADS 和通配等模糊拼写。UNC 仅收普通反斜杠形式。校验只限定 CLI 文本，不证明文件存在、实际身份、权限或 T03 artifact 来源；不是通用 Windows 路径解析器或 namespace 围栏。
- 同文件15条 static_assert：3正向、12负向。其中 `C:probe.exe`、device/extended UNC、缺 share/artifact 等保为明确输入反例。断言只随未来获批 C++ 构建求值，**本轮没有编译/执行这些断言或任何测试**。
- UTF8→UTF16 成功后，新的 guard 在创建 pipe / process 之前执行；不改 child/native owner、sole-reaper、清理、C ABI、Node12 API 或预算。

旧完整交付 `ff0b6ccb8541ef0dc6fef3865ca8ccde71809bca` 与源码 `fa1a7e4155f3afee4a1b3409f9ab8804cc620186` 原样保存在 Git。旧40件中除本次明确修订的测试源外，其他39件仍保持工作区原字节；旧清单/交接/独审均不覆盖改写。本子目录的新清单绑定新候选，旧 manifest 继续只绑定其旧 ref，不能用旧测试 hash 认证本次修订。

仅允许 Git/hash/stdlib文本检查和独立静态审查；不运行 `npm run check`、native compile（含 syntax-only）、任何测试或产品 import、addon/FS/child实验，不安装工具/依赖、不消费 T03 WIP、不 push/PR/merge、不改 Goal。后续 T03固定构建与根精确运行窗口、完整九源控制审查仍保原门禁。
