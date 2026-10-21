# T03 N0 独审处置

2026-10-22。独立 `n0_build_review` 对实际候选4逐件重算并签结；报告10427B，SHA `a33f358b845287e25532399c336cf9446f0639508a3b61b6465e2c082ba03ad3`。报告只支持三 writer 静态交付，四项 P2 已静态关闭，没有剩余 P1/P2；不批准 configure/build/test/load，也不证明完整分支已经运行。

| 项 | 具体修正 | 核定与边界 |
| --- | --- | --- |
| R1 执行事实 | driver dispatch 前单调置 processExecution=true，catch 保真实状态 | 代码已独审；没有实际进入 future build/故障路径 |
| R2 project 前完整门 | addon/Windows pins、Node API/许可、全部工具、resource/SDK inventory、SDK元信息和许可、固定环境、系统库 pins 前置 | CMake 源码已独审；未运行 CMake parser/配置 |
| R3 ABI 头一致 | driver/CMake 绑定批准 source.files[0] SHA 与固定6a合同头，CMake额外比固定常量 | 当前全九尚未采用；未以变锁/假头试验 |
| R4 合法零字节库存 | 一般 pin schema 允许0，仅 inventory文件允许空；工具/许可/manifest仍需非空 | 官方 hello.f=0 的真实静态反例闭合；未运行造输入试验 |

实施者补充的 writer inputDigest、固定 Git及 clean/HEAD/source blob核对、首失败与双流、分 component 前置也已独审。全部当前审批仍 false，九源路径不存在；候选4六个实际 verify-only 均incomplete/2，Node语法与格式检查0，三 writer检查前后hash一致。`static-validation.json` 保存实际 argv/cwd/双流/exit及边界，不把这个结果写成编译或 N0 通过。

材料索引、归档/Node原件、保存的许可文本和11项材料证据又以只读bytes/SHA复核共28项匹配，见 `official-material-integrity-receipt.json`。没有重跑材料脚本、安装、运行归档代码或改源索引。临时材料保留、真实供应采用、SDK覆盖/后置依赖、目标OS、Node最低实际调用集、Windows/Electron、原生资源终态与受控运行仍待后续窗口。
