# 按路径与语义加载的领域模块

来源：`review-policy-20261029/checklist-routing.md`（2026-10-29 已获用户采纳）。触发线索只是提示，模块不因文件名更换失效；反之，路径命中但只有已证明非行为改动（例如逐字节判定的行尾换行规范化）可不加载领域全表。评审政策、候选证据脚本、CI 和清单本身的改动单独按治理改动审（最低 L1，削弱门禁升 L2），不得用"仅文档/测试"跳过。

| 模块      | 触发线索（包含但不限于）                                                                      | 重点                                                                         | L2 主责                 |
| --------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ----------------------- |
| security  | main/preload/csp.ts、权限、来源、错误输出、外联、依赖                                         | sender/frame、CSP、白名单、输入/路径/大小限制、最小权限、敏感数据            | A                       |
| storage   | storage.py、project/**、job_store、schema/迁移/事务/快照/撤销                                 | 唯一 Store.commit、原子性/旧基线、崩溃恢复、物理保护、历史不变、备份真实恢复 | A；B 核实测             |
| contracts | packages/contracts、protocol.py、invalidation、跨进程消息                                     | 版本/严格校验、身份绑定、错误码、能力声明、生产消费一致                      | A                       |
| engine    | semantic/reasoning/SHACL/query、coordinator/worker、rdf_snapshot/resources/memory_guard       | 语义正确性、终止/取消/资源边界、快照隔离、确定性/非法外联                    | A；B 核真实引擎用例     |
| agent     | 网关、凭据、模型配置、提示输入、工具调用、外发授权                                            | 凭据不出主进程、显式授权、注入隔离、工具白名单、草稿不自确认、退路/预算      | A；B 核 eval 与失败场景 |
| packaging | build、workspace package 配置、electron-builder、build-engine、prepare-fr003、pyproject/locks | 二进制/资源一致、跨OS/架构、依赖、签名/安装/干净设备、包内真实运行           | B；A 核供应链/凭据      |
