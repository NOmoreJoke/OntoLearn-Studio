# Mapping P2：新指定双审收件与处置

结论：两个新任务均已正式completed，完整派发附件均有原生逐字匹配证据；**完整同版双Pass仍未取得**。两方都以继承面、零diff或历史已读为由缩减了本轮明确要求的完整范围。保留Z局部Pass和M整体NotPass原判，不改写两份报告。

## 实际任务及原稿

| 角色    | 原SID / 原turn                                                                       | 正式终态                                                                    | 原稿身份                                                                  |
| ------- | ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| ZCode   | session_3d7a3bc7be217561ee227f6415e78e50 / turn_2be6c154-5b67-4845-8176-1dc5ec55616e | 日23官方event第18230行 turn.completed，2026-10-22T20:59:06.548Z             | 27632B / bbe0d321270f4eb40ffdac3cc508077f35bceb7a935f9d498bfe1493d12fc6a1 |
| MiniMax | mvs_b159af436fec43caa2b7272568bfc248 / 05e3f459-c218-4804-b6f2-3e76076fc4c0          | 明确授权的只读四列exact SID+turn查询：completed，updated_at_ms1792702707999 | 42120B / 886d6934b6c35a7acb4a37836a00aa5fc99972731813c39183bf3fde5bb6f178 |

各仅一次发送、一次受理；本次没有续发、新任务、GUI或产品运行。实际受审HEAD均为c1e44f81723f9c616f669f56481d1b1ada7e57f2，产品da1795b20c3c0d47ae975fe3371e802092a4b429。两树仍只见受保护AGENTS覆盖的unstaged差异。

Z UI为GLM-5.3/最高/完全访问；M UI为M3.1-Flash/xhigh/始终授权，原生模型分别GLM-5.3与MiniMax-M3.1-Flash。后台effort/permission标量仍UNKNOWN，不据UI推成后台字段。M原稿引用pre-submit时点的accepted:false及UNKNOWN ID，不是后继正式受理/终态的否定；原模型写回task-actual也保原样，owner的独立final-intake单列后继事实。

Z首main_turn中的明确本方附件自动Read块逐行重建为44835B / 8106610dac75122b6846c8050e5352f51bd90319179dee838c26ffc372fc1abf；显示244号空行保留了原末LF。M第一次Read真实截断至110行，第二次Read从111续至243；两份公开返回原件及截断标识保留，重建44876B / 48839f37ed03a220ea1f82cf97e67528a4a82fd7f0ee769be47b213e55288662，原末LF保留。两者均与冻结提示逐字相等，未用expected正文填缺字节，未导出其他system/header/thinking。

主已全文读两原稿并对初次工具输出截断的M历史表六行另行精确补读；原件稳定后复制封存。独立agent又全文审两稿及必要静态源，报告11276B / fd664a23fdf17dd3455dace5809eb8e0d0abfbaa26f68600443554f0d07aa00e；主全文读该报告并核其6件manifest。

## 未完成的本轮范围

Z明列14个unit、5个e2e未逐行读；锁仅身份级、若干schema/fixture抽验、约25历史工具及大量历史文档/ADR未全文，用旧轮次或其他owner替代。M登记1028项中44FULL、19PARTIAL、964METADATA、1UNREAD；按实际索引join，engineering180中27FULL、8PARTIAL、144METADATA、1UNREAD，许多允许工程文本缺语义审读。964条METADATA里962条逐项note为空。独立报告和JSON保存精确缺口，不把合法二进制/受限payload例外用来解释普通工程缺读。

已读原生输入、已正式结束、未发现新高等级缺陷均不能关闭这些缺口。仍需按原完整输入补足允许范围的独立语义审查；当前没有为补读而重跑check、pack或新增产品候选的必要。尚未发送任何补充消息，也未互传另一方本轮意见。

## 历史18项与新增11项

完整29项原文、行号和处置在independent/static-evidence-and-ledger.json，摘要见independent/review.md。历史Z1–Z7/F01–F11原ID和原严重度不改：Z1残余preview说法、F09计数、F06普遍XML论断为报告纠正；Z2维持P3与旧“无P3”终段矛盾分别保留，UI/正式接线仍按原owner边界，不把18编号当18产品缺陷。

新增观察不直接转成产品修复：

- Z Obs-3“row-limit不是最后case快照”不采纳。源码真实顺序为外部引用两例后CSV file→column→cell→row；row是最后解析case，JSON键排序不是执行序。边界仍只承诺最后解析后的累计三API计数。
- M N01“defusedxml首次import在guard内”证据不足。局部from语句在guard内，不代表首次模块初始化；已安装openpyxl.xml先尝试import defusedxml，条件成立时xml.functions亦在guard前导入ElementTree。历史实际首次导入时刻UNKNOWN，不按其建议改产品或倒改旧收据。
- Obs-1/2为binding登记和docs oracle依赖建议；Obs-4/N06保持原P2树、提交前同候选字节的实测来源；N02为已知B2坐标限制；N03为包证据增量而非首次单元语义；N04实际0symlink；N05与F06、N07与Z2分别合并理解，均不重复制造产品缺陷。

## 当前门与后续边界

候选及完整原始包继续冻结。原17项、首失败、历史报告与本轮原稿分别保留；本收件仅完成证据与意见处置，不是完整双审通过、CI/远端、发布或父业务验收。I05 fixture修复在另一供方分支，未混入c1e44或本产品。STOP/native/身份载荷不触碰。后续补读与任务续接由总控调度；本包不授新GUI、模型消息、产品命令、源码修改或发布动作。
