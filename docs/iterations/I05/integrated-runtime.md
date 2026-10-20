# I05：真实有限语义的运行接线

本记录描述 B1 候选工程验证，沿用原 PRD C/D/E/G、B1 原计划和 Q6 十二项差异。没有批准 Q2/Q3/Q5/Q6/Q7/Q8/Q9，也没有完成 M1 编辑器、映射、行为或沙盘。历史独立阶段和失败记录继续保留。

## 输入、执行与发布

`semantic.start` 是协调器的有限应用请求。主进程提供已授权项目并生成一次 operationId，三个业务命名 bridge 只选择已保存定义、断言/含推导范围及明确当前/历史输入。renderer 不传数据库路径、图、来源可信度、依赖向量、库选项或通用方法。失败、刷新和窗口恢复不会自动重放创建。

Store 在接受事务中校验真实快照、参数内容哈希、定义集合、来源版本与选中结果，将完整输入固定在 immutable Job context。当前输入要求当时确为最新项目快照；历史输入必须显式选择。选中推导只能是一个实际已有 reasoning result，核验项目、snapshot、producer succeeded Job/resultRef、定义/参数/依赖/实现三键、完整载荷及展示行内容哈希；当前选择还要求真实 current 指针。历史或 stale 只能进入显式历史输入，evicted 不可复活。投影从不重新执行被选中结果的规则。

SHACL 的 assertedFacts、ontologyAxioms、constraints、derivedFacts、derivedAxioms 分别存为真实内容寻址资源，角色/约束/结果/范围/实现关联由现有 canonical validationProjection/resource resolver 验证。原本体公理与派生公理独立，断言及选定派生类型均保留，不能整图充作 SHACL 数据。

隔离 worker 在读取输入前建立 C4 parent-owner 监控、内存边界，并以最小环境启动。准备请求不导入 RDFLib/pySHACL；真正 Turtle term、查询、RDFS/一阶段规则、SHACL 和既存结果投影在 worker 计算。私有输入/输出使用有序、逐字节哈希校验的 JSON 分块，单帧固定 262144 字节，重组总量 8 MiB；公开协商帧预算保持独立。总期限、取消、父死亡和 worker 故障继续由真实协调器管理。

完整语义 payload、稳定展示 rows、来源/内容哈希与 Job succeeded 同事务发布；取消、超时、回滚或未知内部故障不留下成功 current。迟到结果保留原输入，按依赖成为 stale/history。显式历史输入即使恰与最新快照相同也不发布 current。缓存回收同时清空完整语义 payload 与展示载荷，保留历史身份；固定输入/资源证据仍保留，I01 历史增长风险没有被本轮宣称关闭。

## 错误与读取

只注入完整 canonical catalog/schema。存储结构、已保存用户内容、词法预算、规则求值和最终展示投影在实际调用分支建立 Producer/Stage/Origin；不从异常正文或客户端自报字段推断来源。既有 25 规范行、75 期望及未知兜底保留。未支持的已保存 OWL/RDFS/datatype、SERVICE/imports、输入/工作/最终结果预算分别返回已批准安全 DTO；最终追加资源绑定后超限同样是 semanticResult。禁用规则不执行或消耗其词法执行预算。

完整 payload 通过 JSON pointer、part/parts 无损投影为有限标量 rows。长值分片不截断，达到总行/字节预算明确失败。现有 result.get/current/page 与不可变游标保留项目、输入、范围、参数、TTL 和回收校验；UI 分页显示真实 queryText、约束版本、违规位置、推导依据和历史标识，错误仍按四段式本地模板解释。

## 验证边界

Mac 仅 CLI/check/构建及未签名打包，未启动 Electron/native/HMR。源码和包内真实 stdio 可运行三类能力及选中来源；CLI 同完整语义样例、受控接收端、两档原口径/fresh 测量另存原始证据。实际匹配的 Mac CPython 与 Linux aarch64 CPython 具有独立来源与许可证；未知运行时明确 pending，CI 功能运行不代替其完整原生来源、签名、干净设备或首发平台决定。

Linux 原生验证使用 I05 自己的容器、数据库、依赖和产物；复用不可变工具镜像不等于沿用 I04 新版通过。先前缺工作目录/窗口管理器、namespace 权限失败，以及 1017 事实验收负载下的耗时探索保留。当前原生 fixture 保留 G-base 的全部 18 条事实、明确删除003名称作 V01，再加入10条独立负载事实，共27条；九重 COUNT 组合仍为十亿，真实 worker 接受取消。它不是业务容量基线；S1/B1 两档18/180测量口径不变。

隔离环境为 Chromium namespace 提供 SYS_ADMIN；不添加 no-sandbox、不禁 hang monitor。验收保留真实可见、外部 X11 焦点、renderer crash/infinite-loop/unresponsive、实际原生对话框操作和三窗口同一持久语义结果/完整来源。具体通过、候选源哈希、失败与限制以本轮证据清单为准；本设计文档不单独构成验收或指定双方审查通过。
