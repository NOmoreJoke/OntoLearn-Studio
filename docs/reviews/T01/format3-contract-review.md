# 格式3基础合同独立设计复核

审查者：`/root/recovery_design_review`，只读文档，未修改文件、未运行产品或GUI。对象：T01 format3-foundation-contract.md，对照总控格式提案/独立review及依赖澄清。

首轮结论：四语义及真实依赖边界正确，但需补5处：一致备份和两层结构清单；操作类型CAS、代次防ABA、全局claim/receipt；保留既有域no-op revision语义；checkpoint版本/coverage和辅助审计；hello有限错误和完整fixture责任。

已在合同第7节逐项落实。独立全文复核 SHA `3e5bbb4f8f68e257f641ca62721dc06f202cc00ed51cc5dba83bfa8139f9c45c` 后明确：**五项处置准确，无关键误改，可交 T00 统一合同。** 仅提醒旧引擎 `[2]` 需要作为有限终止诊断分支，不被新 `[3]` 精确校验提前挡掉，也不放宽null-session错误；随后仅追加这一澄清，未改已验产品源码/测试。

公共完整JSON和安全格式启动诊断通道仍由canonical/main唯一负责人冻结；SQL精确结构/跨层ready由Store/JobStore owner统一。此复核不批准metadata启用、数据库迁移、公共协议或共享文件写权，不替代指定模型或基础候选运行/发布验收。没有增加I05/I06整项或T10全包前置。
