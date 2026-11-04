# 内容归属与共享索引

I01→P00独立物性输入/P01/当前快照准入→R00/M01–M15→O01/O02；物性失败回P00，其他修复回R00。K01仍是动力学录入后检查。教材/案例保留单一正文。

| 文件 | 维护模块 | 共享调用 | 内容角色 |
|---|---|---|---|
| [LESSONS_LEARNED.md](../LESSONS_LEARNED.md) | M15 | O02 | compatibility |
| [SKILL.md](../SKILL.md) | I01 | R00, O01, O02 | entry |
| [agents/openai.yaml](../agents/openai.yaml) | I01 | — | invocation |
| [assets/column-split/bt_split.bkp](../assets/column-split/bt_split.bkp) | M06 | M15 | case_asset |
| [assets/column-split/bt_split.inp](../assets/column-split/bt_split.inp) | M06 | M15 | case_asset |
| [assets/column-split/bt_split_hx.bkp](../assets/column-split/bt_split_hx.bkp) | M06 | M15 | case_asset |
| [assets/column-split/bt_split_hx.inp](../assets/column-split/bt_split_hx.inp) | M06 | M15 | case_asset |
| [assets/column-split/bt_split_no_hx.inp](../assets/column-split/bt_split_no_hx.inp) | M06 | M15 | case_asset |
| [assets/column-split/styrene_heatpump.bkp](../assets/column-split/styrene_heatpump.bkp) | M06 | M15 | case_asset |
| [assets/column-split/styrene_heatpump.inp](../assets/column-split/styrene_heatpump.inp) | M06 | M15 | case_asset |
| [assets/pfd-layout/pdo-energy-validation.json](../assets/pfd-layout/pdo-energy-validation.json) | M09 | M15 | case_asset |
| [assets/steam-generation/README.md](../assets/steam-generation/README.md) | M05 | M15 | case_asset |
| [assets/steam-generation/verification.txt](../assets/steam-generation/verification.txt) | M05 | M15 | case_asset |
| [assets/steam-generation/waste_heat_steam_generation.inp](../assets/steam-generation/waste_heat_steam_generation.inp) | M05 | M15 | case_asset |
| [modules/intake.md](../modules/intake.md) | I01 | — | classification |
| [modules/migration-ledger.json](../modules/migration-ledger.json) | R00 | I01, O01, O02 | routing_metadata |
| [modules/output/check.md](../modules/output/check.md) | O02 | — | output_check |
| [modules/output/evidence-format.md](../modules/output/evidence-format.md) | O02 | I01, R00, O01, M09, M15 | evidence_contract |
| [modules/output/index.md](../modules/output/index.md) | O01 | — | output |
| [modules/output/kinetics-validation.md](../modules/output/kinetics-validation.md) | O02 | I01, R00, M01, M03, M15 | stage_check |
| [modules/output/methods/run-audit.md](../modules/output/methods/run-audit.md) | O02 | I01, R00, M01, M03, M15 | stage_check |
| [modules/output/process-acceptance.md](../modules/output/process-acceptance.md) | O02 | — | output_check |
| [modules/output/properties-validation.md](../modules/output/properties-validation.md) | P00 | I01, R00, M01, M03, M15 | compatibility |
| [modules/registry.json](../modules/registry.json) | R00 | I01, O01, O02 | routing_metadata |
| [modules/run/M01-properties-and-boundaries.md](../modules/run/M01-properties-and-boundaries.md) | M01 | — | run_module |
| [modules/run/M02-distillation.md](../modules/run/M02-distillation.md) | M02 | — | run_module |
| [modules/run/M03-reactors.md](../modules/run/M03-reactors.md) | M03 | — | run_module |
| [modules/run/M04-pressure-transport.md](../modules/run/M04-pressure-transport.md) | M04 | — | run_module |
| [modules/run/M05-heat-and-energy.md](../modules/run/M05-heat-and-energy.md) | M05 | — | run_module |
| [modules/run/M06-thermal-coupling.md](../modules/run/M06-thermal-coupling.md) | M06 | — | run_module |
| [modules/run/M07-hydraulics-rating.md](../modules/run/M07-hydraulics-rating.md) | M07 | — | run_module |
| [modules/run/M08-numerics.md](../modules/run/M08-numerics.md) | M08 | — | run_module |
| [modules/run/M09-execution-interfaces.md](../modules/run/M09-execution-interfaces.md) | M09 | — | run_module |
| [modules/run/M10-solids.md](../modules/run/M10-solids.md) | M10 | — | run_module |
| [modules/run/M11-mass-transfer.md](../modules/run/M11-mass-transfer.md) | M11 | — | run_module |
| [modules/run/M12-special-materials.md](../modules/run/M12-special-materials.md) | M12 | — | run_module |
| [modules/run/M13-dynamics-batch.md](../modules/run/M13-dynamics-batch.md) | M13 | — | run_module |
| [modules/run/M14-optimization-custom.md](../modules/run/M14-optimization-custom.md) | M14 | — | run_module |
| [modules/run/M15-troubleshooting.md](../modules/run/M15-troubleshooting.md) | M15 | — | run_module |
| [modules/run/diagnostics/aspen-input-completeness-and-delivery-lessons.md](../modules/run/diagnostics/aspen-input-completeness-and-delivery-lessons.md) | M15 | O02 | diagnostic |
| [modules/run/diagnostics/aspen-plus-textbook-guide-fixes.md](../modules/run/diagnostics/aspen-plus-textbook-guide-fixes.md) | M15 | O02 | diagnostic |
| [modules/run/diagnostics/calculator-flowsheeting-options-fixes.md](../modules/run/diagnostics/calculator-flowsheeting-options-fixes.md) | M15 | O02 | diagnostic |
| [modules/run/diagnostics/column-splitting-and-heat-integration-additional-fixes.md](../modules/run/diagnostics/column-splitting-and-heat-integration-additional-fixes.md) | M15 | M05, M06, M08, O02 | diagnostic_case |
| [modules/run/diagnostics/com-attach-and-license-env.md](../modules/run/diagnostics/com-attach-and-license-env.md) | M15 | O02 | diagnostic |
| [modules/run/diagnostics/double-effect-distillation-and-design-spec-fixes.md](../modules/run/diagnostics/double-effect-distillation-and-design-spec-fixes.md) | M15 | O02 | diagnostic |
| [modules/run/diagnostics/double-effect-user-workflow-fixes.md](../modules/run/diagnostics/double-effect-user-workflow-fixes.md) | M15 | M06, O02 | diagnostic_case |
| [modules/run/diagnostics/general-verification-methods.md](../modules/run/diagnostics/general-verification-methods.md) | M15 | O02 | diagnostic |
| [modules/run/diagnostics/heat-carrier-and-salt-properties-fixes.md](../modules/run/diagnostics/heat-carrier-and-salt-properties-fixes.md) | M15 | O02 | diagnostic |
| [modules/run/diagnostics/historical-lessons.md](../modules/run/diagnostics/historical-lessons.md) | M15 | O02 | diagnostic |
| [modules/run/diagnostics/initialization-and-coupling-cases.md](../modules/run/diagnostics/initialization-and-coupling-cases.md) | M15 | O02 | diagnostic |
| [modules/run/diagnostics/kinetics-recycle-and-delivery-reasoning-additional-fixes.md](../modules/run/diagnostics/kinetics-recycle-and-delivery-reasoning-additional-fixes.md) | M15 | M05, M06, M08, O02 | diagnostic_case |
| [modules/run/diagnostics/pdo-heat-integration-and-delivery-lessons-additional-fixes.md](../modules/run/diagnostics/pdo-heat-integration-and-delivery-lessons-additional-fixes.md) | M15 | M05, M06, M08, O02 | diagnostic_case |
| [modules/run/diagnostics/pdo-heat-integration-and-delivery-lessons-fixes.md](../modules/run/diagnostics/pdo-heat-integration-and-delivery-lessons-fixes.md) | M15 | O02 | diagnostic |
| [modules/run/diagnostics/property-provenance-and-repair-gates.md](../modules/run/diagnostics/property-provenance-and-repair-gates.md) | M15 | O02 | diagnostic |
| [modules/run/diagnostics/rplug-native-sensitivity-fixes.md](../modules/run/diagnostics/rplug-native-sensitivity-fixes.md) | M15 | M03, M08, M09, M14, O02 | diagnostic_case |
| [modules/run/diagnostics/run-verification-and-reconcile.md](../modules/run/diagnostics/run-verification-and-reconcile.md) | M15 | O02 | diagnostic |
| [modules/run/diagnostics/thermally-coupled-distillation-fixes.md](../modules/run/diagnostics/thermally-coupled-distillation-fixes.md) | M15 | O02 | diagnostic |
| [modules/run/diagnostics/three-component-thermal-coupling-case-fixes.md](../modules/run/diagnostics/three-component-thermal-coupling-case-fixes.md) | M15 | O02 | diagnostic |
| [modules/run/diagnostics/variables-and-troubleshooting-fixes.md](../modules/run/diagnostics/variables-and-troubleshooting-fixes.md) | M15 | O02 | diagnostic |
| [modules/run/implementation.md](../modules/run/implementation.md) | R00 | I01, O01, O02 | routing_metadata |
| [modules/run/index.md](../modules/run/index.md) | R00 | I01, O01, O02 | routing_metadata |
| [modules/shared/modeling-contract.md](../modules/shared/modeling-contract.md) | R00 | M01, M02, M03, M04, M05, M06, M07, M08, M09, M10, M11, M12, M13, M14, M15, I01, O01, O02 | shared_contract |
| [modules/shared/validation-stages.md](../modules/shared/validation-stages.md) | O02 | I01, R00, M01, M03, M15 | stage_check |
| [references/aspen-input-completeness-and-delivery-lessons.md](../references/aspen-input-completeness-and-delivery-lessons.md) | M15 | — | compatibility |
| [references/aspen-plus-textbook-guide.md](../references/aspen-plus-textbook-guide.md) | M01 | M11, M12, M13 | shared_reference |
| [references/calculator-flowsheeting-options.md](../references/calculator-flowsheeting-options.md) | M08 | — | shared_reference |
| [references/column-splitting-and-heat-integration.md](../references/column-splitting-and-heat-integration.md) | M05 | — | shared_reference |
| [references/com-attach-and-license-env.md](../references/com-attach-and-license-env.md) | M15 | — | compatibility |
| [references/content-ownership.md](../references/content-ownership.md) | R00 | I01, O01, O02, M15 | generated_navigation |
| [references/convergence-separation-and-energy-integrity.md](../references/convergence-separation-and-energy-integrity.md) | M02 | M06, M08, M15 | shared_reference |
| [references/differential-pressure-thermal-coupling.md](../references/differential-pressure-thermal-coupling.md) | M04 | — | shared_reference |
| [references/distillation-case-library.md](../references/distillation-case-library.md) | M02 | — | shared_reference |
| [references/double-effect-distillation-and-design-spec.md](../references/double-effect-distillation-and-design-spec.md) | M02 | — | shared_reference |
| [references/double-effect-user-workflow.md](../references/double-effect-user-workflow.md) | M09 | — | shared_reference |
| [references/engineering-modeling-basics.md](../references/engineering-modeling-basics.md) | M01 | — | shared_reference |
| [references/equipment-hydraulics-and-rating.md](../references/equipment-hydraulics-and-rating.md) | M04 | M05, M07 | shared_reference |
| [references/feed-stage-sensitivity-curves.md](../references/feed-stage-sensitivity-curves.md) | M02 | — | shared_reference |
| [references/first-principles-cards.md](../references/first-principles-cards.md) | M09 | — | shared_reference |
| [references/general-modeling-mechanics.md](../references/general-modeling-mechanics.md) | M01 | M03, M09, M10, M11, M12 | shared_reference |
| [references/general-verification-methods.md](../references/general-verification-methods.md) | M15 | — | compatibility |
| [references/heat-carrier-and-salt-properties.md](../references/heat-carrier-and-salt-properties.md) | M05 | M06 | shared_reference |
| [references/input-file-and-rstoic.md](../references/input-file-and-rstoic.md) | M03 | — | shared_reference |
| [references/kinetic-reactor-input-workflow-320-322.md](../references/kinetic-reactor-input-workflow-320-322.md) | M03 | — | shared_reference |
| [references/kinetics-recycle-and-delivery-reasoning.md](../references/kinetics-recycle-and-delivery-reasoning.md) | M01 | M03, M05, M08, M09, M14 | shared_reference |
| [references/li-ruijiang-rplug-kinetics-validation.md](../references/li-ruijiang-rplug-kinetics-validation.md) | M03 | — | shared_reference |
| [references/modeling-guide.md](../references/modeling-guide.md) | M09 | — | shared_reference |
| [references/pdo-heat-integration-and-delivery-lessons.md](../references/pdo-heat-integration-and-delivery-lessons.md) | M05 | — | shared_reference |
| [references/phase-diagram-before-distillation.md](../references/phase-diagram-before-distillation.md) | M01 | M02 | shared_reference |
| [references/principle-case-map.md](../references/principle-case-map.md) | R00 | M01, M02, M03, M04, M05, M06, M07, M08, M09, M10, M11, M12, M13, M14, M15 | shared_index |
| [references/property-provenance-and-repair-gates.md](../references/property-provenance-and-repair-gates.md) | M15 | — | compatibility |
| [references/reactor-flash-column-example.md](../references/reactor-flash-column-example.md) | M03 | — | shared_reference |
| [references/rplug-native-sensitivity-method.md](../references/rplug-native-sensitivity-method.md) | M03 | M01, M04, M05, M08, M09, M14, M15, O02 | shared_reference |
| [references/run-verification-and-reconcile.md](../references/run-verification-and-reconcile.md) | M15 | — | compatibility |
| [references/sensitivity-scope-and-configuration.md](../references/sensitivity-scope-and-configuration.md) | M02 | M03, M08, M09, M14, M15 | shared_reference |
| [references/styrene-recycle-and-dewatering.md](../references/styrene-recycle-and-dewatering.md) | M09 | — | shared_reference |
| [references/sun-lanyi-case-derived-reasoning.md](../references/sun-lanyi-case-derived-reasoning.md) | M01 | M02, M03, M04, M05, M06, M07, M08, M09, M11, M12, M13, M14 | shared_reference |
| [references/sun-lanyi-ch7-4-radfrac-strict.md](../references/sun-lanyi-ch7-4-radfrac-strict.md) | M02 | — | shared_reference |
| [references/textbook-distillation-and-towers.md](../references/textbook-distillation-and-towers.md) | M02 | M06, M07, M15 | principle_source |
| [references/textbook-fluid-transport.md](../references/textbook-fluid-transport.md) | M04 | M15 | principle_source |
| [references/textbook-heat-and-energy.md](../references/textbook-heat-and-energy.md) | M05 | M06, M15 | principle_source |
| [references/textbook-numerics-economics-and-custom-models.md](../references/textbook-numerics-economics-and-custom-models.md) | M08 | M09, M14, M15 | principle_source |
| [references/textbook-properties-and-boundaries.md](../references/textbook-properties-and-boundaries.md) | M01 | M15 | principle_source |
| [references/textbook-reaction-engineering.md](../references/textbook-reaction-engineering.md) | M03 | M15 | principle_source |
| [references/textbook-solids-and-mass-transfer.md](../references/textbook-solids-and-mass-transfer.md) | M10 | M11 | principle_source |
| [references/textbook-source-coverage.md](../references/textbook-source-coverage.md) | R00 | M01, M02, M03, M04, M05, M06, M07, M08, M09, M10, M11, M12, M13, M14, M15 | shared_index |
| [references/textbook-special-materials-and-dynamics.md](../references/textbook-special-materials-and-dynamics.md) | M12 | M13 | principle_source |
| [references/thermally-coupled-distillation.md](../references/thermally-coupled-distillation.md) | M02 | — | shared_reference |
| [references/three-component-thermal-coupling-case.md](../references/three-component-thermal-coupling-case.md) | M09 | — | shared_reference |
| [references/tianjin-distillation-9-5-calculation.md](../references/tianjin-distillation-9-5-calculation.md) | M02 | — | shared_reference |
| [references/utility-steam-generation.md](../references/utility-steam-generation.md) | M05 | — | shared_reference |
| [references/variables-and-troubleshooting.md](../references/variables-and-troubleshooting.md) | M09 | — | shared_reference |
| [scripts/aspen_plus_bridge.py](../scripts/aspen_plus_bridge.py) | M09 | — | tool |
| [scripts/binary_distillation_9_5.py](../scripts/binary_distillation_9_5.py) | M09 | — | tool |
| [scripts/build_from_input.py](../scripts/build_from_input.py) | M09 | — | tool |
| [scripts/build_styrene_column.py](../scripts/build_styrene_column.py) | M09 | — | tool |
| [scripts/check_delivery.py](../scripts/check_delivery.py) | O02 | — | tool |
| [scripts/configure_sensitivity_series_plot.py](../scripts/configure_sensitivity_series_plot.py) | M09 | — | tool |
| [scripts/estimate_min_reflux_asymptote.py](../scripts/estimate_min_reflux_asymptote.py) | M09 | — | tool |
| [scripts/heat_carrier_screen.py](../scripts/heat_carrier_screen.py) | M09 | — | tool |
| [scripts/history_check.py](../scripts/history_check.py) | O02 | — | tool |
| [scripts/hydraulic_screening.py](../scripts/hydraulic_screening.py) | M09 | — | tool |
| [scripts/optimal_stages_from_dstw.py](../scripts/optimal_stages_from_dstw.py) | M09 | — | tool |
| [scripts/plot_radfrac_feedstage_sensitivity.py](../scripts/plot_radfrac_feedstage_sensitivity.py) | M09 | — | tool |
| [scripts/styrene_column.bkp](../scripts/styrene_column.bkp) | M09 | — | tool |
| [scripts/styrene_column.inp](../scripts/styrene_column.inp) | M09 | — | tool |
| [scripts/styrene_column_result.apwz](../scripts/styrene_column_result.apwz) | M09 | — | tool |
| [scripts/styrene_column_result.rep](../scripts/styrene_column_result.rep) | M09 | — | tool |
| [scripts/tests/test_delivery_loop.py](../scripts/tests/test_delivery_loop.py) | O02 | — | test |
| [scripts/tests/test_history_check.py](../scripts/tests/test_history_check.py) | O02 | M15 | test |
| [scripts/tests/test_stage_validation.py](../scripts/tests/test_stage_validation.py) | O02 | I01, R00, M01, M03, M15 | test |
| [scripts/validate_modular_skill.py](../scripts/validate_modular_skill.py) | O02 | — | tool |
| [update_skill_files.py](../update_skill_files.py) | M09 | — | retired_compatibility |
| [中文分类索引.md](../中文分类索引.md) | I01 | — | navigation |

| [modules/properties/index.md](../modules/properties/index.md) | P00 | I01, R00, M01, M09, M15, O02 | preflight |
| [modules/properties/check.md](../modules/properties/check.md) | P00 | R00, M01, M09, M15, O02 | stage_check |
| [scripts/check_process_gate.py](../scripts/check_process_gate.py) | P00 | R00, M09, O02 | process_admission |
| [scripts/tests/test_process_gate.py](../scripts/tests/test_process_gate.py) | P00 | R00, M09, O02 | test |
| [references/extractive-distillation-workflow.md](../references/extractive-distillation-workflow.md) | M02 | P00, M01, M05, M07, M08, M09, M15, O02 | principle_case_method |
| [modules/run/diagnostics/extractive-distillation-fixes.md](../modules/run/diagnostics/extractive-distillation-fixes.md) | M15 | P00, M01, M02, M05, M08, M09, O02 | diagnostic_case |
