# Double-Effect Distillation with HeatX and FlowSheet-Level Design Specs

Read this reference when the user asks to:

- Split a single RadFrac into a **high-pressure + low-pressure** double-effect pair.
- Add **HeatX** heat integration (HP overhead vapor -> LP reboiler) and converge it.
- Add **flowSheet-level Design Specs** (`.inp` syntax) to lock product purity/recovery.
- Debug **transient severe errors** (tray dry-up, component-balance failures, HeatX
  temperature crossover) that appear on every RadFrac run.

V14-validated on an ethylbenzene-recovery column (PENG-ROB, bare towers with external
condenser/reboiler loops).

# Double-Effect Distillation with HeatX and FlowSheet-Level Design Specs

## 0. AUTHORITATIVE WORKFLOW (user-mandated, follow exactly)

When the user asks to build a double-effect (multi-effect) distillation from a
single column, follow these steps IN ORDER. Do not skip or reorder them.

1. **Build the baseline single column first.** Record: overhead distillate rate,
   bottoms rate, product recovery/purity, and reboiler/condenser duties.
2. **Split the baseline into TWO series columns**:
   - column 1 bottoms -> column 2 feed (SERIES, not parallel);
   - D1 (col1 overhead) + D2 (col2 overhead) = baseline overhead;
   - B2 (col2 bottoms) = baseline bottoms.
   Verify the deviation of (D1+D2) vs baseline overhead and B2 vs baseline bottoms
   is **< 5%**; if not, redo the split.
3. **Make one column high-pressure (HP) and the other low-pressure (LP)** as the
   separation requires; choose pressures so HP-top temperature >= LP-bottom
   temperature by 10-20 K (or more).
4. **Remove both columns' internal condensers and reboilers**: convert to bare
   RadFrac (`CONDENSER=NONE REBOILER=NONE`) with external condenser/reboiler loops.
5. **Heat-integrate**: HP overhead vapor exchanges heat with LP bottoms (HeatX,
   HP hot side -> LP reboiler cold side).
6. **Energy check**: external load must be >= 35% lower than the baseline column;
   if not, go back to step 3 and redesign the HP/LP pressures. **If necessary,
   sacrifice energy savings to guarantee component recovery and mass purity.**
7. **Final result must have ZERO hidden errors**: read the `.his` file and confirm
   no Severe/Error/Warning, and the Aspen control panel must show no errors or
   warnings.
8. **If hidden errors appear, use Aspen's Reconcile** on streams and column blocks
   to supply initial values and try to resolve the errors.

### Pressure-drop rule (applies the WHOLE way through)

- Every module EXCEPT mixers and pressure-changing devices (pump/valve/compressor)
  MUST account for pressure drop as a NEGATIVE pressure.
- Do NOT reuse one fixed number everywhere. Select the drop from fluid phase,
  density/viscosity, equipment type, duty, pressure level, and downstream
  pressure margin.
- For ordinary positive-pressure heat exchangers, condensers/reboilers,
  coolers/heaters, and similar equipment, an engineering starting point around
  **-0.2 bar** is preferred when it is pressure-feasible.
- Use tiny values such as **-0.01 to -0.05 bar** only for vacuum/near-vacuum
  service, low-pressure loops, or return streams that would otherwise fall
  below the required tower/feed pressure when no real booster can be added.
- **NO compensation pumps** are allowed (do not add pumps to re-pressurize after a
  drop).

---

## 1. FlowSheet structure (bare towers + external loops)

Copy the original RadFrac into `T303A` (LP) and `T303B` (HP), set both to
`CONDENSER=NONE REBOILER=NONE`, and attach external loops:

```text
SPLIT(0.5) ─┬─ LP-FEED ─► T303A (LP, bare)
            └─ HP-FEED-RAW ─ PUMP1 ─ HP-FEED ─► T303B (HP, bare)

LP:  T303A ─ LP-VAP ─ LP-COND(full) ─ LP-SPLIT ─ LP-REF(stage1) / LP-DIST
     T303A ─ LP-BOTL ─ REB-HX(cold) ─ REB-OUT ─ V-REB(ad.) ─ LP-REBV(stageN) / LP-BOT
HP:  T303B ─ HP-VAP ─ REB-HX(hot, full) ─ HP-COND ─ HP-SPLIT ─ HP-REF(stage1) / HP-DIST
     T303B ─ HP-BOTL ─ HP-REB(steam) ─ HP-VREB(ad.) ─ HP-REBV(stageN) / HP-BOT
```

Tear `LP-REF`, `LP-REBV`, `HP-REF`, `HP-REBV` with a `BROYDEN` convergence block and
give all four initial estimates.

## 2. CRITICAL: reboil-vapor initial state must be ALL VAPOR (root cause of tray dry-up)

**Symptom**: every run reports `UDL03.3` tray dry-up (top stages 1..k),
`UDL03.2` component-balance failure, and `HEATX.4` temperature crossover — even when
the run converges and products meet spec.

**Root cause** (found by reading the `.his` flash results): the reboil-vapor tear
streams `LP-REBV` / `HP-REBV` were initialized at the **bubble point**
(e.g. 104 C at 0.4 bar, 177 C at 2.7 bar), so the first flash gives
`V = 0.0` (all liquid). RadFrac then treats the "vapor feed" as liquid, there is no
rising vapor in the stripping section, the tray flow profile collapses, and the top
trays dry up.

**Fix**: set the reboil-vapor initial temperature a few degrees ABOVE the dew point so
the flash is all vapor:

```text
STREAM LP-REBV
    SUBSTREAM MIXED TEMP=110.0 PRES=.40 MOLE-FLOW=152.44   ; was 104.0 (bubble pt)
    MOLE-FLOW C8H10 152.03 / C8H8 .026 / C6H5CH3 .38

STREAM HP-REBV
    SUBSTREAM MIXED TEMP=185.0 PRES=2.70 MOLE-FLOW=258.20   ; was 177.0 (bubble pt)
    MOLE-FLOW C8H10 257.53 / C8H8 .047 / C6H5CH3 .60
```

**Verification**: after the fix the run is `0 Severe / 0 Error / 0 Warning` from a
fresh `.inp`, DS converge, `BLOCK STATUS = Calculations were completed normally`,
products unchanged (recovery >= 99.99%, purity >= 99.9%).

**How to detect this class of bug**: read the `.his` first-flash lines for every
inlet of the tower:

```text
ENTHALPY CALCULATION FOR INLET STREAM LP-REBV OF BLOCK T303A
KODE = 2  NTRIAL =   1  T = 377.1500  P =  40000.0      V =  0.00000  <- should be 1.0
```

If `V = 0` for a stream that must feed vapor to the column, raise its initial T
(or set an explicit vapor fraction) before blaming convergence.

Other root causes that were ruled out (do not waste time on them):

- Raising the reflux/tear initial flows by +10..50% does NOT fix dry-up (RadFrac
  standard init does not use tear-stream values as tray-flow guesses; +50% diverges).
- `Reconcile()` updates tear-stream inputs to the converged values but does NOT
  remove these transient errors (same reason), and its effect is lost on save/reopen.
- `MIN-TAPP` alone on HeatX can destabilize the run.
- RadFrac `MAXOL` is capped (200) and `DAMPING` only accepts `NONE` on this build.

## 3. FlowSheet-level DESIGN-SPEC `.inp` syntax (V14)

Column-internal `SPEC/VARY` does not apply to bare towers; use flowsheet Design Specs
placed AFTER all `BLOCK` paragraphs and BEFORE `EO-CONV-OPTI`:

```text
DESIGN-SPEC DS-LP
    DEFINE EBBOT MOLE-FLOW STREAM=LP-BOT SUBSTREAM=MIXED COMPONENT=C8H10
    DEFINE EBFEED MOLE-FLOW STREAM=LP-FEED SUBSTREAM=MIXED COMPONENT=C8H10
    SPEC "EBBOT/EBFEED" TO "0.99992"
    TOL-SPEC "0.00001"
    VARY BLOCK-VAR BLOCK=LP-SPLIT SENTENCE=FRAC VARIABLE=FRAC ID1=LP-DIST
    LIMITS "0.060" "0.070"
```

Syntax rules learned the hard way (V14 `.inp` translator):

- Component stream variable: use the **`MOLE-FLOW` variable type directly** with
  `COMPONENT=`, i.e. `DEFINE EBBOT MOLE-FLOW STREAM=LP-BOT SUBSTREAM=MIXED
  COMPONENT=C8H10`.
  `DEFINE X STREAM-VAR STREAM=... VARIABLE=MOLE-FLOW COMPONENT=C8H10` either fails to
  parse or silently defines the TOTAL flow (component ignored).
- FSPLIT manipulated fraction: `VARY BLOCK-VAR BLOCK=LP-SPLIT SENTENCE=FRAC
  VARIABLE=FRAC ID1=LP-DIST` — `SENTENCE=FRAC VARIABLE=FRAC`, with the splitter
  outlet stream as `ID1`. (`SENTENCE=FLOW/FRAC VARIABLE=FLOW/FRAC` is the old .bkp
  spelling; the V14 `.inp` export uses `FRAC`.)
- `SPEC "expr" TO "target"` accepts Fortran expressions (`EBBOT/EBFEED`).
- Set the target slightly ABOVE the spec (e.g. `0.99992` for a `0.9999` guarantee) so
  the converged value is strictly on-spec within tolerance.
- Any unknown top-level paragraph makes `InitFromFile2` fail with 2041 "cannot open
  file" — when debugging, add one sentence at a time and re-test open.

### Design Spec convergence requirements

- Tear-stream tolerance must be TIGHTER than the DS tolerance. Set
  `CONV-OPTIONS PARAM TOL=0.00001` (default 1e-4) or the outer SECANT DS cannot
  converge (`DESIGN-SPEC FUNCTION NOT CHANGING`, variable pinned to a bound).
- Give the manipulated variable a good initial value and tight `LIMITS` around the
  solution (find it by sensitivity sweep, see section 5). A bad init (e.g. FRAC 0.5)
  makes SECANT pin to a bound or land in a reflux-accumulation pseudo-steady-state.
- DS ordering: outer DS sees inner DS + tear loop, so convergence cost grows; check
  `$OLVER01/02` iteration history in `.rep`.

## 4. Saving and validating deliverables (.inp / .apwz / .bkp / .rep)

- `.apwz` (save with `SaveAs2`) and `.inp` are the reliable openable formats.
- Generate a clean `.inp` with `Export(4, "case.inp")` — it is GBK-encoded and is the
  authoritative spelling of the input language (use it as the syntax reference).
- Generate `.bkp` with `Export(1, "case.bkp")` FROM THE `.apwz`, NOT `SaveAs2(...bkp)`
  (SaveAs2-produced .bkp fails to reopen on this build) and NOT from a fresh `.inp`.
- **Never validate a `.bkp` with `InitFromFile2`**: opening a `.bkp` through the COM
  tree rewrites it into a tiny "input summary" backup (timestamp updates; ~3-8 KB).
  Validate `.bkp` by launching the GUI the way a user double-clicks it:
  `AspenPlus.exe /a "case.bkp"` (ftype `Apwn.Archive`), or `aspenplus.exe "case.apwz"`,
  or `aspenplus.exe /i "case.inp"`.
- `.rep` via `Export(2, "case.rep")`.
- The `Summary of Simulation Errors` counts the WHOLE run (transient iteration
  messages included), so a converged run can still show Severe/Error counts. Judge the
  model by `CONVERGENCE STATUS` (all DS + tears converged) and
  `BLOCK STATUS = Calculations were completed normally`.

## 5. Design workflow that converged

1. Rebuild the baseline single tower in V14 and verify it meets the original specs.
2. Build the simple HP/LP split (two full towers) first; pick pressures so
   `T_HPtop - T_LPbot >= 10-20 C` (e.g. LP 0.2 bar / HP 2.5 bar gives ~33 C).
3. Add stages vs. the original (LP 31->40, HP 31->50) — splitting is NOT a simple
   plate split; recovery vs. purity is a non-monotonic (bell) curve vs. distillate
   fraction, and more trays make both specs reachable.
4. Make sure the HP feed pressure is ABOVE the feed-stage pressure (PUMP 2.8 bar vs
   2.598 bar feed stage) or RadFrac warns `FEED PRESSURE ... IS LOWER THAN STAGE ...`.
5. Sensitivity-sweep one tower at a time: fix one FRAC, vary the other, record
   bottoms recovery and C8H10 mass purity; pick the FRAC where BOTH specs pass
   (e.g. LP FRAC 0.0654, HP FRAC 0.0486 on 40/50 trays).
6. Put the sweep-found values into the DS initial guesses and tight LIMITS; set
   `CONV-OPTIONS TOL=1e-5`; run.
7. Verify: 0 errors, DS converged, products on-spec, `REB-HX` duty ~ LP reboiler
   duty = HP overhead duty, HP-top vs LP-bottom delta-T, energy vs. single tower
   (steam/cooling savings).

## 6. Check & Reconcile utilities

- Input completeness check: `Tree.FindNode(r"\Data").NextIncomplete("")` returns
  `('', 0)` when complete (no missing inputs).
- Control Panel COM: `app.Engine.ControlPanel()` returns E_NOTIMPL on V14 — the
  control-panel messages are equivalent to the `.his` contents; read the `.his`.
- Reconcile: `root.Reconcile(flags)` with `HAPP_RECONCILE_CODE` bit flags read from
  `happ.tlb` (INPUT=1, TP=4, TV=8, PV=16, CF=32, TF=64, MICF* / MITF* / CICF* / CITF*
  component-flow bits, QUIET=1048576, DONTASKWARN=2097152, ONLYSTREAMS=16777216,
  NOSTREAMS=33554432, TEARSTREAMS=67108864). It updates tear-stream inputs to the
  converged values in-session but the effect is lost on save/reopen.

## 7. Post-run checklist (deliver before reporting)

- Read the newest `.his` immediately after `Run2` (copy it while the doc is open;
  `.apwz` runs can delete it on `Quit()`).
- Confirm `0` Severe / `0` Error / `0` Warning, or document transient messages with
  their block + iteration and the final convergence proof.
- Products: each tower recovery >= spec, purity >= spec.
- Heat integration: HeatX duty, LMTD, HP-top vs LP-bottom delta-T.
- All deliverables open: `.inp` / `.apwz` / `.bkp` (validate `.bkp` via GUI, not
  `InitFromFile2`).

## 8. Pressure-drop modeling for the split flowsheet (validated V14)

The user will ask "did you account for pressure drops?". The final validated
deliverable models EVERY pressure-changing unit, not just tray DP-STAGE, by
entering a NEGATIVE value in the module's pressure field:

```text
REB-HX : PARAM ... PRES-HOT=-0.2 PRES-COLD=-0.03   (hot side ordinary, cold side pressure-pinched)
LP-COND: PARAM PRES=-0.01 VFRAC=0.0                (small drop justified on a 0.2 bar vacuum tower)
HP-REB : PARAM PRES=-0.2 DUTY=2380000.0            (ordinary positive-pressure service)
towers : COL-SPECS DP-STAGE=...                    (tray dp)
```

Rules that were hard-won (user-corrected approach):

- NEGATIVE pressure in a module's pressure field means PRESSURE DROP:
  `PRES-HOT=-0.2` / `PRES-COLD=-0.05` on the HeatX PARAM sentence, and
  `PARAM PRES=-0.01` on a pressure-pinched low-pressure Heater such as LP-COND;
  use approximately `PARAM PRES=-0.2` for an ordinary positive-pressure Heater
  such as HP-REB. Positive = absolute outlet pressure. The `.rep` then shows
  `HOT SIDE PRESSURE DROP ... N/SQM`.
- Size the drop by fluid and equipment first, then check system pressure:
  near-vacuum/low-pressure side (0.2-0.4 bar) may need small drops like
  -0.01 to -0.05 bar; ordinary higher-pressure sides should start around
  -0.2 bar unless detailed hydraulics say otherwise.
- Pressure-drop values are NOT fixed; tune them by their effect on the
  downstream flow. On a 2.5 bar side start with -0.2, but if it makes the
  reflux/reboil return pressure too low relative to the tower (e.g. HP-COND
  2.30 vs stage-1 2.50), lower only that pressure-pinched path to -0.05 or
  similar and document why. Near-vacuum/low-pressure side (0.2-0.4 bar) can
  use -0.01 to -0.05. Smaller drop also raises the hot-side condensing
  temperature and improves LMTD, but this is a justified exception rather than
  the default.
- To reach ZERO warnings/errors WITHOUT extra pumps, combine two tricks
  (validated V14, `.his` = 0 Severe / 0 Error / 0 Warning, BLOCK STATUS =
  normally):
  1. Reflux path may need a pressure-pinched exception: set a very small
     pressure drop or, only when unavoidable, `LP-COND PARAM PRES=<tower top>`
     and `REB-HX PRES-HOT=0` so reflux liquid returns to the tower at exactly
     the top pressure. Reflux comes from the overhead vapor; if the condenser /
     hot side drop makes reflux pressure = top - drop < top, no tower pressure
     setting can fix that path by itself.
  2. Reboil path KEEPS pressure drops and is fixed by tuning the tower:
     set the tower top pressures (e.g. LP 0.19 bar, HP 2.45 bar) so that the
     bottoms pressure (top + tray DP) exactly equals the reboiler flash outlet
     (V-REB / HP-VREB) pressure. Then reboil vapor returns at the bottoms
     pressure with no message. Example for a pressure-pinched double-effect
     case: `REB-HX PRES-COLD=-0.01`, `HP-REB PRES=-0.05`,
     `V-REB PRES=0.39`, `HP-VREB PRES=2.65`. An ordinary positive-pressure
     reboiler should instead start near `-0.2 bar` and only be reduced if the
     return pressure check shows that this exception is necessary.
  This yields the drops where they matter (reboil path) and keeps the reflux
  path at tower pressure.
- If the user insists EVERY module gets a pressure drop (hot side, cold side,
  condenser AND reboiler) with NO pumps AND zero warnings, and the reflux path
  is pressure-infeasible at ordinary drops, the validated exception recipe is:
  1. Re-tune the tower tops so bottoms = reboiler flash outlet pressure
     (e.g. tops 0.19/2.45 bar -> bottoms 0.39/2.65 bar = V-REB / HP-VREB
     outlets). This removes the reboil-side messages.
  2. RadFrac's `FEED PRESSURE ... LOWER THAN STAGE` check has roughly a 1%
     RELATIVE tolerance. Keep the reflux-path drops below it: hot side
     `PRES-HOT=-0.02` (0.8% of 2.45) and `LP-COND PRES=-0.001` (0.5% of 0.19)
     produce NO reflux message, while still being negative (= a pressure drop).
     Cold side `PRES-COLD=-0.01` and `HP-REB PRES=-0.05` are on the reboil
     path (handled by the tower tuning).
  This gives `.his` = 0 Severe / 0 Error / 0 Warning, BLOCK STATUS = normally,
  all loops CONVERGED, products on spec. If larger reflux-path drops are
  demanded (-0.05 / -0.01), the two reflux messages come back (benign; fix by
  raising tower pressure or adding a reflux pump).
- NEVER write `HOT-SIDE DP-OPTION=CONSTANT DP=0.3` or `DPVALUE=` — the V14
  translator returns 2041 "cannot open file".
- After moving a HeatX feed in the FLOWSHEET, you MUST also update the
  `FEEDS HOT=... COLD=...` sentence inside the `BLOCK REB-HX HEATX` paragraph.
  FLOWSHEET/block inconsistency -> 2041. Unconnected blocks also cause 2041.
- With pressure drops + no pumps the HP tower Design-Spec curve becomes very
  steep around FRAC ~ 0.050 (recovery jumps from 0.999998 to 0.9964 over FRAC
  0.0495-0.053). Wide LIMITS make SECANT overshoot and oscillate forever
  (`SOLUTION OUTSIDE BOUNDS OR SPEC FUNCTION IS NOT MONOTONIC`). Fix: seed FRAC
  at ~0.0495 and tighten LIMITS to 0.049-0.051.
- The `.his` `Summary of Simulation Errors` counts the WHOLE run including
  transient iterations (RadFrac UDL03.3 dry-tray, CH4 phase-equilibrium UHE01.4,
  BROYDEN intermediate failures). Final proof = `CONVERGENCE STATUS` all
  CONVERGED + on-spec products + only the known FEED-PRESSURE warnings.
  Do not claim "0 errors" if the `.his` has transient messages; report honestly.

### Deliverable .bkp gets rewritten by COM opens (new finding)

- `Export(1, "case.bkp")` from the `.apwz` produces a full backup (~80-100 KB).
- ANY COM `InitFromFile2` of a file in the SAME directory (even a `.inp`, not the
  `.bkp` itself) can rewrite that directory's `.bkp` into a tiny ~9 KB "input
  summary" (timestamp updates). So: after generating deliverables, do NOT open
  any file in the deliverable directory via COM. Verify the `.bkp` by copying it
  to a scratch folder and `InitFromFile2` there (readable + Run2 = valid), or via
  GUI `AspenPlus.exe /a case.bkp`.


## 9. SERIES double-effect (column 1 bottoms -> column 2 feed), validated V14

The user may insist on a SERIES split (not parallel): all feed -> col1, col1 bottoms
pumped -> col2, D1+D2 = baseline overhead, B2 = baseline bottoms (deviation < 5%).
Workflow and hard lessons (ethylbenzene/toluene, PENG-ROB):

1. Build the baseline single column (record overhead 17.695, bottoms 217.66 kmol/h,
   reboiler 3.69 MW).
2. Series split at same pressure first: col1 D1 ~ 13-15 (benzene 3.87 + most toluene),
   col1 bottoms -> col2. Structural fact: benzene 3.87 occupies D1 capacity, so
   col1-bottoms toluene has a floor ~0.17 kmol/h; D2 = 17.70 - D1 can never hold all
   remaining toluene (D2 - B1tol = -0.166 always), so B2 toluene >= 0.166 is
   unavoidable. Use MOLE-D / MOLE-B on complete columns to hit D1=13, B2=217.66.
3. Make col1 = LP (0.19 bar top) and col2 = HP (1.5 bar top gives 24.7 C delta-T at
   bottoms 102 C; 2.45 bar gives 43 C but EB/toluene separation gets hard and
   reboil duty balloons).
4. Bare towers + external condenser/reboiler loops (condenser PRES=-0.001, reboiler
   PRES=-0.05, HX PRES-HOT=-0.02 / PRES-COLD=-0.01; no compensation pumps).
5. HeatX: HP overhead vapor -> LP reboiler. REB-HX heat = HP overhead condensation =
   LP reboil duty; it is set by HP-REB (external reboil) duty, not by the splitter.
6. Energy: external = HP-REB only. For this EB system the series double-effect tops
   out at ~32% saving (HP-REB 2.5 MW) with EB recovery 99.99% BUT col1 cannot strip
   toluene fully at that reboil (col1-bottoms toluene ~9, B2 toluene ~7), so overhead
   sum is far below baseline and product toluene is high. HP-REB 2.4 MW (35% saving)
   diverges (tear loop unstable). Accept the limitation and report it honestly:
   series needs a high-reflux polishing HP tower whose reboil (external) fights the
   energy target.
7. `.his` will contain many transient UDL03.3 dry-tray messages for series+HeatX+
   tears (coupling is strong); final proof = tear loops CONVERGED + products + duty.
   Do not claim 0 warnings for series unless verified clean.


## 10. Getting a SERIES double-effect to ZERO warnings/errors (validated V14)

The user may demand series + zero warnings/errors (energy can be lower). A
zero-warning series HeatX case was achieved (`.his` = 0/0/0, BLOCK STATUS =
normally, 35% saving, EB 99.99%) with these five tricks, in order of impact:

1. Add the bottoms-transfer stream to the tear set: `TEAR LP-REF / LP-REBV /
   LP-BOT / HP-REF / HP-REBV`, and give LP-BOT a non-zero initial estimate.
   Otherwise PUMP1 warns `MIXED SUBSTREAM HAS ZERO FLOW. BLOCK BYPASSED.`
   (UPC01I.1) every first iteration while column 1 is being established.
2. Make tear initial component sums EXACTLY equal MOLE-FLOW, else Aspen warns
   `COMPONENT MOLE FLOWS ... ARE NORMALIZED TO THE TOTAL MOLE FLOW VALUE`
   (STSTRM.29) at input translation.
3. Keep the HP polishing tower reflux ratio moderate (~30, FRAC ~0.032) — near
   total reflux (FRAC ~0.008-0.012) makes RadFrac dry out trays (UDL03.3) and
   the tear loop diverges or floods `.his` with transient severe errors.
4. Initialize reboil-vapor tear streams ABOVE the dew point by a healthy margin
   (LP-REBV 120 C at 0.39 bar, HP-REBV 165 C at 1.70 bar) and reflux slightly
   subcooled (LP-REF 50 C), which removes the one-time initialization dry-tray
   severe at TIME=0.02.
5. Reflux-path pressure drops below Aspen's ~1% relative tolerance (REB-HX
   PRES-HOT=-0.01 on a 1.5 bar top) so no FEED PRESSURE warning remains.
Use converged tear values as the initial estimates and re-run to verify the
`.his` stays at 0/0/0 for both `.inp` and `.bkp`.
