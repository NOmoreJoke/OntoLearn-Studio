# I05 保留源码逐文件字节覆盖矩阵

本件仅证明固定Git字节关系，不证明运行或指定审查通过。主候选2cf仅原字节采用date6891的22模块，不等于采用其整工程/全部测试。缺失不自行解释为撤回。

| 代号 | 固定ref |
|---|---|
| C4 | `523c478d5f39671c4ac7c1ea6997e51d3047d58e` |
| P1 | `0475d0ec6c486a63c7e8f62f11f35181da6b2576` |
| R | `3ef2f6952ed1a4f852da31c0bef7e8d8679752a5` |
| F | `6c1eec41091a997f898cb448bfc7d4000c154307` |
| D | `8e8b5126c69534c6259d37b2d3e88f75ef935aa0` |
| S | `43d56317f0bfbdfeec05efc583b306615ae54a30` |
| I | `91e98074a334931648e9b7c8f58a3b5e8f93a642` |
| T | `6891a5842302859a531cf82767c5a482417bc274` |
| M | `2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64` |
| B | `5f910b52c69d86a1076b2032e5d3c63e715947f3` |

集合方法：B→各phase固定树逐路径Git blob差异；产品为engine源Python、contracts源Python/TS、desktop/src代码；测试为engine/tests及tests中的程序；fixture、config与harness另列。排除docs/design/licenses/AGENTS是本delta表的统计边界，完整包另保留全部固定树。相同/不同均以独立SHA256核验；C4实际40c测试头与523除docs/AGENTS无差异。22supplier另查包含同base的根__init__。

| 阶段 | 产品same/changed/missing | 测试same/changed/missing | fixture缺失 |
|---|---|---|---|
| C4 | 3/16/2 | 0/2/16 | 0 |
| P1 | 12/3/2 | 0/0/15 | 26 |
| R | 13/5/2 | 0/0/18 | 27 |
| F | 15/17/13 | 0/1/43 | 27 |
| D | 21/12/13 | 0/1/44 | 27 |
| S | 21/12/13 | 0/1/45 | 27 |
| I | 21/12/13 | 0/1/46 | 27 |
| T | 22/11/13 | 0/1/47 | 27 |

以下每行只列该phase对B有实际delta的路径；—表示该路径不在该阶段delta，**不是不存在**。=相同主候选；~主候选存在但字节不同；X主候选没有该路径。每个source Git blob、bytes、独立SHA256及target都在coverage-matrix.json。

| 路径 | 类别 | C4 | P1 | R | F | D | S | I | T |
|---|---|---|---|---|---|---|---|---|---|
| `.github/workflows/ci.yml` | config | ~ | — | — | — | — | — | — | — |
| `apps/desktop/src/main/engine.ts` | product | — | — | — | ~ | ~ | ~ | ~ | ~ |
| `apps/desktop/src/main/index.ts` | product | ~ | — | — | ~ | ~ | ~ | ~ | ~ |
| `apps/desktop/src/main/jsonl.ts` | product | — | — | — | ~ | ~ | ~ | ~ | ~ |
| `apps/desktop/src/main/task-service.ts` | product | ~ | — | — | ~ | ~ | ~ | ~ | ~ |
| `apps/desktop/src/preload/index.ts` | product | ~ | — | — | — | — | — | — | — |
| `apps/desktop/src/renderer/src/App.tsx` | product | ~ | — | — | — | — | — | — | — |
| `apps/desktop/src/renderer/src/task-presentation.ts` | product | — | — | — | ~ | ~ | ~ | ~ | ~ |
| `packages/contracts/python/contract_v2.py` | product | ~ | — | — | = | = | = | = | = |
| `packages/contracts/src/index.ts` | product | ~ | — | — | ~ | ~ | ~ | ~ | ~ |
| `packages/contracts/src/v2.ts` | product | ~ | — | — | ~ | ~ | ~ | ~ | ~ |
| `packages/contracts/v2/binding-regressions.json` | config | — | — | — | ~ | ~ | ~ | ~ | ~ |
| `packages/contracts/v2/errors.json` | config | — | — | — | = | = | = | = | = |
| `packages/contracts/v2/fixtures.json` | config | ~ | — | — | ~ | ~ | ~ | ~ | ~ |
| `packages/contracts/v2/registry.json` | config | ~ | — | — | = | = | = | = | = |
| `packages/contracts/v2/schema.json` | config | ~ | — | — | = | = | = | = | = |
| `packages/engine/entrypoint.py` | config | ~ | — | — | ~ | ~ | ~ | ~ | ~ |
| `packages/engine/pyproject.toml` | config | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |
| `packages/engine/src/ontolearn_engine/__main__.py` | product | — | — | — | ~ | ~ | ~ | ~ | ~ |
| `packages/engine/src/ontolearn_engine/coordinator.py` | product | ~ | — | — | ~ | ~ | ~ | ~ | ~ |
| `packages/engine/src/ontolearn_engine/job_store.py` | product | ~ | — | — | ~ | ~ | ~ | ~ | ~ |
| `packages/engine/src/ontolearn_engine/project/__init__.py` | product | — | — | — | X | X | X | X | X |
| `packages/engine/src/ontolearn_engine/project/applications.py` | product | — | — | — | X | X | X | X | X |
| `packages/engine/src/ontolearn_engine/project/compensation.py` | product | — | — | — | X | X | X | X | X |
| `packages/engine/src/ontolearn_engine/project/domain_changesets.py` | product | — | — | — | X | X | X | X | X |
| `packages/engine/src/ontolearn_engine/project/draft_plan.py` | product | — | — | — | X | X | X | X | X |
| `packages/engine/src/ontolearn_engine/project/format3.py` | product | — | — | — | X | X | X | X | X |
| `packages/engine/src/ontolearn_engine/project/project_host.py` | product | — | — | — | X | X | X | X | X |
| `packages/engine/src/ontolearn_engine/project/project_lifecycle.py` | product | — | — | — | X | X | X | X | X |
| `packages/engine/src/ontolearn_engine/project/source_content.py` | product | — | — | — | X | X | X | X | X |
| `packages/engine/src/ontolearn_engine/project/transactions.py` | product | — | — | — | X | X | X | X | X |
| `packages/engine/src/ontolearn_engine/project/workspace.py` | product | — | — | — | X | X | X | X | X |
| `packages/engine/src/ontolearn_engine/protocol.py` | product | ~ | — | — | — | — | — | — | — |
| `packages/engine/src/ontolearn_engine/quality/__init__.py` | product | — | = | = | = | = | = | = | = |
| `packages/engine/src/ontolearn_engine/quality/rule_calendar.py` | product | — | = | = | = | = | = | = | = |
| `packages/engine/src/ontolearn_engine/quality/rule_comparator.py` | product | — | = | = | = | = | = | = | = |
| `packages/engine/src/ontolearn_engine/quality/rule_firing.py` | product | — | = | = | = | = | = | = | = |
| `packages/engine/src/ontolearn_engine/quality/rule_numbers.py` | product | — | = | = | = | = | = | = | = |
| `packages/engine/src/ontolearn_engine/quality/rule_profile.py` | product | — | = | = | = | = | = | = | = |
| `packages/engine/src/ontolearn_engine/quality/rule_revalidation.py` | product | — | — | = | = | = | = | = | = |
| `packages/engine/src/ontolearn_engine/quality/rule_terms.py` | product | — | = | = | = | = | = | = | = |
| `packages/engine/src/ontolearn_engine/resources.py` | product | ~ | ~ | ~ | ~ | = | = | = | = |
| `packages/engine/src/ontolearn_engine/semantic.py` | product | ~ | ~ | ~ | ~ | ~ | ~ | ~ | = |
| `packages/engine/src/ontolearn_engine/semantic_error_adapter.py` | product | ~ | = | = | = | = | = | = | = |
| `packages/engine/src/ontolearn_engine/semantic_execution.py` | product | ~ | ~ | ~ | ~ | = | = | = | = |
| `packages/engine/src/ontolearn_engine/semantic_offline.py` | product | = | = | = | = | = | = | = | = |
| `packages/engine/src/ontolearn_engine/semantic_probe.py` | product | X | — | — | — | — | — | — | — |
| `packages/engine/src/ontolearn_engine/semantic_profile_directsteps.py` | product | — | — | — | — | = | = | = | = |
| `packages/engine/src/ontolearn_engine/semantic_profile_input.py` | product | — | — | — | = | = | = | = | = |
| `packages/engine/src/ontolearn_engine/semantic_profile_probe.py` | product | — | X | X | X | X | X | X | X |
| `packages/engine/src/ontolearn_engine/semantic_profile_production.py` | product | — | — | — | ~ | = | = | = | = |
| `packages/engine/src/ontolearn_engine/semantic_profile_restore.py` | product | — | — | ~ | ~ | = | = | = | = |
| `packages/engine/src/ontolearn_engine/semantic_profile_restore_budget.py` | product | — | — | ~ | ~ | = | = | = | = |
| `packages/engine/src/ontolearn_engine/semantic_query.py` | product | = | = | = | = | = | = | = | = |
| `packages/engine/src/ontolearn_engine/semantic_samples.py` | product | X | X | X | X | X | X | X | X |
| `packages/engine/src/ontolearn_engine/semantic_scopes.py` | product | = | = | = | = | = | = | = | = |
| `packages/engine/src/ontolearn_engine/semantic_turtle.py` | product | ~ | = | = | = | = | = | = | = |
| `packages/engine/src/ontolearn_engine/storage.py` | product | — | — | — | ~ | ~ | ~ | ~ | ~ |
| `packages/engine/src/ontolearn_engine/worker.py` | product | ~ | — | — | — | — | — | — | — |
| `packages/engine/tests/test_frame_corpus.py` | test | ~ | — | — | — | — | — | — | — |
| `packages/engine/tests/test_native_inventory.py` | test | X | — | — | — | — | — | — | — |
| `packages/engine/tests/test_project_applications.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_project_business3_contract.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_project_changeset_service.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_project_changeset_stdio.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_project_compensation.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_project_create_contract.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_project_draft_plan.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_project_format3.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_project_host_read_services.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_project_job_format3.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_project_source_table_material.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_project_source_transport.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_project_startup_contract.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_project_startup_stdio.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_project_transactions.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_project_workspace.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_quality_profile_revalidation.py` | test | — | — | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic.py` | test | X | X | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_error_adapter.py` | test | X | X | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_error_reasons.py` | test | X | X | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_execution.py` | test | X | X | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_fresh_probe.py` | test | X | — | — | — | — | — | — | — |
| `packages/engine/tests/test_semantic_lexical.py` | test | X | X | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_lexical_runtime.py` | test | X | — | — | — | — | — | — | — |
| `packages/engine/tests/test_semantic_profile_directsteps.py` | test | — | — | — | — | X | X | X | X |
| `packages/engine/tests/test_semantic_profile_errors.py` | test | — | X | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_profile_imports.py` | test | — | X | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_profile_input.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_semantic_profile_integration.py` | test | — | X | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_profile_limits.py` | test | — | X | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_profile_production.py` | test | — | — | — | X | X | X | X | X |
| `packages/engine/tests/test_semantic_profile_restore.py` | test | — | — | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_profile_restore_limits.py` | test | — | — | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_profile_shape_entry.py` | test | — | — | — | — | — | X | X | X |
| `packages/engine/tests/test_semantic_profile_source.py` | test | — | X | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_query_tokens.py` | test | X | X | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_rdfs_basis_determinism.py` | test | X | X | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_runtime.py` | test | X | — | — | — | — | — | — | — |
| `packages/engine/tests/test_semantic_scopes.py` | test | X | X | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_selected_projection.py` | test | X | X | X | X | X | X | X | X |
| `packages/engine/tests/test_semantic_shacl_date_policy.py` | test | — | — | — | — | — | — | — | X |
| `packages/engine/tests/test_semantic_shacl_entry.py` | test | — | — | — | — | — | — | X | X |
| `packages/engine/tests/test_semantic_string_identity.py` | test | X | X | X | X | X | X | X | X |
| `scripts/build-engine.mjs` | harness | ~ | — | — | ~ | ~ | ~ | ~ | ~ |
| `scripts/i05-build-inventory.py` | harness | X | — | — | — | — | — | — | — |
| `scripts/prepare-i05-fixture.py` | harness | X | — | — | — | — | — | — | — |
| `scripts/verify-i05-runtime.py` | harness | X | — | — | — | — | — | — | — |
| `scripts/verify-i05.py` | harness | X | — | — | — | — | — | — | — |
| `tests/e2e/i05-semantics.spec.ts` | test | X | — | — | — | — | — | — | — |
| `tests/fixtures/quality/approved-T09-873c8c0/content/learning/checks.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/content/learning/course.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/content/learning/glossary.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/content/learning/transfer-inputs.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/manifest.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/E.5.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/G-base.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/G-behavior.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/G-map-empty.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/alarms.csv` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/cases.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/conventions.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/coverage.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/equipment-duplicate-key.csv` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/equipment-missing-key.csv` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/equipment-updated.csv` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/equipment.csv` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/unclosed-high.rq` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/fr505-extension-cases.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/profile-revalidation-v1/cases.json` | fixture | — | — | X | X | X | X | X | X |
| `tests/fixtures/quality/profile-v1/calendar-oracles.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/profile-v1/comparison-matrix.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/profile-v1/firing-cases.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/profile-v1/lexical.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/profile-v1/manifest.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/profile-v1/numeric-oracles.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/fixtures/quality/real-executor-acceptance-inputs.json` | fixture | — | X | X | X | X | X | X | X |
| `tests/unit/contract-v2.test.ts` | test | ~ | — | — | — | — | — | — | — |
| `tests/unit/semantic-bridge.test.ts` | test | X | — | — | — | — | — | — | — |
| `tests/unit/t01-business3-contract.test.ts` | test | — | — | — | X | X | X | X | X |
| `tests/unit/t01-changeset-canonical.test.ts` | test | — | — | — | X | X | X | X | X |
| `tests/unit/t01-changeset-runtime.test.ts` | test | — | — | — | X | X | X | X | X |
| `tests/unit/t01-source-table-material.test.ts` | test | — | — | — | X | X | X | X | X |
| `tests/unit/t01-startup-canonical.test.ts` | test | — | — | — | X | X | X | X | X |
| `tests/unit/t01-startup-presentation.test.ts` | test | — | — | — | X | X | X | X | X |
| `tests/unit/t01-startup-supervisor.test.ts` | test | — | — | — | X | X | X | X | X |
| `tests/unit/task-runtime.test.ts` | test | — | — | — | ~ | ~ | ~ | ~ | ~ |
| `uv.lock` | config | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |

22supplier与各前驱的直接路径关系及主候选SHA见JSON supplier22；同名旧semantic、execution、restore等被改写时不标字节已覆盖。T的delta产品same22和supplier22是不同集合，前者含Python contract且不含同base根__init__，不能混淆。

未跟踪26项仅opaque stat/SHA，未复制为冻结产品；五种未匹配本轮固定phase的字节为calculation semantic、两树rule_terms、lexical turtle、restore-tests两源。lexical semantic等C4、calculation turtle等C4、samples等C4..T但M缺失。所有保留/撤回需原owner明确，原表仅给可核字节关系。

