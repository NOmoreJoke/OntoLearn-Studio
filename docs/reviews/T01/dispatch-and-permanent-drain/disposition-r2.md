# Dispatch / permanent drain R2 处置

R1独审的P2-DI-01和根补充的reserve同步重入问题已形成新候选，等待原独审者定点复核；作者不自行判Pass。原产品04ed06a、原过程4f270f0、独审14062B/eec339及两次真实失败全部保留，不修改独审报告或旧测试。

## P2-DI-01：跨Session共用真实control额度

R1错误地为hello和ping各设1池，并把它们不会同时未结当作总130的前提。独审真实旧child/stdio未终态时，新child已发hello，实际128业务+1completion+1旧ping+1新hello=131。

R2在实际accounting.reserve中令hello/ping合计最多1，旧unknown不提前回收；普通128+completion1+control1严格≤130。#start退避之后、实际spawn之前预留同一hello ticket，并同时固定真实hostClientId；spawn事件只发送这个预留。缺额度是规范QUEUE_FULL、候选尚未spawn；never-created候选在starting finally实际收口。真实已发送控制帧仍等严格response或其实际owner终态，不能以新Session或逻辑失败解额。

复制独立原probe，仅替换作者输出路径，实际4d52de exit0。原旧child发过hello/create/get/ping，原completion/ping仍各1，128次业务尝试被正确撤回后新hello为0、第二spawn为0。原独立两份失败脚本/log/evidence未覆盖。新增真实跨代专项另记录每次实际reserve成功/拒绝及等待采样：达到130、下一项拒绝，control始终≤1；真实旧owner结束后才可新hello和重连。还覆盖旧unknown hello、128等待者永久stop及逻辑control双向±1。

## 根补充：reserve → stop → return已知reservation

R1 cancelAttempted布尔把“已请求取消，但reservation尚未返回”误当作“已尝试取消这个真实reservation”。source.reserveOperation同步stop后再返回时，该新获真实token从未被cancel，watch也无child owner可释放。

R2分别记录cancelRequested和attemptedCancellation原对象身份。stop先撤never-written业务预留，未知producer清理仍保watch；返回真实token后重核stopped/原ticket，已取消则至多尝试一次针对该token的真实cancel，禁止进入ensure/spawn/write。cancel前先记录同一token，防取消自身再入；成功且无已bound观察才回收相应watch。throw或非undefined异步样返回保unknown watch/原known身份，不以重试或fulfilled Promise冒充清理。

新增三种真实同步重入机制测试：成功、throw、async-looking。每项都验证原token只cancel一次、spawn0/write0、业务payload已退；失败两项仍watch1，transport无child结束不代签producer清理。这里只证明消费者机制，不构造生产issuer。

## 首失败与验证范围

R2首联合专项有两项失败：启动前新增control拒绝未转规范错误，已保留原EngineError来源并将局部LifecycleFault转QUEUE_FULL；第二联合专项还暴露“128帧必须在短请求期限内全部逻辑成功”的新测试性能假设。预算测试现允许合法TIMEOUT，但必须等待严格原回包结清全部foreground、逐reserve/delay≤130，再验证一次正常health重连；没有放宽产品期限或硬界。

第一次额外PID采集还出现一个批量TIMEOUT，随后观察器把-t误列为待指纹源码路径而exit1，原脚本/双流/工具终态保留。后续观察器改为增量解析自有marker，以免反复解析完整文件干扰测试；最终针对冻结候选的新8例复验与原件见checks-r2/runtime-process-evidence-r2。

完整正常check及独立source重新对应新候选；原51 readonly仍逐项等423b，AGENTS与独审原字节未动。未改生产source/producer、协议、TaskService或native等原后置门禁，不以本轮修复宣告生产闭环。

## 历史PID措辞更正

原395861B/ebc0 JSON保持不变。它有29个marker PID和29次定向ps成功，但仅28份完整fixture argv；PID37879的stdout只有进程名(node)，不能因ps exit0称为完整argv。另有28个marker文件，一个文件可含多个child incarnation。当前runtime summary/main改正该表述；旧4f270 Git历史和原双流不重写，也未为追数字重跑旧29个进程。
