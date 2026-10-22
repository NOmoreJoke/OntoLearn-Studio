# 最终测试格式 delta：有限候选可移交，wholecheck 保持 NotPass

结论：**唯一 line-wrap 修订静态可接受，可按 root 已明确的有限候选范围冻结/移交；完整 check 仍 NotPass。** 新测试文件 216d 与实跑101项的76068在完整 AST 去位置属性后相等，实际文本差异仅 make_case 的一条 if any() 条件合并换行。没有重复 supplier 模块运行，101项结果必须继续绑定76068；不能改称216d已实跑101或全量检查已通过。

首 `independent-final-intake-review.md` 与其 manifest 保持原件，描述格式化前的 intake。审计过程中观察到当前测试字节改变，随后收到主控明确的新格式阶段说明，本报告追加固定新状态，不追改先前当前字节观察。

## 新旧源码身份与精确差异

- 格式化前：47649 B / SHA `76068ad0853dabef7d99d97445f1a3da7b8ec52f2615524856f99c9655c28f9a`；完整 supplier101和首 npm check 均为该版本。
- 当前格式化后：**47627 B / SHA `216d92b0dae54c28bb9464cf854e39110b8010d73020b1d66cdd9cb4df92d4a2`**；当前文件等于 owner/actual-test-v2-formatted.py.raw。

独立用 stdlib ast.parse 对两个完整原字节做 ast.dump(include_attributes=False) 比较，结果完全相等；用文本 unified diff 再确认仅以下一处：

```diff
-        if any(
-            name == prefix or name.startswith(prefix + ".") for prefix in p.FIXED_DISTRIBUTIONS
-        ):
+        if any(name == prefix or name.startswith(prefix + ".") for prefix in p.FIXED_DISTRIBUTIONS):
```

没有改匹配范围、MonkeyPatch 生命周期、seed/恢复/None/近似名、首次 fake_module 抛错、动态 request.getfixturevalue、clean-positive→unknown-child 或 recheck 的断言/预期。完整 AST 相等支持这次源码结构没有变化，不等于两个不同 SHA 的字节身份相同，也不生成一个新的 runtime101结果。现有 body、固定字符串、embedded Node raw 与 imports 都进入该完整 AST 对比。

## 实际有限验证及首格式失败保全

独立复读04/05/06/07/08各 start、receipt 和完整双流，全部 start 字段匹配最终 receipt，流的 bytes/SHA 全符；三份 production source 的 before/after 都不变。按实际 UTC 次序如下，编号04不代表它先执行：

| 步骤 | 实际 UTC 开始 | child exit | 绑定测试身份/结果 |
| --- | --- | --- | --- |
| 05 test Ruff check | 21:06:33.040065 | 0 | 76068；All checks passed |
| 06 首 test Ruff format --check | 21:06:58.430485 | **1** | 76068；明确只指 if any 条件包装，1 file would be reformatted |
| 07 仅 test Ruff format | 21:07:39.674148 | 0 | 76068→216d；1 file reformatted |
| 08 最终 test Ruff format --check | 21:07:39.893455 | 0 | 216d；1 file already formatted |
| 04 test 路径 git diff --check | 21:08:00.893402 | 0 | 216d；双流空 |

日期均为2026-10-22 UTC。06失败收据及487 B stdout原件存在，没有覆盖、删除或把它回写成通过。07是明确允许的单测试文件格式操作，它的 fourSourceBytesUnchangedDuringRun=false 正确记录了测试 SHA 的有意变化；其余三个 source 不变。当前记录器仅给此 label 且仅此 test 的预期变化特例，未普遍允许其他源漂移；本 agent 只静态读记录器，没有执行它。

Ruff check 实际在76068通过；216d实际执行的是最终 format check 与产品 test 路径 diff check。本报告没有虚称另一次216d Ruff check或supplier重跑。主控转达 root 已允许这种有限101/wholecheck NotPass移交及单 test 样式收口；本次静态 AST/文本复核为该有限交付提供明确对应关系。

## 未改变的阻断与固定产品

独立再次核当前 builder8437/738f55ef…31a8ff、entrypoint976/aaf9f85b…035ef3、reader46602/c96f0630…3b7b0c，与6202逐字节相同。完整 SHA见 audit-format-delta.stdout.json，未改生产 reader 的未知 loaded child 拒绝、路径/代码/loader/native规则。

此前首原 npm check 仍为 exit1：三份继承固定文件的 Prettier format gate，不是06这个单 test格式检查。两次格式失败对象与范围不同，须分开保留。原 check 未到 typecheck/vitest/build/Ruff/whole pytest，verify:sources 等未执行步骤仍不计通过。没有因本次允许有限交付而修旧producer三冻源、改ignore/配置/expected或重跑fullcheck；root的有限移交不是整体通过。

原 fullcheck03 的1320/2、原98、76068 supplier101、首 npmcheck格式FAIL、06 test格式FAIL、216d的08/04通过，各自按实际输入保留。I05以后是否采用及整套复验由root另行交接；不是当前供应方已在I05树修复成功。不得据此形成 native/CLI/打包/GUI/父业务、CI或发布通过。

本 agent 仅追加独占 independent-final 的报告与静态审计raw/输出，不执行工具链或测试、不 import产品、不修改其他文件或 commit。旧 intake报告/manifest与旧6202历史manifest均未改；新增 format-delta-manifest 单独覆盖本次增量和旧 intake 原件，防止覆盖首轮审查历史。
