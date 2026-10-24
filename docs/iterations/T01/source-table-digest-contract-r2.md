# T01 完整解析表摘要合同 r2：D1受控数据捕获

本页只补充 [r1](source-table-digest-contract-r1.md) 的输入所有权、一次捕获和预算不变量，保留r1原件。总控独立设计报告 `T01-controller-source-r4-table-digest-design-review.md` 10249B/SHA `9da31728abe373a0e6b455f508d4fc4de2459c1e570362674561c7f286868c39` 已全文读；其中D1/P2是设计缺口，不冒称已跑出的代码bug。本页未装配helper或运行机制测试，实际状态见 [status](../../reviews/T01/status.md)。

## 1. 接受边界与所有权

纯canonical材料助手是受信owner内部函数，只接受由受限解码或批准producer适配生成、由该owner独占的 **data-only JSON树** 及受信sourceHash/预算；不把任意同进程宿主对象当输入能力。传输来源在原严格字节解码器完成重复键/深度/字节/数值等原有门后，才由owner取得树。完整表超过单帧时须走批准的受控运输，不扩大单帧限。parser dataclass须在producer自己的已批准适配边界转成明确值，不能让canonical对未知对象自动调用转换协议。

- TS对象只能是该受控树中的普通记录/数组及JSON原始值；全部材料属性必须为own data descriptor，禁止getter/setter、toJSON、Symbol.iterator、自定义valueOf/toString、方法、symbol或原型回调参与读取/转型/遍历。数组拒hole/额外属性，按数字索引取已查descriptor.value，不调用输入迭代器。字符处理使用受信内置标量操作，不对宿主对象强转String/Number。
- Python仅精确builtin dict/list/str/int/float/null，bool仅在允许的位置（行号/预算不允许）；拒容器和标量子类、dataclass/custom Mapping/Sequence、generator及自定义转换。先确认exact type及精确str键，再做真实builtin访问，不调用未知对象的__iter__/**getitem**/**str**/**int**/相等/哈希协议。
- 受信sourceHash、options和implementation也经同一捕获，不把“可信配置”解释成可以含getter的对象。三字段仍指回唯一canonical原定义；仅在捕获的私有原始值上调用必要既有validator，不先把caller对象交给Zod/JSON/stringifier/deepcopy。

**JS Proxy不能仅靠反射绝对识别。** ownKeys/getOwnPropertyDescriptor/getPrototypeOf等本身可触发恶意Proxy trap；本函数不宣称在任意同进程敌对Proxy、被篡改intrinsics或并发宿主内存之上提供安全隔离。owner须保证入口来自实际受限解码/自有producer，不能把renderer或扩展直接传入的对象赋予该前置。需要对不可信执行代码抗CPU/内存滥用时，使用原受控worker/进程隔离和硬预算，不能用“无await”或浅freeze代替。机制测试可以验证普通accessor拒绝且不执行回调，不能把它宣传成所有Proxy绝无trap。

## 2. 一次有界捕获，之后只用私有材料

选择 **有界捕获一次→只读私有材料编码**，放弃“第二遍再次读caller原对象”的旧推论。精确流程：

1. 检查受信必填预算为正safe integer；用受信builtin做有限头结构/计数检查。fields≤256、rows≤50000、每row宽度≤256；拒未知或缺字段。记录自身每层键数/shape亦须有界，不能先对不受限对象全量descriptors/深clone再检上限。实际运输树的先验字节/深度预算由原owner负责，不能拿encoded材料预算补证此前解码内存已安全。
2. 每个材料字段的own data值只捕获一次；普通记录读取descriptor.value后立即校验其原始类型。捕获一个row/cell所需值时先拿固定小字段集合并冻结其局部标量，不在计费与存储间重新读取caller。原记录/数组对象引用不进入最终材料树，不保留稍后可执行的getter、迭代器或callback。
3. 使用独立计数器逐标点、标签/版本、safe integer十进制、字符串码点计精确escaped UTF8长度。**每个值/容器加入私有树或生成escaped副本之前**，先比较剩余额度并预留相应材料字节；超预算立即终止。集合/行/格上限与材料总预算共同限制捕获规模，不先全量map/Zod clone/JSON.stringify/encode后再计费。
4. 私有树只保存已捕获的不可变标量与新建owner私有容器。JS字符串是不可变primitive，可保存该已计费值的引用；不必对同一字符串再复制。Python精确str同理。可保留已计费的有限escaped chunk；若先存原字符串，最终编码只读这一私有值且按同一规则，不读caller。每个保存节点均已有对应材料预算，逻辑预算不宣称等于实际heap/RSS。
5. 完成完整类型/顺序/跨字段等值验证后，以同一私有树编码/哈希；需要一次分配最终buffer时，只按已核验精确总长分配，核实际写入长度相等。不得在第二遍回读caller或使用其toJSON。编码完成前不公开私有容器；公开只返回独立材料bytes或摘要，之后caller修改原对象不得改变已产出字节。异步SHA只能在材料bytes完全私有确定后开始。

无单项长度界的sheet也逐码点计费，在越过剩余总预算的第一个点立即拒绝；不先Array.from、展开字符数组、完整escape/UTF8副本或全量clone，也不为简化实现擅加sheet产品长度限制。字符串不可分割的实际宿主存储已由producer/decoder持有，不将该既有分配冒称摘要器已防住；本合同控制新增捕获/输出分配。Unicode和NUL规则、空白字符集、JSON值整数规范、完整材料次序均沿r1。

任一捕获/验证/编码失败，私有临时状态不发布，不能返回部分材料或部分digest；错误只用批准的受限内部类型，不回传caller值或宿主异常。未知宿主对象的异常不做字符串化日志。预算和编码必须基于同一捕获值，不能仅在编码后发现超长再把其称为合格预检。

## 3. 必要机制反例（未运行）

| 输入或动作                                                                 | 必须验证的边界                                                                              |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 普通own data属性对比同名getter/setter                                      | data值按合同工作；accessor在任何回调执行前拒绝，计数器证明getter未被调用                    |
| getter试图第一次短字符串、第二次长字符串/孤立surrogate，或改options/另cell | 不得读取getter来计费或编码；明确拒绝，不以无await作为证明                                   |
| 自定义toJSON/valueOf/toString/iterator、数组hole/额外symbol                | 不调用；不得影响输出材料，按严格数据树规则拒绝                                              |
| Python dict/list/str/int子类、Mapping/Sequence/dataclass/custom equality   | 精确类型门先拒，不隐式执行自定义协议；正常builtin数据作为对应正例                           |
| caller在捕获完成/结果返回后改原字段、数组、options和implementation         | 原已产出bytes/hash不变；编码逻辑无第二次caller读，必要时对私有快照入口定点验证              |
| sheet超预算、Unicode escape/非BMP/NUL及exact预算/±1                        | 超预算在昂贵新分配前短路；已计费值与最终UTF8精确相等，不擅加sheet上限                       |
| 小预算与极多行/字段、超大/NaN/非整数行号、布尔预算                         | 先有限数量/范围判断，避免math.isfinite超大int、隐式类型转换或全量材料构建；无未处理宿主异常 |

上述与r1六完整T03投影/合成身份golden、5无Table拒绝/6direct cell机制区分及全部原边界一起实际跑后，才有机制运行证据。恶意Proxy可作为“前置不满足/隔离边界”反例，但不承诺通过任意trap安全检测；不得以跳过callback测试来隐含接受宿主对象。

## 4. 准备原件与后续门

未完成准备patch `ffdde792d12ed63705dc715e005cf7574af261dbfdc6b3cd487c2c48712c5845` 保留不变，**不能直接采用其两遍读caller方案**；它只是root冻结到达前的准备原件。下一候选必须按本r2一次捕获重新实现并补真正专属测试；原静态检查不能认证该新实现。b35受审产品源码当前保持原字节，不因本设计修订复测。

本r2须先独立设计复核并由root读回关闭D1，再按明确新phase启动代码。T03真实parser三字段/CSV编码词汇仍等实际owner答复；synthetic机制身份不授予生产授权。source wire/预算账本/worker接线、真实parser→预览确认→Job/Store、业务3 ready/启动诊断、包/native及指定双审/CI/父验收均保留原门。
