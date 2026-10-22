# 完整正例合同与决策实验：独立窄审

结论：**本轮合同/有限实验决策提案可交root，无未关闭的设计阻断；唯一P2“count1对照未核ACE本体”已在本轮局部修订关闭。** 这不是完整产品接纳路线已证、实验实施/构建/CLI许可或N0通过。当前产品仍不能完成必需正例，组件和失败状态不得以本静态结论转成运行成功。

## 受审身份及实际范围

工作树为/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-native-location-N0，方案基准904cc2675c37387621954bb5a39a055c09d492b3、产品1217e0f63a9c62b72e01046ef5fbc5c53434251a。已全文读最新AGENTS/common、根前提独审及完整正例合同窗口；本轮只读指定五文档，未重开旧18件、17KB算法、完整源码或构建供应链。

根前提独审12583B/855e591907422e3d9c1ef98510d230261e4f126a4cfd0d6c982e51375f221eae；根窗口4225B/24ac2ccc3e64fb59b8c786cdd7ee273177ae9d14411f563d6589d106445b68fa。规则的保护身份保持AGENTS15852B/78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759、common17891B/e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0。首次合并cat输出发生显示截断，已单独重读common，未把被截断内容冒称完整读回。

最终实际读取/实算的候选如下：

| 文件                            | bytes | SHA256                                                           |
| ------------------------------- | ----: | ---------------------------------------------------------------- |
| observation-and-acl-contract.md | 12447 | 209f25ba0e82e982c3d04a0650f7f005171d38f3a767108e5e2af1cfe6b7238c |
| decision-experiment.md          | 15506 | 55f073f1352ef7e621455a2fb70dfe92c6287e10c591459abf916ee4d532c1e7 |
| experiment-static-bounds.json   |  1377 | 63623e918aca20d85cf5ffa03404d2cb662fc5e07666a15ddee58ab9cc9ff8c1 |
| evidence-and-preservation.json  |  6991 | 7e67a9b2ebc55d08553f3c8c58ab43829e36bea1afef341361a41d9c6f499378 |
| handoff.md                      |  3435 | c3c16b1428a9933f9c5e969390413e04054ab171e7fb56af9c8c7aea76e30f81 |

全程仅Git/文本/stdlib JSON、哈希及静态字符串算术，不import产品、不编译/测试/npm、不执行任何native/API/ACL/FS/DB/进程探针、不扫描/清理/kill、GUI或Goal操作。只写本报告并格式化自身，未改产品、测试、主合同或其它文档。source/历史保护与先前官方查找结果按evidence记录引用，本轮没有全量重审或重新下载，不能声称又独立验证了全部历史/目标平台行为。

## P2-01：单ACE对照本体，已关闭

初步发现针对decision-experiment.md14565B/216df9bc25163ffc300795a66deff596960e37f65060036e7bdcb8945f3f8fd8的52、68、82行：完整header、H+A长度、count1和collection flags0仍允许sole ACE是DENY、其它qualifier/继承flags或不同rights。只核这些外层字段，就可能把与setup不一致的对照记form3/eligible，影响采用路线的证据可信度。这是本实验合同的必要修订，不是已执行产品漏洞或实测失效。

最终55f073稿新增同一已验证payload内的精确门：ace_applicable等于内部已取得owner UUID；ace_flags精确KAUTH_ACE_PERMIT，无继承/其它entry位；ace_rights精确对应目录LIST_DIRECTORY或文件READ_DATA；目标SDK/API到kauth映射必须在源码/SDK冻结前核定，未知不能靠数值巧合通过。DENY、其它qualifier/flags/rights或矛盾failed并停止，不记form3、不eligible。form3定义、采用判据、bounds和handoff已同步。

修订只增加既有有界payload解析与内部比较，不新增API、敏感输出或样本，不改变7/5调用预算。该项在文档层关闭；映射/布局和真实解析正确性仍须未来精确源码与SDK证据，当前未验证其实现。

## 正例路线和观察语义

合同正确采纳根澄清：UUID门是可替换实现见证；不默加单次原子调用或系统库源码同源交付件。必须保持同held对象、真实ACL语义、自有变更协调及受控empty正例可用，不能让全部正例UNSUPPORTED仍完成功能。

装配责任具体到观察期间borrowed FD live、不关闭/复用，owner/group/mode/ACL/links和自有namespace mutation稳定，UID/groups不变。harness直接syscall不受native mutex自动保护，必须阶段互斥；setup、负例mutation、cleanup置于同步观察之外。root缓存不是重查OS，held-object-only不是名字持续指向、权限lease或ABA不可能证明；晚epoch/TTL和失败资源仍由原owner收口。没有发明OS锁，也未以外部未知窗口开启production admission。

对象级状态表没有混淆API结果和ACL状态：NULL/ENOENT、filesec valid0、security缺位/零占位均不构成absence；明确NOACL、有效empty、任意ACE、畸形/跨响应矛盾、释放未知分别处理。只有充分无ACE证据与原标量/身份/安全检查及收尾全通过，才可NL_OK/acl_checked。setup历史不代替实际读取，未知ownership/释放失败优先保留责任。

完整产品目标明确含root/sub/member及替换后新member的原owner/root/acquire/observe和关闭；五样本先导不代替这些原case。当前尚缺目标受控empty对象的可判别实际响应，若仍缺位则对象级absence语义也缺失。方案没有把“可能有稀有header”当完整路线，亦未声称所有公共API均不存在合同。

## 决策实验是否值得另审

五样本提案具有采用/放弃后果：原样empty root/sub/member三对象必须全部得到充分无ACE响应，目录/普通文件两真实单ACE对照必须全部精确核同，身份/标量/setup/收尾均合格，才eligible进入固定profile适配设计。任何必需empty缺位/零占位即放弃当前fgetattrlist-only路线，不以setup已知、对照有ACE或少数对象成功补写absence规则。

FD模式含目录O_RDONLY和普通member O_EVTONLY，不能换更强read模式追绿；两个member的创建FD身份与观察FD核同。实验独占两个新fixture，不另给empty子项设ACL强造表征，不更改环境、重建重试或省略失败样本。setup失败、未知flags、畸形、矛盾、错ACE或目标不支持均停止；释放未知单列retained。它能改变“选定profile是否值得适配”的决定，区别于此前两个UUID布尔位，但尚未证明路线实际可用。

同FD fstat与fgetattrlist并不产生共同原子时点；提案用受控自有mutation协调保持实验前提，没有声称排除全部外部ABA。完整required mask、REPORT_FULLSIZE、PACK_INVAL缺位拒绝、相对引用/溢出/对齐/变量区、magic、NOACL先判再受检乘加、H或H+A精确长度及collection flags0均明确。ACCESSMASK只比权限，目录link不冒充stat nlink。ABI编译期断言/目标符号/ACE映射仍是未来先决，不由SDK声明宏直接推定跨版本安全。

## 固定输出、资源与权限

实算格式最坏71/63/64B含LF，case0–4、布尔0/1、固定api/form；包含Int32最宽errno、UInt32最宽bytes/count仍每行低于96B。每样本最多三行，五样本加最长28B disposition共5×(71+63+64)+28=1018B，低于stdout4096B；stderr另4096B。未到达字段归0、errno仅API失败有效、NOACL哨兵不参与乘加。原值身份、路径、payload和任意异常文本不输出；stdio失败不重试或伪造eligible。

应用侧预算明确5次观察fstat+2次member创建identity fstat=7，最多5次fgetattrlist；固定4096B复用buffer，无扩容/重调/换路由。五metadata FD、一个暂态创建FD、一个setup ACL副本、两个三对象fixture是应用清单，不证明内部heap/系统调用/wall硬界或stdio零成本。实际源未写，不能把该算术当真实调用轨迹通过。

每个已知ACL只free一次，自有FD只close一次，未知责任保留，失败仍按规定收尾，不签drain或清理成功。没有产品owner/cap/child，不能拿这个独立实验代替失败owner close或原生命周期验证。

拟唯一新实验源只是申请，T03独占构建/锁/输入/SDK及精确命令；root仍需另授源码、构建和一次CLI。当前未建源码/record/运行目录，不复用004许可/旧pair，不改变两产品writer或其它共享所有权。若路线eligible，仍须另审产品parser并实际跑原正反/生命周期case；若不合格，保持模块未完成并补精确正式合同，不能转移给用户降低目标。

## 最终限定

唯一P2已按一轮局部修订在文档层关闭，最终五件之间未见新增阻断或误授权。可接受本轮合同与实验决策提案，**不能批准具体实验执行、产品成功修复、第七构建或完整N0**。003/004失败、drain/fixture未知、目标双OS/EXCL、父功能、指定同版外审/CI/真人/远端及T01 HOLD和已拒SQLite/heap/OS线均保持。报告冻结后停止改写。
