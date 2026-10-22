# 全新完整独立审查：M3.1-Flash

实际模型必须为 **M3.1-Flash**；思考 **xhigh**；本任务权限 **bypassPermissions**。创建/进入任务后实际读回设置，用户级默认不是会话回执，不擅自换模型或降低思考。若不匹配，记录并停止出PASS，交owner修正。

你是本轮全新、独立、完整的只读对抗审查者，不是开发agent，也不是继续旧审查。审查目标是给用户操作的完整阶段验收组合，不能只看摘要、只复核旧问题，或拿原基线通过抵新增组合。

审查包：`/Users/kyle/Documents/工作/知爻/本体/outputs/20261022_review_backlog/stage-review-package`。候选 `stage-acceptance-20261022-review-c1`；`payload-manifest.json` SHA-256 **1918d6d38c094885a37e88b9c746f433459abea4dbd1a0a9c99cfe258fcb7129**。两指定模型读取同一payload。不要读取另一指定模型本轮报告、对话或意见。可读取同包历史内部报告和失败原件，它们是共同既有输入。

先运行只读 `python3 /Users/kyle/Documents/工作/知爻/本体/outputs/20261022_review_backlog/stage-review-package/verify-freeze.py`，全文读candidate、payload/scope.md、payload/guidance/AGENTS.current-de15.md以及同目录最新桌面政策与权限规则。当前guidance SHA为de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4。人类已经撤回静默限制，允许按授权computer use及必要本机窗口验证；互斥资源由总控内部协调，不需要再向用户预约桌面时段，不把后台/headless/CLI登录作为前置。历史产物中的旧静默说明只代表当时操作，不是当前阻断。

必须阅读全文和实际代码，不只信作者报告：

- payload/artifacts/browser/entry.tsx、shell.css、build.mjs、verify-browser.py，34份固定snapshot及完整import链中的组件、controller/model、view-model、查询draft/results、学习content/presentation与schema；实际index和build输出；来源manifest与verification。确认没有以新仿制实现或活动树import代替固定已开发组件。
- payload/artifacts/根与两子目录README、stage-delivery、打开阶段验收.command。逐项核对用户入口、动作、预期、合成标识及未完成项与实际组件一致。
- payload/artifacts/desktop/reproduce-build.sh、probe-packaged-engine.py、packaged-metadata、manifest、app-files、code-parity、engine-probe、首败/签名/构建证据；payload/baseline-source中58份精确5f源参照，尤其main/preload/App/CSP/engine/build/builder代码。完整树身份及导出字节见baseline-identity与baseline-git-tree。基线已有审查不能转授给新增metadata与stage组合。
- payload/independent-review原报告/proof及现存截图、下载、快照。独立判断，不能把内部limited Pass当本轮指定模型裁决。

完整验收依据以scope.md为准，至少独立核对这些真实行为与边界：

1. 本地index可加载，classic内嵌脚本/CSS及CSP hash实际工作，没有HTTP服务/CDN/数据外发；不能禁浏览器安全策略冒充通过。
2. 本体合成目录精确搜索2项、树/局部图、内存表单、重置；真实预览/保存/事务没有接通，不产生虚构已保存状态。
3. 查询Sensor/temperature输出完整可核对SPARQL；执行/保存禁用、没有示例结果冒充实际查询。实际支持的编辑/模板/条件边界也检查。
4. 行为草稿、条件、动作、事件可编辑增删，真实试跑未接服务，不能产生run/committed；显示的项目与隔离字段只是合成说明，没有创建真实副本。
5. 课程任务/术语/技术定义可切换；“检查我的操作”可能可点击但正确提示暂不可用，不能笼统断言所有无回调按钮都禁用；没有假完成、假留痕或假持久化。
6. 真正触发并读取两种JSON下载，人工选择与反馈文字正确，版本和synthetic标志准确，没有自动上传。草稿切换/重置清空，与重置保留checks/notes及刷新全清的区别明确。
7. 在1440和390检查实际内部容器与重要控件bbox/可达性，而不是仅document.scrollWidth。学习路径内部有界横滑应可达；父overflow:hidden掩盖超宽子树必须报问题。
8. 原生metadata/productName/appId、实际Info.plist/ASAR与编译parity、两锁/文件清单、ZIP hash、探针十次health与18triples完整结果。原生userData隔离尚无GUI实际路径证据，仅静态依据，不能据名字不同判真实隔离通过；未签名/公证、无Windows/干净机、native恢复/新业务接线/完整发布均未验，不得补成已通过。

既有三P2必须逐项独立复核：首390学习子项宽1398/right1439被裁而document仍390，已改shell minmax(0,1fr)+子项min-width:0；重置提示曾错称验收勾选也丢失，现应保留checks/notes；根指南曾笼统称无回调全禁用，现区分课程检查暂不可用。旧失败、首轮漏检与修后原件保留。最终browser index为adff7f408e1844392d550a7e0a3bdacb5e1c1cd167b24d3b236a517456033a81。不得只复核三问题而缩减完整新审。

只读约束：不修改payload、已交付browser/desktop、原开发树、实现/测试/依赖/锁/配置；不提交、不推送、不切分支、不PR、不合并。完全访问是应用权限，不改变只读任务或付费、密钥、生产发布边界。原.app/ZIP未复制，请按external-artifacts.json只读核对现有绝对路径，必要执行verify-freeze.py --external。要运行先在你自己的scratch复制精确来源；源码和原包不能改。

特别注意：build.mjs会回写index/manifest；原生reproduce-build硬编码原树/输出，probe会回写旁边JSON，现有verify-wrapper固定browser session。**不能直接对冻结包执行这些会写回或争用的脚本。** 复制到你专属scratch后以唯一session/日志/合成临时库验证；允许改验证副本的输出位置和session名，记录差异，不修改产品求通过。GUI/native资源由owner与总控协调，当前不需重新申请用户时段；不控制另一模型任务。

无变化源码/锁/环境的既有构建或CLI探针可按精确身份限定引用，报告明确“读取已有证据、未重跑”；不机械重跑所有未变项。真实发现、候选/环境变化或关键证据不足时必要补验。这个包只做复制和操作规则更新，没有产品变更；不把准备行为写成产品验证或任务启动。

最终完整中文报告要列：实际任务ID、模型/思考/权限读回、候选hash；已阅读全文与关键逻辑；静态/运行/打包/生产证据分开；每个发现的P级、精确文件位置、依据、影响、建议；3P2逐项处置；未验证是否阻止本阶段；唯一裁决PASS / FAIL / NEEDS_EVIDENCE。阶段包自身必需未验不得PASS，不用“条件Pass”掩盖缺口，不拿已披露代替验证；也不能把明确未承诺交付的完整产品能力误称本包承诺完成。

仅写你专属reports目录的报告/回执和scratch，不读另一模型本轮目录。receipt里的session/turn、设置、终态和报告SHA必须实际读回，不能造ID或把任务创建算完成。你只给自己裁决；双方同一完整候选真实终态、全文报告owner读回、全部意见处置并明确双PASS后，才可关闭本stage组合外审。

专属报告：`/Users/kyle/Documents/工作/知爻/本体/outputs/20261022_review_backlog/stage-review-package/reports/minimax/report.md`；回执：`/Users/kyle/Documents/工作/知爻/本体/outputs/20261022_review_backlog/stage-review-package/reports/minimax/receipt.json`；验证输出：`/Users/kyle/Documents/工作/知爻/本体/outputs/20261022_review_backlog/stage-review-package/reports/minimax/scratch/`或报告明确记录的唯一临时目录。当前这些任务与报告尚未创建，请勿把路径预留当已有结果。
