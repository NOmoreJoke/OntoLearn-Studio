# T10 报告文件服务独立内审

审查 agent：`/root/t10_private_review`，只读完整当前私有候选，重点为新增主进程文件发布服务及测试、首 LF 报告修复。未修改源码/测试、未启动 GUI，未重复主线全仓检查。

## 问题与处置

本轮实际发现的 3 项 P2 均已修复并读回关闭：

- 暂存文件原地改写但 inode 不变会发布错误内容、沿用旧 hash。现保留 `wx+` 句柄，发布前有界检查真实长度/完整字节和路径身份；补同长度及不同长度改写反例。
- 成功发布但清理 pending 后，重复保存错误报告 cleanup complete。现按实际暂存/句柄状态返回状态，清理重试采用单飞；补成功后 pending 重入及并发清理。
- post-link hook 抛 EEXIST 会被误判目标冲突，并允许第二次发布。现 link 成功返回立即固定 published，之后回调不改变提交事实；只有 link 自身拒绝才进入不明结果读回。补 post-link EEXIST 和实际 link 后注入 IO 回执失败。

目录 fsync 新测试首次未命中 macOS 规范化后的 `/private/var` 路径，属于故障构造错误。已按 realpath 识别句柄并断言注入恰好一次；保留首失败原件，修正例由主线与审查 agent 分别实际通过。

审查方实际运行 7 项相关命名回归、1 项 IO 丢确认、1 项目录 fsync，均通过；最终明确完整私有范围没有未关闭 P0/P1/P2。无 native picker、凭据投影、迁移/G.6 或同 UID 外部持续篡改保证；不替代指定双模型外审。

## 冻结读回哈希

| 文件                                          | SHA256                                                             |
| --------------------------------------------- | ------------------------------------------------------------------ |
| main/project-transfer/prepared-report-file.ts | `71e7359ed62f53d9b9c9ac0e3559f5993431e99a7f2527afe1916735824a0219` |
| tests/unit/t10-report-file.test.ts            | `7d0f42531fc7b8e512b075e2062c10c13161dd4059bbe7fe0996b60560f814e5` |
| renderer/src/transfer/report.ts               | `b5e508106bf6072f8b72f9c77cce9ab77d9e06bc91a926840ea2eaac379b8c05` |
| tests/fixtures/transfer/malicious-texts.json  | `b1b41d908b66559e4a3ee66e86d2065411613353765a27a1eec6cafe248d4e0f` |

读回时 HEAD 为 `a1c76d8a136519455267c00d08f63c68ecea0806`，上述新候选尚未提交；原 `internal-review.md` 对应前一版，只作为历史证据。
