# 交root：仅静态承接准备

状态 NOT_BUILT / NOT_RUN。本阶段只新增本目录过程文档/输入原件/预算/独立窄审；没有消费I06当前实验源，未创建新build/record/run目录，不改12项产品输入/CMake/driver/锁或第六pair。

方案见build-plan.md，账见budget.json，身份见input-receipt.json。选择未来单用途直接clang++单源编译兼链接，不复用旧core产物；命令/新runner/解释器、source/ref/headers/symbols/layout及准确索引定位仍待root补齐并另授。未来256MiB/16628 metadata/8192实体只是候选cap，不是本次构建或runtime许可，也不证明资源内部硬界。

本轮从原未分配余额新增8MiB/7000 metadata预留，guards不变、旧票不回收：build声明108746624040B，余28692329432B；metadata2062635/2250000，余187365；实体513264/600000不变。root独审2MiB/2000独票，作者窄审另2MiB/2000。当前未调用compiler/cmake/xcrun/API/额外探针，SDK/resource实体新增0。

顺序：root收I06冻结源及独审→转固定输入/补pending→另授T03精确构建及预算→真实构建/归档/独审→root收新产物→原I06另授一次CLI。任一必需输入或预算不足即具体报缺口，不扩大扫描/重试/修源。

独立窄审和最终有限manifest在本目录收尾；manifest排除自身，父过程固定37fe056e5d1716a10237de20f79042db54aa0549；最终纯过程ref由实际Git提交结果交回。没有提前预签新源码或产物。

独立窄审已完整阅读，无剩余阻断：independent-static-preparation-review.md，7524B/SHA256 3769f5573d4458da85d3c37f9473d592f59bb786716edbc3aedfcce68e97941a。作者应用读取保守上界384KiB、记录≤1000，未借root独票；未预签最终index。18项有限静态断言及8输入43015B逐pin通过；本轮新增范围cached whitespace实际0，旧第六62处原件诊断及全部历史账保持。最终有限manifest及Git index/working字节实检随后完成，不提前填未来源码或产物身份。
