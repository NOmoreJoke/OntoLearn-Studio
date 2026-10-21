# T04 原始日志恢复

归档与索引是固定产品候选 `554ec89844ae5e8efcc4ac0d4f7e21d955a4b6a6`、已审计流程 HEAD `19ef25259e6304949cef4a1993b006de11fb885b` 的补充证据。它们将原本 ignored 的 37 份日志无损纳入 Git；不代表重新测试或父功能验收。

在包含本补证提交的 checkout 中，读取 `raw-logs-554ec89.index.json` 并先核对 `archive.bytes` 与 `archive.sha256`。使用 Python 标准库 `tarfile.open(..., "r:gz")` 遍历全部普通文件，以 `extractfile(member).read()` 读取原始字节；将每个名称、字节数、SHA-256 与索引 `members` 一一比较，确认无重复、缺失或额外成员。37 项总原始字节应为 61602。需要落盘时，在新的空目录中按索引成员名逐文件写入，保留现有原件。

Git 本身也保留归档与索引：可用 `git show <补证提交>:docs/reviews/T04/evidence/raw-logs-554ec89.tar.gz` 读取归档原始字节，不能经文本解码或文本编辑后再验证。索引的 `sourceSummaries` 指向旧、新三份汇总及其固定提交与实际哈希；首次失败日志、空日志和重复内容均按各自文件名保留。

本次归档创建后已重新打开，37 项逐成员读回，与原件逐字节、大小和 SHA-256 全等；全部原件未删除或修改。提交后还会直接读取 Git blob 重新验证归档和索引，以确认脱离 ignored 原日志仍可恢复。没有重跑产品测试、构建或外审。
