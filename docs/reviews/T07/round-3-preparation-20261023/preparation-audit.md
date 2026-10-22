# T07 R3 一次内部非作者准备审查

结论：**仅 R3 准备静态范围通过；未发现需阻断准备交 root/controller 预检的 P1/P2 实质错误，未发现必读材料缺失。** 这不是工程 Pass、环境已安装/可执行、验证 hold 解除或指定 Pair 门通过。新任务/发送均为 0，GUI RELEASED，无 START；R1/R2 PROCESS_FAIL、Pair 0、原 M 新 P2/P3 的 root 未决状态保持。

审查者 `/root/t07_dispatch_preflight_audit`，2026-10-23。按根要求完成本次一次独立准备审；未创建外部任务、发消息或等待外审。依据当前已读 AGENTS、Audit and Verify 技能，读取 owner 新准备目录及两明确新根和各自已列 runtime 输入/源副本/缓存；必要只读固定 Git B/P/R 与 owner AGENTS。未访问旧 review roots、原应用/session/global 数据、其他任务、实时 controller 或 peer。仅新增本报告；没有改源、测试、锁、合同、旧原件、Goal，没有 stage/commit/push。

## 1. 固定身份、完整输入与确定性重建

固定 B=`5f910b52c69d86a1076b2032e5d3c63e715947f3`，P=`f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3`，R=`7fd17f93ebb4b68bac69faec15cb657e60c90729`。两新树均实际 detached R，B→P→R 祖先关系成立；P→R 在 apps/packages/tests/package.json/package-lock.json/pyproject.toml/uv.lock 无差异。本项是新副本静态来源核查，不是旧 14 项重测或旧 native 重取。

- ZCode 新根：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-zcode-review-r3-f9a1157`；runtime 为该绝对根后加 `.runtime`。
- MiniMax 新根：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-minimax-review-r3-f9a1157`；runtime 同理。
- 两 scratch 均为本角色 runtime 的 `scratch/probe-copy`，是未执行、无依赖的纯源副本。

Z 输入 **392679 B / 3509 LF**，SHA256 `0baeae0e98fd6642659365fa08420c4279f40c4071415283e3c0433729da9580`；M 输入 **392835 B / 3509 LF**，SHA256 `a56ef772b34bf51dd1e38fa9bfd9a326ee7d0f223f47b644e3adee085f47aba0`。每份 owner 与角色 `round-3-input/full-input.txt` 逐字节一致，符合各 manifest。

只静态阅读 build-materials.py，**未执行该脚本**。另用标准库在内存中独立按当前模板替换本角色地址/设置，拼接 17 份历史完整原字节及其精确边界标题，再追加本角色旧 R2 完整输入，所得两份均逐字节等于最终输入，无未替换占位符。17 个 currentOwnPath 均在本角色新 root/runtime，逐项 bytes/SHA 符合。R2 后缀分别为精确 242491/242581 B、SHA `513da17b6f17e8004244cbc72c8f98dbc55a837862bd9c4d6d5c5ae80814c87d` / `525ac36e5e505c103760501ada799c4399b3780559891a3a1b6b28f8e2ed8ede`；不删旧正文或仅留摘要。

17 份内嵌完整材料包括两 R2 completed 作者报告、最终非作者独审、完整接收回执、新意见处置/静态复核/新旁注、006/007/008 比较及来源、M 越写脱敏证据、Z 读写缺口、首收时点缺口、导出脱敏、原拒绝 call/result、作者拒绝首错、采集端首错与实际分类索引。作者 NotPass/PASS/P2/P3、旧 UNKNOWN 时点、后继 completed、PROCESS_FAIL 分别保留，不互相替换。

owner 与角色的 input-manifest、full-git-files、required-reading、issue-register、environment-setup-plan JSON 及 short-launch 副本均逐字节相同；dispatch 对应角色记录与 input-manifest 结构相同。短启动壳逐项含本角色精确新 root、附件路径/bytes/LF/SHA、operator 收据、新报告及本轮无运行许可，不以历史地址或“同名”推导路径。

## 2. 1020 项新 Git 源与隔离

使用 `git ls-tree -rz R` 与新物理 root/scratch 逐项重算 SHA256/blob 身份。每树清单路径集合恰为 **1020 项；1019 精确等 R，唯一例外为 AGENTS**。root 与 scratch 对应内容全部相同，例外 AGENTS 与 owner/current-AGENTS 快照同为 SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。tracked diff 唯一 AGENTS M，index 无改动，不 stage。

四套 root/scratch 的 1020 个源文件均非 symlink；任意两套源文件 inode 集合交集为 0，四个物理目录 resolve 也不跨根。两角色 metadata/tmp/uv-cache/npm-cache/ruff-cache/pytest 共 12 个目录均为独立实际目录，12 个 device/inode 身份互异；metadata 各 2 项，其余列明临时/缓存/pytest 目录均为空。未把共享只读 Git 对象误记为共享可变环境。

两 root 与两 scratch 下 `.venv`、`node_modules` 共八个路径均不存在，连 dangling symlink 也无。environment-setup-plan 均为 `PLAN_ONLY_NOT_EXECUTED`，dependencyCommandsExecuted/productCommandsExecuted=0，所有 cache 路径只在本角色 root/runtime；两项锁定安装方案 executed=false，明确不是执行授权。没有借旧环境或把源准备说成 installed、Electron 可运行或 check 通过。未安装不是本轮静态准备缺项。

## 3. 236 项完整读取材料与身份来源

每方 required-reading 恰为 **236 个唯一存在路径**；全部实际 bytes/SHA 符合，resolve 均在本角色新 root/runtime，无跨角色或历史外部实物路径。所有 actualReadCompleted=false、requiredVisibleEOF=true。类别如下，数量仅表示清单分组，不是缺陷数或已读数：

- 原 148 项完整保留：14 项 SOURCE/TEST/fixture、25 项 P 候选原件、完整 candidate.patch、B 的完整 PRD、31 项历史/指南、当前政策及 75 个旧原件。
- 新增 13 份 completed R2/静态旁注全文、72 个安全 R2 导出成员、1 份未解除拒绝原 call/result、2 份当前方案/议题索引，合计 236。

25 个新 history/product-candidate 镜像均与给定 P 的 Git 原文件逐字节相同，包含 status.md 的 P 原件，不将树内后继过程版称全部等 P。完整 PRD 新副本逐字节等 B 的批准原文。旧 75 个新提取成员逐项符合固定 archive-manifest 的大小/SHA，均非 symlink；其中确为 33 日志+2 PNG=35。两方 9 条原始 final 的含原末换行 rawLineSha256 和 payload.id 全部与索引对应；3 条加密中间消息只作元信息，不追索源 session。

R2 安全导出 archive 的 72 个 regular 成员与新 runtime 物理提取件全部逐字节相同；export-index 的 71 payload 逐项大小/SHA 相符。使用当前安全 export-index，没有拿 freeze-index.source 的旧未脱敏预期去覆盖已声明脱敏。M 第 84 行的全局 listing 只在授权脱敏范围内使用，未恢复被遮蔽的其他条目，未访问旧 assets 或全局文件。

此处 hash/JSON/Git 比较只证明新准备件齐备与来源，不证明审查模型已经看见 236 项全部内容，也不把 SOURCE/TEST 不变当作已全文阅读。本内部准备审没有代做外审模型的完整产品源码审查、历史图像审查或旧 native 取证；未把程序内部 load/hash 当可见 EOF。

## 4. 当前读取/写面/EOF 与身份边界

当前前缀第 1/3/4 节明确：普通静态工程读取限本方 full-git-files 已列固定源，必读历史限本角色已物理映射路径；历史 sourcePath/app/native/其他角色旧根只为来源标识。另行阅读也须记账，不横扫 runtime，不使用 agent/list/sessionget/globalconfig/全 session/父目录 find 补身份，不读 controller 实时状态、凭据或本轮 peer。

两 operator 收据及模板均为 `PREPARATION_ONLY_NOT_SUBMITTED`，tasksCreated/formalSends=0、GUIReleased=true；actualSettingsUI/SID/turn/附件/terminal/verdict 均 null。要求 GLM-5.3/最高/完全访问、M3.1-Flash/xhigh/始终授权只是待实际任务 UI 读回，不由旧 SID/设置推断。readiness-notice 与 operator checklist 均无 START、无 GUI lease，当前 Pair gate 保留 PROCESS_FAIL/Pair 0。

完整附件与本地 full-input 身份分别核；实际返回按真实末尾、字符/字节/UTF-8 边界续读到 EOF，不能用请求 limit、hidden details、hash、keys、程序内部 json.load、测试读取、选段或历史已出现内容替代可见全文。明确禁 stdout 接 head 导致 BrokenPipe 后按原请求 offset 续读；旧漏 30 字符与 compaction 缺口保持缺口，不由当前全文回填旧 Read。ledger 仅记录真实 call/范围/截断/EOF，不预签 38 项 eofConfirmed。

唯一报告为各角色新根 round-3 报告；新增取证限本方 raw/validation、reports 与明确 reviewer metadata。operator/历史/输入/清单/源码/测试/PRD/验收/配置/锁只读；禁止 /tmp、全局 assets、父项目、其他树及任意“待清理”占位写入，不能用 trash/删除清洗事实。不重写旧报告或冻结输入，不提交或修改 Goal。

## 5. 既有 check/raw 优先、未解除拒绝与零执行许可

新前缀先要求全文核现成原 check/raw 的原入口、双流、环境、退出、首错及因果链，再判断其可采范围；没有机械 fresh rerun 前置，也没有把文件存在、通过计数、isError=false、exit 文本或 completed 当整数目标 exit0/工程 Pass。必要证据仍不足时，须明确 UNVERIFIED/NotPass、缺何原链及其必要性。

明确分列 M R2 001–004 原调用处于 compaction 缺口，和 M005 已有真实 scratch cd/pwd、相对脚本、直接 rc=0；不以 005 补 001–004，不混不同运行。旧 check/raw 的完整材料可读不等于本内部审已重新确证全部历史执行。

本轮原拒绝 call `call_67be7300c0dc4552845dc9c0` 的完整调用、isError=true、原 Mimosa 理由/作者首错原文已内嵌并列入读取清单。rootRelease=null；pytest/vitest/npm check 同目的仍 UNVERIFIED。前缀明确不重跑、不换 argv/重定向/脚本/wrapper/工具/身份/角色绕行；可能误报、Write 成功或完全访问都不解除。静态单文件工具本身若被拒也须停止同目的换路。

**当前没有产品验证、probe、setup、依赖安装、新 native/实验执行许可。** scratch 纯源不带运行能力；不自动执行 environment plan，不借旧依赖，不把 M005 或旧图作为本轮产物。需要运行须 root 另作精确处置；本报告不给执行或放行授权。本审也未执行 build-materials.py，只读其内容核装配逻辑；preparation-receipt 所列 build stdout/stderr bytes/SHA 符合原件，原 exit0 是准备者记录，不等于本审运行或产品证据。

## 6. Definition 守卫、意见命名空间与父门

新前缀保持完整 Definition 内容身份守卫；新 Git 源核对未见自动排序/去重或合同改动。integration-request 的“待批准/非公共契约”身份明确保留，未升成 T00 已批准合同。006 完整 rounds/checkpoint 不等、007/008 仅选定子集相等、008 无反向尝试，按不同原输出分列；不合并成全值等价。runner 158–160 与 IR-03 删除后复用历史 ID 的旁注校正不改作者原文、不新增运行关闭证据。

issue-register 两角色副本均按实际记录分别保留：原七项观察 7、R1 NR01–05 5、R2 独审读写/报告问题 5、M 新工程意见 2、未解除 operational hold 1。字段明示这些是类别数量，不是某个合并缺陷总数，不猜“13项”。原 M authorPriority 仍 P2/P3，rootDecision=null，责任接受 false，sourcePatchProposal 空；没有接受作者“非阻断/接线前处置”作为 root 已批延期，也没有借本次准备通过降低工程分级或 Pair 门。

R1/R2 PROCESS_FAIL、Pair 0、两作者不同结论及两轮不同拒绝/包装/读缺/越写事实均保留。真实 T05/T06、T01/I04 生命周期/取消竞态/原子 Round+progress/终态/operation-id 响应丢失对账、公共契约/bridge/App、真实删除/恢复/快照创建续跑、完整 E5 四类结果、T10 跨设备、父 FR/附录、双 OS/真人/CI/远端/发布边界完整透传。原 Goal 不重建，无 push/PR/合并许可。

## 7. 发现与限制

没有发现真正的准备材料缺项、错误路径、字节漂移、错误 installed 声明或授权扩大，因此本次限定准备条件 Pass。环境/执行证据仍未验、原验证 hold 未解除、236 项未来可见 EOF 未完成、M 新工程 P2/P3 root 未决、指定双审/Pair 门不通过；这些明确保留的状态不能被本报告转成完成。

本内部审仅运行静态读取、标准库 JSON/tar/hash/stat 比较与只读 Git；没有产品/测试/probe、依赖安装、外发、GUI、旧 native/session/global 恢复，未扫描旧 roots 或 controller。未遇本次工具自动拒绝，亦未重放任何旧被拒目的。本报告完成一次内部非作者准备审，之后仅供 root/controller 一次性核 READY；文件存在及本条件 Pass 本身不授予 START。

文档验证：仅调用 owner 现有 Prettier 对本报告作 `--check`，exit0；未调用 npm/npx、未安装依赖、未修改其他文件，也不计为产品验证。
