# 准备过程异常与纠正

首个打包命令 exit1：`git show 5f910b52c69d86a1076b2032e5d3c63e715947f3:docs/architecture/m0-review-and-update-plan-2026-10-19.md` 返回 `fatal: path ... does not exist in ...`（函数 subprocess.CalledProcessError，status128）。此错误只发生于过程打包，未运行产品或测试。已保留已写出的patch/guidance，没有伪称首次成功。

随后只读git ls-tree发现批准base真实路径为 `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`，改用该固定Git原件完成包装；没有补造旧路径、修改规范或产品。最终文件与归档逐项核验另见preparation-verification.json和后续独立文档核验。

文档格式首个 `prettier --check` 使用默认ignore，不能作为本目录已检查证明。随后显式 `--ignore-path /dev/null --check` exit1，三份新文件 historical-issues.md、minimax-frozen-prompt.md、zcode-frozen-prompt.md 有格式warning。仅格式化这三份新过程文件；原guidance快照、JSONL原文、归档和产品均不修改。之后显式复查。

独立静态字节核验：75个archive成员逐项大小/SHA与Git/原文件一致；9条原始final逐行等原session字节；14实现/测试/fixture均等f9；完整binary diff逐字一致。25项中24项物理等f9，唯一差异是后继流程status.md，按固定ref审查，不视为产品变化。
