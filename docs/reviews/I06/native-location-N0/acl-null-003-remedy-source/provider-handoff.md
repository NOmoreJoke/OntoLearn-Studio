# I06 两源源码交接

产品固定为 **1217e0f63a9c62b72e01046ef5fbc5c53434251a**，直接父提交为只读方案过程 **3cc158e0a62b154d110a6fc80e3ddf171cea0098**。仅以下两源变化，另七源、CMake、driver、lock、限额、Windows、Node和TS保持。九源完整前后bytes/SHA及current/Git逐一核验在source-before.json和source-after-and-static.json。

| writer                                               | before bytes / SHA-256                                                   | after bytes / SHA-256                                                    |
| ---------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| packages/native-location/src/platform_macos.cc       | 8670 / e1fbbcd9c9b73916bd9a030da8bc237dd46230fdd8d0366f0e2424168d4cd71a  | 12579 / d944a4901b6d3f516f18ab436aed9ec56a78eb1bbd12d1949ebf6a6e171825ce |
| packages/native-location/tests/location_core_test.cc | 30037 / 4cec7d67ba66fdf47d0ae26ba056372dc437e67ac076e768a548c334bd260319 | 37928 / 2517eb970ef39f37dd99ca9945909331df937d4dd43ce53b74eb722bf47a7053 |

生产只调整platform_metadata和必要同文件cleanup/error helper：同FD fresh filesec、一次fstatx、三必需标量一致、两个UUID存在见证、成功ACL presence之后才允许absence或有效空ACL。新API非成功按批准分类，已知ACL一次free，未知ownership或释放失败RETAINED优先，void filesec_free无伪造返回检查，最后才发布metadata。原type/UID/mode/link/no-follow/identity安全门及owner责任保持。

测试只加Darwin include/helper/定点empty、one-ace和invalid-fd case，原fixture方法/原用例断言逐字未改，28个Windows静态断言保留。新failed-adoption的非零owner在状态断言前close。源码移除这三块增量即可逐字还原旧test；Mac去新helper并还原metadata即逐字恢复原文件其余部分。新增固定输出最坏71B，含换行，不含敏感身份或路径。

固定产品后只执行一次正常npm run check，退出0；ESLint/Prettier/类型检查、前端三段Vite build均通过，Vitest为16文件、637 passed及1 skipped，ruff检查通过且236文件format检查通过，pytest 1052 passed。缺失显式native addon的真实集成测试保留skip；本次仍没有C++编译或native执行。12份归档源verify:sources退出0。完整argv/cwd/env调整、原始双流、退出与时间见check-command.json/check-result.json、verify-sources-command.json/verify-sources-result.json及对应原始log；双stderr均0B。原始check stdout 5074B/SHA db63b5a8114f6a8fd18cefdabb66efdb9e71ffe4675976a09006e9f97a058bb2。

独立source审查见independent-source-review.md，范围为本固定两源及本次交接；报告的静态结论不能替代C++构建/fixture行为证据。过程包有限清单为manifest.json（自排除），自身提交身份由Git提供，不在包内制造自引用哈希。

精确API和fixture范围、P1/P2表征区别、未来许可顺序及未覆盖故障见validation-scope.md。该文件列的是源码，不是运行记录。本轮没有生成新的native产物/digest或编译新pair；旧T03第五对输入0514d37e32e31ae569e583bb56ec225ebc0483e6、过程8528ccb3d68de4f31ee1e10bd984084e0f7f418c及digest 0d5223985fcd9761c60cee55d4c258af9b8204c8b0131df1535928cd1953c8fb不含这次remedy，不能验证它。

001/002/003和旧五轮过程仅以Git父链保留身份，未重审或改写原件。003仍固定失败b0342c44c08441049edc7d246d201bd44ea35719，不能由本源码倒填NULL/ENOENT原因或宣告已修复。T03须另授新输入采用/编译，再按新pair另授精确一次CLI（含批准的定点fixture ACL setup/read）。本轮未执行该后继工作。

公开Libc推论仍不等于installed libSystem身份或通用合同；statx内部for/realloc、ACL转换内部资源/调用/wall上界未知，stdio非零成本。不关闭drain、EXCL全路径、目标双OS、父N0、同版指定外审/CI/真人/远端门、T01 H或SQLite物理HOLD。
