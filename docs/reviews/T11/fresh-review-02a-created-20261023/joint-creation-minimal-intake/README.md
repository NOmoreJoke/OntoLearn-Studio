# T11 两侧实际 fresh 创建最小单入口

两侧均已实际创建并各正式发送一次、受理、官方 Copy SID 在本方空草稿读回后清空，GUI 已 RELEASE。MiniMax 原 turn 后续 failed 不改变其已经实际创建的事实。本入口供创建首收，不计指定双审通过 Pair。

| 角色 | 官方 SID | 原始 turn | UI 模型／等级／权限 | cwd |
| --- | --- | --- | --- | --- |
| ZCode | session_65a1c0dbec5e79bbb778b444f370d4b5 | turn_b24126aa-bbc1-4e41-9801-9776cde0629b | GLM-5.3／最高／完全访问 | T11-zcode-review-02a4738a |
| MiniMax | mvs_b82c66fcac2a4adbbac0528a35505d1f | 3b445c40-e6bd-42a5-bf39-1cc32b82166b | M3.1-Flash／xhigh／始终授权 | T11-minimax-review-02a4738a |

完整绝对工作根和实际02a HEAD见 `minimal-creation-proof.json` 及两份创建收据。Z 原请求标量为GLM-5.3/max；M后台设置标量UNKNOWN，UI现场事实单独保留。

Z实际附件：35540B／dc5dcc5d…，原始精确文件块与连续1–227编号行完整保留；第227行为实际空行，连接实际行体后不另加LF。M实际模型可见两个公开Read返回：1–130及131–226；去编号时保留实际返回的每行终止符，直接连接为35607B／8f942109…。未用首返回 `details.textFile.content` 中的全文替代模型可见分片。

两侧分别与f94固定角色全文逐字节比较，差异均0；prepared和actual末字节均为LF（10），没有末尾换行差。实际cover由各自精确short-request文件保留，包含当前START生效说明；冻结正文中的仅准备字样仍作为历史快照保留。

已有非作者只读审查见复制的 `independent-creation-review.json`：核原10payload及M可见分片重建，明确不重新认证Z原始native编号源。本入口补入该精确原块及两侧直接换行重建，另做本入口非作者只读核对。

三件事分开：两侧完整输入正文可核；107产品及证据文件实际全文审完尚未建立（Z仍在原turn，M failed且无最终报告）；无指定双审Pass、无19项最终处置或发布授权。不得用107项hash通过替代阅读全文证明。

亲跑事实也分开：显式flag专项两侧125/125；Z默认121通过+4 skipped；Z tsc列表仅真实verify.mts、无旧verify.ts。M原npmcheck首败子命令exit1，Z首败exit2，后续分项不能替代原检查通过；部分环境继承UNKNOWN。固定元数据、ignore及输入未修改。本入口不复读累计工具安全包，不含global/headers/system/hidden上下文；Z仅继续原turn窄收终态，不续发或重建。
