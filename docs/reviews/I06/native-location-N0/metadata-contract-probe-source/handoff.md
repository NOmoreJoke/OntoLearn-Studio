# I06 ACL表征实验源交接

本轮仅新增 `packages/native-location/tests/location_metadata_contract_probe.cc` 和本过程目录，基准7ea3bfb06ff117f80f0aa770ab5f563b6b5c3b3e；状态 **NOT_BUILT / NOT_RUN**。源/过程固定ref在交回及manifest中，既有产品/test/ABI/CMake/driver/锁、九源、AGENTS和旧失败原件保持。

冻结设计引用同基准 `metadata-full-positive-contract/decision-experiment.md`（15506B/55f073f1352ef7e621455a2fb70dfe92c6287e10c591459abf916ee4d532c1e7）、observation-and-acl-contract.md（12447B/209f25ba0e82e982c3d04a0650f7f005171d38f3a767108e5e2af1cfe6b7238c）、independent-contract-review.md（8891B/a8949c68d6d60d12c0e37678ec63a3a25fbbc538be6b0564929b634cc7786f6b）。本目录保存根源码窗口原字节；没有改写旧设计或接纳记录。

实现E三必需正例先行，原setup/生产FD模式；E全部充分才一次owner UUID和N两真实单ACE。完整mask/packing/length/offset/变量区/magic/flags/count前门、NOACL先判与受检算术、同FD标量/身份、ACE qualifier/ALLOW flags/精确rights匹配均写入。SDK命名语义联合固定Libc setter/native export转换摘录说明映射，编译期ABI断言尚未编译，不能当installed源码同源或目标运行证明。

单一路径最多7 fstat / 5 fgetattrlist，其它setup/open/close/ACL/cleanup数及短路见source-contract-and-build-input.md和static-source-check.json。五个Observation仅固定340B记账，全部同步查询后统一一次已知资源cleanup，再写有限输出，避免stdout/SIGPIPE绕过已知收尾；异步终止仍未知。已知FD/ACL只close/free一次、释放及残留未知retained。最多1018B程序stdout、每行≤96B，stderr无程序写入；实际运行输出未取得。

独立agent只审新源/必要摘录/本轮说明和调用、输出、解析/ownership，不重开旧供应史；报告单列本轮发现与定点修订。静态检查只读源码文本、JSON/哈希和格式算术；没有预处理、编译、运行、API/FS/进程探针或fixture创建，没有record/运行目录。JS/TS/Python未改，不重复正常套件。

T03下一门需要独立单用途C++17/Darwin构建：唯一entrypoint源、直接headers和API符号白名单/SDK摘要已列，实际闭包/符号/编译及累计预算仍由root另授T03唯一维护。当前没有向T03发新任务、复用旧pair或执行旧004许可。

仅eligible表示五样本及可检查收尾足以继续profile适配设计；不代表原owner/root/acquire/observe/撤销/关闭case或N0功能成功。003/004失败、drain/fixture未知、内部资源硬界、双OS/完整父功能/同版外审/CI/真人/远端、T01 HOLD保持；SQLite/heap/OS资源拒线继续停止，无GUI/Goal变更/push/PR/merge。
