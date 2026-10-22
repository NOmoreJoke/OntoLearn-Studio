# R3 实际创建与完整输入取证独审

2026-10-23；独立 agent `/root/t04_private_review`。**创建/完整输入过程包核验通过，无新发现。** 本结论不是产品审查、模型报告收件或正式双审通过。

## 原件与身份

- `creation-index.json`对应23成员归档36881B/SHA `8dd366a8f5cb38a527e36c933a21d918377ddd4e913b0d33a732b03360b77143`；归档成员集合、每成员bytes/SHA及本目录settings/proof副本均一致。
- Z：`session_56788899c99e13a8d348bb21b2d62289` / 原turn `turn_dee9efbf-58dc-473e-8f12-b9be14ed1a72`；本人提交前后UI客观显示GLM-5.3、最高、完全访问；官方附件与本人SID在未发送composer读回、清空证据对应。
- M：`mvs_4e9f4b2b7bdd47348293cdbb41f60109` / 原turn `659fd77a-9a0b-49c5-b39f-48aeb928d9f1`；本人提交前后UI客观显示M3.1-Flash、xhigh、始终授权；官方附件与本人SID读回、清空证据对应。
- 两方operator/settings.json与acceptance.json均与归档原件逐字一致；来源为owner新写的本方UI回执，不是reviewer或默认配置自证。早期原turn/完整native proof为UNKNOWN的历史字段保留，由后续独立proof补足，不改写早期所知状态。
- 两棵实际owncwd均detached `5070004ec8e3219bea33960bd88f57f1976e9cf8`，42项受控文件仍等固定507 Git blob及manifest；指南15147B/SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`保持。owner准备ref `09a85f86f6d32d774e4dff6cdd2c10686963cb58`内两正文与当前输入逐字一致。

## 完整输入及原生范围

| 本方 | 原生编号与LF口径                                                                                                  | 重建字节 | 固定SHA-256                                                        |
| ---- | ----------------------------------------------------------------------------------------------------------------- | -------: | ------------------------------------------------------------------ |
| Z    | 严格本人SID/原turn首request，仅已知输入TAB编号块1–148连续；148为末尾空行，含LF                                    |    29675 | `45828e0984d527d2a105dca0b6cd6bc5823713e96f0b802ade914d603bc5bf1c` |
| M    | 严格本人原turn的两次Read 1–98、99–147，无缺行/重复；尾LF按proof从实际Read参数指定asset另核，不冒充第148个模型读行 |    29715 | `1985d7c54e0d1f0b8804018542e7d57d070c3d4da08b3055e1940f8dc53f1c40` |

本独审从归档编号正文实际重建，均逐字等当前及固定09a85正文。M已知UTC日期目录的base64url suffix、manifest身份声明与已登记SID/原turn对应；没有由此打开原生源、枚举目录或扩大读取。两方提取说明限定本人已知附件和必要scalar，不含系统headers/context/thinking或peer材料。

## 首失败与实际接收边界

- M首次附件核验请求把文件当目录cd，关联结果明确Not a directory、isError=true、exit1；后续对同一已知附件直接wc/hash成功。两次必要请求/结果原样保留；这是路径错误，不是审批拒绝或绕过。
- owner首提取器对generated-prefix asset误用精确basename而得到0行并在M proof写入前assert失败；后续仅改为已知实际Read文件suffix及精确编号块，未扩读或重跑模型/产品。此项按包中首失败说明登记，不将叙述升级为另有完整原始运行收据。
- index明确承认首次getApp偶然显示I06前台，未展开/保存该内容或使用意见；归档仅本方必要UI片段。本独审不据此宣称全程零偶然显示，也不从最小片段推定未记录的行为。
- 两方受理/SID后owner记录在 `2026-10-22T20:15:03.300Z` RELEASE，根已ack并转T06；未等待terminal才交还，不产生新的GUI授权。
- 归档strict snapshot与index相同：Z仅原turn.started，M原turn terminal_outcome=null，无current-turn fallback。完整输入受理不等于模型完成；本包没有正式completed/完整报告收件或新双Pass，上一轮过程Fail保持。

本独审仅核此小包、指定owner准备输入和必要冻结文件；未读模型意见/报告、后台/native/global源，未运行产品测试或GUI，未改原件、产品、review树或operator回执。只新增本文件，后续正式终态、两全文报告及全部意见须另行独立收件核验。
