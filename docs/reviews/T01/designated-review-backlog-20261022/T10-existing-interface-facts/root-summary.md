# T01现有材料回件：T10迁移/checkpoint纯设计

结论：**没有可直接交给T10的完整typed项目export/import供方。** 固定423实现有私有一致读checkpoint、域snapshot/补偿预演、部分应用CAS、唯一Store原子提交及既有operation/receipt对账；这些是可引用的原语。它们不包含完整业务typed闭包、全部版本/retirement账、跨项目typedID映射或import manifest/receipt/错误合同，不能拼成完整迁移接口。

[固定事实表](T10-checkpoint-fixed-facts.md.raw)按8个423固定文件逐项给真实函数/行号；[精确源码身份](C1-existing-checkpoint-source-identities.json)列ref/path/blob/bytes/SHA。Store.state的opaque payload保真、facts的owner/source_row/managed_value/object=NULL墓碑、snapshot当前dependencyVector分别说明；CP是domainSnapshotRef与应用覆盖引用，learning/audit仅JSON形状、draft也不是所有业务typed schema，非完整包。现有project_checkpoint一致读/receipt链核验可引用，workspace仅一个editor草稿。域restore限同项目可信snapshot历史，已有typed ChangeSet限ontology/manual，C1创建是空白创建，均未提供外来包导入/typedID重映射。

[既有f51材料与错误目录身份](fixed-design-and-error-identities.json)中完整f51 ref为`f51a9e10647d75cd07fe28007ab73c0e65451f63`，四件原文当前仍逐bytes等该ref：

| 固定路径（docs/iterations/T01下）                 | 角色                                                                                                    |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| format3-foundation-contract.md                    | 历史基础设计，§4/§7.4计划完整CP/恢复；部分基础后来实现，不据设计认完整恢复/迁移已交付                   |
| application-cas-contract.md                       | 私有metadata/draft/combined CAS实现合同；实际源码以423核，不含完整应用恢复/导入导出                     |
| changeset-business-service-implementation-plan.md | f51 typed业务方案，§2明确域restore不能冒全项目restore；后来原受限domain链已实现，不扩成完整import       |
| full-function-acceptance-map.md                   | P04/P07/S06/G02/G03/L01明确复制/导出/完整恢复/跨设备/缺原文件/学习的未交付与跨owner前置，不是可调用接口 |

上述四件bytes/SHA依次为19818/`d435f2340ddda8d77e1f74c9291a7de64dfcac2fba1ba2d3834c6e24498c9855`、3937/`bcbc9509dfc24f03d9a755c6d4031b31b61ac8ecd668be7c02c4d72c2b729e55`、27888/`39ebbf378386004eb9e8654bf9dbd7465e50d5215a87c55fde01cffc258d71e1`、46745/`1262fbee16e7819b87f7f04b83f19ec7ec6587d76af5459d706c4f686c6c71c5`；blob精确值见JSON。

错误方面：423的`packages/contracts/v2/errors.json`为16299B/`ad242d93ced7a0c8a463b708b7a1f3105e65f03c3980e0a0c6c4309f8c26544c`，仅既有v2目录26固定码；私有Conflict/ProjectFault/Format3Fault/JobFault另按事实表定位。没有T10完整导入的错误枚举/归因/幂等receipt合同，不能从通用码/异常名补造。C1接口B仅澄清这些当前边界，不创建迁移API。

本回件仅现有固定纯材料和源码事实，不写新规范、不改受审源、不运行产品/测试/SQL/DB/native；不包含本轮M/Z意见，不向T10发消息，由根转交。物理位置/准入、凭据排除、包发布与全部验收门仍按原owner负责。
