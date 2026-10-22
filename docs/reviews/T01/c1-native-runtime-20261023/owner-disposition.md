# C1 原生驱动修订收口

本轮只修验收驱动的有界进程核算与证据收口，原 52 项产品/测试及 observer 不变。原 run01 的 driver exit1、两次真实对话恢复和原进程 close0 分别保留，不改签原运行结果，也不推断当时缺失的新 ps 行。

独审首报告 10982 B／SHA256 `d6992db2f6c9825fe038d89080a0d8365057e7e94bbe51ec3098f1ee4fc544a5` 确证 helper 展示变化后无原 close 仍可结清的 P2。首版源码、原报告、修前反例失败和 check01 原件均保留。修订增加一项必要 guard；delta 独审 6522 B／SHA256 `07e34009fd4a044bfa55dba873598031ea0ff647f990d884873c8c25ba8ecc7c` 确认关闭，未发现新增阻断。两原件在本目录，不以静态审查代实际 native。

主线已读两独审全文、设计与完整 check02 回执，核对当前分类器及亲缘/原 ChildProcess 来源升级接线。17 组实际候选函数的受控验证通过；新源 41637 B／SHA256 `8c69a55ce6fdfa7b444f1b91211d42cc562753b1596fddc554406c3277624cdc` 的完整 `npm run check` 实际 exit0，1125 项 TS、2969 项 Python 通过，44 项跳过，源前后哈希一致。原始双流和首败已复制至本体根 `outputs/20261022_review_backlog/T01-C1-native-runtime-20261023/author-evidence/`。

本树另按原锁定官方链安装 Electron 44.9.0 darwin-arm64；ZIP SHA 等包内 checksums，主二进制等已校验 ZIP 成员，源/锁不变。安装与代码检查不证明实际恢复通过。新候选仍须在总控内部交接后执行原完整 Mac suite（沿既有 CI 的 12 轮 reload fixture、全部原断言和平台 skip）与新真实 native；同版指定双审、CI 和发布门保留。
