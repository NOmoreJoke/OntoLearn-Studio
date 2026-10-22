# 四资源私有只读采用：独立静态审查 R1

2026-10-22。结论：**Pass，仅限本次四资源 owner offer 的纯静态文档范围；没有发现需要阻断该接收的 P0/P1/P2 问题。** 四路径均接受其固定6891原字节的私有、不可变、只读使用；不签运行、构建或其它入口。没有把原HOLD／blocked状态改为通过，亦不替代指定外部双模型。

## 1. 身份与审查范围

独立审查者未参与候选实现。worktree为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-i05-semantic-resource-offer`，branch=`docs/T01-i05-semantic-resource-offer`；base=`5f910b52c69d86a1076b2032e5d3c63e715947f3`，被审candidate=`4064b216635f9b7a472879b31b07033edf14d185`。

已全文读取本次root窗口4478 B／SHA256 `12de397294435b7335a26bfd2635e156148cd1bdb092f65da9fd0a30d59480a7`、新树受保护AGENTS15852 B／`78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`、root限定closure、固定docs `ee2b30a2dad35b2d395f9c735aff80371ab41110` 的合同§5.1–5.4、对应静态闭包／资源调查，以及主offer、verification、dispositions、两份审查工具源码。候选26文件全体已从固定Git读取，对应25件manifest及17件原输入全部逐bytes/SHA核同当前；不是仅核件数。两份作者JSON静态证据也完整解析并检查其方法与边界。

必要产品源码只取 `6891a5842302859a531cf82767c5a482417bc274` 或基线5f固定Git文本；未import或调用。主线审查工具未重跑；本审另写独立小脚本抽取／对比，证据见同目录 `review_check.py`、`independent-check.json`。

## 2. 逐路径决定

| 6891固定路径 | bytes／SHA256 | 独立决定 |
| --- | --- | --- |
| `packages/contracts/python/contract_v2.py` | 34608／`17aa68bc2271b45ffb70a023b9db9e441bb1b4e79fc9a42bb6932f60631be7b7` | 接收，仅原canonical CONTRACT启动与普通固定error闭包；不扩大validate名称或执行其它公共helper |
| `packages/contracts/v2/schema.json` | 207256／`e913138e6f3ac632268ae7f8c2461577022e8298d1c03e0668416a0d654eaabf` | 接收，仅启动与普通error结构；其包含的新增v3定义不授运行权 |
| `packages/contracts/v2/registry.json` | 15962／`1f2e298209e238433c02864a05c70b24482e4c1fd00e7309f63eac84a1f3706b` | 接收，仅原启动读取与实际字节hash；不授capability／ready／profile dispatch |
| `packages/contracts/v2/errors.json` | 16299／`ad242d93ced7a0c8a463b708b7a1f3105e65f03c3980e0a0c6c4309f8c26544c` | 接收，仅普通26码和原有限参数；startup/business3分支仍在本次使用面之外 |

四项身份分别独立对照窗口字面值、固定Git与保存原件。没有接受替代ref或混合5f版本；公共维护责任不转移。候选实际diff只新增本授权的26文档／证据文件，没有产品文件，AGENTS没有被stage或提交。

## 3. 实质核验与发现处置

### R1-01：顶层读取不是无副作用

已直接检查固定checker第6–16行、resources全部97行：checker顶层stdilb imports和三JSON读取真实存在；resources第14–20行动态执行checker，第21–22行再次读registry并hash，第23–32行读lock并生成IMPLEMENTATION。主offer§3对此明确，没有把静态“只读采用”描述成无顶层执行或无资源读取。动态模块未做sys.modules缓存的事实也已保留；单实例是后继真实验证要求，而非本次已证事实。此项通过，无需修订。

### R1-02：允许闭包与禁止入口

独立AST核22个固定模块身份，并按显式相对／绝对ImportFrom和Import重建128条literal边，与供方闭包逐边一致。实际命名资源调用为semantic_execution第731行semantic_identity，以及resources内普通ERROR_CATALOG／validate-error。允许error校验的validate、check、equal、semantic、encoded_size、_changeset_semantics六函数之lexical调用未到达read_text/read_bytes、derive_dependencies或permits_transition；`_changeset_semantics` 对固定error名称落到第309行True。

resources第97行确有main内resource_manifest调用；该main不是本次入口。候选已明确拒绝直接或间接调用这一入口，没有将函数存在误报为自动执行或把它隐去。checker第724/818行dependencies/states延迟读因此不在本用途闭包；如果新probe改用这些helper，须新owner delta。两个quality懒导出仍禁止调用；AST不证明动态导入或未来probe行为。此项通过，无需修订。

### R1-03：兼容性不是“位于供应ref所以接收”

独立JSON／AST比较核实：原66项schema定义全部相同，供方共94项；原24个capability逐值相同，供方共27项，v2Runtime相同；errors原顶层字段全部相同，普通26码逐项无变。26个error oneOf分支的code、messageKey、retryable、paramsSchema、required与additionalProperties逐项核同，607个本地ref都有定义。旧checker函数中只有validate增了新语义分派；对获准error域无新增资源读。主offer明确区分新增changeset/business3/startup数据与普通error用途，不授新的公共契约运行权。此项通过，无需修订。

### R1-04：路径、额外lock及canonical身份

resources source定位packages/contracts，frozen定位_MEIPASS/contracts；checker从自身路径定位相邻v2，故主offer保留python/与v2/目录层级正确。lock source在仓库根、frozen在provenance/uv.lock；它不是T01本四件批准，仍须T03/root固定组合。原registry被读两次，需同一原字节；源码相同不自证运行时单实例。主offer§5及§6没有漏掉lock侧读、loader布局或未来probe再审条件。此项通过，无需修订。

### R1-05：未借四资源接收关闭其它门

已读顶层清单及固定semantic_offline文本的相应记录，audit hook/logger filter属于真实导入副作用；主offer没有以T01四件owner身份代签完整语义导入、第三方物理资源或whole-H。T03 writers、lock、模块未来维护、许可证、实际source/package/parent、平台与指定外审均仍有独立门。SQLite损坏输入保护HOLD、被拒SQLite/heap/OS线和原Goal blocked保持。此项通过，无需修订。

### 非阻断限制

原样资源的目录放置、路径／符号链接行为、实际frozen archive与runtime单实例、第三方传递资源、error实际执行及新probe完整调用面未运行验证；它们是窗口明确排除／后继门，不是本静态owner offer已通过的事项。Prettier不可用也没有被改写为通过。无新增整改项，不需要用替代ref或产品修改修复本offer。

## 4. 实际执行与准确边界

- 只运行普通Git固定文本读取／diff和stdlib审查脚本；独立命令 `python3 -X utf8 docs/reviews/T01/i05-semantic-resource-offer/independent/review_check.py` 实际exit0。它未调用作者脚本或供应函数。
- 独立结果2655 B／SHA256 `d5ea0285d766352970a975f8767f7d572da46b1202bae6dac606bf4bd44b0e45`。它核全候选原字节、25项manifest、17输入、四件窗口身份、差异及schema／catalog／import边；不是只看现有绿结果。
- `git diff --check 5f910b52c69d86a1076b2032e5d3c63e715947f3 4064b216635f9b7a472879b31b07033edf14d185` 实际exit0；独立UTF8/JSON/LF/尾空白核验exit0。本树local Prettier不存在，PATH也没有；未安装或借共享可变依赖，未运行Prettier。
- 没有产品imports、checker执行、tests、build、DB/SQL、native、业务child、GUI/桌面、网络、T03计量、指定外部模型、push/PR/merge；未改任何候选、AGENTS、旧树或Goal。普通git子进程不冒称为业务试跑，也未声称完全没有子进程。
- 本轮未遇自动审批拒绝／检查失败；没有首轮失败被覆盖。独立报告及小证据仅新增于independent目录；完成后停止写入。主线应全文读本报告，并在自己的处理记录注明R1-01至05均无待修，不把Pass扩成运行许可。

## 5. 首轮结论增补：总控新增格式证据

前7960 B原报告完整保留。本增补形成当前R1最终结论：**不通过，仅因已确认的文档格式门；§2–3的限定实质接收结论仍为Pass，没有新增资源采用语义阻断。** 主线在本报告完成后转达总控对固定4064b21所作现有Prettier只读检查：实际exit1，仅以下三件不符；并另授现有固定3.9.10 formatter路径。此前“工具不可用／未运行”的记载是本审当时的实际操作，不覆盖总控后来取得的证据。本审遵嘱未重复检查，不冒称自己运行了该formatter。

### FORMAT-01（P3）：三件新文档未满足格式门

- 位置：`docs/iterations/T01/i05-semantic-resource-offer.md`、`docs/reviews/T01/i05-semantic-resource-offer/dispositions.json`、`docs/reviews/T01/i05-semantic-resource-offer/static-audit.json`。
- 触发／证据：总控对固定候选使用既有Prettier 3.9.10检查，主线转达实际exit1和上述三件名单。此项为新增格式验证事实，不反推产品行为失败，也不声称源／raw数据损坏。
- 影响：静态owner offer的实质结论可保留，但本地文档交付尚不能记全部验收通过。
- 最小处理：主线仅格式化这三件，保留原.raw与本首轮报告；重建变化后bytes/SHA清单和准确验证记录，固定新候选，再交独立delta复审。不得批量改冻结原始输入或把本R1不通过改成通过。
- 实际可用工具由主线另获授：`/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/node_modules/.bin/prettier`，3.9.10；本审未连接该依赖、未运行或修改它，未更改任何被审文件。

收到此新增事实后仅追加本节，原候选仍固定4064b21，独立证据脚本／JSON未重跑，所有实质未运行边界和HOLD保持。后续通过只能由新候选的复核形成，不覆盖本轮不通过。
