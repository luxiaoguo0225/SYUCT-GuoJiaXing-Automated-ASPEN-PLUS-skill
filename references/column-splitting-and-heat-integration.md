# Column Splitting and Stream Heat Integration

Read this reference when the user asks to:

- Split a RadFrac column into a bare column plus external condenser/reboiler.
- Convert an existing tower inside a recycle loop before splitting.
- Add a stream-to-stream HeatX heat-integration loop to a split column.
- Reuse the benzene/toluene split or heat-integration templates.

## 1. Split a standalone RadFrac into external condenser/reboiler

Workflow:

1. Run the original column and record `D`, `B`, `RR`, `L1`, `VN`, condenser duty, and reboiler duty.
2. If the column is inside a loop, first reconcile/tear the loop and confirm the standalone column converges by itself.
3. Change the RadFrac to `CONDENSER=NONE` and `REBOILER=NONE`.
4. Connect the external loops:

   ```text
   TOP-VAP -> E-COND -> COND-OUT -> V-COND -> COND-LIQ -> SPLIT -> REF / DIST
   BOT-LIQ -> E-REB  -> REB-OUT  -> V-REB  -> REB-VAP / BOT
   ```

5. Return `REF` to stage 1 and `REB-VAP` to stage 20.
6. Provide initial estimates for the recycle streams and use Broyden/Wegstein convergence.

Rules learned from a working BT case:

- `CONDENSER=NONE` plus `REBOILER=NONE` already consume the two allowed RadFrac operating specs. Do not add `D`, `B`, `RR`, `BR`, `L1`, `VN`, `Q1`, or `QN` in `COL-SPECS`.
- Still add `P-SPEC` and a pressure profile such as `COL-SPECS DP-STAGE=0.0005`.
- For the reflux splitter, specify the distillate product flow directly with `MOLE-FLOW DIST 50.0` instead of a split fraction. This keeps the RadFrac fully specified and makes reflux the remainder.
- Set the condenser Heater with the original cold duty and the reboiler Heater with the original hot duty. Keep the Flash2 blocks at zero duty.
- A missing `DP-STAGE`/`DP-COL` and a missing FSPLIT product-flow spec are the most common translation blockers.
- After adding HeatX, Aspen may auto-select `BOT-LIQ + REF` as tear streams instead of `REB-VAP`, which makes the RadFrac bottom vapor feed zero at iteration 0 and raises a severe RadFrac error. Explicitly tear `REF`, `REB-VAP`, and `BOT`, and give `BOT` an initial estimate.

- **CRITICAL: the reboil-vapor tear stream (`REB-VAP` / `LP-REBV` / `HP-REBV`) initial
  state must be ALL VAPOR.** If its initial temperature is at the bubble point, the
  first flash gives `V=0` (liquid), RadFrac treats the vapor feed as liquid, the tower
  has no rising vapor, top trays dry up (`UDL03.3`), the component balance fails
  (`UDL03.2`), and a downstream HeatX may report a temperature crossover (`HEATX.4`).
  Raise the initial T a few degrees above the dew point (e.g. 110 C at 0.4 bar,
  185 C at 2.7 bar) so the flash is all vapor. Detect it by reading the `.his`
  first-flash `V` value of the tower inlets. See
  `double-effect-distillation-and-design-spec.md` for the full double-effect workflow.

Working minimal skeleton:

```text
FLOWSHEET
    BLOCK C1 IN=FEED REF REB-VAP OUT=TOP-VAP BOT-LIQ
    BLOCK E-COND IN=TOP-VAP OUT=COND-OUT
    BLOCK V-COND IN=COND-OUT OUT=OFF-GAS COND-LIQ
    BLOCK SPLIT IN=COND-LIQ OUT=REF DIST
    BLOCK E-REB IN=BOT-LIQ OUT=REB-OUT
    BLOCK V-REB IN=REB-OUT OUT=REB-VAP BOT

CONV-OPTIONS
    PARAM TEAR-METHOD=BROYDEN
    WEGSTEIN MAXIT=500
    BROYDEN MAXIT=500

CONVERGENCE CV BROYDEN
    TEAR REF
    TEAR REB-VAP
    TEAR BOT

BLOCK C1 RADFRAC
    COL-CONFIG CONDENSER=NONE REBOILER=NONE
    FEEDS FEED 10 / REF 1 ON-STAGE / REB-VAP 20 ON-STAGE
    PRODUCTS TOP-VAP 1 V / BOT-LIQ 20 L
    P-SPEC 1 1.2
    COL-SPECS DP-STAGE=0.0005

BLOCK E-COND HEATER
    PARAM DUTY=-1261498.8 PRES=1.2

BLOCK V-COND FLASH2
    PARAM DUTY=0.0 PRES=1.2

BLOCK SPLIT FSPLIT
    MOLE-FLOW DIST 50.0

BLOCK E-REB HEATER
    PARAM DUTY=1105378.69 PRES=1.2

BLOCK V-REB FLASH2
    PARAM DUTY=0.0 PRES=1.2
```

Validation target for the BT 50/50 feed:

- `DIST` = 50, `BOT` = 50 kmol/hr.
- `REF` ~ 100 kmol/hr, `REB-VAP` ~ 120.9 kmol/hr.
- Top/bottom temperatures within a few tenths of the original column.

## 2. Stream-to-stream heat integration with HeatX

Recommended simple integration: preheat the cold feed with the hot bottom product.

```text
FEED (cold side) -> HX-FEED -> FEED-HX -> C1
BOT  (hot side)  -> HX-FEED -> BOT-HX  -> product
```

HeatX input pattern that opens and runs in V14:

```text
BLOCK HX-FEED HEATX
    PARAM DUTY=15000.0 CALC-TYPE=DESIGN MIN-TAPP=5. U-OPTION=PHASE F-OPTION=CONSTANT CALC-METHOD=SHORTCUT
    FEEDS HOT=BOT COLD=FEED
    OUTLETS-HOT BOT-HX
    OUTLETS-COLD FEED-HX
```

Notes:

- `FLASH-SPECS` inside the HeatX block was rejected during testing on this V14 build; omit it and use the default flash settings.
- Keep the external condenser as a full condenser with `PARAM VFRAC=0.0 PRES=1.2` so it never over-subcools when the column vapor flow changes.
- Tune the reboiler with `VFRAC` (for example `0.74234`) so the heat-integrated reflux matches the no-HX baseline, then compare duties fairly.
- Explicitly tear `REF`, `REB-VAP`, and `BOT` as shown above and provide a `BOT` initial estimate; this removes the iteration-zero severe error and the run reports `NO ERRORS OR WARNINGS GENERATED`.
- A 15 kW example with 80 C feed gives `FEED-HX` ~ 83.5 C, `BOT-HX` ~ 111.9 C, and saves about 15 kW of reboiler duty versus the no-HX baseline.

## 3. Vapor recompression heat pump on a split column

For a vacuum column whose overhead and bottoms are close enough in temperature, a vapor recompression heat pump can replace the steam reboiler. There are TWO valid ways to handle the overhead vapor (pick by heat balance):

### Scheme A - NO split, compress the full overhead (全部塔顶蒸汽直接加压)

Use when the reboil duty ≈ the full overhead condensing duty (heat matches). The whole overhead goes to the compressor; there is NO external overhead condenser - every kmol of overhead vapor is compressed, condensed in REB-HX and returned as reflux:

```text
TOP-VAP(全部) -> SUPERH -> COMPR -> HP-HOT
HP-HOT + BOT-LIQ -> REB-HX -> HP-OUT / REB-OUT
HP-OUT -> VALVE -> HP-LOW -> MIX
REB-OUT -> V-REB -> REB-VAP / BOT
MIX -> SPLIT -> REF / DIST
```

### Scheme B - Split the overhead first (提前分流, FSPLIT)

Use when the reboil duty < the full overhead condensing duty (typical). Only part of the overhead goes to the heat pump; the rest goes to an external condenser:

```text
TOP-VAP -> HP-SPLIT -> HP-VAP(部分) -> SUPERH -> COMPR -> HP-HOT
HP-SPLIT -> COND-VAP(其余) -> E-COND -> V-COND -> COND-LIQ -> MIX
HP-HOT + BOT-LIQ -> REB-HX -> HP-OUT / REB-OUT
HP-OUT -> VALVE -> HP-LOW -> MIX
REB-OUT -> V-REB -> REB-VAP / BOT
MIX -> SPLIT -> REF / DIST
```

Scheme selection rule: if `(reboil duty) ~= (overhead condensing duty)`, use
Scheme A (no split, simplest, no external condenser); if reboil duty is
smaller, use Scheme B and send only `HP-SPLIT` to the compressor so the
remaining vapor goes to `E-COND`. In Scheme A a mismatch forces the REB-HX hot
side to partially condense (or add an auxiliary condenser), which complicates
the model - check the duty balance first.

Key input pattern:

```text
BLOCK COMPR COMPR
    PARAM TYPE=ASME-POLYTROP PRATIO=3.5 PEFF=0.8 MEFF=0.95

BLOCK REB-HX HEATX
    PARAM VFRAC-HOT=0.0 CALC-TYPE=DESIGN U-OPTION=PHASE F-OPTION=CONSTANT CALC-METHOD=SHORTCUT
    FEEDS HOT=HP-HOT COLD=BOT-LIQ
    OUTLETS-HOT HP-OUT
    OUTLETS-COLD REB-OUT
```

Rules learned from the styrene vacuum split:

- Split the overhead vapor with an `FSPLIT`; send only part of it to the heat pump and the rest to the external condenser.
- Superheat the compressor inlet so the inlet stays vapor; a wet compressor inlet is the first thing to check if the compressor fails.
- Keep the reboiler on the `HeatX` and let the compressed vapor condense (`VFRAC-HOT=0`); the external reboiler heater is eliminated.
- Return the heat pump liquid through a valve to column pressure, then mix it with external condenser liquid before the reflux splitter.
- Tear `REF` and `REB-VAP`; provide initial estimates for both recycle streams.
- Compare on the same product basis. For the styrene case: compressor 208.3 kW + superheater 100.8 kW vs the eliminated steam reboiler; external condenser duty dropped from -7.822 MW to -6.259 MW.
- Give every heat exchanger and heater an explicit pressure drop. Do not leave
  `REB-HX` hot/cold sides, `E-COND`, or `SUPERH` at zero pressure drop without
  a stated basis. Do not default to tiny `0.0x bar` drops: for ordinary
  positive-pressure exchanger/heater/condenser/reboiler service, start around
  `0.2 bar` unless detailed hydraulics or vendor data say otherwise. Use small
  drops (about `0.01-0.05 bar`) only for vacuum/near-vacuum service or a
  pressure-pinched return loop, and recheck LMTD after adding them.
- To keep `REB-HX` input complete and clean on a fresh open, prefer
  `RATING + AREA + SPEC=T-COLD` with the converged cold outlet temperature
  (styrene case: `82.08 C`). `VFRAC-HOT=0` can trigger a transient temperature
  crossover ERROR/WARNING; see [run-verification-and-reconcile.md](run-verification-and-reconcile.md).

### Compression ratio and temperature difference control

- Do not set `COMPR PRATIO` above `2.5` for this vapor recompression heat pump
  pattern. Prefer `2.3-2.5`; `2.5` is the hard upper limit.
- Sweep `COMPR PRATIO` (for example `2.0 / 2.2 / 2.5 / 2.8 / 3.0 / 3.5`) on a
  copy of the case. Run each point, read the `.his`, and export the report.
- Low PR fails first: when the hot-side condensing temperature cannot stay
  above the cold boiling temperature, the `.his` reports
  `TEMPERATURE CROSSOVER DETECTED` as an ERROR even if the GUI looks converged.
- High PR is not automatically better: it adds compressor power without
  improving the reboiler duty once the minimum approach is adequate.
- Read both the overall `LMTD (CORRECTED)` and the zone section
  `TEMPERATURE LEAVING EACH ZONE`. The real pinch is hot condensing
  temperature minus cold boiling temperature in the condensation/boiling zone.
- Target roughly `5-10 C` minimum approach and `LMTD ~8-15 C` for a
  condenser/reboiler. If the margin is too tight, do not exceed `PR 2.5`;
  instead adjust `REB-HX` area, `HP-SPLIT` flow, or superheater outlet
  temperature, or accept the tighter margin after `.his` verification.
- Styrene vacuum example sweep: `PR=2.5` is the preferred upper limit and is
  clean (`150.7 kW`, `LMTD 5.6 C`, minimum approach `3.7 C`, tight but
  accepted); `PR=2.8` gives `LMTD 8.8 C`, minimum approach `6.8 C` at +19 kW,
  and `PR=3.0` gives `LMTD 10.7 C`, minimum approach `8.6 C` at +31 kW. Both
  exceed the cap and are shown only for reference.
- With `RATING + AREA + T-COLD`, the reboiler duty stays nearly constant
  across PR; the tradeoff is mostly compressor power versus exchanger margin.

## 4. Bundled templates

Copy and adapt these from `assets/column-split/`:

- `bt_split.inp`: bare RadFrac + external condenser/reboiler, fixed duties.
- `bt_split_hx.inp`: same split plus feed/bottoms HeatX.
- `bt_split_no_hx.inp`: baseline with same feed temperature and reboiler vapor fraction, for energy comparison.
- `styrene_heatpump.inp`: styrene vacuum split with external condenser/reboiler plus vapor recompression heat pump.
- `styrene_heatpump_user_layout.bkp`: user-preferred PFD layout template for
  the styrene heat-pump split. Use it as the base when regenerating this
  flowsheet and keep its `GRAPHICS_BACKUP` / `PFS` section. The layout maps only
  when block IDs and stream names stay the same; do not strip the layout unless
  explicitly requested.

## 5. Delivered example files

The portable source of truth is `assets/column-split/`. The `.inp` templates there produce
the split-only, HeatX-integrated, and no-HX baseline cases. For a shareable delivery, run
`build_from_input.py` on the templates and export `.bkp`/`.apwz`/`.rep` files, or copy the
templates into the target machine's skill folder.

## 6. Opening delivered files from chat

Markdown links to local `.bkp`/`.apwz` may open as text in a chat file viewer instead of Aspen.
Tell the recipient to open `.bkp` through Aspen Plus `File -> Open` or Windows Explorer. Do not
rely on machine-specific URL protocols or shortcuts from the author's machine.


## 7. Global acceptance & pressure-drop rules (apply to heat pumps too)

- Final result: read the newest `.his` — must be `0 Severe / 0 Error /
  0 Warning` (no hidden transient errors), and the Aspen Control Panel must
  show no error/warning.
- Hidden errors: use `Reconcile()` on streams and tower modules to seed
  initial values and try to resolve them; verify on a fresh open.
- Pressure drop: every module except mixers and pressure-changing devices
  (pump/valve/compressor) carries a justified NEGATIVE pressure drop. Select
  the value from fluid phase, equipment type, pressure level, and downstream
  pressure margin. Ordinary positive-pressure services should usually start
  near -0.2 bar; reserve -0.01 to -0.05 bar for vacuum/low-pressure or
  pressure-pinched return loops. NO compensation pumps.
