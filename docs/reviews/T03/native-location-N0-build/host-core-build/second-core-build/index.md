# 第二次构建证据索引

结论及边界：[delivery-summary.md](delivery-summary.md)。固定输入与批准：[input-closure-manifest.json](input-closure-manifest.json)、[authorization.md.raw](authorization.md.raw)。

- 实际执行：[build-once.result.json](build-once.result.json)、[driver-raw-manifest.json](driver-raw-manifest.json)、[driver-raw/supplier-log.0065.json](driver-raw/supplier-log.0065.json)。
- 冻结产物：[artifact-pins.json](artifact-pins.json)、[external-build-output-manifest.json](external-build-output-manifest.json)。
- 只读静态检查：[artifact-static-summary.json](artifact-static-summary.json)、[inspection-output-open-failure.json](inspection-output-open-failure.json)、[inspection-continuation-plan.json](inspection-continuation-plan.json)。
- 编译/依赖/链接：[generated-evidence-manifest.json](generated-evidence-manifest.json)、[compile-and-link-evidence.json](compile-and-link-evidence.json)、[used-dependencies.json](used-dependencies.json)、[sdk-alias-catalog-bindings.json](sdk-alias-catalog-bindings.json)。
- 预算：[read-account.json](read-account.json)、[outcome-closure-plan.json](outcome-closure-plan.json)。
- 独立审查：[outcome-independent-review.md](outcome-independent-review.md)。最终字节清单：[delivery-manifest.json](delivery-manifest.json)。

第一轮失败、优化产品/过程与本轮固定输入各自保留，不互相替换；本目录仅证明本轮 built-unverified / NOT_RUN。
