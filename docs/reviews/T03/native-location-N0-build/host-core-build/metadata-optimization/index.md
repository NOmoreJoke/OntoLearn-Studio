# N0 inventory metadata修复候选

仅落实3192B/SHA a2b2bc77a41c59e5ad4e3322d511cf4704a5e529f86bfbc96ea153e942fa164f窗口。首轮实际失败和85原件在7bfd7c493698107fc70913e249d164cdb6515205保留，当前只静态metadata修复，未第二configure/build、未实体pin复验、未执行产物或测试。

固定产品ref95f07d931eeffd3bdcd52cb21e9fa2d8a1db12bd（parent7bfd），完整12候选见candidate-input-manifest.json，实际最小三writer差异见implementation-delta.patch。两inventory descriptor只由原四pin变为{source:原四pin,records:新四pin}，其余审批/source/platform/tool/env与原c80完全不动。原SDK JSON/资源JSON、所有供应来源与28行追溯不改；derivation-receipt.json及独审固定33464/9308四pin/roots/顺序/0B的全映射。

新JSONL是非执行数据：固定小header与每行四pin JSON。字段顺序/类型/小行界限先约束，仍由真实JSON解析器处理字符串转义，不用正则拆分JSON或手写JSON解码。header prefix/suffix通过小JSON sentinel验证files槽位置，整行join重建原JSON的SHA；另重建规范JSONL SHA防丢行/CR/BOM。CMake大source JSON只在一次metadata阶段按root数有限取值，root缓存为indexed变量；逐file只解析当前小行，SHA键集合拒重复/碰撞，然后原nl_pin仍在project之前逐实体realpath/size/SHA全检。Node另完整逐项核原source与行对象、UTF8往返、限制split数量并对records原bytes重建防尾截断；原CLI/build/R5尾部不变。

首次静态CMake全映射确曾exit1：SDK /usr/share/man/man1/[.1含未配对[，CMake list令物理33465行变19714项。旧full-metadata-only*、list-line-diagnostic*和旧harness/初始小例全部保留。这只定位本次静态容器反例，不认定原configure超时唯一根因。

最终以无损@A/@B/@L/@R/@S作为CMake list容器传输（@先编码、最后解码；JSON内容仍原字节/原解析器），避免括号、分号、反斜线及token碰撞。返回与物理循环间保持encoded list，只单行或整join后恢复，root也避免进入raw list。

实际验证：final-static-validation.json的Node --check及Prettier均exit0；validation-v3/node-metadata-validation.json最终24项pass；validation-v2/cmake-finite-validation.json的19项符合预期，含合法0B/转义/未配对[与后随行/根方括号/@token，以及重复路径/越根/计数/空行/CRLF/BOM/未知键等；validation-v3/additional-guard-validation.json另2项cap/摘要键碰撞拒绝，且当前CMake metadata函数与v2实际执行harness逐字相同。validation-v2/full-metadata-only-result.json完整9308+33464 metadata-only exit0，无compiler/project/实体pin循环。没有测量性能改善或实际RSS/总I/O。

原32GiB构建账/200000实体记录界、旧供方9745727085B账保持。read-and-parser-budget.json分开记录首轮实体校验上界、未知CMake进度、本轮metadata reserve与重复metadata访问。1941B账澄清明确实体200000与纯metadata逻辑访问分列，本窗口metadata cap400000、1GiB预留计入32GiB。追溯补账发现原owner223168只覆盖显式row循环，补source/派生/诊断后owner608116，加独审128316=736432；有限/收尾预留5120，保守741552，超过400000，750000申请随后也不足：root另有一次source/sidecar成对映射85544，累计已知821976，有限/收尾预留5120共827096。1754B/SHA130323fc6d12a2823e6bb9591f79b13807c5695bd724b8ad902bad02abf43363精确补授本有限metadata窗口累计1000000，保旧400000不足事实及全部前后账；不扩实体200000/32GiB或新构建权限，不隐去原约数或更正理由；不再无变化全量重测。新一次两前门若获准，其声明pin+metadata为17,755,667,816B；累计保守计划含静态/收尾reserve为37,044,475,528B，比原32GiB多2,684,737,160B，待根给精确下一累计界，不自行扩额或清零。

正常npm check包含测试/产品build，超本次metadata窗口未执行；verify:sources只核原64档案，本轮未改而未重复。没有重审/修改R5或I06、AGENTS、依赖、原型、全局配置、Node/Windows门、Goal、push/PR/merge。独审通过也只签静态候选，原TC/core approval字段不能据此自授新输入第二次执行；须根根据新固定ref与账另授。

Node最终24例有原stdout/空stderr和原tool invocation/assert出口证据，未单独保存同时结构化子进程receipt或时间戳。final-node-metadata.execution-reconstruction.json明确是事后据原记录重建的argv/exit0证据及该缺口，未冒充原件、不无变化重跑。

最终独审：independent-review.md10643B/SHAf016b32259cab6404f441a15c9a6816d0fe0fd553bc59a7b06903175a99baa84签静态实现与全映射无剩余P1/P2；accounting-delta-independent-addendum.md3973B/SHAa3f85301b6cb973416e66a5f89df4c4b6f5eb3948c584d57d9edf6a88d3dcd66按1754精确delta关闭当前静态账界，保历史不足和Node同期回执缺口。两份均已全文读回，未追加新运行。
