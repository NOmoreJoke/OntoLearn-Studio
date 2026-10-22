# 独立静态子任务：Z六项及M collector边界

2026-10-23。独立 agent `/root/t11_independent_review` 只读固定7d28fdb对应源码及归档报告，未改文件、未跑测试/GUI。

- Z-F1：重复schema条件成立，整个分支不应称不可达；删重复parse但保finite(now)。
- Z-F2：readBound之外，large和installerFormat也有realpath/stat→open或fd/path竞争；SHA不能防先耗资源。同fd/fstat/有界读取并保受控目录条件，不能承诺仅fstat消除祖先竞争；小型确定性模拟，无压力/SQLite损坏/new-native扩展。
- Z-F3：fail只累积，缺dest分支可达；前置错误仍阻止consistent=true。显式目标错误并停止该绑定；不据此认定可虚假放行。
- Z-F4：OS/arch门与后续工具均有PATH依赖，已知系统命令绝对路径；bash-n不等于目标机运行。
- Z-F5=M-F-H③：DOS头和PE offset预检查缺失；现为异常失败，未证错误接受。目标Windows小文件边界验证仍须实际执行。
- Z-F6=M-F-H①：半成品目录；推荐保失败原件并增加完成/失败状态、消费端拒无complete，不采用自动删目录。
- M-F-H②独立来源问题未由六项全解决；同解包根不足证明同包，须可信包内清单/hash与真实安装/解包证据。
- M-F-I是结构/声明级边界；明确不验证签名链/安装器实质即可，不擅加签名库或安装执行。

原Z六项P4与M低级别不变，不自动关闭或改M NotPass；后续新候选、实际验证与指定双审门保留。
