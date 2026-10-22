# T07 R3 actual-setup 后独立静态审查

结论：**本次精确 setup-only 执行记录、冻结边界及实际安装静态元数据核对通过；未发现 P1/P2 阻断或必需 setup 证据缺项。** 两角色各五条命令一次直接 child exit0，无重试或 operationalStop；这不是产品 build/check/test、环境运行 smoke、完整 EOF、指定双审或 Pair 门通过。原 hold 未解除，PROCESS_FAIL / Pair 0 与 M P2/P3 root 未决保持。

审查者 `/root/t07_dispatch_preflight_audit`，2026-10-23。这是本次唯一一次非作者 actual-setup 后审查，区别于先前准备审。只读 owner 本目录、明确两新根及其对应 runtime/setup、声明的依赖/缓存/元数据、固定 manifest/Git 与既有 Python pin；唯一新增本报告。不执行 npm、uv、安装、安装后工具、产品 import/test/build/probe、GUI/native，不重跑被拒目的，不改源/输入/历史/Goal，不提交。

## 1. 授权、执行器与命令来源

本目录 setup-authorization 原字节为 **10996 B**，SHA256 `2b6dada1ddd4f4270b94c7924a85095a5df14b50349744e91bb8a5673ef5566d`，与给定票和 execution-summary.authorization 相符。未沿票内 controller 私有路径另行读取，未扩搜任务或全局配置。已静态完整阅读 run-authorized-setup.py 和 inspect-installed-metadata.py，没有执行它们。

runner 将票中的精确 argv 直接交 `subprocess.Popen`，`shell=False`、`stdin=DEVNULL`、完整替换 env，不叠加宿主环境；分开独占新建 stdout/stderr，保存真实 child PID，再 `process.wait()` 取得整数返回码。记录与源码之间的退出因果链是直接子进程返回，不是管道尾 `$?`、日志文字或 isError=false。对本次实际未触发的超时/捕获边界，不宣称硬配额或整棵进程树隔离。

两角色按相同授权顺序各执行一次：

1. `/usr/local/bin/node --version`
2. `/usr/local/bin/npm --version`
3. `/Users/kyle/.local/bin/uv --version`
4. `/usr/local/bin/npm ci --ignore-scripts --no-audit --fund=false`
5. `/Users/kyle/.local/bin/uv sync --frozen --no-python-downloads`

十条 summary 记录与各 result.json、started.json 子集及 role-execution-receipt 对应一致；number/argv/cwd/env/shell/PID/UTC/真实 exit/无重试字段均逐项核对，五条顺序与票完全相同。runner PID 为 98363，十个 child PID 唯一。每条 realChildIntegerExit 为整数 0，operationalStop=null，版本均符票：node 24.15.0、npm 11.12.1、uv 0.11.12；Python 安装输出明确使用既有 3.12.12。

ZCode cwd：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-zcode-review-r3-f9a1157`。其五条 UTC 起止与 PID 为：

- 1：23:26:01.179253—23:26:01.382929，PID 98376。
- 2：23:26:01.739743—23:26:01.944293，PID 98383。
- 3：23:26:02.327507—23:26:02.531971，PID 98391。
- 4：23:26:02.932533—23:26:25.130161，PID 98398。
- 5：23:26:25.768129—23:26:38.894688，PID 98985。

MiniMax cwd：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-minimax-review-r3-f9a1157`。其五条 UTC 起止与 PID 为：

- 1：23:26:40.346267—23:26:40.551196，PID 99452。
- 2：23:26:41.009128—23:26:41.213009，PID 99460。
- 3：23:26:41.696940—23:26:41.901874，PID 99512。
- 4：23:26:42.379964—23:27:03.991487，PID 99563。
- 5：23:27:04.657619—23:27:10.517134，PID 191。

上述时间均为 **2026-10-22 UTC**，非本地时区；记录顺序、每命令 snapshot UTC、runner 总时段 23:26:00.510197—23:27:10.951904 连续一致。PID 大小无须单调，未据 PID 191 推断异常或追查其他进程。

## 2. 完整双流、首警告与准确结果口径

十条命令的 **20 份 stdout/stderr** 均已全文读至实际末尾，字节/hash 全符合 result/summary。首次综合展示夹杂大 metadata 被工具截断，随后单独完整展示了全部 20 流；没有用截断展示、head/tail 或程序内部 load 代替本项的可见全文。

每侧前三条 stdout 分别为 9/8/55 B，stderr 均 0 B。npm stdout 各 27 B，分别为 added 440 packages in 22s / 21s；stderr 各 **605 B**，完整保留 rimraf@2.6.3、inflight@1.0.6、glob@7.2.3 的 deprecated 警告。未为消警告改锁、升级包或重跑安装。

uv stdout 两侧均 0 B，stderr 分别 **1162/1167 B**：明确 Using CPython 3.12.12、创建本树 .venv、Building/Built ontolearn-engine、本次网络获取及 Installed 14 packages。**Building/Built 是本票准许的 uv sync 内本地 editable 依赖构建，不能省略，也不计为产品 build、engine:build、check 或业务运行通过。** 空 stdout 不是退出证明；退出依据是同一已封存 Popen/wait 记录。

安装链没有失败/重试记录。README 保留更早票路径短称不存在的读取错误；后继静态元数据比较首错另由 static-metadata-first-error.json 明确记录：真实工具 exit1、`KeyError: 'tomli'`，原因是把 setuptools/_vendor 的 dist-info 误归为顶层安装分发。其 stderr 是从实际工具返回逐字转录，文档已注明不是另捕获的原始子进程流。本审按顶层范围核实纠正，没有更改原 installed-metadata，也没有重跑安装或产品。该分类首错不是安装失败或自动审批拒绝，不被涂成“全程无首错”。

## 3. 每命令/全链冻结向量与固定身份

每角色有链前/链后及五条命令各 before/after，共 **12 份 snapshot**，两侧共 24 份。所有被 summary/result 引用的 snapshot bytes/SHA 均匹配；重算每份 rows 的 vectorSHA256，与其记录及本侧链基线一致。每份 **2289 行**为 root-source 1020、scratch-source 1020、required-input 236、input-sidecars 11、metadata-originals 2。

本审逐项核当前实际文件 bytes/SHA 与这些快照行相同；每条 before/after 的 files 也与本侧 chain-before 逐项相同。两侧向量分别为：

- Z：`d7ccaabc26b3130d39074756b7dde254297487d89e37b2ed2c506e14a9f679cf`。
- M：`edfc34002ed867400abca86dc3c7f920a0120c6316bcea8b7d2ee58831d5f11b`。

票列四项依赖输入 package.json/package-lock.json/pyproject.toml/uv.lock 的大小/hash 均与当前文件相同。当前 Git HEAD 仍 **detached `7fd17f93ebb4b68bac69faec15cb657e60c90729`**，tracked diff 唯一为既存 AGENTS M，index 无变更。guide、全部输入侧车、原 metadata、236 项材料及其历史报告原字节均未在采样边界发生变化；原“16 处历史空白”包含在这些字节 pin 内，没有格式化或清理历史。

原 R3 完整输入及 hash、旧 suffix、1020 源/纯源 scratch 均被向量保护；本次不重测旧 14，也不把源码未变化当作模型已全文阅读。236 项 actualReadCompleted 仍全 false。旧 PLAN_ONLY_NOT_EXECUTED 是此前阶段原件，保持不回写；本目录和 role-installed-facts 记录后来的获准实际 setup，二者时点没有混淆。

## 4. 精确 env、Python pin 与实际安装静态元数据

十条 environmentExactReplacement 均与票逐键相同。各自 HOME/TMP/TEMP/TMPDIR、XDG 三目录、npm/uv cache、UV_PROJECT_ENVIRONMENT 都指本侧 root/runtime；清单没有借旧可变缓存或带入宿主凭据。两个 npm 配置各自空字节且 mode0600，实际值与记录相符。npm registry 固定、ignore-scripts、skip Electron 下载，UV 固定现有 Python、downloads never/keyring disabled、link-mode copy；这不是离线安装声明。

给定 Python pin 49968 B，SHA256 `322572c8d73b308856d23a07f26afe9d65b9159f8174575e14fb23503a7f734e`，当前只读重算相同；本审没有执行该解释器。两 pyvenv.cfg 记录 base home 为该 pin 的 bin、CPython 3.12.12、include-system-site-packages=false。允许的共享基础解释器链接不等于共享可变 venv，也不宣称其操作系统权限不可写。

两侧 installed-metadata.json 的文件大小/hash 均符合 static-installed-isolation 引用；其中 regular 文件的当前大小/device/inode、全部已列 metadata/PTH/pyvenv/installed-lock 的 bytes/SHA 逐项相符。

npm 每侧 **438 份锁内安装包 package.json** 的名称/版本与文件内容一致，版本同时符合根 package-lock 与安装后的 node_modules/.package-lock。两 @ontolearn workspace 链接只指本侧 contracts/desktop；npm 原 stdout 的 440 含这两个 workspace，不能把 438 当作丢包。安装后 lock 有 442 个路径记录，另含 apps/desktop 与 packages/contracts 两个 workspace 目标路径记录，不将路径记录数混成包数。

Python 每侧递归保留 **105 份 metadata 文件**，其中顶层 site-packages/*.dist-info/METADATA 为 **14 个安装分发**，全部规范化名称/版本与 uv.lock 相同；另有 **12 份 setuptools vendored METADATA**。105 不是 105 个安装包，vendor 的 tomli 等不按顶层 uv 分发比对。METADATA/WHEEL/INSTALLER/RECORD/direct_url 等只读文件，不导入任何安装包。

editable direct_url 的本地 URL 仅绑定各自新根 packages/engine，editable=true；_editable_impl_ontolearn_engine.pth 仅指回本侧 packages/engine/src。另两 .pth 是已保留的 distutils-precedence 和 _virtualenv 启动声明，本审只读未执行。Python symlink 只解析到本树或票指定 base；npm symlink 全解析本树，无跨角色源绑定。

## 5. 物理隔离与 scratch 无依赖

每侧依赖 regular 文件 **15607 个**，当前 inode 与清单相符；两侧依赖普通 inode 交集为 0。已列 HOME/tmp/XDG/npm-cache/uv-cache/setup/node_modules/venv 共 20 个目录均为实目录、身份互异、非 symlink。

cache-isolation 另核：每侧 home/XDG 普通文件 0，tmp 533、npm-cache 843、uv-cache 2530，共 **3906 个唯一普通 inode**；每侧 19 个缓存 symlink 的当前 target/resolve 与记录相同且只回本侧 root/runtime。缓存普通 inode 的跨侧交集为 0；本审再合并依赖与缓存集合，跨侧交集仍为 0。未清理残留 tmp，也未访问全局缓存或其他任务。

两 scratch 下 node_modules/.venv 均仍不存在（含无 dangling link）；本侧 node_modules/electron/dist 与隔离 HOME 下 ms-playwright 浏览器目录均不存在。此项只限声明位置，不能泛化为全机没有浏览器、任何网络下载都未发生或整个依赖树已运行验收。

role-installed-facts 分别只记录本侧 facts，其 commandsOnce、executionReceipt/installedMetadata 身份与完整执行记录一致，14 顶层分发/12 vendor 分类正确。其 auditPending 是本报告生成前时点，未由本审回写；owner 汇总/票及本报告不自动成为未来模型可读 peer 材料。

## 6. 最终发现、证据边界与后继门

本 setup-only 静态审查没有发现真正缺失的命令回执、双流、冻结快照、锁/输入 pin 或安装隔离证据；无 P1/P2 阻断。静态元数据分类首错已被诚实保存和限域纠正，不需要再安装或试跑求绿。

结论依据是当前可核的原 Popen 代码、started/result/summary、完整双流、前后向量及实际文件元数据；本审不是独立现场进程监控，不把可复算封存记录提升成全机零写、任意时刻无瞬时改动、进程树硬隔离、registry 全链网络审计或业务可执行证明。快照证明给定采样边界与当前字节一致，元数据/版本一致也不替代包内容全量供应链审计或产品测试。

本票只授权十条 setup 命令，**没有解除 pytest/vitest/npm check 的原同目的 hold**。本审没有执行安装后 smoke、product/test/build/probe/DB/stdio/native/GUI，没有新任务或外发；原 PROCESS_FAIL/Pair 0、M 新 P2/P3 未决、Definition 完整身份守卫、原首错/EOF 缺口和所有父验收/CI/远端/发布门均保持。安装阶段通过只供 root 接收本次 setup 事实，不授权下一次运行、外审 START、push/PR 或 Goal 完成。
