# Dispatch／永久排空：静态调查依据

本轮只有文档。主方案的源码事实来自固定423b真实文件及已固定I06方案的指定切点；未import或执行产品、测试、Node子进程、GUI/native/网络/模型，没有stage/commit。本报告不是独立审查结论。

## 实际读取与来源

- engine.ts全文工具5f62fd、f9125b；#operation301、#finish328、stop366、#ensure373、#start382/spawn424、stdio473–487、heartbeat514、#receive533、#send637/stdin.write689。固定26260B/6d55774068ca27a49958daeea9f4b1fa15614c95563ca28b8a768265ecd4365e。
- Coordinator request233–330同步调用dispatch；dispatch333–471全部方法、tick474后续任务；serve880先emit(request)后tick。实际全文目标段38d694、28ea3a；stop756与finally882–923为0dc281。job.create queued回复与后台任务分开；普通同步真实response可结该次handler，不能把所有reply永久占128槽。
- 当前registry business3 methods真实列表及v2Runtime、effects为38d694、598c53。方法分类不能由caller选background布尔或只猜effect=read。
- 现main/index before-quit与构造、TaskService TaskEngine/request来源、t01-startup-supervisor真实business3无scope回归为1f0869。它们只读，现裸request不是生产scope来源；新生产attached路径必须封闭它的旁路，正式接线另授，不修改原测试取绿。
- I06 ffb主B方案§4.1/6/8、controller B报告为5f62fd/f9125b/0dc281/28ea3a。0dc281大输出包装截断后，28ea3a把§4.1/6/8精确重读，未把截断当全文。只使用该固定方案，不以e2c旧实现当已批准依赖。
- 本树@types/node child_process.d.ts的stdin/stdout/stderr失败spawn可空、killed/kill不证明进程终止、PID复用风险，以及stream.d.ts的destroyed/closed/writableEnded语义，见143082/0dc281/28ea3a。这里只用已实际读取的离线官方声明注释；没有浏览网络，也没有把未核验的child close概括成三pipe已全释放。

固定输入及每件完整bytes/SHA在 investigation-inputs.json。Node声明文件是离线调查材料，不是额外产品依赖采用。52个拟采用产品/测试逐项独立 Git423b=current/bytes/SHA核同，075951实际exit0；主方案新树与两新产品/测试均不存在。未来writer仅engine和两新路径，尚未授权实施。

## 静态反例及方案选择

1. #finish移除当前session后旧child未close，下一ensure可再spawn；每分钟5次速率界不限制无限分钟未关旧child。提议owned cap2是新增工程政策：1个current/starting（单#starting互斥）加1个retiring，满时拒新spawn，不能遗忘unknown。
2. pending timeout删除映射但stdin可能已写；以pending=0或kill返回true作underlying结束会漏实际工作。普通同步RPC应在严格原response后释放foreground；job.create回复queued仍持后台ticket。主线提出该区分后主方案§3.1补全真实registry/coordinator方法表、迟到response关联、job.cancel不结原Job。
3. 当前#receive遇缺pending的business3响应会finish；若保留已超时foreground，须先核真实retained原request，合法晚response只结completion、不重结logical Promise。未知id/错session仍沿原异常政策，不能放宽所有late response。
4. Nodechild exit后某自有pipe仍可能未观察close；本方案独立等待child和三pipe，不用exitCode或时限释放。已exit/close不重复kill，避免PID复用危险；缺真实close就占槽/unknown。
5. hello没有完整issuedImplementation，不能写前发明该字段；现business3 Store首次IO发生在hello前。主方案明确实际Job DTO/context来源、首spawn位置lease必须先到，写前门不能倒授权初始Store IO。
6. 同UUID新Supervisor对象不能取旧来源，也不能只给旧ModelService换一个engine字段；主方案要求整个source/projector/core/application/context链重建，短断线同对象重连则保永久寿命。

以上是静态推演，不是已跑反例或性能/容量结论。未来真实测试必须按主方案执行；原57P0、两OS/真人、双指定模型及CI/正常合并仍保留。

## 本轮失败与校验边界

首次合并规则输出包装使common中段截断，随后606e90单独全文补读。f9125b命令最后rg没有匹配Node close文案而exit1，前面的源码输出仍是读取事实；没有把该exit1声称产品检查失败或通过。一次apply_patch因Prettier已改变表格空格而原子verification failed、未写入；之后按f51d77实际行修正并成功，未覆盖产品或C2。

本轮只运行文档Prettier及stdlib文件/Git/hash静态校验。代码改动完整npm check、真实子进程、平台native/e2e均未授权也未运行；既有C1无变化未重测。后续独立agent审查将由另一作者写独立报告，不能由本作者自填Pass。
