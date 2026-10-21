# 四个 SHACL shape 前门修复

本窗口仅修复四个已有规范红：合法 `sh:datatype rdf:langString` 以及 inclusive 的 `xsd:nonNegativeInteger`、`xsd:dateTime` 参数进入原真实 Validator。保留原 NodeShape→PropertyShape 结构及完整报告，未改通用 `_terms`、query/rule 比较器、date 扩展政策或 illtyped 数据前门。

独立树 `.worktrees/I05-profile-shape-entry`，分支 `feature/weekly-i05-profile-shape-entry`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。adoption `6e64311957a43b725bfb3e5da88c8df29c000b87` 逐141文件采用原Git字节：6c139+9333 consumer C两源。完整受控142=141+新test，140既有只读；相对base实际产品差异133，另9受控项同base。实际product及逐current/Git/bytes/SHA见新过程 `candidate.json`。

唯一旧源码改动在 `_shapes` 两个白名单判定：datatype局部允许RDF.langString；inclusive参数局部增加已支持、仍须词法合法的nonNegativeInteger/dateTime。所有原类型、ill_typed、计数非负、属性路径、节点唯一性、外联拒绝仍走同一原gate。没有绕过 `_shapes` 直喂 Validator，也没有用 profile Calendar 比较器代替原 SHACL 关系。

新test仅向实际 parser/check_shapes 输入纯 dataTurtle/shapesTurtle，执行后才读取独立golden。wrap只调用真实 Validator.run并观察次数，不供应报告。四例完整比较conforms及focus/path/value/sourceShape/component/severity；dateTime两个显式offset等值conforms，早一秒为原MinInclusive违规。新增独立边界覆盖nni零/上限、非法nni/dateTime词法、date门仍拒、未知datatype、错误参数/结构、外联及illtyped数据仍拒。

实际首跑 `01-original-four-red` 四例均原前门失败，真实Validator0调用；完整双流/报告原件保留。最小修复后 `02-shape-special` 26 passed，`03-shape-ruff`通过。每run独占basetemp、真实argv/cwd/env/gitHead、142成员before/after、完整报告/双流及结束成员hash独立保存，记录只在新目录创建，不轮转覆盖。shape未新增费用域或采用DAG新池；原报告与费用边界不伪补新usage。

冻结产品为 `3bd19e347051627242197f15fce712c9c9dd6b8f`。`04-normal-check` exit0：1125 Vitest、4913 Python passed/44 skipped，lint/Prettier/typecheck/build/Ruff/格式均完成；142来源前后相同。`05-verify-sources` exit0核12归档源。独立审查在固定产品上通过：26专项及原13格实际探针与规范一致，完整AST核仅_shapes两局部集合变化，140只读与142来源核同。26与13覆盖重叠，不相加冒39；44原skip不冒通过。

已全文读回独审 `independent-review/report.md`（11127B，SHA256 `3915d61ad0129749e3967793c51bd8181571595d9b0d9c5c3ec1e1fa08d74c8f`），无已确认阻断。独审首次系统Python3.9辅助失败、元数据格式首警及作者原四红均保原件；实际验证终态和成员hash见 `validation.json` 与 `final-manifest.json`。正常check不等于所有历史原始日志均能通过空白检查；首红双流原样保留。本窗口不自动采用进directsteps或T01，根读回后再精确回供T05；原四首红、两fixture/golden、其它原数学/83和受保护原件不改。没有GUI/native/e2e/网络服务/模型/付费、push/PR/merge或Goal修改。
