# MiniMax fresh R04 七项意见独立处置核验

结论：01的仓库状态记录缺口可采，交ROOT唯一维护；02“锁文件不记hash”是误报，压缩方式推断亦需纠正；03只采4299／4300应用边界回归缺口；04保留standalone EOF OPEN，不外推当前UI；05引用后置catch推导definitions受控的链条不成立；06是校验层次说明，已有双端内容ID测试，不作为当前漏洞；07为低优先维护建议，不直接改导出入口。全部保留作者非阻断等级，由ROOT逐项接受／延期／纠正，不改变MiniMax原Conditional Pass或代行指定双审。

原稿全文已读：`minimax-report-original-final.md`，646行／78500B，SHA256 `a893ab0a1d8782fe5c03d0944963f2eab17abb222f792dfa39bc24d6578f6a7f`，本审复算一致。源码均通过Git对象 `cb8c9b7a5d780544b2910901ec9141236905d65c` 只读取得。除静态文本、JSON／TOML、Git对象和标准库ZIP元数据读取外，未运行任何产品、测试、新探针、GUI、安装、PS、SQL或PRAGMA；未改源码、模型原稿或既有证据，未向外审传递结论。唯一写入为本报告。

## T02-R04-01：可采仓库内记录缺口，非阻断，ROOT负责

固定SHA的 `docs/m0-checklist.md`35行没有FR-200／201条目；`git ls-tree`下T02只有既有独审文件，没有对应status.md。可采“仓库内指定状态入口未反映本候选”的事实，不能扩为总控完全没有任何外部状态或证据记录，也不能把候选功能实现写成已合并可用。

责任归ROOT维护中央唯一状态来源。由ROOT决定在其正式收口流程中补状态／引用与边界；本T02不另建status或改m0-checklist来遮盖中央记录，不将6GUI成功充当mergedUsableFRs增长。原2/17与合并门禁保留。本审不写任何仓库状态文件。

## T02-R04-02：不采纳无hash缺陷与删除建议；ZIP事实需纠正

原稿只引用 `uv.lock:73` 的metadata.requires-dist路径，遗漏正式 `[[package]]`：

- `uv.lock:250–259`明确有rdflib版本／source.path，**第258行**为 `wheels = [{ filename=…, hash="sha256:99fab7bdd9148267ac0fcbd49363fc10d9a1edd47a4744726c14a7d14fc51edf", size=2379774 }]`。
- 因而“path依赖不记sha256”“锁文件不约束内容hash”“无任何机制报警”不是该固定候选的事实。不能仅从metadata第73行推导冻结安装／CI必然接受任意同名替换。本审没有做替换或安装实验，不另声称uv运行时具体行为已由本审实测。
- `PROVENANCE.json`有fr201.3 artifact与上游成员哈希；`scripts/repack-rdflib-input-types.py:19–22,94–120`显式核上游wheel、patch、上游源与patched源SHA，且102–118核RECORD。它不是“无自动校验点”的纯文本描述。本审只阅读，未运行repack。

标准库ZipInfo元数据实读如下（每包142成员）：

| wheel | compress_type | 总uncompressed bytes | 总compressed bytes |
|---|---:|---:|---:|
| fr201.1 | 0（ZIP_STORED） | 2358909 | 2358909 |
| fr201.2 | 0（ZIP_STORED） | 2359468 | 2359468 |
| fr201.3 | 0（ZIP_STORED） | 2360506 | 2360506 |
| upstream 7.6.0 | 8（ZIP_DEFLATED） | 2358325 | 596328 |

`01-01-1980`是时间戳，不是压缩方法列。上游压缩、本地确定性STORED格式才解释体积差；原稿§5.5“上游亦STORED”与§9该推断应纠正。

旧.1／.2不是当前依赖pin，但属原审计来源与历史对照；upstream wheel又是PROVENANCE指向的真实来源／repack输入。**不采纳本轮直接删除三者的建议**，不把不在当前运行依赖表中的审计材料等同死代码。若后续确需迁移证据存储，由供应维护者与ROOT保全字节、哈希、来源及重建路径后单独处理，当前不得删除。本项不形成新的供应链阻断。

## T02-R04-03：部分采纳应用回归完善，非阻断，T01负责

静态检索固定SHA的engine tests／unit／e2e未见4299／4300字面边界测试；`test_mainline_language_input_rejection.py:31–47`明确覆盖4301位manual／edit，另有独立stdio用例。可采“应用层两侧4299／4300回归保护可再补”的建议，不把当前相同INVALID_REQUEST码本身判为需求违反。

原稿“第40行超长分类目前只有供应方库外证据”过强：4301已有仓库内owned host／stdio定义及本候选已有GUI拒绝证据，不能抹去；4299／4300机制边界是不同的证据范围。未进行修改cap／canonical规则的mutation实验，不能保证式宣称“未来改动没有任何测试会失败”。裸整数的canonical拒绝与解析位数拒绝应分别说明；合法显式datatype也仍须满足完整canonical与预算规则，不能泛称任意带integer后缀即接受。

由T01在后续回归工作中按需固定两侧机制与未知HOLD对照，不在本轮改源或追加运行，不把非阻断建议变成新功能／新错误码要求。

## T02-R04-04：保留standalone EOF OPEN；不采纳泛捕IndexError方案

原稿已区分文档级恰EOF与 `rdf_snapshot.term()` 自行补 `" ."` 的单词项路径（源码第38行）。可采此前披露的standalone EOF残余与非穷尽限制；本审不重新运行该反例，也不把它当作已证的当前manual／definitions／UI入口反例。

未来直接文档解析接线前，可由T03／T01针对已定位抛点做专用输入异常／准确语法预检。原建议(b)“所有rdflib入口把裸IndexError归一受控”不可直接采纳：裸IndexError也可能是未知内部故障，不得仅凭类型一概吞掉既有未知parser／N3／Store／坏快照HOLD保护。原D8第40行和本稿H-1已经明确该保护意图；这不是尚待决定的新政策。保留当前OPEN／非阻断，未来接线另行验收。

## T02-R04-05：部分事实可采，但definitions受控的概括因果不成立

已知事实：`rdf_snapshot.py:44–45`把非已知解析异常转为普通ValueError；manual／edits caller守卫 `domain_changesets.py:459–465`只捕TermInputError，未知异常仍按既有规则保留HOLD。这个区分是有意保护，不应通过把未知解析失败改为普通用户错来“收敛”。

原稿对definitions出口援引第474–477行的catch，但该catch**只包 `supported(store, preview)`**。真实先后顺序：

1. `entity_metadata.merge_plan:108–134`主要处理允许字段／metadata继承，没有对任意triples对象做term词法预检；其调用在domain_changesets第467行。
2. domain_changesets第471行先调用 `transactions.preview`，此处第472行**仅捕MetadataError**。
3. `project/transactions.py:146–178`在162调用真实 `self.store.commit(...)`，只在166捕其专用 `_PreviewRollback`。
4. `storage.py:715–726`在定义写入前调用 `_definition(definition["value"])`，`1125–1129`对triples做iri／term／canonical校验。其TermInputError（ValueError子类）或非canonical ValueError可在这一早期阶段抛出，**尚未走到supported的后置catch**。

因此不能从后置catch推出“definitions坏词法已受控INVALID_REQUEST”或宣布旧wire HOLD已修；本审未做新运行复现，维持原D8第24行OPEN／非阻断延期，不新增范围。某些较晚的supported错误确可受控，这是局部阶段事实，不能概括所有定义出口。原稿§4／H-3保持OPEN与§9-05的泛化说法需消歧。

处置：可接受未来在已知caller定义边界精确预检的改进方向，由T01在原始triples／Agent接线前负责；**不采纳把未知Term解析失败在manual出口一律映射受控的建议**。不更改当前未知保护，不用新异常名字包装后就降低故障语义。

## T02-R04-06：不作为当前漏洞；校验层次事实与文档建议分开

schema中 `changeSetFact.id`只约束hash形状是事实；普通JSON Schema不能直接表达SPO的SHA-256关系。但引擎 `storage._fact:484–495`权威校验canonical对象与内容摘要，当前 `newManualFactPlan:53–81`也正确从原始SPO的JSON UTF-8生成WebCrypto SHA-256；edits按ADR保留初始ID，不应重算。

原稿“缺少双端可测不变量”的建议已有对应仓库测试：`tests/unit/t02-manual-fact-id.test.ts:53–75`调用真实Python Store._fact／digest检查；81–86核全部golden records，90–99核TS产生计划与golden一致，123–133再次把TS结果送真实Store接受并保留ID。这是既有测试定义与完整check覆盖的证据，不是本审新运行。

架构本来禁止绕过唯一Store.commit直接SQL写入；假设将来另建绕过路径，不构成当前接口漏洞证明。可选的derived-from说明只属契约文档可读性，交共享维护者评估，非当前阻断；不得把注解当作新的权威校验或要求edit重算ID。

## T02-R04-07：可采聚合入口事实；仅低优先维护建议

`packages/contracts/package.json:6–9`把 `./v2`指向design-v2.ts；该桶文件2–4行确实转出v2／dependencies-v2／states-v2，且首行明确其为共享v2运行时与校验入口。原稿也承认当前导入正常、无同名冲突。可记录命名与职责边界建议，不作为已证功能缺陷。

不直接采纳把既有 `./v2`改指单一文件的动作：这可能移除当前消费者已依赖的聚合导出，需共享契约唯一负责人（T01／ROOT分配）盘点兼容性后决定。对未来同名export*的“由解析顺序决定实际生效”不作未验证的运行结论，本审没有为该设想执行新编译或运行。维持低／非阻断延期，当前不改入口。

## 原判定与门禁保留

MiniMax七项均由原稿声明非阻断；本审仅形成事实处置建议，不改模型结论，不把作者未亲跑GUI／包的披露误解为已存在同版验收证据无效，也不以本审替代任何实际验收。Conditional Pass的逐项处置／ROOT显式接受条件由ROOT登记。旧首败、容量与恢复、未知保护及其它独立HOLD照原件保留，是否满足同版双审与后续push／PR／CI／merge门禁仍由ROOT核验。
