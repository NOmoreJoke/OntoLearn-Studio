# 准备合同信号状态意见处置

2026-10-22。首审固定 b59239f9c1ec2774c7922f95dfc67db4dc8754e8，原文另存且不改写。

独审指出一项文案 P2：最小环境及 sole-waiter 声明不能排除继承 SIGCHLD=SIG_IGN、SA_NOCLDWAIT 或阻塞 mask；Popen restore_signals=True 也不保证复位 SIGCHLD。若 child 被 OS 自动回收，native waitpid 的 ECHILD 与保留旧 PID 会使失败清理身份失去依据。

已在 plan.md 和 execution-plan.json 的 preExecSignals 补明确执行前置：只在本次新 core 子进程 pre-exec 设置 SIGCHLD=SIG_DFL、无 SA_NOCLDWAIT、SIGTERM=SIG_DFL，清空继承 signal mask；probe 继承且无外部 reaper。现有 executor 必须先证明能够落实，否则维持 BLOCKED。没有修改 host 或全 UID 信号配置，也没有开发或试跑新 runner。

这是准备文案修正，九件产品/测试源码仍逐字匹配 b59239f；不是信号设置已执行、运行安全已验证或批准运行。独立点读跟进另存，不把首审发现删除后改称首审无问题。
