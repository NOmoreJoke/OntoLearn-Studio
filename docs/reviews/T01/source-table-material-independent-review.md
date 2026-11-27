# T01 sourceTable 纯材料实现独立审查

修前结论：发现 **P2-M1：预算 JSON 整数值两端接受不一致**，开发者已接受修复。本节固定修前候选；该项关闭前不支持此候选最终冻结。其余本轮只读实现审查与小型独立机制探针未发现第二项实质阻断。只评估 pure-table 内部机制，不认证 producer、来源授权、worker 或 runtime-ready。

## 1. 范围、授权和修前固定输入

工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions`，分支 `feature/weekly-t01-project-transactions`。产品比较基底 `b35cb4e21d375386775e5fc0431a8089a47195da`；过程提交可继续追加文档，本轮末读 HEAD 为 `2c12038504e256928997e4d5081a33b0a9e6d08e`，不以过程 HEAD 替代下列实际源码身份。

实际全文读取总控 `T01-table-material-phase-authorization.md`，SHA256 `562be71b7b122f17ab3747c1bf149a30574b6aba44330a7a8c1750d95f071a02`；按 capture r2 及 [identity/options 补充](../../iterations/T01/source-parser-identity-and-options-contract-r1.md)审查。阶段只新增唯一 canonical helper/sourceTable corpus 与两份专属测试；没有 startup/ready/source wire 或其他实现批准。common ff5f9f、无 GUI 和只读约束保持。

下列 **5 路径开始和结束实算 SHA256 完全一致**；后续修版不得沿用本表冒称同一候选。

| 路径 | 修前 SHA256 |
| --- | --- |
| packages/contracts/src/v2.ts | d61d00f0f0fbba3cb658f628d1e1d128cac232a1c0e183bb9e38e112cc424ef6 |
| packages/contracts/python/contract_v2.py | 8255fb743079b8c2bd1dc8cf7055c02a84b06e556aec579b327815a630f495ff |
| packages/contracts/v2/fixtures.json | 7cebecc48e8a077d317bcd8310f1ca6afb560a1f946fe40cd1e5082c432ef923 |
| tests/unit/t01-source-table-material.test.ts | 8a02c4ad375e11a6dc49841218ae21cc512567a45af70e55954f3d05eec0986c |
| packages/engine/tests/test_project_source_table_material.py | e7a4b40e3fef327d80bbe1245da63db20e62178d559c54820136e9763b6ae08a |

本任务只写本报告；未改产品、测试、旧报告、配置、依赖、AGENTS，未提交/切分支，未运行 GUI/Electron/e2e/native/HMR 或完整测试矩阵/全仓检查。开发者提供的先80/84、扩112/116及首typecheck/lint失败，均不包装成本审查独立实跑；第一全仓 check 后获开发者通知已退出0，但因 P2-M1 修复将被替代，不覆盖后续代码。

## 2. P2-M1：预算 JSON 整数值两端不一致

- 位置：修前 `packages/contracts/python/contract_v2.py:351`，`type(max_encoded_bytes) is not int`；相对的 TS `packages/contracts/src/v2.ts:436` 使用 `Number.isSafeInteger(maxEncodedBytes)`。
- 触发：普通 JSON table 为单列 v、row.number=2/text=x/string，CSV utf-8，sourceHash=a×64，synthetic-v1/test/b×64 三字段 implementation；预算分别由 JSON `10000`、`10000.0`、`1e4` 解码。没有 getter、子类、恶意 Proxy 或实际 parser。
- 证据：Python int10000 产出242B、SHA `8376f394fbaf4c47ca05108d965c22d87eee56f38f706a708235a5ee4df21785`，float10000.0 返回固定 `INVALID_REQUEST`；TS 三种 JSON token 全部产出同242B/hash。实际命令入口为 `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/contracts/python .venv/bin/python - <<'PY'` 及 `node --input-type=module <<'JS'`，工具输出逐项显示上述结果。
- 影响：共享正 safe integer 预算在两个值层助手中不是同一接受集合；TS 已无法区分10000与10000.0/1e4的原词法。合同没有预算专属 Python-int 前置或词法门，不能以隐藏本机类型规则解释为一致。此为纯机制可接受性缺陷，不声称已存在生产利用或物理内存失守。
- 建议：Python 先精确 builtin int/float、非 bool、有限 safe 范围，再核 integral 并规范化；必须先范围检查，避免巨大 int 转 float、NaN/Inf 或宿主转换。共享 token fixture 两端各用 native JSON decode 验证10000/10000.0/1e4，以及分数、bool、越界/NaN/Inf和子类边界。
- 状态：开发者实际回执接受 P2，并明确不采用隐含 Python-int 前置；准备新源码及定点验证。修前记录不删除，修后另节核定。

## 3. 其他实现与测试审查

普通记录先限定原型/精确键，逐 own data descriptor 捕获；数组不调用输入 iterator，按索引 descriptor 取值，hole/额外属性拒绝。Python exact builtin 类型和键先于内容比较/遍历，避免宿主子类协议。受信 sourceHash/options/implementation 同样经过捕获，不把 caller 对象先交给 Zod/json/deepcopy。既有 implementation 校验只接已捕获的精确原始字符串。

两端对字符串先逐码点核 surrogate/NUL/长度及 escaped UTF8 费用再生成 escaped chunk；字段空白与 Python3.12 集合一致；无单项长度界 sheet 受总预算逐点短路。行号先范围/整数/顺序检查，完整字段/行/格顺序和真实行间隔进入材料。私有 chunks 不保留 caller 对象，最终 TS encodeInto/Python join 只处理私有值；异步摘要在私有 bytes 完成后开始。无部分材料/部分 digest 返回。

共享 sourceTable corpus 有62项（29合法），另有大材料和上界 oracle、精确空白集合；测试覆盖五编码、六完整表、direct cell 类型、尾部/身份/选项/顺序、0行、unknown/缺项、字段/文本/行数上界及exact±1。普通 accessor spy、Python宿主子类零回调、后续 caller 修改、sheet先短路和 Proxy保证边界均是有针对性的测试，不把六类direct cell说成真实workbook。已有反例缺 integral JSON budget，已由 P2-M1 指出。

JS Proxy 反射可能执行 trap、恶意 intrinsics 或并发宿主内存不属于此内部函数可绝对检测的安全隔离范围；源码注释和测试均如实承认，仍依受控 decoder/producer 独占 data-only 前置及实际进程资源隔离。没有拿浅 freeze/无await 冒充 D1 保证。

## 4. 独立机制探针与旧区域保护

没有重复112/116或全仓矩阵。TS 用本树 TypeScript5.9.3 在内存 transpile 实际 v2.ts/states-v2.ts，实际 JSON 资源与已装 zod；无依赖安装或产物落盘。Python 子进程直接导入实际 contract_v2。自建输入不复制共享 golden 的预期 hash。

- 7份小表：五个精确CSV编码各一份，另XLSX sheet含NUL/非BMP/U+2028一份及header-only一份；保留 FEFF/组合与预组字符/非BMP字段、引号反斜杠/短转义/001C、完整尾行及row.number=50001。
- 独立 Python 标准 JSON 数组 oracle 直接按规范材料排列；两端实际材料完整 bytes/hash/长度均相等，exact预算成功、减1拒绝、输入不变；TS digest 与同一完整bytes的hash一致。
- TS 另5项：cells数组索引accessor、隐藏cell accessor、setter-only options、expectedHash宿主对象、budget宿主对象；全部固定拒绝，所有callback计数为0。
- 实际 stdout：`Independent cross-language full-byte/hash/exact-budget cases: 7 passed in each language; byte-below cases rejected in each`；`TS additional host/accessor rejection cases: 5 passed; callbacks=0; Python subprocess exit=0`；outer node 到达最终断言。
- 机器比较：去除新helper区域后，TS旧源码与b35逐字相同；Python旧源码仅新增hashlib import；fixtures全部旧顶层值不变，仅增加sourceTable。没有以测试数量或 schema 未变声明替代该比较。

证据记录边界：本批 wrapper 直接输出完整 stdout，但未把嵌套 `exec_command` 的整个返回对象直接 emit。Python子进程的status=0由外层实际断言并打印；不补造未展示的旧外层exit_code对象。开发者已获通知，后续修版定点必须保留完整 command/result 对象并与本修前输出分开，不能把本记录扩大成原全量子shell证据已封存。

## 5. 未验边界

真实 parser 三字段/wholeimplementation、受信producer认证、真实五编码解码、CSV/XLSX运行、来源权限与typed context、worker/大结果运输、预算账本/GC/pin、确认/Job/Store、业务3-ready、包/native、指定双审/CI/合并/父功能均未由本纯助手审查关闭。D1 在当前 data-only 前置内未发现新的二读/回调缺陷；P2-M1 的修复及新候选验证待追加，不沿用旧全仓通过。

## 6. 修后冻结候选定点复核与 P2-M1 关闭

**最新结论：P2-M1 已关闭，支持当前纯材料机制阶段继续收口；未发现新增阻断。** 前文修前结论、源码身份、失败复现和证据边界全部保留，不把两个候选混写为一次通过。开发者报告的新126 TS/132 Python及新全仓session67934属于修后候选，本审查不重复完整矩阵；进行中的全仓检查不提前记通过。

修后5路径开始/结束实际SHA一致，并与开发者冻结值完全一致：

| 路径 | 修后 SHA256 |
| --- | --- |
| packages/contracts/src/v2.ts | d61d00f0f0fbba3cb658f628d1e1d128cac232a1c0e183bb9e38e112cc424ef6 |
| packages/contracts/python/contract_v2.py | e50be513b51a817029c3a212e7d3a8ac02cb1b7164b7ab08987fc6af339ae20c |
| packages/contracts/v2/fixtures.json | 752284cb502e34ff6c97f223c20610c96a4eda7366bfb3aa7ab2858bf583cd5d |
| tests/unit/t01-source-table-material.test.ts | 4a650f1d23661eabbff5488f69e633bb8c05ee14628584cc194c0f4330e58902 |
| packages/engine/tests/test_project_source_table_material.py | 96f0dc32e2ff847f4cd3880f548faa65b1aa4dd57be4e488f8c41a173d9ef3cf |

修复实际读取：Python先限定精确builtin int/float，再判 `1 <= budget <= 2**53-1`，之后才执行 integral 比较和 `int` 规范化；bool/宿主子类先拒，巨大整数及NaN/Inf在范围门拒绝，不发生溢出的float转换。TS helper hash不变。共享新增14个budgetJsonTokens，由两端各自原生JSON解码；Python另两个预算子类零转换回调测试。

本轮独立命令和真实结果：

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest packages/engine/tests/test_project_source_table_material.py -q -k 'shared_json_budget_value_semantics or budget_host_subclass'
................                                                         [100%]
16 passed, 116 deselected in 0.09s
```

该命令的完整 `exec_command` 返回对象实际 emit：

```json
{"chunk_id":"8e61cf","wall_time_seconds":0.098618625,"exit_code":0,"original_token_count":29,"output":"................                                                         [100%]\n16 passed, 116 deselected in 0.09s\n"}
```

另执行 `node --input-type=module <<'JS'`，仍用现有TS编译器在内存装载实际helper；以第2节**独立单列表**为输入，TS与独立Python子进程分别原生解码同14个JSON token。两端结果对象完整全等：10000、10000.0、1e4、9007199254740991、9007199254740991.0全部产出242B及原hash `8376f394fbaf4c47ca05108d965c22d87eee56f38f706a708235a5ee4df21785`；10000.5、true、0、-1、1e400、1e-400、9007199254740992、null、字符串10000全部固定拒绝。Python另独立核10**1000、NaN、正负Inf四项拒绝。

该node命令完整返回对象及**全部14项TS结果和Python完整stdout/stderr/status/signal**已原样 emit 到工具记录，chunk_id `f6e9cc`，`exit_code=0`、`wall_time_seconds=0.151004166`、`original_token_count=542`；子进程status=0、signal=null、stderr为空，`crossLanguageEquality=true`、`pythonAdditionalHugeNaNInfRejected=4`。这次没有只抽stdout或只引用调用存在；完整结果与修前缺外层退出对象的记录明确区分。

修后起始哈希/读回命令完整返回为chunk `627453`、exit_code0；末次5hash命令完整返回为chunk `d4f332`、exit_code0。本轮仅追加本报告；仍无产品/测试修改、完整矩阵重复、GUI或发布声明。第5节所有真实producer/运行时/双审/发布边界继续保留。
