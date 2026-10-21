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
