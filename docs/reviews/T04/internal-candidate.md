# T04 独立实现候选范围

2026-10-21。本候选只审查已批准 base 上新增的查询编写服务、独立页面和展示校验；原父功能全部验收继续由 status.md 追踪。不是正式外审候选，也未消费 I05/I06 未批准实现。

实现：离线告警模板、对象/条件/字段构建、完整 SPARQL 草稿；RDF IRI/语言/类型字面量安全序列化；严格保存意图；明确范围/当前与历史选择；真实结果元数据及分页绑定的展示；空页检查方向、载荷回收、CSV 当前页导出。页面无 Node、通用 IPC、网络或 Store，无默认示例结果。

共享文件无修改，保护 AGENTS 保持未暂存。使用新建独立 node_modules/.venv；依赖安装为 npm ci --ignore-scripts 与 uv sync --frozen，无锁文件变化。编写服务没有执行器；RDFLib 仅在测试验证合成查询的标准互操作完整集合。

首失败原件位于 evidence/check-first.log（正则 lint）；后续 check-second/third.log 为类型失败，check-fourth.log 为 import 排序失败；已修复。ssr-first.log 是探针误用本仓库未安装 esbuild 的模块缺失，改用已锁定 TypeScript 的独立 CLI 编译后，ssr-second.log 8 项静态渲染检查通过，无新增依赖。未将删除 JSX 单元导入当作 UI 通过：unit tsconfig 未启用 jsx 且属共享责任；使用本线 SSR 脚本另验，桌面 tsconfig 仍完整类型检查页面。

当前运行：npm run check 在 check-fifth.log；TS 17 文件/640 项通过，构建与 lint/format/typecheck、ruff 通过；Python 1080 项仍在运行，未先报全套通过。新增 Python 28 项已单独通过。SSR 为静态 HTML，不含浏览器交互、真实查询、存储/取消/CSP/性能/平台证据。

待独立只读内审固定 SHA；审查问题修改后再核验。指定 ZCode GLM-5.3/最高与 MiniMax M3.1-Flash/xhigh、实际 push/PR/CI/正常合并及远端核验仍保留，资源由总控预约。
