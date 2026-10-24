# T01 同候选双指定模型审查输入

本文件原样供两次独立审查使用，不拆成不同范围或以历史阶段部分通过代替完整审查。模型分别固定 ZCode GLM-5.3最高、MiniMax Code M3.1-Flash/xhigh；实际任务模式分别读回 yolo、bypassPermissions/Full access。仅由总控在安全独立环境/实际租约就绪后调度，不在当前用户桌面打开应用，不把此输入当已创建任务或 Pass。

1. 审查开始先读同宿主 `/tmp/t01-changeset-final-git.json` 最终 Git 回执中的精确 base/head；总控转入隔离环境时同时携带该原件，缺失则不能假定HEAD。固定该 Git 对象只读读取，核本阶段14源码/测试及 ZIP 与 `evidence/changeset-final-source.json` 全等。过程 f51 不冒充受审最终 HEAD。不得修改实现、测试、依赖、配置，不提交/推送/切分支，不运行 Electron/native/e2e/HMR、凭据或 GUI；可约定无窗口验证，输出独立报告并保存完整原始输入/输出及真实终态。
2. 从批准基线 `5f910b52c69d86a1076b2032e5d3c63e715947f3` 到最终 HEAD 审完整 T01 实现及原 Goal，包括已有 Store3/事务/补偿/CAS/内容缓存/canonical/startup，不只审最后14路径。阅读原 PRD FR-001–006/804及相关附录、`full-function-acceptance-map.md` 全44项和实际根授权；明确哪些仅内部机制、哪些完整产品仍缺。不能删除缺口使阶段看似父功能通过。
3. 本阶段重点：真实 typed before/after/control 与唯一 Store writer；四hash命名空间；同连接事务和两个线性化点；完整Diff字节/manifest/分页链及有界data-only捕获；首次confirm与持久原请求回执、TTL/GC/新RPCid/旧Session；新operation拒接管、原claimed operation跨重开精确重试；Store3 marker/sequence/checkpoint/receipt+结果终态同事务；取消/超时/postCOMMIT；undo ABA/引用/owner-slot/墓碑/retirement完整影响及缺证据暂停；旧2/原sourceTable/已有任务兼容。
4. 阅读本阶段实施报告、独立实现报告、最终源码清单和原始归档索引；核首次失败、被替代候选、修前/修后P2和真实完整工具终态，不以摘要数字/重建日志替代原件。核 fullcheck1125TS/2789Py/44既有skip、新unsigned包正式3Job与重开、实际9资源/asar/main同源；区分机制注入、真实OS退出、源码、包内CLI、真实UI、native及生产证据。
5. 保留原全功能未决：真实 I06 项目选择与命名bridge/完整Diff/真人确认、T08真实Agent、完整附录C语义/来源parser和pin、学习及不可洗白辅助、全项目恢复、其余44项、跨功能/双平台/native/至少5位用户验收、CI/正常合并/远端。对阶段可否继续与父功能/发布可否通过分别给明确结论，不以不可用UI的scope waiver放行父功能。

报告列具体路径/行、可重现条件、影响、优先级与修复要求，明确未执行项。实际出现新产品/测试/依赖/验收或基线改动时须新候选并重新同版独立审查；内部agent报告和历史双审不能代替这两次新审。当前仅准备输入，完整Goal保持active。
