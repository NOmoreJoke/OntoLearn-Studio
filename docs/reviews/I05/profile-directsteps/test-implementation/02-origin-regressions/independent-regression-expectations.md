# 独立来源反例回归补充

本补充只追加新测试，不改 `aec3b2ef98fb4d27cb2d2e4cbf9133cfeb89682e` 已采用测试的任何字节；旧测试文件原件仍为当前文件完整前缀。旧过程证据不改，新记录仅在 `test-implementation/02-origin-regressions/`。作者未参与产品修复，也未执行主线探针或候选 pytest。

已完整读原 `counterexample-probe.py.raw`、`roots-probe.py.raw`，以标准库读取/解析原 observations 与 supervisor 元数据、双流文件；原 JSON 的 fee records 不用来重造预算。读 `initial-18908e4-report.md`，并只读主线 working diff 的 production/material 类型门、expectation domain 类型门、leaf ID 绑定、typed firing/head 与 evidence 对应检查、private capture exact 类型门。原 probe 绑定 `18908e4abca900a07a15a5d157d4022f2a11349a`；working 修复尚非本作者签署的固定运行候选。输入与所读源码 SHA 见 `inputs-readback.json`。候选 append 持有、Reader 费用及 carrier B 接线由预算独审复核，本补充不重复或代签。

## 1. 外来协议不得在类型门前执行

纯输入从真实 `prepare_profile_material` 制得 exact ProfileMaterial，再用 dataclass replace 改一个字段。八个 material case：input_preimage、definition_material、source_preimage、definitions_preimage 各一个有 len/eq 的外来对象；前两个字段另用 bytes 子类；source exact tuple 内放外来对象；records 中 exact TermInput 的 source 放外来对象。外来类使用带 `__eq__` 的 metaclass，能检测 `type(value) in (tuple,list)` 一类协议泄漏。所有 len/eq/class-eq 方法只记一次调用并抛 AssertionError。独立预期是 callbacks 恰 `[]`、真实 reason 调用0、D failed、有限产品异常且无 context/cause/成功 prefix。外层 exact class 不等于嵌套字段已可信。

Expectation 单独从真实 caller-held 上下文建立 exact ExplanationRestoreExpectation，只有 input_domain 替换为外来 len/eq 对象。字符串域判定必须先过 exact str，故 len 和 equality 的调用数均为0；拒绝本次完整恢复，D failed。这里没有把一个外来对象的 `__eq__` 回答当实际 domain 判定。

这些预期由 exact 类型语法门决定，不从修复后的 actual 调用计数回填；测试本身还核外层 material/expectation 类型保持 exact。原审查在旧候选观察到 len、class-eq、domain-eq 非零，不是本作者重新运行的结果。

## 2. 全链一致改名不能替换原叶算法

实际纯输入固定为 domain→type depth2 三个 records：`(p,domain,A),(x,p,y),(A,subClassOf,B)`。其真实三元组不变；选原叶表第一行，依旧算法独立算 `i05-proof:` + SHA256(`i05-profile-proof-leaf/1\0` + 三字段以 NUL 拼接)，确认原 reference 与该值相同。改名值固定 `i05-proof:` 后64个0，显式核它不同于该 triple 的固定算法值。

只在已产 wire 的接收副本上，把原 ID 全量统一替换，包括 proofLeaves、directSteps leaf refs、rdfsEvidence union refs；至少三处替换且旧 ID 全部消失、原 triple 保持不变。只更新 payload/rows canonical bytes 与它们的 caller-held digests，原输入/来源前像和其上下文不变。这能排除“仅因悬空引用或 envelope 摘要不符拒绝”的伪通过。独立预期仍是 DIRECT_STEPS_INVALID 或 RESTORE_INPUT_INVALID，不能因所有引用一起改名就接受；不允许把预算 LIMIT 当该回归通过。整次恢复有限失败，没有返回 view。

## 3. evidence 索引必须指向实际 typed occurrence

纯输入是两条 ObjectProperty 声明与 `(x,p,y)`；真实 rule 的 when 为 `(s,p,o)`，heads 为同一个 `(s,out,o)` 两次。手工预期只有 firing0，具有 head0/head1 两个实际 occurrence。测试先断言该预期，再只把接收副本中 evidence 第一行 firingIndex/headIndex 改为 integerHex 的1023/15，完整 typed firingGroups 字节不变。只重绑 payload/rows 摘要。

1023与15纵使在各字段数值范围内，也不对应当前保存的 firing0/head0或head1。要求完整恢复 DIRECT_STEPS_INVALID 或 RESTORE_INPUT_INVALID，D failed；恢复不得重新 reason。这样 roots 没有机会发布不存在的 occurrence，不以“返回伪 root 后再隐藏”替代 fullview 一致性门。第二条相同结果的真实 head1 不因测试而删除或裁剪。

## 4. 私有 finite closure 只接批准 exact capture

给真实 parse_turtle 两 seed 图 `(x,type,A),(A,subClassOf,B)`；若进入候选循环必然遇到 type-via-subclass。传入外来 capture，其 candidate 仅计数并抛 AssertionError。独立预期是在任何 candidate 调用前以有限 ProfileReasonError/INTERNAL_ERROR 拒绝，callbacks 恰 `[]`。这项是私有入口误用防御，不供应任何 fake reason 结果、carrier 或新费用。

## 验证与交接边界

本树仅有旧产品与新增测试；不运行 pytest，不借主线环境，不把 import failure 当测试。自己的 .venv 执行 Ruff format、Ruff check、format --check；标准库 AST 解析不导入产品。新测试26个函数；静态 runner 另核原测试字节完整前缀、所有139成员与原 adoption/Git/固定SHA相等。argv/cwd/有限环境/起止/双流/exit/新测试前后hash/独占保留basetemp位于同前缀 `static-final-*`；静态命令不产生产品 fee events。主线逐 Git 采用后运行全部新旧回归并保留首失败/实际 fee 原件，才可签候选运行通过。
