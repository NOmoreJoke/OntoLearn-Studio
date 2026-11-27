# T01 启动诊断合同 r2：内部设计R1–R4处置

保留 [r1](business3-ready-startup-contract-r1.md) 原件（SHA `f715934e6a8bfd130fbb0c01c62d33026b6f19f990bc4268eb66a0ee6a3673ed`）及 [独立报告](../../reviews/T01/business3-ready-startup-design-review.md)（SHA `d869a4542da0419d07ad673fa9d2b694f8db9291272e28c6124fb7d10dbf8628`）。本页逐项补充四个P2合同要求；仅文档，未批准新码或运行时，产品仍固定b35。状态见 [status](../../reviews/T01/status.md)。

## R1：优先分派、首错和所有错误门

在main当前受信child/generation的decoded-value入口，**先于业务notification/response验证**识别kind=startupFailure。仅显式受信profile3且hello尚未成功可接受；精确形状/单行实际UTF8≤1024/expectedRegistryHash/有限error全部通过才接纳一次。非法记录也同步终止，不走anomalies三次容忍，不加入普通response/envelope或null-session业务错误通配。

每generation显式保存启动promise的resolve/reject和已锁定的startupCause；合法诊断同一同步调用中先锁首错、terminal+reader.stop、拒启动promise和全部pending、清timer/停止新发送/终止自有child。即使hello尚无pending，也直接拒启动promise。随后close/stdout-end/stdin-error/timeout/清理异常不能覆盖已锁首错。没有合法诊断时使用原通用安全原因；child退出码或文本均不能升级成格式错误。未曾ready不制造带旧session的disconnected事件，初始错误由启动promise→真实catch传给调用者。

精确错误接收门逐个登记，不能只改一个safeError：

| 门                                                             | 责任/必要适配                                                                                             |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| main-engine receive/finish/start promise                       | T01；startup记录单独严格验证和首错，实际business3仍走独立response/error3分支                              |
| contracts/index safe-error helper、taskUpdateSchema            | T01；新增精确local-startup-safe定义与获批3错误入口，保留旧error2约束，未知/多字段均拒绝                   |
| task-service connection事件先验错误校验/恢复状态及catch        | I06仍持有；必须经root精确owner接线，按受信profile及错误来源选批准分支，不因我方改index就假称已通          |
| main/index handler catch及命名bridge返回、preload/renderer显示 | I06仍持有；真实最终SafeError投影、可信sender/代次、固定messageKey呈现均须同版联验；不得新增generic invoke |

PROJECT_FORMAT_UNSUPPORTED建议仅属于批准后的 **local-startup-safe** 分支，不自动添加到普通业务error3或error2。该分支精确使用r1新码/key/params/retryable；已存在三码的startup形状收窄到r1固定params，不反向修改普通业务错误。safe-error helper只能验证批准有限union，不能接受任意code；真实调用来源/profile由main私有状态绑定，renderer不提交这些标志。root尚未批准这组schema/字段，也未完成I06精确接线，当前全部保持缺口。

必要oracle比较完整入口JSON、启动promise的最终固定SafeError、所有close/timeout后的同一首错、task-service中间投影及bridge最终值；不能只断言child关闭或pending清空。

## R2：profile3专用格式诊断

仅显式main受信profile3、实际target_format=3，可发PROJECT_FORMAT_UNSUPPORTED/{supportedFormats:[3]}。默认生产profile2保留原通用安全启动失败，**不发此新码或支持[3]的记录**；日后要2精确呈现需另冻结local profile2/[2]合同，本次不扩。profile由main内部有限配置决定，不从renderer、child自报或任意继承环境读取；未知profile是配置错误，不能推断数据库不支持。

3App/2Engine与2App/3Engine只涉及协议协商不兼容，给各自完整VERSION_INCOMPATIBLE终止oracle；Store未来格式是另一typed原因。Store typed异常可继承原ValueError以保留旧调用兼容，但只有真实格式检查点能产生，禁止按字符串startswith/异常文本映射。实际format数值不跨边界输出。

## R3：从未ready与ready后失效分开

- 合法启动失败记录先到、假hash hello、非法hello：不发ready，同chunk后续帧不消费。
- 合法hello已接受并发ready后，再出现startupFailure、重复hello、错误版本/session：当前会话同步失效并发真实ready→disconnected，停止同chunk后续帧和新请求。已发生的ready和accepted/committed历史不能抹除，不登记为“从未ready”。

第二组中的startupFailure按无效帧关闭，不能当新的启动原因或回拨到pre-hello状态。失效后的任务结论按原claim/Job/receipt恢复，不把连接问题覆盖成durable失败。r1验证表中的“统一无ready”以本节精确两组替代。

## R4：逐资源清理及最终canonical门

入口从第一个自有资源取得开始登记状态：temporary、Store/lease、Coordinator/任务、signal旧值、reader线程/停止标志及其实际启动状态。每个已取得资源都执行自己的有界收尾，采用嵌套finally或独立受控cleanup列表；某一步失败继续其余释放。未取得资源不清理，未安装signal不错误恢复，不宽泛kill用户/其他任务进程。reader的fd/daemon和实际worker fence保持原批准边界。

锁定第一处真实typed启动原因；cleanup次生异常只记录有限本地失败状态，既不覆盖首错，也不回传异常文本。没有首错的主动取消/正常退出不制造格式/存储失败；不编造成功cleanup或资源settled。完成全部收尾尝试后才最多输出一条合格诊断、flush并非零退出；诊断写失败继续安全退出。自有temp删除失败/reader未settled等不能据一次错误记录宣称资源已清，恢复仍依据真实状态；进程结束与磁盘清理不等价。

最终canonical须另行批准：startupFailure独立定义、local-startup-safe有限新码、常量/strict字段、1024实际UTF8预算、受信profile/expectedHash来源、开始/终止状态与单行UTF8完整golden。r1排版JSON代码块仅完整值示例，不能当实际JSONL逐行原件；新candidate registry变化后重算真实hash与全部同源fixture，不能沿用b35hash。资源加载失败而无可信hash时保持固定stderr+通用退出，不发假诊断。

无窗口机制计划增加每个初始化及cleanup点故障、first-cause保留、lease可重取、剩余资源收尾和真实bridge错误全链。源码/包/native及指定双审/CI保持原门。内部设计意见关闭也只是可交root独立读回的合同，不自行实施或启用ready。
