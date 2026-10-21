# T05 本地验证证据

范围：base `5f910b52c69d86a1076b2032e5d3c63e715947f3` 上新增私有定义/计划/比较/UI与样例。未消费未批准 I05/I06。远端 develop 实查仍为相同 SHA。

## 初始与复测

- 环境：独立 `npm ci --ignore-scripts`、`uv sync --frozen`；未修改依赖清单或锁；没有启动安装产物。
- 首次定向 ruff：4 处 E501 长行，格式化后关闭；首 pytest 42 passed。最初 ruff 自动修复另 2 处；没有把失败写成通过。
- 首全仓 `npm run check`：退出 0，16 个 TS 文件/633 tests；1094 Python tests；lint/格式/类型/构建/ruff 全通过。
- 内审修复后第一次完整 check：退出 0，TS 635、Python 1097；运行期间又增加依赖键 Unicode 修复，因此不能用此日志作为最终候选全检查。
- 最新定向：Python 49 passed，Vitest 5 passed；真实执行本地纯算法与校验，不代表推理器/SHACL/GUI执行。
- 49 项定向版本全仓 check：退出 0，635 TS / 1101 Python。
- 后续仅补常见 datatype 模板 IRI 和四个回归，最新定向 53 Python 通过；该改动后最终全仓检查退出0：635 TS / 1105 Python，ruff/格式/类型/lint/构建均通过。

原始输出保留在本线本地日志；提交摘要及必要哈希，避免把重复全仓输出混入产品 diff。首次内审及复审意见与处理见 `internal-review.md`，所有未验边界保持。

## 未执行与限制

没有本机 GUI/Electron/e2e/native/HMR、凭据/真实安全存储/模型调用/费用/外发。未改 main/preload/bridge/依赖/归档源，故未新增本机 e2e、包内或 source 验证。页面经过 TypeScript 静态检查，尚未挂到 App；未作浏览器/原生实际交互验收。

执行器/Store/公共协议接线缺失，G.2 仅有私有输入和领域预期，尚无真实 actual/trace 或全 RDFS 闭包输出基线。双平台/包内/发布证据、指定双审/PR/CI/合并均未取得。

## 获批固定输入后的最终检查

固定873的manifest/17输入/PRD源全字节核对后，新增22项纯输入/plan适配测试。完整 `npm run check` 退出0：16个TS文件/635 tests，1127 Python tests，lint/格式/类型/构建/ruff均通过；原始完整日志 `check-approved-inputs.log` 本地保留。独立内审75项Python通过，完整实现与dcc5ec8无变化。无GUI/包内/实际推理/持久化/生产证据。

## FR-505 完整代表输入增量

`test_quality_fr505_inputs.py` 新增36项结构/计划/预期依据一致性验证；16个完整输入，真实执行状态均pending。最新定向由独立reviewer实际复跑111项Python通过；全仓 `npm run check` 实际退出0：635 TS / 1163 Python，逐文件原件在本地 `check-fr505-inputs.log`。这不执行原P0比较/推理；独立手工检查不是执行器替身。新增前首ruff长行失败经格式化关闭。

产品/输入已提交后的一次状态追加Python脚本发生stdin编码错误；实际没有改到这些文档，随后改用文本追加修正。无需重跑未变化产品检查；格式复核单独执行。

## 保存参数与真实 Store 增量

新增7项探针只运行固定批准格式2真实Store，临时SQLite的opaque质量定义完整往返/启停版本/历史/旧base/事务回滚/marker成立。独立reviewer实际复跑quality118/118，原13核心文件未改。最新全仓check退出0：635 TS / 1170 Python，原始日志 `check-store-probe.log` 本地保留；格式检查/差异检查通过。首次定向ruff长函数名E501经格式化修正，原工具输出保留。

没有T01未批格式3/服务、生产写入口、真实推理/验证、进程崩溃/IPC丢包、GUI/包内或上线验收证据。保存参数/引用包装提案已实际发送总控。

## 总控 R1/R2 后固定版本

`fff89f6` 升级为22个输入，18格同型比较含30个有向算子替换的可辨识断言。独立reviewer对完整本线重新只读审查，实际148项quality Python通过；最新全量 `npm run check` 退出0，635 TS / 1200 Python（原始 `check-fr505-r1-r2.log` 本地保留）。真实18格图执行、跨datatype支持及完整trace仍未运行；标量oracle自检不构成执行器实测。

后续同一执行器契约仅文档变化：执行Prettier与`git diff --check`，未重复未变化的代码检查。标准资料链接只支持值域/term语义参考，不证明当前库或提案的实际支持。
