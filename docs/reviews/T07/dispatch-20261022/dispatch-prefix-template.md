# T07-S1 {{APP}} 完整工程新任务：当前派发操作补充

本补充后接旧完整冻结正文的**原始字节**，不是只审最新delta或source-only片段。保留完整工程、原验收、首错原件及IR-01～05发现/关闭。以下只更新物理路径、当前政策、独立性和执行授权；不改产品/测试/验收、旧输入/manifest。与旧正文的旧路径、旧静默/CLI前置或“尚无任何产品测试许可/只写一报告”冲突时，以本当前补充为准，其余完整审查内容全部保留。

## 当前精确任务身份

- 应用workspace和所有源码读取/命令cwd唯一为 `{{ROOT}}`，detached reviewHead `24f3703ecf4fce75e0d0375f7291ed928f083c41`。不得选原开发树，也不自行切分支。
- 受审base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → 产品/测试 `f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3`，完整25路径、14项实现/测试/fixture；该reviewHead仅追加过程材料，产品14项仍等f9。status等过程文件按各自固定ref读，不把后继流程状态混作f9原件。
- 指定模型/思考/权限要求：**{{MODEL}} / {{THINKING}} / {{PERMISSION}}**。这些是要求，不是已经核验的实际设置。创建负责人必须保存本实际任务级模型、思考、权限读回、真实ID/正文受理时间；不要依据用户默认或标题预填Pass。
- 旧正文出现的 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-scenario` 一律只是历史来源标识；本次源码、测试、文档和输出路径均映射到上述自己的实际workspace。历史原文不改字节；不得因此跨树读取原开发目录或当前session。
- 唯一最终报告：`{{REPORT}}`。独占原始输出/补充证据在 `{{RUNTIME}}/raw/validation/` 和 `{{RUNTIME}}/reports/`；临时检查文件在 `{{RUNTIME}}/scratch/`；任务设置及文件增长记录在 `{{RUNTIME}}/metadata/`。
- node_modules `{{ROOT}}/node_modules`、venv `{{ROOT}}/.venv`；其余环境/缓存/TMPDIR/pytest/日志都用 `{{RUNTIME}}` 的本角色目录。不能共享可变依赖环境、DB、scratch、raw、报告或metadata。

## 完整范围、原验收与历史证据

完整审查私有场景定义/事件/轮次编排/FIFO三指标、不可变历史/恢复身份、私有页面/view/合成探针、批准T09输入/资源投影、Context/冻结计划/逐动作轨迹、真实批准Store事务/取消/READONLY/崩溃测试及完整投影交接样例。前6个技术组成仍是一个完整S1，不缩为6个小任务。还须读纯接口提案与当前未就绪父积压，辨别已有工程与未实现能力。

必须完整读取本树 `docs/reviews/T07/round-1/frozen-manifest.json`、25路径完整diff/candidate.patch、14项全部实现与测试/fixture、批准PRD全文及对应FR-700～705、D/E.1～E.5/G.4/G.6/第10～12节、原验收/接线提案；不能用摘要替代源码。完整Git源码身份清单在本次 `current-inputs/full-git-files.json`，该清单包含本树全部tracked文件，不仅末次补丁。当前AGENTS是唯一允许的受保护操作政策差异，M保留、不stage。

须读取本树旧包 `frozen-inputs.tar.gz` 的全部既有log/png原件、失败与最终记录、9条原始独审终态和来源索引，核其大小/hash。压缩包只提取到本角色scratch，不能覆盖固定review路径。3条加密中间消息只登记元信息，不解密。原sourceSession和旧绝对链接只是历史索引，**不要跟随到正在增长的原会话或其他任务目录**。`internal-review.md`只是开发者摘要，原始终态才是历史原文。早期42项READONLY假证明已失效，后来43/44项修复和交接不追认旧证明；空日志不能单独证明退出码。首失败均保留，不删除/改成通过。

下面附原验收、历史问题和9条原始内审终态的可读全文；原始逐行JSONL/hash及全部原日志仍在本树封存包核验。普通内审、准备包独审和本任务尚不存在的终态都不等于指定双审Pass。

### 现有工程原验收全文

{{ACCEPTANCE}}

### 历史问题与处置索引全文

{{HISTORY}}

### 9条历史普通内审原始final全文

{{ORIGINAL_FINALS}}

### 全量保留技术项/未就绪父积压

下列盘点来自原过程提交 `15dcbb103fade7a91df73a54c5217a6053bd5f47`，是身份/范围材料，不是新增产品版本；所写“无任务”是盘点时状态，实际本任务ID及设置由创建负责人另行读回。

{{BACKLOG}}

## 普通验证授权与明确边界

setup owner已按本角色原锁准备npm依赖（忽略lifecycle）和独占venv，没有运行产品。**正式审查中允许按必要性运行原普通对应检查及受控测试worker回归**，这项许可取代旧正文“本准备授权无产品测试/只能先列命令”的操作限制；不机械重跑无变化历史。不能泛禁child进程、临时SQLite、原READONLY/事务/进程退出suite；也不能扩大物理资源研究、已拒绝动作、新native/caller/producer或API付费。

实际调用预检及每项副作用/边界如下，必须完整遵守。setup成功不证明下表检查或产品通过；本角色只对自己实际运行的命令和观察负责。

{{EXECUTION_BOUNDARIES}}

具体运行时非敏感环境路径：TMPDIR=`{{RUNTIME}}/tmp`，UV_CACHE_DIR=`{{RUNTIME}}/uv-cache`，UV_PROJECT_ENVIRONMENT=`{{ROOT}}/.venv`，npm cache=`{{RUNTIME}}/npm-cache`，RUFF_CACHE_DIR=`{{RUNTIME}}/ruff-cache`。清除ROOT_SOURCE_PATH/PYTHONPATH/ONTOLEARN_TEST_ENGINE/ONTOLEARN_DB_PATH跨树覆盖。pytest如指定basetemp只能用 `{{RUNTIME}}/pytest/` 下全新唯一子目录。不要输出环境秘密，不读取/搬运凭据。

允许写自己的报告、raw/metadata/检查临时材料，以及正常检查按原逻辑生成的本树out/cache；候选源码/测试/fixture/验收/依赖锁/配置和旧证据/旧输入只读。应用生成的本树metadata按实际路径/大小/mtime记录增长并保留；不能新加ignore、删除或清空metadata求git clean。继承的ignore状态也要如实记录，不能把未显示文件当不存在。正常原测试对其精确自有子进程/临时目录的回收不等于删除应用metadata。

## 严格独立性及调度

只能读取本角色workspace、自己的runtime和指定B/P/reviewHead的只读Git对象。**禁止读取或发现peer本轮报告、状态、任务流或metadata**；禁止枚举其他worktree/refs、controller实时队列、全会话文件、其他应用账号任务。禁止把另一模型本轮意见带入本任务；历史普通独审已完整封存于自己输入，可核历史关闭。

当前人类已撤回静默桌面要求，可按已授权范围computer use；没有用户时段、CLI登录、后台或隔离桌面前置。桌面仅创建/设置/读回短时内部串行，后台推理不占整个应用。准备时当前短lease归T01，本消息不是T07操作前台许可；实际创建负责人须先取得root短lease。此处是内部调度，不让用户重答桌面时段，不重复其他线既有真实任务。

真实T05/T06、T01/I04正式Job生命周期/取消/原子进度/终态/operation-id响应丢失对账、公共契约/bridge/App、实际删除/恢复/快照创建/续跑、完整E5四类领域结果、T10跨设备及FR-700～705/两OS/真人/发布门照实保留。这些缺口不阻止对现有完整工程审查，但不能填成已完成或缩减原父验收。所有57P0、双审/全文终态/所有意见处置/CI/远端门保留。

## 当前操作政策全文

以下为本次快照；其操作段优先于后附旧冻结正文中的历史政策。执行前由负责人核当时仍适用，审者不为发现最新队列而读取peer/controller状态。完全访问不允许改产品或自行commit/push/切分支。

### 当前受保护AGENTS全文

{{AGENTS}}

### 当前共同开发指令全文（含第九节）

{{COMMON}}

### 当前桌面政策全文

{{DESKTOP_POLICY}}

## 后附旧完整冻结输入

后续正文从下一个标记后的首字节开始，与原 `{{OLD_FILE}}` 完全逐字相同，原SHA256为 `{{OLD_SHA}}`；完整输入、前缀长度、suffix offset和整体hash由本次input manifest固定。后附旧文中的历史位置/执行限制按上述映射和更新解释，其他范围/验收/问题/报告门均有效。

--- BEGIN EXACT ORIGINAL FROZEN INPUT BYTES ---
