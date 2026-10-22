# 有限材料 entity metadata helper

本窗只交付两个新增 Python 文件。它检查调用方明确给定的不可变材料，不读取项目、数据库或文件，不认证 home、profile、出处或全项目覆盖，也不产生可编辑实体、proof、公共 canonical 或迁移能力。无旧产品路径修改，AGENTS 精确携带且不提交。

## 私有接口

`check_metadata_materials(scope, materials, *, bounds=DEFAULT_BOUNDS)` 接受本模块 frozen/slots 数据类与精确 tuple，返回 `MetadataCheck`；结构、冲突或局部输入界错误抛 `MetadataFault(reason, location)`。错误不夹带输入正文。它保留 scope、materials 及内部值的原对象，不转换、排序或归一化。这里是进程内叶子表示，不是第三份公共 schema。

`MetadataScope(project, homes)` 明示有限检查范围。每个 `MetadataHome` 明示 project、entity_iri、entity_kind、home_id；四种 kind 精确为 class、objectProperty、dataProperty、individual。相同 IRI 在该范围仅可有一个声明 home，声明与材料必须一一匹配；同一 home 可以包含不同实体。此处匹配只是检查输入自洽，不能证明真实 home。

`MetadataFields` 精确包含 identifier、labels、definitions、synonyms、examples。缺失使用 None；已知空集合使用空 tuple。identifier 缺失只报告 gap，绝不从 IRI、id、label 或其他信息派生；空 identifier 拒绝。已给定的 identifier 在该 project 的声明范围内跨四类型精确唯一，不 trim、不 casefold、不合并大小写或 NFC。未声明的实体不在结论内。

四类文本集合保存 `MetadataText(text, language=None, datatype=None)`，保留原文本、语言拼写、顺序和重复项。language/datatype 的非空字符串与互斥仅是词法结构检查，不认证 BCP47、IRI、RDF datatype 或 literal 语义。文本允许 NUL、控制字符和 non-BMP，拒绝 Unicode surrogate；不提供 domain/range 值门。

profile 必须为精确整数 1 或 2。profile1 只接受未解释 opaque bytes 与 fields=None，即使同名 JSON 字段看似齐全也不会升格为 profile2。profile2 接受结构化 fields，拒绝 opaque 混入。结果使用 legacy-opaque、missing-metadata 或 missing-fields gap 表达未解释/缺失材料；这些 gap 不是 L1 来源认证。

## 局部有限性

本模块私有默认上界为 256 homes、每字段 128 cells、每字符串 65536 UTF-8 bytes、逻辑输入总量 2097152 bytes。调用方只可收紧为非负精确整数，不可上调。它们是本叶子的实现输入限制，不是获批业务限制、CostSession、S1、公共协议预算或全链/操作系统内存上界。没有要求其他供方接受此表示或这些数值。

计数按给定字符串的每次逻辑出现计 UTF-8 bytes，包含 scope 的 project、声明 home、材料 home、identifier、text/language/datatype，以及 opaque bytes；共享对象重复出现仍重复计费。循环逐 Unicode scalar 累加，不构建完整编码副本；测试另用实际 encode 独立核算。已由调用方分配的原对象、Python 对象开销、hash 和容器开销不计入此字段，不能把它当物理资源证明。

只接受精确内建类型和精确本模块数据类，拒绝可变 list/dict、字符串子类、bool-as-int、未初始化对象与未知 kind/profile；输入容器数和字符串长度在相应遍历前核界。

## 与固定供方方案的边界

采用固定 f20 七文档与 836c convergence/intake/independent 文档的五字段、真实 identifier 不派生、显式有限冲突范围和 profile 不冒认语义。未来同 issuer 首读前 CostSession、全源 supports/proof、S1、M1/S2、唯一 canonical 与原四事务及 current/historical host 接线均由后续真实 owner 交付，本窗无这些依赖接线、读写能力或 readiness 声明。

基线没有 project 包目录；本窗只新增指定模块，不新增 **init**.py 或旧路径 import 接线。由现有父包下 namespace 子包导入，局部测试已实际导入。

## 验证范围

新增纯材料测试覆盖五字段保存、缺失/空值、profile1 opaque、四类型所有 16 组合冲突、无归一化、home/scope 不匹配、类型和 Unicode、独立 UTF-8 计数及精确/越一边界。它们不构造假 Store、认证 home、DB、模型或完整 supplier 链。首轮测试与 Ruff 失败/警告原输出和首版源码另保原件；最终局部检查及完整 npm check 的实际终态以 review 目录回执为准。独立审查由主 agent 安排，本作者不自宣独审通过。
