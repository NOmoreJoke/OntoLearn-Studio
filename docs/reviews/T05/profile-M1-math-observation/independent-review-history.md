# 独立审查历史记录

审查者：`/root/m1_observation_independent_review`。未参与实现，仅只读审查；本文件由实施负责人整理其已收到的结论，不冒充审查者自行落盘的原文。

## 首候选 b0fcb7dc1dd8b4ebe3436e996926dba55f9e19d6

审查核对149批准输入、adoption逐项字节及sourceRef；151受控与实际base差异142分开；目标AGENTS仍为base。纯输入1331 ID与golden物理分离；未发现golden参与材料、生产或restore上下文构造，未发现假origin/手填allocation/重建payload或正式Job假通道。真实7/15/11完整结构、typed数学值/原source、原L与新C/R观察及retention边界可核。

发现一项P2：成功main比较原先只比较Boolean和生产/恢复自洽，没有把左右完整typed PV分别绑定到独立验证的operand观察，可能放过左右值错误。要求真实main左右完整PV分别与对应eq-self观察逐结构相等；unary也核两边，不由golden回填实际值。

## 修订 e686a112fdbffdcc2b2bd042e5c131c1e2d586b1

仅新test加强上述完整PV比较，测试21143B/SHA256 `5ec7206ee82d4b6a29604f670fc8cbced68c5685e1fe6de291dc1b596472f868`。审查者核实际Git/字节、149与fixture未变，关闭该P2。全量该版仍有两项前门合同层级差异，原件另存p2-full；关闭P2没有把两项差异宣称为通过。

## 最终候选静态复核 051ae4cb9b5e58560c8e45cdc56fd98522777b5c

审查者全文核root2461B/c10a07b1…分层决定及最终test24239B/SHA256 `250a760bd1c0f2710a9585a67650c3d0b743f376c1ecdd308fdf0d3d8aaf6047`。固定例外仅errorOperandCases/error/28与error/31；完整错误合同、精确类型/DTO/diagnostic、无产出/恢复、main调用计数0及C/R状态严格断言，未放宽为任意错误通过；原pure expected单独保留，明确未由入口执行。

透明观察器以wraps调用原compare_values，记录真实次数并正确撤销patch，不替换返回值、不生成expected；既有P2补强仍在。局部静态复核通过，无新增静态阻断。最终实际原件/正常检查的独立复核另见`independent-review-final.md`，本历史不替代最终证据审查或父M1验收。
