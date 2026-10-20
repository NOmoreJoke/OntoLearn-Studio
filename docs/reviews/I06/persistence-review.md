# I06 私有持久化独立审查

2026-10-21，内部只读 agent `/root/i06_design_review`。审查范围为 private-directory、ciphertext-repository、persistent-audit、credentials schema 复用、Electron factory 和相应故障测试。审查不修改共享文件、不启动本机 GUI；不是指定 GLM/MiniMax 双审，也不是完整 S3 通过。

## 已处置意见

| 发现 | 直接反例 / 影响 | 修正与复核 |
| --- | --- | --- |
| P1 排除目录检查与最终路径之间的竞态 | reviewer 在独占 tmp 中用 fs.lstat 边界注入切换祖先 alias，得到 `opened:true, createdInsideExcluded:true`；原 38 项测试未覆盖 | 原始路径所有祖先检查，非 root 拥有 symlink 拒绝；最终 canonical userData 创建私有命名空间前重新比对排除根；每次操作重新验证原始 userData 路径、目录 FD 身份和排除根。增加 ancestor alias 与运行中 export alias 改变反例。独立代码复核确认关闭。 |
| P2 scope 并集与持久审计上限不一致 | 两份材料各 256 个不同 scope，原网关可建立 512 个 scope 的拒绝 metadata；审计拒绝后错误变为 AUDIT_UNAVAILABLE 且没有拒绝记录 | 整个请求唯一 scope 并集在 metadata 建立前按 scopesSchema 限 256，超限 INVALID_INPUT，不截断来源。实际 receiver 测试断言零请求、无伪造不完整 audit。独立代码复核确认关闭。 |
| P2 并发准入和恢复硬上限混用 | 并发写者可同时在阈值下通过，然后合法新记录使之后整个恢复被错误视为损坏；失败请求审计还处于网关 pending 门外 | 每个 PrivateOperations 最大 32；准入阈值与恢复 11024 项硬界分离；opendir 逐项有界。恢复保留越准入线但仍在硬界内的合法历史，新写拒绝；不会删除证据或自动回收其他进程 pending。独立复核确认关闭。 |

reviewer 另建议 root 环境下 ancestor alias 反例必须明确 skip，不能直接 return 后记 passed，已改 `it.skipIf`。4097 反例是实际仓库文件/严格格式恢复，不是 4097 个真实平台解密凭据验证。

## 持久化设计意见及实施

- 没有 openat 原子目录相对操作，不能声称防御可控制同一 OS 账号或内核的攻击者；检查假设可信路径祖先，拒绝不安全 owner/mode，不自动 chmod。原始路径的别名信任与最终目录身份都检查。
- 新目录创建同步父目录，记录发布同步文件和目录。link 成功后同步失败仍失败关闭；保留可能已发布文件，恢复不等于前次调用已确认成功，绝不自动重放业务请求。
- 崩溃可在 pending 与 final 两个名字留下同一 inode；只承认匹配本目录 pending 的双链接，不读半写 pending，不误删活跃写者临时文件。读前 fstat/有界分配，拒绝 FIFO/device/不安全权限/外部硬链接。
- base64 严格往返；凭据密文绑定 ref/principal/version；audit 字段白名单、UUID、origin、时间、事件/原因配对。普通 SHA-256 仅损坏检测，不是同 UID 恶意篡改证明。
- 真实进程 SIGKILL 六个发布阶段各覆盖 credential/audit；文件故障注入与真实 loopback receiver 组合检查零请求。额外测试真实 5 秒 audit deadline，晚到完成后仍零外发。

最终只读代码复核回执：“三项修正已在代码层关闭，未发现新增阻断”；该轮没有重复大测试。根实际验证版本、完整命令/退出码、source/test/log hashes 另见本阶段 evidence；Linux 实际平台组合还需单独核对运行文件、镜像与 raw 的来源绑定。当前没有主进程正式注册、实际 Store/导出/窗口链证据，保持待验。

## 实际 Linux 组合证据复核

同一独立 reviewer 随后只读核对 [组合证据](platform/combination-linux-evidence.json)、probe/build/collector/runner、实际停止 r4 容器和 raw archive；没有启动或重跑。确认容器 `be974444…`、实际镜像 `419ab9c6…`、exit 0、network none；archive SHA `b8a37192936a32600f4b353d8c2f126f3cb872c961c6e2ff8fd4cd2af7da2361`、43 项 final raw 摘要、九个当前 TS source hash、实际 compiled JS 与脚本字节对应。实际六个 case 均为 Electron 44.9.0/browser、runAsNode false；corrupt/key-loss 均在 gnome_libsecret available=true 时拒绝，排除了“仅因后端不可用而通过”的替代解释。

直接阅读断言确认真实 factory→repo→audit→core/transport 链；第二 Electron 进程先在原 saved.port 监听再恢复，观察 100ms 零 POST。reviewer 最终回执：“组合探针与证据链复核通过，未发现新增阻断。”该结论限隔离 Linux arm64、明示观察窗及当前 source hashes，不扩大到实际窗口重连、Store/导出、macOS/Windows、签名升级/干净设备或指定双方审查。
