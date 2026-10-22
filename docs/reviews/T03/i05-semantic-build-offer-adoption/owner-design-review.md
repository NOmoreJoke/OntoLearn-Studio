# I05 offer 的 T03 owner 接收设计审查拟稿

结论：**建议连同 adoption §3 增补接收纯设计；原 schema 原样实施 needs-change。** 这是 helper 的独立静态建议，未代原 T03 最终接收或 root 批准。报告写定后停止新增写入，等待原 T03 全文读取；本 helper 不 stage/commit。

## 范围与证据

固定 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，offer candidate `6ba273a892b18a5ebaedc07aea6f36584999adcf` / process `21f9d4d288e8bd462b2252018578590110c08691`。唯一树 `.worktrees/T03-i05-semantic-offer-owner-review`，branch `docs/T03-i05-semantic-offer-owner-review`。AGENTS保护M 15,852 B / `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，不stage。

先读最新AGENTS、外控window/setup/limited-root-closure，再delivery/final-manifest/R1/R2，随后O主文/P descriptor/B/F两schema。主文第一次大输出在L114–125附近截断，已重显L1–104、L105–150及L190–266；L151–189在首输出完整可见，已实际读全，没有把截断字节当完整阅读。B全部JSON在完整buffer中解析后按所有properties/$defs显示完整结构和值；P全部540行、F全部262行已显示。完整读与有限抽读范围记录于input-evidence，未把47payload哈希清点或JSON解析当源码/运行全审。

106 Git/43guard/33路径/417有序集引用固定R1/R2独审，不重复不变旧binary/tool/SDK/witness。抽核2cf probe前门/代码指纹/实际loader/header（L1–115、572–706）、6891 resources实际唯一样例对象（L1–97）；实际只读源文本，不 import 或执行。静态读取主目录M0 S1/B1原文相关段及本树两ADR，原M0不在5f Git的事实保留。

## AD-01 · P2 · runtime根executable不能由现_MEIPASS file域如实指认

依据：O L90–100、L136；B `runtimeComponents.kind` L1649–1656、`bundleFiles` L1684–1708；F.executable L35–54。当前布局exe在bundle根、_internal为_MEIPASS，但runtime映射被规定为_MEIPASS相对且禁`..`。pyinstaller-bootloader位于启动exe，既不能写`../exe`，也不能用假的`_internal/exe`替代；F中确有exe不等于B对应字段已有跨域关联。

建议最小修订：所有最终包文件映射固定bundle-root相对；payload仍固定meipass-root；prefix转换与同文件bytes/SHA跨账核同，bootloader绑F同一exe，保持文件级证据/角色关系，绝不造bootloader独立文件。path字段按域固定，拒绝任意根、absolute/drive/UNC/NUL/dot-segment/别名/symlink逃逸。完整许可/运行时覆盖不删。

处置提议：已在adoption A1给出完整设计；必须owner明确接收并在后继新schema版本实际落文后才可实现。当前未修改B/F，不能称原件问题已经消失。

## AD-02 · P2 · 嵌套PYZ与第四函数的实际archive绑定缺少显式闭口

依据：B `archives` L821–918、module `actualArchiveCode` L2093–2195；functionBindings L1416–1619；O L129–150。新实际构建尚未发生，不能预设PYZ一定是独立目录文件。对“exe CArchive 内 member PYZ”这一与profile兼容的具体结构，单一path/bytes/SHA缺父容器引用，无法同时真实表示exe与内嵌PYZ。任意`exe!PYZ` locator不受允许。Validator.run来自installed pyshacl.validator，23canonical中无该模块绑定；function条目只有模块名/索引/指纹，缺唯一实际archive模块见证引用。源编译函数指纹不得冒充actual archive提取。

建议最小修订：有ID封闭archive账，父文件或父member二选一、无环/唯一/完整TOC、最多此profile指定容器深度；module/function仅引用已有ID及exact member。另以单独distributionCodeBinding记录pyshacl.validator模块actual raw code/source/RECORD/artifact，不把canonical23扩成任意集合；四function显式引用该模块或canonical semantic binding，再按同一co_consts索引分别从compile/archive域抽取。对应adoption A2。此为数据表示，不授probe读archive/外部文件。

dynamicChecker.loaderCode也须消歧：builder只能产期望data-source code，runtime真正loader观测在后继caller/header。resources.CONTRACT原对象继续保留；不能为了让builder字段好填另exec alias或声称已测runtime缓存。

处置提议：采用设计增补可审；后继schema/descriptor/提取器/consumer须同一新版本重冻。没有本轮actual archive实例、CodeType执行或运行证据；报告不声称当前工具实际输出就是该反例。

## AD-03 · P3 · 安装根、运行收据跨字段约束需在实现前定死

B installedRelativePath/RECORD对完整实际安装文件的路径域尚未明确；本轮未读实际installed RECORD，不能推定当前某库已有逃逸行。adoption A3保原RECORD行作证据，固定安装根ID+规范相对路径，所有行逐项核物理文件/disposition；环境外逃逸拒绝，runtime必需不允许omit。此项是实现前定义需求，不冒充实测库缺件。

F L206–235允许runtimeValidation与null/non-null manifest任意组合，正文虽有完整证据要求，仍须明确not-executed→null、其余→完整manifest的跨字段规则，以及compared不等于matched。adoption A4将后续validation receipt引用原approved build receipt，避免原地回填改变launch前输入或与后出的runtime evidence互成等待环。无需probe可信receipt新载体；包外批准保持caller/root。

处置提议：在D0 docs窗固定跨字段规范/新版本，独审一致性后再实施。不得以schema结构解析通过等同这些关系已运行验证。

## 原R1处置与可接受设计

R1-01职责边界和R1-02 source-only owner旧标签由固定R2关闭，本轮未重开。O§4.3.1/P actors现在可清楚限制probe只核声明/bundle/actual loader，caller launch前批准receipt与全目录、launch后header回绑；root审真实组合、T03产真实外部见证。source第23 actualSourceSha由caller按批准pin核，不嵌自己hash，避免自指；严格三argv保留。exact错误码/exit及阶段在adoption §4逐项接受为后继提议，不虚称2cf已有新增码。

依赖唯一锁、parent原义、独立onedir profile、canonicalbootstrap、33路径与43guard迁移、后置provenance→外部目录→receipt→过程commit有向链可接受；已分Git/source、installed、actual archive与runtime域。无环不等于证据齐全；actual get_code/marshal cold-warm/cache稳定性、同Python build/cacheTag/optimize与真实artifact/code/许可均留实际窗。

完整417/320、83/106/54/50和C13、所有not-executed/missing-context/known rejection、typed费用与库分类缺口保留。T05最新窗口给固定首oracle3d8f4ee，作者报告417/37纯自测、280specified/137pending，未独审收件；主文28项是旧快照。本轮没有读其新oracle原件，不判oracle通过，actual child allocation及12date首码仍pending。

源/独立包/parent全suite、另12B1 fresh、原12S1真实snapshot、正式Job/Store/selected/H、原全57P0/C–G/PRD10–12/六迭代及指定同版双模型/CI/两OS/真人/develop远端门全部保留。SQLite损坏HOLD/被拒物理线不重开，不移用R7票；独立artifact不代parent，逻辑cap不代物理资源许可。adoption §5将缺证拆为D0文档、D1依赖、D2消费delta、D3包装、E0实际构建、E1域微验、E2全采集、E3oracle、E4原门，各窗须另授精确资源/路径/进程。

## 验证边界

只使用普通Git/文件、stdlibJSON/hash与现有Prettier3.9.10格式，不执行资料脚本或业务。未运行JSONSchema validator，未import产品/probe、builder/spec/reader/helper/局部函数/fixture模拟、pytest/compile/archive解码/版本能力探针/安装/network/DB/native/GUI；未读旧binary/witness/SDK/toolpayload。未借native专票，未改任何四writer/锁/CI/公共契约、其它树、offer47原件；未stage/commit/push/PRmerge/创建Goal或用户线程。

最终候选由原T03全文读后明确owner接收并提交；本报告不是该最终接收或该候选提交后的独立复核。formatter/whitespace/hash检查的实际结果保存于交付清单，验证只覆盖本次文档，不证明环境或产品能力。唯一状态仍遵循项目状态文件，本报告不改完成度。
