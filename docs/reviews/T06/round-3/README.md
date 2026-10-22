# T06 S1 R3 静态派发准备

**READY，仅静态准备。** 两个全新独立环境、完整输入及共同历史已准备，独立预审11537B全文已由owner读取，结论为READY；没有创建模型任务、实际设置或受理证明，没有本轮产品验证或新的产品Pass。须总控完整预检和另发START后才进入应用。

产品固定 `3be0397faf03de6520c47bf7d86f3dc2fd004287`，base固定 `5f910b52c69d86a1076b2032e5d3c63e715947f3`；原两轮及补正共同历史固定至 `992f5b4a0369867e2898d85449a55dcbc6f684fa`。旧作者私有Pass、M4P3、流程Fail/未闭与全部UNKNOWN均保留，不再补原SID。

| 项目 | ZCode | MiniMax |
| --- | --- | --- |
| 工作树 | `.worktrees/T06-s1-zcode-r3-review-3be0397` | `.worktrees/T06-s1-minimax-r3-review-3be0397` |
| 主树完整输入 | `zcode-full-input-3be0397.md` | `minimax-full-input-3be0397.md` |
| 正文字节 | 47678 | 47701 |
| 正文SHA256 | `7fda538ae97fc7ea3eb04fd78ead0c3c995ec1aa9cc6a543199a6edec9bffa17` | `78a1ce7bfa3c4a099552098607a6f636952cb2e9804fe0135b30f179644d9f85` |
| 本方cover | `zcode-cover-3be0397.txt` | `minimax-cover-3be0397.txt` |
| 指定设置 | GLM-5.3/max/yolo | M3.1-Flash/xhigh/始终授权 |
| 实际SID/turn/设置/受理 | UNKNOWN | UNKNOWN |

每树自己的 `out/review-r3/input` 含正文、cover和9页连续UTF8正文（每页≤6000B），只在静态文件层面证明拼接相同，不冒充native实际读回。56份逐文件owned全文差分含13产品，另UI16/binary4仅metadata；这20项已sparse物理排除，不提供混合连续diff。176件共同历史与旧local1–6/R1原文件的路径映射已写清，原40K冻结输入仍精确保留为历史后缀。

两套新node_modules/.venv、cache、TMPDIR均独立，各一次npm ci与uv sync真实child0，8份完整分离日志SHA已核；这不等于各内部生命周期child都分别仪表化，更不是产品check。root准入12839/4759两原件已固定复制，未读其他private条目。旧prior-validation两包/混合patch只登记metadata，未放入新树；只提供选择出的安全文本及原日志。

主入口为`ready-handoff.json`。独立全文预审为`independent-preparation-review.md`，原结果与归档/收证计划短核分别为`independent-preparation-result.json`和`independent-archive-plan-receipt.json`。未来顺序与停止边界见`dispatch-and-collection-plan-20261023.md`：新START之前不GUI/消息/运行；必要命令若写准入三处之外先停，不用wrapper或历史check许可绕过；拒绝即停目的，保实际child、双流与首败，页缺证和旧压缩UNKNOWN不补造。

可恢复静态材料包位于`../evidence/s1-r3-static-review-materials-20261023.tar.gz`，7382068B／`ae09c3cfb3785b846aa67dd9182b7e6c8c10c0564a992ab0111e78ce24c65b75`，290 regular／289清单。两模型私有页与共同材料去重存放；归档只在owner树，不给任一模型复制包含对方新输入的整个包。独立审计包50853B／`7ca42c47f9f13f06cf9fd6f33928b62119281de457053948e1760edf5ae8d514`，7 regular／6清单。owner逐成员bytes/SHA均核真；独审对大包只核外hash/安全metadata，不能冒称其重哈全部body。

Q5/P2-2容量风险、原4P3、完整FR600–604与真实接线、G3、native两OS、package、人验、CI/远端门保留，UI970新指定仍0。保护AGENTS未stage，原blocked Goal不改；本准备无push/PR/CI/merge。
