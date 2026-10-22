# F1/N1 unit delta freeze

- Unit bytes/SHA256: 120578 / ee09707ab895bdfa8e831f38a200e5445d0a37d12c1fb8a603987efd4700edc9
- Original c706 58 declarations and BUILDER_UNIT preserved. All previous d468 declarations preserved except the standalone Node test expected case count (28 to31).
- Six added Python relation tests and one added Node machine-mapping case; hash IO cases now run over all three stub phases.
- Python AST/Ruff format check/Ruff check/Node --check passed. The initial E501 failure raw receipt remains.
- No runtime execution. buildScratch guard/threshold are verified as an I05 external policy; builderEnforced/osHardLimitImplemented/runtimeGuarantee remain false.
- All earlier reports and source freeze receipts remain unchanged. Writer paused.

## Added test mapping

- test_standalone_contract_source_and_frozen_domains_are_relational: 2731
- test_standalone_contract_target_and_launcher_domains_match_archive_and_runtime: 2768
- test_standalone_contract_separates_actual_base_historical_components_and_root_approval: 2820
- test_standalone_contract_defines_conditional_unit_without_granting_build_execution: 2838
- test_standalone_contract_requires_all_sixteen_negative_test_domains: 2858
- test_standalone_scratch_policy_is_single_external_accounting_domain_without_quota_claims: 2895
