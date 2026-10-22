# I05 generator style 独立实施与黄金复核

结论：Pass。已实施产品与前审冻结候选逐字节相同，178 项 Ruff 清零的实际证据完整；真实旧/新生成的两件 runtime JSON 均精确复现原冻结字节。未发现需要阻断此唯一 generator style 修改的问题。本结论不扩展为语义、产品、CLI、数据库、生产或业务执行通过。

本报告承接 proposal-independent-review.md；前审的“运行待验”状态由本报告所述实际文件与收据复核完成。审查者未重跑 generator、Ruff、formatter、pytest 或产品；只执行 pinned Python 3.12 标准库只读检查及固定 Git 读取，所有新写入均限审查者 exclusive 输出目录。

产品 scripts/generate-i05-source-package-inputs.py：author 与 new golden 树均为 75633 bytes / c51a1a7f3085e79958022deda95d8a08792f3a95f7c4f1fb171d56196f3d2d26，逐字节等于已批准 proposal；old golden 树为 60354 bytes / e58dd4efd1c64952b6555b98c65271fc7e82d7b99b198d848d69f5a7c9dcde0b，等于 fixed 513。前审全 AST 受限四项逆转证明直接适用于已实施字节，无需重复运行生成器。

真实生成证据：old/new 均在各自 .worktrees/I05-input-generator-golden-old、.worktrees/I05-input-generator-golden-new 受控副本；独立读取 Git 确认两者 HEAD 都是 detached 513db0056f312342a6791e2d4c7842f3726581f2；AGENTS overlay 两者均为 15147 bytes / de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4。实际命令均为 `/Users/kyle/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12 scripts/generate-i05-source-package-inputs.py`，默认模式，PYTHONDONTWRITEBYTECODE=1。作者实际 old 2026-10-22T18:47:37.756288+00:00 至 18:47:38.935442+00:00、new 18:49:47.072788+00:00 至 18:49:48.302456+00:00，均 exit 0。start/end 为原 UTC 收据，不回填为本地日期。两者 stdout 970 bytes / 4c7c73c8ec5c42979cf6998a47d84b82d85acade27bd2487d862045e6c18a456，逐字节相同，JSON mode=generate；stderr 均 0 bytes。

直接读取 fixed513 Git 原件、author 工作树原冻结文件、old/new 树实际生成文件，四方 bytes 全等：

- i05-source-package-parity-manifest.json：21202 bytes / 0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a。
- i05-source-package-parity-inputs.json：8205267 bytes / 47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa。

另用标准库 JSON 读取确认 supplierRef=6891a5842302859a531cf82767c5a482417bc274、observations=417、datasets=320，manifest counts 与实际生成 stdout counts 相同。未改 oracle、删 case 或替换供应来源。

审计输出：old/new inputs-source-manifest.json 均 22513 bytes，SHA 分别为 781178acc6eaa6ec31c0ad44ddced7096a7b7dc7c8a69b73af5540247daffea3、9ea444f1492e31b8928a649e9da8aadcaa8096a4795ba8481117620f5bc411e7；唯一结构差异是 generator 的真实 bytes/SHA，path 相同。移除该字段后所有 JSON 数据结构相同；old 审计输出也等于 fixed513 与 author 原件。input-generation-report.md 四方逐字节相同，20983 bytes / fbd20baad3e0608d304d8dc9536cf2d335500c6061a2cd5481f9037b3deac847。作者未执行 --check，未拿旧审计文档伪称新脚本 --check 通过；本任务以隔离默认生成实际输出核黄金，现有 --check 行为和接口没有新 bypass。

实施后 Ruff check 与 format --check 收据实际 exit 0，原 stdout 分别恰 []（2 bytes）与 `1 file already formatted\n`（25 bytes），stderr 均空。独立核验完整 argv、时间和每个 raw stream 的 bytes/SHA，并直接核实际产品候选身份。旧 baseline 178 项与首轮候选 37 项失败边界仍保留，未抹去。

归档复核：作者将 raw / patch / proposal 等确定性 gzip 归档并保留完整原件；本审查独立对 lossless-archive-map.json 全 32 项读取压缩字节、核 archive bytes/SHA、mtime=0、解压 bytes/SHA，再与 originalPreservedAt 实际原件逐字节比较，全部通过。原始 stream 不 trim、不重写；收据内 logical raw 路径由映射解析。前审 checker 与收据是前审时点冻结记录，产品实施后其“产品仍旧版”断言有意不再成立，不应为凑绿重跑或改写它。

独立 applied-review-check.py 实际 2026-10-22T18:51:09.607781+00:00 至 18:51:09.865657+00:00，exit 0；stdout 6538 bytes / 76467e736c306f828aef8bb73ba7838a7641a415db9e40860b91d22a0e033dff，stderr 空。检查源码、完整未 trim 分流和命令收据随本目录 manifest 固化。最后暂存精确路径、提交与集成仍由作者及 root 执行，不属于本审查者写面。
