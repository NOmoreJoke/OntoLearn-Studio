# T03 N0：固定81项dyld供应身份读取额度修订

2026-10-22。继6465B/1e47f7工具供应窗口，仅把该窗口累计实际读取guard从8GiB提高至10GiB（10737418240B）。200000项数量guard保持。此修订只允许补读以下精确清单，不扩目录、不授新进程/编译/加载或写系统权限。

根已实际解析全部81条路径/realpath/bytes/状态，核清单自身24420B/SHA256 `a0a368c44eec7843270d9f65a517bf43fa546e3766aeeb3fceeea82b80c6f08c`：

`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-native-location-N0-build/docs/reviews/T03/native-location-N0-build/tool-supply/unhashed-system-cache-objects.json`

所有对象均为 `/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld/dyld_shared_cache_arm64e` 及该清单明确后缀，81路径唯一、path=realpath、总7046515706B。原read-budget.json378B/SHA32ef2836d14e348f6e5919eeade542d08322f48d109f2c01d6c88f657587bd42记录累计2699211379B，完整补读后预计9745727085B，在10GiB内；实际每次读取照计，不重新计零、不减去已耗费。根读了21个直接install-name在实际map中的精确命中摘要；这是整体cache身份范围的依据，不声称81项都被compiler实际使用。

仅流式只读一次哈希该清单每个实物，先lstat/realpath/size核当前身份与清单，不跟新链接或接受自动新增项；实际读取累加，前后stat变化/读失败/预算不足如实停止并保首失败，不能给未读对象伪SHA。不得复制/提取cache内部image、执行cache代码或更改系统/SDK/权限；不全局扫描其它cache/架构或用户目录。证据只写既定tool-supply过程前缀，旧24420清单、预算与原件保留，追加新manifest和实际累计费用，不覆盖pending为过去已完成。

本窗口没有新增缓存内部传递依赖解析/提取工具、系统动态加载或编译授权；若现有只读有限脚本可提供静态解释，另列实际方法/未覆盖事项，不把整体hash称完整传递依赖或编译后used闭包已证。所有source/toolchain/execution审批仍待根核完整固定供应后采用，不能因本修订置true。原R5独立修复、九源/ABI与组件拼装、configure/try_compile/build/CTest/native/child/FS实验、Node/Electron、Win/双OS/生产位置及指定双审/CI/develop门均保持。
