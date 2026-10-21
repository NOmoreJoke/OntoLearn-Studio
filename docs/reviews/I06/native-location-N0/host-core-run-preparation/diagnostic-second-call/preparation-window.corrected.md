# I06 新诊断 pair 的第二次精确调用准备

2026-10-22。T03固定输入d98b503ebe9c477d30d0f36d831cffbeeaf2a988/过程d51a0555e6feb062fc935173222cc142687901a5已受限收件，见同目录T03-fourth-diagnostic-build-root-closure.md。继续原I06聊天/Goal及原树，仅准备，不执行原生调用、不重建。

新pair位于 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-native-location-N0-build/build/native-location/n0/darwin-arm64/a0e724fdf90afa980f01719fc8cc4d55f158400cf5abe26665c72a2d288cac77/core/artifacts/`：

- location_core_test：343920B/SHA256 `d4f5ca322146d9696860a74de4bee2ad27866a2223340669898fb82cbbfeb817`。
- location_child_probe：34120B/SHA256 `21928ca2b5570055fad4bebcd81fcb658016ca9a738294397a83056b662b87e8`。

以原固定准备 `b942e12cd122873109f4bd16d51e06e05ad7005d` 的exact-tool-call.preparation.json arguments为唯一模板，复制到新独占过程 `docs/reviews/I06/native-location-N0/host-core-run-preparation/diagnostic-second-call/`。只改cmd中AUTHORIZATION、CORE_PIN、PROBE_PIN三项赋值，前者取新唯一record标识 `I06-N0-execution-002-a0e724fdf90afa98`，后二者上述新path/bytes/SHA。不改其余shell/Python文本/逻辑、timeout、env、信号/等待/清理、记录/双流限额或tool参数。保原shell独立-I/-S CLI及原workdir/login=false/yield1000/max1000；不改既有准备、execution-001、源码、API报告或Goal。

新副本及metadata明确PREPARATION_ONLY，record身份不代运行授权。保存固定来源/三赋值精确diff及AST除值一致证明、新cmd大小/SHA与全调用、简短handoff；独立agent仅核这一小增量/新pair来源，勿重审旧17KB控制算法/11562B已收件审查或重跑API探针。固定新过程ref交root读回后才另授一次CLI，不可按旧001窗口直接执行002。

## 固定目录增量更正（准备前适用）

总控随后静态读取发现旧cmd除三项赋值外，还在三处硬编码execution-001目录；只改record会遇旧目录存在而停止。现明确追加这三个精确字符串增量：RUN赋值的BASE后缀改为`/execution-002`；os.mkdir首参数改为`execution-002`；os.open同一目录的首参数改为`execution-002`。全部其余参数/flags、mkdir存在即停行为及控制算法不变。不复用、移动、删除或覆盖旧001目录。

上文“三赋值”应准确读为“三赋值加三个目录字符串”，共六处表达式值。独审和root AST证明仅这六位置改变；不准泛化全局替换所有001文字或改BASE/外层环境。原首版窗口保留来源和本更正，不能把其不完备说成真实运行失败；本窗口仍只准备，尚未执行。

本窗口无GUI/native/e2e/HMR/凭据/外部模型/付费/push/PR/merge，不复制旧运行结果充新证据，不删未知fixture残留/不杀旧未知PID。旧5处失败label不代表旧运行通过了前几case，新有界case/status/owner_nonzero仍待真实运行才可解释。现仅built-unverified；首次失败根因、native drain和所有父门保留。常规准备直接完成，无纯ack提交。
