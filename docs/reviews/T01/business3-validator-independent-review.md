# T01 business3 validator 独立只读审查

结论：本轮未发现可复现实质阻断，支持 **validator-only、runtime-disabled** 候选继续。该结论不批准业务3握手、Store/Job ready、source/parser/learning 接线或发布；不替代指定双模型审查和最终同版验收。

## 固定范围

- 来源：T01 开发者委派 `/root/store_interface_audit` 独立审查；后续追加两份纯设计文档复核。
- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions`。
- 分支：`feature/weekly-t01-project-transactions`；HEAD/base：`33a55907c2f4835d79701c8d5609ed6ffabaf208`。本轮受审实现/测试为其上未提交候选。
- common `ff5f9fd0a4913cc6c2fa612ec565bdf40d67db4a6640e5293d4ca1e7d02cfaff` 及既有无桌面/只读约束保持。未操作 GUI、Electron、e2e、native、HMR 或外部审查应用。
- 唯一写入为本报告；未改实现、测试、依赖、配置、AGENTS，未提交或切分支。AGENTS 的既有工作树差异不属于本轮修改。

下表在审查开始和结束分别实算一致；路径相对上述工作树。

| 文件 | SHA256 |
| --- | --- |
| packages/contracts/python/contract_v2.py | 7d1093059047ab930787fe16b356133199b7efd8e38b61f53655640aa2364a5f |
| packages/contracts/src/v2.ts | 81656b129dc3646fc9e66e2f8c111031d448e75bc626af4b3c57e1c1d0da17a8 |
| packages/contracts/v2/schema.json | 166dba53c482ba8d94778371165c89f0d250cd6daf130907ea5a916fd0816848 |
| packages/contracts/v2/registry.json | 04642f84124bc29ba3ee4092376e6c82d98c2e87a8353616734d0f419670dbc5 |
| packages/contracts/v2/errors.json | 5ac7c6a70dffc020f4b20fb8607890ac34888fa406afae8c2f9641f2f3f158eb |
| packages/contracts/v2/fixtures.json | 0b9be87eb05450a9385072ff79b4eef9431687589ed2d3252c23656648d5ee0b |
| packages/contracts/v2/binding-regressions.json | 45c1bd1775a819cb3d798416b103ad0fead1ae20e076b98ab3d27f9aa403b9a8 |
| tests/unit/t01-business3-contract.test.ts | bb3d02b4d6874a60743caf0d030ae3bd492ed3ab1c386873bc9ea4050f95af34 |
| packages/engine/tests/test_project_business3_contract.py | b157630df49d1a30310e881bb144a454db0e506ab9c7b487ecd493107bea9435 |
| docs/iterations/T01/business3-validator-adoption.md | ad6beab2f45f5d7e15009820f7722be978c1c4c56c9a491c5ab4599f8c658200 |

## 审查依据与结果

1. 新 request/response 分支只允许 bootstrap hello 外层2；hello 成功要求 selectedVersion3、非空且内外一致 session。后续业务帧外层3且非空 session。null-session 错误严格限 hello 的三种有限错误；旧引擎 `[2]` 诊断只能终止，不形成成功会话。普通业务 VERSION_INCOMPATIBLE 仅 `[3]`。
2. 两端绑定助手先通过完整 business3 形状、语义和编码预算，再复制并只投影已知版本字面值复用原绑定；没有先丢字段再验证、修改调用者对象或发送2降级帧。hello 成功另核实际可信预期 registryHash 和允许方法集合。实际预期构建 hash 的加载、会话作废和 Store ready 仍是未来运行时责任。
3. 原 response 的 project/job/operation/input/confirmation/result/page 绑定及事件 subscription/session/sequence/state 约束继续复用。project3 只改变 formatVersion 字面值，不接受额外 metadata。
4. 机器对比 HEAD 资源：**全部原 `$defs` 定义不变**；registry/errors/fixtures/binding-regressions 的全部旧顶层值不变，新增 foundation/business3 区域单独承载。没有用“默认2仍声明”替代这个实际比较。
5. 新测试两端消费相同84 schema、15 hello、43 response、11 routing及41 trusted-binding 数据，数目和包装差异与采用文档一致。首跑196 TS/195 Python是开发者提供结果，本审查未重复该矩阵或正在运行的全仓 check；未把其进行中状态记为通过。

## 独立运行探针

均为当前工作树无窗口 stdin 脚本；不建测试文件或改产品。执行入口与输出如下：

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/contracts/python .venv/bin/python - <<'PY'
  # import contract_v2，读同一 business3 fixture，逐项 deepcopy 后变异并断言
  # matches_business3_response 的结果及原对象不变；比较 HEAD 与当前旧资源子树
PY
Python independent response mutations: 39 passed; input immutability passed
All pre-existing schema definitions and registry/errors/fixtures/binding-regressions top-level values unchanged

node --input-type=module <<'JS'
  // 现有 typescript 5.9.3 transpileModule 在内存编译实际 v2.ts 和 states-v2.ts；
  // JSON 资源保持实际值，zod 使用实际安装路径，data URL 加载；无落盘产物
  // 对相同39项响应及5项事件路由作断言
JS
TS independent response mutations: 39 passed; input immutability passed; 5 event route checks passed
```

两端39项具体输入选择相同：

- 从 `hello: success actual registry` 开始，正常成功1项；分别只改 outer session、inner session、外层版本3、result额外projectId、registryHash为0×64、capabilities为source.begin，6项均拒绝。
- hello offered `[2]`、`[3]`、`[2,3]`、`[3,3]`、`[]` 共5项；仅包含3且无重复的合法数组可成功，未以一般协商数组的存在误授予旧客户端3会话。
- `matching health/project.get/job.get/job.list/result.page/operation.get` 各正常1项，并分别改 response session=null、不同合法UUID、外层unknown字段，共24项；变异全部拒绝。
- 以 matching health 改成正常 session 的 VERSION_INCOMPATIBLE 错误，supportedVersions 分别 `[2]`、`[3]`、`[2,3]`，3项仅 `[3]` 接受。
- TS 另以 `valid job event` 正常1项，逐个改 engineSessionId/projectId/jobId/subscriptionId 为不同合法UUID，共5项仅正常项接受。

TS 初次尝试用 esbuild 在内存装载，在运行校验器前即因本树没有 esbuild 报 `ERR_MODULE_NOT_FOUND`；该次不计产品失败或通过。随后使用已经安装的 TypeScript 编译器成功完成上述真实探针，未安装依赖。原始工具调用保留该首次错误，不隐去。

## 设计复核（不作为实现验收）

另按追加任务只读两份文档：

| 文件 | SHA256 |
| --- | --- |
| docs/iterations/T01/source-lifecycle-decisions-r4.md | 17f34e57c503ddca2da18c1cb62eb22dab3b6fd250db5a600ce2a4c30930cb9e |
| docs/iterations/T01/source-table-digest-contract-r1.md | 7dd2d8e09dea2cfbf50dedb49b091433aaebda747850da4f338a706261b72cc0 |

生命周期 r4：未发现新增设计阻断。receiving 精确重复必须有原字节且未到期；sealed/终态不再返回 append 成功；accepted 先于冲突/release/expiry 时保护 durable claim/pin。旧 nextIndex 不回退进度；满256时先行 release 不伪造第257条 tombstone，以永久拒新 begin 加 barrier/fence 证明不能迟到分配。未知工作及未完成清理继续占账；读保护和正式写 pin 分开。此补充关闭 r3 重复 append 的终态歧义，当前不证明这些状态机已实现。

完整表摘要 r1：完整有序数组、全部行格、三字段 implementation、独立预期 sourceHash、原 Unicode/严格 surrogate、Python/JS integral-number 值语义及明确 UTF8/转义规则相容；强制 owner 总编码预算先于全量 clone/stringify，且不借其声称 RSS/Q5 通过，方向可接受。**实施前仍保留文档自己明确的两个精确合同门：XLSX sheet 的类型/空值约束、parser implementation 三字段的共同合法形状。** 当前文本没有给出这些完整定义，因此不能据本次设计审查称摘要 API 已可装配或 golden 已被实跑；这不是新发现的实现缺陷。未读取未批准 parser 实现，也未生成/运行这些设计 fixture。

## 未验边界与收口

本轮无新增需修复的 validator finding。支持纯 canonical 校验层继续；运行时 bootstrap/启动诊断/重复hello会话失效/迁移及任务对账之后才成功hello/真实子进程互操作、source与学习能力、包内及native、指定双审/CI均保留。两份设计可以按上述已声明门禁继续推进，不能算运行通过。本轮未复测已提交 source_content 产品。

## 表摘要设计修订定点复核

追加任务仅复核设计修订，未重审或复测前述产品。原被读文档 SHA `7dd2d8e09dea2cfbf50dedb49b091433aaebda747850da4f338a706261b72cc0` 及其当时两个显式合同空项的记录保留。修订后 `docs/iterations/T01/source-table-digest-contract-r1.md` 实算 SHA 为 `568cb308ec5db6b7b537b4a385958a475c200268d750cedd73bdb1e28ce65b79`，与委派值一致。

结论：两个显式设计空项已关闭，未发现本次修订新增阻断，支持按当前受限设计实施。

- Table.sheet 是合法 Unicode string、非 null；CSV 的 options.sheet=null 与 Table.sheet=CSV 区分。XLSX options.sheet 与 Table.sheet 精确等值，存在性由实际受信 producer 认证。未无依据增加31/32768长度、非空或控制字符限制；sheet NUL 明确按 `\u0000` 编码，仍受 owner 总编码预算约束。
- implementation 直接复用现有唯一 `$defs.implementation`。本次只读核对当前 schema 原定义，确认三字段全必需、禁止额外字段，两名称为 ASCII `[A-Za-z0-9_.-]{1,128}`、lock hash 为小写 hex64，与修订吻合；未复制或修改身份 schema。
- CSV utf-8-sig 明确为本次受限 profile 的技术选择，不将样本编码说成 S1 唯一能力；其他编码必须由 owner 冻结词汇后扩展。
- 真实生产 parser identity 仍缺，当前 golden 只能使用明确 synthetic 身份；这不阻止纯摘要器机制实施，但禁止据此声称实际 parser/生产身份、来源授权、运行时或公共能力已经接通。

本次只读修订文本与上述既有 schema 定义，仅追加本报告；未测试、改产品、修改其他受审范围或运行 GUI。前述 mandatory 编码预算、完整材料和真实接线/指定双审/CI 边界均不变。
