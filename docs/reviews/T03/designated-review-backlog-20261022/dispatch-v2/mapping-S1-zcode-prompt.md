# 不可变共享包入口（前向F1修复）

工程仍只读提示正文指定的本组工作树；完整发审包跨树只读，不复制、不拼装其它分支源码。共享包绝对根：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping/docs/reviews/T03/designated-review-backlog-20261022`。包固定Git ref：`ed9cef968b17a1edefc0977b509906fb9f81a336`，其Git仓库读取位置为`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping`。原candidate-manifest绝对路径`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping/docs/reviews/T03/designated-review-backlog-20261022/candidate-manifest.json`，固定Git地址`ed9cef968b17a1edefc0977b509906fb9f81a336:docs/reviews/T03/designated-review-backlog-20261022/candidate-manifest.json`，4301B，SHA256 `60c52bd13dac43bb9685b5233db817118dda10341357794d9f27500f07301e6c`。

本组完整输入绝对路径`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping/docs/reviews/T03/designated-review-backlog-20261022/mapping-S1-fixed-inputs.json`，固定Git地址`ed9cef968b17a1edefc0977b509906fb9f81a336:docs/reviews/T03/designated-review-backlog-20261022/mapping-S1-fixed-inputs.json`，241447B，SHA256 `ddbeeb2177a5ca9a3f070f50db15239e12dab760c7f85f8bc58aab7c98476995`。历史矩阵与覆盖关系为共享根下`historical-stage-inventory.md`、`coverage-matrix.json`、`coverage-summary.md`，均从上述同一fixed ref读取并逐件对原manifest核身份。可通过指定mapping仓库的只读Git show读取该ref:path；不能在本组工程猜相对路径、搜索一个未固定版本，或切分支。

下文旧“本包”均指上述**外部只读共享包**。当前新提示属于dispatch-v2前向定位修复，旧19原件及Fail报告保留，不用新提示覆盖旧candidate-manifest。实际任务ID、设置、终态及lease仍未发生。native当前仍禁止派发；三组现有工程可按真实短lease创建。操作政策在总控根目录使用最新原件；当前3160B/SHA2032bd9e1cdbf398a0d505e092e1a08b80ff15df26b1d06c7d7e1c2e0a5a8ec1说明T06已释放前台、仅创建/设置/读回短lease、后台推理不独占整个应用；不向用户索要桌面时段，不扩大native/static执行边界。

---

# T03 mapping-S1 完整独立审查提示：zcode

这是待实际创建的任务输入，实际task ID/逐任务设置/lease/终态均未发生。要求设置 **GLM-5.3 / 最高思考 / permission.mode=yolo**，必须从真实任务读回。只读审查，不修改实现/测试/依赖/配置/验收，不安装、提交、推送或创建PR。与另一模型独立，不传递本轮意见。

精确工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping`；分支 `feature/weekly-t03-mapping`。批准base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；产品/验收候选 `30319412daf8ae4745987babf7bbed93c53b6b42`；完整证据固定ref `3c396070c74fbf09cf319b0230c6f96ed2858482`。本包 `mapping-S1-fixed-inputs.json` 列出完整工程全部tracked路径及blob身份、base delta，不只修复delta。必须审完整源码、工具、tests、fixtures、配置、依赖锁和全部原验收/失败/缺证。工具位于docs或扩展名.py.raw/.input.py.txt也不能漏。metadata清单不是作者已全文读所有载荷的声明。

从固定Git原件读取。过程ref全部非docs工程字节已逐blob等于产品；process中后来追加或修改的证据工具另列laterEvidenceHelperDifferences，亦须按本次完整process审查，不能因位于docs漏审。后续本包纯流程commit不改变产品。若实际工程/测试/配置/依赖/验收或base变化，报告归属差异，不沿用旧Pass。禁止切分支、checkout/reset/fetch/cherry-pick或把不同树互斥共享文件拼成一个运行候选。

完整原依据包括本树PRD `docs/prd/PRD-本体学习与落地Agent工作台.md` 的全部FR-300–304、附录C–G（D/G.1 M-01–06）及§10–12；M0架构S1/S2/S3/C1/B1/U1及当前实际AGENTS；父I05/native相关完整原合同/57P0继续保留。每个局部、父业务、平台与发布门分别判断，不能排除未验部分后给整体Pass。历史阶段和后继见本包historical-stage-inventory.md、精确覆盖见coverage-matrix.json。首读入口（不是范围排除清单）：

- `docs/reviews/T03/current-candidate.json`
- `docs/reviews/T03/project-candidate-validation.json`
- `docs/reviews/T03/status.md`
- `docs/reviews/T03/product-package-verification.json`
- `docs/reviews/T03/round-1/scope-and-evidence.md`

现有证据：638 TS /1110 Python/0 skip，mapping58；原0ad unsigned macOS27 arm64包11 CLI通过。303新增OOXML/CSV边界只有源码测试，未新包复跑。父业务/两OS/GUI/安装签名待验。

当前完整共同指南/操作政策/权限及第九节在 `/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release` 的developer-common-instructions.md、desktop-operation-policy-20261022.md、external-review-permissions.md，须全文读。当前AGENTS为15147B/de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4受保护未暂存。用户已撤回静默桌面要求；旧待用户桌面时段/先CLI登录不是现行阻点。实际CUA短lease由总控内部交接，提示存在不证明lease。

本轮先审完整固定工程与既存运行原件，不新运行产品或验证命令；没有变更不强制重测。若完整判断确需新运行，报告精确命令/原因/所缺执行权，由原owner按实际阶段权限处理。尤其旧HOLD/自动拒绝/native未签票、caller及其局部函数、runner/reader、dry-run/fixture/模拟、编译/ABI/loader/drain不得由模型代跑。完整仓库源码和工具源码在本次静态审查范围；未获当前读取授权的SDK、工具安装/二进制身份载荷、原witness/descriptor/index身份payload及归档载荷不重读/解码，按原fixed manifest逐项明确未验证，不能谎称已全文审读。父runtime缺证不永久排除其余已有源码审查；需要该缺证才能判定的门明确不通过或无法验证。既有票不借/退/自提高guard，不读密钥，不新增付费或模型API。

首失败、历史HOLD、全部报告原件保留。内审不算指定Pass；源码、运行、打包、目标平台、生产/父业务分别给结论。未实测性能不量化，不能只看最后success、数量或作者摘要。完整报告含真实应用task/session/turn及实际设置、工作树/分支/base/product/process、全文读取覆盖、实际命令和结果或未运行原因、全部意见严重度/文件行/触发/影响/证据/建议、历史逐项处置、全部原验收矩阵、未验边界及明确通过/不通过/无法完成验证。真实终态后必须全文读回，不能只报阶段摘要，不能强行把任何模型不通过改为通过。

报告建议路径为本树 `docs/reviews/T03/designated-backlog/mapping-S1/round-1/zcode-glm53.md`，须原owner实际调度确认唯一报告写面；尚未确认时返回完整原文供owner封存，不擅写别处。实际模型设置和task ID留给真实派发收据，不在本提示伪填。

本阶段状态：PREPARED_NO_ACTUAL_TASK。可在短lease交接后创建新独立完整任务，不因父runtime缺证无限等待。
