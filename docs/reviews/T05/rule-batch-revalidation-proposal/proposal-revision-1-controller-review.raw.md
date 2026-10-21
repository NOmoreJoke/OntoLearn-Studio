# T05 batch重验提案独立静态审查

结论：**固定c1a提案在其写明的完整输入/当前发行/独立资源前提下技术可行，未发现必须改旧20或改比较语义的算法阻断；但I05四项真实调用事实尚未到，不能据此批准实施或宣称selected预算已经闭环。** 三池与K只约束新API内的计费，不包含保存载体恢复、parse重新发行、原matches保留以及整个child的资源成本。该缺口已被提案明确列成实施前置，不能在授权时省略。

## 1. 固定输入及实读范围

- tree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-quality-reasoning`。
- 固定提交：`c1a616bbc8fc699ad11cd73cbf663c3692515e5f`。
- 提案：`docs/iterations/T05/rule-batch-revalidation-proposal.md`，24357B/SHA256 `578032f78cd8571496c5709f18c7f5c02292db89cf316a52e3d2f49c61234bea`。已全文读，与root `.private/T05-batch-revalidation-proposal-received/rule-batch-revalidation-proposal.md`逐字相等。
- 固定旧机制：`1e3e0ee1d9d5b70f1f59233d0a3c64f6d85fd2cb`。静态全文读rule_firing、rule_profile、rule_terms、rule_comparator；定点核rule_numbers的计费/限额使用。未执行或import这些模块。读取本线最新AGENTS约束，未读取其他线WIP、主线独立oracle或任何新指定外审结论。
- 提案input-bindings的20条路径均按Git读取：旧1e3与c1a逐字相同，bytes/SHA与绑定清单一致。root final-input-manifest四项与c1a blob匹配；final-input.zip内四原件与Git相等（另含manifest.json）。此处是文件归属/完整性核验，不是旧测试重新通过。

本报告仅写本独占文件；没有改功能树、owner证据、state/common或权限登记。

## 2. 完整原matches是实质调用前提，不能用true groups替代

提案§2（约51–64行）明确original_matches为当时传入evaluate的完整原有序BindingMatch，包括false matches、每条bindings原顺序、when/proof leaf occurrences与TermInput/source；definitions/catalog也保原样。其合理性直接对应旧rule_firing：

- `_one:381–458`逐项检查所有comparison，全部完成后才因false不产firing；不能在首false短路后面的错误。
- `_evaluate_bound_batch:470–523`对全部给定matches执行、逐一做重复输入检查，包括false；之后才保成功firings。生成输出时bindings已排序，保存group不是原输入的无损副本。
- `_resolve:352–362`按输入bindings线性查找并逐项付费，输入顺序不同可使work不同。输出能相同不表示执行计费序列相同。

因此不能在I05回复不保false后，仍以“true groups已足够”自动采用本提案的成功蕴含证明。可在同child保留原tuple直至读回复核，或另行批准保存/恢复载体；两者的窗口、大小和生命周期均须I05提供真实事实。长期selected若只有成功groups而无原输入，本提案当前前提不满足，不能重新跑图匹配补齐，更不能对已保存旧结果回填false输入。

一个确切的边界反例是：原输入含一条合法false及一条true，保存payload仅含true；只传该true给重验，完整输出仍可能逐字相等。API无法从payload发现调用者删过false。提案已承认这一边界，故它不是遗漏的机制鉴权漏洞；**若集成把返回True当作“原全部匹配已核”则是错误。** 必须由真实producer/不可变请求绑定证明传入的是原集合，不能靠调用者标志或新摘要替代原授权。

## 3. 三池及K静态成立的精确范围

提案§3、§4约68–103行与旧API相符，未借更大旧ProfileLimits或逐组reset绕限。

| 部分 | 静态依据 | 必须保留的条件 |
| --- | --- | --- |
| replay | 原compile_rules一次+evaluate_bound_batch一次，原顺序和数据相同；compile/evaluate同Budget，包含plan校验、所有false、去重、排序、全heads及完整输出 | 同模块固定旧算法；传入原定义/Catalog/原matches；不在此池增加恢复/预扫描/新编码 |
| saved-encoding | 原evaluate最后encode_output((PROFILE,firings,facts))的相同一次字段/occurrence遍历；合法完整保存结果的bytes及该段work与原输出段相同 | 保存值完整、顺序相同、准确记录类；不归一化/去重source、proof、head或groups |
| saved-issuance | 每保存成功comparison的left/right各check_value，对应原compare_values:32–33的两次check；合法保存值字段相同，因此编码/input/hash计费是原执行的一部分 | 当前模块实际发行且强引用仍活；不把重新parse/载体构造偷偷并入“子集”证明 |
| control | 固定入口guard；每group和每comparison唯一一次付费循环；两次完整payload、一次digest、一次profile比较在操作前付费 | exact原生类型与常数len先守外层边界；无额外递归预扫/第二遍guard/排序或未列复制 |

旧rule_profile中`fingerprint:374`仅按长度bound并扣work，不累计input_bytes；`check_value:70–84`则先encode_input再hash。因此replay占input/output各至多I/O，saved-encoding占output≤O，saved-issuance占input≤I，输入2I/输出2O的来源界没有漏把hash当另一份累计input。原执行的每次check_value包含同样的发行指纹核验，saved-issuance对true部分的相同调用确可作费用子集。

K逐项相加为入口1、F、F×C、两次bytes比较最多4O+2、digest比较2H+1、profile比较2P+1，即：

```text
K = 1 + F + F*C + 4*O + 2*H + 2*P + 4
F=1024, C=32, O=262144, H=64, P=35
K=1082571
3W+K=51414219；2I=524288；2O=524288
```

这些数是固定debit单位/编码字节的数学上界，不是实测时间、内存或吞吐。每池不可借用，不能把总量写成单个旧Budget放大后的新限额；trace/firing/head计数仍只由完整replay按旧值限制。生产child若使用更紧per-rule限额，成功执行可由默认限额复演，是这里的单调用上界；它**不证明100规则逐个取默认三池符合I05整次总预算**，实际批调用次数/稳定子池或整次资源门仍待I05第四项回复。

合法结果的saved-encoding工作界依赖它与fresh输出逐字段相同；恶意/损坏数据可能先在编码池资源失败，提案已明确不保证损坏输入成功。不能把这种安全拒绝反过来当作合法执行结果可恢复性的证明。

## 4. 恢复发行、shape与安全失败

提案对ProfileValue保留真实发行检查，未通过JSON字段相同、重算hash或复制seal来冒认。旧rule_terms的弱引用登记按对象身份与指纹，check_value不绑定原生产Budget，故当前同模块经parse_value重新发行且由saved强引用持有的实例可在独立issuance池检查；跨进程旧对象或直接构造的同字段对象不可因此通过。

**恢复费用尚未证明，且明确不在上述三池内。** 从字节到受控记录类、解析每个比较operand、source/大整数处理、构造与持有全部数据，其扫描/分配/hash/发行以及失败原子性须由I05真实载体方案给独立有界来源。不能让复核函数收到saved前做无限parse或每operand新默认池，再把3W+K称整条selected链上界。提案§7的第一/四问足以承接这个必要事实；回复/批准前不得启动消费。

算法guard次序未见未付费全递归漏洞：入口先exact class/tuple及外层数量、native bytes/str/len边界；payload≤O、digest长度64、profile长度P，facts≤16384而非误套1024 firing数。第3步使用受限typed encoder；第5步的PreparedFiring/ComparisonEvidence exact类、comparisons tuple/≤32合并到唯一计费循环，不隐藏第二次全结构扫描。深层坏类型由replay或付费encoder拒绝；不调用用户repr、属性协议或自定义迭代器。

完整比较链为fresh.payload==saved canonical、canonical==saved.payload、fresh.digest==saved.digest，加已比较的profile；不是只认hash。typed编码记录实际批准类名和各字段，元组/list有区别；随后发行核验避免同字段伪造值通过。额外/遗漏group/fact/occurrence、顺序、source/lexical、basis、head与comparison证据变动均由完整字节相等门拒绝，不由repair补齐。源码实现仍须实际检查这些次序和预扣，不可用计划文本替代。

resource保私有安全reason/location，其他不一致/伪造/意外异常统一internal，返回True前不发布fresh或局部结果，这与本私有一致性API边界相符。正式Job取消/deadline、producer/source授权、Store原子性与晚到current由实际owner接口承担，API不能替代；不得把parse_value发行当作源图成员、项目权限或producer身份授权。

## 5. 静态见证与兼容性：能证明什么

40000字符source的census脚本已静态读入，没有执行。其逐引用大小规则与旧_walk的tag/字段/元组及ASCII字节表示一致；提案给291430>262144的逐组input下界能说明费用结构障碍。182041 input、82902 output尚未覆盖work/trace全部成功条件，因此本轮不据它断言原evaluate已经成功，更不宣称新API实跑成功。新候选须按计划完成同一完整见证的旧成功→旧逐组资源拒绝→新批成功及计数原件。

原20路径已Git逐字核为不变；拟新增仅rule_revalidation.py、专属test和fixture三路径，无root导出、旧Budget/PROFILE/语言版本变更、依赖/锁/loader/Store/worker/protocol/main/UI扩权。这个新增模块直接用canonical旧类/API，静态未见必须改旧20的依赖；但未实施、未运行旧回归，也未证实新模块在真实包内可用。若实现增加任何预扫、解析、排序、hash或复制，须重算成本来源并更新精确候选；若触旧20，先单独申请路径，不以本提案作授权。

## 6. 给总控的可执行结论

可记录“提案层条件可行、静态无新增算法阻断”；不可记录“batch API已交/selected已闭环/可直接实施”。授权前先取得原I05对§7四问的真实明确回复：

1. 保存/恢复完整证据及当前发行如何实现，恢复池、上限与原子失败；
2. 原有序全部matches含false能否保留到何时，跨child恢复需哪份获准载体；
3. 原定义/Catalog/版本/source与producer的不可变绑定；
4. 真正批调用次数及整个child/每rule复核资源上界，不挪用已耗生产池。

若这些事实满足且root随后精确授权，可用独立新候选实施三新增路径并执行提案已列正反/边界测试；不要求完整T01/T03/T05父模块先完才开始独立工作。若只可提供true groups或无有界恢复，该方案当前调用前提不满足，应回唯一owner协调新精确设计，不删false要求、不暗增存储、不把typed身份检查放宽成字段相等。

完整FR500–505/G.2、实际图解码/匹配、原父验收与目标平台、包、固定新候选双方指定审查、CI/PR/正常合并门均保留。本次未执行产品、parser、测试、构建、probe或GUI；未消费凭据；没有向功能聊天发消息或修改其证据。以上结论是方案静态审查，不是运行/集成/发布通过。


## 7. 追加：I05实际四项答复后的落地判断

本节新增全文读I05 `docs/iterations/I05/profile-selected-carrier-facts.md` 当前5316B/SHA `d7f128c22719561e75a737a7093a01d19132265f805f429eb9811cf7b74dcd47`，位于 `.worktrees/I05-profile-integration`。这是尚待作者格式/固定的事实答复，不当最终候选或已批准实现；未据它追读动态源码。上文“四问尚未到”为本报告首次静态判断的历史时点，本节更新接续结论。

**当前c1a不能直接成为I05实施合同。** 答复确认：生产确实构造完整false/true原序controlled，但未保进返回对象；JSON没有exact records恢复/重发行器；正式producer不可变ref和跨child载体未交；每child默认三池也与整次分池政策不等价。因此前文条件可行不变，实际采用前提尚未满足，不能将原对象仍活的当场复核说成selected保存读回已可用。

### 7.1 原child限额需要T05新精确提案

原c1a签名不接收limits，且三池均固定默认。I05实际按N≤100分child，W_i/I_i/O_i等总和≤整次默认；逐child套c1a的默认三池，对损坏输入的最坏消耗可变为N倍默认。即使各合法成功结果在默认池能够复演，也不能据此证明整个请求资源不放大。

由T05增加可信原child ProfileLimits或等价受控入口是技术上合理的方向，但它改变c1a API/预算合同，需要T05新精确提案、证明、测试及固定ref，不由I05复制/改checker，亦不修改旧1e3默认限额。至少需绑定：

- exact合法原child limits，由真实私有allocator/原执行capture提供；不是公共caller选择较大限额。definitions/catalog/原matches/limits必须来自同一原child，不能用结果内容或当前profile反推额度。
- replay/saved-encoding/saved-issuance分别使用同一原child上界，仍各自独立、不借用、不reset。原成功执行片段/子集的证明须以这些相同限额重新写实，不只说默认上界足够。
- 外层matches/firings/输出边界与该child限额一致，comparison C保原固定32或实际更紧值；K_i的循环与预扣须对应真实实施。整次应写 `3*sum(W_i)+sum(K_i)`、`2*sum(I_i)`、`2*sum(O_i)`，不再把每次默认K无条件当全请求K。规则数、总bindings、总额度和调用次数都须在可信总控门固定，不能通过拆更多child取得更多池。
- disabled条目没有evaluate产出的batch，不能虚构空batch让新API宣称已重验。禁用定义原本仍需有界编译/常量预检，且费用必须归入整次限额；T05/I05新合同须明示该编译路径与active replay如何合计。无匹配的启用规则确有合法空成功batch，与disabled不能混同。

R恢复池另算，不能塞进上述Σ式或再把100个默认R累乘。答复建议R_work≤W、R_input≤I以及JSON8MiB/depth32/1M节点只是待证明申请，尚不能保证全部批准合法成功结果可读回；解码、完整字段对照、唯一term缓存、parse发行、key构造/比较/hash和载体保留须逐项给来源。缓存key须包含完整TermInput/source四字段及精确None/lexical身份，不因归一化或别名免费漏算；缓存只抵恢复parse，不能免T05每occurrence编码/issuance。若独立证明不成立，应改精确成本界/版本，不删source、false、head或comparison取巧。

### 7.2 最小临时mechanismBatches carrier的边界

在当前私有P1计算对象内保留**实际传给evaluate的同一原tuple**，连同同child原definitions tuple、实际Catalog、实际division limits和disabled状态，属于解决已确认事实缺口的最小合理方向，静态未见必须扩Store/公共DTO/长期载体才能保这些当前进程数据。root可另行精确决定此临时增量；本报告不授产品写权。

有以下必要限定，满足前不将capture记为完成：

1. 保存引用发生在原controlled生命周期内，不能从排序后的true groups重建，不重跑图matcher，不补false；原bindings顺序及全部when/proof/source保持。defs/catalog/limits也要来自相同实际执行，不用当前定义重构旧输入；不得在执行后改写原对象。强引用只维持本进程发行身份，不产生来源权限。
2. 延长原数据存活、任何复制/完整JSON投影均在操作前扣独立图侧/载体额度，保整次1024 bindings、helper输入总池和既有最终JSON+rows门；新增材料触顶应整批安全失败，无局部结果/省略项/少存false。不能用“只是引用”免掉载体扫描/编码成本，也不能把8MiB结果门当进程峰值内存证明。
3. disabled只记录真实状态与用于原预检的定义/限额，不伪造保存batch或零firings通过。active空匹配和disabled要可区分；该carrier不是新增规则启停产品语义或持久字段。
4. 即便当前原PreparedFiringBatch持有已发行对象，也只证明同进程对象可用；完整JSON恢复、字段不匹配不repair、当前重新parse及R证明仍缺。临时carrier不注册新public DTO、wire/能力，不写Store/Job/producer/schema，不承诺长期/跨child窗口、GC或撤回授权。
5. 正式selected必须另接T01实际不可变载体/producer/权限/历史与三字段身份门；current/unknown/historical不能由这个数学capture升级。即时原对象重验不代替保存字节读回，不据此创建空selected测试或关闭父selected验收。

这些限制允许当前独立计算继续，不要求等全部M0才保留自己的原输入。它们也保留真实依赖：T05更新按child重验合同、I05真实有界恢复器与整次R、T01正式跨child载体三者分别交付，不能借本次carrier授权一并放行。当前最新结论为“原提案条件可行、实际I05采用尚需新合同与有界载体”，不是API实施/运行/selected通过。
