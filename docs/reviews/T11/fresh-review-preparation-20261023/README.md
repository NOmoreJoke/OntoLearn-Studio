# T11 036 全新双指定审查准备

本目录只准备，不创建或续接应用任务。固定受审候选/两个review HEAD均为 `036d7172ddba8502fe81e6e7ce375ce09ef7fa1c`，受验实现/测试 `33894063fcf17bc865f4c91556a8ca01845812e7`，repair base `692077da9754a303915798789b7b0c5b4f609125`、原工程base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；新准备提交仅是process，不改候选036。完整固定交接/主报告/内审的精确路径、字节和hash在handoff-manifest.json。

两独立实际树分别为 `.worktrees/T11-zcode-review-036d7172`、`.worktrees/T11-minimax-review-036d7172`（绝对路径见review-roots.json），detached；各自node_modules/.venv/tmp/raw/report/metadata/input，不共享可变环境。实际离线 `npm ci --offline --ignore-scripts --no-audit --no-fund` 和 `UV_OFFLINE=1 uv sync --frozen` 均exit0，只是环境setup，不是测试/构建/产品通过。四份日志留各自raw，并复制本目录（索引固定）。没有读取secret/auth配置、网络探测、Electron postinstall、产品/native/collector/API/GUI，也没重跑已通过检查。

每树892个受控Git blob与实体核hash，891个等036，唯一差异为最新AGENTS政策 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，保持未暂存。固定873 Git对象存在。source-setup逐文件身份在各自metadata和本目录同名副本；自己的input只有本方提示、共同正文和完整handoff manifest，没有本轮peer提示或收据。setup/app metadata真实生长不删除、不新ignore求绿。

两份提示只角色封面不同，共同正文25780B完全相同；包含原25全工程、原8流程、本轮23变化和历史两份完整报告/18矩阵等，共56个必读固定文件，不做18项delta审查。原57P0、1000轮/每轮1000动作、两collector、全部恢复/迁移/真人/模型/签名/渠道及CI/合并门保留。允许按疑点使用既有普通检查权，不泛禁child/临时SQLite，不机械重跑无变化检查；不扩外部HOLD或新native/资源/API票。只读自己本轮receipt，明确禁止peer本轮prompt/receipt/report/state/metadata，即使列在Git或index；范围等价由owner事前核。旧报告是明确列出的上一轮历史，允许全文处置。

当前根通知T05唯一GUI，其后helper e93及其他ready队列；036内handoff提T03是当时历史。本线只有准备，不表示根已接收、应用任务已创建、真实model/effort/permission已读回、新版Pass、双审通过或发布授权。待根接收固定准备清单并安排GUI交接后，分别创建全新GLM-5.3/max/yolo、M3.1-Flash/xhigh/bypassPermissions完整任务，不复用任何旧completed会话。不能用旧Z通过或owner109/739/1052替代新审。
