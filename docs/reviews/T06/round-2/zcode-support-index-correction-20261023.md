# Z 支持索引更正附录（准备件，待总控完整预检后定稿）

原 `reviewed-evidence-index.json` 的第一项引用已过时：仍把可变路径 `outputs/20261023_t06_s1_r2/zcode/minimal-manifest.json` 标为 **2242B／`141303912410c326b256311d93c8007f2d96c220f02aa41e186792563cef5f57`**。当前该路径实际为 **3063B／`033c1c1a33f15bad11237a093f665ec3bd4f7757a184f8533684122b89a1e831`**；parent 已实际读回，且与既封主包内 `minimal-manifest.json` 安全成员逐字相同。这是支持清单精度问题，不是产品错误。

原索引、独立流程审查、原报告及主包全部保留原字节，不把旧引用改写成当时已经指向新版本。新建快照和 v2 索引，精确路径及 SHA 见同名 JSON：

- 当前 manifest 的不可覆盖快照：本方审查树 `out/environment-prep/process-correction-20261023/zcode-minimal-manifest-snapshot-20261023.json`，3063B／`033c1c1a…`；主树 round-2 有相同文件副本。
- 新索引 `out/environment-prep/process-correction-20261023/zcode-reviewed-evidence-index-v2-20261023.json` 仅第一项改指上述固定快照及其真实 bytes／SHA，其余13项保持原引用；14项已逐件实际核 bytes／SHA。主树 round-2 有相同 v2 副本。

原 `reviewed-evidence-index.json` 继续作为旧审核时点索引；后续定位当前支持文件时应同时阅读本附录并使用新 v2，不再将旧2242B身份应用于当前3063B文件。不能因当前支持更正追认原作者已经完整读取缺失的 owned diff／metadata，原流程缺口保持。

两份完整补正 body、唯一原冻结后缀及所有已封包均未改动；未复测、重封、重开准备、发模型消息或操作桌面。原两 turn 的正式终态与作者私有范围 Pass 保持，双审流程门未关闭。当前只准备独立更正，待总控完整报告后一起定稿和内部 START。
