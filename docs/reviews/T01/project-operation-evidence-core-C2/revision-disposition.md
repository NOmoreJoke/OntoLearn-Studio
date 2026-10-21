# C2 独立审查处置与证据边界

最终产品 `256b7f1f1abd51b7cabfdfe9fd2e5013f4e8cd8c`：模块39943B/d6554289、测试50985B/9097ccb7。独审原报告保留全部首问题、实际输入版本、真实探针和后续闭环，不倒写早期通过。

1. P2-01：每次自开事务后经计数门读实际 user_version，exact integer3 才继续；0/2/4拒state，未用owner._target_format代替实际库头。
2. P2-02：结果同版 row contract允许有限小数。只对已通过该合同的payload开放constant-size finite safe-range float编码计费，selector及SQL typed行仍不接受float。
3. P2-03：所有目标Job均经view调用原format3._history核到当前head，后续CP损坏报incomplete；正常后续base推进不否定原受理。
4. P2-04：全行预收费同时按固定DDL的列类型/nullable核SQL typeof；created INTEGER列的TEXT拒绝，真实SQL允许的NULL未被擅改为NOTNULL。
5. P2-05：schema预收费纳入结构异常有限映射，HostReadFault先显式穿透；坏容器先检查并保AttributeError/IndexError结构族，SQL/资源控制异常与真正取消不被吞成incomplete。

额外观察：table names先count≤64再定位/收费sqlite_master全行，table_info先count≤32再物化；固定SQLite自带五列仅作明确bootstrap枚举，未允许任意schema字段免费。原query/probe/read常量不增。取消保存原BaseException对象；同时ROLLBACK故障附cleanup_failed，实际连接仍active则如实交owner，未伪称已释放。受控driver与持久损坏fixture不冒OS断电、OOM或真实磁盘故障。

专测由独立测试作者完成97→107→127候选；primary在其停止写入后仅补最后两条结构回归，最终129项通过。三编码各普通受理/runNULL/零轮阳性、真实ChangeSet完整多页/末segment/detail、partial rounds与终态消费完整性、cache真实回收、六类预算±1及零写/未知caller/取消/cleanup均有原件。低层typed测试因新增schema收费208B而首失败，已按独立完整实际行oracle补计该真实schema，不删收费或放大预算。

早期大字段fixture被原put_blob上限先拒，其后明确改为受控持久损坏材料，仅证明低层probe执行前拒绝。首pytest、ruff、格式与静态工具失败保原返回及原日志。最初primary复合ruff/check+format命令最终shell0不能冒ruff通过；独立8fcaf1确为ruff exit1，之后实际修复终态另列。早期27条ruff返回自带工具截断，归档保该实际返回，不补造未返回的尾部；完整后续9条与最终通过终态分别保留。

所有日志按原argv真实捕获；`2>&1`合并时保全部返回内容，不能恢复逐行stdout/stderr来源。原工具JSONL保call/result原行与源offset/一基line/hash，架空最终化之后的新命令不算已入旧ZIP。修前3bf/d8/d332源由primary按原patch和原ruff格式精确恢复后逐SHA核同独审当时实际输入；它们不是当时即时拷贝，也没有重新执行冒原探针。1c5d/1ce两版是在下一改动前保存的真实原字节。

本地完整check、source和独审只关闭内部机制阶段；没有正式scope、原物理绑定、启动首IO、生产reader/adaptor、GLM/MiniMax指定双审、跨OS/真人、CI/PR/merge或父FR通过证据。原44跳过不改称执行通过。进程/SQLite生命周期及真实origin缺失均不由哈希或C2事实补造。
