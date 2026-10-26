# 运行接口与实现机制

由M09调用，其他工艺模块共享；只实现已完成原理判断的输入。文中旧节号是原文定位，不改变本次“任务→运行→输出/检查”的顺序。

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

> 本节是 共享建模约束的操作化：**先做 6.1 的设计，再写文件**。6.3 中的既有示例/脚本属于第二原则的"学习参考"，不得照搬其数值。

### 6.0 模块定位记录（先完成）

按运行模块索引 从任务描述定位主模块和相关模块。开始读取案例前，先在工作记录中写下：

```text
主模块：Mxx 模块名称
相关模块：Myy、Mzz（没有则写“无”）
原理层：本次实际读取的 references/... 文件
案例层：原理判断完成后实际读取的 references/...、assets/... 文件
```

模块定位不是标签工作：它决定先检查哪些自由度、物性、压力/温度边界和验收指标。一个案例若同时包含精馏、反应、压力网络和热集成，必须分别读取这些模块的原理层，再读取案例并标注其跨模块用途。

### 6.1 建模前的需求与原理检查清单（先完成）

- **需求清单**：分离/反应任务、进料组成与状态、目标纯度/回收率、操作压力与温度、温度敏感组分与限温、能耗/公用工程目标、允许与禁止的技术路线、拓扑要求、验收标准。
- **原理清单**：物性方法选择的依据（组分极性/缔合/电解质/水系统/压力温度范围）、模块与塔型选择的依据、自由度与所需规定数、压力剖面可行性、热量/物料平衡的预期量级。
- 设计草案完成后进入 6.2；需要原理支撑时查阅 教材来源与对应专题（`references/engineering-modeling-basics.md`、`references/aspen-plus-textbook-guide.md`、`references/modeling-guide.md`）。二元连续精馏的 q 线、Rmin、理论板、进料板和优化流程见 `references/tianjin-distillation-9-5-calculation.md`。

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

- See [references/input-file-and-rstoic.md](../../references/input-file-and-rstoic.md) for a complete ethylbenzene-to-styrene example — 只学习其 `.inp` 语法与段落组织，体系数值须按你的需求重设。
- See [references/reactor-flash-column-example.md](../../references/reactor-flash-column-example.md) and `scripts/build_styrene_column.py` for a full reactor + flash + RadFrac flowsheet with a 99.9% purity design spec — 学习 flowsheet 结构与设计规定的写法，不要复制其纯度/能耗目标。
- For a split column with vapor recompression heat pump, use `assets/column-split/styrene_heatpump.inp` only as a pattern reference; verify every number against your own first-principle analysis.
- See [references/modeling-guide.md](../../references/modeling-guide.md) for stream input conventions, common property methods, block selection, and block/stream connection.


### 7.2 工具与机制规则（COM / `.inp` 语法 / 文件处理；服务于任何原则）
- **跨版本通用机制/验证文档（工具与机制层，服从 §1 两级原则）**：见 [references/general-modeling-mechanics.md](../../references/general-modeling-mechanics.md) 与 [references/general-verification-methods.md](../../references/general-verification-methods.md)。二者只收录跨版本通用方法，不改变“原理+需求先行、禁臆想”的第一原则；其中任何树路径、单位、节点名、API 均须以本机安装版本实测为准，不得把其他版本的结论当通用事实套用。

- Open both `.bkp` and `.apwz` with `InitFromFile2(path, True)`. On V14, `InitFromArchive2` can fail with "cannot open file" for `.apwz`.
- Access simulation data through `Tree.FindNode("\\Data")`. Stream paths follow `\Data\Streams\<name>\Input\...` and `\Data\Streams\<name>\Output\...`.
- Write scalar inputs through leaf nodes such as `Input\TEMP\MIXED` or `Input\PRES\MIXED`. Writing `Input\TEMP` directly can raise `AE_UNDERSPEC`.
- Run synchronously with `Run2(False)`; save with `SaveAs2(path, True)`.
- Read result values such as `Output\RES_TEMP`, `Output\RES_PRES`, and `Output\RES_MASSFLOW`.
- Export the report immediately after `Run2`; component-level results may not reload into the COM tree from a saved `.apwz`.
- For recycle loops, run to a converged base first, then call
  `apwn.Reconcile(...)` with tear-stream flags to initialize inputs; its effect
  may not survive save/reopen, so always verify on a fresh open.
  See [references/run-verification-and-reconcile.md](../../references/run-verification-and-reconcile.md).
- Check input completeness with
  `Tree.FindNode(r"\Data").NextIncomplete("")`, not `Tree.NextIncomplete`.
- Set `Visible` after initialization. To keep the GUI open after automation, save the case and launch it with `os.startfile(apwz)`.
- COM automation may start the Aspen Plus GUI process; call `Quit()` in `finally`. Terminate leftovers only by verified PIDs belonging to this run, including confirmed child processes; preserve user and unknown instances. Respect any user prohibition on Computer Use or GUI inspection.
- **COM connection mechanics (measured)**: `Dispatch("Apwn.Document")` **never attaches** to an
  already-running instance - the COM SCM always spawns a fresh `aspenplus.exe -Automation -Embedding`,
  and `GetActiveObject` fails with `MK_E_UNAVAILABLE` (no ROT registration); so pre-launching
  `aspenplus.exe -Automation` to "attach" is pointless and only costs an extra process/seat. License
  checkout is decided by `LSHOST`/`LSFORCEHOST` in the **client** process environment (the spawned
  server inherits it). A successful `Dispatch` does NOT prove the license works - `2040 ... 无法核实许可 /
  无法实例化` surfaces only at `InitFromFile2`; when `LSHOST` is unresolvable and subnet broadcast is
  blocked there is no fallback, so set `LSFORCEHOST=<host>` explicitly. See
  [references/com-attach-and-license-env.md](../../references/com-attach-and-license-env.md).
- FlowSheet-level Design Specs in `.inp`: place after all `BLOCK` paragraphs and
  before `EO-CONV-OPTI`; use `DEFINE X MOLE-FLOW STREAM=S SUBSTREAM=MIXED
  COMPONENT=C` (the `STREAM-VAR ... COMPONENT=` form parses wrong or ignores the
  component), `VARY BLOCK-VAR BLOCK=FSPLIT SENTENCE=FRAC VARIABLE=FRAC ID1=out`,
  and audit the effective tear and inner-solver tolerances against the DS accuracy.
  Historical `CONV-OPTIONS PARAM TOL=0.00001` is a case example, not a required
  value: retain an already stricter setting and never relax it. See
  [references/double-effect-distillation-and-design-spec.md](../../references/double-effect-distillation-and-design-spec.md)
  and [the tolerance audit](../../references/convergence-separation-and-energy-integrity.md).
- Deliverables: prefer `.inp` via `Export(4,...)` and `.bkp` via `Export(1,...)` from
  the saved case. `SaveAs2(...bkp)` has both successful and failed reopen histories;
  validate the chosen method on the local version. COM initialization can rewrite
  backups in the opened folder: do NOT initialize any file in the deliverable folder.
  Copy each candidate into a fresh scratch directory, then use `InitFromFile2` and
  `Run2(False)` there for cold-start validation. Record source/final hashes and actual
  file content/type; preserve the delivered bytes. Opening a GUI is not a substitute
  for run validation, and requires compatibility with the user's tool restrictions.
- 新建流程且无指定排布时使用Aspen原生默认排版；已有模型保留用户最新PFD、真实端口、连线及默认标签。参数修复不授权重新排版。

- Heat/enthalpy outputs: verify leaf nodes and UnitString; collection Value and missing
  output are not scalar results. Calibrate report conversion rather than assuming a
  universal calorie factor. See [references/pdo-heat-integration-and-delivery-lessons.md](../../references/pdo-heat-integration-and-delivery-lessons.md).
