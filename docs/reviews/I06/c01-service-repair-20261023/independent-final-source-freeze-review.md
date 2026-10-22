# 四路径最终源冻结静态复核

结论：相对已完成的四路径独审，仅 gateway test 有无语义变化的格式调整，其他三路径逐字不变；未发现新增 P1/P2。新 plan 的初始格式修复追加合理，未扩大 target/check/verify 的参数、环境或预算。本报告只静态读文本/JSON并计算字节SHA，没有运行 formatter/linter/typecheck/测试/产品、没有执行runner或导入候选代码。

## 精确输入与最终四路径

树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-C01-service-repair-20261023`，沿1f3 base、精确四路径START票6465B/`73b70587ff0a1301ab9ecba6ccf56ccd3fc96c4b452650175d2c6ed5b49d2612`。旧独审原文及首失败记录保持，未覆盖。

| 路径 | 最终bytes | SHA-256 | 与首次四路径独审比 |
|---|---:|---|---|
| apps/desktop/src/main/model-gateway/model-service.ts | 22303 | be3cb0c91ead9a84d34b14429e5284789c205dd234d61eba3513c89a1f075098 | 完全相同 |
| tests/unit/i06-mf02-preview-cleanup.test.ts | 8731 | 3477be7b5b0a516353293e4c0546e5bd896022fc1469db49e55e34547badcfce | 完全相同 |
| tests/unit/i06-gateway.test.ts | 23589 | e167ab5f7e557b3c3e316ae9383703ebbb5616329ac5464d6424ff2e42f4eb27 | 仅下面格式delta |
| tests/unit/i06-stored-result.test.ts | 51350 | 2a2b2afc9c1644e30812790bf1452b8336712f919fa5d58c00445d7002ab376e | 完全相同 |

## gateway test精确格式差异

直接比较当前文件与固定scratch `outputs/20261023_I06_C01_disposition_scratch/zn1-3/proposed/tests/unit/i06-gateway.test.ts`。唯一hunk是原622附近 `it.each([429,503])` 调用的换行/缩进收拢，并移除最后async回调参数后的可选trailing comma。**因此严格说不是“只删空白字节”，而是仅无语义的格式变化。** 未改测试名、两状态值、fixture handler、调用次序、两条完整URL/body、终态错误、两intent/末项failed或不含上游错误正文的断言；没有新增执行语句、hook、skip、弱化断言或测试开关。

首次四路径独审8909B/SHA `979f3409d0a76c8534352207f4d519e0abf50811b92024a56f205dbdd504afe4` 的实质结论因此继续适用于最终四路径，须与本报告的新版gateway SHA一起引用，不能继续使用格式前09fc…作为最终gateway pin。

## plan追加精确对照

- `runtime-plan.initial.json`仍6079B/`c544aad84b1f4cb939c8c60e42025ba17bf469fd7425d86134707e7142f499c4`，是r2 runner独审核过的原计划。
- 当前 `runtime-plan.json`为7277B/`5f29823dea71d08dc441987965408a90c4e412d091469154a6037a21e5c52b31`。
- JSON结构比较仅增加 `format-fix-gateway`（own Prettier --write **只该一个gateway test**，120000ms、不要求runtime freeze、allowsFormattingOnly=true）、`format-check-four-r2`（同原四路径--check，120000ms），把 `lint-four.dependsOn` 改成后者，以及新增明确保留原format-check-four child1的说明。没有删除旧format命令或其原receipt。
- 既有七命令除上述lint依赖外逐项完全相同；特别 target-mf02/target-zn2/target-zn3/ordinary-check/verify-sources 的argv、依赖、300000/600000/120000ms预算与requiresRuntimeFreeze=true未变。没有新增native/e2e/package/OS/probe或产品修复动作。
- `runtime-environment.json`现已实际存在，2091B/`843f2c06aed90371644114a7ff77520d1d540eb22c7e922172be2e13a52e6833`；解析dict与初始plan及新plan.environment精确全等，非只检查PATH某几项。没有新增环境授权或用户凭据读取。

主线报告原format-check-four首次child1仅gateway格式warn，随后单文件write与四文件check-r2 child0；原raw/format-check-four保留。本独审没有重跑或将该主线消息等同本轮独立运行观察；此处只判断实际source/plan追加符合票内“初始四路径静态准备，失败保留、精确修复后复核”。允许write只为本次已发生的精确格式修复，不是允许任意后续失败自动重写源码。

## 冻结与剩余门

本报告供主线生成最终948项向量（947tracked before路径+授权新增test）并登记正确独审pin。targets仍须通过实际source-freeze与运行前全向量精确比较，不能把格式前报告/旧gateway SHA当新版向量。runner首审和r2保持原字节，后续actual source-freeze与runtime receipts由主线按原票核定；此处不代签尚未执行的targets、普通check或verify，更不关闭MF01/ZN1/真实平台/双指定模型门。

只新增本报告，未改作者源、runner、plan、环境或旧报告；冻结后停止写入。
