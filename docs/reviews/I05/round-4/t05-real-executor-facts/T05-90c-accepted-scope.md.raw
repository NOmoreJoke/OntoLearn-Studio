# T05：I05/T01联合接受、实现缺口与Q6可审定范围 r1

**最新联合设计状态，非产品采用或运行通过。** 读取范围仅I05固定设计报告/inputs及已收到T01 r2；不读或消费实现。I05新技术接受不能倒填为旧C3或当前C4已实现；C4正在验证、尚未冻结或通过指定双审。原Goal仍blocked，四语义路径future未生效。

| 来源        | 固定身份／内容边界                                                                                                                                                                                                                                                                |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| I05新回复   | `96fb5977f3e0533dfc7f735a3727084824a3cb74:docs/reviews/I05/t05-ta-response-157963e/owner-response.md`，15368B，SHA `8bf9e6086da486757b2016ef95c7be3c68bce6622ce3ea5b79e4b54933a942c2`；同目录inputs.json全文读回/核原T05固定157输入。未读其中链接的候选、反例、独立草稿或其他实现 |
| T01包装回复 | 固定b35cb4e `t05-context-wrapper-response-r2.md`，3906B，SHA `3d300cf1070adf54f97fec45d060273f78d0e29fba9bbef502403466084b8d09`；此前全文读回，原f51接受保留，不据此采用T01未批准实现                                                                                             |
| 审定对象    | [算子/消费者矩阵](comparison-operator-consumer-matrix-r1.md)、[Q6决定单](q6-policy-decision-request-r1.md)；本表只整理答复，不替Q6记录决定。来源及逐项收据见`docs/reviews/T05/i05-ta-response-receipt.json`                                                                       |

## 1. 已接受的技术选择与仍未完成项

| 项         | I05技术接受                                                                                                                              | T01责任／剩余实现证据                                                                                                                   | Q6状态                                               |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| TA-S       | RDF1.1 simple无lang与同lexical xsd:string同抽象term，非可选合域；新规则S六算子按解码Unicode码点字典序，不trim/casefold/NFC/locale/数值化 | 空串/前缀/U+10000对U+E000/组合与预组字符、转义同文的独立oracles与新规则运行未完成；当前string修复与未来比较实现分开                     | 技术已答；算子产品采用待定，抽象term身份不是可选合域 |
| TA-L       | well-formed标签先验、内部小写表示/source原拼写分层；同合法标签六算子按文本码点，合法异标签含en/en-US六操作E3、无回退                     | 完整BCP47校验、canonical内部/source真实载体/授权/往返待实现；现en/EN有限控制不证明全域或source全保存。非法标签先输入/词法错误，非E3跨域 | 待产品采用；不借value比较证明join/图集合已正确       |
| TA-I/B     | IRI仅eq/ne、完整身份无URL规范化/解引用；boolean仅eq/ne，true/1及false/0值等、term保留；同值le/ge也E3，B不入N                             | 全正反/词法/跨B-N oracles及新运行证据待；不宣称SPARQL没有boolean顺序                                                                    | 技术已答，待Q6                                       |
| TA-X       | 九域有序表、N六型全部有序混型；非N跨域/合法异语言标签六操作X6，ne也失败；定义常量预检、false后全comparison校验与全heads原子保持          | 486分类槽/216数值细化槽非通过数；L标签参数族及完整错误/定位/生命周期未真跑。T01保真实context/原子持久边界，不造第二comparator           | 技术已答，具体profile/版本及Q6采用待定               |
| D3/D4      | 原ffc462b技术接受继续有效：精确词法直接目标精度舍入、实际表示值精确混型；独立calendar/完整秒/offset四域/date起点及跨域失败               | 新执行/入口→持久载荷→selected/源包/精度日历全矩阵/独立oracles/预算阈值及新身份均未完成，不夹带进string修复                              | Q-NUM/CAL/REC未采用，REC/勘误正式pin未完成           |
| TA-C/K/D/R | 接受每个消费者按自己合同正确，K集合/in term、D精确datatype及适用词法、R自身SPARQL非true含type-error为违规；不统一D3/D4                   | T01已接受包装、真实Job/result/快照依赖/全hash/分页与授权，三字段仅分区。I05有限入口/未支持及责任见下表；具体新增异常对表/golden仍缺     | 独立目标已技术接受，不是整表实现合同完成或Q-CONS采用 |

## 2. C格：有限事实、未支持／未证与补齐责任

以下“当前”是**I05固定设计报告所述候选事实**，不是本线读实现/复现，也不是所有旧候选或当前C4已经通过。图10 datatype白名单及原位置/离线/预算门的存在，不证明每格正确或承诺通用datatype；未逐一展开的白名单不凭猜测补齐。

| C格／消费者                       | 已答目标／当前有限边界                                                                                                                                                      | 未实现、未支持或未证项／owner责任                                                                                                                             |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 新reason/selected G+N             | 保RDF位置/外联/资源/定义门；未来同一执行器/原选定结果验证共享唯一validator，不全局关ill_typed或以值eq改term                                                                 | 新operand/heads/原子发布未实现；宿主先挡合法值、source/selected认证待补。四路径未来责任须root生效，I05/T05届时协作；T01认证真实producer/版本/hash             |
| float/double query term/匹配/投影 | 保lexical/datatype，不量化改写或用D3值eq折叠                                                                                                                                | 完整声明精度边界/常量/变量/绑定构造/投影保真未证，I05补原有限入口和oracle；不先宣称全支持或全部不可用                                                         |
| float/double query值/FILTER       | 原query数值提升/error，不变D3精确有理比较；图门不覆盖所有常量/中间值                                                                                                        | I05按query合同核精度/有损路径，真正不支持格给真实入口/分类及缺口；不同于D3不构成能力错误，不扩大完整SPARQL                                                    |
| float/double SHACL R              | 正常false/type-error给真实value违规，不进adapter、不套E3                                                                                                                    | 全精度/边界未证；I05补shape参数/data双侧、定位有损路径后修复或精确受限，不能以库名宣称全符合                                                                  |
| date/dateTime query term          | 原lexical/offset/精度保真，与日期运算支持分开                                                                                                                               | 年零/负年/大年份/高精度受当前图门/宿主范围影响；I05补可达子集/合法但未支持识别/保真，不把宿主不能表示当标准非法                                               |
| date/dateTime query值/FILTER      | 原有限query日期合同，不继承D4起点或跨TZ全拒绝，不补机器时区                                                                                                                 | 完整年份/秒/offset/中间值未证；I05另补，不在string修复中改policy，不以截断后的值成功                                                                          |
| date/dateTime SHACL K/D/R         | K抽象term集合，D精确datatype及该consumer词法，R自己的关系；**当前min/max shape参数只integer/int/decimal/float/double且not ill_typed，不是任意Literal，日期shape边界未支持** | 若要日期边界，须单列扩展/规范/shape-data双侧证据/精确授权。I05补未支持格，T01承载真实失败/定位；不把数值模板说成已有完整日期范围，不以拒绝关闭原FR/新合同缺口 |
| 非有限/溢出 graph/query/K/D/R     | 新规则E6只属于其policy；图入口先拒时consumer未运行，query中间值不能据此全算已验；能进入validator的合法值按组件合同                                                          | 全路径矩阵未证；I05补入口先拒/操作支持/真实错误/缺口。不能把合法INF当D词法违规、以规则E6自动终止R或伪报K/D/R空成功                                            |
| 未知datatype/lexical/shape/预算   | 未知IRI不天然非法；当前10类型外不承诺通用datatype；**sh:datatype rdf:langString不在当前shape白名单，明确未支持**                                                            | 不由该shape缺口推断所有语言数据均拒绝/均正确。I05后续精确扩展/测试，公共码/schema/载体归T01；shape参数限制与已入validator的数据违规分开，资源仍走真实原边界   |

普通S/L/I/B和整数/decimal仍各按query、K、D、R自身合同。IRI可计数/in，面对已允datatype约束应为违规；boolean新规则无顺序不覆盖query/SHACL。string已核P1另线修复，既不能泛称所有格错误，也不能记为当前已修复。FR504五模板/双范围/真实定位及修复后复验保留，安全拒绝不登记完整首版完成。

## 3. 已知错误上下文与仍须成对冻结的边界

| 入口／情形                                             | I05已给的准确上下文／映射或责任                                                                                                                                                                                                               | 仍缺内容／不能推断                                                                                                              |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| 初始facts/ontology的_terms（即使后续query/validation） | `Producer.REASON / Stage.SYNTAX / Origin.VERIFIED_USER_INPUT`，不是未来规则R/R/U                                                                                                                                                              | 这是I05已核有限入口事实；新consumer或shape/query错误不能统一贴rule                                                              |
| 同一初始图term入口                                     | UNSUPPORTED_LITERAL_DATATYPE→UNSUPPORTED_CONSTRUCT `{construct:datatype}`；UNSUPPORTED_NONFINITE_LITERAL→UNSUPPORTED_CONSTRUCT `{construct:literalValue}`；INVALID_LITERAL_LEXICAL→SEMANTIC_INPUT_INVALID `{field:syntax}`，均在上一行context | 不能用此把合法但宿主不能表示的值说成坏词法；不把字符串任务成功发布错误语义掩成能力DTO；未复用到其他未核组合                     |
| 普通SHACL违规                                          | 不进入adapter；产生正常validation结果，T01包装真实result与分页/hash/授权                                                                                                                                                                      | 不是整Job E3/空成功；不能仅凭code目录存在发新路由                                                                               |
| shape白名单/shape结构/query执行/预算拒绝               | 各走真实reason/context；I05 adapter owner和caller逐新增拒绝点给token×producer×stage×origin正反表，涉及权威Store/schema交T01                                                                                                                   | 此报告未列出的确切token/context和完整success/failure golden仍待，不猜通用异常/params、不先写caller再等映射；M3/M8a/M9未因此接线 |
| M12、内部损坏/unknown                                  | 当前跨实现新消费仍IDENTITY_CONFLICT；UNKNOWN/未接受组合/可信损坏Internal，旧resource/network合法例外保持                                                                                                                                      | 未来UNSUPPORTED语义适配和诊断资源未实施未批准，三字段不证明consumer同义                                                         |

每个C格的三字段新producer身份、实际入口/输入definition source/输出、有限预算和完整成功validation／失败诊断golden仍需补成**可实施的精确组合**；T01已接受按精确context接真实Job/result/快照/依赖/定义/payload/rows hash与授权，不能代I05裁值政策或猜异常。I06实际main/UI仍其owner。

## 4. source与历史：接受要求，不假称载体已有

source技术接受是“原文与抽象term分层且可追溯”，**不证明S1 canonical事实保存每个导入前写法**。规则/shape/query原定义文本可作受控来源；其他原文缺口须实际source owner/T01明确授权、大小/保留/生命周期和公共投影，若需新字段/DTO/方法先共同批准。本线不私加、反向推断原文、改数据库事实ID/raw resource或规范化旧payload重签历史；载体未有则保持未完成，不删source要求。现有错误定位也仍是受限诊断提案，不能夹带operand原值/path/stack。

旧finite5历史按原身份/schema/授权/availability可读且原字节不改，新current或historical selected继续全三字段拒旧；新同版source/producer/hash认证另须真实验证。本表技术答复不代替string新候选通过、批准依赖或未来四路径交接。

## 5. Q6现在可审定的范围与明确待补项

| Q6项          | 技术答复进展／可审定决定                                                                                  | 不能据此登记完成的内容                                                                                                                 |
| ------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Q-SLIBX       | 新S/L/I-B/X已I05技术接受，可逐项采用或改写具体operator/有序域格；同term身份本非可选                       | Q6尚未决定；完整标签/source/新比较实现与真实oracles未完成                                                                              |
| Q-NUM/CAL/REC | D3/D4原接受保留，可审定精确profile、固定REC正文与勘误集、新语义身份方案                                   | 未正式pin/实现/全精度日期预算验证；不扩大当前SHACL范围或夹带string修复                                                                 |
| Q-CONS        | K/D/R独立目标获I05与T01接受；可审定目标及**当前数值shape边界、langString shape明确未支持**的处置/补齐范围 | 每格新入口/异常对表/完整golden/可达子集不齐，不能整表当实施完成。日期shape与rdf:langString扩展需单列，不静默降低原FR或把安全拒绝当完成 |
| Q-LIFE        | T01已接受真实context/包装/授权/分页/hash及原子/历史职责，I05保持全comparison/head原子和真实定位要求       | D8阈值、新错误route/公共source或诊断载体、I06真实呈现及完整运行门仍缺；Q6不释放文件责任或公共协议                                      |

全部Q项仍未采用，D3/D4原接受不清零，新技术答复也不等于旧候选已支持。未来四语义文件仍未生效；I05 query/turtle/adapter/samples/旧tests维持原owner/代改，T01 Store/canonical/worker，T03锁/build，I06桌面。C4 string修复正在验证、未冻结未指定双审通过，仅记录总控通知；T05不消费代码、不复现/造新比较、不重测，原完整Goal保持blocked。
