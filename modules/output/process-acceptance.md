# 按工艺适用的详细检查

仅加载本次任务相关条目；不把严格塔优化、进料比较、载热或评级自动扩展到无关任务。用户明确约束与不放宽容差、零错误/警告要求保持。

### 7.1 第一原则类：原理与需求驱动的建模与验收规则

- COLUMN BUILD SCOPE: if the user only asks for tower basics, deliver the DSTWU/shortcut baseline only. If the user explicitly asks for 精馏塔严格计算, 第7.4节, 严格塔, 最佳理论板数/进料板/回流比, or Sensitivity, then the full Sun Lanyi Section 7.4 workflow is in scope: DSTWU baseline -> RadFrac rigorous tower -> product Design Specs + Vary -> S-1/S-2 strict Sensitivity -> convergence/penalty checks. Do not expand this into full economic/TAC optimization unless the user explicitly requests it.

- For binary continuous distillation, start from the Tianjin 9.5 sequence: mass balance -> q line -> `R_min` -> choose `R` -> Fenske/Gilliland `N` -> feed stage. Treat the textbook `1.1-2.0 R_min` range as an economic rule of thumb, not a mathematical optimum. Use bubble-point feed (`q=1`) as the default baseline when there is no special heat integration. A hotter feed lowers `q`, `V_prime`, and reboiler duty, but the preheat duty must be counted. Re-select the feed stage whenever `q` changes. MANDATORY feed-state gate: do not select the final feed state in one step. Compare the upstream actual state, `q=1` baseline, a hotter/two-phase candidate when heat is available, and saturated/superheated vapor for a vapor feed; exclude any candidate with a documented reason. For every candidate record `T/P/VFRAC/q`, `R_min`, `R`, integer `N/N_F`, `Q_reb`, `Q_cond`, preheat duty, column loads/diameter/flooding, utility cost or the user objective, and robustness. Determine the true optimum of `q`, `R`, integer `N`, and feed stage only with an explicit TAC/utility objective and constraints. See [references/tianjin-distillation-9-5-calculation.md](../../references/tianjin-distillation-9-5-calculation.md).
- GLOBAL ACCEPTANCE (every flowsheet, incl. heat pumps and double-effect):
  - Final result must show NO hidden errors in the `.his` file
    (`Summary of Simulation Errors` = 0 Severe / 0 Error / 0 Warning), AND the
    Aspen Control Panel must be free of any error/warning.
  - If errors appear, return to M15 for diagnosis; use Reconcile only if phase-correct initialization is the supported cause, then verify on a fresh open.
- 压力网络：各设备的出口压力、压降或零压降处理均须有当前相态、物性、负荷、几何/关联式和压力预算依据；Mixer不提供真实压头，泵/压缩机/阀按实际设备作用处理。缺几何时记录假设范围和未验证项。历史 -0.2 bar 或 0.0x bar 只属于原案例，不能为消警告机械套用。
- After every `Run2`, read the newest `.his` before reporting; the GUI summary
  can hide errors. Use [运行审计](methods/run-audit.md) for current `.his`, effective settings, initialization dependencies, cold reopen and unit checks. Return input repairs, Reconcile and HeatX specification changes to R00; independently recheck the resulting new candidate.
- Use a partial-vapor condenser when H2 or other noncondensables are present; a total condenser can produce unphysical cryogenic overhead temperatures.
- TEMPERATURE-SENSITIVE COMPONENTS FIRST: use sourced limits for the actual composition, inhibitor, residence time and local wall/film temperature. Compare every candidate's compression, tower-pressure and heat-exchange temperature changes. Heat pumps, thermal coupling and multi-effect each require an independent temperature/phase/pressure feasibility check; none is automatically temperature-safe. Use M02-K08, M03-K09 and M06-K01–K03 before the historical [thermal-coupling case](../../references/thermally-coupled-distillation.md).

- HEAT-CARRIER PROPERTIES ARE DESIGN DATA, NOT DEFAULT DATA: for molten salt / thermal oil / pressurized-water carriers take cp, rho, mu, k and the freezing/decomposition limits from an authoritative source (nitrate salt: INL/EXT-10-18297 = OSTI 980801; water: IAPWS-IF97). Aspen's databank is NOT usable for molten nitrates: measured here, 40 wt% KNO3 + 60 wt% NaNO3 gives cp ~1.15 kJ/(kg.K) and rho ~438 kg/m3 -> cp low by ~40%, density low by ~4x (pump power / volume flow / dT all wrong). ALWAYS audit a case by back-calculating cp = Q/(m*dT) from a Heater duty and rho = m/(FLUID_POWER/dP) from a Pump; reject any case whose back-calculated values differ from handbooks by >10%. Entering user property data additionally requires the GUI Prop-Data + Model Selection route - file injection alone is silently ignored. See [references/heat-carrier-and-salt-properties.md](../../references/heat-carrier-and-salt-properties.md).


### 7.4 设备水力学与验收边界

- 水力学结论必须标明等级：`PRELIMINARY`、`SOURCE_BOUND`、`ASPEN_EVIDENCE`、`VENDOR_RATING` 或 `CLOSED`。不得把初估或工具调用成功写成最终设计通过。
- 塔器水力学至少检查面积闭合、降液管、堰和液层、开孔或填料几何、压降、漏液、夹带、液泛和正常/最小/最大/扰动负荷包络。填料塔还要检查湿润、分布、分段、再分布器、压降和 HETP。
- 换热面积用显式、有依据的U或详细模型；热阻/关联式的面积基准、流态和物性范围按M05-K03/K06核查。`U-OPTION=PHASE`在旧熔盐案例测试中返回默认850 W/(m²·K)，不代表通用设计U或所有版本行为。校核局部壁温/膜温的凝固、分解和腐蚀边界；旧案例10–25%面积裕量、凝固点+20 K仅为原任务起点，当前裕量由来源/设备/工况重新确定。见 [references/heat-carrier-and-salt-properties.md](../../references/heat-carrier-and-salt-properties.md)。
- `HYDRAULIC=NO` 的干净物料模拟只证明物料和能量计算，不证明塔内件水力学。任何塔径、压力、内件或负荷改变后，必须从同一最终 Aspen 工况重新导出阶段数据并复算。
- 换热器要区分 HeatX、Shortcut、Detailed 和真正的 Aspen EDR，并确认同设备身份、负荷、面积、压降、速度和材料证据。
- `scripts/hydraulic_screening.py` 可从 Aspen 结果中提取塔径、阶段负荷与水力数据做透明初筛；输出必须保留适用条件和证据等级，不能替代厂家评级。
