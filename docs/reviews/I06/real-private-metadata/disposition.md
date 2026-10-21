# B-M 冻结处置与实际验证

2026-10-21。本轮从批准5f新树施工；采用ref `f63fe6fa0ba9eff944b11b9e4bbd7e6235e43dbc` 恰含只读A inventory+专属测试两件。新增产品/测试只有private-resource-owner及专属测试，完整相对5f范围由manifest与实际Git差异绑定。原AGENTS保持未暂存，未写ffb/6a38/e2c/961产品、测试或旧原件。

## 最终结果

| 实际原件                                          | 终态                                                                                         | 精确适用输入                                                        |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `raw/bm-agent-after.2.*`                          | exit0；47pass、2skip                                                                         | module f9667954…5a54，test633403a4…dad3；前后hash及原源归档全同     |
| `raw/full-check-first.*`                          | exit0；17 TS文件，713pass/2skip；1052 Python通过；正常lint/format/typecheck/build/ruff全通过 | inputs/frozen-before-check.json五件逐hash绑定，检查后未改代码或说明 |
| `raw/sources-first.*`                             | exit0，12个归档源文件                                                                        | 同树最终代码                                                        |
| `raw/module-types-fixed.*`、`module-lint-fixed.*` | 各exit0                                                                                      | 同最终源；测试作者另有自身格式/lint原件                             |
| `independent-review-r1.md`                        | 明确通过，8612B/SHA `129c93e65057d0fff89dc5998b897ce382d5f879d6bbdbfc4d6813d583983b52`       | 审查者全文读两新件/说明/只读采用与必要原件，没有冒称重跑产品        |

正常check含已采用A专属回归；不声称另有未执行的独立A命令。两skip是Linux非法byte名及Windows分支，当前实际macOS27.0.1 arm64、Node24.15/Python3.12.12，详见environment.json；不是目标macOS15或Windows11验证。独立npm ci与uv sync --frozen均exit0，依赖和.venv均本新树，未借其他树可变环境。

## 首失败及逐意见处置

1. **初始类型检查失败。** `module-types.*`真实exit2，保存原stdout/stderr；never函数声明的控制流收窄未成立，导致Result.value与stats初始化检查失败。改明确函数声明后module-types-after/fixed为0，无any/stub或改A。初始类型输入没有另行封存完整源码，不能拿后续hash冒称其精确输入；实际命令/错误原件保留。
2. **首专项exit1，38pass/7fail/1skip。** bm-agent-first绑定ae7984…模块及当时测试hash，owner源码在运行后同hash读回另存.source-readback，明确不是追造运行时快照；该旧测试只有当时hash，未伪称留有旧全文。失败包括mutation屏障/字段与权限、两项同bucket映射以及Mac真实非法byte名fixture创建EILSEQ，全部保留。
3. **同bucket多资源投影。** after.1定向2fail/45skip、reason inventory-rejected，原A捕获树拒重复引用共享parent对象。最终每resource的parent/identity/components独立值复制，不删真实条目、不改A；同bucket孤儿/pending、final+pending真实硬链接均在after.2通过。
4. **mutation取消不能清屏障。** static-preflight原实施中反例及首失败均保留。最终cancel/close保原精确token直到end；close可报告mutation-unsettled，不能变成已释放；克隆token拒绝，收尾不恢复接纳。实际专属反例通过。
5. **权限与故障注入分列。** 宽写root/bucket/leaf先保事实再unknown；真实mode000为当前OS权限用例。after-root-reserve为注入初始化拒绝；close-receipt-once在真实Dir.close后注入收据失败，保留slot，不能称OS close真的失败。最终专项通过。
6. **未知异常分类与投影后TTL。** 初读static-preflight绑定ad611…，不伪称保存过该快照全文。最终内部WeakMap识别固定错误，unknown descriptor访问有catch；观察Promise有拒绝收尾；投影后重核整轮deadline/generation。独审实见修正，只有静态确认这两分支，没有伪称另跑时钟/异常探针。
7. **Node竞态与系统调用pending。** 未修成原生能力。静态symlink拒递归，但lstat→opendir可被替换并follow；ABA/绝对nofollow及真实系统调用5秒超时均不由B-M证明。说明及独审保留该限制；所有实际观察只在受控fixture，无用户目录许可，production unsupported。

测试作者static-3使用git diff --no-index新文件，exit1但两流零字节是新增差异退出，不是whitespace失败；外层max(exit)=1原样保留，不当专项测试失败或改报exit0。初始工具串行组合曾仅输出Prettier和外层exit0；采用本review后续逐命令分离receipt作正式类型/lint证据，不推断未单独保存的早期逐命令exit。

## 完整原件与冻结规则

根明确要求完整argv/cwd/环境、分离stdout/stderr、首失败和hash，本阶段未push/CI；因此本地review提交必要的原始日志与源版本快照。原字节不批量格式化，包括被默认ignore的.log；只精确强制加入本raw内的实际日志，不改.gitignore。五个最终输入、采用原件、独审原文、首次失败与后续记录全部在manifest逐bytes/SHA列明。

`evidence.zip`只封存明确列出的四产品/测试、主说明及本review原件；不含依赖、用户数据、ZIP自身、manifest或后出的packaging-verification。实际逐成员CRC/集合/字节hash验证后，ZIP和各原件由外层manifest绑定；manifest不自列，最终Git提供外部ref。packaging-verification保存实际核验，不纳入自身或包，避免循环hash。全证据Git whitespace与排除原始bytes的源/摘要检查按实际退出分别记录，不清洗原件。

本阶段只真实I06四角色子集与本供方计账，非全应用inventory、跨重启retired或OS释放证明。同址旧新identity仍在原A上unknown且保历史；A两件只读。B-R/B-L、T01/T03共享、native/VFS/两目标OS、首内容IO/公开消费未实施。原Goal、指定模型双方新审、父功能/CI/正常develop合并/远端/真人门不变；无GUI/e2e/native/HMR/Keychain/模型/付费/push/PR/merge。
