# O 完整工程双指定审查：隔离 launch 准备

本候选只交付可审的launch输入、路径/权限映射和静态预检；没有GUI lease，未创建任何指定任务。产品/工具/expected仍固定77852d2，完整资料过程固定86df64a。六个不同历史工程保持分离，这次只准备O。

两实际workspace由总控detached创建，唯一setup owner原T05：

| 本方 | 实际workspace | 完整正文 bytes / SHA256 |
| --- | --- | --- |
| zcode | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-O-zcode-review-e15ce44` | 12897 / `887066cd54f48216215faa2096cebd5ca95e1f851f8c93569aa6beca800ff6fd` |
| minimax | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-O-minimax-review-e15ce44` | 12946 / `4f585bddefe6ba504c9b5786b3b2db29078e0d07fa262da3facaed73bb04abf1` |

本方输入位于workspace内`docs/reviews/T05/projection-R3-receiving/launch-O/`，本目录zcode/和minimax/是setup owner保留的字节镜像，不是模型报告共享面。每方完整正文含当前路径/执行补充及原O完整prompt逐字正文；原冻结prompt/manifest均未改。两方同scope契约与输入字节由launch-index.json、各自launch-input-manifest.json和preflight-setup.json引用。

实际AGENTS已由stage传播1056→15147/de15；owner只核对并保M，未覆盖或stage。规范快照与原历史指南分开保存，共同指南泛Goal新建/宽验证文字不覆盖本次精确setup。没有共享可变依赖、.venv、node_modules、scratch、raw或报告；本方report.md唯一本方可写，任何peer当前意见/自动状态/全局session元数据禁读。

每方实际运行的新静态预检exit0：914原tracked树metadata核同，过程958 tracked路径；149工程/authoring、原130及新44两份manifest合并290唯一受控文件current=固定Git=SHA。其余受控tracked变更只有保护AGENTS，index为空。实际stdout/stderr在本方raw及本目录镜像；stderr空，未执行产品、原oracle/正常47测试、原actual或模型probe。预检snapshot在原流文件落盘前产生，随后真实stdout/stderr/command三件追加到已声明本方raw写面，其最终字节另列manifest；不把调用前文件快照误称包括调用后新日志。

执行补充只为实际指定审查单列必要时的两个既有正常O命令：own stdlib47测试、build脚本`--check`只内存对照五件。setup没有运行它们，未变化不为调度强制重跑；不以SQLite/child等词泛禁原正常suite，也不借此扩到HOLD/被拒物理资源研究/未签native或I05产品/模型/实际collector。未提供的runtime依赖与137pending保持。

新元数据按本方真实路径/bytes/SHA记账，不删除、不用ignore制造全树冻结Pass。新工具只检查源/输入/本方文件，不检查模型taskID、设置或终态，也不读取模型任务DB。setupReady只属静态准备；真正创建前须根预检/短lease，之后正式设置/ID/完整受理与终态证据另存。

初次只读rg误指不存在的declared-allocation/README.md退出2，后定位固定脚本及实际独审报告；launch-index准确保留工具结果摘要。没有伪造这次探索的分离raw流。
