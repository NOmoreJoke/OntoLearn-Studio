# Dispatch方案 r2：首审意见处置

这是作者处置记录，不是独审通过。首轮主稿35460B/SHA7b1fc29a0314787a5c13e14da903b2c2c8f12394a4e88db73f2989cb4b15151c原字节另存 plan-r1-before-revision.md；首审9173B/SHAa6bce6c54fb66b812b2971a539775de18c216cd72843eebcdfbfe7becec12a26原字节另存 independent-review-r1-before-r2.md。r1输入与checks.json均保持原字节，旧格式检查不跨归r2；唯一独审报告未由作者改写。

## P2-DP-01：仅撤scope的同步fence

首稿只重核stopped/current/owned不足。主方案§5.4与新增§12.1规定：真实issuer在撤scope/lease/cohort私有registry之前，先同步推进T01为同一actualSource保留的私有epoch；source最终check→consume→return禁止外调/再入。T01捕获E，返回后直接读本地附着身份/epoch/source未封闭，与原三项一起核同；不调用source getter。失效sink只有否定能力，无权限授予或caller设epoch。source路径未兑现、联动失败或OS撤权无法native证明时不升级为生产授权。

scope-only revoke不stop、不换session/engine/generation的write0反例已列§10.1；consume后fence变化则旧permit保持失效，不自动重发。以上是具体合同与未来验收，未运行fixture，待独审复核。

## P3-DP-02：producer、ticket与真实终态到达

§12.2给出bindOperation、bindAcceptedJob、observe、projectTerminal、closeObservation最小私有签名，绑定实际issuer incarnation、Supervisor/child、原private ticket/dispatch、完整原request、实际issued版本/limits/origin、真实claim/Job/receipt或round。任意Promise、caller bool或字段同形新DTO均不充分。terminal Job事实只结业务ticket，worker/Store/native永久寿命另交；原implementation没有真实来源时保持缺失。

每ticket一个privateObservation/内部订阅，最多128；通知只注册一个总分派listener。注销失败保cleanup-unknown与watch槽；终态待清理identity每件4096B/共524288B，不借WeakMap/闭包暗留整frame。缺producer仍unknown，当前wire和三writer不冒称已供。

主线另指出128后台ticket满额可能阻止producer自己的job.get自锁。§12.3明确共享真实128订阅总额、预登记通知来源，以及独立受同scope/fence/profile约束的completion foreground通道：最多1个RPC/独立262144B池，只许真实producer为现ticket发送job.get/subscribe/unsubscribe；不是health/ping或caller优先级。原普通pending128+heartbeat1+completion1最多130为新增申请政策，scheduler仅1timer，poll超时不无限新发。满128后真实terminal来源仍可到达的闭环已加§10.8；实际producer未交之前不声称生产闭环通过。

## P3-DP-03：clear timer同时结delay deferred

§6、§7对应行及§12.4明确stop撤接纳后clear自有退避timer并同步reject其delay deferred，令await/finally实际执行；仅清本attempt starting引用，防双结。只有spawnEntered=false且无child的路径能结never-created；已进入spawn或资源不可证明未产生则走真实终态/unknown，不从取消路径删除。§10.3增加退避期stop、starting实际settle/spawn0/无child drain可结束，以及相邻已spawn仍等close的未来fixture。

## 本轮边界

只修本主稿、仅新增r2过程文件；r1材料、独审报告、C1原59/root-closure、C2固定0a03539及全部产品/测试保持原字节。两次大patch因格式化表格上下文不匹配而原子拒写；改为小范围精确段落与新§12后成功，原工具记录保留，不当产品测试失败。仅文档格式/Git/hash，未执行产品、DB、测试、新子进程、网络、模型、GUI/native或stage/commit。
