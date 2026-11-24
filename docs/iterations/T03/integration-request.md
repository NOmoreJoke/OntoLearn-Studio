# T03 精确集成交接请求

基线 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。本文件最初为接口/依赖提案；当前四个依赖与构建文件已由总控正式交接给T03，并在本树实现最小项目增量。T00/T01/T02公共业务接线仍为待落实请求，不能据此发布产品能力或采用未批准候选。

## 已实现的私有服务

- `mapping.source.parse_csv(bytes, encoding=...)`：UTF-8 默认，其他允许编码显式选择；`parse_xlsx(bytes, sheet=...)` / `xlsx_sheets(bytes)`：真实候选 openpyxl 只读解析，不执行公式/宏，只读保存缓存。返回不可变 Table，保留 source hash、sheet、源行、字段、原字符串/观察类型和真实样本。
- `mapping.plan.preview(Mapping, Table, trusted_snapshot)`：稳定单/复合业务键、关系引用、明确转换、全部 RDF、增删改/身份变化/人工值/所有权冲突、源行计划。没有文件路径读取、IPC、模型或写入。
- `mapping.plan.checked_plan(old_preview, current_mapping, current_table, current_snapshot)`：重新计算并比较项目/revision/完整快照/源 hash/定义；旧预览或阻断拒绝。返回已批准 Store 的 `base`、`mapping={id,rows:[{row,facts}]}` 和 `definitions` kwargs。没有第二 Store/网关/可变权威。Preview 为进程内可信对象，不接收 renderer 反序列化实例作为授权。
- `mapping/MappingPage.tsx` 与 `mapping/model.ts`：受控的私有页面和草稿/迟到结果隔离辅助函数。展示用类型仅为内部 view model，不是公共协议或桥接替代。尚未挂入 App；回调未接入时明确禁用文件选择/提交。

## T00 / I06 唯一公共契约及接线负责人

涉及已有共享路径仅由原 owner 维护：`packages/contracts/src/{index.ts,v2.ts}`、`contracts/v2/{schema,registry,errors,fixtures,binding-regressions}.json`、`apps/desktop/src/main/{index,task-service,engine}.ts`、`preload/index.ts`、renderer 的 `env.d.ts/App.tsx/style.css`。本线没有修改这些文件，也不自行新增另一份公共契约。

需要正式方法/严格成功失败样例：

1. 受信主进程文件选择 CSV/XLSX，返回绑定项目/生命周期的不透明选择标识；读取前、预览前及提交前重新核对文件指纹；不接受 renderer 指定任意文件路径。选择 XLSX 时列出实际工作表，由用户明确选一个；CSV 编码显式传枚举。
2. 根据选择标识、mapping definition/version 与项目当前不可变快照生成预览；返回受限 `resultId`，完整集合按已批准统一分页形状读取。错误码复用唯一公共清单，由 owner 确定本服务内部 Issue 到 messageKey/安全定位参数的映射，不能把 SourceError 原始异常直接跨界。
3. `mapping.commit` 当前 registry 是 `design-only`，必须在实际业务参数/预览/确认与服务接入、联验后才能改为可用。提交只接受主进程保管的预览/result 身份、确认和 project/revision；重验完整输入与 T02 定义，交 T01。保留 I04 job/operation/取消/提交标记对账，响应丢失不得自动重放写入。
4. Python 完整预览中的原值只可进入该项目已授权的本地展示；不能放进错误信封、普通日志或自动外发模型。内部字段名/sheet 由公共 owner 转为白名单且有长度上限的定位标识。XLSX 不可用、空缓存、宏/XLS/加密与资源限额均需明确提示，不能当空文件导入。

成功样例：`tests/fixtures/mapping/equipment.csv` → `urn:example:equipment/001`、`002` 的 rdf:type 与 name 四条完整事实；源行为 CSV 2/3。失败样例：空/重复键、非法转换、人工漂移/墓碑、所有权冲突、源/定义/revision 过期；具体固定断言见 `test_mapping_plan.py`、`test_mapping_source.py`。

## T01 项目与事务负责人

- 批准基线可用 Store 形状已真实测试；这些测试是服务层整合证据，不是 T01 正式应用服务已接入。
- 基线已有 `Store.snapshot(project)` / `load_snapshot(id)`，请正式应用服务复用其同事务不可变输入（project、projectRevision、dependencyVector、state）；不可分两次读取 revision/state 后冒称原子快照。
- 受信应用服务保管旧 Preview；提交前重读源 bytes、映射定义和一致 snapshot，调用 `checked_plan`，在同一 Store.commit 内再次检查 base 并提交 mapping 与 definition。此处定义保存含 mapping version、全部规则、source hash、sheet；source row 使用规范 JSON 字符串 `{"sheet":"CSV","row":2}`，Store 按不透明来源字符串存储。
- 冲突暂停整批；本线只输出当前/源/managed/owner/row，没有静默恢复接口。若放弃人工值，T01 必须另生成预览及单独确认 ChangeSet，显式 edits 恢复 managed_value 后，再重新预览映射；墓碑亦如此。
- 与 T10 迁移保留 facts.owner/source_row/managed_value、映射定义/source hash，缺原始源文件须明确不可直接重跑；重新关联源文件后才能重跑。实际迁移验收留在父功能。

## T02 / T08

T02 提供批准的类、属性、单值声明与身份引用规则，正式 handler 必须做语义校验；本线只验证绝对 IRI 和确定性转换，不宣称已验证任意本体定义。T08 只增强建议草稿；离线 `suggest` 按精确字段名返回真实样本和依据，不自动应用，不调用模型。

## 已生效的 T03 四文件依赖/构建责任与 T11 平台验收

拟引入 `openpyxl==3.1.5`（MIT）、`et-xmlfile==2.0.0`（MIT）、`defusedxml==0.7.1`（PSFL）。官方元数据、源码链接与全部发行文件 SHA 见 `parser-dependency-candidate.json`。defusedxml 必需，缺依赖明确 `XLSX_PARSER_UNAVAILABLE`，无不安全降级。未另建锁。总控四文件交接已生效后，T03实际修改本树 `packages/engine/pyproject.toml`、唯一 `uv.lock`、`scripts/build-engine.mjs`、`packages/engine/entrypoint.py`，仅增加三依赖、收集和受限探针；CI/resources/verify脚本/其他共享路径未改，未采用I05未批准源码或锁。

独立候选探针命令：

```sh
uv run --frozen --with openpyxl==3.1.5 --with et-xmlfile==2.0.0 --with defusedxml==0.7.1 pytest packages/engine/tests/test_mapping_*.py -q
```

T03作为已交接唯一owner已更新项目声明/唯一锁与构建入口，保留原资源收集并显式collect-all三解析库（含metadata/许可证）。项目frozen环境55项mapping测试零skip通过；依赖候选尚未通过指定外审/合并。`npm run package:dir` 后从包内执行同一固定 CSV/XLSX（含稀疏空值、公式缓存、宏拒绝）探针；Windows/macOS 各自的真实引擎/干净设备证据必需。隔离 overlay 通过不能证明项目依赖、包内或双平台通过。

解析限额当前是防御性候选上限（8 MiB 文件、64 MiB ZIP 展开、50,000 物理行、256 列、32,768 字符/格），不是 Q5 业务容量通过线。正式 owner 可按统一资源 profile 调整并重新验证。

## 候选探针补充与页面生命周期

包内探针入口候选为 `python -m ontolearn_engine.mapping.probe`（真实 CSV、openpyxl 生成双表 XLSX、精确四事实和字符串身份）。总控生效交接后由T03在本树正式产品entrypoint新增 `--mapping-probe`，只运行固定合成样例；拒绝任何额外路径/脚本/URL参数，错误使用固定脱敏诊断。没有扩为业务能力注册或通用脚本入口。独立 PyInstaller 首跑已发现需要现有 `invalidation-v2.json` 资源（plan 复用 approved Store.digest，间接导入 invalidation）；构建入口须保留现有资源收集，不能仅拷贝 Python 文件。

页面 owner 适配时必须使用 `selectSource`、`updateDraft`、`cancelPreview` 增加本地 generation；预览事件记录当时 generation/selectionId/sheet/encoding，迟到回调不得改用到达时的新代次。公共协议仍由 T00 唯一维护；这些字段仅是 renderer 请求上下文，不是写权限。服务端继续以真实 source/table/snapshot/spec 重新校验。取消本地预览与实际 I04 job.cancel/持久标记对账分开，取消请求不证明正式事务未提交。

已生效交接依据：仓库外 `I05-T03-build-ownership-handoff.md`，独立复核 SHA `072dff2749fb32eb6852109761b73087e696ae2b748a949c19e7a10c4225f0cd`；本线双树实体核验/接受与生效记录 `../../reviews/T03/build-ownership-acceptance.json`。运行结果以最新 `../../reviews/T03/status.md` 为准，不沿用初始proposal或overlay的通过范围。
