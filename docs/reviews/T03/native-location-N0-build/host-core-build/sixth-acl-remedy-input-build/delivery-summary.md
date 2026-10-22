# T03 第六次 ACL remedy 输入构建交付

状态：BUILD_SUCCESS / STATIC_REVIEW_PASS；尚未运行 native/core/child、CTest 或 ACL fixtures。此次是已授权新输入的一次构建，未重试，未启动第七次。

授权 ad93c6a744bf243633ed3f265816454630c32923；两源采用 2ce18bb20aace0f4434a97d691afdf08f4413b89；锁产品 3e6e5ddd14ae08241f2f26f8b30e0a765ce70077；固定构建输入 bfe137f371361f9fda446d5cbe6b3079c5433ee5。供方产品 1217e0f63a9c62b72e01046ef5fbc5c53434251a，过程 9509d02790f9a79905371c5183be16cab99f5114。锁仅八叶变更，10475B（+1B）；其余七源、CMake、driver 字节不变。

原 driver PID 47416，退出0；实际13条顶层命令均有正PID且退出0。CMake physical pins 明确完成9308+33464。4个翻译单元、两个链接成功；10条 file/otool/nm 静态检查均退出0，检查前后两个产物字节一致。未执行产物。

两个产物保持在 build-input-plan.json 指定的独立目录：

- location_core_test：362656B，SHA-256 17fb8b48ec3e79cfd36015edc4047bbd390ac0145dd2c40b1c20850455771f60。
- location_child_probe：34120B，SHA-256 5b9978c2e7bbb8d3ee51d3d94d95ab4797ac01337654180cf121d89dc3e05b98。

二者为arm64，LC_BUILD_VERSION minos15.0/sdk27.0；加载libc++.1、libSystem.B，动态加载器/usr/lib/dyld，rpaths为空。core 11个_nl_外部定义保持，_renamex_np仍是libSystem未定义导入、无_rename导入。新增filesec/fstatx/ACL等17个undefined导入，移除_acl_get_fd_np；具体列表见 actual-difference-summary.json。静态链接与符号证据不证明运行时加载或ACL行为。

依赖原始词1805→1808、全局唯一877→880；只在test TU新增membership.h、ntsid.h、uuid/uuid.h；Mac仍178，其他TU不变。新增3条均找到批准索引记录，unmatched=0。条件一次批准索引stream访问42772记录、读取19368210B；只保存3条新记录及其lstat身份，不读取头文件payload、不重复完整source-to-sidecar映射。另有2条格式探测记录，已计入owner预留。旧两别名本轮只核对6次元数据操作。编译器真实open trace、实际选中tbd/archive成员与运行时closure仍PENDING。

原B目录144个文件共3104411B；92份driver原始记录/流、17份生成证据按字节归档；二进制和object保留B目录。所有旧失败、超额/未知账目、旧五轮输入和产物保持原状。预算见read-account.json：build声明108738235432B/128GiB，实体保守513264/600000、已知完成470492；元数据保守2055635/2250000，根控独立审查15000另票，未释放旧预留。实际OS/compiler/loader I/O未知。

运行边界：ACL-003新remedy尚未验证；自然空ACL/显式absence观测、单ACE拒绝、duplicate gate invalid-FD fixture未执行。SQLite拒绝线继续STOP/HOLD。没有push、PR或merge。

独立结果审查已完整阅读，无阻断。报告 outcome-independent-review.md：10799B，SHA-256 5ce2cbb8ac11d5eec0f645492cb19f527ab9de9b5f5c3e91274c4c35ccbb7b18。审查不预签最终Git index；最终封存由verify-delivery-index.py另核。

Git空白检查：完整cached检查返回2，62处诊断仅限7个生成raw文件；原始字节保留，精确排除该7文件后普通检查为0。52个stdout/stderr使用逐项-text规则，无glob。
