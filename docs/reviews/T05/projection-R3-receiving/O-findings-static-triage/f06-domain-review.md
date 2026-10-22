# F06 RDFTerm / raw occurrence 静态领域核查

结论：原 F06 的 **288 处 / 25 条 observation / 五键形状**计数可以复现，但将其归因于 `packages/contracts/v2/schema.json` 的 RDFTerm `oneOf` 不成立。该公共 schema 没有 RDFTerm 定义；实际被比较的是 O 私有说明 schema 的 `normalization.RDFTerm.oneOfExactKeys`。288 项全部是明确保留输入写法与来源的 `expected.businessMath.rawTermSourceOccurrences`，不属于规范 RDF 身份对象。不能为此扩展公共 schema，或把 raw records 强制改成规范 RDFTerm。O 自身仍有可收敛的声明/约束缺口：私有 schema 没有独立列出 raw occurrence 的 exact keys、字段类型与适用路径，现有校验也没有将该域逐项绑定回 sealed input。这里没有证明 288 项 expected 内容错误，也没有证明实际消费者发生拒绝或漏检。

## 1. 核查范围与固定身份

- source O：`77852d27a3c4e84867a42f243e0f4e0f32b8df67`。
- 过程 ref：`86df64a2c707355ed177d536ef5975a1986c0f0b`。
- 只在主工作树 `.worktrees/T05-source-package-oracle` 读取 AGENTS、固定 ref 的 Git blob、相关源码、sealed inputs 与原规范；未读取冻结审查树。当前 HEAD 为 `c00e10be2a9a778bd73d814ff9898f5dc6d5b617`，没有将当前 HEAD 冒充 source O。
- 下表文件均逐字节比较当前文件、`git show <source O>:<path>` 与 `git show <过程 ref>:<path>`，三者全部相同。行号据这些相同字节。
- 本次只用 Git 与 Python 标准库作 JSON 解析、对象遍历、相等性与 SHA-256；没有 import/执行 builder 函数，没有运行产品、测试、模型、网络、GUI、Goal 或数据库。没有格式检查或运行通过声明。

| 文件 | bytes | SHA-256 |
| --- | ---: | --- |
| `packages/contracts/v2/schema.json` | 122889 | `9215266523f539c81282bbc96ca88de52b79c99ef39f7696b3a49c58fa7a2b79` |
| `tests/fixtures/quality/i05-source-package-oracle/schema.json` | 9106 | `74889cca94e90d62b2a456087946cfdd35f7a716039729091892a0bcda13f7c5` |
| `tests/fixtures/quality/i05-source-package-oracle/oracle.json` | 5920695 | `7ae1c1311f71bfbcc76d5ab9592eebb66f39410ef9e0871965951de35dc77023` |
| `scripts/build-i05-source-package-oracle.py` | 89455 | `024b352964880f57154ee2f49b31fce9dea368e29d5cd3112ffbad7497b06610` |
| `scripts/test-i05-source-package-oracle.py` | 32188 | `601ca5b48b2cc1422ca7a956907b3da1b63b8f450a414ad5fa1dc47261cabb4d` |
| `docs/reviews/T05/source-package-oracle/inputs/i05-source-package-parity-inputs.json` | 8205267 | `47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa` |
| `docs/reviews/T05/source-package-oracle/guidance/contract.md` | 60953 | `d2cdc2e6017ad0257f30611d2928a60a116f4dc389cacdfc977c17efe13e2a23` |
| `docs/reviews/T05/source-package-oracle/guidance/directsteps-contract.md` | 34958 | `c947430801e6b3cca113c15a856704c3d5bed418efa9083d67819830a6961fba` |
| `docs/reviews/T05/source-package-oracle/guidance/q6-profile.md` | 16428 | `9259f4ac6622857182570509378afb6c96ab5c4dc19d2e887db559c27a282427` |
| `docs/reviews/T05/source-package-oracle/guidance/q6-mechanism.md` | 26782 | `8008e906c7b20dbd9c9ba2d0a1bce0661ec32336f78d477831103cbc9bc27424` |

原意见原件为 `docs/reviews/T05/projection-R3-receiving/O-launch-dispatch/normal-recovery-progress/minimax-final-v2-original.md`，44941 bytes，SHA-256 `9921ffe20f68b1bbf5c7938fa7d45c9b0059cd9c8ed5b0a4afcb5a6e23852df7`。它是本次保存的外审原件，不宣称存在于上述固定 source blob。

## 2. 原意见与限定判定

原件 `minimax-final-v2-original.md:306-310` 称公共 `schema.json` 的 RDFTerm oneOf 未覆盖 25 条 observation 的 288 处五键 raw occurrence，并建议按语料补齐 RDFTerm 分支及交叉校验。

| 子主张 | 判定 | 直接依据及边界 |
| --- | --- | --- |
| 公共 schema 声明了这里所述 RDFTerm 分支 | **不成立** | `packages/contracts/v2/schema.json:2-4` 声明 JSON Schema 2020-12 / `urn:ontolearn:contracts:2`；`:4399-4410` 的 envelope 是 request/response/notification 联合，`:4751` 为根引用。标准库解析遍历其全部 66 个 `$defs`，无 RDFTerm/term 定义；全文也无 lexical/datatype/language 等对应字段。 |
| 存在 288 个不符合私有 RDFTerm 三组 exact keys 的 term-like 对象 | **确证，须限制域** | 实际声明在 `tests/fixtures/quality/i05-source-package-oracle/schema.json:168-190`，不是公共 schema。遍历所有 observation 中 kind 为 iri/literal/blank 的对象，三种允许键组之外的 288 项均具有 `{kind, lexical_form, datatype_iri, language_raw, source}`。其余规范身份对象有 17236 个 iri 二键对象及 2166 个 literal 四键对象，未见额外键组。 |
| 288 项由错误的规范 RDFTerm 序列化导致 | **不成立于现有证据** | 所有 288 项仅位于 `/observations/185..209/expected/businessMath/rawTermSourceOccurrences/*/*`；其父字段有明确 raw 语义，builder 源码与原规范要求保留原记录。所有 25 个 raw 数组与各自 sealed `datasets[datasetId].records` 完整相等。没有 source 或尾项被规范化掉的静态证据。 |
| O 的 schema/验证无需改进 | **不作此结论；声明缺口确证** | 私有 schema 只列 RDFTerm 三组键，未独立列 raw occurrence 键组、type/path applicability；`scope` 是 semantic model，并非可直接运行的 JSON Schema。builder 的 `FIELD_POLICIES` 同样未把两域显式列开。`validate_oracle` 的相关遍历未核 raw records 全字段对 sealed input 的相等性。 |
| 因这 288 项导致实际 schema 拒绝或无效 oracle-match | **需证** | 本次禁止执行；O 自称无 frozen JSONL adapter。未见运行拒绝记录或消费者把 raw 路径当规范 RDFTerm 的证据，不能把计数写成 288 个运行失败或放行。 |

## 3. 两个 term 域的真实合同

`guidance/q6-profile.md:15-25` 明确机制输入是私有已解码 `TermInput`，kind 只有 iri/literal，字段包含 lexical_form、datatype_iri、language_raw 与可空 source；`term_key` 则使用抽象 datatype 与内部小写语言标签。simple/string 可归为同一身份，integer 01/1 仍是不同 term；原 source/actor 不因此获得认证。`guidance/q6-mechanism.md:11-12` 也将 TermInput/SourceRecord 定为私有类型而非公开 DTO。

`guidance/directsteps-contract.md:22` 要求真实 occurrence/source 保留，缺 span 时不能编造；`:72-76` 区分用于 identity linkage 的代表形式与必须原样保留的 input/termSources raw、None、language_raw、source 和 occurrence 顺序。`guidance/contract.md:188` 还禁止一般性删变化字段或归一语义 input/source 词法。因此 raw 五键对象是需要被保真验证的独立记录域，不是可无损塞进规范 RDFTerm 联合的第四个身份分支。

builder 中两条路径清楚分开：

- `scripts/build-i05-source-package-oracle.py:203-210` 产生规范 `iri={kind,value}` 与 `literal={kind,lexical,datatype,language}`；`:692-695` 的 `record_term` 将私有记录转换到该身份表示。
- `:817-825` 的 records 分支对每项调用 record_term 生成图，同时单独持有输入 records；`:849-852` 把原 records 放进 `rawTermSourceOccurrences`，并明说 raw lexical/datatype/language/source 与 None/空字符串必须保留。
- `:945-955` 的 `FIELD_POLICIES.RDFTerm.oneOfExactKeys` 列的是规范表示；`:1219-1226` 将其写入 O 私有 schema。后者 `schema.json:166` 是 `T05-oracle-schema/1`，`:168-190` 采用自定义 `oneOfExactKeys`，不是公共 JSON Schema 的 `oneOf` 验证分支。
- `scripts/test-i05-source-package-oracle.py:228-232` 仅核 raw-aliases 的六身份、24 原 occurrence 与零 directSteps；`:329-335` 的“schema”测试只核 native 7/15/11 字段，不能证明 raw 类型与完整原值合同已验证。`scripts/build-i05-source-package-oracle.py:1231-1263` 的 validate_oracle 会核 inventory、binding、状态、allocation 与 SHACL，但没有 raw occurrence 的逐项专用核验；`:1266-1281` 的 exact-model helper 是通用精确比较，本身不是此路径已接入的证明。

例如 `oracle.json:142999-143021` 是 dag/type 的 raw source 表，首项五键 IRI 为 `lexical_form=urn:x` 且三个可空元数据保持 null。输入 asset 为单行 JSON，来源定位应使用 `inputs/i05-source-package-parity-inputs.json:1#/datasets/dag~1type/records/0/0`；完整 raw-aliases 例用 `:1#/datasets/fullview~1raw-aliases/records`。其中 source 的 null/空字符串、simple/显式 xsd:string、EN-us/en-US 原写法确实不同；把这类输入统一成规范 RDFTerm 会丢失本应核验的信息。

## 4. 288 项分布与静态复核方法

标准库解析现存 oracle/schema/asset，不调用 builder。对每个 observation 递归记录 kind 为 iri/literal/blank 的对象及完整 JSON pointer；比较键集合只用于复现原计数，再限定到 raw 路径。最后直接比较 raw 数组与同 entry.datasetId 对应 sealed dataset.records，25/25 全量相等。这个比较以固定输入为依据，不把 product actual 或 builder 算法结果作为 expected。

| observation | raw terms |
| --- | ---: |
| dag/type | 6 |
| dag/domain-depth2 | 9 |
| dag/range | 6 |
| dag/subclass | 6 |
| dag/first-witness | 12 |
| dag/cross-rule-witness | 12 |
| dag/range-literal | 6 |
| fullview/raw-aliases | 24 |
| dag/raw-aliases | 24 |
| fullview/two-head-occurrences | 12 |
| dag/two-head-occurrences | 12 |
| restore/fullview/payload-unknown-key | 12 |
| restore/fullview/tail-source-tamper | 12 |
| restore/fullview/tail-definition-tamper | 12 |
| restore/fullview/tail-limits-tamper | 12 |
| restore/fullview/tail-child-tamper | 12 |
| restore/explanation/payload-unknown-key | 12 |
| restore/explanation/tail-source-tamper | 12 |
| restore/explanation/tail-definition-tamper | 12 |
| restore/explanation/tail-limits-tamper | 12 |
| restore/explanation/tail-child-tamper | 12 |
| restore/explanation/dag-depth-plus-one | 9 |
| restore/explanation/dag-last-premise-forward | 9 |
| restore/explanation/leaf-rename-all | 9 |
| restore/explanation/head-occurrence-1023-15 | 12 |
| 合计 | 288 |

## 5. 最小修复建议与唯一 owner

唯一修复 owner：**T05 O oracle 维护者**。本结论不将修改公共 contracts/schema 的责任派给其他线。当前仅形成 triage，不实施修复；新候选及指定复审仍由根协调。

1. 在 O builder 的 FIELD_POLICIES 及其生成私有 schema 中给规范 RDFTerm 与 RawTermSourceOccurrence 分别声明 exact keys、字段类型及路径。raw 记录限定到 businessMath.rawTermSourceOccurrences 与已批准的真实输入合同；source 的原 null/空值与顺序按 sealed input 保留。不往规范 RDFTerm 身份分支盲加五键对象，更不修改公共 schema。
2. 在 O 验证逻辑对有 raw records 的 entry 增加完整逐项与 sealed input 的对应关系检查，包含行数、每行三项、exact keys/type、末项、source、None/空字符串、language_raw 与 multiplicity。规范 RDFTerm 形状检查限定在实际图/typed term 路径，不能用“遇 kind 就套同一联合”的全树规则。Turtle 的 unavailable/null 按当前合同保留。
3. 用预先列明的独立小例及 mutation 验证 raw 尾项、source None/空、language 原大小写、额外/遗漏键和重排不能漏检；规范身份允许的 simple/string、语言 identity 关系不能改写 raw。预期来自固定规范和 sealed input，不执行实际产品算法再生成 golden。未来消费者接线时另证明其按域分派，不以静态计数充当消费者运行证据。

私有 schema/builder/test 的修订会改变 O 受审字节，须按新固定候选处理；本次没有改写原报告、oracle、公共 schema 或共享矩阵。F06 的最终归类建议为“公共域归因不成立；O 私有域声明和专用约束待收敛；实际消费者后果需证”，不能据此宣告整包通过，也不能将 288 计为公共协议缺口。
