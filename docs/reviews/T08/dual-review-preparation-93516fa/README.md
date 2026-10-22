# T08 指定双审完整准备包

状态仅prepared_not_dispatched。product `93516fa8455cf4b195cbfb699aa7a6652d428b6f` 保持；证据来源process `77c45949d39d797b39ef2cf30a10f3e1772730a1`，最终准备提交另由交付回执记录。没有任务ID、实际模型设置、指定报告或指定Pass。

先读input-manifest.json和full-review-input.md。两份独立prompt各含同一完整正文，差别仅模型/权限与唯一报告路径。全部25源码/测试/fixture和44项base→product差异已按固定Git对象逐字节快照；完整828项Git树用于核验上下文，不引入任何别线未批准代码。原PRD全文、当前政策、历史内审/失败/验证及缺口映射齐备。当前包只在docs/reviews/T08新增，不修改旧manifest或product。

固定清单packageFiles包括所有输入/正文/提示；input-manifest.json本身不自哈希，独立准备复核及root交付记录其实际SHA。包外独立复核/状态/未来报告不进入冻结输入，避免循环哈希。准备过程中如发现材料缺陷，修改本新准备包并重新完整核验，历史product/报告原件不变。

root短lease创建任务前，记录最终准备process、input-manifest实际SHA、真实task/session/turn、设置和命令执行授权。新运行不是本准备授权；不自动运行API、check、native或任何付费服务。关键完整验收缺失时不得Pass；静态代码审查必须完成，不因无法预判Pass而搁置。

归档理由：本包是两指定模型同源输入，需要逐字节固定已有源码、原验收与历史失败/日志，防止可变HEAD、临时日志和控制文件漂移；不包含secret、运行库或业务凭据。旧原check原件与三个gzip失败均作为输入保全，非新运行。

归档扫描隔离：23份TS/TSX/Python源码快照统一追加`.snapshot`后缀，仍逐字节等原Git对象；manifest保留原路径来源与实际快照映射。未改ESLint/Ruff、产品、依赖或测试配置。历史679/691/706成功日志仅有摘要及SHA，本包完整成功原日志为最新717项check。
