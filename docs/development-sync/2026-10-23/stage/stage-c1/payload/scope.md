# 阶段验收组合：完整冻结外审范围

候选标签：`stage-acceptance-20261022-review-c1`。内容身份以包根 `candidate.json` 引用的 `payload-manifest.json` SHA-256 为准，不以目录名、历史内部 Pass 或单个 index 哈希替代完整候选。

## 必须读取的实际代码

1. `artifacts/browser/entry.tsx`、`shell.css`、`build.mjs`、`verify-browser.py`，以及 `artifacts/browser/snapshot/` 中34份固定文件。按其 import 链完整读取相关组件、controller、model、view-model、query draft/results、learning content/presentation 与公共 schema。确认原模块源码是固定提交原字节，外壳没有偷偷换成新仿制实现或活动树 import。
2. 实际 `artifacts/browser/index.html` 与 `build/bundle.js`/CSS，对照源代码与哈希，检查离线 classic IIFE、内嵌资源、CSP script/style 哈希、无网络与无业务服务 callback、下载和内存生命周期。
3. `artifacts/打开阶段验收.command`、根/两子目录 README、stage-delivery、manifest、verification；用户入口承诺必须与真正组件行为匹配。
4. `artifacts/desktop/reproduce-build.sh`、`probe-packaged-engine.py`、packaged-metadata、manifest、app-files、packaged-code-parity、packaged-engine-probe、首败、签名观察和构建原件；并读取 `baseline-source/` 中主进程、preload、renderer App、CSP、engine、builder和build脚本实际源码。`baseline-identity.json` 及 `baseline-git-tree.txt` 绑定原生既有5f910b5源码。基线已合并不代表新增打包metadata、脚本与这次组合自动通过。
5. `independent-review/stage-independent-review.md`、`stage-review-proof.json` 与现存原始截图、快照、下载、日志。它们是内部历史证据，须独立判断，不能当本轮指定模型裁决。
6. `guidance/AGENTS.current-de15.md` 与最新桌面政策，按现行操作规则执行；历史产物中的旧静默操作说明只记录当时行为，不是当前前置。

## 验收内容

- 离线文件可真正加载：无开发服务/HTTP端口，源组件仍有真实可操作行为；直接本地index不依赖活动源码或远程CDN。报告CSP实际执行、控制台和请求观察，禁止浏览器禁安全策略冒充通过。
- 本体：合成对象的精确搜索、表格/树/局部图、内存编辑/切换与重置；真实保存/事务/导入未接通，禁止虚构状态。
- 查询：现有编写器按Sensor/temperature产生完整可核对SPARQL；其他条件/模板/输入边界按实际支持检查。执行/保存不可用，无示例结果冒实际查询。
- 行为：草稿、条件、动作、事件编辑与增删；缺真实服务时试跑不可用，无虚构run/committed结果。字段中明确合成项目与未创建隔离副本，不能说真实副本已存在。
- 学习：任务、术语/定义和内容真实切换；“检查我的操作”可能可点击但只提示暂不可用，不能把“全部无回调按钮禁用”当实际结论；进度不伪造，提示留痕/检查/导出未接通。
- 真实触发并读取两种JSON下载。反馈结果、文字、版本与人工选择对应；样例标明synthetic且对象数/内容正确，不上传数据。无敏感业务数据或凭据。
- 生命周期：切换模块/当前草稿重置与刷新/关闭的区别。重置保留验收选择/反馈；刷新清空内存。提示与行为一致，不声称持久保存。
- 1440与390尺寸审阅可用性。必须检查内部容器与关键控件边界/可达性，不能只检查document.scrollWidth。学习路径有界横向滚动应实际可滚、可选；禁止以父overflow:hidden掩盖宽子树。
- 原生打包组合：精确名称/appId/额外metadata、产物身份/代码parity/锁、脚本异常处理、引擎探针与首败处置、未签名/未公证及平台范围。默认userData路径隔离只有静态依据，尚未GUI运行核验，不能据metadata不同直接记真实运行隔离通过。
- 跨模块业务、Store/bridge/Job/executor/model正式接线、native UI/原生恢复、Windows/干净机、签名公证分发与完整产品发布不在本交付已验证事实中。应检查这些缺口是否准确披露，不能用局部交互通过推导父功能通过；若某项是阶段包自身必须验证的阻止项，明确NEEDS_EVIDENCE，不以“已披露”掩盖真实缺陷。

## 已知三项P2，须独立复核关闭

1. `P2-MOBILE-LEARNING-CLIP`：首候选 c323ad6… 的document=390却surface.scrollWidth=1424、grid子项width1398/right1439；修复只在shell mobile采用minmax(0,1fr)+子项min-width:0。最终index adff7f4…；内部复验surface360/360、grid宽308/right349、提示最右332、术语最右328。内部path ol有界横滑1398/308不是全局裁剪。原失败与修后证据保留。
2. `P2-RESET-COPY`：旧提示错误地说重置会丢验收勾选；现提示准确区分草稿和全局记录，重置应保留checks/notes。
3. `P2-LEARNING-CHECK-COPY`：根指南曾笼统写无回调按钮全禁用，已精确改为执行/保存禁用，课程检查可提示暂不可用而不会完成。

## 只读职责与必要验证

- 不修改本包payload、已交付browser/desktop、原工作树、候选实现/测试/依赖/配置，不提交、不推送、不切分支、不合并。完全访问只是应用执行权限。
- 对源码、原.app与ZIP只读。巨大.app/ZIP没有重复复制，`external-artifacts.json`给出现有绝对路径与完整逐文件/ZIP身份；若运行前要复制到自己的scratch，先验证精确来源。不得直接运行会回写原包的build/probe脚本。
- 新报告/日志与临时验证仅写本模型专属reports目录或由报告记录的独立临时scratch。复制浏览器目录到scratch后可构建；现有build会回写index/manifest，所以只能在复制件。现有verify-wrapper带固定session名，不能原样与另一模型并发共享；独立验证时使用各自唯一浏览器session/输出路径。
- 原生reproduce-build.sh硬编码原路径，不能直接执行；probe脚本会回写旁边packaged-engine-probe.json，也不能直接对冻结目录执行。需要复验时在独立scratch布置等价准确路径/唯一输出，用现有精确引擎只读运行且仅合成临时库，保留首失败，不改产品。新增GUI/native运行须由实际owner与总控协调互斥资源；当前政策允许桌面操作，不需重新询问用户时段。
- 无变化代码/锁/环境的既有构建或CLI探针可按精确身份限定引用，说明“读取既有证据，未重跑”；不得虚构本轮实跑。不要求机械重跑所有未变项；实际发现、候选/环境变化或证据不足时补必要验证。
- 本次新增外审冻结包没有改交付产品或验收标准，不因拷贝/操作政策本身重跑产品。两指定模型仍须各自新完整审查全部范围，不能只复核三个P2或读摘要。

## 终态与关闭条件

每个模型独立给完整中文报告，列精确候选、模型/思考/权限实际读回、全部阅读/运行及范围、逐项发现、位置/依据/影响/修复建议、历史3P2处置、未验与阻止项，最终使用PASS / FAIL / NEEDS_EVIDENCE。任何必需未验不写Pass；“条件Pass”“内部Pass”“任务已创建”不作为双通过。只有同一完整候选双方真实终态、全文报告读取、所有意见逐项处理且双方明确通过，才可关闭本stage组合指定双审。当前没有实际创建两新任务。
