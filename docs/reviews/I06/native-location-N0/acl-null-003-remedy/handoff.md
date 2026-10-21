# ACL-null 003：只读修复准备交接

003失败档案已先固定为 `b0342c44c08441049edc7d246d201bd44ea35719`。随后仅按本目录authorization-window及execution003-root-closure进行定点只读方案；产品/测试均冻结，无API/FS探针、native运行或第六构建。

建议见proposal.md：同held FD单次fstatx取得stat/filesec；先证明必需元数据完整一致、扩展envelope见证成立，再用成功query的ACL presence区别明确absence与present ACL。任何失败、缺省见证或不一致继续拒绝；不增加NULL+ENOENT成功白名单，任何ACE继续拒绝，真实acl_free失败不成功。该absence证据链来自固定公开实现的保守推论，尚不是已验证的本机行为。

三份必要Apple公开Libc源码固定 `71bbe350ab79eef58113991d817ccc6165061a64`，四份SDK声明只留必要摘录，身份/hash在source-pins.json。公开source不是本机libSystem版本/运行路径证明。关键反例是：短security envelope和NOACL均可清ACL属性；公开realloc失败路径还可能返回0但fresh属性未填。故仅fstatx0+ACL valid0不够，也不能把valid当固定1。

内部for/realloc仍有未证明的次数/字节/wall上界，ACL_MAX_ENTRIES=128不能关闭它。方案只限制应用侧1个filesec+1个ACL副本和有限调用点；不把原wrapper已存在的内部链冒充新增硬资源保证，不新增一般trace/资源框架或恢复SQLite被拒线。

精确拟writer为Mac的platform_metadata/必要cleanup，加Darwin test局部ACL fixtures；core/ABI/Windows/Node/TS/driver/限额保护。真实验收范围在validation-scope.md：明确absence正例、可能自然出现的present-empty、同FD一ACE拒绝、原安全门及有限失败输入；setup失败/未覆盖层/无法自然制造的故障分开记录。本轮未实施这些writer，也未执行测试setup或任何查询。

独立最小方案审查见independent-remedy-review.md；有限manifest排除自身，过程ref在提交后回复。root拿到具体方案后还须授源码/测试窗口，T03编译和新一次CLI各自另授；不自动重跑003。旧003原件、001/002未知边界、未排空/残留和目标OS/EXCL/父N0门均保持。
