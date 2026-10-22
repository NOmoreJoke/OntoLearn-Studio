# Standalone unit source freeze

- Product: `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-semantic-parity-profile-20261023/packages/engine/tests/test_semantic_build_provenance.py`
- Bytes: 103779
- SHA-256: `7437a6ac4c5c2779abe46bb7f9a39dfba865d5b65dd7cd5fe9886817b3f3c48b`
- Python AST parse passed. Original 58 function/class declarations and original BUILDER_UNIT are unchanged.
- Added 35 top-level Python test functions, including parametrized negatives and an independent 28-case Node FD-stub block.
- Only AST parsing and Node --check were executed. No product import, unit test, CLI, prepare/finalize/build or child stub execution occurred.
- All earlier static receipts and raw Node source versions remain preserved.
- Writer paused after this vector. Formatting/lint and runtime verification are pending parent control and the independent review gate.

## Coverage mapping

- `test_standalone_contract_uses_real_hash_and_exact_roles` at line 1373
- `test_unknown_profile_rejects_before_any_file_read` at line 1396
- `test_standalone_preflight_has_no_imports_and_preserves_runtime_domain` at line 1408
- `test_standalone_unknown_internal_and_distribution_children_are_rejected` at line 1428
- `test_standalone_evidence_context_is_rechecked` at line 1439
- `test_standalone_paths_and_license_roles_are_exact` at line 1459
- `test_standalone_missing_authors_cannot_be_covered_by_license` at line 1477
- `test_standalone_mirror_caps_not_widened` at line 1489
- `test_standalone_notice_inventory_covers_undeclared_record_notices` at line 1497
- `test_standalone_prepare_returns_nested_paths_and_preserves_first_output` at line 1522
- `test_standalone_prepare_only_accepts_exact_builder_reservation` at line 1551
- `test_standalone_layout_rejects_source_ancestor_symlink_and_foreign_prefix` at line 1577
- `test_standalone_source_guard_dirty_check_is_exact_and_before_source_adoption` at line 1592
- `test_bounded_pyz_reads_real_compressed_code_without_execution` at line 1671
- `test_bounded_pyz_toc_rejects_ambiguous_or_unbounded_records` at line 1685
- `test_bounded_pyz_header_and_marshal_eof_are_exact` at line 1714
- `test_bounded_pyz_limits_toc_records_bytes_and_decompression_before_code` at line 1730
- `test_bounded_compressed_members_and_code_eof_are_exact` at line 1752
- `test_bounded_carchive_compares_logical_cap_separately_from_physical_size` at line 1775
- `test_bounded_carchive_toc_rejects_invalid_actual_members` at line 1790
- `test_bounded_carchive_options_do_not_override_unique_members` at line 1826
- `test_bounded_carchive_header_caps_and_target_marshal_are_enforced` at line 1839
- `test_standalone_archive_binds_exact24_anchor_and_independent_target` at line 1878
- `test_standalone_archive_rejects_missing_or_changed_real_code` at line 1889
- `test_standalone_finalize_and_external_binding_use_real_synthetic_archive` at line 1914
- `test_standalone_node_builder_uses_only_fd_run_stubs` at line 2336
- `test_standalone_exact_builder_reservation_keeps_open_stream_evidence` at line 2353
- `test_standalone_carchive_unknown_runtimehook_is_not_silently_collected` at line 2377
- `test_standalone_target_identity_must_equal_canonical_private_writer` at line 2388
- `test_standalone_declared_contract_bytes_must_be_exact` at line 2398
- `test_standalone_rejects_parent_contract_before_using_its_schema` at line 2407
- `test_code_graph_depth_and_node_caps_are_checked_before_normalization` at line 2414
- `test_standalone_carchive_known_option_cannot_select_another_layout` at line 2426
- `test_marshal_allocation_and_reference_preflight_happens_before_load` at line 2451
- `test_code_field_preflight_happens_before_marshal_load` at line 2470
