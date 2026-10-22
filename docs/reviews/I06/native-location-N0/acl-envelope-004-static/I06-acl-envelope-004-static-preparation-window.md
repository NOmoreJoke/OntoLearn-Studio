# I06 004 envelope见证失败：静态后继准备

2026-10-22。004失败归档已由总控受限接受，见I06-execution004-failure-root-closure.md；这不是运行通过。原I06从固定0c20804537cca79578e0344870b4a3f24eb76998继续同一树/分支/Goal。本窗口仅新增独立设计/审查过程文件，实际实现、编译、诊断或API调用待固定方案受件后另授。

## 本次唯一工作

针对第一个fixture的acl-witness-envelope合取失败，区分测试见证假设与生产metadata完整性要求。按固定源码及已有官方API合同/公开实现，提出最小可审查后继：

1. 说明UUID/GRPUUID presence与完整fstatx响应、ACL是否存在之间哪些关系有官方保证，哪些仅公开实现假设，哪些installed行为未知。不得把公开Libc当本机身份或把本轮合取失败认定为具体哪项/短envelope/权限/平台根因。
2. 原同FD/fresh、OWNER/GROUP/MODE一致安全门、query返回码和ACL ownership/error边界不因求绿降低。若认为UUID presence不是合法完整性门，必须给出独立、可审核的替代完整性证据及其未知边界；只删门或NULL/ENOENT放行不可接受。若无法证明，明确组件继续fail closed，不能设计伪成功。
3. 先判断是否仅需固定有限诊断，或已有足够静态证据支持最小修复。列唯一writer、精确输出/资源/错误变化、必要反例和验收；诊断仅固定阶段/布尔/有限错误，不输出路径/UID/UUID/FD/owner，不引入额外API/重复查询/无界流。保持旧失败原件和运行控制算法，后继运行仍需单独窗口。
4. 若需要新增SDK头/链接依赖/重新编译，由T03唯一构建owner后续核增量预算。当前不构建、不改锁或借用他线可变环境。内部heap/系统调用/wall硬界、allocator/get/free异常及未知ownership不能由正反例关闭。

## 证据与交付

仅阅读固定相关源码/已有头文件和必要的官方文档/公开源，静态数据核对；不运行native/addon/ACL/FS/DB/进程探针，不扫描/tmp或旧fixture、清理/kill，不重跑004或前轮，不修改产品/tests/依赖/构建锁。被拒SQLite/资源接口线继续停止，与本次ACL准备无关；不得借此改述重开。无GUI、外部审查任务、付费、push/PR/merge或Goal变更。

新增最小方案和独立agent窄审，按固定source/bytes/hash引用，可作一次局部修订关闭设计问题；无需重新大审旧8750源码、旧17KB算法、旧构建/供应史。固定纯过程ref、有限manifest、保护状态与未解决门交root；无产品变化不重复npm/测试。若同一实体接口不能静态解决，准确给出缺少的证据，不无限更换方案或扩大读取。
