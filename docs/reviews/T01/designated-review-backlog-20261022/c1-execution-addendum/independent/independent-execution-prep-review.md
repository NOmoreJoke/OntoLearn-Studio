# C1 执行准备独立定点审查

首轮结论：**当前执行准备不通过，需先修环境注入与写出边界，再完成清单导航。** 固定源码、安装记录与当前guidance身份检查通过；这只是静态准备检查，没有执行产品或测试，不产生指定模型Pass。若后续补充复核，须保留本首轮发现。

审查者 `/root/i05_resource_offer_independent`，只读审查 `outputs/20261022_review_backlog/T01-C1-execution-prep/` 新包及必要固定源码/Git/环境元数据；只在 `/tmp/t01-c1-execution-prep-20261022/` 写独立报告/小证据。未改repo、输入、测试、锁、AGENTS或旧manifest，未import产品、pytest collect、测试、SQL/native/业务child/GUI、安装或启动模型。

## 阻断发现

### EXEC-01 / P1：环境未清理能替换候选的变量

位置：两模型 `review-env.sh:2` 只清PYTHONPATH、PYTEST_ADDOPTS、I02_HMR。原suite真实消费的 `ROOT_SOURCE_PATH` 与 `ONTOLEARN_TEST_ENGINE` 仍会继承。

具体反例：若审查应用环境继承 `ROOT_SOURCE_PATH=<另一候选树>`，`tests/unit/task-runtime.test.ts:41,158` 会选择另一源码/registry并为Python加入该源；`packages/engine/tests/test_i04_lifecycle_boundaries.py:20` 在导入前将该树src插入sys.path。若继承ONTOLEARN_TEST_ENGINE，`test_resident_runtime.py:30,109`、`test_worker_parent.py:50`、`test_worker_owner_bootstrap.py:219` 会启动该外部engine。即使cwd与editable安装正确，也无法保证本轮执行固定C1候选。

必要修复：两脚本至少清ROOT_SOURCE_PATH、ONTOLEARN_TEST_ENGINE及解释器/测试注入（PYTHONPATH/PYTHONHOME、VIRTUAL_ENV、PYTEST_ADDOPTS/PYTEST_PLUGINS、NODE_OPTIONS/NODE_PATH），设PYTEST_DISABLE_PLUGIN_AUTOLOAD=1或提供等效明确插件隔离。不要改suite/deselect旧guard，不需读出当前环境值或重新执行产品来证明脚本文字修复。本轮未观察到实际发生污染，问题是执行入口未封住该原有分支。

### EXEC-02 / P2：普通build获准但默认输出被写面文字排除

位置：两 `inputs/execution-addendum.md` 的“本轮可执行验证”允许原npm check含普通build，后文“源…保持只读”“可写…本模型目录”及dispatch“只能在自己的scratch/raw/reports记录”没有明确允许自己隔离树的构建输出/缓存。

`package.json`的check真实经过build→desktop `electron-vite build`；`apps/desktop/package.json`的main指向`./out/main/index.js`，未覆盖默认outDir。普通build会写自己树`apps/desktop/out/`，ruff/pytest默认也有本树ignored缓存。这不是tracked产品修改。现文字会迫使执行者违约、跳过build或改构建配置，三者均不应发生。

必要修复：明确仅本模型隔离树中原工具正常产生的ignored build/cache（或精确重定向的独占输出）可写，列出具体范围；tracked源码/测试/锁/配置/Git与保护AGENTS仍只读。自己反例、DB、raw/report仍按专属目录，不授权任意ignored路径、另一个模型或原冻结包。不要为此改产品构建脚本。

### EXEC-03 / P2：引用清单尚未交付；摘要clean需带时点

两addendum引用补充根`test-command-static-audit.json`，首轮检查持久包内尚无该文件。临时清单已存在，但其MD第5行“两个树…clean”与当前受保护AGENTS M不符；可注明此前clean观测时点并补当前状态，不能把根传播的M抹掉或称产品改变。

必要修复：将最终清单无损固定到提示词实际路径，并核MD/JSON身份和状态一致。保留旧clean观测及首次缺导航事实，不倒改原日志；不需重跑测试。此项为当前备包未交齐，不质疑该作者已完成的静态源码遍历。

## 已核同的身份与权限边界

两树分别为 `.worktrees/T01-c1-zcode-review-423b7e4`、`.worktrees/T01-c1-minimax-review-423b7e4`，实际detached HEAD均`c0b61fd245c1b3bd2a84e488f00a742a1942fd8c`，批准base为`5f910b52c69d86a1076b2032e5d3c63e715947f3`，C1产品`423b7e4c799f188cf2ce6e8e7121893ce85624cd`。独立核52产品/测试路径原字节全部等423；423→c0恰90件docs。对E13完整825件快照，实际824同，一件AGENTS是root传播15147B/de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4当前guidance。两树均只AGENTS M，staging空；不能称clean。当前附本与主规则文件逐bytes同。

`C1-execution-decision.md`把本C1原正常check/128功能/普通事务范围与新N0/native caller/production producer、被拒C2/S1 SQLite/heap/OS研究清楚区分。addendum明确旧blanket禁npm/pytest/child仅本C1由新精确规则替代；原I04未改libproc/resident_bytes/test-worker及Coordinator现有传递调用属于已授权原suite，不过滤、不再逐命令请示。保留损坏物理SQLite HOLD、whole-H未证、禁止旁路同目的研究、原scope/真人OS/父功能/指定双审门，未把旧RSSguard当新物理资源证明。两方原prompt raw与旧封存原件逐byte相同，不互看本轮结论，源码/tests/锁/Git只读，任务实际字段均null、仍未派发。

四次环境安装receipt均真实exit0，argv分别npm ci --ignore-scripts --no-audit --no-fund、uv sync --frozen --python固定3.12 --no-python-downloads --link-mode copy；四份stdout/stderr bytes/SHA均核同。7件依赖输入before/after及当前原件无变化，cwd分别属于自己的树。两node_modules真实路径独立，venv关闭system-site-packages，editable路径各指自己树；环境metadata读回只importlib.metadata，不import引擎。记录中的Python3.12.12、pytest9.1.1、ruff0.17.1、rdflib7.6.0等只是发行包元数据，不是测试通过。npm原stderr有deprecated警告，没有以exit0掩掉其存在；本审不把安装成功当产品/原生二进制可运行。

## 旧guidance导航缺件的更正

旧完整发审包确实缺`control/AGENTS.md`，旧prompt却指向它；原主规则实际在`OntoLearn-Studio/AGENTS.md`。此前盘点独审只核已列104件控制资料，没有检查这条必读导航的存在性，这是前次审查遗漏。不能把先前静态接收结论解释为该导航曾完整。旧报告、prompt、manifest保持原件，本新addendum显式记录缺件并附当前15147B主规则，补救方向正确。后续实际模型必须读当前附本/完整common第九节/桌面政策/原C1授权，不能靠旧1056B副本替代。

## 实际命令与独立证据

实际只用`rg`、普通Git rev-parse/status/symbolic-ref/diff/show及Python标准库pathlib/json/hashlib/ast文件读取。Git源码blob与52路径、825快照比较、两树身份/状态、4安装receipt和双流哈希、依赖前后/当前字节及原prompt字节比较均完成，脚本exit0。Python准备脚本AST语法可解析；本审未执行它们或source env脚本，未跑product/helper/pytest collect/DB/native/GUI/模型。初次rg无排除地列到cache，输出截断，随后改为只读明确文件；没有把截断列表当完整审查。

独立证据 `independent-execution-prep-check.json` 记录初始输入身份、两个env脚本原文、任务空字段和上述实际结果，后续修复可追加最终delta读回，首轮发现保留。

## 修复后定点delta复核与最终限定结论

**EXEC-01、EXEC-02、EXEC-03均关闭；本C1执行环境与输入准备可派发。** 这不表示C1实现/运行验收通过，也不是指定GLM-5.3或MiniMax审查Pass。首轮7241B正文及不通过发现完整保留，持久history原件SHA为`887c9b233db05a884b20d3a57e003f5b5716e164e2327e6936859f40105ba8fa`；本节只追加，不倒改原结论时点。

本次只核冻结修复delta，未重验源码/安装，未执行env脚本、产品import、pytest collect/测试、DB/SQL/native/业务child/GUI或模型。

- EXEC-01：两review-env.sh均清除ROOT_SOURCE_PATH、ONTOLEARN_TEST_ENGINE、PYTHONHOME/PYTHONPATH、PYTEST_ADDOPTS/PYTEST_PLUGINS、VIRTUAL_ENV、NODE_OPTIONS/NODE_PATH、UV_PROJECT/UV_WORKING_DIR/UV_CONFIG_FILE与I02_HMR，并显式设PYTEST_DISABLE_PLUGIN_AUTOLOAD=1。自有env/cache路径保留，不deselect原suite。由此封住首轮定位的外部源码/engine/插件注入入口。本审静态核原文，没有运行这些脚本或声称全部未来shell环境均受沙箱强制。
- EXEC-02：两addendum明确本轮树/env/scratch/raw/report与执行规则优先，原完整scope/验收保持；允许本模型自有隔离树正常ignored工具输出（apps/desktop/out、.ruff_cache、.pytest_cache及本模型依赖缓存），tracked源/tests/锁/验收/Git仍只读。禁止据此改配置、他树或冻结输入。dispatch和旧prompt的旧写面文字由该明确优先条款限定；普通check/build可以按原工具执行。
- EXEC-03：test-command-static-audit.md/json已在本补充根，导航实际存在。MD第5行保初核clean时点，当前末核写仅AGENTS M；与既有映射一致。普通check中原I01固定负载measure与I04旧guard/worker回归均按未改suite保留，不能据此重启新N0/生产producer或被拒物理研究。两addendum将zcode字面替换为minimax后全文相同，未发现一方放宽边界。

冻结清单 `preparation-input-manifest.json` 为7663B，SHA256 `91c9e007089fb23cabf1018a4920a3f8c8542777350e430b0fccbc788e646bb1`。实际逐件重读43个清单输入，bytes/SHA全部匹配，无缺件/差异。关键修复身份：

| 输入 | bytes | SHA256 |
| --- | ---: | --- |
| zcode/review-env.sh | 1374 | 41edd27e05e057cad22602337c6aa7a770deb9c62b1fb2117106fdc8cf34c687 |
| minimax/review-env.sh | 1388 | 847cdecbb75a5ddba16c44e26e23a4fd1bb9c5027af9f03d7a9f72f832a85160 |
| zcode/inputs/execution-addendum.md | 8125 | 2d73bd86ee227b60c12613d12ec27a4faa1b107f0dd8d688520c7c729f1e26e2 |
| minimax/inputs/execution-addendum.md | 8141 | 2311f5e01f28636151e2eb53d8954760f5cc887dd94b2fe8ea12ba1fa3adcde3 |

本节逐件身份以43清单及delta证据为准。C1-execution-decision、四份current-guidance和两旧prompt.raw身份与首轮相同，原guide导航缺件事实仍保留。两task record已作为`inputs/pre-dispatch-task-record.json.raw`不可改准备期快照；清单明确未来真实任务/设置/报告进入各自raw/review及reports。准备时实际指定任务0、产品测试0，不得将这份历史空快照当未来实时任务状态。

读回raw-preparation-format/receipts.json及六份双流：新文档首次check exit1指identity/environment两JSON格式；write0、末check0。原raw、当前guidance和静态报告未因此格式化。这里只确认主线执行记录，未自行重跑formatter。首轮独立证据原件未改；新delta证据为`independent-execution-prep-delta-check.json`，14914B，SHA256 `87f8fbe3367d90a8371ab2429b40b292d7b678887d5dae1f54731b69d3fcc2a8`。后续派发必须实际读回任务模型/推理/逐任务权限，保全部首次失败、argv/cwd/退出与报告；原HOLD、Goal blocked、完整指定双审和父范围门保持。

## 实际GUI提交完整正文的最终追加核验

两份新增`inputs/complete-dispatch-prompt.md.raw`静态核验通过，属于追加派生输入。分别严格等于同一392B ASCII优先说明 + 对应旧完整prompt原bytes + 固定50B分隔标题 + 当前execution-addendum原bytes，无截断、替换或多余尾部；旧prompt与addon各出现一次。前言只规定本轮树、环境、验证执行权限及输出路径以addon为准，明确完整原验收scope保持，并仅本C1取代旧blanket static-only禁令；未新增实现写权或放开被拒研究。实际GUI应直接提交该完整正文，不能仅给路径dispatcher；本审没有操作GUI，也未证明粘贴或实际任务已完成。

- ZCode：13463B，SHA256 `13e864e3bca8a42e2bf249aa8f2e0135870e4f1c8e09631f90b00c04c5bc6e44`。
- MiniMax：13490B，SHA256 `f3a8988345861c0a924383dd5ce29effd56786a984b86fbc166534aadd9b8c08`。
- `dispatch-concatenation-manifest.json`：1486B，SHA256 `f9f6c24468e8f746f3831ac9df46cf45c6f3850f260528538b8fed957fc42f0d`；各文件与来源hash均实核匹配。

原43件输入的preparation manifest自身SHA仍为`91c9e007089fb23cabf1018a4920a3f8c8542777350e430b0fccbc788e646bb1`；本轮没有重复读取全部43输入或源码/env/安装/测试。独立追加证据`independent-dispatch-concatenation-check.json`为947B，SHA256 `52fc0c3f65f91aa18cf4e49a5ebbb2d11adc3a8509d3712fb9a17862a3a84982`。本次新增正文已覆盖，维持“环境与输入准备可派发”的限定结论；实际任务设置、产品验证与指定模型终态仍须其后真实读回。
