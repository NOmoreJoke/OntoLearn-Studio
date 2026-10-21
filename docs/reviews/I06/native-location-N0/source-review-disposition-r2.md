# N0 源码修订处置 R2

2026-10-22。唯一产品作者处置；状态为**已修源码、待新固定ref独立复核**，不替独立审查者签关闭，不宣称已构建或测试通过。

首个完整候选 `4cffd2d43b42dd1c14ae5c5745f2c705b7a6c6c8` 原样保留。三份首审分别为 independent-source-review-r1.md（16508B/585ea61f3f808af4b8221368ee12122f6b6f928b35c8639bd5e9fb29d5d49917）、platform-source-review-r1.md（15779B/10dbd240a5d2580947e2a801f97b86643a003024f80b45631963efc767cad7a2）、interface-source-review-r1.md（10473B/cfce3c180c3388ea693192fb6234853f87ae9a3e0e576c44b61defd219dc2cc3）。无改写原文或把WIP倒贴首审。

| 发现 | 实际源码修订 | 后续证据边界 |
| --- | --- | --- |
| P2-N0-01，平台P2-1：第二unresolved open耗尽cleanup槽 | 首个unresolved native open保原reservation并设全局不可逆新接纳fence，撤销所有已发布owner；新owner直接retained，其余active入口stale。禁止再开第二native open，留原两槽中的另一槽给close/poll/release/snapshot。Win静态open_record保真实returned_status，区分pending与失败异常输出，不声称后者仍running | 只证分支不变量；同步NtCreateFile实际是否出现pending仍无运行事实，unknown不减槽、不签释放；本N0无恢复该未知的实现 |
| P2-N0-02，平台P2-2：ACL未知阻止已知FD首次close | close_object只以value==-1判号码已退休；仍确切持有的FD/HANDLE恰close一次并立即value=-1，unknown采用OR保原ACL/其他未知。close成功也不清unknown或把owner签closed | 固定Apple Libc acl_free总返0，首审所列为显式错误分支的静态归属缺口；不能声称自然触发真实free失败 |
| P2-N0-03：晚返后下一dispatch未重核TTL | owner create最终active；parent metadata后新member open前active；child匹配后actual adopt前active，adopt/前pipe后下一pipe dup前active；最终active继续保留。过期保partial receipt/原owner，不能发新cap | 现并发revoke case不确定触发在途syscall，未写入伪装OS事实的fault callback。仍缺获批运行窗的定向TTL/晚返trace |
| P2-IF-01：test bootstrap/teardown丢fallback owner责任 | 两平台fixture均记node_owner并在register hook前固定；无论bind是否早退，fixture hook先实际close该原owner，非OK明确abort，不继续删fixture/顺利卸载。hook注册失败、失败owner adoption的close非OK也明确失败；已成功close可幂等复核，未知号码不重试 | 普通trusted native host仍须独立给image pin闭包；本源码未self-pin，不以测试进程abort/退出为release receipt |
| P3-N0-04：mac pipe多接纳socket | 收窄S_ISFIFO，不再S_ISSOCK；借用原FD不变，若dup后发现非FIFO，副本仍由原owner有限cleanup | 未运行socket或pipe反例，不扩网络资源面 |
| 平台C-1：kill声明依赖传递头 | mac fixture显式include signal.h | 消除源码声明依赖，尚非实际SDK编译成功 |

产品实际改动限 core、mac、Win、core_test 四件；ABI header、Node、TS owner、child_probe、TS test五件与首候选字节相同。全部九件新hash见source-text-check-r2.json，header仍13296B/fc3f7983d62b0ef4f5a3a056198c00a0b971d2ae722acc33bc6f61937ec8e172，public ABI未改，不要求替换首ABI过程ref。

本轮仅stdlib文本/hash/预处理条件平衡/空白检查与新主文档既有formatter；原两份TS未变，沿用同字节Prettier与TypeScript5.9.3 parseDiagnostics0证据，不冒称完整typecheck。未编译、运行测试、加载addon、进行native/FS/child实验、安装工具或借旧树依赖。所有运行反例留后续精确授权；三构建文件仍T03唯一writer，当前只docs，不实际采用。
