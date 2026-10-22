# I05 generator style 独立前审

结论：冻结候选无静态阻断（Limited Pass）。此结论只覆盖 proposal，实际旧/新生成黄金字节与最终产品字节尚待复核；不代表产品、语义或业务运行通过。

审查范围：固定 513db0056f312342a6791e2d4c7842f3726581f2 的 scripts/generate-i05-source-package-inputs.py，旧 60354 bytes / e58dd4efd1c64952b6555b98c65271fc7e82d7b99b198d848d69f5a7c9dcde0b；候选 proposal.py.raw 为 75633 bytes / c51a1a7f3085e79958022deda95d8a08792f3a95f7c4f1fb171d56196f3d2d26。完整读取旧 786 行、候选 2043 行；读取本树 AGENTS overlay 并保持未写。审查者独立执行的程序仅用标准库 AST、tokenize、hash、JSON、内存补丁解析及固定 Git 读取；没有执行 generator、Ruff、formatter、pytest、产品、语义 collector、CLI、数据库、网络或 GUI。

独立 proposal-review-check.py 实际 exit 0、stderr 0 bytes。仅允许下列四项受限逆转后，候选整个模块 ast.dump(include_attributes=False) 与固定旧版本逐字段完全相等：

- 顶层 I 改名 iri_term；恰 26 个 Name 引用全部直接用作 Call.func，无函数值逃逸。
- add_records 局部 iri lambda 改为单 Return def；参数和返回表达式完全相同，所有引用直接调用。名称、代码位置、函数对象 qualname 等 Python 反射属性并非本次全观察等价主张；该局部函数未逃逸。
- add_original_qv 将未使用 cases 赋值改为 Expr，原 json_source(path) RHS 原位置完整保留，因此解析和 source inventory 副作用未删。旧 cases 恰一处 Store，无 Load。
- 相同 pathlib.Path 导入移位；其他导入及执行顺序与旧版 AST 一致，所有导入均在 ROOT 求值之前。

其余 AST 字段完全不变，包括所有 Constant、JoinedStr/FormattedValue、数据结构、迭代顺序、版本、policy、supplierRef、引用和表达式。35 个 literal / 6 个 JoinedStr 拆分是作者的中间证明统计；本审查另从最终冻结候选直接验证全部 AST 字段，不依赖该中间证明。15 个 COMMENT token 的字符串及顺序原样。完整 32 个 patch hunk 按上下文核验并在内存重建，其结果逐字节等于候选；build 内副本也完全相同。执行本次检查时产品路径仍为旧字节，没有提前实施。

核验作者实际收据及原始分流的 bytes/SHA：baseline Ruff 178 项为 E501 174、E731/E743/F841/I001 各 1；proposal 第一轮 37 项记录原样保留；proposal-ruff-02 exit 0，stdout 原始恰 []（2 bytes），stderr 空；proposal-format-check-01 exit 0，stdout 原始恰 `1 file already formatted\n`，stderr 空。上述是对作者运行收据的独立核验，审查者没有重复运行这些工具。完整 argv、实际 start/end、exit、分流 bytes/SHA 见原收据及本目录 review 原始流。

执行边界：源码仅导入标准库；本地原件通过固定 git show ref:path 读取，未添加业务导入或运行路径。example.invalid、file:// 等为序列化拒绝输入字符串，不在生成器中访问。main 固定输出两件 runtime JSON、source manifest 与说明报告。--check 逐字节检查全部四件输出，其中 source manifest 含实际 generator 自身 bytes/SHA；新生成器不能拿旧 source manifest 伪称 --check 通过。

后续验收：作者在 old/new 两个 detached 513 隔离副本各实际默认生成一次，保持 live 冻结原件不写。应核旧/新脚本身份、受控树路径、完整实际 argv/时段/exit/原始 stdout/stderr 和四输出，分别对两件 runtime JSON 验证原冻结 21202 bytes / 0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a、8205267 bytes / 47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa。原失败不可改写、oracle 不可调整。完成后由同一独立审查者只读实际结果，不重跑未变化 generator。
