# I06 / S3 状态

2026-10-21 当前接续：正式 main / 命名 bridge / 最小 UI 检查点 `9fcba6634d5c16983c36ef671d4ec8e79694b6d6` 已完成固定Linux正常链/native/包内专项；随后原e2e发现模型提示新增role=status干扰唯一health status，已仅改为aria-live=polite并独立复核，产品新内容固定 `e2c269ad78a78e1a042cadc93b1c81a874707153`。旧平台事实保持原9fc绑定，不整体套给新候选。其前契约子线 `69dd44d` 已正常合入为 `0ce0258`。批准依赖仍为本次现场 `ls-remote` 核验的 develop `5f910b52c69d86a1076b2032e5d3c63e715947f3`；不采用 I05/T01/T00 未批准实现或语义常量。原14文件责任中八文件已提供[未来维护释放 ack](../../iterations/I06/format3-maintenance-handoff.md)，已由总控正式登记生效，未来唯一维护为原T01，见[生效接收回执](format3-ownership-effective-receipt.md)；其余六文件仍归I06。其他 Python/入口 build/锁/CI/安全恢复未改。

来源与转移设计回应已交付：[源快照唯一传输决定](../../iterations/I06/source-snapshot-transport-decision.md)、[选择/预览/确认/Job 生命周期](../../iterations/I06/source-selection-lifecycle-interface.md)和[T10 受信转移回应](../../iterations/I06/T10-trusted-transfer-response.md)。来源方案采用待T01冻结的单canonical 64KiB分块、8MiB单源/2lease合计16MiB、丢begin回执原attempt对账/取消、最终实际写帧guard及持久pin；未接纳lease不跨session恢复。T10接受业务白名单、全私有根排除和唯一writer新项目receipt后的授权隔离；现有private-directory尚无动态转移lease/完整inode inventory，不能把设计当能力。新guard候选 `apps/desktop/src/main/security/private-root-transfer-guard.ts`、来源宿主候选及专属测试均只申请精确登记，未创建或获得写权；metadata owner/一致性/退役规则、T01 canonical/receipt、实际parser/Job/Store/export及源/包联验仍待。三份设计已完成[独立静态审查收口](source-transfer-design-review-20261021.md)，本轮只文档合并/格式/diff，不新增运行通过、不改产品或受保护AGENTS，不标原Goal完成。

T01固定 f51dd38dbdfd2fbb1b9923efee666a19d5b415cc 跨owner答复已全文读回并实核 SHA `0f3ab7e539b9b69c6a602f4eabd089936a37afd9d842fa836748793031df6768`，§2/§3已保存[最小对接回执](../../iterations/I06/T01-owner-response-alignment-r1.md)。接受同协议分块、位置lease/固定业务闭包及唯一writer新项目receipt后选择local context的方向；明确worker stdin第一帧关闭仍是真实接线缺口，重复append语义和配额/取消/最终写帧/pin需精确冻结。worker.py未来维护申请尚未生效；source.*/diagnostic.*未成为公共schema/runtime。独立静态复核无阻断；原Goal不自动恢复，本轮未改共享或重测产品。

总控后续四文件生效通知已接收并全文读取：`I05-T03-build-ownership-handoff.md` SHA `88057b59e173453d197bfeae183dc99b8c09c71e30d518781bf774ebc037e95b`。`packages/engine/pyproject.toml`、`uv.lock`、`scripts/build-engine.mjs`、`packages/engine/entrypoint.py` 的未来唯一维护为原T03；I06不改这四项、不消费未批I05内容，不能将转交当作依赖/包内通过；格式3八文件的独立逐项ack及总控登记现已完成，见生效接收回执。

总控格式3 Python四文件转T01通知已接收并全文读取：`I05-T01-format3-ownership-handoff.md` SHA `18485767098d448a4fcce2fc7e59b5a325433826894b98111cab96926fdc2097`。`job_store.py`、`coordinator.py`、`__main__.py`、`packages/contracts/python/contract_v2.py` 的未来唯一维护为原T01（前三在engine包），含唯一全局claim迁移、非Job同连接adapter及两层ready责任；保持默认2/显式内部3隔离，不引入未批I05。I06不改这些路径；canonical/main八文件现已另行完成独立接收及登记；两项交接均不是业务3通过。

格式3 [wire/启动诊断小合同提案](../../iterations/I06/format3-wire-contract-proposal.md)及[完整固定JSON](../../iterations/I06/format3-wire-fixtures-proposal.json)已完成独立静态复核，两项消歧已关闭，见[审查记录](format3-wire-proposal-review.md)。28对wire/4通知/6启动分类/4兜底均为未来合同预期；测试hash明确schema-only、实际ready/dispatch=false，不冒充真实协议3catalog或运行通过。八文件原释放回执为24b224f；后续总控/T01已正式完成逐项接收及登记，权威协议SHA `add9884ab9a0cda3a8a562f26a3b7c515255919d65eb0487d6c254681ed4991d`，本线已全文读取并接收生效。其后文档正常合并与政策/权属同步未改变e2c产品内容，未重复无变化产品检查。

共同指南责任更新接收：已在安全边界全文读取 `iteration-control/2026-10-21-weekly-release/developer-common-instructions.md`，实际SHA `b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39`；原df090快照仅为当时权限政策记录，旧冻结输入保持原字节。本线AGENTS实核仍为78df2825…a759，指南文首db1为初始快照，按后续实际更新规则执行。当前T01唯一维护storage+格式Python4+canonical/main8，T03唯一维护构建四，I06只保留原14余6；具体排除/返还依已生效交接。已分别向i06_interface_docs、i06_platform、i06_design_review发送全文路径/SHA/责任及原权限、指定双审、逐任务模式读回、只读、无桌面约束，要求其下次正常工作边界读取；随后三线均在本轮正常安全边界实际全文读回并确认当前b24；旧冻结输入保持。未改产品/AGENTS/冻结输入，不重开Goal、测试或整轮外审。

实质运行收口（不是政策终态代替功能）：已合入原运行[当前终态回执](main-platform/runtime-termination-readback-20261021.md)。三原容器exited/Running=false/Pid0，原session96217/62110/5804均实际final exit1/0/0，无对应活跃等待客户端，不需重启。已全文读回总控e2c独立审计SHA `35994a0675376d9dd9ac3a93491713b36ec62afff4b3ca77cd48465e1abc13d2`，无新要求改产品/重复旧矩阵；本次根只读工件核对597index/860产品Git来源/243包及十门退出与唯一retry一致，见[读回JSON](evidence/e2c-terminal-root-readback-20261021.json)。全部原件、实际退出/未明首败、恢复句柄、保存/导出/语义/format3/外审余项统一见[恢复索引](recovery-index-20261021.md)；不将9fc领域平台套e2c，也不将当前阶段视为I06完成。

剩余依赖已拆为[正式语义/真实导出X1–X6请求](../../iterations/I06/semantic-export-integration-request.md)和[format3消费C1–C6请求](../../iterations/I06/format3-consumer-integration-request.md)，不是仅按迭代编号等待。现有整结果只读API可复用；正式producer/版本/按需字段来源由I05与T01冻结，T10须给真实导出入口/可信范围根/白名单及重新导入边界。format3冷启动可优先复用；仅受控同进程迁移需可信撤销/重建，替换Supervisor须连关联模型服务安全重建。准确UI诊断涉及余6外task-presentation.ts，未擅自修改或授权。新增[独立复核记录](closure-and-integration-request-review.md)确认两处文案修订已关闭、恢复索引和接口请求无剩余文档意见；没有新产品/平台运行通过，也未push/PR/外审。

新App源码内容完整 `npm run check` exit0：998TS、1052Python、lint/format/typecheck/build/ruff 全过；`verify:sources` 12项及diff通过，检查时两处protected AGENTS为db1fb184；随后授权政策追加后当前为78df2825，未stage，见[政策接收回执](external-permission-policy-receipt.md)。命令启动时App工作树修订已固定，随后以相同bytes提交e2c；检查期间无产品内容更改。[本次证据](evidence/aria-status-fix-20261021.json) SHA `a411e552e19390e37861f5f67066184d9e4f833c8686c4abdcf847c77b96f4da`，10文件原件archive SHA `60e3bdb6e91e764237f9e48aaf2ae2adc2fdd60d5ad613009b68e95e1f80b619`，位于tests/i06-stored-material/out。旧完整check r9日志保留，不以它替代ARIA改动后完整检查；新源码/包内原e2e及CI fresh-fixture分项已覆盖，首次十门九过一失败、唯一原用例定向复验通过，失败与未明时间差保留，不称一次全绿。

[正式接线计划](../../iterations/I06/main-wiring-plan.md)记录唯一main服务、strict12方法/10G错误、独立取消、实际项目context与单profile锁、私有配置原子journal/安全录入版本边界、独立启动与有界退出、只读恢复/纯文本结果。头部无实际项目默认local；无通用转发/secret读回/worker模型入口。配置journal两实例竞争/不确定发布后失败、password随版本清空及新建草稿保留已修，独立只读复核关闭；旧9fc的Linux正常22项/native4/pkg2均限定通过，源码变化对应的UI/原e2e/新包实际身份另验，不复跑未变化私有核心矩阵，不宣称新候选完整S3通过。

专属真实链46项含37来源/字段、6配置、3named-service HTTPS。凭据加解密在这一headless服务测试中是明确double，密文/配置/审计实际私有文件、实际批准Store/coordinator/test.read worker与经证书校验HTTPS receiver均运行；已保存合成完整body原件，不记录headers。正常生产字段模型仍为空、runtime-only；固定finite policy仅既有可信launchfixture/test-runtime且非packaged可启用，不外推生产业务provenance。I05实际新语义批准merge后再刷新/绑定/冲突处理和全新联验。

字段阶段 `a930e11` 的旧manifest/源码/raw保持；追加独立v2是新运行，4份实际receiver原正文和100工件hash根已逐项复核，归档SHA `588cd43c6851352ab36e74526b59d5ef666c30996c10679d98bc0213cf2dd180`，不倒贴到旧run。原v2专属证据含明确synthetic header，不含真实凭据；后续正式集成raw只收正文。根读回见[evidence](evidence/finite-fields-v2-raw-readback.json)。

本轮[源码与验证 manifest](evidence/main-wiring-20261021.json) SHA-256 `718198c2797ab03a64ddec5b644bf1ff10ca1f18fe3246725ea07bf255acb1d4`；归档 `tests/i06-stored-material/out/main-wiring-raw-20261021.tar.gz` SHA-256 `536f80923ec23b44e7caeed54b95ae93fce6357e67fddcfbc26990a5cfb45ba6`。归档保留117项固定源码/测试输入、5项构建输出、19份日志及18份合成服务原件，当前实现意见与验证边界见[内审记录](main-wiring-safety-review.md)。

平台agent只写 `tests/i06-main-platform/` / `docs/reviews/I06/main-platform/`，已正常合入9fc固定源；独立Docker构建完成，首轮实际运行r4无项目禁用通过，但 secure backend 前置检查得到 basic_text，未写密钥、零POST。已确认 Playwright Electron loader 强制追加 password-store=basic 等参数，该次不能作为产品原生凭据失败或通过证据；保留失败原件，改为直接启动正常 Electron 后用容器内 loopback CDP/inspector 驱动。runtime network none、无host mounts/端口映射、非privileged，不运行当前Mac窗口/native/Keychain/CUA。

直接正常启动的r5实际确认Electron44.9.0/browser/app-ready、gnome_libsecret/encryptionAvailable=true，无mock-keychain/readiness补丁；随后项目恢复使表单重挂，驱动填写超时，尚未录入key、零POST，原件保留。r6仍用固定9fc源码，在本线 `tests/i06-main-platform/out/9fcba6634d5c-r6` 独立容器完成：真实libsecret录入无回显/首字段授权/实际worker环境等4项通过；之后新catalog异步返回前误用旧checkbox，驱动等待失败，`result=failed/receiverRequests=0`，不记作HTTPS发送通过。根已直接读回result/cases/runtime核对一致。r5/r6命令带 `--no-sandbox`：只能保留实际已走到的有界凭据链事实，不能计作最终C1/C4一致的完整窗口/native门通过。总控要求另准备实际可启用Chromium sandbox的本线隔离容器，正常启动不带该switch，实证 `noSandboxSwitch=false` 后重做受环境影响的main/bridge/存储/恢复；不更改产品sandbox/CSP/window-recovery，也不把能力准备或配置文本当实际安全运行通过。r6原raw独立保留。

本线default Docker/nonroot userns探针实际 `unshare --user --map-root-user /bin/true` 返回EPERM（kernel userns配置已开）；未据此宣称产品缺陷。只读I05成功记录确认其方案使用CAP_SYS_ADMIN、root:root/4755 helper和非root进程。按总控已授权环境准备范围，下一独立I06镜像仅修容器内helper owner/mode，测试容器仅增加CAP_SYS_ADMIN并保留Docker默认seccomp、network none/无host mounts或端口、非privileged；不使用seccomp=unconfined，不借其他线可变环境。能力扩展须明确披露，不称default Docker无额外能力；实际无no-sandbox运行仍待证据。

后续平台运行（与根完整check r9分开编号）：platform-r7仅有界userns/helper预检通过，未运行app。platform-r8正常app无no-sandbox，实际UID1106、main Seccomp2/filter1、renderer NoNewPrivs1/Seccomp2/filter2与嵌套NSpid均有原件，GNOME后端可用；之后刷新了模型而未刷新实际任务UI，驱动找不到第二结果，4case/0POST/总体failed。platform-r9修驱动后实际14case通过、3次合成HTTPS POST，覆盖实际两worker授权复用、独立cancel/complete、reload、同profile第二实例、隐私/审计/配置失效和表单刷新；随后全页alert定位器撞到既有多个错误卡，未到最终scan，collector全部总体gates仍false。根实际读回cases/result和3份693bytes正文并计算hash，但该失败run尚未写receiver-manifest，不能称为最终绑定通过。platform-r10另冻harness运行，修直属alert定位并追加两轮实际source/catalog/selection/preview/grant合成原件；旧run不改。当前仍无完整平台pass。下一项为断开调试器后的真实crash→真实原生提示→窗口恢复，核对I06 ledger/Store和receiver不重放；避开会stub dialog的旧helper，不能只以reload代替native联验。

最新platform-r11：固定9fc产品、22项实际case/3次合成HTTPS POST/collector五gates均通过，root直接读回并逐项核对正文长度/SHA。独立只读复核核对851份源码、19个实际compiled+harness产物、14份harness原件、before/build/after与5个binary记录；image `sha256:f7fc7b481eb6270fc169a173970846ce998e1b59b4a42fffdb9b36295730dff1`，正常sandbox/GNOME、namespace/seccomp、isolated container事实均吻合。binding SHA `058a61825c78816b1ba586585edb32c7ec66341f61475361ce5815b33d05068c`。A03两轮实际raw同旧grant、不同result/job/catalog/selection，三行实际source含私列/派生值；3份693bytes完整body均SHA `4bea2fec09859fae6a3f5f685630b22bd3c3595f486edde3df2b5cedaedda2f0`，逐项无原rowUUID/ordinal/私列/派生值/secret/header。scope一致由冻结projector映射和同grant复用验证，不能称直接读取未公开scope UUID；取消/重载等依赖本run执行断言与case记录，不宣称每次outcome完整DTO均归档。22私有文件/5DB扫描由本run冻结scanner与receipt支持，独立复核没有重扫未归档vault/DB原件。native/C4、其他平台、适用I05与完整S3仍待验；真实crash→原生prompt→恢复单独准备，不倒贴r11为native通过。

最新native4独立增量亦已通过并独立只读复核关闭：相同compiled app/5binary，真实crash→可见X11标题 `OntoLearn Studio 窗口恢复` →实际shift+Tab/Return→第二窗口，main PID不变、renderer/window身份更换，非dialog stub。故障前inspectorURL=null、从未rendererCDP，noSandboxSwitch=false/hangMonitor开启；整个project DTO/job/result/stateVersion/operation marker/context/selections/invocations/completed outcome前后严格相等，receiver始终1份695B，不重发。native-binding SHA `9bade372085b53c7e95e9fe0c2d337ec648e6767d63b4b14ab0baf166af35637`。截图缺CJK字体，仅证明提示存在，中文标题由X11原文确认；不称中文排版或unresponsive全矩阵通过。停止后另回收5个DB/vault原件并新增readback SHA `a765852442015d7c599c7e05a2312243a091f7ae8ef48a60af1ec28c10a93e50`，独立只读核对hash、23行/raw pages、配置digest链与audit一条metadata关联，无secret/response正文；不改或倒贴旧runtime scan。

平台专属24文件提交 `3124b7df4497df6c57954106982cd83cc8d16673` 已正常合入根，仅新增tests/docs，不改产品。定向ESLint/Prettier/Ruff/语法/diff通过，未重跑未变998/1052。953文件原件归档已复制本worktree `tests/i06-main-platform/out/i06-main-platform-9fc-r11-native4-raw.tar.gz`，SHA `9dac44b0cd0a588c902b85b35079f691a52ef13a0e51dce5c9b9e5f9dd99f0fe`；root逐项验证952索引文件bytes/SHA及3份passed绑定，见[根读回](evidence/main-platform-archive-readback-20261021.json)。实际执行冻结harness与最终格式化/采集脚本分开记录，旧失败run保持。原计划要求真正打包executable，source app不能代替：本线正在独立正式 `npm run package:dir` +实际package executable/GNOME/sandbox/包内engine/具名whole-result HTTPS和恢复最小增量，包内有限fixture字段policy必须按现有门拒绝，不为测试放宽。

总控独立检查点核验（`iteration-control/2026-10-19/I06-controller-main-wiring-checkpoint-evidence-audit.md`，总控回执SHA `1d5888302a3b63d34ba8393ae9ae36c0c52aa63f518af7153b23db56956c462f`）未提出新增实现修复请求。117source/5compiled/19logs/18raw及998TS/1052Python/source12/46专属/validator43支持其各自边界；18raw是6组同case历史重复正文，非6项新用例。headless safeStorage为double，CAS为同进程两repository实例，postpublish旧context失效和零POST不等于已归档旧pending精确cancelled对象；当时singleprofile仅静态，后续平台事实按新run单列，不倒贴旧证据。

旧9fc包内pkg2专项已通过并独立复核：正式PyInstaller/electron-builder产物，isPackaged/243实际包文件/asar五编译文件、当前main后代engine父链均原件核对；显式历史whole-result经具名桥授权一次2327B POST，真实crash/prompt恢复无重发。该整份请求有意含合成私列，不能当A03 public-only字段证明。独立finite profile有效格式configure/store/start实际MODEL_UNAVAILABLE，活跃共享receiver delta0/凭据目录空；旧pkg1弱绑定/无父链/硬编码计数原件保留不倒改。提交 `424d80716e2434aec921a647d716e6be15fc0c24` 已正常合入；591文件原件归档SHA `006f0bb374c659077c6433df3bdaeede900bb90bddd7fe7d4bc2d1dd6f26f7fd` 已复制根out，root复验590索引文件，见[包原件读回](evidence/packaged-archive-readback-20261021.json)。

同旧9fc的原仓库regression1 source与package各1passed/3fixture-gated skipped/2failed、测试exit1；collector采集exit0不记测试通过。具体为新增模型段role=status使desktop/CSP normal全局status定位出现两个元素，CSP后续断言尚未执行。e2c仅改该段aria-live=polite，提示/条件与旧测试断言不变，独立复核关闭；新构建source+package及原CI独立fresh-fixture三个用例分别在验，不以基础3skip代替具名bridge回归，不重复无变化S1/S2或凭据全矩阵。

总控对r11/native4独立审计回执SHA `ea9f5cc64f62df53cbcc56bbe7c845ffac8faf05963ab31b34b202983717c7ef` 支持固定9fc阶段，无新增否决矛盾：完整未选catalog两轮未独存、部分cancel/reload/singleton中间DTO未全存；binary为runtime realpath/hash记录而非本体；扫描的普通日志未全部归档，不能把原件子集当重扫所有扫描对象。新增停止后6DB/26private原件另按readback核对，native crash不等于hang矩阵/中文排版。以上边界保留，不补造旧材料、不将旧9fc整体贴到e2c。

T00版本提案SHA c4f32d已全文读回，本线[I06兼容影响回执](../../iterations/I06/T00-format-version-impact.md)完成独立只读复核，仅建议DB/协议/私有格式分离、受控升级撤销context、应用CAS不污染领域输入及逐路径维护，没有实现或批准协议3。storage.py后续已交T01，I06仍独占原14文件，T00仅提案；当前源码/平台不采未批代码，最终指定审查等实际批准依赖和确定基线后预约。

最新e2c回归收口：独立只读review核对881源码记录、39harness、44执行产物、243新包文件及ASAR内五out，source/build/实际包均同e2c。原source和package `npm run test:e2e` 各3pass/3默认fixture skip；随后各三个原CI独立fresh-fixture用例全部取得实测pass，只有source-native首次未见hang提示，另在同inspect镜像身份、新容器/新fixture、未改原测试的唯一target retry通过。两模式ARIA initial/reload均polite/无status role/health status唯一。精确结论为 `passed-on-targeted-retry-with-initial-failure-retained`；原每phase源码 `Date.now()+30000`，首次trace约12.25秒差异原因未知，不推断时钟或已消除flake。两generic S3 binding非适用门仍failed，不当作本回归测试结论；以专用逐门receipt判定，不将本轮扩大成新App全S3。

上述新增harness/docs主体 `5018d65`、说明修订 `1edee922264fae99f29dd7cdd90b81fa75be5bf3` 已正常合入；定向静态/格式/语法/diff通过，没有再次跑未变核心矩阵。598文件完整归档已复制根out，SHA `f13d9a6f0cb06b39703a91bfd76e85266c87583c0123f5c31a92ee8ccb1afa34`；root逐项复验597索引工件，专用receipt SHA `974ee6e93e0f027a96abe76a0dca13ddf62648e0d86bae6023015eb16d3b7757` 一致，见[根读回](evidence/aria-regression-archive-readback-20261021.json)与[分项报告](main-platform/aria-regression-review.md)。后续源变化当前仅doc/test，产品相对e2c无diff；尚未push/创建PR/运行远端候选CI，完整原Goal仍待批准依赖、最终联验/同候选双方全新完整审查和实际集成门。

文档子线从同9fc完成四份接口/交接文档与专属记录，对齐提交 `11666cfcfcc15c8f5f8b164bfeaa3fad2acc464e`；原35例和5场景ID保留，新增6例，实际校验43/43通过，原raw SHA `458ddca166bb568532944741a37216996c92e9c82925ddeca1d940564534cd01`，根已复核21快照及41行receipt。独立只读发现终态淘汰文案顺序偏差，在追加 `302f1a440aed47b13e42fee37e3bb9c9286d9440` 纠正并同步ADR/验收旧阶段事实；复核关闭、无新增问题，未改实现/样例或重跑无关检查。新文案raw SHA `22bc2a57dff0cd185250aadca10d2d12d93390b7d7d228dc0541e328ca124bc3`，根已核对6快照，旧raw不变；两提交均已正常合入。原Goal不重建、不标完成；完整S3/平台/适用I05、同候选指定双方全新全范围审查、push/PR/实际CI/远端合并核验仍未完成。未push，不改总控state。

## 先前阶段记录（历史，当前以上文为准）

日期：2026-10-21（Asia/Shanghai）。阶段：I02/I03/I04 真实依赖已合并，原会话继续私有凭据/持久审计/隔离平台验证实施；完整 I06 未完成。启动 get_goal 仍返回原 Goal blocked；此为工具实态，原依赖阻断已由实际合并消除，按总控接续授权推进，不重建 Goal、不宣称有 resume API、不标为 paused/complete。

最新阶段：已实现 `StoredResultSource` 与 `GatewayApplication` 私有整份既存结果读取/应用服务，使用批准 I04 的实际 Store/coordinator/worker，只读来源、用户确认、完整内容复核、来源并集、定向取消和持久审计贯通合成 receiver。23项新测试通过，完整 `npm run check` exit0（793TS、1052Python、构建/静态检查）；之后预览集合硬界的一行修正完成必要lint/typecheck/23项复验。独立复核无新增阻断。首轮夹具违反单写者租约的6项失败及修正原件保留，真实保存改走同 coordinator 的 test.atomic，不绕过 Store 所有权。

本轮 [最小命名接口草案](../../iterations/I06/narrow-interface-draft.md)、[35个合成正反样例](../../iterations/I06/narrow-interface-examples.json) 和 [内部审查](stored-result-review.md) 已交付；公共接口尚未批准/注册。A-03字段投影与其他列零外发、适用的I05真实语义、正式main/bridge/UI/可用导出日志排除/窗口联验仍未验收。所选版本、读取时状态和历史必须明确；PRD已经允许显式历史选择，不需重新批准。Store/socket原子lease只是承诺持续current时的增强候选，不是原S3自动前置。Q9真实协议不是本合成S3自动前置；原Goal工具仍blocked，原目标未重建或标完成。

当前接续：有限字段投影器及应用接入已通过完整check（807TS、1052Python、静态/构建）和12项sources校验，37项专属真实来源/字段测试通过；独立探针对应当前三文件SHA，真实Store/worker合法字段1POST、原始行标识/私列/派生值零出现，中间释放取消且0POST。在私有边界实施有限可信字段模型/目录/投影，以实际批准Store/worker结构化结果及receiver全bytes证明A-03；不扩成M1 CSV追踪，不要求必须I05或恰好两个特定API。前阶段manifest/审查保留原件，其中把lease、历史语义重新批准或完整原始列溯源写成强制前提的表述已由本次原需求归属纠正取代，不作为原S3门禁。1911检查点和所有失败证据保持。精确14文件共享责任已由总控通知正式移交I06，见[接收回执](../../iterations/I06/shared-owner-acceptance-20261021.md)；未采用未批准I05候选，本轮没有第三方双审；793TS/1052Python完整check在最后preview cap前，cap后仅lint/type/23专属复验，未声称最终改动后整库重跑。

本轮字段manifest见[evidence](evidence/finite-fields-20261021.json)，raw归档 `tests/i06-stored-material/out/finite-fields-raw-20261021.tar.gz` SHA-256 `8647d2510cc14c8c5398510a98a2dfd5f300f67c0b4d65bff9b2a6b37d8379ec`；独立证据归档SHA `408385a95365c6eb5a93e9f9127584a6aac7b2709cfbc42a2e9e6781f7d63023`。两项独立意见已修复：原始行ID/ordinal不得外发、完整祖先释放必须取消后代。仍无正式接线/当前完整候选平台或指定双审pass。

上一存储结果阶段实质代码保全 `373d88ac36f8fac52b4d930f67b8e2a28e418d85`；窄接口草案 SHA-256 `d18c1033c9ff98e8a90f628f60d14e755afdd09fa48badced238e06c809b82d4`，样例 SHA-256 `ca3b86473b06a21f79983ac11f6925cb2d84a10ca54e72a124541415e21ae5a2`。[本轮来源与验证 manifest](evidence/stored-result-20261021.json) SHA-256 `77a524e2d40ee21169d77e7613df1242c1ac258d5ad37f5f7a90623ba55e05c4`；本线忽略目录 `tests/i06-stored-material/out/stored-result-raw-20261021.tar.gz` SHA-256 `353046febce55867c30a30931bcd01465a90511b6e1fc6a8dc5b1875c4714e7b`，保留12原始日志、首次失败源码、19最终源码/测试输入及两份结构化测试报告，无项目DB。仅protected AGENTS保持dirty，未push；后续唯一owner交接和完整候选新审仍由总控安排。

上一阶段结果：实际 POSIX 私有密文仓库与 metadata 持久审计、Electron safeStorage factory，完整check770TS/1052Python、sources12及54项文件/发送门故障反例均保留。Linux arm64 Electron44.9.0组合六场景曾按当时源码/运行字节与43项raw摘要验证；本轮gateway新增私有定向取消，因此该旧组合不能称为当前完整候选的平台通过。未变化的凭据/私有仓库/审计/factory平台事实仍按其原hash引用，没有重复不变平台测试。下文旧计数/依赖值作为历史。

当前交接：[具体 main 内部类型、调用顺序、失败行为和共享文件面](../../iterations/I06/main-integration-handoff.md)、[持久化独立审查](persistence-review.md)、[实际组合证据](platform/combination-linux-evidence.json)。正式接线、真实 Store/导出/窗口联验、Windows ACL/其他平台、指定双审/PR/实际 CI/远端合并仍未完成。未 push，不改总控 state 或 I05 共享文件。

实质代码保全提交 `6316c1952add9625e914dea096950a4b4dbf81b0`；之后只同步 ADR/验收/状态中旧的“未实现”描述。main 交接文档 SHA-256 `f77edfa9703dadc988647db4bd0b87ac199ee09f2c8f7dea5b9a180e5361fa90`，[阶段验证 manifest](evidence/persistence-platform-20261021.json) SHA-256 `a272a3325d5ea8ce74733d83a1a102a673ea860b99ed2d7c6c13ccb7f334467e`，组合证据 SHA-256 `7a7462d6c37612cd5fee2daf7e6209cac95dc5313454b1c05542cffcb645194f`。实际 raw archive 已复制保存在本 worktree 忽略目录 `tests/i06-private-platform/out/combination-platform-raw-20261021-r4.tar.gz`，SHA-256 `b8a37192936a32600f4b353d8c2f126f3cb872c961c6e2ff8fd4cd2af7da2361`；391 个归档文件中 43 项最终 raw 已在根独立逐项复验。仅 protected AGENTS 继续 dirty，原仓库 SHA 同值未变。

## 身份与保护

- 开发会话：`01a15746-c2e2-7ee0-836b-c8c92346ddd4`；总控/额度唯一负责人：`01a154de-843b-7a00-8a80-51ba1c0aebce`。
- 唯一可写 worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-model-gateway`，分支 `feature/I06-model-gateway`。
- base/启动 HEAD：`1b6df7a220fc9a67d7046133a340085f03f0a96c`；origin `https://github.com/NOmoreJoke/OntoLearn-Studio.git`。尚未冻结完整候选。
- 初始核心检查点：`8336559c65b8d8ece3fcb15ea3dc224c398b7d9c`，流程追加为 `56de8312c72d8ec2dd7a6739ac01f5737e5914fe`。续跑发现凭据密文与主体/版本绑定缺口，已修复并完成新版内部复核和验证，后续检查点记录于本文件末尾；旧检查结果仅对应旧版，不作为新实现通过依据。以上均不是完整验收或指定双审候选。
- 当前核心实现源码检查点：`637e0e6869091610141b0b9b9ebf01545205e648`；此后有流程文档与超时/容量专属测试追加，五个实现模块哈希未变，完整候选尚未冻结。每次新版验证均保留独立证据，不沿用旧版测试通过替代新增反例。
- 已完整读取 Goal（含第九节）、scope、transition policy、parallel coordination、state 和 before-I06 两清单。最新指南与原仓库 SHA 均为 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`。AGENTS.md 是唯一启动时 dirty 文件，保护、不暂存、不混入功能。
- 仅写新 `apps/desktop/src/main/model-gateway/`、`tests/unit/i06-*`、`docs/iterations/I06/`、`docs/reviews/I06/`。未写 main/preload/renderer/CSP、公共契约、storage/protocol/失效表、依赖/锁、总控 state 或其他工作区。
- `npm ci --ignore-scripts`、`uv sync --frozen` 建立本 worktree 独立 node_modules/.venv；未链接他线环境。无 Electron/GUI/native/HMR 启动、无凭据提示、无真实模型/真实密钥/业务外发。

## 交付与验证

- [ADR-0004 草案](../../iterations/I06/ADR-0004-model-gateway.md)：进程归属、授权身份/失效、发送竞态与凭据适配器。
- [完整验收和接口需求](../../iterations/I06/acceptance.md)：向 I03/I04/总控提供精确依赖，当前私有形状不作公共协议。
- 当前专属测试：77 项（网关 55、凭据边界 22）通过，含真实 loopback 假接收端、定向取消、响应上限、字节复制、密文身份/严格信封及超时/容量反例。测试边界不等于实际 OS safeStorage 或接入运行证据。
- 新版 `npm run check` exit 0：lint/format/typecheck、81 TS（77 I06 + 4 既有）、生产构建、ruff、198 Python 全通过。构建不包含尚未接线的 I06 模块，其 TS 检查及专属测试单独覆盖；未启动 Electron。
- `npm run verify:sources` exit 0：12 项既有归档源文件一致。I01 归档 M0 更新计划与原仓库当前只读文件 SHA 同为 `c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96`。
- 独立内部只读审查 agent：`/root/i06_design_review`，两项实现意见已修复并获关闭，最终未发现新增阻断，独立重跑 50 网关测试通过；见 [内审记录](internal-review.md)。不替代指定双审。
- 首次 check 仅被 no-control-regex lint 阻断；已等价改为字符码检查，最终完整 check 通过。验证摘要和文件哈希见 [evidence](evidence/validation.json)。
- 续跑新增的四项凭据绑定反例在旧实现上实际失败；密文改为封装并核对 ref/主体/版本，新增严格格式反例。独立 agent 再次实际验证 72/72，并确认绑定问题关闭、未发现新增阻断，见 [记录](credential-binding-review.md)。本轮 check 先后遇到测试变量 lint/格式错误，均修正后完整通过；新版文件哈希和日志摘要见 [证据](evidence/credential-binding.json)。
- 依赖已通过正式 `wait_threads` 重新核验：I03/I05 的实际 turn 为 inProgress；I02 为 inProgress，尚无 I02/I03 合并证据，I04 在总控清单仍 pending。未把对 I02 的审查应用授权扩大到本会话桌面操作；本会话继续无 GUI。
- 2026-10-20 总控请求受限错误需求：已整理 [11 类公共错误映射输入](../../iterations/I06/public-error-requirements.md)，含建议 messageKey、严格空 safe params、禁止透传集合和 retryable/禁止自动重放边界；供总控转交 I03。未修改公共 contracts 或提前接线。远端 develop 本次只读核验仍为 `1b6df7a220fc9a67d7046133a340085f03f0a96c`，正式依赖尚未合入。
- 已实际只读核对 I03 的 `docs/reviews/I03/handoffs/I06-error-disposition.md`（SHA-256 `25910655ff5f03e20509393a45863af0093a0d7d0436cceb72ff1603deaee50a`），[承接读回](../../iterations/I06/public-error-requirements.md)记录了通用错误仅安全兜底、新契约版本/公共正反例/双审后才精确接线、独立 cancelled 结果分支、网关新错误空 params/false、retryable 不授权自动重放及写任务先对账。现有 INVALID_REQUEST 的固定 `{field:"params"}` 兜底按实际源文件明确保留，没有误写为空参数。未修改 I03、共享契约、实现或测试；Goal 仍为 blocked，原待验不变。
- 超时/容量续跑追加五项验收反例，未修改实现：凭据等待超时后零外发及恢复复用、审计等待超时零外发、第五个请求不排队且取消释放容量、持续 503 最多两次尝试、真实无响应本地接收端超时不自动重放。前两项以受控时钟验证等待边界，最后一项使用真实 Node socket/计时；见 [本轮证据](evidence/timeout-capacity.json)。此类测试追加仍属于未来完整冻结候选的受审范围，不能沿用指定双方旧版通过（当前也无指定通过）。

## 依赖、双审和下一步

### 2026-10-21 实质接续（当前）

已现场核验唯一 worktree/feature 分支/origin，正常 merge 已批准 develop `5f910b52c69d86a1076b2032e5d3c63e715947f3`，本地 merge HEAD `0c569851baa067a08ad8cf8d6d94437ef9620d69`，保留 I06 原历史。premerge 证据逐项复验既有 I06 源码/测试与 AGENTS SHA 未变。原 Goal 和全文、最新 scope/parallel-coordination、PRD/S3 原验收及第九节已实际接收；旧依赖状态仅作历史。

本阶段责任/并行接口/验证见 [实质计划](../../iterations/I06/persistence-platform-plan.md)。I05 唯一维护共享契约/Store/job/主进程/bridge/UI/入口/依赖锁/共享 CI；I06 不争写这些文件、不提前公开注册。审查应用预约仍归 I05，本机 Mac 原生/Keychain/GUI 操作禁止。Linux 平台采用本线独立 Docker 环境，不借用其他线运行数据或可变依赖。接线、实际 Store/导出/窗口联验、Mac/Windows 平台与完整指定双审/CI/合并仍待原门禁。

### 本次恢复：I02 合并已核验，I03/I04 仍待就绪

- 本次已直接核验远端 develop 为 `c2f9b038b23f9f48cdbb8f433a89b55a00edc9d3`，PR #3 实际 MERGED 到 develop，原 base 是该 merge 的祖先；PR run39364497557 的 Quality/macOS/Windows 三项 SUCCESS。合并后 push run39364825646 同一 head 也 completed/success，三个实际 job 均 success。没有沿用总控陈旧 state 中 I02 merge=null 的值。
- I03 的实际任务已 terminal（idle/completed，cursor `4e760116-fc4e-44e4-82df-053fdee3eaa5:91`），不是仍在运行的等待句柄。已观察到本地候选 `8305d204bb132eb8e695b2122ecbf48f67120f2a` 仅在 feature/I03-protocol-contracts；开发者回执指定双审未创建、未推送/合并。I04 在总控清单仍 pending，无线程 handle。依赖门未全部满足，不能提前接线或把本地冻结当已合并。
- I06 保持原分支/实现基线，没有 rebase、产品接线、依赖或测试修改。本轮只追加 [真实依赖核验证据](evidence/dependency-resume-20261020.json)，不重复无变化检查；已有实现/测试哈希仍匹配上次完整验证。I02 依赖已解除，剩余为 I03/I04 合并与后续隔离运行条件；本次恢复按新一轮核验处理。

### 本次恢复后三次核验：再次 blocked

- 第一次：I02 实际合并已核验，I03 处于本地冻结、未双审/合并状态，I04 pending；没有把 I02 完成当成全部接线依赖完成。
- 第二次：正式句柄确认 I03 已恢复新 turn，正在刷新基线且审查应用时段只预约给 I03；执行一次 45 秒实际等待，cursor 到 `4e760116-fc4e-44e4-82df-053fdee3eaa5:98`，仍 inProgress。没有把 I03 的 UI 许可扩大到 I06。
- 第三次：对同一活跃 turn `01a15763-b232-7132-b72f-d23b8b7c3baf` 再完成 45 秒等待，cursor 到 `4e760116-fc4e-44e4-82df-053fdee3eaa5:105`，仍 active/inProgress；远端 develop 仍 `c2f9b038b23f9f48cdbb8f433a89b55a00edc9d3`。总控清单 I03 merge=null、I04 pending/无线程。观察超时不等于任务停止，没有重启或打断 I03。
- 连续三次相同的 I03/I04 依赖门未满足；当前 I06 可独立实施及验证的授权工作已收口，无法在不提前复制未批准契约/接线或违反平台环境限制的情况下继续必要实施。正式工具已返回 blocked；不是因为实现困难、额度不足或单纯等待一次。
- 当前保全点为 `ca59135c4abc137290440f148357445e021dcef6`，后续仅追加本记录；未改实现/测试/依赖，未 push。由总控核验 I03、I04 真实合并后恢复同一会话，刷新包含 I02/I03/I04 的基线并继续原全验收及指定双审。实际平台/外部审查环境仍按原约束安排，不因恢复自动取得 GUI 许可。

### 此前阻塞核验与恢复条件（历史快照，I02 状态以上文为准）

- 同一“正式依赖尚未合并、平台/指定审查缺少本会话可用环境”条件跨初始交付及后续多次 Goal turn 持续存在；期间仍完成凭据绑定修复、I03 接口交接和超时/容量反例。当前未发现仍可在授权阶段内独立推进的必要工作，不能用新文档/重复测试或提前复制未批准协议替代实际依赖。
- 本次 `git ls-remote origin refs/heads/develop` 实际返回 `1b6df7a220fc9a67d7046133a340085f03f0a96c`；核心/测试哈希与最新已通过验证一致。检查点为 `208f48bf9888a78b19e4a8049eb29772b3f10f24`，后续仅追加流程记录。
- 对同一实际任务执行 45 秒 `wait_threads`，均仍 inProgress：I03 cursor `4e760116-fc4e-44e4-82df-053fdee3eaa5:49`，已明确收到 11 类需求，尚在形成新候选；I02 cursor `72c9322d-f0e9-4b8f-bd47-081efdc63a8c:638`，正在核对 GLM 报告勘误，未合并。总控清单 I04 仍 pending、无任务 handle。观察超时不等于任务终止，没有重启他方任务。
- 正式 `update_goal(status=blocked)` 返回 blocked；未缩小完整目标，也未声称全验收、指定双审或远端集成已完成。
- 恢复：由同一开发会话在总控核验 I02/I03/I04 实际合并后继续；刷新包含依赖的 develop，按 I03 冻结公共契约映射并接线。实际 safeStorage/native 与指定双外审须有不干扰用户的隔离环境或用户明确时段；当前仍无本会话 GUI 许可。语义特定来源仅在需要时等待 I05。之后按原全验收 → 同版双方独立通过 → PR/实际 CI/正常合并/远端核验完成，不能沿用阶段内审作为指定通过。

正式主进程/bridge/窗口/任务联验等待实际 I02/I03/I04 合并；语义相关材料等待相应 I05。然后刷新 develop 基线，核对契约与唯一权限/存储边界，补齐真实持久审计、私有凭据仓库与平台 safeStorage，验证失败不影响本地保存、导出排除与重连。原生/平台行为仅在隔离环境或用户明确时段实测，不在当前桌面启动。

ZCode GLM-5.3/最高、MiniMax M3.1-Flash/xhigh：均未新建正式审查任务、无通过报告。不得以阶段提交或内部审查当作完整冻结候选；实际依赖和全验收后，同一完整 base/head 各新建独立任务并核验真实完成。变更受审代码/测试/配置/依赖/验收/基线即新版双方新审。

push：未执行。PR：未创建。CI：未执行远端候选。合并/远端 develop 核验：未完成。仅完整验收+双方同版本明确通过+意见处置齐后才预约总控串行集成、推送与 PR→develop（创建后 attach_artifact）；实际 CI 及远端核验通过才完成 Goal。当前无实际额度告警，不兑换重置、不新增支付、不擅自换模型。
