# T05 保存参数与真实 Store 探针

使用固定批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3` 的 `storage.py`，实际字节与本线一致，SHA写入 fixture 并由测试核对。没有导入T01未批准服务/格式3或改共享文件；没有新建生产写入口。

## 提交给 T01 的具体参数

`tests/fixtures/quality/store-parameters.json` 给现有 Python `Store.commit` 的精确参数：projectId、base、operation、job、definitions[{layer,id,value}]。value 是本线严格校验后的完整约束/规则payload，不是执行结果；本探针实际保存五模板与同一规则多结论；独立比较表达样例在fr505-extension-cases.json中，尚未通过本探针逐例持久化。修订2关闭一个约束和该规则，base必须重新取权威revision。

这仅为私有格式2探针，不是公共IPC/schema或产品ChangeSet决定。T01需明确接受或给最终包装映射；正式保存仍经T01唯一预览/确认/原子提交/undo。用户草稿中的revision不是权威版本，不能直接据此覆盖。

## 实际探针范围

测试在pytest临时目录创建真实SQLite Store，校验域payload后调用唯一 `Store.commit`，真实关闭重开：

- 五模板/多结论完整字段往返不丢；保存前后不可变快照及operation/job标记真实存在。
- 启停和修订后依赖向量推进，旧快照原payload保留；旧base返回真实revision Conflict，当前状态与标记不变。
- 在mid_data、mid_marker、before_commit三阶段真实事务抛错，整批定义/版本/标记回滚，重开仍为最后已提交状态。
- after_commit响应丢失后真实marker仍存在；同operation/job/参数重试返回同marker，不推进第二次revision。产品应先查marker对账，本测试不是自动重发写入策略。

不填推理/验证expected到Store，不运行推理或SHACL，不构造执行结果/current指针。只证明现有Store可完整保存该opaque域payload并保持已有事务语义；不证明空白项目表单已接线、约束/规则已生效、正式启停失效/推理撤回或产品undo完成。

## 必须由 T01 接受的引用缺口

当前Store对一般定义payload是opaque；通用引用校验只消费其既有显式references格式，而本线私有严格definition字段不包含references。正式应用服务必须从constraint targetClass/path、rule conditions/conclusions导出概念/属性引用，并按T01单一格式存储/校验。**不得把本次opaque往返当作域引用已校验**，也不能本线自创第二包装契约规避。

同时需T01确认：服务端分配/复验定义revision、启停/删除的ChangeSet预览与引用影响、旧base拒绝和失败草稿保留、撤销/历史、结果失效依赖；格式3公开启用及相关路径另按原owner交接和同版门禁。参数fixture可直接由owner逐项回应，不需要等整个M0。
