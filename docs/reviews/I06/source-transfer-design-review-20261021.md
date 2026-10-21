# I06 来源传输与 T10 转移设计：独立审查收口

2026-10-21。本轮仅设计与静态复核，原 Goal 未完成；没有采用未批准实现、注册公共方法、创建 guard/测试或启动产品、容器、GUI。

| 最终文件（相对仓库根）                                      | SHA-256                                                          |
| ----------------------------------------------------------- | ---------------------------------------------------------------- |
| docs/iterations/I06/source-snapshot-transport-decision.md   | 2aeb824987978a83da3e94173c349e816772ffb85700a838d13232ac60239eb8 |
| docs/iterations/I06/source-selection-lifecycle-interface.md | 2495c4b371b6bf02519b62d1e3465422795703b4aaa110d2ac3f1dff52264a16 |
| docs/iterations/I06/T10-trusted-transfer-response.md        | db29f3a37e281bb83232dd2a18eda0eadfa670ba65b56f25e643b68800ce6b2c |

独立 agent /root/i06_design_review 核对固定输入和边界，最后定点复核以上来源两文件实际 SHA，确认无新增阻断。源生命周期子线提交 41cd0d68a22e4625fce9e0581941332229b7f3a6、T10 回应 d0dfe8a91fc2308b7e5f41fc6d71baff685fb845 已正常 merge，未覆盖产品路径。初稿意见及最终处置：

- 全局 pending begin 不可漏计：main 在任何 await 前预留；server 原子登记 pending/配额；稳定 attempt + 同 descriptor 幂等；丢 ack 仅按原 attempt 对账，not-found 不证明不会迟到。release 的 attempt/upload/snapshot 严格互斥；未有 uploadId 时按原 attempt 建取消 tombstone，取消处理中与实际清理终态分开，清理前不释放配额。已关闭。
- 旧未接纳 upload/inspection/preview lease 不得跨 session 复活，不能靠同 SHA 或旧字符串重新授权；新会话重建完整绑定。已接纳的持久输入只按原 Job/operation 与 pin 恢复，普通瞬断不自动重置模型 grant。生命周期最终稿已关闭。
- T10 回应保留完整 inode inventory、跨根锁/失效与退役、原子平台能力、唯一 writer receipt 等实际缺口。未把路径复验写成原子隔离，也未把现有 PrivateOperations 当全根互斥。新项目只在成功可信 receipt 与最后代次核验后选择；失败或状态不明不切换、不重放。无新增阻断。

待总控精确登记的新实现位置为 apps/desktop/src/main/security/private-root-transfer-guard.ts；测试候选 tests/unit/i06-transfer-location-guard.test.ts、隔离证据候选 tests/i06-transfer-platform/。来源宿主及三个拟新增测试的完整路径见生命周期提案第6/7节。这些均不是已授权或已实现文件。metadata owner/完整性/锁协议须先冻结；若平台不能提供所需能力，真实 I/O 保持拒绝，只验收明确可证明的核心。

静态检查：三份设计及本记录、status 的 Prettier 检查和 git diff --check；产品 apps/packages/scripts/.github、原 tests/e2e、tests/unit 与 package/uv 锁相对 e2c269ad78a78e1a042cadc93b1c81a874707153 无 diff。受保护 AGENTS 保持 SHA 78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759，未暂存。状态编辑首次 Python stdin 因中文编码报错且未改文件，随后以 UTF-8 Node 写入成功；不计作产品测试失败或运行证据。

本轮没有重跑旧998TS/1052Python、旧平台矩阵或工件全量审计。T01 canonical/最终写帧 fence/持久 pin、T03 实际 parser 与 XLSX 枚举、正式 Job/Store、T10 真实 export/import 及源码/新包 X1–X6 联验仍待；不以本静态复核代替指定双方完整新审、PR、实际 CI 或远端合并门。
