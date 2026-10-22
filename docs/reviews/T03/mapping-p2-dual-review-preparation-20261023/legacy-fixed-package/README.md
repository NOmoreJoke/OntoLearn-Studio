# T03 历史指定双审补齐包

此包把既有保留实现落实为四个**分别固定的完整工程审查组**：mapping-S1、source-selection、profile-D2、native-current。历史阶段清单、29 个阶段的逐路径覆盖矩阵、各组完整 Git 路径与身份及双方完整提示均已落地。它们是派发准备，尚无真实 task ID、逐任务设置、报告或指定 Pass，不把内审当指定模型通过。

三个现有独立工程组可按总控短 lease 创建任务，不全量等待父 runtime。native-current 正在修 caller 内部 Fail，先封新候选并完成既定 fresh delta，再前向新增该组输入身份；本包的旧 6815495/cf9 快照保留。当前原 Goal、维护职责及全部原验收继续，不新建用户聊天或 Goal。

## 固定范围与覆盖口径

- `historical-stage-inventory.md`：五树的实现、六构建、供方与修复链、纯方案、原报告及全部已知缺口。其 snapshot 后 caller 首审封存 cf9、新 D1 计划实际候选 ae28572c91b78933c35996f0d80e81c03b96edf0，均由本说明前向记录，不改历史观察。
- `coverage-matrix.json`、`coverage-summary.md`：从共同批准 5f 到每个历史阶段的每条 engineering 路径，比较完整当前审查组相同位置的 mode/type/Git blob/bytes。相同字节才标覆盖；改变或删除明确不覆盖，并保实际替代与修复历史。源码、测试、配置及位于 docs 的 `.py.raw`、`.input.py.txt` 工具均计入，不能只审新增 delta。
- 四份 `*-fixed-inputs.json`：各组完整固定证据 ref 的全部 tracked 文件及 base→product 全路径。Git blob OID 是 SHA1 对象身份，**不是 SHA256**；此准备没有读取/解码这些 payload。没有把 metadata inventory 冒成全文源码审计。
- 八份 `*-{zcode,minimax}-prompt.md`：同组双方各自全新完整只读审查提示，互不传本轮意见。ZCode GLM-5.3/最高/yolo、MiniMax M3.1-Flash/xhigh/bypassPermissions 是待实际确认要求。native 两提示明确禁止当前派发；不创建重复旧任务。

本包不拼装四分支：S1 的 XLSX21 锁、profile 的 semantic23 锁及各自入口/build guards 都是不同真实实现；完整并集26只是 D1 前向方案，尚无运行组合。`independentBranches` 列出当前共同非 docs 路径的不同 blob。另有已合并基线、其他 owner 模块或 I05 offer/D0/D1 纯方案，只按各自固定 scope 登记，不制造一个任务审数十个 worktree 的虚假运行候选。

profile a4d→56a 非 docs 产品逐字不变，但后来追加了九个证据工具；它们已列入 `laterEvidenceHelperDifferences`，按完整 process ref 审，不当作无需审查的普通文档。每个组所有历史报告和失败原件仍在对应固定 ref，不强行给旧候选继承新结论。

## 验收与操作边界

完整 PRD FR-300–304、附录 C–G/G.1 M-01–06、§10–12、M0 及父 I05/native 相关合同全部保留。各组的原验收、真实命令/退出和尚缺运行、平台、业务联验分别给结论。D2 源/包83各78成功、4资源拒绝、1缺规则未执行，probe/oracle exit1；native 第1次 timeout、第2–6 built-unverified/NOT_RUN；caller 四项首审 Fail 都明确进入提示，不缩范围做 Pass。

本轮先完整源码与已有证据审查；没有新变更不强制重测。旧 HOLD、自动拒绝、未签 native、caller/局部函数/runner/reader/fixture/模拟/编译及未获读取授权的载荷，不能由指定模型代跑或擅读。确需新证据时逐门判“不通过/无法验证”，由原 owner 按其精确票处理；不因这些缺口永久排除其他已实现源码。后续如改变实现、测试、配置、依赖、验收或 base，必要验证后双方全新完整审查；本包纯流程元数据不触发产品复测。

当前最新政策已撤回静默桌面限制，受保护 AGENTS 为15147B/SHA de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4。实际同一桌面应用由总控短 lease 内部交接，不向用户重问时段。旧冻结 round-1 提示/清单不修改，当前政策由本新提示及真实派发收据附加。

完整必要上下文在仓库外 `iteration-control/2026-10-21-weekly-release/{developer-common-instructions.md,desktop-operation-policy-20261022.md,external-review-permissions.md}`，指定模型逐任务权限和完整第九节必须实际透传。未使用 CUA、未创建 task、未运行新测试/产品/native、未 push/PR/merge；所有 ID 保持 null。唯一下一步是本包独立核验、总控接收与真实短 lease 派发，native 另等修复封存与 fresh delta。

## 准备中的实际首错

首次 stdin 文档生成命令因编码 SyntaxError 在任何语句执行前退出1；改为带 UTF-8 声明的本任务 scratch 工具后继续。第二次普通 Git 元数据检查发现 profile process 新增九个证据工具，原“所有 engineering 与产品相同”的断言失败；已纠正为“非 docs 产品相同、证据工具逐项纳入完整 process 范围”，没有掩盖或删掉这些工具。本任务 scratch 只生成/核对文档和 Git 对象元数据，不执行 caller 或其他准备代码。
