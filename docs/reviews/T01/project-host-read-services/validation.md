# 私有项目宿主读取：实施与验证记录

本阶段的新读取模块与52项真实服务测试已完成，独立代码审查的两项P2已关闭。创建/resolution仍仅为待批合同；合同审查记录另列，未将提案登记为实现。完整T01 Goal继续，未申请push/PR/merge。

## 候选与范围

- 树：`.worktrees/T01-project-host-read-services`，分支 `feature/weekly-t01-project-host-read-services`，批准base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 精确授权 `0c96119b…0757`；固定清单 `d0c242de…e1c6` 的48项逐Git原件、bytes和SHA一致，未修改这些继承项。不存在whole-commit采用。
- 新代码 `project/project_host.py`：15777B，SHA256 `a142d9dc9e3c56c51110fd21125c65cc72a19631743be92ccf2e8be98da4edeb`。
- 新测试 `test_project_host_read_services.py`：25403B，SHA256 `f27a53c8f69398bd16ec7b40fadd2d03e28927a2f5aa3f9751569bc6583ede64`。
- 实现文档 `project-host-read-services.md`：12820B，SHA256 `a27a4d0a8a26cb99558eae529e323b7310fd35b3edd24bf6ee57138ba317ed3f`。
- 保护AGENTS 15852B/`78df2825…a759`、共同指令17891B/`e437121a…b0`保持原字节；AGENTS不stage。

## 最终实际验证

`UV_CACHE_DIR=/tmp/t01-project-host-runtime-cache/uv-seeded npm run check` 最终04：启动原件exec `aba62e`/session5551，实际终态原件 `70ca9d` exit0。完整log8441B/SHA256 `f396e35b42e4dbcd264aec18055e4716ede138ccec870b211a511ae768a19524`。lint、Prettier、类型、22个TS测试文件1125项、构建、ruff及Python全套均通过；Python为2841 passed、44既有skipped。52项新服务用例包含在该最终全套中。该轮开始到结束，上述三项输入保持不变。

`npm run verify:sources` 原件 `60f3c4` exit0，12个归档源逐核；log111B/SHA256 `1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536`。只核原归档资料，不把它当新产品正确性证明。新增合同在独立文档审查/格式检查中单独核验，不假称它在此前已被全check格式阶段读取。

代码独审报告28048B/SHA256 `df10a77a18f7345b00b7beb495b111b3790d95110b9b2ce634b41a168db910c9`，已停止写入。独审直接读取最终源码/新测试/实现文档、48项继承保护和最终check原log，并只做必要定点复核。该报告不是指定ZCode GLM-5.3/最高与MiniMax M3.1-Flash/xhigh同版双审替代物。

## 失败、意见与中间结果

- 环境UV01/02实际exit2：把独立cache放在尚未创建的 `.venv` 内导致目录不是有效venv；确认仅cache后移走该新建目录。UV03实际网络超时，未解析hatchling官方metadata。未改依赖/锁。UV04对官方全局artifact cache作独立APFS clone后离线同步成功，构建当前树editable engine；没有复制/借用其他工作树venv。
- npm01中断后handle缺失，且实际无该npm进程，不登记成功。npm02独立缓存offline实际ENOTCACHED失败。npm03对官方全局npm artifact cache作独立clone后offline `npm ci`实际exit0，安装440包；未使用其它工作树node_modules。所有cache、环境、构建和临时DB独立。
- 首目标pytest01：31 passed/2 failed。两个失败发生在损坏fixture尝试改受immutable trigger保护行；只在新测试fixture临时移除并按原SQL重建trigger，制造真实损坏后再核零修复。原失败保留，不冒称产品失败被忽略。
- 新ruff01的unused import/长行/闭包绑定与ruff03的新增循环闭包问题均在本新测试内修复；原log保留。目标pytest02/03/04/05分别36/45/47/52 passed。最终52项由check04覆盖；不把未配最终源码身份的旧目标结果当final。
- 独审P2实际格式头：旧实现只核配置target3，未来header4仍能读。修后每次数据库读取在BEGIN内实际核user_version3；独审修前 `2dc34e`、修后 `efa3f2`，零写和完整dump均实测。缓存后页无DB I/O，能力失效由真实owner close reader的后续合同负责。
- 独审P2游标复活：旧随机token只排除活动token，重复刚消费token可把旧token重新安装；修前 `9eadff`。修后reader namespace+从不复用的有界counter+随机suffix，固定entropy下连续页/跨catalog/跨reader和耗尽均实测；修后 `a7f1d5`。当前无consumed-token无限日志。
- clock失败/回退安全清缓存、authorizer禁止同值/异值header写的负控均按独审建议加入。完整dump不能单独覆盖header，不能只用dump相等推零写。
- 全check01/02/03均实际exit0，但依次属于中间实现/测试；01期间随后新增边界，02/03之后均有新测试或实现修复，不沿用为final。最终检查04完成后不再无变化复测。
- 原件整理首轮因异步通知型tool output没有call_id而停止；整理脚本修后把这类原记录单独标明，未伪造调用配对。归档保留完整120组调用/输出、独立通知及首轮整理失败；未收集推理记录或运行数据库。最终归档/成员/源行偏移与哈希见original-evidence-index.json。

## 结论边界与下一步

真实Store3内部一致读取、有限目录分页和指定draft投影机制已被源码、SQLite authorizer、完整逻辑dump、事务trace、异常反例与独审共同核验。未运行本机GUI/Electron/e2e/native/HMR或审查应用，未接真实位置许可、公开IPC或人类选择。未用本阶段单元结果代替打包、生产、FR-001–006/804或全T01完成证据。

按根本次分阶段交付指示，创建/resolution合同的精确原库绑定与完整投影预算意见继续独立修订；该合同及未闭合同报告不包含在本读取阶段Git/manifest内，后随单独docs/process提交交付，不阻塞稳定读取代码交付。只有根收口并给下一精确授权后才可扩本阶段两代码路径；指定双模型新审、CI、正常develop合并、远端及原44/57P0门继续保留。
