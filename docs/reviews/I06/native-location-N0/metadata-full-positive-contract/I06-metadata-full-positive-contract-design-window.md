# I06 N0：完整正例路线与对象级ACL合同设计

2026-10-22。继续原I06同一Goal/树/分支，基准904cc2675c37387621954bb5a39a055c09d492b3。本窗口仅授权必要静态合同/完整设计与独立窄审，不授产品/测试改动、API/ACL/FS/进程探针、编译或运行。

## 已核验的前提

总控全文读取独立前提审查I06-metadata-contract-premise-independent-review.md（12583B/SHA256 855e591907422e3d9c1ef98510d230261e4f126a4cfd0d6c982e51375f221eae），直接核9ff原方案、1f3威胁边界、fa1a首源、1217 ABI和正例fixture的固定字节/关键行段，见I06-controller-metadata-contract-premise-direct-proof.json。

- N0是受控held-object观察，production_admission始终0，不是持续namespace/ACL许可，不抵御任意恶意同UID进程。普通替换/alias/自有并发/撤销/关闭边界不降低。
- 原合同没有要求metadata和ACL必须由单一原子调用取得；原实现也是多调用。所需为同held对象与自有变更协调、明确观察边界，不能据数值相等声称OS lease、排除ABA或持续稳定。
- UUID presence是003后实现见证，可用有充分依据的技术路线替代，不是用户/ABI必需字段。不得只删门，吞NULL/ENOENT或把query成功/缺位/零占位当absence。
- 原合同未要求installed libSystem与公开commit逐字同源。若正式接口语义足够，可依据合同设计并在固定OS/runtime/产物上真实验证；公开实现分支本身仍不能当跨版本合同。
- 满足既定策略的受控空ACL正例必须成功。OS不必保留某一种empty表征；不能强造P1/P2，也不能用所有正例UNSUPPORTED完成阶段。此为完整原目标，不限定到罕见返回header求绿。

## 本次交付

1. 冻结N0观察/装配合同：trusted harness保持live borrowed对象及哪些权限/ACL稳定性，自有mutation如何和native gate协调，root/member实际身份检查与异常收口如何保留；明确外部未知窗口及生产拒绝。不要发明新的OS锁或默加原子快照条件。
2. 对实际held对象给出ACL状态表：API成功/失败、缺属性、明确NOACL、有效empty、任意ACE、畸形/矛盾、释放未知。每一结论标明正式语义、特定公开实现或待实测；尤其解释既有acl_init(0)+成功set的受控正例为何存在可证明的接纳路线。先补完整路线，不批准只在可能header上成功的条件解析器。
3. 有必要时只补当前已知filesec/fstatx、acl_get_fd_np及fgetattrlist相关的精确官方合同/目标版本适用依据，不大搜或枚举无关API。旧URL不可访问不等于合同不存在；正确来源只采用官方文档/公开发行源。不要因某个声明宏自动推成不可用或跨版本安全，精确说明实际ABI/目标绑定。只保必要固定摘录和来源指纹，不复制完整系统主体。
4. 若缺的是实际表征且正式合同已允许判断，可另提一次有限、会改变采用/放弃路线的受控响应实测设计：列各结果对应下一动作、精确调用/字段/输出/资源/ownership/失败停止边界；不能是仅两布尔诊断。本窗口不授该实测，也不预建运行目录或新record。
5. 提交明确可执行结论：有完整可审查路线时列最小writer、解析/ownership/预算/错误及必要正反验收；若仍不足，精确指出对象级语义/目标证据缺项和进一步工作是否能内部完成。不得声称接口普遍不存在、永久缩减功能，或把安全拒绝当完整可用性。

仅新增本阶段设计/证据/独立窄审过程文件，固定纯过程ref及有限manifest交root。复杂设计由独立agent审新合同，不重审旧17KB算法、构建/供应史或已收件18文件；无产品变化不跑npm/旧测试。T03继续冻结，不授第七构建。原源码/失败归档/AGENTS/WIP不改，003/004失败与drain/残留未知不追认。

拒绝的SQLite/heap/OS资源接口分析线继续停止，本窗口不得改述重开。不做DB、GUI、凭据/外发数据/付费、push/PR/merge或Goal变更。物理/内部资源硬界、目标双OS、完整父功能、指定同版外审/CI/真人/远端及T01损坏保护HOLD均未关闭。
