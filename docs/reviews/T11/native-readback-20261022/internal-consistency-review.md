# 最小补采投影：限定内部一致性复核

实际审查者：同一既有独立agent `/root/t11_independent_review` 的新限定文档任务。只读本目录投影/索引、旧创建回执与冻结正文，不访问原生全流、其他session、GUI或产品验证；因此不能独立认证上游原生采集真实性。

首轮发现1项P2：README称已投影M精确Primary working directory，但M proof.cwd为null。其余编号行重建/哈希/索引/权限、failed/aborted/无报告/无Pass表述均通过。首轮对应索引c9a860c8e52bcd4ea63b86fe164aa187e27eaf2f114548af899a3fd13614e2a7。

owner在已获准的本人精确session llm-call中，仅重新提取Primary working directory标量：原行首限定regex漏掉非行首marker，修正后精确值等T11-minimax-review-7d28fdb。未保存/打印周围system；M proof添加cwdSource、cwdScalarCapturedAt、collectionCorrection并刷新索引。没有产品改动、重测或新外审。

实际残留复核结论：**P2文档不一致已关闭**，当前cwd与README/冻结工作树一致，来源/时间/修正说明齐，当前字节与新索引匹配。最终索引SHA256：`495941dd959dea66ceb2a71ec1c1404d1ddbd1c8c413330142bc45336b75d833`。

agent从投影编号行独立重建双方正文，确认无缺失/差异/冲突；Z的322空尾与M四段实际范围保留，line-map hash匹配。这个结论仅证明文档内部链路与冻结稿一致，不宣称agent重新读取原生记录、确认模型完成或指定Pass。实际终态仍Z failed、M aborted，两约定最终报告均不存在。

开发者显式文档格式检查初次发现3份新流程文件格式问题，仅格式化新投影/README并刷新索引后通过；没有改原创建回执或任何旧冻结prompt/manifest。目录0700、投影文件0600，未保存原生headers/一般system/thinking全流。后续重派、错误恢复与GUI窗口仍由总控安排。
