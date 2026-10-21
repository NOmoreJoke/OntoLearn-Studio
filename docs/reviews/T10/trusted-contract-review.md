# T10/I06 受信导出合同提案内审

审查方 `/root/t10_private_review`，只读提案及固定 I06 e2c owning sources；没有执行 GUI、读取密钥或修改共享文件。本审查不批准接口，也不替代实现/实际验收。

发现并修复两项 P2：

- 首次guard的前后顺序不明确，可能先open/hash文件或创建staging后才检查私有范围。现picker只给候选位置，metadata-only bootstrap必须先于open/read/hash/mkdir，随后扩展绑定实际身份并持续重验。
- 完整包必需集合和“应用历史”表述不够精确。现逐项列出FR-1000全部必需内容，必要撤销闭包限定为可证明最小集合；一般历史/会话仍服从选择项，冲突须拒绝/协调schema，不暗带或静默删。

复核结论：两项关闭，当前提案未见新增逻辑缺口。私有密文/配置/audit/授权排除、同profile新project/context边界和X1–X6全部未验的表述与固定源码一致。

受审文件 `docs/iterations/T10/i06-trusted-transfer-contract-request.md`，SHA256 `6e52cdf4230b61034366963ef39808cbdf8b7e62655a0ec168d77706b311b7bd`。仍待总控协调I06/T01批准正式合同与实现，未新增canonical能力或争写共享路径。
