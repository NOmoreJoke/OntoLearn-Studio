# 后续宿主环境最小差异候选

2026-10-22。本件仅为5965B窗口下的可审候选，不修改driver/CMake，不授执行权。固定driver仍fe98的27002B/d1ddcbd，CMake仍13332B/81df。原Mac lock environment schema严格空对象，build()构造硬编码最小环境；单在shell或当前锁写DEVELOPER_DIR不会形成获准传递，额外lock字段会先被拒。

根要求后续宿主core固定 `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`。优先使用已固定inventory里的真实绝对make/git/compiler/linker backend pins，避免以`/usr/bin/make`与`/usr/bin/git`相同dispatcher表面SHA代替真实选择证明。当前13版本探针与静态backend映射属于不同证据，不补造新backend版本执行。

后续如根批准此差异，最小实现范围是：

1. driver Mac environment exact keys从空改为仅DEVELOPER_DIR，并严格约束其值为已核固定Developer根；Windows六字段约束不扩张。
2. driver构建子进程的Mac最小环境显式传该锁值；不承接用户后续xcode-select/PATH/CFLAGS/CXXFLAGS/CPATH/SDKROOT等覆盖。PATH继续固定最小字面值，C/CXX/make/git仍使用批准绝对pins。
3. CMake的Mac `project()`前门读取同一字段，要求其与固定根及实际传入环境相同；缺值或不符先拒，不延后到compiler probing。
4. 锁中Mac environment仅填该唯一候选字段；实际工具采用和execution各自仍须根精确批准。未来最小静态复核应绑定新driver/CMake/lock同候选及原source pins，不能单改字段冒充已可运行。

编译器真实loaded/used/link依赖、产物架构/最低系统/exports等仍属首编译后观测；不能在首编译前伪造，也不以其未产生为理由停下已授源码/候选准备。供方派生清单从fb40及其追加81项元数据生成，本轮不再hash大SDK/cache。未来driver与CMake前门按其当前实现会各自核供应pins，须在新执行窗口记录实际读取范围及费用，不重置/覆盖旧9745727085B。
