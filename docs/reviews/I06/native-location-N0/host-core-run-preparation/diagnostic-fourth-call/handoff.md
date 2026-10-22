# ACL remedy 新pair：004固定调用准备

状态：**PREPARATION_ONLY / NOT_RUN**。从9509d02790f9a79905371c5183be16cab99f5114接续原I06树/分支/Goal，仅准备数据、只读核指定pair；未执行cmd或其中Python payload、core/probe/native/addon、ACL/API/FS probe，未编译或重跑003。record不是运行授权。

## 固定调用及六值

唯一模板为5b78098ae8b53168fc23ec7499f240d1ede3f1c6中的diagnostic-third-call/exact-tool-call.preparation.json arguments。模板19615B/SHA 4c14304e4e4be6b041f60596aa581ed277af40e79d4499f9d2e8bf9e38d8cbe5；新调用exact-tool-call.preparation.json为19614B/SHA 8f9788b64b721ad60a8a1c5bf4a72287dd2519d6fcdedc82f5b681e1a8adb739。

- record：I06-N0-execution-004-1526093e58aeaa43。
- 完整cmd另存exact-cmd.preparation.txt：17176B/SHA 100ebd1ae0a8f43608146565b95d145503e014b87beaccb53182fbc5115d8781。
- stdin（含末尾LF）：16976B/SHA 5a3fb0e4b6e273ca20c76f7ddb0567fcd0f2ce75baed151722e6b7dbebd7db92。
- 其它tool参数逐值相同：workdir为本原树绝对路径，login=false、yield_time_ms=1000、max_output_tokens=1000。

只修改AUTHORIZATION、CORE_PIN、PROBE_PIN，以及RUN后缀、os.mkdir首参、对应run-directory os.open首参三处execution-003→execution-004；cmd行4/5/6/24/240/241恰六行。三赋值注释、其它文字/空白/BASE、历史记录、shell和Python算法均保持。逐行反向还原恢复完整旧cmd字节，六节点归一化后全AST相同；见exact-six-values.patch和delta-static-check.json。没有执行或重新大审旧17KB算法。

原清环境-I/-S、单Popen、取消/信号/exact waitpid/未知、stdio/控制记录及全部原限额不变；本轮无wrapper、环境、timeout或算法增量。初次只读提取器误猜heredoc标签导致IndexError，发生在解析/写入前；改用模板原I06_N0_ONE_SHOT_PY标签后静态核对通过，未更改模板或运行payload，工具首失败身份保留于静态记录。

## 新pair及真实来源

I06产品1217e0f63a9c62b72e01046ef5fbc5c53434251a/过程9509d02790f9a79905371c5183be16cab99f5114；T03输入bfe137f371361f9fda446d5cbe6b3079c5433ee5/过程37fe056e5d1716a10237de20f79042db54aa0549。新digest：1526093e58aeaa43cd5c96dfc911dd032759df27c039bf3d11eacfb1e6cbfd50。

| 实物                 |      B | SHA256                                                           |
| -------------------- | -----: | ---------------------------------------------------------------- |
| location_core_test   | 362656 | 17fb8b48ec3e79cfd36015edc4047bbd390ac0145dd2c40b1c20850455771f60 |
| location_child_probe |  34120 | 5b9978c2e7bbb8d3ee51d3d94d95ab4797ac01337654180cf121d89dc3e05b98 |

两绝对路径在新调用的CORE_PIN/PROBE_PIN及静态记录中，位于T03第六digest的core/artifacts。只读bytes/SHA及文件metadata吻合根窗口；不替代未来获准调用的pre/post核验。T03为built-unverified/NOT_RUN，不是API行为通过。

raw模板result.sourceRef仍为b59239f9c1ec2774c7922f95dfc67db4dc8754e8的历史字段，**不是本次真实源码/产物来源**，未改写。未来归档必须另绑定上述真实refs/digest/pair、本准备ref、cmd指纹及另授执行窗，不能仅凭该raw字段追认。

## 下一CLI窗必须明确的fixture应用范围

新core确有三Darwin case行为增量，下一精确一次CLI需要单独授权其setup/read及原规则清理；本轮仅写出边界：

1. 三个新fixture各自持有自身anchor，沿原构造器empty-ACL setup和本fixture清理；不扫描旧路径，不改系统/用户权限。
2. empty：同FD一次独立fresh filesec/fstatx，OWNER/GROUP/MODE getter一致及安全门、UUID/GRPUUID与ACL presence query；present时独立ACL copy/valid/FIRST，必要NEXT确认。随后一次owner create、root公开metadata校验、显式close/cleanup；固定布尔行。只有absent_observed=1才算P1明确absence；自然present且空只能算P2，不制造第二表征或改门求绿。
3. one-ACE：当前owner一次mbr_uid_to_uuid只供qualifier；acl_init/create_entry、ALLOW tag、ACL_LIST_DIRECTORY最小permission和零flags、valid、同FD set/free；一次独立见证必须确认present且恰一条有效ACE，再一次owner create，预期DENIED。非零失败owner必须先close后断言；任何setup/query失败均是无效测试，不能算DENIED通过。不输出UUID/FD/owner身份。
4. invalid-FD：仅自身input副本borrowed_directory=-1，一次创建及失败owner关闭、fixture清理；只测duplicate输入门，不声称覆盖fstatx/property内部错误。其后原metadata/child/partial/concurrency/budget case和原child probe仍保留，原调用控制/限额不变。

以上不是本轮许可或运行结果。真实API/fixture检查失败保原件停止，不能自动重试、改环境、扩大清理或放宽absence链。allocator/query/get/free异常、短envelope/fresh未填、未知ownership、内部heap/系统调用/wall硬界不能靠正反用例关闭；公开Libc不是installed身份，stdio非零成本。

## 冻结和交回

execution-004准备时不存在，未创建其运行目录；未来若已存在须停，不复用、移动、删除旧001/002/003或扫描fixture/杀PID。九源current/fixedGit及AGENTS受保护WIP指纹保持，旧源码/锁/过程tracked原件未变，见preservation-check.json。纯准备不跑npm check或旧源无变化复测。

独立窄审见independent-delta-review.md；有限manifest自排除，固定新过程ref在提交后交root。root读回后另授新pair精确一次CLI，此前不执行或编译。003仍为失败，旧drain/根因未知，EXCL全路径、目标双OS、父N0、双指定外审/CI/真人/远端及T01 wholeH/SQLite损坏保护HOLD均保留，拒绝的SQLite线停止。无GUI/e2e/HMR/凭据/外部模型/付费/push/PR/merge或Goal变更。
