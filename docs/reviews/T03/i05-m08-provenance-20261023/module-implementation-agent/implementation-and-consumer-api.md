# 私有 provenance 模块实施与消费接口

本提交只新增私有模块、其针对性单元测试和本目录记录。冻结合同未改：36587 bytes，SHA-256 `9d97a6a233b47abc23064a9a8f8330080d62f39b3db981de14a148880e202a04`。AGENTS 覆盖保持 unstaged；未写入口、Node builder、旧 probe/tests、依赖或原始输入。

实现 bounded strict JSON/精确角色 schema、22 supplier + 2 private + 4 resources + 2 inputs + 8 distributions、CPython 3.12 完整 identity 与仅 filename 归一化代码 fingerprint、literal 双赋值 anchor 的 loader.get_code 预检、不可变 opaque evidence/进程上下文复核。构建侧只 programmatic：读取 Git HEAD 对应实际源 bytes，静态审计真实 PYZ、data/METADATA/licenses/native 存在与完整 engine 目录，再在目录外产生未批准绑定。入口仅处于外部 launcher/PYZ/file-binding 域，不被伪装成可在运行时 get_code 的 module。

## 构建约定

`prepare_build(repository_root, output_dir)` 的 output_dir 必须是仓库 `build/i05-provenance/<fresh-lowercase-UUID>`，调用者不预创建。独占返回：

- `provenancePath`: `<run>/provenance/i05-private-build-provenance-v1.json`
- `contractPath`: `<run>/provenance/i05-private-contract-v1.json`
- `generatedDir`: `<run>/generated`
- `anchorPath`: `<run>/generated/_i05_private_build_anchor.py`

`finalize_build(repository_root, output_dir, engine_dir)` 只接受 `<run>/dist/ontolearn-engine`，返回 `bindingPath`（`<run>/artifact-binding-v1.json`）、`bindingSha256`、`engineDirectory`、`provenanceSha256`。binding `rootApproved=false`，独占写入，不覆盖。实际输入固定于 frozen `_MEIPASS/ontolearn_engine/probe_inputs/<两固定原文件>`，源包同名 `probe_inputs`。

`verify_external_binding(binding_path, artifact_dir, *, expected_sha256)` 需要外部提供的 lowercase64 SHA，绑定文件必须在 artifact 外，核对完整目录再返回 JSON-safe dict：`expectedBindingSha256`、`actualBindingSha256`、`artifactDirectory`、`inventoryVerified=true`、`sourceCommit`、`provenanceSha256`、`rootApproval="unknown; supplied-external-digest-verified, no run executed"`。它验证给定 digest 对应的字节，不产生批准记录，也不执行包。

## I05 运行时消费

签名固定为 `load_frozen_provenance(*, expectations: dict) -> FrozenBuildEvidence`、`verify_loaded_modules(evidence, modules: dict[str, ModuleType]) -> dict`、`verify_native_extension(evidence) -> dict`。

preflight 在 observer 前调用，只执行有界 stdlib/文件/anchor code 静态核对，不执行 anchor。opaque evidence 必须仅保存在局部变量并原样交给后两个 verifier；不能直接放 header/序列化，也不需要读取 `_manifest` 等内部字段。所有 verifier 返回的 dict 都是独立 JSON-safe 值，后续修改返回 dict 不会修改 evidence。

observer 安装后，I05 自己显式导入实际 22 modules 与 `wcwidth._wcwidth_c`（不得假定 Validator/import wcwidth 会偶然加载 extension），再调用两个 verifier。reader 不主动导入任何 target。缺少/伪造/越界 native loader 必须失败，不返回 pure-Python fallback Pass。所有失败跨消费边界只暴露 `BuildProvenanceFault.code` 固定 `BUILD_PROVENANCE_*`，不附私有路径或原始异常文本。

`verify_loaded_modules` 精确返回 keys/值域：

| key | value |
| --- | --- |
| rootApproval | `"unknown"` |
| provenanceSha256 | 实际 manifest bytes 的 lowercase64 SHA |
| packageCodeBoundToSource | `"verified-python-code-and-identified-resources-only"` |
| nativeSourceByteEquivalence | `"unknown"` |
| semanticParity | `"unknown"` |
| supplierAndPrivateModules | 24 行 `[{module, path, actualCodeSha256}]`，22 supplier 后接 2 private |
| loadedDistributionModules | 当前已加载的 8 distribution Python modules 的 `[{module, path, actualCodeSha256}]` |
| actualPythonSharedLibrary | 实际 artifact 文件 `{path, bytes, sha256}` |
| pythonSharedLibrarySourceByteEquivalence | `"unknown"` |
| entrypointDomain | `"external-launcher-PYZ-binding-only"` |

`verify_native_extension` 精确返回 keys/值域：

| key | value |
| --- | --- |
| module | `"wcwidth._wcwidth_c"` |
| loader | `"ExtensionFileLoader"` |
| path | artifact 内安全相对路径 |
| actualArtifactFile | 实际 artifact `{path, bytes, sha256}` |
| installedSourceFile | manifest 的 installed-source `{path, bytes, sha256}` |
| sourceByteMatch | 实际 artifact SHA 与 installed-source SHA 字节比较 bool |
| nativeSourceByteEquivalence | `"unknown"` |
| rootApproval | `"unknown"` |

I05 可把这两个结果 dict 分别放进 header 的 JSON-safe identity 子字段；可从 `provenanceSha256` 关联身份，不将 opaque evidence 当作 JSON。`sourceByteMatch` 只报告字节比较：即使 true，也不能自动提升为 native semantic/source 等价。上述字段不表示 whole-Python-code、整个 native artifact、root approval 或 semantic parity。

## 已运行验证与边界

最终目标文件 ruff check 与 ruff format --check 通过；定向 pytest **86 passed in 1.74s**。第一轮 style failure 原始输出已保存（20 errors，自动修 1 个，余 19 个），后续 2 个 style failure 也保留。实际 argv、exit、日志 hashes、产品 hashes 在 `implementation-receipt.json`。

这些是临时小输入/假的已有 CodeType/ModuleType/ExtensionFileLoader 身份夹具与 mock archive 单元验证；测试原始两 JSON 仅复制原 bytes，不执行其语义。没有实际导入 native、没有执行真实 prepare 全仓采集、PyInstaller build、frozen launcher、GUI、full-v1/B1、旧 probe test、enginecheck 或全量 pytest。真实包的 external expected digest 由 root 后续整合与批准；本提交不能报 runtimePass。
