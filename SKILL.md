---
name: aspen-plus-automation
description: Automate locally installed Aspen Plus on Windows through its COM interface (Apwn.Document). Use when Codex needs to open/create/edit .bkp/.apwz/.inp simulation cases, configure components, property methods, streams, and blocks, run simulations, read results, save copies, split a RadFrac column into external condenser/reboiler loops, add stream-to-stream HeatX heat integration, or study local distillation case folders (heat pump, pressure-swing, azeotropic, batch, dividing-wall, extractive, and multi-effect distillation) (V14 validated). Includes textbook-backed guidance for fluid flow, heat transfer, distillation, absorption, reaction engineering, and convergence. Invocation priority is to build every simulation from engineering principles and the user's stated requirements FIRST, with every principle and numerical value traceable to authoritative textbooks or the user's stated requirements (never fabricated); bundled cases/examples are learning references only - never copy them.
---

# Aspen Plus 自动化 (Aspen Plus Automation)

> **总纲：先原理与需求，后案例参考。** 本 skill 的所有内容按两级原则组织——**第一原则**：依据化工原理与用户/题目给出的要求建模；**第二原则**：已有案例只作学习参考，禁止照搬模仿。每次调用本 skill 都要先执行第一原则，第二原则仅在需要时辅助。**跑流程时的每个原理与数值都必须“有出处、可溯源”——来自权威教材/资料或用户规定，禁止臆想、杜撰公式、物性与经验值。**

## 1. 调用总原则 (Guiding Principles)

> 本节是最高优先级指令，优先于后面任何具体段落。它决定"一个新模拟应当如何开始"，而不是"如何点按钮"。

### 1.1 第一原则（最高优先级）：按原理与个人定义的要求建模

- **需求先行（个人定义的要求优先）**：先完整收集用户/题目给出的规定——进料组成与状态、目标产物、纯度/回收率、操作压力与温度、能耗或公用工程目标、允许与禁止的技术路线、塔型/拓扑要求（如串联/并联）、温度敏感组分与限温、验收标准等。用户明确规定的，必须按用户规定执行；用户未给全的，按合理工程假设补齐并明确说明假设。
- **原理驱动**：依据化工原理（热力学、相平衡、分离、反应工程、传递与单元操作）和工程判断，独立推导建模方案——物性方法、模块/塔型选择、设计规定（Design Spec）的数量与目标、操作条件与压力剖面等。每个建模决策都要能回答："这是由哪条原理或哪条用户要求推出的？"
- **教材溯源，禁止臆想**：建模所用的原理与数值必须有出处。优先级：用户/题目规定 > 权威教材原理 > 有据工程判断。本 skill 已按教材提炼的原理底稿见 `references/engineering-modeling-basics.md`（源自《化工原理》夏清/贾绍义 上、下册、《化学反应工程》朱炳辰 第5版、《化工过程模拟实训——Aspen Plus 教程》孙兰义 第2版等）与 `references/aspen-plus-textbook-guide.md`。凡是公式、物性数据、经验取值、压降、回流比、设计规定目标等，都要能回答“来自哪条教材原理/哪个出处”；查不到或记不准确时，回到教材/参考文档核对，或明确标注“假设”并说明理由——**绝不凭印象编造公式、物性、压降或“经验值”，绝不臆想原理**。
- **先方案后参考**：不得先翻案例再照着搭流程，案例不能替代需求分析与原理推导。
- **冲突处理**：当"已有案例的做法"与"原理/用户要求"冲突时，以原理和用户要求为准，并在交付说明中主动指出差异与理由。

### 1.2 第二原则（辅助）：已有案例只用于学习，不用于模仿

- 案例（本地案例库、已验证 flowsheet、文献复现、历史 `.inp`/`.bkp`）的正当用途是**学习**：理解"某条原理如何落地"、Aspen 的路径/语法写法、常见报错与收敛技巧、合理的取值区间。
- 从案例借鉴的任何数值、构型、压力降、回流比、设计规定等，都必须回到第一原则重新推导，或与用户要求核对；能解释"为什么"才可采纳。
- **案例不等于答案**：不得仅因"案例里就是这么写的"而照抄，也不得把案例的数值直接当作本任务的设定；引用案例时必须说明其适用条件与差异。

### 1.3 推荐的调用顺序

1. 收集并写清需求、目标与约束（用户规定优先，缺省处用合理工程假设并注明）。
2. 独立完成原理分析，形成建模方案草案（物性方法、模块、设计规定、压力剖面、操作条件）。**草案中的每个原理与数值都要可溯源到教材/权威资料（拿不准就查 `references/` 或原教材后再定），不许臆想。**
3. 仅在需要时查阅第二原则资料（案例/模式/踩坑记录），用来补全或检验草案，而不是取代它。
4. 搭建/运行模拟，按 §7.1 验收规则校验，并把结果对照需求与原理复核后再交付。

## 2. 概述 (Overview)

Drive a locally installed Aspen Plus through the `Apwn.Document` COM automation interface. The bundled bridge script handles opening cases, editing variables, running calculations, reading results, and saving copies without opening the Aspen GUI by hand.

## 3. 前置条件 (Prerequisites)

- Windows with Aspen Plus installed (V14 validated; `Apwn.Document` must be registered)
- Python with `pywin32`: `python -m pip install pywin32`

## 4. 快速开始 (Quick Start)

Run the built-in demo from the skill directory:

```powershell
python scripts/aspen_plus_bridge.py --demo
```

The demo opens `sour.apwz`, changes FEED temperature from 40 C to 50 C, reruns the simulation, prints FEED/BOT1/BOT2 results, and saves `aspen_demo_result.apwz`. (演示只示范自动化操作机制，不是建模答案。)

## 5. 自动化核心工作流 (Core Workflow)

1. List streams to discover names:

```powershell
python scripts/aspen_plus_bridge.py --open "C:\path\to\case.apwz" --streams
```

2. Edit an input, run, read a result, and save a copy:

```powershell
python scripts/aspen_plus_bridge.py --open "case.apwz" --set "\Data\Streams\FEED\Input\TEMP\MIXED=50" --run --get "\Data\Streams\BOT1\Output\RES_TEMP" --save "result.apwz"
```

## 6. 新建模拟：从需求与原理出发 (Build a New Simulation from Principles and Requirements)

> 本节是 §1.1 第一原则的操作化：**先做 6.1 的设计，再写文件**。6.3 中的既有示例/脚本属于第二原则的"学习参考"，不得照搬其数值。

### 6.1 建模前的需求与原理检查清单（先完成）

- **需求清单**：分离/反应任务、进料组成与状态、目标纯度/回收率、操作压力与温度、温度敏感组分与限温、能耗/公用工程目标、允许与禁止的技术路线、拓扑要求、验收标准。
- **原理清单**：物性方法选择的依据（组分极性/缔合/电解质/水系统/压力温度范围）、模块与塔型选择的依据、自由度与所需规定数、压力剖面可行性、热量/物料平衡的预期量级。
- 设计草案完成后进入 6.2；需要原理支撑时查阅 §8.1（`references/engineering-modeling-basics.md`、`references/aspen-plus-textbook-guide.md`、`references/modeling-guide.md`）。

### 6.2 用 `.inp` 落地并运行（机制）

Prefer an Aspen Plus input file (`.inp`) when a case does not already exist. Open it with `InitFromFile2` and run normally.

Run a generic build script:

```powershell
python scripts/build_from_input.py --inp "case.inp" --save "case.apwz" --report "case.rep"
```

- Set units explicitly so values are not misinterpreted:
  `IN-UNITS SI TEMP=C PRES=BAR MOLE-FLOW='KMOL/HR' MASS-FLOW='KG/HR'`
- Define components with `COMPONENTS <ID> <DATABANK-NAME>`, for example `EB ETHYLBENZENE / STY STYRENE / H2 HYDROGEN`.
- Set the global method with `PROPERTIES PENG-ROB` (PR) only when the principle analysis supports it (e.g. non-polar hydrocarbon systems); otherwise pick the method your 6.1 analysis justifies.
- The conversion reactor is the `RSTOIC` block; V14 has no separate `RConv` block.
- Define stoichiometry and conversion with `STOIC` and `CONV` sentences inside `BLOCK <name> RSTOIC`.
- For kinetic reactors, prefer the `General` form first when Aspen offers it, then map the literature rate law into `LHHW` or `PowerLaw`; only skip `General` when the source model or Aspen page forces a direct built-in form.
- For literature kinetics, separate what the paper actually gives from values inferred, retained from templates, or fitted. Do not present a missing `Keq(T)` or driving-force coefficient as literature data unless the source explicitly provides it.
- After running, read component flows from `\Data\Streams\<name>\Output\MOLEFLOW\MIXED\<comp>` and export a report with `Export(2, "result.rep")`.

### 6.3 可参考的落地示例（第二原则：学习模式，校验后使用）

- See [references/input-file-and-rstoic.md](references/input-file-and-rstoic.md) for a complete ethylbenzene-to-styrene example — 只学习其 `.inp` 语法与段落组织，体系数值须按你的需求重设。
- See [references/reactor-flash-column-example.md](references/reactor-flash-column-example.md) and `scripts/build_styrene_column.py` for a full reactor + flash + RadFrac flowsheet with a 99.9% purity design spec — 学习 flowsheet 结构与设计规定的写法，不要复制其纯度/能耗目标。
- For a split column with vapor recompression heat pump, use `assets/column-split/styrene_heatpump.inp` only as a pattern reference; verify every number against your own first-principle analysis.
- See [references/modeling-guide.md](references/modeling-guide.md) for stream input conventions, common property methods, block selection, and block/stream connection.

## 7. 关键规则 (Key Rules)

> 每条规则都先问：它属于第一原则（原理/用户要求）还是第二原则（案例经验）？**原理与用户要求优先**；案例经验作为参考，采用前必须回到第一原则校验。因此下面按三类组织：

### 7.1 第一原则类：原理与需求驱动的建模与验收规则

- GLOBAL ACCEPTANCE (every flowsheet, incl. heat pumps and double-effect):
  - Final result must show NO hidden errors in the `.his` file
    (`Summary of Simulation Errors` = 0 Severe / 0 Error / 0 Warning), AND the
    Aspen Control Panel must be free of any error/warning.
  - If hidden errors appear, try `Reconcile()` on streams and tower modules to
    seed/initialize values and resolve them; verify on a fresh open.
  - Pressure drop rule: EVERY module except mixers and pressure-changing
    devices (pumps/valves/compressors) must carry a justified pressure-drop
    treatment. Do not type a fixed value by habit. Estimate by fluid phase,
    density/viscosity, equipment type, duty, pressure level, and downstream
    pressure margin. For ordinary positive-pressure exchangers,
    condensers/reboilers, coolers/heaters, and similar equipment, use an
    engineering starting point around -0.2 bar when reasonable. Use very small
    drops such as -0.01 to -0.05 bar only for vacuum/near-vacuum services,
    low-pressure loops, or cases where a return stream would otherwise become
    pressure-infeasible and no real pressure-boosting device is allowed.
- Account for pressure drops in every pressure-changing unit before running:
  column tray profile (`DP-STAGE`/`DP-COL`), heat exchanger hot/cold sides,
  condensers/reboilers, valves, splitters/mixers, and piping. Do not
  blanket-set zero pressure drops, do not use arbitrary empirical values, and
  do not default to tiny `0.0x bar` drops just to avoid pressure warnings.
  Estimate from stream and equipment conditions using chemical engineering
  principles, document the assumptions, and only relax toward very small drops
  after checking that the pressure network or vacuum service requires it.
  See [references/engineering-modeling-basics.md](references/engineering-modeling-basics.md).
- After every `Run2`, read the newest `.his` before reporting; the GUI summary
  can hide errors. See [references/run-verification-and-reconcile.md](references/run-verification-and-reconcile.md) for `.his` error checking, `Reconcile()` tear-stream initialization, complete HeatX specs, PFD stripping, and report unit conversion.
- Use a partial-vapor condenser when H2 or other noncondensables are present; a total condenser can produce unphysical cryogenic overhead temperatures.
- TEMPERATURE-SENSITIVE COMPONENTS FIRST: when the system has a component that degrades
  or polymerises above a temperature limit (styrene >~100 C), energy-saving technology
  selection must consider whether the technology RAISES temperature, not just the original
  column delta-T. Heat pumps compress/superheat the overhead vapour (can exceed 100 C on
  styrene-bearing vapour) and are structurally infeasible when the bottoms already run
  above the limit (hot side must condense above bottoms temp). Prefer heat integration /
  thermal coupling / multi-effect which do not raise temperature. See
  [references/thermally-coupled-distillation.md](references/thermally-coupled-distillation.md).

### 7.2 工具与机制规则（COM / `.inp` 语法 / 文件处理；服务于任何原则）
- **跨版本通用机制/验证文档（工具与机制层，服从 §1 两级原则）**：见 [references/general-modeling-mechanics.md](references/general-modeling-mechanics.md) 与 [references/general-verification-methods.md](references/general-verification-methods.md)。二者只收录跨版本通用方法，不改变“原理+需求先行、禁臆想”的第一原则；其中任何树路径、单位、节点名、API 均须以本机安装版本实测为准，不得把其他版本的结论当通用事实套用。

- Open both `.bkp` and `.apwz` with `InitFromFile2(path, True)`. On V14, `InitFromArchive2` can fail with "cannot open file" for `.apwz`.
- Access simulation data through `Tree.FindNode("\\Data")`. Stream paths follow `\Data\Streams\<name>\Input\...` and `\Data\Streams\<name>\Output\...`.
- Write scalar inputs through leaf nodes such as `Input\TEMP\MIXED` or `Input\PRES\MIXED`. Writing `Input\TEMP` directly can raise `AE_UNDERSPEC`.
- Run synchronously with `Run2(False)`; save with `SaveAs2(path, True)`.
- Read result values such as `Output\RES_TEMP`, `Output\RES_PRES`, and `Output\RES_MASSFLOW`.
- Export the report immediately after `Run2`; component-level results may not reload into the COM tree from a saved `.apwz`.
- For recycle loops, run to a converged base first, then call
  `apwn.Reconcile(...)` with tear-stream flags to initialize inputs; its effect
  may not survive save/reopen, so always verify on a fresh open.
  See [references/run-verification-and-reconcile.md](references/run-verification-and-reconcile.md).
- Check input completeness with
  `Tree.FindNode(r"\Data").NextIncomplete("")`, not `Tree.NextIncomplete`.
- Set `Visible` after initialization. To keep the GUI open after automation, save the case and launch it with `os.startfile(apwz)`.
- COM automation may start the Aspen Plus GUI process; call `Quit()` in `finally` and stop a leftover `AspenPlus` process if it remains.
- **COM connection mechanics (measured)**: `Dispatch("Apwn.Document")` **never attaches** to an
  already-running instance - the COM SCM always spawns a fresh `aspenplus.exe -Automation -Embedding`,
  and `GetActiveObject` fails with `MK_E_UNAVAILABLE` (no ROT registration); so pre-launching
  `aspenplus.exe -Automation` to "attach" is pointless and only costs an extra process/seat. License
  checkout is decided by `LSHOST`/`LSFORCEHOST` in the **client** process environment (the spawned
  server inherits it). A successful `Dispatch` does NOT prove the license works - `2040 ... 无法核实许可 /
  无法实例化` surfaces only at `InitFromFile2`; when `LSHOST` is unresolvable and subnet broadcast is
  blocked there is no fallback, so set `LSFORCEHOST=<host>` explicitly. See
  [references/com-attach-and-license-env.md](references/com-attach-and-license-env.md).
- FlowSheet-level Design Specs in `.inp`: place after all `BLOCK` paragraphs and
  before `EO-CONV-OPTI`; use `DEFINE X MOLE-FLOW STREAM=S SUBSTREAM=MIXED
  COMPONENT=C` (the `STREAM-VAR ... COMPONENT=` form parses wrong or ignores the
  component), `VARY BLOCK-VAR BLOCK=FSPLIT SENTENCE=FRAC VARIABLE=FRAC ID1=out`,
  and tighten the tear tolerance to `CONV-OPTIONS PARAM TOL=0.00001` so outer
  Design Specs can converge. See [references/double-effect-distillation-and-design-spec.md](references/double-effect-distillation-and-design-spec.md).
- Deliverables: generate `.inp` with `Export(4,...)` and `.bkp` with `Export(1,...)`
  FROM the `.apwz` (`SaveAs2(...bkp)` can produce a `.bkp` that fails to reopen).
  Never validate a `.bkp` with `InitFromFile2` — opening it rewrites the file into a
  tiny input-summary backup. Worse: ANY COM `InitFromFile2` of a file in the SAME
  folder (even a `.inp`) rewrites that folder's `.bkp`. After generating `.bkp`, do
  NOT open any file in the deliverable folder via COM; verify the `.bkp` by copying
  it to a scratch folder and opening/running it there, or launch
  `aspenplus.exe /a "case.bkp"` (the same command Windows uses on double-click).

### 7.3 第二原则类：来自已验证案例的可复用经验（学习参考；采用前必须回到第一原则校验）

> 下面这些是历史案例/文献中沉淀的模式与踩坑记录。它们能显著加快收敛与避免返工，但都默认**适用于原案例的体系与前提**；用到你的任务前，须逐条用 §6.1 的原理/需求核对适用性。

- For a bare tower with an external reboiler loop, initialize the reboil-vapor
  tear stream a few degrees ABOVE the dew point (all vapor). A bubble-point
  initial T flashes to `V=0` (liquid), which makes RadFrac treat the vapor feed as
  liquid and produces a cluster of transient errors every run: `UDL03.3` top-tray
  dry-up, `UDL03.2` component-balance failure, and HeatX `HEATX.4` temperature
  crossover. Detect it by reading the first-flash `V` value in the `.his`.
  See [references/double-effect-distillation-and-design-spec.md](references/double-effect-distillation-and-design-spec.md).
- Column splitting (RadFrac `CONDENSER=NONE`/`REBOILER=NONE` with external condenser/reboiler) and stream HeatX integration: read [references/column-splitting-and-heat-integration.md](references/column-splitting-and-heat-integration.md) first.
- For vapor recompression heat pumps, sweep the compression ratio and check
  `REB-HX` overall and zone LMTD plus the condensing/boiling minimum approach;
  do not set the compression ratio above 2.5. See [references/column-splitting-and-heat-integration.md](references/column-splitting-and-heat-integration.md).
- For the styrene heat-pump split flowsheet, reuse and preserve the
  user-preferred PFD layout in `assets/column-split/styrene_heatpump_user_layout.bkp`;
  do not strip its `GRAPHICS_BACKUP` / `PFS` section unless explicitly asked.
- For differential-pressure thermal coupling (差压热耦合 = two-column vapor recompression): LP tower overhead vapour -> compressor -> HP tower bottom; HP overhead vapour -> HeatX -> LP reboiler (main coupling); auxiliary reboiler/condenser only for load mismatch. Keep compression ratio <= 2.5, check HeatX LMTD/min-approach, use phase-correct tear-stream initial values, compare energy on the same product basis. C3 propylene/propane case: conventional 200-stage heat 6.39e7 kJ/h -> compressor 4.92e6 kJ/h (-92.3%). See [references/differential-pressure-thermal-coupling.md](references/differential-pressure-thermal-coupling.md).
- Three-component thermally coupled distillation (Petlyuk two-column equivalent): the coupling is STREAM-based, not tray-heat-duty-based - a prefractionator with CONDENSER=NONE REBOILER=NONE and EMPTY COL-SPECS gets its reflux (REF-PF liquid) and reboil vapor (REBV-PF vapor) from the main column as tear streams; verify PF duty 0/0. REBV-PF flow is the dominant B/C-split variable; side-draw stage must match the V-PF feed stage; more MC stages can make it WORSE (design spec lowers RR and starves the B/C stripping section). To clear transient UDL03.x dry-up errors in .his: seed the tear-stream inputs from converged results AND tighten the design-spec LIMITS around the solution - Reconcile() API alone does not fix them. See [references/three-component-thermal-coupling-case.md](references/three-component-thermal-coupling-case.md).
- Double-effect distillation must PREFER the SERIES topology (column-1 bottoms
  -> column-2 feed); PARALLEL (split feed) requires asking the client first.
  Follow the user-mandated workflow (baseline ->
  series split, overhead sum & bottoms deviation < 5% -> HP/LP -> bare towers +
  external condenser/reboiler -> HP overhead to LP reboiler HeatX -> >= 35%
  energy saving, energy may be sacrificed for recovery/purity; final `.his` =
  0/0/0 and Control Panel free of errors/warnings; Reconcile may seed values).
  注意区分：本条目中的**用户规定的流程与验收标准属于第一原则（必须执行）**；具体的塔拆分/HeatX/收敛细节属于第二原则经验。
  Every applicable non-pressure-changing module gets a justified NEGATIVE
  pressure drop: ordinary positive-pressure services should usually start near
  -0.2 bar, while tiny drops are reserved for vacuum/low-pressure or
  pressure-infeasible return loops; NO compensation pumps. See
  [references/double-effect-user-workflow.md](references/double-effect-user-workflow.md).

## 8. 参考文档 (References)

> 按两级原则分组：8.1 是**第一原则支撑**（原理/方法/机制，设计时按需查阅）；8.2 是**第二原则支撑**（案例与已验证工程，只作学习参考，采用前回第一原则校验）。

### 8.1 第一原则支撑：原理、方法与机制

- See [references/engineering-modeling-basics.md](references/engineering-modeling-basics.md) for textbook-derived modeling fundamentals and design checks.
- See [references/aspen-plus-textbook-guide.md](references/aspen-plus-textbook-guide.md) for property methods, unit-model workflows, flowsheeting tools, and convergence strategies.
- See [references/modeling-guide.md](references/modeling-guide.md) for stream specs, property methods, module selection, and connectivity.
- See [references/kinetic-reactor-input-workflow-320-322.md](references/kinetic-reactor-input-workflow-320-322.md) for the three-part kinetic-reactor workflow: define the reaction set first, organize the literature expression in `General`, then implement it with `LHHW` or `PowerLaw`, and select `RCSTR` or `RPlug` based on reactor hydrodynamics.
- See [references/variables-and-troubleshooting.md](references/variables-and-troubleshooting.md) for the COM object model, node API, variable path conventions, and failure modes.
- See [references/run-verification-and-reconcile.md](references/run-verification-and-reconcile.md) for `.his` error checking, `Reconcile()` tear-stream initialization, complete HeatX specs, PFD stripping, and report unit conversion.
- See [references/calculator-flowsheeting-options.md](references/calculator-flowsheeting-options.md) for the verified Calculator (Flowsheeting Options) workflow: GUI-exported `.inp` + `CALCULATOR` section, `DEFINE` shorthand, `READ-VARS`/`WRITE-VARS`, `EXECUTE BEFORE BLOCK`, FSPLIT by stream name, and `TEAR` declarations.
- See [references/input-file-and-rstoic.md](references/input-file-and-rstoic.md) for building `.inp` cases and RStoic conversion syntax (其中的完整示例只示范语法与段落组织，数值须按你的需求重设)。
- See [references/general-modeling-mechanics.md](references/general-modeling-mechanics.md) for version-neutral modeling mechanics: the spec-meeting three-strategy decision, a property-method decision tree, from-scratch object-tree build mechanics, solids/crystallization modeling elements, reaction-kinetics type selection and Arrhenius-to-Aspen conversion, and official-example reuse rules (second-principle). Tree paths/units/nodes must be confirmed on the installed version.
- See [references/general-verification-methods.md](references/general-verification-methods.md) for version-neutral verification methods: calibration trio, four independent physical benchmarks (mass balance / phase equilibrium / enthalpy balance / duty vs theory), enthalpy-pollution trust checklist, recycle convergence triple-check, and COM automation hygiene.
- See [references/com-attach-and-license-env.md](references/com-attach-and-license-env.md) for the measured COM connection mechanics: `Dispatch` never attaches (the SCM always spawns `-Automation -Embedding` and the ROT holds no registration), why pre-launching `aspenplus.exe -Automation` is pointless, how `LSHOST`/`LSFORCEHOST` in the client process environment decide license checkout (surfacing only at `InitFromFile2` as error 2040), and the local Sentinel RMS facts (UDP 5093 only, no TCP, subnet broadcast blocked so a wrong `LSHOST` has no fallback).

### 8.2 第二原则支撑：案例与已验证工程（学习参考）

- See [references/reactor-flash-column-example.md](references/reactor-flash-column-example.md) and `scripts/build_styrene_column.py` for the complete styrene column example (flowsheet 结构与 design-spec 写法可学，数值目标不可照抄)。
- See [references/distillation-case-library.md](references/distillation-case-library.md) for local heat pump, pressure-swing, azeotropic, batch, dividing-wall, extractive, and multi-effect distillation case folders and their reusable patterns. Use those cases as workflow and model-pattern references, then verify all chemistry, units, stream specs, and energy targets against the current project.
- See [references/column-splitting-and-heat-integration.md](references/column-splitting-and-heat-integration.md) for splitting a column into bare RadFrac + external condenser/reboiler and for stream-to-stream HeatX heat integration.
- See [references/thermally-coupled-distillation.md](references/thermally-coupled-distillation.md) for Petlyuk/DWC thermal coupling (prefractionator + main column, side draws, flowsheet DESIGN-SPEC) and for the temperature-sensitive-component rule (styrene >100 C polymerisation) when choosing energy-saving technology.
- See [references/differential-pressure-thermal-coupling.md](references/differential-pressure-thermal-coupling.md) for the 热耦精馏 article summary: thermally coupled distillation applicability (B-major feed, alpha_AB~alpha_BC, fixed pressure, high-purity intermediate only) and the differential-pressure two-column vapor-recompression upgrade (LP tower overhead -> compressor -> HP tower bottom; HP overhead -> HeatX -> LP reboiler; auxiliary reboiler/condenser for load mismatch). C3 propylene/propane case: conventional 200 stages @ 1800-2100 kPa vs 145+55 split towers; heat 6.39e7 kJ/h replaced by compressor 4.92e6 kJ/h (-92.3%).
- See [references/three-component-thermal-coupling-case.md](references/three-component-thermal-coupling-case.md) for the validated 2026-08-31 three-component (EtOH/BuOH/HexOH) thermally coupled distillation build: Petlyuk two-column equivalent (PF prefractionator with CONDENSER=NONE REBOILER=NONE + main column MC), coupling by REF-PF/REBV-PF tear streams (NO tray heat duties - the coupling is stream-based, not heat-duty-based), BROYDEN tears + phase-correct initial values, flowsheet DESIGN-SPEC on MC RR, REBV-PF sweep for the B/C split bottleneck, and the .his 36-error UDL03.1/UDL03.3 fix (seed tear streams from converged values + tighten DS LIMITS -> 0/0/0 persistent; Reconcile() API alone does NOT fix transient dry-up). Energy: -19.7% reboiler vs fixed-RR=1.3 conventional, ~equal vs near-minimum-reflux optimized conventional.
- See [references/styrene-recycle-and-dewatering.md](references/styrene-recycle-and-dewatering.md) for water/aromatic systems: PR+UNIQUAC+HENRY+FREE-WATER properties (do NOT write `PR`/`UN` section IDs), FLASH3 three-phase cold recovery of noncondensables, stripper (CONDENSER=NONE, feed on stage 1) for dissolved water, Calculator-based EB/water recycle with tear-stream initial values, `<bar>` on DP-STAGE/DP-COL, and the warning-clearing checklist.
- See [references/li-ruijiang-rplug-kinetics-validation.md](references/li-ruijiang-rplug-kinetics-validation.md) for the Li Ruijiang low-water-ratio ethylbenzene dehydrogenation LHHW input path, RPlug adiabatic validation setup, unit conversions, and the 2026-08-19 Aspen verification workflow.
- See [references/double-effect-user-workflow.md](references/double-effect-user-workflow.md) for the user-mandated double-effect workflow, acceptance (`.his` 0/0/0 + Control Panel clean), Reconcile, and pressure-drop selection by fluid/equipment/pressure level (ordinary services near 0.2 bar, tiny drops only for vacuum/pressure-infeasible loops, no compensation pumps).
- See [references/double-effect-distillation-and-design-spec.md](references/double-effect-distillation-and-design-spec.md) for the HP/LP double-effect + HeatX workflow, the reboil-vapor initial-state rule, flowSheet-level `DESIGN-SPEC` `.inp` syntax, pressure-drop modeling (HeatX `PRES-HOT/PRES-COLD`, reflux/reboiler-circulation pumps), and the deliverable save/validate procedure.
- Account for pressure drops in EVERY pressure-changing unit by entering a
  NEGATIVE value in the module's pressure field (negative = pressure drop,
  positive = absolute outlet pressure): HeatX `PARAM ... PRES-HOT=-0.2
  PRES-COLD=-0.03`, Heater/Flash2 `PARAM PRES=-0.2` for ordinary
  positive-pressure service. Size it by equipment and system pressure:
  near-vacuum/low-pressure or pressure-pinched return paths may need small
  drops (-0.01 to -0.05 bar), but do not start there by habit. Do NOT add
  extra pumps to "close" the network unless they represent a real pressure
  boosting device; instead tune tower pressure/profile or document the
  pressure-feasible small-drop exception. Never write `HOT-SIDE ... DP=...`
  (2041). After
  moving a HeatX feed in FLOWSHEET, also update the `FEEDS HOT=... COLD=...`
  sentence inside the block. With drops the Design-Spec curve can get very
  steep — tighten `LIMITS` around the solution so SECANT does not oscillate.
  See
  [references/double-effect-distillation-and-design-spec.md](references/double-effect-distillation-and-design-spec.md).
