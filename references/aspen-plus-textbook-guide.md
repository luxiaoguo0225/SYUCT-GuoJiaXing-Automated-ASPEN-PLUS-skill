# Aspen Plus Textbook Workflow and Convergence Guide

This reference condenses the Aspen Plus 教程 (孙兰义) into actionable rules for
the automation bridge. It complements [engineering-modeling-basics.md](engineering-modeling-basics.md)
with property-method selection, unit-model choices, flowsheeting tools, and
convergence troubleshooting.

## Property Method Selection

The property method controls K values, enthalpy, entropy, Gibbs energy, molar
volume, viscosity, thermal conductivity, and diffusivity. A wrong method can
converge while being physically wrong.

### State Equation vs Activity Coefficient

| Situation | Recommended family |
| --- | --- |
| Nonpolar/weakly polar hydrocarbons, gas processing, high pressure | `PENG-ROB`, `RK-SOAVE`, `SRK` |
| Polar/nonideal liquids at low-to-moderate pressure | `NRTL`, `UNIQUAC`, `WILSON` |
| Prediction without binary data | `UNIFAC`, `UNIF-DMD`, `PSRK`, `PRMHV2`, `PRWS` |
| Light gases in aqueous solution | add Henry components |
| Carboxylic acids and vapor association | `NRTL-HOC` / `UNIQ-HOC` |
| Electrolytes | `ELECNRTL` |
| Water/steam | `STEAM-TA`, `IAPWS-95` |
| Petroleum and wide-boiling hydrocarbons | `BK10`, `CHAO-SEA`, `GRAYSON`, `PENG-ROB` |

Key checks:

- After selecting components and method, inspect binary interaction parameters
  before running.
- Run once after changing components/method so Aspen refreshes binary
  parameters.
- For LLE, make sure the binary parameter source is an LLE databank (for example
  `LLE-LIT`) and the model can predict two liquid phases (`WILSON` cannot).
- Use property analysis/regression when parameters are missing or results do not
  match plant data, especially for infinite-dilution activity coefficients.

## Unit Model Cheat Sheet

Full `.inp` sentences below are limited to blocks already exercised by this
skill (Flash2, Heater, HeatX, RadFrac, RStoic). Other blocks are described by
their GUI specification paths and COM variable names; build those cases through
the bridge and verify the input file with the Control Panel before relying on
the exact sentence syntax.

### Separators and Splitters

- `Mixer`: combine streams.
- `FSplit`: split a stream into fractions or fixed product flows.
- `Flash2`: two-outlet flash, specify two of temperature/pressure/duty/vapor
  fraction.
- `Flash3`: three-outlet flash with organic/aqueous/vapor.
- `Decanter`: liquid-liquid separation.
- `Sep`/`Sep2`: component or split-fraction separators for early simple models.

Example flash:

```text
BLOCK FL1 FLASH2
    PARAM TEMP=40.0 PRES=0.4
```

### Pressure Changers

- `Pump`: liquid pressure change, power calculation.
- `Compr`: single-stage compressor/expander.
- `MCompr`: multistage with intercoolers.
- `Valve`: adiabatic pressure reduction or valve sizing.
- `Pipe`/`Pipeline`: pressure drop and heat loss in piping.

In the GUI, `Pump` accepts discharge pressure, pressure increase, pressure
ratio, power, or a head-vs-flow performance curve. `Compr` accepts isentropic,
polytropic, or positive-displacement models. `MCompr` adds interstage coolers.

### Heat Exchangers

- `Heater`: outlet temperature, duty, vapor fraction, or subcooling/superheat.
- `HeatX`: two-stream; shortcut design, detailed rating, or rigorous EDR.
- `MHeatX`: multi-stream, energy-integration oriented.

HeatX shortcut design example used in this skill:

```text
BLOCK HX-FEED HEATX
    PARAM DUTY=15000.0 CALC-TYPE=DESIGN MIN-TAPP=5. U-OPTION=PHASE F-OPTION=CONSTANT CALC-METHOD=SHORTCUT
    FEEDS HOT=BOT COLD=FEED
    OUTLETS-HOT BOT-HX
    OUTLETS-COLD FEED-HX
```

For rating, switch `CALC-TYPE` to rating, add geometry, fouling factors, and
pressure-drop limits.

### Columns

- `DSTWU`: shortcut design (minimum stages, minimum reflux, stage estimate).
- `Distl`: shortcut rating (fixed stages/reflux, product composition estimate).
- `RadFrac`: rigorous single column, including absorption, stripping,
  extractive/azeotropic, three-phase, and reactive distillation.
- `Extract`: liquid-liquid extraction column.
- `MultiFrac`/`PetroFrac`/`SCFrac`: complex petroleum towers.

Workflow: run `DSTWU` first, use its reflux/stage/feed-stage estimates as
initial values, then build `RadFrac` and add design specs.

### Reactors

- `RStoic`: known stoichiometry and conversion/extent.
- `RYield`: known yield distribution, no stoichiometry needed.
- `REquil`: equilibrium with known stoichiometry and phase equilibrium.
- `RGibbs`: Gibbs free energy minimization, no stoichiometry needed.
- `RCSTR`: kinetic CSTR.
- `RPlug`: kinetic PFR with heat transfer options.
- `RBatch`: kinetic batch/semi-batch reactor.
- For kinetic input, prefer Aspen's `General` expression layout first, then fit the data into `LHHW` or `PowerLaw` as needed.

RStoic example:

```text
BLOCK R1 RSTOIC
    PARAM TEMP=650.0 PRES=0.4
    STOIC 1 MIXED EB -1.0 / STY 1.0 / H2 1.0
    CONV 1 MIXED EB 0.65
```

For kinetic reactors, define a `Reactions` set (for example `POWERLAW`), select
it in the block's `Reactions` page, and assign the reactor volume or residence
time.

## Flowsheeting Tools

### Design Spec

Design specs solve "what input value makes an output equal a target?".

Define:

- Sampled variable or Fortran expression.
- Target and tolerance.
- Manipulated input variable with lower/upper bounds.
- Optional Fortran expression.

Examples:

- Tune condenser temperature so product purity equals 98%.
- Tune solvent flow so absorber off-gas composition equals 0.5%.
- Tune steam flow so brine concentration reaches 20%.

Use `Sensitivity` first to confirm the manipulated variable can actually move
the sampled variable across the target.

### Calculator

`Calculator` embeds Fortran or Excel logic into the flowsheet:

- Feedforward control: compute an input before a block runs.
- Correlate two inputs, for example keep methanol flow equal to toluene flow.
- Write results to reports or files.
- Drive a variable from another result.

Define input/output variables, enter Fortran, and choose the execution sequence
carefully. Variables that start with I-N and are not declared are integers.

### Transfer and Balance

- `Transfer`: copy a stream or variable to another location in the flowsheet.
- `Balance`: enforce mass/energy balance around a set of blocks and update
  unknown stream variables, often replacing a design spec/calculator.

### Sensitivity, Optimization, Constraint

- `Sensitivity`: vary one or more input variables and tabulate results; no
  effect on the base case.
- `Optimization`: maximize/minimize an objective by adjusting decision variables.
- `Constraint`: enforce equality/inequality constraints on the optimization.

Recommended order for optimization:

1. Converge the base simulation without optimization.
2. Run sensitivity to find feasible decision-variable ranges.
3. Add constraints.
4. Add the objective.

## Flowsheet Convergence

Aspen defaults to sequential modular calculation. Recycles and design specs
create iteration loops that must be converged.

### Core Objects

- Tear stream: a guessed recycle stream.
- Convergence block: updates tear streams and manipulated variables.
- Sequence: order of unit blocks and convergence blocks.

If the user does not define these, Aspen auto-selects them. The defaults are
usually good, but they can fail on strongly coupled or heavily recycled flows.

### Convergence Methods

| Method | Default use | Notes |
| --- | --- | --- |
| `Wegstein` | tear streams | Fast, ignores interactions; set q bounds if oscillating |
| `Direct` | fallback | Slow but robust; useful for diagnosing accumulation |
| `Secant` | single design spec | Use Bracket for flat functions |
| `Broyden` | multiple design specs / coupled loops | Handles variable interactions |
| `Newton` | strongly coupled loops | Expensive, use when Broyden fails |
| `Complex` | optimization with inequality constraints | Direct search |
| `SQP` | optimization | Simultaneously converges tears/design/optimization |

Default max flowsheet evaluations is 30. Increase to 100 or more for hard
recycles. For Wegstein:

- q < 0 accelerates.
- q = 0 is direct iteration.
- 0 < q < 1 damps oscillation.

If iteration oscillates, try q between 0 and 1 or switch to `Broyden`. If it
converges slowly, lower q bound to -20/-50 or provide better tear estimates.

### Tear Stream Selection

Choose a tear stream that:

- Has relatively stable composition.
- Has few variables/components.
- Is an outlet of a mild block such as a Heater rather than a reactor or column,
  when possible.

Provide an explicit initial estimate for every tear stream. A zero-flow tear
stream inside a recycle to a RadFrac often causes iteration-zero severe errors.

### Flowsheet Build Strategy

From the 孙兰义 workflow:

1. Split the process into subflowsheets.
2. Start with simple blocks (`Sep`, `Sep2`, `Heater`, `Mixer`, `FSplit`).
3. Optionally disable energy balance while material balance is being fixed.
4. Use default convergence first.
5. Replace simple blocks with rigorous blocks one or two at a time.
6. Run each rigorous block standalone with simple-block results as initial
   values before reinserting it into the recycle.
7. Provide tear-stream estimates from the simple model.
8. Tighten design specs gradually.

### Troubleshooting Checklist

- Read the first error/warning in the control panel; later messages are often
  consequences.
- Raise diagnostic level (`Simulation=3`, `Convergence=5`) to see tear history.
- Check for component accumulation: every component must have a leaving path.
- For flat design-spec response, use sensitivity to check bounds and choose a
  better manipulated variable.
- For nonmonotonic design specs, use `Bracket=Check bounds`.
- For wide-boiling absorbers, use `Sum-Rates` or `Absorber=Yes`.
- For azeotropic systems, use `Azeotropic` convergence with `Newton`.
- For strongly nonideal systems, use `Nonideal` or `Strongly non-ideal liquid`.
- For very strict purity specs, converge a relaxed case first, then tighten.
- Before changing anything, reinitialize so old converged results are not reused.

## RadFrac-Specific Convergence

RadFrac has two algorithm families:

- Inside-out variants: `Standard`, `Sum-Rates`, `Nonideal`.
- `Newton` (Naphtali-Sandholm) for highly nonideal three-phase and azeotropic
  systems.

Convergence method presets:

- `Standard`: most two/three-phase columns.
- `Petroleum/Wide-boiling`: many components, design specs, wide-boiling.
- `Strongly non-ideal liquid`: slow or failed Standard convergence.
- `Azeotropic`: azeotropic separations.
- `Cryogenic`: low-temperature air separation.
- `Custom`: pick algorithm and initialization manually.

Design-spec handling:

- Nested middle loop: minimizes weighted squared errors; design spec count may
  exceed manipulated variable count.
- Simultaneous middle loop: solves specs with the column equations; spec count
  must equal manipulated count and bounds are not used.

Common RadFrac failure causes:

- Infeasible design specs (for example ignoring a noncondensable component).
- Conflicting specs (condenser temperature above bubble point for the specified
  flow).
- Too-small reflux near minimum reflux or pinch points.
- Very small/zero internal liquid or vapor flows; adjust `Fminfac`.
- Wrong property method or missing binary parameters.
- Total condenser with H2/noncondensables; use partial-vapor condenser.

For absorption, provide top/bottom temperature estimates and consider
`Petroleum/Wide-boiling` when the boiling range is very wide.
