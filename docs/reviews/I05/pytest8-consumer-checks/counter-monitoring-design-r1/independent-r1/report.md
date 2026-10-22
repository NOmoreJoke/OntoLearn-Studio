# I05 selective monitoring 纯设计独立审查 r1

结论：固定3.12事实与两个入口的计数设计 Limited Pass；旧严格域下“一般槽洁净不可只读证明”的判断正确。按root随后澄清的合作式工程域，该不可遍历性不能再作唯一阻断：其他event callback/未知code-local可原样存在，不等于本方错计或改他人资源。当前旧伪代码仍不是完整合作式实施合同，须待新的cooperative-v1/精确patch独审，不能直接实施。

本轮无monitoring API、线程、产品/pySHACL导入、pytest、benchmark、formatter或OS实验。作者五member身份全核，design11051B/b48d…及pseudo3193B/53eb…全文已读；未修改原稿或新T03四产品。

## 官方固定事实

独立使用官方v3.12.12文档与实现，不采用3.14 free/clear语义。该版本get_tool只报告名称；use/free仅保留/清除名称，不清callback或events。register_callback为交换并触发audit；local mask只可针对指定code查询，且local不屏蔽global。公开接口没有只读callback getter或全code-local枚举。这支持原严格域负面结论，但不说明本机实际有外来残留。[固定文档](https://github.com/python/cpython/blob/v3.12.12/Doc/library/sys.monitoring.rst#L43-L74)

固定实现又显示：callback交换前先audit；set-local先更新mask，再instrument，后段可失败；instrumentation按new/removed event bits更新具体code。它支持“先记attempted code再设置”和失败后按可能已变状态回滚，不支持只free名字。[3.12.12实现](https://github.com/python/cpython/blob/v3.12.12/Python/instrumentation.c#L1699-L1853)

monitoring是per-interpreter，而原setprofile是thread-specific；PY_START表示开始，resume/throw另有事件。owner线程过滤因此必要；get_ident cookie只在同一存活owner生命周期使用，不作永久身份。[PEP669](https://peps.python.org/pep-0669/#specification)、[固定setprofile文档](https://github.com/python/cpython/blob/v3.12.12/Doc/library/sys.rst#L1364-L1392)、[固定线程cookie文档](https://github.com/python/cpython/blob/v3.12.12/Doc/library/_thread.rst#L99-L104)

## 计数领域

独立只读固定553a63源码/指定venv文件的字节与AST，四来源长度/hash均和作者extracts一致。reason1247–1258及Validator.run175–324均为同步普通def、无decorator、无yield；这是本版本可以只数入口的依据，不推广到generator/coroutine。

两个独立if/code-is比较保留同code双角色各加1；去重仅用于事件设置，不能去掉第二角色计数。别名仍按实际code计；同名不同code不计；零入口为0；直接异常在进入后仍应计1；普通递归/嵌套每个真实入口计；其他线程同code回调虽可发生，但owner过滤不加计数。这里是逻辑推导与未来测试义务，没有实际运行这些场景。目标必须保持强引用并按identity去重，不能用code结构相等代替is。

public co_code的去专门化取值路径可见固定codeobject.c，但这不是本项目loader/marshal指纹在启用前中后必然相等的运行证据；后续仍需限定真实单元，不预签身份或性能。[固定codeobject实现](https://github.com/python/cpython/blob/v3.12.12/Objects/codeobject.c#L1433-L1469)

## 工程域澄清后的正反例

此前独立中间意见针对严格“从未瞬间交换、全槽洁净”域，保留为历史。root现明确允许申请已释放槽、有限PY_START交换检测，承认短暂交换；不要求抵抗same-process任意接管，不允许清未知其他code-local或调用global restart。以下按这个实际工程域判断：

- 名称已占用或原profile非None：必须拒绝且不清外来资源，不能换ID绕开。名字空闲仅使use_tool_id申请有机会成功，不是clean证明。
- 其他event的callback与未知code-local：只要本方未写它们，应原样保留。它们原先可观察执行，不是新计数器必须消除的东西；不能为了“空槽”去逐event交换/清理或扫全code。未知code上的PY_START可能调用本方新callback，code/owner过滤使本方计数不误加；不得宣称全解释器只两code触发callback或总开销只两目标。
- 若交换PY_START返回旧callback非None：立即原样恢复并拒绝，不能链式调用它后继续成功。这是已允许的检测性交换，不是接管活动工具。
- 退出只撤销确获确改资源，然后释放本方名称；“恢复本方前像”不要求消灭预存other-event/unknown-local。旧伪代码中可能被读成“存在任意callback/mask就不许free”的措辞，须在新的合作式方案明确改成“本方未恢复则不free”。不把原有外来观察误作本方残留。

## DISABLE：固定源码给出的边界

DISABLE不改declared event mask；同mask set_local_events会早返。所以已释放名称但target local仍为PY_START且该位置曾DISABLE的状态，必须由非零target-mask准入检查拒绝；不能直接再次set(PY_START)并假定重启，更不能先清别人mask来满足准入。[固定DISABLE文档](https://github.com/python/cpython/blob/v3.12.12/Doc/library/sys.monitoring.rst#L257-L275)

静态正例是global0、target local0，且本次0→PY_START设置完整成功：fixed _Py_Instrument计算新增tool bit，再在目标code相应入口位置add_tools/instrument，因而会重新启用该目标入口。已有nonzero→同nonzero不触发这条新增路径。该结论只限成功的精确target转换，不是API实验，也不保证失败中途状态已恢复。[固定新增bit路径](https://github.com/python/cpython/blob/v3.12.12/Python/instrumentation.c#L1484-L1554)

必要后续单元应分开：残留nonzero+DISABLE拒绝且前像不动；合法local0重新启用target可计入口；同mask setter不能作为restart替代；不影响别code及别tool的disabled位置。不得用global restart_events解决局部问题。

## 合作式实现前还需落实

1. callback对象必须保存稳定引用；register时存入的bound method与cleanup比较对象要is同一实例，不能每次self.method生成新bound method再误报。正常注销返回的旧callback若不是该对象，须保存/恢复实际交换出的外来对象并报private integrity失败；不能静默丢弃它或只因name相同就free。恢复再失败/状态不明时隔离本方reservation，不报告成功。name是合作标记，非所有权token；此处要求正常错误检测，不要求一般恶意竞争可恢复证明。
2. acquired只在申请成功后置位；callback注册/恢复与每个local尝试分别记状态。去重目标必须在set-local前登记；entry失败、body异常、cleanup异常都先active=False，再尽力恢复确改资源。不得全局清事件、清未触碰code或free未取得槽。
3. cleanup完整性失败优先阻止成功/业务拒绝/可靠0；body异常保留私有上下文但不能掩盖counter失败。确有本方callback/local未清时不可释放dirty本方reservation给下一case。未触碰的外来状态无需证明为空，也不可顺便清理。

这些是下一份具体方案和源码patch必须可审计的状态机条件，旧设计尚未把所有交换/回滚分支写成可实施合同。不能根据本次计数逻辑或PEP低开销目标预签120秒达标；417、原120秒/64MiB和业务语义不变。

当前probe仍2996，counter未实现；原严格结论保留，新root澄清也明确记录，二者不混成无条件实施批准。下一步只审固定cooperative-v1提案/patch及有限units计划，再由root发实施票；本审没有开启任何实验或扩大到真实full-v1/B1/整体验收。
