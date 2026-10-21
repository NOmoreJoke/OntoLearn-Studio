# task-runtime.test.ts 单次写窗口：供方意见

**I05可为 T01 提供这个精确文件的一次写窗口，但当前没有授予写权。** 必须先由根总控实际读完并审过最小补丁，再登记基线、补丁SHA、开始时点、结束条件和唯一writer；当前仅核实供方状态，不改测试或产品。

当前维护者仍为I05。产品文件交接及T01七份专属测试授权没有转移旧共享测试。现场 donor HEAD 为 `81ab29ccda73795718c387cfe4c9795186609496`；批准5f、产品1a、冻结C4及现场文件完整相同：26406 bytes，Git blob `8bc5fe2141d409f1157d7153efd13a342f71fae1`，SHA-256 `2f8f8c1fd34cc449b2cca6ff2a05dcbed43b47560f97fcc039810233f2dfee50`。该path的status、staged/unstaged diff均为空，无WIP；末次Git变更为d83442e的历史提交，不等于当前owner变更。

已全文读取原8个测试。前三项复用disconnectRuntime，399–435行一带反射session/starts、pending与child用于真实退出/重启观察。可以将这部分编排迁到测试自持的真实子进程句柄和受支持生命周期；不回退产品运行时私有字段，不加公开凭据/test hook绕过隔离，也不以mock成功或固定等待替代真实恢复。

全部原恢复、幂等、单job/claim、原子marker、已提交轮次、旧session失效/新session与PID、无重复create/cancel及旧unsubscribe、自动恢复一次/三次真实失败后offline/显式恢复第五次启动、恢复view/generation等断言必须保留。其余五测试与所有其他旧测试不在窗口范围；不得删断言、改预期、时限或skip掩盖回归。

最新供方关联证据是固定40c的完整check：16个TS文件/672测试及1847Python通过；原日志SHA `b16e34efc8fad814639dfc4443ca3be0cbc47125450f56dfeb8ad40bec502dce`。它没有单独本file终态收据，本次未复测。T01新实现3失败/其余1024通过及private原因来自根通知，不冒称I05在T01树亲测，也不归给冻结C4。

窗口若获批，仅T01在其独立树修改此文件，I05保持只读。根收回实际HEAD/SHA/diff/验证结果并登记关闭及后续唯一owner；不自动扩成永久责任或其他测试写权。修改后的T01测试不进入旧523候选、不得沿用旧绿背书；C4的1284冻结文件、205跟踪执行输入及原件保持不变，原双审/发布门保留。

完整机器收据及原文件快照同目录。此意见没有执行产品/测试/GUI，不授权修改未见补丁，不改变根的逐项审批条件。
