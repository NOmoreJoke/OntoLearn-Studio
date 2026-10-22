# I06 对象ACL表征决策实验：源码窗口

2026-10-22。原I06从7ea3bfb06ff117f80f0aa770ab5f563b6b5c3b3e继续同一Goal/树/分支。总控已收完整合同与独审，见I06-full-positive-contract-root-closure.md。现仅授权编写并静态审查独立单用途实验源；**不授编译、API/探针执行、fixture创建或新CLI**。

## 唯一源码writer及冻结输入

唯一新增源码为packages/native-location/tests/location_metadata_contract_probe.cc。配套仅新增本实验独立过程目录，保存7ea3固定decision-experiment.md（15506B/SHA256 55f073f1352ef7e621455a2fb70dfe92c6287e10c591459abf916ee4d532c1e7）、observation-and-acl-contract.md、独审和本窗口原字节或固定引用。不得修改现有Mac/core/ABI/Windows/Node/TS、原test/core main、CMake/driver/锁/依赖、旧准备或失败原件。新程序不链接产品owner注册表，不产生cap/owner/child，不接收用户路径或任意API参数，不做通用runner。

以已收件提案为全部行为边界：E原样empty root/sub/member三个必需正例先行，全部有充分响应才建立N的目录/普通文件单ACE对照；不能另给E子项设ACL、换强read FD、重建fixture或改变环境求绿。目录按原O_RDONLY模式，member按O_EVTONLY模式。固定case0–4、同held对象、自有变更阶段协调、原UID/mode/type/links/identity安全门保持。

## 必须在源码固定的证据

- 精确请求mask/4字节packing、REPORT_FULLSIZE及PACK_INVAL、固定4096B复用buffer、完整长度/必要actual位/相对signed offset/受检乘加/对齐/变量区/attr_length/magic/header/flags前门。缺位或零占位不解析为absence；NOACL先判再算，H与H+A精确长度按目标定义固定。
- 核sys/acl与kauth目标字段/常量的语义映射及布局，尤其ALLOW→PERMIT、目录LIST_DIRECTORY及文件READ_DATA、owner qualifier与零其它flags；只核常量数值碰巧相等不够。用既有官方目标SDK/必要固定发行源精确片段作依据，不引入系统库源码同源交付要求。静态编译期断言预写，实际编译由T03另授。
- 两N对照在同一已验证payload内逐字核内部owner UUID、精确ALLOW flags与对应rights，未知/矛盾不记form3或eligible。不得只凭count1判断有效对照。
- API调用清单须与源码路径逐项核算：最多5次观察fstat加2次member创建identity记录，即fstat≤7；fgetattrlist≤5；geteuid一次、当前owner mbr_uid_to_uuid最多一次且仅在E合格后供N使用。ACL setup/get/set/valid/free、open/close和自有cleanup按提案明确列数及失败路径；禁止额外响应/FS/进程探针、扩容、重读、换API、动态fallback或重试。
- 应用侧上限五个长期metadata FD、一个暂态创建FD、一个ACL setup工作副本、两组三对象fixture及一个4096B响应buffer。每个已知ACL free一次、FD close一次，失败号码退役不重试；仍按规定收尾其它自有资源，未知优先retained。不扫描/tmp、旧fixture或PID，不扩大cleanup。不能把应用清单当libc/kernel内部heap/调用/wall硬界。
- 输出仅固定schema/有限枚举与布尔，保Int32/UInt32宽度约束；最长行≤96B、stdout预算4096B且设计最多1018B，stderr≤4096B。无payload、路径/FD/PID/UID/GID/UUID实际身份或任意异常文本。stdio失败不重试、不签eligible，成本非零。
- 最终disposition只为本次采用/放弃决策：全部五样本及可检查收尾成功才eligible；任一必需empty缺位/占位为unproven并停止该route；API/setup/畸形/对照不符为failed；释放未知为retained。先收尾再决定最终结果，不能让异常退出跳过已知资源责任，也不能把leader收回当drain。

## 验证、独审与交回

仅静态/source检查与独立agent审新源码、解析边界、调用/输出/ownership及决策有效性；未编译须明确NOT_BUILT/NOT_RUN。既有JS/TS/Python无变化不重复正常套件，C++实际编译和依赖闭包/SDK/符号由T03唯一owner后续核验。不要重开旧17KB控制算法、构建供应史或已收件旧包大审。

固定新源码ref、纯过程ref、有限manifest、九源和AGENTS保护，给T03所需精确source/headers/symbols/entrypoint/build输入建议后交root。T03本轮无新任务或第七构建许可；实验源码收件后再由root明确单用途构建路径与累计预算，随后才有一次运行窗口。本阶段不预建record/运行目录。

无产品行为/原test期望修改，无GUI、SQLite/heap/OS资源拒绝线、DB、付费、push/PR/merge或Goal变更。完整功能与双OS/指定同版外审/CI/真人/远端门、T01损坏保护HOLD不缩减，旧003/004失败和未知保留。
