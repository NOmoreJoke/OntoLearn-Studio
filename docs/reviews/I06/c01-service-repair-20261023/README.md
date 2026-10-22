# C01 四路径服务修复交付

产品提交 1f123364e5e7b4315917c7caf163011858836fd0，tree 15df4913bd879f2db30d5213abc66c94e1505688。本目录为单独证据提交；未推送、未建 PR、未合并。

## 实际修改

- MF02：异步 preview 失败仅回收本次新建记录及捕获旧 context.application 的对应记录；保留成功所需 preview 和可复用旧 grant。新增真实 service/application/core 分层回归，以受控 doubles 验证同 owner 128 轮三处存储归零、旧 ID 不可确认，正常确认前后生命周期正确。
- ZN2：429 与 503 均实测两次同 URL/同 body 请求、两条 intent 以及最终 failed/audit。
- ZN3：纠正原 core 测试命名，加入 service 层 displayName-only 更新后的完整公开配置/version、原 grant 可复用及单次受控 HTTPS 请求回归。

仅四个产品路径变更，清单与字节见 product-candidate.json。AGENTS.md 为当前政策 overlay，未提交。四共享路径、Python、公共 DTO/schema、bridge/App/Store/bootstrap 未修改。

## 实测证据

定向 MF02 2、ZN2 58、ZN3 41，共101测试。原 npm run check child exit0：24个 TS 文件、1002个 TS 测试及1052个 Python 测试通过。原 npm run verify:sources child exit0，12来源核验。四文件 formatter 最终通过，四文件 lint 通过。

运行时 HEAD 为1f3b053d8a69d1f7ddb1e29c143f648d910fe689，四文件为冻结的未提交工作字节；这些字节随后原样形成产品提交。回执不声称当时已在新 commit HEAD 运行。五组实测各自保留 actual argv/cwd/full replacement env、PID、起止时间、child exit、完整双流及948项前后 source vector；全部一致。未重跑、未将文档提交冒充产品运行身份。

依赖从兼容既有本地安装复制至本隔离树，未安装或下载。复制内容及非符号链接 inode 独立核对，必要 venv 文本绑定和 RECORD 更新另有记录。环境不继承凭据、代理或工具选择器。setup最初两次精确环境断言失败均在复制前停止；第三次仅接受已观测 Darwin 自动 __CF_USER_TEXT_ENCODING 后成功，该键未加入传入 runtime env。首 formatter child1、gateway格式修复及重检通过均保留；格式变化含可选尾逗号移除，未称纯空白。

## 独立审查与边界

四路径实际 delta、runner静态修复前后、最终 source freeze 和五组实测收件有独立报告。首 runner 静态P2及修订关闭保留；未执行异常注入。压缩包逐项 inventory 覆盖原始双流、回执、source vectors、环境/计划、setup操作及首失败，不含依赖树或 home/tmp/cache。

MF01/P1 ordinary bootstrap/engine admission 尚未关闭；ZN1属T01；新候选的两份指定完整 fresh 模型审查待另行安排。未执行或声称真实供应商、OS凭据、native、GUI、e2e、打包、CI、PR、push、merge 验证。没有 baseline-red 运行，旧缺陷为静态证据，新回归为实际green。

外部固定交付 manifest 在证据提交后生成，记录产品提交、证据提交、压缩包及全量成员 SHA；manifest 不自包含。
