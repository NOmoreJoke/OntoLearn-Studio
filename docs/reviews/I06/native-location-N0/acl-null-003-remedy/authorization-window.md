# 003 ACL-null：原会话定点修复准备

2026-10-22。先完成003原结果的独审、固定归档及交接，再在原I06会话继续本项只读文档工作；不修改产品、不构建或再次执行。当前原stderr126B/SHA256 f508e845a5ee83f12edcd0a2d0a1456f78124530b167538cea7755ae0a21c74f实际为acl-null errno=2，随后metadata case/UNSUPPORTED/owner_nonzero=1与owner-create失败。只定位本次返回空分支，不追认001/002相同errno或完整根因。

总控已只读核固定fc9853的platform_metadata：fstat/owner/mode/link检查后一次acl_get_fd_np(held FD, ACL_TYPE_EXTENDED)，任意nullptr均UNSUPPORTED。Apple官方归档手册说明NULL为错误，不能仅凭errno=2直接放行；其公开Libc的acl_get_fd_np还经filesec_init→fstatx_np→filesec_get_property(FILESEC_ACL)→filesec_free，具体哪层失败/无属性未被该简化调用区分。公开main源码只是语义线索，不是本机libSystem身份或运行路径证明。

已读官方入口：

- https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/acl_get.3.html
- https://github.com/apple-oss-distributions/Libc/blob/main/posix1e/acl_file.c

请定点查官方公开API文档/源码与本机已知SDK声明，形成最小可实施修复方案：严格区分“成功读取元数据且明确无扩展ACL”与“查询失败/权限不足/不支持/未知”；保持同held FD、不走字符串路径、不跟随链接、不修改ACL/模式或环境。若建议fstatx_np/filesec的显式存在性查询，证明其成功/缺省/无效/清理/errno语义与有限资源、身份快照关系，不能只把NULL+ENOENT加入成功白名单。任何非空ACE继续拒绝，错误与无法确认保持fail closed，真实释放失败不当成功。

仅核必要少量官方源/声明和固定I06相应函数/原fixture，列出明确来源身份、反例、错误映射、精确拟writer和必要真实正反验收。独立agent审最小方案，有限新文档置docs/reviews/I06/native-location-N0/acl-null-003-remedy/。不得重审旧五轮大供应、添加一般能力框架或重跑无变化验证。

本窗只读静态设计，不授实际ACL/FS/OS探针、setfacl/chmod/删除旧fixture、native运行、源码/测试修改、第六构建、GUI/模型/凭据/付费/push/PR/merge或Goal变更。003原件和既有产品冻结。拿到具体修复与验证范围后总控授相应源码窗口，随后T03必要新输入编译及CLI再分别核定，不把本窗作自动重试。

此ACL API语义问题独立于先前平台拒绝的SQLite/heap资源分析；后者保持停止，严禁借此恢复或改入口。
