# 初始化与耦合流程的历史故障案例

以下参数与因果受原案例条件限制；只能经当前问题的原理诊断后参考。

### 7.3 第二原则类：来自已验证案例的可复用经验（学习参考；采用前必须回到第一原则校验）

> 下面这些是历史案例/文献中沉淀的模式与踩坑记录。它们能显著加快收敛与避免返工，但都默认**适用于原案例的体系与前提**；用到你的任务前，须逐条用 共享建模约束 的原理/需求核对适用性。

- For a bare tower with an external reboiler loop, initialize the reboil-vapor
  tear stream a few degrees ABOVE the dew point (all vapor). A bubble-point
  initial T flashes to `V=0` (liquid), which makes RadFrac treat the vapor feed as
  liquid and produces a cluster of transient errors every run: `UDL03.3` top-tray
  dry-up, `UDL03.2` component-balance failure, and HeatX `HEATX.4` temperature
  crossover. Detect it by reading the first-flash `V` value in the `.his`.
  See [references/double-effect-distillation-and-design-spec.md](../../../references/double-effect-distillation-and-design-spec.md).
- Column splitting (RadFrac `CONDENSER=NONE`/`REBOILER=NONE` with external condenser/reboiler) and stream HeatX integration: read [references/column-splitting-and-heat-integration.md](../../../references/column-splitting-and-heat-integration.md) first.
- Reactor waste heat plus two-column integration: read [references/pdo-heat-integration-and-delivery-lessons.md](../../../references/pdo-heat-integration-and-delivery-lessons.md) for stage remapping, steam-loop degrees of freedom, heat-grade matching, pressure budgets, units and cold-start evidence. The PDO energy subsystem was validated; its original deep-cold quench issue was not resolved. Case numbers are not defaults.
- For vapor recompression heat pumps, sweep the compression ratio and check
  `REB-HX` overall and zone LMTD plus the condensing/boiling minimum approach;
  the original case limits compression ratio to 2.5; determine the current limit from machinery, discharge temperature, phase state and user constraints. See [references/column-splitting-and-heat-integration.md](../../../references/column-splitting-and-heat-integration.md).
- For differential-pressure thermal coupling (差压热耦合 = two-column vapor recompression): LP tower overhead vapour -> compressor -> HP tower bottom; HP overhead vapour -> HeatX -> LP reboiler (main coupling); auxiliary reboiler/condenser only for load mismatch. The cited case uses compression ratio <= 2.5 (not a universal cap); check HeatX LMTD/min-approach, use phase-correct tear-stream initial values, compare energy on the same product basis. C3 propylene/propane case: conventional 200-stage heat 6.39e7 kJ/h -> compressor 4.92e6 kJ/h (-92.3%). See [references/differential-pressure-thermal-coupling.md](../../../references/differential-pressure-thermal-coupling.md).
- Three-component thermally coupled distillation (Petlyuk two-column equivalent): the coupling is STREAM-based, not tray-heat-duty-based - a prefractionator with CONDENSER=NONE REBOILER=NONE and EMPTY COL-SPECS gets its reflux (REF-PF liquid) and reboil vapor (REBV-PF vapor) from the main column as tear streams; verify PF duty 0/0. REBV-PF flow is the dominant B/C-split variable; side-draw stage must match the V-PF feed stage; more MC stages can make it WORSE (design spec lowers RR and starves the B/C stripping section). To clear transient UDL03.x dry-up errors in .his: seed the tear-stream inputs from converged results AND tighten the design-spec LIMITS around the solution - Reconcile() API alone does not fix them. See [references/three-component-thermal-coupling-case.md](../../../references/three-component-thermal-coupling-case.md).
- The historical double-effect task preferred SERIES topology and specified >=35% energy saving, strict clean logs and no compensation pumps. Apply its topology, saving target and equipment restrictions when the current user requirements inherit them; otherwise choose and justify the current topology and target from M02/M04/M05/M06. Pressure drops require current geometry/phase/property evidence, not a blanket 0.2 bar. The case realization is in [references/double-effect-user-workflow.md](../../../references/double-effect-user-workflow.md).
