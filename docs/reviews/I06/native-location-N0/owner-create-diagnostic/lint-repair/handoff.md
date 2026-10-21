# I06 诊断候选 lint 增量交接

产品候选：`fc6237e8cad1a4043d46a1c7198439f1da06ad67`，父提交：`2de79e886bb9fb3aa97cb66efc1d04a86961c552`。本目录为新增过程资料，旧诊断窗口、报告、原始日志和清单未改写。

本次仅修改 `tests/unit/i06-native-location-owner.test.ts` 中 reentrant revocation 测试：删除提前的 `let current` 声明，将原赋值改为 `const current = owner(data.binding)`。mock 安装、owner 创建位置、调用顺序和断言均保持。两处声明差异见 `single-test.patch`；逐源静态核对见 `source-static-check.json`；独立审查见 `independent-delta-review.md`。

供方精确指纹：

- C++：`packages/native-location/tests/location_core_test.cc`，30037 B，SHA-256 `4cec7d67ba66fdf47d0ae26ba056372dc437e67ac076e768a548c334bd260319`；与上一诊断候选字节相同，本次未重复语义审查。
- TS：`tests/unit/i06-native-location-owner.test.ts`，8424 B，SHA-256 `4552db106b86a8a8a80b9fcb7b55292a1696f69b72a20bd97bdfaae2bdc104ce`。
- 新固定九源指纹完整列于 `provider-handoff.json`。相对本次父提交仅 TS 变化；相对旧 T03 实际构建的 b592 源，C++ 诊断与 TS 两项变化，其余七项相同。

本候选只运行一次完整 `npm run check`，实际退出码 0：lint、格式、类型检查通过，TS 16 文件 / 637 测试通过、1 项 native addon 测试跳过；Electron Vite 编译通过；Ruff 通过（205 文件格式匹配），Python 1052 测试通过。`npm run verify:sources` 退出码 0，核对 12 个归档源。实际双流与退出记录保留在本目录，摘要见 `checks-summary.json`。

旧完整 check 的 exit 1 原件仍保留，不能把旧结果改记为通过。`preservation-check.json` 已核旧过程清单 40 项及清单自身字节保持，并保留未提交 AGENTS.md。

本次无 C++ 原生构建、native 执行或应用启动。此前唯一原生执行的 `owner-create` 失败根因仍未知；尚未观察新增 C++ 诊断输出。现有 T03 二进制不包含新诊断，不得视为此候选的构建或验证。由总控按新九源指纹另行给 T03 必要采用/构建授权；本交接不生成新输入 digest、不授权构建或原生重跑。

本目录 `manifest.json` 为有限清单，自身排除；过程提交号由提交后的最终回复给出，避免自引用改写。
