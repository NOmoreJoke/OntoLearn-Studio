# I05 私有 strict restore 本地技术交接

实现源码固定 `3ef2f6952ed1a4f852da31c0bef7e8d8679752a5`，基线 `5f910b52c69d86a1076b2032e5d3c63e715947f3`；分支 `feature/I05-profile-restore`，树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-profile-restore`。最终本地交付 HEAD 在该源码候选之后仅增加本线说明与证据，完整路径/字节/SHA见 final-full-diff-manifest.json（manifest自身以该最终Git commit绑定，明确不造自引用SHA）。

| 新文件                                  |  字节 | SHA-256                                                          |
| --------------------------------------- | ----: | ---------------------------------------------------------------- |
| semantic_profile_restore.py             | 50276 | aa3d51c1ccc487ce21a78560ad6cdf7a6485cc86f746c29ee329e6a0bc4c4d09 |
| semantic_profile_restore_budget.py      | 37478 | 593b2a832dd510063bb60d7b3d5526fbd6cf4dcba53ad9c513e82dbfdd77ef7f |
| test_semantic_profile_restore.py        | 33681 | d3726f6170d126f7a6b495f53b951093faf0b3caa935b3d87a06c18c25619aac |
| test_semantic_profile_restore_limits.py | 21089 | 4eed5e316f0033080b3f2761b83ddcd53f093f18a6e2aa48706619d109872a8c |

68只读继承输入逐字保留，采用收据 adoption-receipt.json 已由控制根先前核过，未覆盖。AGENTS 15852B/SHA78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759 保持 dirty 未stage，不计入交付delta。

实际验证：最终 npm run check exit0/未超时、630 Vitest + 2873 pytest（145 restore），全部静态检查/build通过；verify:sources exit0核12源。runs08/09含完整源前后绑定、真实进程与原输出。最终23exec/25slots/93原件归档ZIP 326113B/SHA354133c1237ed2ea33fc6aa2ef42b7155628f5dd4a937853b9d8e8ba6600c807；逐流/成员hash及完整native签名、原calls/L/parseusage对独立94核同。N100原生产失败保留，不列成功。首134/5、旧139/142和两次实际P2反例均保留版本身份。

独审终报：schema-review/delta3ef-report.md 有限通过，S1/S2关闭；budget-review/delta-3ef2f69-review.md 静态预算/持有通过，首BR三条关闭。本范围无未关闭源码意见。预算独审未代跑引擎；schema独审做独立AST分支并读回根实际运行，均没有冒充指定模型或CI。

这是根总控可据固定ref继续验收的私有技术交付。返回只声明 supplied-batch consistency；不重新授权selected、producer、Store、worker、长期保存、聚合重算、T03包接入或上线。目标平台、指定GLM/MiniMax双方新审、CI和合并门继续；未push/PR/merge/GUI/Electron/e2e/native/HMR/CUA/Keychain/模型/付费，未重建或改变原Goal。
