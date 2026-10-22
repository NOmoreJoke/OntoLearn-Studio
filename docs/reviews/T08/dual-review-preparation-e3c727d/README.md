# e3 完整同候选双审输入准备

仅T08流程文档，未创建任务、review worktree或读回设置，未运行产品／浏览器／GUI，也未改变Goal。源候选e3的28文件冻结；证据过程0932268固定，旧93516/5b64审件与旧原始输入均未改。

先读 `review-scope.md` 与 `input-manifest.json`。`full-review-input.md` 是双方相同的完整公共正文，包含新完整范围和当前政策全文；两份角色prompt只增加各自指定模型与待登记信息，公共正文SHA一致。它们不是已可直接投递的真实任务证明：总控还须建立独立树、固定过程/输入提交、实际cwd与报告根，并按原门禁登记运行/资源票。当前不CUA、不创建指定任务。

原101成员全部保留在 `inputs/history-original/`，不是当前实现；本轮28源在 `inputs/current-product/`，完整PRD/上下文在 `inputs/current-context/`，两旧NotPass与修前/修后全部证据在 `inputs/evidence/`。全部源码快照加 `.snapshot`，输入原字节不做文本规范化；`.gitattributes`只作用本材料inputs归档，不改变产品lint/build/test。

完整产品树与base差异分别列在 `complete-product-tree.json`、`base-to-candidate-diff.json`，不可用旧25/44/828或只用28源取代完整树审查。原件/新正文/manifest核验、独立材料审查及本次收据另列；该准备通过也不是新指定Pass。

静态生成初次遇到Git默认quoted Unicode路径，完整树读取未完成；已改NUL分隔解析并只在字节相同时续接半成品。该次失败的原工具输出留在本聊天，没有伪造另一个raw文件，也未执行或更改产品。材料最终须重新核所有Git/blob/SHA与包成员才能交接。
