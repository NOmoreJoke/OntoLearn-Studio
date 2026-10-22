# O15 MiniMax 原审查终态、原稿与限制收件

M原turn正式completed，完整报告原样保全、owner分四段全文读完；完整150 scope结论为NotPass，另有明确未读/部分读取。不能与Z的静态Pass拼接成整体双Pass。原15外部意见流程全部open，原报告不改。

## 原turn与原稿身份

精确session `mvs_c28510d4b96a4ecbaea7be3f838c5110` / 原turn `677c3d52-3d00-45ec-96af-2005b0a71d58`，官方runtime SQLite以mode=ro、query_only=ON、timeout1、SID+turn四字段精确SQL核到completed，updated1792695033165（2026-10-22 18:50:33.165Z）。没有用子task/投递turn/UI停止按钮代替原审查终态。

本方新树launch-O15/report.md为非symlink普通文件，59291B、548行、SHA256 `256f7af033f4141bea9b26cc0895272e39076beeec1f39f69eda2b52ce6f2ada`，复制前后来源两读相同，原样另存minimax-report-original.md.raw。owner按1–140、141–280、281–420、421–548逐段全文读取，无输出截断。当前原turn末assistant公开text4044B/18c15563ec14dad8af46d308c66ee2ec13fbb5c6cc5e097280c8df46f4f8e9ce，stop，message id与timestamp见terminal preservation JSON；未复制thinking/system。

报告三层结论分别为：A九文件候选delta条件Pass；B完整150工程静态NotPass；C运行/打包/生产无法验证。F01–F11实施证据成立，F12–F15未实施且归属/处置理由成立，但全部15流程仍open。§8.1–§8.12新问题逐节登记标题、原行号和原段hash，不直接采纳为已确认产品缺陷，不篡改严重度。

## 覆盖与当前原生缺证

M自述五项旧全文缺口已读完、四条只读子线已回收；§3.4仍明示job_store/storage仅测试依赖区段、entrypoint未读、i04_matrix_evidence第121行后未读、部分大fixture仅程序化检索、若干输入只pin/hash、I02JSON仅grep。子线与主审的阅读口径分别保留，150身份全部匹配不能消除实质阅读缺口。

M当前messages.jsonl已从本原turn的compactionSummary起始。独审没有读取或输出该summary，也没有把其中摘要当完整原始工具流。首轮正式附件/短启动在压缩前已由71bc9e固定输入包和根独核接收；它证明输入进入原turn，不外推到后续五全文阅读或命令执行。

当前可见段能重放原报告Write+7次成功edit，最终等于原稿；原始五全文Read与两正常O执行call已不在现段。manifest声明的本方ledger/display/snapshot精确路径均不存在，首次读取ledger的FileNotFound属于收件导航限制，不是模型/产品失败；没有glob扩扫、重跑命令或伪造原始argv/exit配对。因此五全文native覆盖与两命令原始退出链在本次独立收件里仍缺证，保留M自述和可直接核到的原流，不冒称已独核执行。

## 正常命令原流与本轮首错

报告显名四流已原样保存并全文收读：selftest stdout0B、stderr8697B/c0f7dbd8220f001985022901a5384973834ea1fd5a9e5e14147e77545c425e06，57项OK；build-check stdout1001B/030cabeee57f2adf1e3d03376c0f079e78a62e045c819b67f8241b356888bce5、stderr0B，417/320、280/137/wholefalse，五产物bytes/hash相同。报告声明本方3.12解释器、两命令exit0，原始call缺证边界如上，owner没有重跑。

M§2.5报告一次从子目录用相对.venv/bin/python导致exit127，后改绝对路径恢复；该原始执行call不在当前压缩段，按reported-only保留，不称owner原流复现。D子线的父公开task_output（task bg_ed2e8118-7d71-4eab-8058-70f2b02090c6，parent call_kAR5EpL7YT98WA5IRJ0PUjlL，record126）以succeeded/truncated=false返回44330B/1b2217117adb91d01d3f2815336521eb0473148121d2ca88157f00d9c7e6beab，原样另存。它自述observationId/datasetId比较、edit工具、Number/cancelBoundary移植、scanner键类型、Git路径Cquoting、孤立代理计长及pointer/input后缀等首错并自述修正；本次没有进入D子raw，不能把这些自述当独立复现，也不能把D自写Python移植当TS运行时。

## 已核报告准确性限制

- scope-contract真实2476B，报告§1.2误记36691B；其SHA7576仍正确。
- preflight-observe真实5750B/3098230223b0bd76e566cf831b5ad17f60e43c498056a173576830cb85f18445，只含trackedPathMetadataCount=1262，没有1262条trackedPathMetadata列表；报告文字过宽。
- 1262减1246为16，§4.2写多28错误。
- §4.1目录分项36+27+22+16+15+5+5+2+12合140，不闭合150；身份核验结论与这段汇总应分开。
- 首尾汇总称3中等，而§8.1–8.5实际五个[中]标题；十二节标题总计中5、低中3、低2、低信息2。按标题登记，不改原稿或替模型升降级。
- F10证据行仍引用已移除的mock ValueError('invalid finite index')，应按固定source真实测试核对，不能拿旧断言片段作本版证据。该项准确性不自动推翻现有限域防护，需要隔离triage。
- `actualTaskId/Turn/Terminal`的null和“setup-only/未建任务”是审查agent内部视角，不能否定owner实际创建/终态已获官方证据。M权限仅用户配置的自述不能补任务实际模式；owner现场始终授权回执仍独立有效，未另读全局配置或复制凭据。

## 保全与后续

M正式终态后owner仅直接hash声明的450保护件、10launch和1AGENTS覆盖层，全部匹配，HEAD0f87/index空/仅授权AGENTS未暂存；没有运行observe或打开hash未知metadata，不签全filesystem冻结。GUI自派发释放后未再使用，未给Z或M发送对方本轮意见，没有产品复测、安装、付款、Goal、push/PR/merge。

总控另授权隔离triage五个中等标题，责任/反例/外部供方缺口在独立O15-M-owned-triage目录处理；本收件保留A/B/C、§3.4缺口及15流程open，不为补阅读立即续任务，不在本目录改产品或代总控关闭意见。

## 已有父task状态卡追加核回

不增加路由，当前原turn record3的既有task_query公开状态卡还可独核：提取历史首失败的task bg_7c43a5df-9986-47fa-8def-9cd1d6a49c78正式failed/exited/127、rawBytes55/persistence complete；两项获准oracle合并task bg_c0a612bd-d8d1-497e-be96-23cf04830aed正式succeeded/exited/0、rawBytes1404。仅提这两张本方卡，未复制其他task或summary。它们补证实际出现127任务失败和合并正常任务成功，仍没有恢复相对解释器argv/55B原正文，也不替代两Python逐条argv/exit链。前述reported-only边界按这个具体支持范围细化，不能再笼统说127本身全未核。

## 独立收件核验

`independent-minimax-terminal-intake-review.md` 14582B/SHA `1a9f0fa6d51b40a2a62e1fdc3713c05ef0eb6159163c4eb6785912afc8538fd7` 已由owner全文收读。独审直接核原turn正式SQL、源两读=副本=native Write+7Edit重放、原末答及四正常流；M自己的SID/model/xhigh在当前公开me调用核回，permission仍归owner现场回执。它明确保留compaction导致的原始五全文/逐条argv-exit缺证、父任务合并0/首次127的有限支持、D公开自述和六项报告准确性问题，不把收件链通过写成完整scope通过。
