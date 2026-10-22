# C1 Stage B 有限终止候选

基线为已冻结 Stage A `c268408d295cdae7aecae5dc9e52438b98bad024`。本轮仅修改 driver、适配原快照检查并增加有限终止专项检查；observer、产品、旧验收、超时、adopt规则及旧650 classifier均不改。根正式合同为 `T01-C1-stageB-finite-termination-controller-audit-20261023.md`，8466B / `f2f81fa927b2b27930abb5fe91b86ed919f2d046831638dfb009c838c9f9ab42`。

## 行为

历史displayUnknown与有限终止事实分账。只由本方原ChildProcess有序exit0/close0建立其自然关闭；helper没有独立退出码时记null，不借main close冒充。全表采样必须严格开始于最后present区间结束及适用原close接收之后，并追加独立、完整的已知PID查询。保原始argv、采样起止、exit/parse/UTF8/truncation、双流bytes/hash和输入源hash绑定；本树raw路径残余与原inspector端口仅按限定范围辅助核。

所有reported必须绑定known，模糊亲缘下新增candidate单独硬记账、不得adopt或signal。birth/明确exec冲突、生命周期异常、重现、容量溢出、诊断不全均保持硬失败；证书不能清除首因、超时或测试cleanup signal失败。首次证书必须落在原2s quarantine预算内。旧classifier逐字保留，SHA为 `68238542607e8992a4b58f38fa1b2c82a58bb3bbbbd874fff1de435dfb104c89`。

## 实际验证

最终driver为58047B / `bd6e1cdb8828eb0fa04d533e83d439a77365c948ef378fa6d673e960da80554a`；快照检查8817B / `ca486d4e1e4c5679c82c3989eacb7f211e8e89fe429963df6bedc8e004091c4b`；有限终止检查17443B / `5b9d7ebc63f2ddd8c13368fb459910eddc426579bf0289ee29f399894cd60895`。

最终真实源提取检查16/16、原快照检查10/10及定向Prettier检查均exit0。`npm run check`实际UTC 2026-10-22 18:58:15.281453至19:03:23.996003，exit0；lint/format/type/build/Ruff通过，Vitest1125通过，pytest2969通过、44按原条件跳过。stdout8689B / `e95a9e2ec5c68d81a463b0ea700d851ba6d2c7b9d2a22fbaf00bae6fc7e8c5f9`，stderr0B。Python284.05s为本次执行耗时，不是性能提升证据。

本树自有node_modules/.venv，安装按锁；捕获器SHA `87937663b03f2a2043685dbb02e6e5213288dcdd9ef6643659ae8645e92c9572`，cwd/venv/cache/TMPDIR均限定此树与本方输出。942件检查前后逐字节身份相同。此后只增本方过程文档，不机械重跑产品检查。

完整原件位于工作区 `outputs/20261022_review_backlog/T01-C1-finite-termination-20261023/`：frozen-proposal、independent-reviews、raw各运行、pre-final-check-identities及post-final-check-source-proof。raw子目录包含所有首次失败和最终终态，不复用slug或覆盖。

## 验收边界

独立静态审查及本轮受控源检查/完整check均不等于新native验收。本轮没有运行GUI、原e2e或native，没有安装/运行本树Electron二进制，也未做OS/ABI研究。旧650/native02/native03维持Fail；旧03的reported7/known6中74183未绑定仍阻断整run，不能用三个known的有限证书回填。新run若仍漏PID，须另报精确证据与最小捕获计划，不在本轮扩adopt或修改observer。

有限证书只陈述已建立owned集合及明确采样区间的终止，不证明整个模糊区间连续身份、合法exec、任意逃逸子孙或未来永不重现。候选须交总控固定身份预检，再按另行授权的指定审查/真实运行窗口处理；未push、PR或merge。
