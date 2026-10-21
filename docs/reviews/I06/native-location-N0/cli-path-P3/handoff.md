# N0 Windows probe CLI P3 修订交接

2026-10-22。本件只处理根新提的 Windows 测试 CLI P3；根的完整九源/过程控制审查仍待其最终报告与签收，不用本局部修订替其批准。构建/运行窗口未授，T03 WIP 未消费。

完整新源码固定为 `b1c54c3de840e657aba07906587681f6415085d6`，树和 branch 仍为 `.worktrees/I06-native-location-N0` / `feature/I06-native-location-N0`，批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。相对旧源码 `fa1a7e4155f3afee4a1b3409f9ab8804cc620186`，只有 `packages/native-location/tests/location_core_test.cc` 变化：29666B，SHA256 `7d0965cafe74fcbaa0d6c0fcf57078d2969fd3f243d7a14d1e7244329017bcdc`；其他八件完整源码逐字相同。九件新清单在本目录 source-static-check-r2.json。

原盘符判断会把 `C:probe.exe` 误归绝对路径；现在只接受字母 drive 根形式（含 CMake `C:/...`）或普通 `\\server\share\artifact`，拒绝相对/盘符相对/current-drive root、device/extended prefix、缺 UNC 组件、点段/ADS 等合同外拼写。输入 guard 位于 Win UTF8转换成功后、pipe/process 创建前。校验文本根形式不证明 artifact 存在、真实身份或来源，T03 仍必须提供同一构建目标 TARGET_FILE 的实际绝对路径。

首修订 `1b025562b1011155e07130175fdadc522185453e` 和 independent-review.md 原文保留：原盘符相对P3已修，但独审另保同级DOS basename P3。最终按官方列出的保留名称补充带扩展名/大小写/上标变体的有界过滤；UNC server/share明确采用相同保守组件政策，见followup-disposition.md。不是通用Windows解析器或实际对象认证。

同一测试文件最终共28条 constexpr static_assert（5正23负），明确包含旧 `C:probe.exe`、保留名及近似非保留名反例；没有另建 helper 路径、动态 fault callback 或公共 API。**本轮仅静态读取和文本/hash检查，没有编译/执行这些断言或任何测试，也未执行 native/FS/child 实验、产品 import 或 addon load。** 初审和新固定版定点复核分别见 independent-review.md / independent-followup-r2.md，其结论不扩大为目标运行结果。

独立复核原文6077B，SHA256 `7dd820a7f6d833b28c126d83e01fc0184e68b236eb1aad3fdded0c8368b082d2`，绑定完整新源码 `b1c54c3de840e657aba07906587681f6415085d6`：指定DOS basename P3在源码层关闭，diff未发现新确定问题。原盘符相对P3已由首修订独审确认修正；两份原文均保原字节，没有把纯断言源码当测试通过。

旧 `fa1`、`ff0b6ccb8541ef0dc6fef3865ca8ccde71809bca` 及全部首失败/审查原文保留，旧40件中除上述明确修订测试源外其他39件仍保持工作区原字节。旧顶层 manifest/main/handoff 不覆盖改写，继续绑定原 ref；**后续本修订采用本子目录新 manifest**，不能用旧 core_test hash 认证新源码。新源码 ref 后的提交仅本专属过程资料，最终 manifest会验证九件无漂移。

public ABI header 保持13296B/SHA256 `fc3f7983d62b0ef4f5a3a056198c00a0b971d2ae722acc33bc6f61937ec8e172`。Node binding 仍13163B/SHA256 `e10e59bdb200460310489bb4fc5b8c64ab79c1b8e2cfc9e7353a10a0c8667383`，实际调用的12项为：

```text
napi_add_env_cleanup_hook, napi_create_external, napi_create_object,
napi_create_string_utf8, napi_create_uint32, napi_define_properties,
napi_get_cb_info, napi_get_value_external, napi_get_value_string_utf16,
napi_get_value_string_utf8, napi_set_named_property, napi_typeof
```

最低 N-API3，与根固定官方头复核相容；不回退早期11项过程列表。原 T03 单registry/host image pin/固定SDK与Node-Electron工具链/链接导出/CTest绝对 TARGET_FILE 的请求仍依旧 final-source-handoff.md，没有本轮构建实证或实际采用。完整 TS 类型检查、原生编译与两目标OS运行/故障/晚返验证均未完成，N0技术尚未通过。保护 AGENTS 不stage，旧材料不重测，无 push/PR/merge/Goal变化或向其他聊天派任务。
