# B-M 实施中静态前置检查

本记录保存独立 agent `/root/i06_interface_docs` 在实施期间已发给 root 的静态建议，不是冻结候选审查或最终通过结论。只读模块、采用的 A 接口及本轮授权；没有执行产品、测试、构建、GUI、native、网络或凭据操作，没有修改产品或测试。

初读来源为本树 `apps/desktop/src/main/security/private-resource-owner.ts`，SHA256 `ad611b4a99b0e67b7d67d805fd920094d5d09e69e0ab1ad68ffcd6839b4a2b23`。以下位置和反例绑定该实施中快照，不宣称对应后续可变模块。采用的 A 原件保持只读。本轮授权为 `I06-real-private-metadata-BM-implementation-authorization.md`，7201B，SHA256 `feb2f93a2cbc6722b3f7ba61fb4671d34d6f44caeeda2548971bb3a04ecd1b72`；已全文读回 AGENTS `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759` 与共同指南 `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`。

## 原静态反例与建议

1. **mutation 屏障不能由逻辑取消释放。** 初读 `cancel()`（约 619–629 行）清空 `mutation`。轨迹为 `beginMutation()` 成功、实际外部 mutation 尚未结束、调用 `cancel()`、再调用 `observe()`：当 `running` 为空时，新观察可进入，而原 token 的 `endMutation()` 已变 stale。建议取消只撤销观察，精确 mutation token 保留到实际结束；`close()` 也不能把未结束 mutation 当作已闭合。此处仅检查未来 writer 握手机制，不声称当前生产 writer 已接线。
2. **unknown throw 分类本身必须不抛出。** 初读 `reasonOf` / `missing`（102–113 行）对 unknown throw 使用 `instanceof` 和 `Object.getOwnPropertyDescriptor`。Proxy 的 prototype/descriptor trap 可再次抛出，使 scan 的 catch 自身失败；原 `void p.then(...)` 又没有拒绝清理，可能留下粘住的 `running` 和拒绝。建议内部 failure 用私有 WeakMap/Set 识别固定原因，外部错误码检查完整包在 catch 内；任意未知抛出归为固定 `io`，不读出或回传原异常。
3. **最终投影须重新核整轮 TTL / generation。** 初读 scan 在最终 `check()` 后执行 `project(...)`，同步构造列表、四次 reserve 和四次观察 capture 后，直接发布状态。A 各 observation ticket 的 5 秒起点晚于整轮 scan，不能替代供方整轮 deadline。建议投影后再次核截止与代次；过期保留已知 facts、返回 unknown，不能发布 observed。此为静态可触发条件，未实际运行慢 IO 或时钟注入测试。
4. **Node `lstat→opendir` 没有原子 nofollow 保证。** 已检查为目录后、按同一路径 `opendir` 前，目录可能被替换为指向根外的 symlink。`opendir` 可以 follow；之后祖先/根 stats 不一致只能降为 unknown，不能撤回已经枚举的目标 metadata。当前 Node 原语没有这里所需的句柄身份和原子 NOFOLLOW 证明。此竞态尚未解决；B-M 仅在受控临时目录观察 metadata，所有证据仍为 `node-observed-unfenced`，不授予生产内容 IO。不得把双 stats 一致写成竞态下从未 follow，也不为此自行扩展 native。
5. **5 秒检查不是系统调用 timeout。** 初读的时限检查发生在 await 前后。若 `lstat` / `opendir` / `read` 一直未 settle，原 observe Promise 与等待它的 close 可继续 pending；`cancel()` 的同步视图可以返回，但真实槽仍须保留。这不是提前释放漏洞。如果 API 要承诺 5 秒内给出逻辑 unknown，需另行实现只影响逻辑结果、不会释放 underlying 槽的机制；否则文档应明确“操作返还后核 deadline”，不能宣称 Node 调用已超时或终止。

## 静态符合项

- 固定 Node 调用点先预留槽，再启动实际操作；active 在 underlying `finally` 才减少。
- Dir 跨 `read` 持有 acquire slot，直到实际 `close` 成功；释放不确定保留 unknown，不以包装结果清零。
- 四角色列表全部 reserve 后才取整轮 revision，随后投影观察；不补造其他应用角色。
- 同址旧新 inode 分别保留在供方事实中；原 A 的 locationKey 唯一约束拒绝该映射时，供方降为 unknown，不丢旧事实或改 A 取绿。

以上为实施中逐入口静态判断，不替代真实临时目录、受控 Promise、错误注入、采用范围及冻结候选的正式独立审查。

## 修订与关闭责任

保存本记录时，root 已报告修订 mutation 保留、WeakMap 加 catch 的错误分类及投影后 TTL 检查。本记录没有重读这些未冻结修订，没有运行其验证，也不据此把原问题关闭。修订是否满足反例以及最终测试结果，由 root 的正式独立审查和实际证据逐项确认。Node 原子 nofollow 缺口及“5 秒并非系统调用 timeout”的边界继续保留。
