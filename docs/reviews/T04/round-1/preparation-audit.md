# T04-S1 round-1 准备材料独立审查记录

2026-10-22；独立 agent `/root/t04_private_review`。仅核对流程材料，不是 ZCode/MiniMax 实际任务，不是指定双审报告，也不恢复 blocked Goal。

## 首次实际结论：暂不通过

- P2：`review-inputs.md` 与 manifest 原引用后台路线 SHA `5fd7ef28089c6dde7efffaadaf1adca77c249f4e76670d8a9b53a28db7085433`，外部文件在准备期间变为 `9a2d722dc86c64d66929cadd12631cc85042bdd820aba9ec76de882fa3ed5de4`。不能将可变路径当作固定来源，需快照或读回同步；不能当作 T04 lease。
- P3：两提示和历史索引写 `inner-review`，实际历史原件路径为 `internal-review-1..8.md`，须修正并同步提示/索引 hash。
- 其余：33 产品 Git blob、8 支持 blob、当时 6 包文件、完整 170428 字节 diff 一致；内审历史处置索引、最终 TS666/Python1083、SSR14 的 `raw/reader-ssr-first.log` 来源正确；政策/指南和全部边界完整。

## 开发线处置

全文读回新版后台路线，保存 `background-route-snapshot.md` 原字节 5446B/SHA `9a2d722dc86c64d66929cadd12631cc85042bdd820aba9ec76de882fa3ed5de4`，manifest 独立固定 snapshotPath/大小/hash，明确外部源可继续更新、本包快照不是 lease。两份提示和索引路径全部修正为 `internal-review`，同步包文件 hash。产品/测试/配置/依赖/验收均未变，没有运行产品测试/构建/外部应用或模型。

## 第二次实际结论：准备材料通过

独立 agent 实际只读复核：P2/P3 均关闭，无新增问题；快照原字节和全部包 hash 匹配；33 项产品和 8 项支持证据未变；完整 S1、指定设置、双方新独立任务、真实终态读回、无桌面/只读/lease 等边界保持；政策尾部完整一致，没有两份指定报告占位。

最终提示 SHA-256：

- `zcode-glm53-input.md`：`2761fa389ce56d4d9fd875c082291fd074a85e70fe2a391046b6001f6dda13c3`。
- `minimax-m31flash-input.md`：`9873b3f6797d72937fd2da25c204b9aaf57f8c53ccdefc0e7b75b0097dd5ca9a`。

本记录只追加独立准备审查的真实发现和关闭，不替代实际指定审查。产品仍 554/base5f，准备前支持流程 e761；本包提交 SHA 与 manifest 自身 SHA 由提交后回执，避免自引用。后续独立 workspace 映射另附 hash，原 prompt 不改。
