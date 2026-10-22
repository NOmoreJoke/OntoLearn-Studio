# 私有 stage 原型验证与历史处置索引

固定实现12699cc0f536f5875e8b021349b58c2c954145cc，三个完整增量文件；local parent74b17a4，shared批准base5f910b5，原证据e651993，等待/blocked/设计流程延续到9a1baa74f2b6482106eb7c8090efef7f7ba065e2。不是新S2，不取代S1，不是接入持久账本的完成产品。精确路径、Gitblob、bytes、raw/archive SHA见validation-and-history-map.json及input-manifest.json。

| 原件                                       | 实际历史结果与归属                                                                        |
| ------------------------------------------ | ----------------------------------------------------------------------------------------- |
| stage-first-pytest.txt.gz                  | 49通过/3失败：期望后置错误而先触发canonical/job守卫；修改负例定位，未放松实现             |
| stage-second-pytest.txt.gz                 | 中间53通过，非最终候选                                                                    |
| stage-final-pytest.txt.gz                  | 完成回执方案前57通过，未证明后来真实stale路径                                             |
| stage-completion-first-pytest.txt.gz       | 55通过/1失败：同根fixture更新未同步completion root；同步测试数据                          |
| stage-completion-second-pytest.txt.gz      | 67通过/2失败：实际marker字段误猜before/after；按批准Store改before_snapshot/after_snapshot |
| stage-completion-final-pytest.txt.gz       | 中间69通过，后续内审两P2修复后增至80                                                      |
| stage-npm-ci.txt.gz / stage-uv-sync.txt.gz | 本树独立环境从未变锁安装，不是产品验收                                                    |
| npm-check-stage-first.txt.gz               | 中间1163 Py，不能替代修后1174                                                             |
| stage-reviewed-pytest.txt                  | 最终80专项通过，exit0；绑定126三个文件                                                    |
| npm-check-stage-final.txt                  | 最终648 Vitest通过、16 headless明确skip、1174 pytest及lint/格式/类型/构建/ruff通过，exit0 |

两个最终明文及9份gzip均绑定原始/压缩字节。本轮仅解压/hash核对，不重跑上述命令。stage-reviewed日志SHA2fa33ce7e92730ba902778819c283611a6b83bab1ac5c87cba3280bdea55cc31；fullcheck日志SHA842822b3029753ec9a226ca79dedb184b11780b270e95a5e0d20299b240fe9a9。继承S1的664/1094属于765的原显式headless验证，本stage完整检查16套明确skip，不能互代。

STAGE-01/P2：根输入版本缺非空字符串验证、plan_id可为非文本；独立修前纯探针复现空根仍receipt，修后要求非空非空白str、十个负例及独立invalid-plan-identity探针关闭。STAGE-02/P2：quality测试仍query形态，修前仅静态发现；修后真实canonical validation-kind/validation.execute/name-required依赖与参数/结果形态，错query替换拒绝，最终80和1174包含。旧内审关闭不是本轮指定Pass，指定方须逐项重判。

完成回执方案不是新增第三项已复现缺陷。批准I04修改事实后返回旧结果真实stale；原型保留该状态，以完成时保存的current原始DTO绑定，不把今天stale改名historical/current。当前终态仍须current，分页全量/结果job/来源/祖先/顺序/当前plan严格核对。completion必须独立owner join，不能从今天结果补造当时current。

两新增真实I04探针只测JobStore read发布→事实编辑→旧结果stale→result.page→binder与再次编辑后require_current拒绝；test.read发布给定rows，Plan、ledger、祖先视图和完成回执由测试内存对象承载。不能算SPARQL/SHACL、受信持久账本、跨窗口重开CAS或产品域执行；StageReceipt不授予领域passed、操作完成、独立迁移成功。

本地parent74b的765全部运行源保持；S1是课程/reset/reducer/I04七项与独立UI，stage只新增三个文件，没有正式接入LearningService/UI/IPC/registry/Store，d969/72aa/124ed是另树流程上下文，不得夹入126运行输入。H1/H2/旧UI内审与失败原件随完整继承diff/流程ref保留，旧报告数值只归各自候选。设计回执9a1仅accept-design-alignment，runtimeAdoptionApproved=false，不把T01其他未批准实现当依赖。

必须报告全部父门：T01受信attempt/跨attempt辅助/完成时不可变持久ledger/真实输入epoch祖先/一致读与消费CAS；T00唯一公共合同；真实领域adapter、正式App/bridge/生命周期、课程入包/离线无模型、T08完整代做/T10实际报告、双OS/native/包与至少五名非开发新手80%、同版指定双审/全部意见/CI/正常develop合并/远端/57P0。关键验收缺失不得以“有界原型通过”给整体Pass；按指定模型实际不通过/无法验证报告及终态保留，补齐后新候选验证/双方新审。
