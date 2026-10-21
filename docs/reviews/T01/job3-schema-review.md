# Job schema3 有界内部阶段

本阶段实际修改已生效移交的job_store.py及coordinator.py，新增test_project_job_format3.py；未使用未批准I05/I06源码，canonical/main入口仍2。

显式JobStore(target_format=3)仅由Store拿同一writer lifetime lease，默认2保留原路径。Store3完成后，在同连接/同lease执行独立第二层事务，严格区分无Job层、完整旧Job层、完整新Job层；缺表/trigger/未知结构拒绝，不IFNOTEXISTS补坏库。失败保留有效Store3和完整旧/无Job层，重开恢复。job_format是不可变结构来源/hash证据，不是进程/session-ready标志。

原全局operation_claims唯一演进为六列operation/project/job/fingerprint/kind/context；旧四字段原字节保留，旧行kind=job/context=NULL。SQL严格job/application分支、application无Job，尚无完整应用adapter时其行明确拒绝完整层验证。旧Job重试先识别kind，跨kind复用固定identity conflict；没有第二claim表/Job包装草稿。新项目的public映射与domain/app genesis同事务，迁移补齐真实映射并保留已有UUID。project_get报告实际DB格式。

入口额外守门：无效target在任何文件/锁副作用前拒绝；旧Coordinator明确拒绝实际3，防止私有实验被旧v2成功hello包装。此守门只可由后续真实同版ready/握手整体替换，不用于伪造业务3。

实际212项新矩阵通过：新/旧Job层各实际DDL/claim-copy/swap/identity/提交边界的异常、取消、模拟磁盘及真实os._exit；完整旧库比较/重开、旧read/已完成atomic/queued jobs和精确重试、原四字段、不可变/缺失拒绝、唯一lease、公有身份及跨kind反例。后加6项入口测试通过，不重复212矩阵。独立全范围审查新矩阵+旧JobStore377 passed；入口定点6 passed/212 deselected，默认Coordinator/分页22 passed；ruff/格式/diff通过，无新增阻断，支持有界恢复提交。

本阶段未执行任务reconcile/canonical3/应用CAS/非Job receipt/完整恢复，不能称Job-ready。应用-only不推进domain、combined不能伪造jobId、receipt/claim/CAS/辅助不可洗白等仍须下一阶段真实实现；StageA当前只验domain/app genesis的validator亦须随之演进。指定外审/包内/真实公共3/PR/CI/合并/父功能门未关闭。新source尚未做完整全仓，保留本阶段精确验证范围。
