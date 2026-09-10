# Thermally Coupled Distillation (Petlyuk / DWC) 建模经验

Read this reference when the user asks to:
- Build a thermally coupled (Petlyuk) column or dividing-wall column (DWC) in Aspen Plus V14.
- Apply heat-integrated distillation to a BTX / benzene-toluene-ethylbenzene type 3-component split.
- Choose energy-saving technology in a system with temperature-sensitive components (e.g. styrene polymerisation above ~100 C).

Validated 2026-08-27 on the styrene closed-loop case (C2+C3 benzene/toluene/ethylbenzene section):

reboiler 1.934 MW -> 0.729 MW (-62%), condenser 1.958 -> 0.752 MW, prefractionator has no own
condenser/reboiler. Products were CLOSE but not fully on-spec (benzene purity ~91% vs ~96%,
toluene in EB recycle 0.66 vs 0.5 kmol/h) because benzene/toluene are trace components (1.3% / 5%).

> See also `differential-pressure-thermal-coupling.md` for the 热耦精馏 article summary:
> thermally coupled distillation applicability rules (B-major feed, alpha_AB ~ alpha_BC,
> fixed pressure, high-purity intermediate only) and the differential-pressure two-column
> vapor-recompression upgrade (差压热耦合) with the C3 propylene/propane numbers (-92.3%).

## 0. Temperature constraint FIRST (critical lesson from 2026-08-27)

- Selecting an energy-saving technology must NOT look only at the original column top/bottom
  temperature difference. It must consider whether the technology RAISES temperature anywhere
  on a temperature-sensitive stream.
- Styrene polymerises rapidly above ~100 C. In an EB/styrene plant:
  - A heat pump COMPRESSES and SUPERHEATS the overhead vapour -> outlet can reach 110-132 C,
    which is unacceptable on any stream containing styrene (even 0.1-0.2%).
  - If a column's bottoms already run at >100 C (e.g. C1 109 C, 99.8% styrene), a heat pump is
    structurally infeasible: the hot side must condense ABOVE the bottoms temp, i.e. >100 C.
  - Prefer technologies that do NOT raise temperature: feed-efficient heat integration, thermal
    coupling (Petlyuk/DWC), multi-effect, heat recovery - all "cooler or same" technologies.
- Always tabulate max temperature per stream/block of the NEW flowsheet and compare against the
  100 C styrene limit (or the user-specified component constraint) BEFORE delivering.

## 1. Local reference case

- Source folder: `D:\BaiduNetdiskDownload\隔壁塔精馏\`
  - `隔壁塔精馏模型（双塔）.apwz` - Petlyuk-equivalent TWO-column model (B8 prefractionator + B9 main column, ethanol/n-butanol/hexanol).
  - `隔壁塔精馏模型-合并为1个塔10.14.apwz` - single-tower DWC-equivalent model.
- Export the dual-tower case to .inp (COM `Export(4,...)`) and copy its FLOWSHEET / BLOCK / DESIGN-SPEC patterns.

## 2. Petlyuk-equivalent two-column structure (validated)

```
FLOWSHEET
    BLOCK PF IN=<FEED> REF-PF REBV-PF OUT=V-PF L-PF
    BLOCK MC IN=V-PF L-PF OUT=<D> <B> <SIDE> REF-PF REBV-PF
```

- **PF (prefractionator)**: `CONDENSER=NONE REBOILER=NONE`, NO `COL-SPECS` entries (leave the
  `COL-SPECS` sentence empty), only `P-SPEC`. Its separation is driven entirely by the coupling
  streams from MC. Feed at ~middle stage; reflux `REF-PF` at stage 1; reboil vapour `REBV-PF` at
  stage NSTAGE+1 (Aspen accepts a feed stage one above the last tray for a reboiler-less column).
- **MC (main column)**: normal `CONDENSER=TOTAL` + internal reboiler, 35-40 stages.
  - PF top vapour **V-PF (light components) feeds the UPPER section** of MC.
  - PF bottom liquid **L-PF (heavy components) feeds the LOWER section** of MC.
    (Writing them the wrong way round -> top trays dry up, separation collapses.)
  - Liquid side draw near/just above the V-PF feed stage -> `REF-PF` (PF reflux).
  - Vapour side draw at the L-PF feed stage -> `REBV-PF` (PF reboil vapour).
  - Product side draw at the middle section -> intermediate component product.
- Side-draw flow rates are EXPLICITLY specified in `PRODUCTS` with `MOLE-FLOW=<value>`
  (or `MASS-FLOW=`), exactly like the reference case:
  `PRODUCTS D 1 L / B 40 L / SIDE 14 L MOLE-FLOW=31. / REF-PF 7 L MOLE-FLOW=80. / REBV-PF 28 V MOLE-FLOW=300.`
- Reflux-ratio / distillate: `COL-SPECS DP-STAGE=... MOLE-D=... MOLE-RR=...` as INITIAL values,
  then flowsheet-level DESIGN-SPEC vary them to meet product specs.
- Tear streams: `REF-PF` and `REBV-PF` in a `BROYDEN` convergence block (or let Aspen auto-select
  with `PARAM TEAR-METHOD=BROYDEN`).

## 3. Initial estimates - PHASE matters (root cause of dry-up / severe errors)

- `REF-PF` (reflux, liquid): set initial T BELOW the bubble point so it flashes all-liquid
  (for BZ/TOL/EB at 0.24 bar use ~50 C).
- `REBV-PF` (reboil vapour): set initial T ABOVE the dew point so it flashes all-vapour
  (for BZ/TOL/EB at 0.24 bar use ~115 C).
- A bubble-point liquid initial guess for the reboil vapour gives `UDL03A.7640/7660`
  "A LIQUID/VAPOR FEED/PUMPAROUND TO THE TOP/BOTTOM STAGE IS REQUIRED WHEN Q1/QN=0".

## 4. Flowsheet-level DESIGN-SPEC (.inp syntax)

```text
DESIGN-SPEC DS-TOL
    DEFINE TOLBOT MOLE-FLOW STREAM=C2-BOT SUBSTREAM=MIXED COMPONENT=TOL
    SPEC "TOLBOT" TO "0.5"
    TOL-SPEC "0.00001"
    VARY BLOCK-VAR BLOCK=MC VARIABLE=MOLE-RR SENTENCE=COL-SPECS
    LIMITS "6" "30"

DESIGN-SPEC DS-BZ
    DEFINE BZRAW MOLE-FLOW STREAM=BZ-RAW SUBSTREAM=MIXED COMPONENT=BZ
    SPEC "BZRAW" TO "2.50"
    TOL-SPEC "0.0001"
    VARY BLOCK-VAR BLOCK=MC VARIABLE=MOLE-D SENTENCE=COL-SPECS
    LIMITS "2.0" "3.0"
```
- Two DS varying D and RR simultaneously can oscillate (SECANT "FUNCTION NOT MONOTONIC").
  Start with ONE DS (e.g. purity of the key product via RR), fix the other (D), converge, then add
  the second DS with tight LIMITS around the solution.

## 5. Convergence / tuning lessons (trace-component system)

- The SIDE-DRAW FLOW RATE is the dominant design variable for the intermediate component.
  If intermediate leaks to the bottoms, INCREASE the side draw; if the side stream is mostly the
  heavy component, move the side draw up to the intermediate-rich stages.
- Feed-stage placement of V-PF sets the rectifying-section length for the light product:
  moving V-PF feed DOWN (longer top section) improves light-product purity but raises reflux need.
- Raising RR beyond a limit stops helping if the intermediate path (side draw) is the bottleneck -
  fix the side draw, not just RR.
- Trace-component systems (light 1.3%, intermediate 5% of feed) are HARD: top purity and
  intermediate recovery compete for reflux. Expect "close but not fully on-spec" without a
  systematic sensitivity optimisation (side draw position/flow x RR x PF strength).

## 6. Energy comparison method

- Baseline: sum of the two replaced columns (condenser + reboiler duties).
- Heat-coupled: MC condenser/reboiler duties (PF should be ~0/0 - verify).
- Report % saving on reboiler and condenser. Same product basis (same feed and product targets).
