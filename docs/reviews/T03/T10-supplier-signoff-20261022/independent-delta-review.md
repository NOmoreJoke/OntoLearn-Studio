# T03 → T10 F1 最小差异独立复审

结论：**DOCUMENT_DELTA_PASS_ONLY；F1/P3已关闭，无新增问题。** 这只通过两行供方事实/缺口记录的最小文档修正，不是正式sourceObject、producer、传输或持久pin合同已齐，不授schema、装配或运行许可。

## 固定范围

仓库 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping`。首轮审查封存 `4591339f87b5a5bb2e4894fddd62f0851ac12472`；本次固定修复 `76974caa71064a511e78da0a2e25f71eb6ac15dc`。完整读取修后signoff.md、F1-disposition.json和两提交完整差异；不改首轮原报告。

实际差异仅signoff.md第17行一处文字片段替换与新增F1-disposition.json。用精确一次替换核对，修后signoff其余全部字节不变；input-identities、author-checks及首轮两审查文件在两提交和现存字节完全一致。没有源码、fixture或冻结来源改动。

## F1处理

修文现准确列S5实际5个拒绝对象：空源、重复header、短行、空记录、空表头，对应EMPTY_SOURCE/INVALID_HEADER/ROW_WIDTH。独立重新核S5固定原件的length/SHA，并核全部locatedRejections名称与code，确无FORMULA_CACHE_MISSING。

FORMULA_CACHE_MISSING现只按S3“缺失、空、稀疏及重复字段”的已有拒绝语义说明保留；重新核S3固定原件身份及对应说明。修文明确“不是S5已封存反例，本轮未补fixture/未执行”，没有再用formula-empty成功例冒充缺缓存拒绝。F1-disposition正确保留原候选与首审ref、新fixture=false和产品执行=false，pending为修复提交时的历史待审状态，不回填它。

因此F1的证据归属错误已解决，无需新增或重新执行parser fixture。

## 保留范围

首轮其余核对结论继承：两行仍“设计+固定私有事实部分覆盖，未达可装配签认”；稳定sourceObject/真实parser producer与Table-options digest/full-frame profile/durable prepare接点仍缺，WeakMap不等持久pin。C1 raw整对象不得默拆chunk；prepare先于plan保护、唯一T01权威排序和unknown留pin仍保留。旧operation按终局负fence修正，不恢复旧窄口径。

本轮只做固定Git文档读取、精确字节差异与S3/S5针对性核对；未跑产品/parser/测试/构建/native/GUI，未读任何供方源码或caller/费用WIP。受保护AGENTS未写。未重新认证历史fixture执行、目标平台、worker/Store/重关联；无新schema、执行票或公共writer/锁改动。
