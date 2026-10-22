# 历史审查排版副本索引

三份历史审查原.md保持原位原字节；原c0提交、原首轮不通过、后续关闭、原行号与所有历史manifest不改。本目录只提供Python示例排版的阅览副本，不是新技术结论或重新审查。源身份与副本身份逐件见[对应清单](format-copy-manifest.json)。

- [当前累积报告排版副本](formatted-history/current-independent-plan-review.md)
- [r1报告排版副本](formatted-history/r1-independent-plan-review.md)
- [r2报告排版副本](formatted-history/r2-independent-plan-review.md)

副本页首分别链接原件。原identity/hash/行号仍定位原.md或固定c0 blob；不得用副本字节假称历史原件已重新核同。原归档ZIP、索引、审查报告及archive-audit脚本保持不变，不重跑历史脚本补造当时证据。

仅[tool.ruff.format].exclude精确列这三份不可改历史原件；没有排除docs目录，没有修改lint、业务检查或兼容测试。副本继续受ruff格式检查；日后新增Markdown仍正常检查。此次只解决文档格式门，不证明完整npm check、产品、指定双审或发布门通过。
