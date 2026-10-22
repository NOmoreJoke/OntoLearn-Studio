# I05 输入生成器 Ruff 整理

结果：唯一产品改动为 `scripts/generate-i05-source-package-inputs.py`，178 项 Ruff 问题（174 E501；I001、E731、E743、F841 各一）清零。旧、新生成器分别在固定 `513db0056f312342a6791e2d4c7842f3726581f2` 的 detached 隔离副本默认执行一次，均 exit 0。两份 runtime JSON 与固定原输入、旧/新输出逐字节相同。

- Manifest：21202 bytes，SHA-256 `0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a`。
- Inputs：8205267 bytes，SHA-256 `47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa`。
- 417 observations、320 datasets、22 sources、原政策和固定历史输入来源保持不变。旧/新 stdout 同为 970 bytes、SHA-256 `4c7c73c8ec5c42979cf6998a47d84b82d85acade27bd2487d862045e6c18a456`；stderr 均为空。

旧脚本为 60354 bytes / `e58dd4efd1c64952b6555b98c65271fc7e82d7b99b198d848d69f5a7c9dcde0b`；新脚本为 75633 bytes / `c51a1a7f3085e79958022deda95d8a08792f3a95f7c4f1fb171d56196f3d2d26`。受审 proposal 与 applied 文件完全相同。

独立前审先于实施。除 Ruff 排序、布局、等值相邻 literal/f-string 拆分，必要语法整理只有：`I` 改 `iri_term`（26 次直接调用）、局部同表达式 lambda 改 def、去掉未读 `cases` 绑定但完整保留原位置 `json_source(path)` 求值、Path import 排序。受限逆转这四项后，整个模块 AST 与旧版完全相同；15 条注释原样。函数名称/位置等反射属性不作全观察等价主张。独立审查报告及程序、实际结果已归档。

受控旧树为 `.worktrees/I05-input-generator-golden-old`，新树为 `.worktrees/I05-input-generator-golden-new`。生成器仅用标准库与固定本地 `git show ref:path`，无语义 collector、CLI parity、数据库、业务网络或物理实验。两个受控树各运行一次，作者树未运行生成器，原冻结 JSON 未改。新树 audit source manifest 只有 generator 自身 bytes/SHA 改变，其他 JSON 内容相同；生成报告全字节相同。`--check` 本身会核四件输出，其中 audit manifest 含 generator 自身身份，因此未以旧 audit 元数据冒称新 generator `--check` 通过。

应用后实际运行自有 Ruff 0.17.1 的 check 与 format --check，均 exit 0。自有 `.venv`、cache、tmp 隔离；Python 固定 3.12。收据保留完整 argv、cwd、start/end、实际 exit 与分流原字节；早期 baseline/proposal 失败也完整保留。原始流、proposal、patch 使用确定性 gzip 入库，`lossless-archive-map.json` 记录逻辑路径、原件路径、压缩和解压身份，逐个验证无损；这样保留精确证据而不修剪 patch 上下文空白。AGENTS 15147 bytes / `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` 仅作为未暂存 overlay 保留。

边界：此线未执行全仓 check、pytest、语义 parity、桌面或生产验证。黄金复现证明本次输入生成输出不变；不替代产品行为、历史功能或物理实验验收。四个历史工具是否保留冻结例外由总控独立处理，未扩大为本生成器例外。
