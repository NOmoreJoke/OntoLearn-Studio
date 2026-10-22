# builder／entrypoint 局部差异复核

结论：**TWO_PATH_DELTA_PASS_ONLY，F1/P3 已关闭；N1 的 reader 显式可达性已补齐，实际 PYZ 仍未验证。** 04 轮 root 单元的前置不足已在本次复核中指出，owner 以 05 新轮次补齐源目录后通过；04 原日志和首审均保留。此报告限两路径，不签四路径完整候选或实际打包/runtime/parity。

## 04 首读输入与保留

| 工件                                                 | bytes | SHA-256                                                          |
| ---------------------------------------------------- | ----: | ---------------------------------------------------------------- |
| 首审 JS 原样副本 builder-first-review-source.mjs.raw |  8298 | 94a37649cd2471b7140bd6277968aac610bc4d276554a52894b07e24ee8c7238 |
| 当前 scripts/build-engine.mjs                        |  8437 | 738f55ef056c3326f812ab9e4ed272a11a332a21a23a78c72fd07b510d31a8ff |
| packages/engine/entrypoint.py                        |   976 | aaf9f85b59f115ae0646fd31f5305ee588c2bd58a0fbb28d9714c707c9035ef3 |
| 首审 builder-entrypoint-independent-review.md        |  6817 | ae540f4fded6aa22c86eb054349ff0d15325f5cabef45de92baa296ea59de729 |
| builder-private-unit.mjs                             |  8330 | 4077d4372ed4cf5c2b2299981e635926e4eb216af739992d83f8e57ee27cde73 |
| 04-builder-unit-root-guard.stdout                    |   954 | f393deee220b77b2377c8c2f2403e3ba17fa27bc10e65285b6b4322788aad4ab |
| 04-builder-unit-root-guard.stderr                    |     0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |

原首审、首 JS 副本与入口均未覆盖；当前 JS 与首副本的实际 diff 仅为下面两项修订。本轮全文读取该 diff、当前局部路径及 144 行 Node 单元源码、两份输出；原合同沿固定 36587B/9d97 版本。未读取另一 agent 的 Python 模块或测试 WIP。

## F1/P3：产品修复静态关闭

`publishEngineCopy` 在访问 `isAbsolute` 或路径祖先循环前，现先要求 root 是 string，再要求 `root === resolve(root)`。因此带 `/.`、重复分隔等非规范绝对字符串会在循环前以固定 `BUILD_ENGINE_ARTIFACT_PATH_INVALID` 拒绝，不再满足“规范 source 祖先永不等于非规范 root”的反例前提。

该修复局部，不改变 `buildEngine` 原先规范化 root 的正常链，也不新增路径 CLI。首审的原输入、问题等级及其“默认 buildEngine 不受该独立 helper 反例影响”的范围判断保持原样，没有将首报告改签为当前文件。

## N1：显式 reader 引入已补，但不等于实际入包

新加字面 `--hidden-import ontolearn_engine.semantic_build_provenance`，与已有 anchor hidden-import 并存。因此当前 builder 的 reader 收集请求不再依赖未来 I05 probe 静态 import 可达性，也没有用 collect-data 代替 Python 模块收集。

owner 的第一项 Node 单元实际断言该 hidden-import argv，并核八 collect-all/metadata、optimize0 与唯一 run 路径。然而其 subprocess 为 stub、artifact 为 synthetic 内容；没有运行 PyInstaller 或 inspect 实际 PYZ。N1 的声明/可达性缺口已处理，reader 是否实际进入正确 PYZ、源指纹与 loader 是否匹配，仍必须由真实 finalize 和后续完整候选证据确认。

## U1：04 首轮单元不足（历史问题，后由 05 补证关闭）

本轮 stdout 显示 10 tests / 10 pass / 0 fail / 0 skip，stderr 为 0B；其中含预期 prepare-failure marker。owner 报告命令 exit0。前九项使用 stub subprocess 配合真实临时目录/文件，覆盖失败不发布、旧 stage 与 unique source/binding 保留、rename rollback、错误 helper 路径、重复 UUID 和 dangling/source symlink 拒绝。这些是构建编排/文件操作单元，不是真实 Python helper 或 PyInstaller 成功证据。

第十项确实用独立 Node child、2000ms timeout 和真实导入当前 JS，传入 `f.root+'/. '` 的无空格形式 `f.root+'/.'`，断言固定拒绝码及 child status0、无 timeout。但是 `fixture(t)` 此时仅创建 `f.root`；并未创建 `f.engine` 或其 dist/runRoot 祖先。

因此，旧未修 JS 也会在祖先遍历第一步 `lstat(engineDirectory)` 得到 ENOENT，并抛出同一固定拒绝码，测试同样通过。其现有输出不能证明已覆盖首审中“engineDirectory 及所有祖先都存在，最终循环在 `/` 停不下来”的完整反例。这个证据缺口不否定上面的产品静态修复，但应补回归前置。

最小修改仅需在 child 启动前创建 `f.engine` 及全部祖先（例如 recursive mkdir），继续保留同一 2s 独立 child 上界与固定拒绝断言，再留一个新输出轮次；不覆盖 04 原日志。这样旧源码的既有路径不会因 ENOENT 提前拒绝，测试才能区分原反例。此项已发回 owner，本 reviewer 没有代改或重跑。

## 限定结论

本次仅新写本差异报告并格式化；未安装、执行 builder、engine、pytest、GUI、native 或 parity，未改产品、原报告、原日志或另一 agent WIP。当前两产品 delta 无新的静态阻断发现；U1 后续 05 补证见下，已关闭。四路径最终实现、实际 PYZ/loader/native、root 外部 binding 预冻结与完整 CLI 对照仍开放，不从 Node stub 单元外推。

## 05 追加复核：补齐真实祖先目录，U1 已关闭

owner 在收到上述证据缺口后，在第十项 child 启动前追加 `fs.mkdirSync(f.engine,{recursive:true})`，并保留 04 stdout/stderr 不覆盖，另出 05 轮原件。本 agent 只读新单元全文和新双流；未重新运行单元或产品。

| 05 新输入                                  | bytes | SHA-256                                                          |
| ------------------------------------------ | ----: | ---------------------------------------------------------------- |
| builder-private-unit.mjs                   |  8372 | 92f4ea00ef7c6a96e45eba82f5d6457028800bb964518ae2c38ff45ba8dba28c |
| 05-builder-unit-root-real-ancestors.stdout |   954 | 723d27b54f36413bf439864b7506aaea88ee5d45735c9b66df33d5ced3de150c |
| 05-builder-unit-root-real-ancestors.stderr |     0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |

静态从当前单元中仅移除新增 mkdir 语句，可逆得到 04 首读的 8330B/4077d437 身份，确认其余单元内容未变。05 stdout 明确仍为 10 tests、10 pass、0 fail、0 skip，第十项 bounded child 通过；stderr 0B，owner 报告实际命令 exit0。真实 Python prepare/finalize/PyInstaller 仍全部为 stub，没有发生完整产品构建。

现在 engineDirectory、dist、runRoot 及 root 以内祖先均在 child 启动前实际建立，原代码不会再因最初 ENOENT 提前拒绝；测试仍传带 `/.` 的非规范绝对 root，独立 child 保持 2000ms timeout，断言无 timeout、status0 和固定拒绝码。因此，新证据与静态 guard 修复共同关闭 F1 的局部回归覆盖缺口。没有重跑旧源码故意挂起，不虚称已实际观察旧版本 timeout。

本次完成时重新核 builder 8437B/738f55、入口 976B/aaf9、首审 6817B/ae540、首 JS 副本 8298B/94a376 均保持上述身份。新增 Python 模块的后续 cherry-pick 不纳入本局部复核，也没有读取其实现。最终结论不扩大到四路径；完整模块、实际 archive/loader/native、外部 root binding 与最终 source/package 证明继续待独立验收。
