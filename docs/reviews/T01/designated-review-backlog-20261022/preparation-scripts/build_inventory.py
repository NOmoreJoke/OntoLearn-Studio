from pathlib import Path
import json, hashlib, subprocess, datetime
ROOT=Path('/Users/kyle/Documents/工作/知爻/本体'); OUT=Path('/tmp/t01-dual-review-backlog-20261022')
BASE='5f910b52c69d86a1076b2032e5d3c63e715947f3'; OWNER='01a15bba-0884-7401-b24f-f50c1fcf60aa'
TREES={k:ROOT/'.worktrees'/v for k,v in {'early':'T01-project-transactions','host':'T01-project-host-read-services','create':'T01-project-create-core','c2':'T01-operation-evidence-core','drain':'T01-dispatch-permanent-drain','s1':'T01-ontology-projection','producer':'T01-profile-job-artifact-selection','duplicate':'T01-project-host-contract-docs','offer':'T01-i05-semantic-resource-offer'}.items()}
def git(tree,*args):return subprocess.check_output(['git',*args],cwd=tree,text=True).strip()
def ref(s):return git(TREES['early'],'rev-parse',s) if s else None
def ident(p):
 b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def evidence(tree,name):
 p=TREES[tree]/name;assert p.is_file(),p;return ident(p)
rows=[]
def add(id,name,tree,product,process,kind,acceptance,internal,missing,next_action,successor=None,report=None,auth=None,notes=None):
 p=ref(product);q=ref(process)
 actual_delta=[]
 if p:
  actual_delta=[x for x in git(TREES[tree],'diff-tree','--no-commit-id','--name-only','-r',p).splitlines() if not x.startswith('docs/') and x!='AGENTS.md']
 ev=[evidence(tree,report)] if report else []
 if auth:
  a=ROOT/'iteration-control/2026-10-21-weekly-release'/auth;assert a.exists(),a;ev.append(ident(a))
 rows.append({'id':id,'stage':name,'kind':kind,'tree':str(TREES[tree]),'branch':git(TREES[tree],'branch','--show-current'),'integrationBase':BASE,'productRef':p,'processOrDocumentationRef':q,'originalOwner':OWNER,'writeBoundary':'T01 original phase-specific authorization only; actual commit delta below is evidence, not new write permission','actualProductCommitDeltaExcludingDocsAndAgents':actual_delta,'historicalAcceptanceEvidence':acceptance,'internalReview':internal,'specifiedReviews':{'zcode':{'actualTaskId':None,'actualSessionId':None,'actualTurnId':None,'actualSettings':None,'actualReport':None,'conclusion':'not-evidenced-in-local-stage-records'},'minimax':{'actualTaskId':None,'actualSessionId':None,'actualTurnId':None,'actualSettings':None,'actualReport':None,'conclusion':'not-evidenced-in-local-stage-records'}},'oldPassValidity':'No evidenced specified Pass to invalidate. Historical internal/test results bind only their original execution candidate; successor changes do not inherit them.','currentGaps':missing,'nextIndependentAction':next_action,'successorRelationship':successor,'evidence':ev,'notes':notes})
READY='可独立准备原固定候选的完整只读审查输入及历史覆盖映射；待root短桌面创建lease，不重跑未变验证，不把内部Pass当指定Pass。'
BLOCK='仍登记指定补审积压；可先封存实际源/全部历史缺口并准备只读提示，不能借补审运行DB/child/native或恢复被拒线；需要精确运行合同后再补正式验收。'
# Cumulative retained foundations.
entries=[
('E01','私有事务/Diff/受限undo/snapshot/易失草稿','03376dfb','03376dfb','64专项；fullcheck630TS/1116Py','2项内部P2关闭','完整域恢复、持久草稿、公开接线当时未做','E02','stage-one-review.md'),
('E02','完整域补偿/retirement墓碑恢复/operation_list','d9d7138f','d8985284','496相关专项；630TS/1196Py','7项内部意见关闭','尚非全项目恢复/Agent/正式产品','E06/E11后续同源码演进','stage-two-review.md'),
('E03','纯durable-draft CAS计划器','c5ba35b6','c5ba35b6','20专项；630TS/1216Py','Unicode P2修复内审关闭','无I/O，不证明真实持久并发','E06同连接CAS后继','draft-plan-review.md'),
('E04','Store3 StageA迁移/lease/备份/checkpoint/receipt','4858cf17','4858cf17','483专项/44不适用skip；630TS/1699Py/44skip','7类内审问题关闭；每DDL措辞后补','原每DDL4故障覆盖不足，后b902/f51dd补，不移用旧全仓绿','E05/E06','format3-stage-a-review.md'),
('E05','Job3 schema/claim迁移/逐DDL故障','b9027b16','b9027b16','初始212专项；另旧JobStore377/新入口6/默认Coordinator22；后补16故障','原claim CREATE/DROP/trigger覆盖缺口在f51dd补并独审','b902时无新fullcheck；以后继f51dd同候选证据为准','E06','job3-schema-review.md'),
('E06','真实应用CAS/combined/receipt/sequence','f51dd38d','f51dd38d','275专项；独立2+3/第二审20；630TS/2214Py/44skip','prepared跨类型P2修复关闭','learning/audit、完整application.restore、公共同版接线未开','E07/E10/E11累计后继','application-cas-review.md'),
('E07','原子不可变source内容缓存','ff98761a','33a55907','87专项/独立6；630TS/2301Py/44skip；E1后补原session2693/2697','内容同库完整性/intern内审通过','不认证授权/wire/parser/producer/GC/pin','后续source生命周期部分仍纯方案','source-content-review.md'),
('E08','显式business3 canonical validator','b35cb4e','b35cb4e','196TS/195Py专项；826TS/2496Py/44skip','独立validator-only审查；83断言子shell完整exit未封不可补造','当时actual3仍拒；fd/5de后改canonical，旧结果不覆盖新组合','E10/E11','business3-validator-independent-review.md'),
('E09','一次source-table捕获/预算材料编码','bf04169','27a0d171','126TS/132Py专项；952TS/2628Py/44skip；漏首P2反例另补1802B','两端整数预算P2-M1修复关闭','无parser/producer/source wire/runtime-ready，后canonical有变','E10/E11组合；取代撤回两遍patch','source-table-material-independent-review.md'),
('E10','authenticated startup/内部显式business3 readiness','fd3944a','fd3944a','17产品+8测试；1030TS/2706Py/44skip；unsigned包/5真实session9资源/worker原子Job重开/asar同源','startup P2及escapedpair闭合','真实Electron IPC/native/两OS/真人/正式业务未验；task-runtime旧单文件窗已关闭返I05','E11改canonical/coordinator/job_store','startup-implementation-independent-review.md'),
('E11','typed ChangeSet完整Diff/确认/Job/选择undo业务服务','5de3fff','427ba7da','1125TS/2789Py/44skip；sources12；新unsigned包/test_mode=False两session3Job；27os._exit/13authorizer','最终独审30586B无阻断；prepared双审输入尚非任务','真实I06选择/命名bridge/真人确认/Agent/来源producer/学习完整恢复未交','E12/E13固定原字节采用；producer为另组合WIP','changeset-business-service-independent-review.md')]
for i,n,p,q,a,v,g,s,r in entries:add(i,n,'early',p,q,'retained-implementation',a,v,g,READY,s,'docs/reviews/T01/'+r,notes='精确各历史阶段见status.md对应段；这些是历史证据，本轮不重跑。')
add('E12','有限catalog/workspace/draft宿主读取','host','a816c2d','3799162','retained-implementation','52新服务例；1125TS/2841Py/44skip，check04 session5551/chunk70ca9d exit0；sources原npm内exit未独立捕获，仅成功尾+stdlib12源核同','header4漏拒/游标复活两P2修复关闭','真实位置/native/current scope/Host/public create-resolution未交',READY,'48项5de→50项host→E13采用','docs/reviews/T01/project-host-read-services/independent-review.md','T01-project-host-read-services-implementation-authorization.md')
add('E13','C1内部原子空白项目创建','create','423b7e4','a33cc80','retained-implementation','128专项；1125TS/2969Py/44skip；verify12独立exit0；52产品测试+7docs','P2-C1-01旧domain receipt假借修复；事务/预算双内部审查通过','正式create_project_request/resolve_operation、I06物理库/dispatch/current_scope/首IO/UI/两OS未交',READY,'ba2c6c29采用50基础；后C2/dispatch/S1各取52；current c0b61后续仅方案','docs/reviews/T01/project-create-core-C1/independent-review.md','T01-project-create-core-C1-implementation-authorization.md')
# C2 and Node drain histories, all retained and mapped to current repair.
add('C2-0','C2初版operation evidence（采用资格已撤回）','c2','256b7f1','5b11875','historical-withdrawn-adoption','129专项；1125TS/3098Py/44skip；sources12','内部19044B五P2关闭，root曾限定收件','预扣前length/instr元数据扫描，root后撤可采用供方资格',BLOCK,'C2-1→C2-2；旧功能实跑/零写事实保留，不保资源前门Pass','docs/iterations/T01/project-operation-evidence-core-C2.md','T01-operation-evidence-C2-root-closure.md')
add('C2-1','C2 preprobe R1（真实反例，不通过）','c2','2c4257b','aa199fb','historical-failed-implementation','曾141专项/正常检查；后真实rowid alias/最终SELECT全扫描反例','独审不通过，旧首轮与反例保留','该版本不能倒写为通过',BLOCK,'0223d702修实现→ab792仅收窄旧canary断言，即C2-2','docs/reviews/T01/project-operation-evidence-core-C2/independent-preprobe-repair-review.md')
add('C2-2','当前C2 preprobe R2（物理HOLD）','c2','ab792c4','e118a66','retained-implementation-under-hold','160专项；1125TS/3129Py/44skip；sources12；300行原反例+42小例；早11项fee ledger缺失不补造','31297B/a4948d81独审具体PP问题关闭','physical payload/overflow cache先界仍缺；真实scope/dispatch/物理库绑定/公开resolution/56组合/两OS/真人/CI未验',BLOCK,'作者过程bef8e431；当前root仍HOLD，不恢复供方采用','docs/reviews/T01/project-operation-evidence-core-C2/preprobe-r2-delivery.md','T01-controller-C2-physical-overflow-cache-review.md')
add('D-1','Dispatch/permanent drain R1（131>130反例）','drain','04ed06a','4f270f0','historical-failed-implementation','1167TS/2969Py/44skip；42专项；真实旧ping+completion+新hello峰值131','独审14062B不通过，另同步stop/token取消缺口','原fullcheck不能覆盖R2',READY,'cd506d5修实现→7dfa最终product D-2','docs/reviews/T01/dispatch-and-permanent-drain/independent-implementation-review.md')
add('D-2','当前Dispatch/permanent drain内部机制','drain','7dfa9c8','8ecc37e','retained-implementation','1175TS/2969Py/44skip；50专项；sources12；真实Node子进程失败排空机制','25535B/8614f0d4内部R2定点通过，root限定收件','真实issuer/terminal producer/unknown Job发现/Store-worker-native-VFS-cohort/首IO/目标OS真人CI未闭',READY,'e79d9d4采用52基础；作者process009e947→最终8ecc；无当前机制撤回','docs/reviews/T01/dispatch-and-permanent-drain/final-delivery.md','T01-dispatch-permanent-drain-implementation-authorization.md')
for id,name,auth,facts in [
('S1-0','Ontology S1 portable平方UTF16早期试作','T01-ontology-projection-S1-implementation-authorization.md','UTF8正常，UTF16两编码正文前拒；旧4690374B/435697 ledger被覆盖，不重建'),
('S1-1','Ontology S1线性UTF16算法试作','T01-ontology-S1-UTF16-probe-algorithm-window.md','913f2521控制窗；proposal只读设计/后续物理前界补正，非采用'),
('S1-2','Ontology S1完整行上界/缓存试作','T01-S1-bounded-row-cache-prepayment-trial.md','cded41a0控制窗，原两writer/cap，无固定产品候选'),
('S1-3','Ontology S1 fused同cursor保留WIP','T01-S1-fused-row-prepayment-trial.md','f14deda0控制窗；103pass原run从未落完整账，不绑定当前WIP为全通过')]:
 add(id,name,'s1',None,None,'retained-uncommitted-trial',facts,'9939B/e79f4953独审明确尚无固定算法+完整54，不给通过','仅adoption3f5fe151；当前两个writer未跟踪；完整费用/算法上界/清理及最终内审缺；damagedHOLD/平台拒绝禁止续试',BLOCK,'S1-0→S1-1→S1-2→S1-3尝试链；不是版本已通过链','docs/reviews/T01/ontology-projection-S1/independent-implementation-review.md',auth,notes='product/process commit均不存在；当前两WIP身份另列，不冒认每个历史执行源的哈希。')
# Producer current WIP, split by actual technical slice, one shared packet.
producer=[
('P1','private v3定义预演/Diff/确认/补偿scope','133pass/5.83s=132旧默认+1纯predicate；原执行domain/transactions/storage同当前','29816B/0abf5a85，DC01/02/04及resolved DC03静态关闭','真实profile DB确认/commit/rollback/undo/重开未验；jobs/Coordinator后变，133非当前整链','definition-confirmation-prereview.md','原blanket compensation被收窄边界替代'),
('P2','prospective catalog/四表DDL角色约束','08仅两catalog/provider unit 2pass/.09s；identity exit0','15753B/3b9e8c49，CR01 NUL反例静态关闭','DDL三编码/FK/trigger/安装/迁移重开均未运行；prospective不是installed','catalog-role-constraints-prereview.md','42954/4b5151→43040/07e；07含parent capture的scope误记/外置纠正保持'),
('P3','角色codec/provider resolver/actual capture decode','原11role/wait、82R5为历史实跑；当前08仅两metadata unit','18990B/69252508，RC01/02/03及key界局部关闭','需获准bounded SQL reader；packaged resolver未组合；旧39554完整文件后变','role-codec-prereview.md','旧codec切点可引用，但旧整文件内审不覆盖当前43040'),
('P4','Budget/真实snapshot material','作者38项和独立边界原件；当前四文件同R3','35141B/8b072ad3，H01/H02仅一次完整阶段control合同闭合','worker对象16777216计数仍违每actor8388608计数；同库objects/跨Job真实actor绑定未实现；不能机械减票','independent-helper-prereview.md','R1无界/R2可变export/control问题保持；R3仅helper子集'),
('P5','private rows→display/cache key adapter','193历史联跑覆盖该两文件，当前两文件同该轮','未检出该adapter单独完整实质内审报告，不能借budget/material审查代替','尚无Store publish/get/page/current/GC/typed origin持久化；优先补该adapter实质内审','independent-helper-prereview.md','193所含worker/jobs后来变，不能称当前全套通过'),
('P6','Coordinator owner/取消/UNKNOWN/CL07','214旧路径兼容/4.59s；当前Coordinator同执行源','41985B/24c9cd3a，CL07具体反例静态关闭；CL05/06历史修复保持','launch/pending_calls/bootstrap stderr/UNKNOWN恢复/Store六接口与整链缺','coordinator-lifecycle-prereview.md','R4 CL07→R5；214包其它helper后来变，不冒新profile运行验收'),
('P7','worker frame/owned channel/known-process有限失败清理','最终06 96pass/3.99s，31 child当时终态；当前worker/test同该源；06 jobs后变DDL','frame21379B/e7cfa973绑旧25897；closure38178B/b768738a对当前WC01/WC02/WC02-Q定点关闭','whole-H<=8388608对象计数/启动未知/导入输出/实际actor-library及别名未闭；不启动新child','worker-closure-prereview.md','193绑40486/e0d8，32错binding反例后被40488/d049替代；原失败缺账/PID None不回填')]
for id,name,a,v,g,r,s in producer:add(id,name,'producer',None,None,'retained-uncommitted-implementation',a,v,g,BLOCK,s,'docs/reviews/T01/profile-producer-first-window/'+r,'T01-profile-producer-first-source-window.md',notes='同一当前149源packet，adoption b054仅139固定输入；7旧writer+10新源/tests未提交；双指定任务均未检出。P1–P7可在同一完整只读packet逐阶段审，避免重叠后台任务。')
add('P8','真实Store producer受理/成功事务/BLOB reader-GC/重开','producer',None,None,'not-implemented-parent-slice','六方法实际AST未实现；仅Coordinator调用/codec/DDL，不能填产品SHA','仅接口/生命周期契约内审，不是实现通过','create_profile_job/profile_budget/profile_context_fingerprint/profile_input_roles/finish_profile_read_job/profile_failed_owner均缺；准入/wholeH/owner前置未闭',BLOCK,'保留原完整实现待办，不永久排除，不以P1–P7替代','docs/iterations/T01/profile-producer-first-window.md')
# Non-implementation designs and preserved withdrawal, explicitly distinguished.
plans=[
('N01','format3 foundation/owner接口方案','early','0a2a4372','docs/iterations/T01/format3-foundation-contract.md','format3-contract-review.md','5项设计缺口方案层关闭','E04/E05/E06'),
('N02','source transport/lifecycle/learning/digest合同组','early','2c120385','docs/iterations/T01/source-lifecycle-decisions-r4.md','follow-up-design-review.md','内部设计及table-capture设计审；未证明所有后续writer已实施','E07只内容缓存、E09只一次捕获；wire/pin/learning尚缺'),
('N03','startup/ready r1-r3与实施计划','early','79d6bc49','docs/iterations/T01/business3-ready-startup-contract-r3.md','business3-ready-startup-design-review.md','独立设计审，r1-r3与原RAW1024问题保留','E10为具体后继，E11再改canonical'),
('N04','typed ChangeSet实施方案','early','f51a9e10','docs/iterations/T01/changeset-business-service-implementation-plan.md','changeset-business-service-plan-review.md','首轮3P2与后续修订关闭；初稿dafe409原件保留','E11=5de3实现'),
('N05','Host下一接线方案','early','427ba7da','docs/iterations/T01/project-host-integration-next-plan.md','project-host-integration-next-plan/independent-review.md','独立纯方案审；没有自动main/preload/App/worker写权','E12只有限读取，不等完整Host方案'),
('N06','创建/resolution正式合同','host','3799162','docs/iterations/T01/project-create-and-resolution-contract.md','project-host-read-services/creation-resolution-independent-review.md','物理dispatch归因与4096→4178 metadata两P2在合同层关闭','E13仅blank创建，正式resolution尚缺；duplicate树同原bytes'),
('N07','C2实施/预算方案','create','0a03539','docs/iterations/T01/project-operation-evidence-core-C2-plan.md','project-operation-evidence-core-C2-plan/independent-plan-review.md','独立plan+budget调查；仅静态','C2-0→C2-1→C2-2'),
('N08','dispatch/permanent drain方案R1/R2','create','506e157','docs/iterations/T01/dispatch-and-permanent-drain-plan.md','dispatch-and-permanent-drain-plan/independent-plan-review.md','R2方案Pass，首轮待修保持；非运行Pass','D-1→D-2'),
('N09','ontology S1→M→S2供方方案','create','7753666','docs/iterations/T01/ontology-projection-and-changeset-supplier-plan.md','ontology-projection-and-changeset-supplier-plan/independent-plan-review.md','81538B主稿/23030B独审，r3方案Pass；3P2和控制问题仅设计闭合','S1 WIP；M/S2并非已实现'),
('N10','I05 profile Job/artifact/selection供方方案','create','c0b61fd','docs/iterations/T01/profile-job-artifact-selection-supplier-plan.md','profile-job-artifact-selection-supplier-plan/independent-plan-review.md','78754B主稿/31608B独审，PS01/02仅方案关闭','P1–P8；consumer/selected仍未实现')]
for id,n,t,q,main,r,v,s in plans:
 add(id,n,t,None,q,'non-implementation-design','只有静态文档；不填实现/产品Pass',v,'无可核指定两模型实际任务/设置/报告；方案包含未实施范围','登记纯方案审查范围和原内审/后继映射；可独立准备文档双审输入，实际创建待root短lease，不把文档Pass充作实现。',s,'docs/reviews/T01/'+r)
 rows[-1]['mainDocument']=evidence(t,main)
add('W01','撤回两遍source-table helper准备patch','early',None,'064f27aa','withdrawn-unfinished-patch','仅typecheck/ruff初步；45golden草稿未实际跑','准备notes明确不可采用；原patch SHA256 ffdde792d12ed63705dc715e005cf7574af261dbfdc6b3cd487c2c48712c5845 保留','两遍读取不符合后来一次capture合同；无产品验收/指定Pass','保留撤回原件并随E09输入说明其被替代；不重新运行撤回patch','449a05f保存patch；产品恢复b35；后继bf041=E09','docs/iterations/T01/source-table-material-preparation-notes.md')
add('N11','worker drain budget只读设计','producer',None,None,'non-implementation-design','14506B/aa171836；历史25135/97eaf输入','未检出独立定稿Pass；后继closure内部审只覆盖部分实现','没有指定Pass，也不是whole-H上界','作为P7历史设计输入补只读双审，明确未实现/未证明部分','部分known-process已由P7实现','docs/reviews/T01/profile-producer-first-window/worker-drain-budget-design.md')
add('N12','T01 whole-worker对象界分析/I05分量交接','producer',None,None,'non-implementation-analysis','当前17306B/2b4d55fe，原13392前缀保持；I05固定7f99文档交接','T01作者分析不是独立Pass；I052687B独立文档审仅供方U分量','whole H未闭，root不批准部分envelope writer；不能研究被拒SQLite/heap线','登记静态分析/责任分工待审；不为凑ready签H或降低票','I05文档7f99非本线产品；HOLD仍开放','docs/reviews/T01/profile-producer-first-window/worker-object-bound-analysis.md')
add('N13','C2/S1物理输入域与资源合同选项（root所有）','producer',None,None,'root-owned-non-implementation-policy','root选项报告16251B/f296b970；用户2026-10-22保留损坏保护HOLD','root只读选项审；不代T01实现或指定模型','A不采用，B/C未授，被拒线继续停止','登记外部依赖和禁止重启边界；只在root具体新合同/窗口后实施','不能以桌面政策或补双审授权解HOLD',auth='T01-controller-physical-resource-contract-options-review.md')
rows[-1]['originalOwner']='root controller; T01 dependency only'
add('N14','I05四共享资源私有只读owner offer','offer',None,'79d63cc1','non-implementation-owner-offer','受审dd972 53件；最终79d63 71件/1448654B；17原件完整；formatter纠正有全记录','R1最终格式不通过9884B；R2限定Pass7069B/9cb6f568，root限定收件','没有两指定模型实际任务；纯静态接收不等构建/运行/维护权转移','纯文档材料已固定，可准备完整静态双审提示并待root短lease；不回写旧71件manifest','4064→4709不完整→dd972受审→79d63过程；原Goal保持blocked','docs/reviews/T01/i05-semantic-resource-offer/independent/round-2.md','T01-i05-resource-offer-root-closure-and-adoption.md')
add('N15','创建合同重复保留树（非另一个实现）','duplicate',None,None,'duplicate-retained-document','当前39602B/ff725f2c与3799162正式合同逐bytes相同；HEAD5f，文件untracked','复用正式N06独立合同审，不伪造该重复树有独立指定审查','无产品/process commit；不重复算一次实现','将此副本位置映射N06审查覆盖，保留原件；不是永久排除业务范围','N06正式合同是精确后继/规范来源','docs/iterations/T01/project-create-and-resolution-contract.md')
add('FULL','T01完整父功能/集成/指定双审/发布','producer',None,None,'uncompleted-parent-goal','原FR001–006 P0和FR804完整范围保持；当前仅分散内部实现/WIP证据','各内部阶段不代父验收','无完整同版真实Store/项目/事务/撤销/快照/草稿缓存/Host/producer/Agent闭环、wholeH/物理owner、两OS真人/CI/PR/合并证据','先按所有保留实现分批补静态指定审查；完整真实依赖/唯一owner合同就绪后继续原Goal，不以任一子阶段缩减完成条件','全部E/C2/D/S1/P/N记录均保留，不因当前不ready而删除')
# Explicit authorized writer surfaces, separate from observed commit deltas.
AUTHROOT=ROOT/'iteration-control/2026-10-21-weekly-release'
AUTHMAP={
'E09':'T01-table-material-phase-authorization.md',
'E10':'T01-startup-implementation-phase-authorization.md',
'E11':'T01-changeset-business-service-implementation-authorization.md',
'E12':'T01-project-host-read-services-implementation-authorization.md',
'E13':'T01-project-create-core-C1-implementation-authorization.md',
'C2-0':'T01-operation-evidence-C2-implementation-authorization.md',
'C2-1':'T01-operation-evidence-C2-implementation-authorization.md',
'C2-2':'T01-operation-evidence-C2-implementation-authorization.md',
'D-1':'T01-dispatch-permanent-drain-implementation-authorization.md',
'D-2':'T01-dispatch-permanent-drain-implementation-authorization.md'}
AUTHORFIELDS={
'E12':['packages/engine/src/ontolearn_engine/project/project_host.py','packages/engine/tests/test_project_host_read_services.py'],
'E13':['packages/engine/src/ontolearn_engine/project/project_lifecycle.py','packages/engine/src/ontolearn_engine/storage.py','packages/engine/src/ontolearn_engine/job_store.py','packages/engine/src/ontolearn_engine/project/format3.py','packages/engine/tests/test_project_create_contract.py']}
for row in rows:
 rid=row['id']
 if rid in AUTHMAP:
  proof=ident(AUTHROOT/AUTHMAP[rid])
  if proof['path'] not in [e['path'] for e in row['evidence']]:row['evidence'].append(proof)
  row['authorizationSource']=proof
  row['authorizedProductTestWriters']=AUTHORFIELDS.get(rid,row['actualProductCommitDeltaExcludingDocsAndAgents'])
  row['writeBoundary']='原owner T01；精确授权文件与产品/test writer如下；继承候选其余路径只读，当前盘点/补审不重开产品写窗。'
 elif rid.startswith('S1-'):
  row['authorizedProductTestWriters']=['packages/engine/src/ontolearn_engine/project/ontology_projection.py','packages/engine/tests/test_project_ontology_projection.py']
  row['writeBoundary']='T01原S1仅两新增writer；采用52全只读；trial窗不是新产品范围；当前物理HOLD与禁止续试保持。'
 elif rid.startswith('P') and rid!='P8':
  row['writeBoundary']='T01原producer七旧writer+五新源码+五新测试；其余132固定项只读；精确17路径在wipIdentities.producer.controlled17；当前只发审不修改。'
 elif rid.startswith('N') or rid in ['W01','FULL']:
  row['writeBoundary']='文档/分析或未实施范围；本条不产生产品writer权限；保留源树与原方案边界。'
 else:
  row['authorizedProductTestWriters']=None
  row['writeBoundary']='原T01阶段实现；已列实际commit路径和阶段报告，但本次未定位早期逐路径授权原件，不能把commit delta冒充授权；共享维护权须按当前owner核。'
 if rid in ['E10','E11','E12','E13','C2-0','C2-1','C2-2','D-1','D-2']:
  row['ownershipCaveat']='tests/unit/task-runtime.test.ts历史单文件窗2026-10-21T14:04:13.952488+08已关闭返I05；固定旧字节仅采用输入，不授T01当前维护权。'

# Precise uncommitted identities, never HEAD-as-product.
s1=[ident(TREES['s1']/p) for p in ['packages/engine/src/ontolearn_engine/project/ontology_projection.py','packages/engine/tests/test_project_ontology_projection.py']]
fixed=json.loads((TREES['producer']/'docs/reviews/T01/profile-producer-first-window/inputs/fixed-inputs.json.raw').read_bytes())
paths=sorted([i['path'] for i in fixed['files']]+[i['path'] for i in fixed['newFiles']]);assert len(paths)==149
packet=[dict(path=p,bytes=(TREES['producer']/p).stat().st_size,sha256=hashlib.sha256((TREES['producer']/p).read_bytes()).hexdigest()) for p in paths]
pkt_digest=hashlib.sha256(json.dumps(packet,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();assert pkt_digest=='b8083903857c92b63cc8256038af2cc7cb52fb92532cc1353a6127cd37397b10'
controlled=set(fixed['existingWriterPaths'])|{i['path'] for i in fixed['newFiles']};assert len(controlled)==17
inventory={'generatedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'businessDate':'2026-10-22','purpose':'All retained T01 implementation/technical-stage specified dual-review backlog, including unready/WIP/withdrawn/pure designs; no tasks created or implementation restarted','base':BASE,'owner':OWNER,'scopeSearchLimit':'Nine T01 worktrees existing stage docs/Git/accepted input metadata plus root T01 task/closure records. No global application database/session search; absence of local evidence is not a claim that no task ever existed anywhere.','expectedSettingsOnly':{'zcode':'GLM-5.3/highest thought; yolo/full access; actual task readback required','minimax':'M3.1-Flash/xhigh; bypassPermissions/full access; actual task readback required'},'globalSpecifiedReviewObservation':'No retained T01 stage has a verifiable pair of specified task/session/turn IDs, per-task settings and final reports in examined records; all actual fields are null, no specified Pass claimed. Internal agents/tests/root receipts are distinct.','policy':{'originalGoal':'blocked, unchanged','damagedInputProtection':'HOLD retained; A not chosen; B/C not authorized; rejected SQLite/heap/OS line remains stopped','desktop':'Silent restriction withdrawn; root short foreground creation/settings lease required for this line; do not recreate T06 or compete with current leased app','changedImplementationRequires':'Original unique owner repairs; necessary validation and both new same-candidate specified reviews; old Pass not carried forward','inventoryOnly':'No product/tests/DB/native/GUI/child executed, no sources/manifests modified, no model task started'},'currentTrees':[{'key':k,'tree':str(v),'branch':git(v,'branch','--show-current'),'head':git(v,'rev-parse','HEAD'),'stagingEmpty':not bool(git(v,'diff','--cached','--name-only')),'trackedStatus':git(v,'status','--short','--untracked-files=no')} for k,v in TREES.items()],'wipIdentities':{'ontologyS1':{'adoptionOnlyRef':ref('3f5fe151'),'productRef':None,'processRef':None,'files':s1},'producer':{'adoptionOnlyRef':ref('b054b2cd'),'supplier':ref('6c1eec41'),'productRef':None,'processRef':None,'packet149Count':149,'packet149Bytes':sum(i['bytes'] for i in packet),'packet149CanonicalSha256':pkt_digest,'packet149':packet,'controlled17':[i for i in packet if i['path'] in controlled],'readonly132':'Separate agent checked unchanged approved adoption bytes; no authority to edit'}},'stages':rows,'reviewBatchSuggestionsNotActualTasks':[{'batch':'C1-cumulative','scope':'E01-E13 plus their absorbed design histories','candidate':ref('423b7e4'),'process':ref('a33cc80'),'boundary':'Use full52 approved inputs, not just5 writer diff; explicitly map each earlier fixed candidate/test limitations; root decides exact grouping to avoid redundant overlapping tasks'},{'batch':'C2-current','scope':'C2-0/1/2 and N07, preserved failure/withdrawal history','candidate':ref('ab792c4'),'process':ref('e118a66'),'boundary':'Static source review includes physical HOLD; does not restore reader runtime permission'},{'batch':'dispatch-current','scope':'D1/D2/N08 full54 inputs','candidate':ref('7dfa9c8'),'process':ref('8ecc37e'),'boundary':'Internal mechanism only; retain missing real producer/native facts'},{'batch':'ontology-WIP','scope':'S1-0..3/N09','candidate':None,'boundary':'Exact retained WIP snapshot first; no invented commit or replay of lost ledgers; static review may return cannot-verify/not-pass'},{'batch':'producer-WIP','scope':'P1-P7/N10-N12 plus P8 unimplemented scope explicitly disclosed','candidate':None,'packetSha256':pkt_digest,'boundary':'One complete149 snapshot with each substage marked; first fill missing adapter internal audit; no new child/DB or mechanical cap reduction'},{'batch':'remaining-designs','scope':'Nonimplementation N rows not absorbed by an implementation review, including N14 fixed owner offer','boundary':'Explicit document scope and internal-review limitations; document Pass never implementation Pass'},{'batch':'full-parent','scope':'FULL original Goal','candidate':None,'boundary':'Remains on backlog; needs complete actual integrated implementation/acceptance, not service-stage substitution'}]}
(OUT/'backlog.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n')
(OUT/'source-evidence-manifest.json').write_text(json.dumps({'scope':'Current documentary evidence read by inventory contributors; not new product execution','files':sorted({e['path']:e for row in rows for e in row['evidence']+([row['mainDocument']] if 'mainDocument' in row else [])}.values(),key=lambda e:e['path'])},ensure_ascii=False,indent=2)+'\n')
lines=['# T01 全量指定双审积压盘点','', '2026-10-22。仅事实盘点，不重启任何Goal/候选或指定模型任务。范围覆盖九个T01保留工作树，包括历史失败/撤回、未提交WIP、未实现父范围和纯方案。','', '**当前未检出可绑定本线任一阶段的两指定模型真实任务ID、逐任务设置及完整终态报告。** 每项实际ID/settings/report均在JSON登记null；GLM-5.3/最高和M3.1-Flash/xhigh是要求，不是实际设置。此为本地阶段材料与root T01记录的证据边界，不是全平台“从未创建”证明。','', '原始历史内部Pass/全仓测试只绑定当时source；后继修改不继承。没有已证指定Pass可被宣称仍有效或已失效。旧撤回及精确后继逐行保留。','', '## 各阶段','', '| ID | 阶段 | 类别 | product / process或文档ref | 原验收/内审边界 | 当前缺口与下一步 |','| --- | --- | --- | --- | --- | --- |']
for row in rows:
 refs=(row['productRef'][:12] if row['productRef'] else '无产品提交')+' / '+(row['processOrDocumentationRef'][:12] if row['processOrDocumentationRef'] else '无过程提交')
 vals=[row['id'],row['stage'],row['kind'],refs,row['historicalAcceptanceEvidence']+'；'+row['internalReview'],row['currentGaps']+'；'+row['nextIndependentAction']]
 lines.append('| '+' | '.join(v.replace('|','/').replace('\n',' ') for v in vals)+' |')
lines += ['', '## 固定状态与准确来源','', f'- 共{len(rows)}项记录；完整40位refs、原owner/实际源改动、报告绝对路径/bytes/SHA、验收缺口、后继关系和下一行动见 `backlog.json`。实际commit delta只证明改过哪些文件，不取代或扩大原授权。', '- producer HEAD b054仅139固定输入采用；当前17受控源/tests未提交。149件7788249B canonical清单SHA `'+pkt_digest+'`。S1 HEAD3f5仅52采用，两WIP原件hash另列；不伪造product SHA。', '- N14四资源offer为非实现：受审dd972/过程79d63，内部R1因格式不通过、R2限定Pass、root限定收件；仍没有指定模型Pass。', '- N15重复合同当前39602B，与379正式版本逐bytes相同，映射N06；不重复算新实现，也不抹去保留原件。', '- 本轮仅Git/文件/stdlib JSON/hash和既有文档读取，不运行产品、测试、DB/SQL、native、业务child、GUI或指定审查应用。冻结材料/旧manifest完全未改。', '- 桌面偏好已撤回；本线创建审查任务仍等待root短lease，不占T06/T02等既有后台推理。原damaged-input HOLD、whole-H/owner门和物理Goal blocked均保持。', '', '## 建议的补审批次（不是实际新任务）','']
for b in inventory['reviewBatchSuggestionsNotActualTasks']:lines.append('- '+b['batch']+'：'+b['scope']+'。'+b['boundary'])
lines += ['', '盘点不删除未ready项、不把纯设计审作实现Pass、不以内部收口降低57P0/原完整验收/指定双审/CI/两OS/真人/远端门。', '']
(OUT/'backlog.md').write_text('\n'.join(lines))
print(json.dumps({'rows':len(rows),'kindCounts':{k:sum(r['kind']==k for r in rows) for k in sorted(set(r['kind'] for r in rows))},'files':[ident(OUT/n) for n in ['backlog.json','backlog.md','source-evidence-manifest.json']]},ensure_ascii=False))
