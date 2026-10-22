# O15 M §8.4–§8.5 测试/CSP 隔离静态 triage

固定受审 source `b88be226501703f1d5365734dd0e56066bd1bffb`。本次只读取 `git show b88be226:<path>` 及M原稿，不运行产品、测试、oracle、GUI、模型或安装，不改源码/测试/配置。M原稿§8.4和§8.5的 `[中]` 标题及 B150 NotPass 原样保留；下述是owner证据判断，不是修改指定模型严重度或结论。

## §8.4：弱断言必须结合上下文，不能把所有数量/按钮断言算作违规

依据现行AGENTS原文：“测试断言真实需求和错误边界（完整预期集合/顺序），不只断言数量或按钮可点击。”这里的“不只”要求充分语义断言，没有禁止辅助数量或就绪状态断言。

1. `tests/e2e/desktop.spec.ts:21,24,46` 的三次toBeEnabled确实存在，但同一测试L18–25还检查标题、初始状态、真实引擎连接、协议v2；L26–34检查Node不可见与三个隔离偏好，L39–48检查窗口、导航及再次真实连接。将这三行直接称为被明文禁止的“仅按钮可点击”不受完整上下文支持。本次只核静态测试写法，没有执行真实引擎或e2e，不宣称当前环境运行已通过。
2. M以 `packages/engine/tests/test_frame_corpus.py:41` 的 `loaded_cases == CORPUS` 为恒真例，遗漏L17–31的cp1252 monkeypatch和L37的runpy二次加载。模块全局CORPUS是补丁前以显式UTF8读取，loaded_cases是在补丁生效后独立运行同文件所得；若删除显式UTF8，二者可不同。L38–43另有精确中文帧期望、错误默认编码差异和具体乱码值。因此这个表达式不是逻辑恒真。本次未执行变异；这是根据测试控制流的静态反例，不冒充运行复现。
3. `test_job_store.py:166` 的planHash确实从持久job_context计划派生，不能单独证明计划正确。但同文件L417–444已有独立expected_after_snapshot、完整marker字典、精确planHash、持久raw_marker、before/after快照比较；M自己也承认L430有更强断言。单个辅助同源断言不等于整套原子提交测试没有独立预期。
4. `test_stdio_session_shutdown.py:247` 的count=7确实仅计数。`Wire.call:64–72`同时对每个response做schema、ok、精确id和method核对；恢复段L211–246逐项精确比对job/operation/result/project与失败job的固定错误四字段。`Wire.__init__`和send/call代码没有自动重放路径。这个count本身不能证明任意引擎内部没有隐式重放；也不能删除邻近完整断言后称恢复只测数量。若要证明外部驱动绝无重放，应在真正自动恢复驱动边界留完整方法序列，不能仅增强此辅助计数就宣称生产性质已证。
5. M提到约30处count-only/约12处存在性/17项弱断言，但原稿没有交付每项完整上下文和能穿透现有整套断言的具体反例。本次没有将这些总数登记为已复现缺陷数，也不否认其余位置可能有覆盖缺口。供方需逐项提供“对应需求、当前已有断言、允许错误行为、最小变异和预期失败点”，才能落实精准补测。

处置：保留reported-open；其中“出现按钮断言即违禁”和“frame L41恒真”列为报告推论过宽。真实弱覆盖需按实例补足；相关tests/engine/desktop归root与相应唯一owner，本次没有T05 W1–W3自有源码修复依据，不越权修改。

## §8.5：开发CSP单测确有具体回归盲点，当前CSP缺陷尚未证实

固定源码 `apps/desktop/src/csp.ts:3–26` 为单一策略源，生产script-src仅self；开发分支为script加nonce，style额外unsafe-inline用于Vite HMR，connect仅固定loopback。当前代码没有在script-src添加unsafe-inline或unsafe-eval。

- `tests/unit/csp.test.ts:12–19` 的开发策略测试仅正向包含nonce和ws地址，加两条无效输入拒绝，没有完整指令/禁止脚本unsafe的断言。静态构造的具体盲点：若仅在有效development分支给script-src额外加入unsafe-inline，该文件现有开发测试的所有条件仍成立，生产测试也调用非development分支。此为可定位的测试保护缺口；本次没有改源码或运行变异，不能记为已复现当前产品漏洞。
- `tests/e2e/csp-lifecycle.spec.ts:171–183` 同时检查inlineExecuted=false、remoteExecuted=false、fetchBlocked=true、样式按模式、Node隔离、requests精确空集合，另对四个directive做some/enforce。因此不能说只有弱some、没有行为守卫。但当前开发script-src已有nonce，单独追加unsafe-inline在CSP3的nonce优先规则下不必使inline脚本放行，不能据该文本变异断言开发e2e必失败。该例只证明本单测未钉策略文本；实际行为变化和各OS执行仍须供方运行证据。nonce/hash会阻止unsafe-inline获得全内联放行，依据[W3C CSP3 source-list inline算法](https://www.w3.org/TR/CSP3/#allow-all-inline)，这是规范核对，不是本机浏览器实测。
- 四个some确实接受意外额外/重复违规事件。具体逻辑反例：含四个预期enforce事件的数组再加未知directive，四条some仍true。它证明该数组检查不是精确集合相等，不证明真实浏览器已产生多余违规或策略已失效。
- 不能简单将期望固定成四条原始事件：本probe生成两个script元素，生产模式另有style元素/属性违规，开发样式策略不同，浏览器可能重复或按实际directive细分。供方应先定义分模式、跨OS的有限语义投影（directive/disposition/blocked类别及允许重复），再比较完整允许集合，并保真实native事件。不可凭空固定全事件数量/顺序，或用新fixture代替生产证据。

处置：保留reported-open，将开发策略测试盲点明确交CSP/I02唯一owner；建议精确钉当前两模式指令集、nonce与origin替换、script禁unsafe，再用真实e2e验证。AGENTS所指M0更新计划原路径不存在，初次rg返回2已如实记录；后在固定b88be226的docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md:145–153找到归档原要求，已完整读取C1段：支持开发nonce/HMR与明确变体，生产脚本禁unsafe，开发/构建/真实打包同时验证阻断和正常功能，不能仅meta/无报错。它没有给出恰好四条违规原始事件的固定集合，不能凭空加该验收。没有改变CSP源码/验收/现有测试，也不为本次文档triage重跑旧检查。

## 交付边界

本报告给出静态证据、具体未运行反例与供方缺口，未升级为运行/生产证明。两个M中级标题和原15外部意见均不由本owner关单；完整scope仍NotPass、§3.4阅读缺口保持，双指定审结果未汇合为整体Pass。任何实际修复若改变实现/测试/验收，须由唯一owner形成新候选并履行新完整双审。

## 独立复核中发现的owner推论纠正

owner第一版曾把“开发分支单独添加unsafe-inline”的策略文本变化直接说成开发e2e可抓到的脚本放宽。独立复核指出现有nonce会改变该关键词语义，owner已据W3C CSP3核对后删除该确定推论，保留文本断言盲点和现有行为测试两个不同事实。未执行变异、未改产品，也不把此owner推理错误归M或浏览器。初版文字和本次纠正摘要保在本次过程记录，不伪称初版推论正确。
