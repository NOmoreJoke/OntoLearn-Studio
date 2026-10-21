# T05：按原child限额的纯批次复核实施授权

2026-10-21。原T05会话 `01a15bce-021c-74e0-a7ac-a899380b424a` 可实施独立纯模块；不授权I05正式消费、selected保存读回或T01持久接线。原Goal不重建/伪恢复，原两个T05树和全部固定历史保持。

## 固定依据与实际新树

根全文读固定 `330fcedb297792e0addd55557688509550c3b26a` 的32769B提案/SHA `e5fefefd78f62b4b5c989acd02aba6dc227042a3517fe3d90dc23bc0e3bae750`、12853B供方独审，以及根独审原17078B和完整追加。根报告现26970B/SHA `0616717d7c1b85d822cccdd646ae659066bf10b31f864cb16938b6c96354b4be`，结论无独立pure三路径算法/预算阻断。17docs固定Git=current，13成员bundle安全/完整、原件已根快照。旧c1a默认三池不采用。

为遵守从批准develop开分支并避免整份私有提交，核空后在 `.worktrees/T05-profile-revalidation` 新建 `feature/weekly-t05-profile-revalidation`，实际Git base/初始HEAD为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`；根本轮ls-remote仍核该develop。只按 `T05-batch-revalidation-approved-base-inputs.json`（5994B/SHA `d5486d92359fae36363dcf01270394f31e15a92ba16a614a0ba62b2baa621461`）逐项从已根收口 `dbb6b36e9259aa79a1fd908b5cfede3064f0c074` 采用21份固定原字节，随后只读保护；不whole-commit，不复制其他私有代码/配置/证据或可变环境。

21份为原20中19不变、新6176B terms及新IRI边界测试；旧七模块身份以新七清单为准。包root缺失旧definitions/planning仍不可调用，不借lazy入口复制旧实现。带入最新AGENTS78df/common e437并全文读取，保护规则不stage。依赖/venv/cache/build/log/临时数据在新树独立，原5f依赖/锁不变，不能复制C4或他树环境。未知已有目录不覆盖。

## 唯一新写路径与私有算法

除21份精确采用外，产品/测试/夹具只能新增：

1. `packages/engine/src/ontolearn_engine/quality/rule_revalidation.py`。
2. `packages/engine/tests/test_quality_profile_revalidation.py`。
3. `tests/fixtures/quality/profile-revalidation-v1/cases.json`。

可新增一份 `docs/iterations/T05/rule-batch-revalidation.md` 及 `docs/reviews/T05/rule-batch-revalidation-implementation/` 的实施/原件/独审证据。21原件不得重写，不能改package root导出、旧机制/旧API/PROFILE/旧Budget、依赖/锁/构建/loader、公共schema/Store/worker/I05/desktop/CI。额外必要路径先给实际反例与最小申请。

严格实现330f的keyword-only可信原 `limits: ProfileLimits` 与 `disabled: bool`、保存batch或None、返回 `batch-consistent` / `definition-only`，新私有 `mechanism-revalidation-budget/2`。limits逐固定字段exact int/非bool/0到旧默认校验并复制冻结；三个池各用同一原child上限，控制池按K_i预扣，无深层预扫/第二轮隐藏guard/逐组reset/借池。完整原序false/true matches和bindings/when/proof/source不丢失，fresh compile一次、evaluate一次；保存typed编码一次，精确两payload连接边和digest/profile比较，再付费核完整比较operand发行。只认当前canonical模块真实parse发行，不认字段/自报digest或跨模块伪造。

disabled或原无batch空定义按提案仅有界compile，不能制造空成功batch；非空enabled无保存batch失败。成功蕴含只对相同原输入/顺序/原L_i及完整正确当前发行成立。dbb新增准入Unicode须dbb同版生产→复核，不借1e3的旧成功。IRI谓词变化不改变旧debit/typed编码/签发政策，不声称CPU/内存相同。

## 实测、审查与交付

真实执行source40000完整见证：原compile+evaluate成功、旧同池逐组资源失败、新按同原限额批次成功，记录完整输入/预期及各池实际usage，不能把静态字节算式当运行。覆盖多规则/组/head/source/proof、原bindings顺序/false后项错误、tight limits/三池/control耗尽、伪造/后项篡改/全部连接边、disabled/空定义/真实空batch、原子失败及安全错误；预期手工推导，不从actual生成golden，不引用独立oracle输出作计算。

T05纯模块只验数值shape和一次分配成本，不能识别“来自JSON但数值合法”的真实限额来源；该来源/账本拒绝测试属于以后I05入口。多child/N100的纯算式或synthetic账本测试必须标明机制层，不冒称I05真实allocator、重试或跨child已接线。真实整次界为3ΣW_i+ΣK_i /2ΣI_i /2ΣO_i，未证明ΣF_i时不偷换全局F，disabled/失败/重试不能凭测试另发默认池。

完成新候选的受影响旧机制/IRI回归、正常 `npm run check`、必要source检查和独立代码/逐操作预算审查，保首失败/原argv/完整stdout-stderr/实际exit与旧成功→新复核原件。固定候选明确相对5f是21精确采用+3新增，不能谎称整个Git diff仅3路径；逐21固定Git/manifest/归档核同，三新增另列实际bytes/hash/patch，审查冻结后不改。新模块仅源码可用不冒称包内已包含，实际I05组合/T03 D2新包门后补。

## 消费前置继续保留

330f§7四项事实已答，当前只批准独立纯模块，不要求整个父模块先完成。I05原tuple载体/可信原分配账本、严格保存JSON恢复/逐字段重发行与独立整次R/缓存/hash/投影成本、T01真实成功producer/项目快照/定义来源/权限/保存窗口/撤回GC仍约束正式消费与selected；当前均未因本授权通过。纯模块不得增加恢复器/长期载体/Job或制造权限。

本轮无本机GUI/Electron/e2e/native/HMR/审查应用，不push/PR/merge。完整父范围、同版两个指定模型新审、意见闭合、CI及正常develop合并/远端核验门不变。交回固定候选/原件并等根核验后，才另决定精确消费，不将本实施许可记作运行或父验收通过。
