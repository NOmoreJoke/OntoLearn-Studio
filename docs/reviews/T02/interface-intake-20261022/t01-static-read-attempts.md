# T01 接口静态核验尝试记录

仅是 T02 自己的取件/核验脚本尝试，不是供方或产品测试失败。没有 import/执行产品、测试、SQL/DB/native 或模型；以下摘要和错误片段由实际工具输出转存。

1. 初次按消息中的工作输出路径读取固定 a1a66bde，Git exit 128：`fatal: path 'outputs/20261022_review_backlog/T01-T02-interface-B/interface-B-for-T02.md' does not exist in 'a1a66bde3e8078b85d5ea4d48909b96ce6417705'`。随后通过该 ref 的 ls-tree 找到 docs/reviews 下实际归档；主文大小/SHA 与交接值相同。
2. cat-file --batch 的管道输入尝试未返回。只读 ps 确认本任务 Python PID38578 的唯一 Git 子进程 PID38615、PPID38578、命令 Git；只对该子进程发 SIGTERM，未清理其他进程。原脚本 exit 1，原错误末行：`subprocess.CalledProcessError: Command '['git', '-C', '/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes', 'cat-file', '--batch']' died with <Signals.SIGTERM: 15>.`。没有将中断计为通过；未证明卡顿的底层原因。改用临时文件作为 batch stdin，并加 30 秒子进程 timeout 后，实际读取返回。
3. 下一次 exit 1：`assert len(delta)==identity['fullProductTestDeltaCount']==52`，`AssertionError`。核实供方清单是 52 项产品/测试，base→product 完整差异是 59 项（另 7 docs）；错误在本方脚本分类假设。改为核 52 个非 docs 路径与对应完整 Git 身份，另记 59/7，不修改供方清单。
4. 下一次 exit 1：`for name,value in typed['canonicalSchemas'].items():assert schema['$defs'][name]==value`，`AssertionError`。供方每项是 `{line, schema}` 包装；错误在本方比较对象。改为与 value['schema'] 比较，没有修改供方 schema 或数据。
5. 最终校正脚本真实 exit 0，原输出：`{"payloads": 26, "fullSource": 825, "totalBytes": 14253801, "delta": 52, "raw": 14, "schemas": 21, "allMatched": true}`。最终核对范围及固定 ref/bytes/SHA 见 t01-source-readback.json；825 身份核验不是 825 文件全部语义审查。

随后仅静态读取关键事务/确认/提交、metadata 和 references 函数体，更新依赖矩阵；没有运行这些函数。原供方独审首 P2/修正与本方取件脚本问题分开保留，不能混计。
