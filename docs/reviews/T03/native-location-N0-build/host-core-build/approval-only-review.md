# T03 宿主core审批增量定点审查

2026-10-22；独立reviewer：n0_build_review。

结论：当前f6e9f4209e5c285cac248b036d9ac95149725e7d之后的两对象审批增量及approval-map可接收，引用与实际Git授权原件一致，无本次范围内剩余问题。

- `toolchains.darwin-arm64.approval`仅从false/null改为true/`d6ed4e4bb9401ff310337937acd3196b9392e2fa`。该ref实际保存1879B gnumake授权，SHA `2279b03c9acd0d969c6e1ea14cbe22f6c3cd84463e099fb43c102d0af20a041b`；实际parent即c66，继承7961宿主core授权。
- `execution.darwin-arm64.core`仅改为true/`c66f6e8ce7fee7f77ed7ed259d0771ef8c8ff278`。该ref实际保存7961B授权，SHA `697ed52b2aab00ba737cb85b61228f65770a16692d44105627db0e47b21dea00`。
- 独立比较完整JSON：除上述两对象外，锁与f6e9逐字段相同；其余产品无diff。source/API3/testAssembly原批准未变，Node/Windows及全部addon/其它execution未放行。approval-map的candidateRef、两个ref/path/bytes/SHA、继承关系、已固定8221B环境独审身份及仅Darwin/core原命令范围相符；产物执行仍未授权。

实际锁9189B，SHA `e9e18a7748d8f555a65a836b44ee505496035050a400a814f68c48186ef792e7`；approval-map1480B，SHA `3b4ae337d669ca1e18fbf4c9f4d47c77af1f2efe0d591d2ad7587bd45acc1e7f`。

仅作文件/Git/JSON核对，只写本报告；未物理读取工具/SDK、未运行验证/driver/构建/测试，也未重审R5/I06。本结论限审批增量，完整12输入固定及后续一次构建仍须遵守原授权，不表示构建或运行已通过。
