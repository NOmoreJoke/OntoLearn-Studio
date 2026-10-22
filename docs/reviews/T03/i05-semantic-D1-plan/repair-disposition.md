# 首审 F1 / F2 修订处置（申请独立delta，未自签通过）

首审完整报告/检查/seal已由主agent封存于 `d014b925e2c9bb246a71621a919d7f9a412f6c57`，受审初版candidate=`ae28572c91b78933c35996f0d80e81c03b96edf0`。作者本次全文读三原件，保留原NEEDS_CHANGE与F1/P2、F2/P3 OPEN事实；下述仅说明修订内容与实际静态检查，最终关闭须主agent新actualcandidate后由原fresh独审delta。未来candidateRef=null，不预填。

## F1 / P2

承认原计划只具体处理两dependency guard，漏列7源资源同路径不同bytes。修订新增guard-scope-matrix.json完整58行和guard-migration-strategy.md：所有旧43按a4d wrapper字面re/ast数据解析、普通Git核ref/path/bytes/SHA/blob；共享22=13同/9冲突（2依赖+7资源源码），old-only21/new-only11，union54加mapping4为新parent/default58。新consumer/四writer实际未来pins仍null。7冲突精确为contracts/python/contract_v2.py、v2/errors/registry/schema.json和engine/resources/semantic/semantic_execution.py，四T01及三原I05/T05来源责任全部保留，非T03扩权。

策略明确历史a4d43+两个原writer共45路径独立root/入口、原无参build与旧83项flag可获授权复现；新semantic33与新parent/default58分别versioned guard。9冲突新scope选新来源/26锁；21old-only逐owner兼容采用或移植，新parent旧flag同canonical旧83模块main([])，保输入83、报告非claims/限额/实际失败语义；不以永久拒旧flag或删guard/glob假称保留。root/owner接收与实际回归未完成，newparent不获build批准，不宣称新旧兼容已证实。T01只用已批5f及其正式供源，不盲采a4d历史Store源码。主方案、source-and-interface、forwarddelta、consumer接口、dependency引用和验收矩阵已同步。

后继仍须owner/root逐项真实采用/源码pin、历史与新parent83及default/S1/storage/worker/contracts/resources各入口真实回归、所有异常及caller scope选择；这些不在本票执行。当前F1处置状态=修订完成、待独立delta，不把静态矩阵当runtime通过。

## F2 / P3

验收R2已使用反引号精确literal `function.__code__`，并保same canonical object、exact CodeType、同co_consts路径和完整Python/fingerprint domain。不会用name反射或sourceSHA替代。formatter后再次核精确raw literal存在且无旧`函数.**code**`。状态=修订完成、待独立delta。

## 历史与实时政策

原15交付的Git原件仍由ae285与旧delivery-manifest固定，原author-checks/author-delivery及review3原件未覆盖；6件规范方案允许前向修改并由新delta-manifest列旧新hash。旧delivery-manifest不假装描述修订后的全部内容，旧readonly81清单也不改写。当前重新静态核81条=80匹配+1livepolicy漂移，当前3160B/SHA2032bd9e1cdbf398a0d505e092e1a08b80ff15df26b1d06c7d7e1c2e0a5a8ec1已全文读，旧3172B/7b54…保在旧清单与首审。repair-input-snapshot单独列全读身份；guidance变化不触发产品重测。

本修订没有新/tmp scratch、产品/锁/tests/CI/旧D066/其它树修改或运行，也没有指定外审/Goal/stage/commit。原作者39scratch越界及首错记录保在原历史文件，当前不追认。repair-checks/delta-manifest另给本次实际静态核验、格式化、旧新文件身份和未验门；作者seal后停写。
