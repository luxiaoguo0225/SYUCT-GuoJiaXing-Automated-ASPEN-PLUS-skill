# Run Verification and Recycle Reconciliation

## Table of contents

1. Always read the `.his` file after a run
2. Reconcile tear streams with `Reconcile()`
3. HeatX `RATING` spec that stays complete and clean
4. Strip PFD layout without breaking files
5. Report unit pitfalls

## 1. Always read the `.his` file after a run

The GUI summary and `NextIncomplete` do not expose every engine message. A
Simulation Error can hide in the `.his` file even when the control panel looks
finished, and a WARNING is not an ERROR. Read the newest `.his` before
reporting results.

- `.bkp` runs: Aspen writes `_xxxxxx.his` next to the case file.
- `.apwz` runs: Aspen extracts to `<name>_N` subfolders and may delete the
  `.his` on `Quit()`. Scan recursively and copy the `.his` while the document
  is still open.
- Decode bytes as `latin1` first, then try `utf-8` / `utf-16-le`. Count:
  `ERROR WHILE EXECUTING`, `SEVERE ERROR`, `TERMINAL ERROR`,
  `WARNING WHILE EXECUTING`, `TEMPERATURE CROSSOVER DETECTED`.
- A clean run either contains `NO ERRORS OR WARNINGS GENERATED` or simply has
  zero `ERROR` / `WARNING` tokens.

- The `Summary of Simulation Errors` counts the WHOLE run, including transient
  iteration-zero messages. A fully converged run can still show `Severe Errors`
  / `Errors` counts (e.g. RadFrac tray dry-up `UDL03.3`, component-balance
  `UDL03.2`, HeatX `HEATX.4` temperature crossover) even when `BLOCK STATUS` says
  `Calculations were completed normally`. For diagnosis, use `CONVERGENCE STATUS` (tears + design specs), `BLOCK STATUS`, and independent physical residuals together with the message history to distinguish transient from persistent faults. This does not waive the final clean-delivery requirement: save corrected initialization, reopen independently, and rerun until the current task's required `.his`/Control Panel 0 Severe / 0 Error / 0 Warning is satisfied. Unresolved warnings must be reported as unmet acceptance, never hidden.
- The newest `.his` is written next to the case/working directory with a random
  `_xxxxxx.his` name; copy it immediately after `Run2` (it can be deleted on
  `Quit()`), then count `*** SEVERE ERROR`, `**  ERROR`, and `*   WARNING`.
- Reboil-vapor tear streams initialized at bubble point flash to `V=0` (liquid)
  and are the ROOT CAUSE of the `UDL03.3` dry-up + `UDL03.2` + `HEATX.4`
  temperature-crossover cluster on bare-tower loops. Set their initial T above the
  dew point (all vapor). See
  `double-effect-distillation-and-design-spec.md`.

```python
from pathlib import Path

def his_verdict(data: bytes) -> dict:
    text = ""
    for enc in ("latin1", "utf-8", "utf-16-le", "gb18030"):
        try:
            text += "\n" + data.decode(enc)
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue
    low = text.lower()
    return {
        "errors": low.count("error while executing")
        + low.count("severe error")
        + low.count("terminal error"),
        "warnings": low.count("warning while executing"),
        "crossover": low.count("temperature crossover detected"),
    }
```

## 2. Reconcile tear streams with `Reconcile()`

When a recycle loop starts badly and throws transient first-pass errors, run
the case once to a converged base, then copy the converged tear-stream values
back into inputs:

```python
flags = (
    67108864  # HAPP_RECONCILE_TEARSTREAMS
    | 4        # HAPP_RECONCILE_TP
    | 64       # HAPP_RECONCILE_TF
    | 32       # HAPP_RECONCILE_CF
    | 1048576  # HAPP_RECONCILE_QUIET
    | 1        # HAPP_RECONCILE_INPUT
)
apwn.Run2(False)
apwn.Reconcile(flags)
```

This can remove the transient crossover/error on the next in-session run.

**Persistence caveat:** `Reconcile()` updates the in-memory inputs, but the
effect does not reliably survive `SaveAs2` + reopen. A fresh open of the saved
file can hit the same first-pass error again. Never claim a fix is persistent
until you reopen the saved file and rerun, then read the `.his` again.

## 3. HeatX `RATING` spec that stays complete and clean

- `RATING` + `AREA` only runs cleanly, but the GUI can still mark the HeatX
  "input incomplete" because no specification is set.
- Valid `SPEC` enum values are `T-HOT`, `T-COLD`, `DUTY`, `VFRAC-HOT`,
  `VFRAC-COLD`. Set `Input\SPEC` and `Input\VALUE`.
- `VFRAC-HOT=0` forces full condensation and can trigger a transient
  `TEMPERATURE CROSSOVER` ERROR on cold start. `ALLOW-TCROSS=YES` removes the
  ERROR but leaves a WARNING in the `.his`.
  A second root cause of the same crossover is a liquid-phase (bubble-point)
  reboil-vapor tear initial guess — fix the initial T, not just the HeatX flag.
- Most robust tested combination: `RATING` + `AREA` + `SPEC=T-COLD` with the
  converged cold outlet temperature (for the styrene case, `82.08 C`). A fresh
  open and rerun is complete, and the `.his` has no ERROR or WARNING.
- Check completeness on the data root, not the tree root:

```python
result = apwn.Tree.FindNode(r"\Data").NextIncomplete("")
# Observed V14 return: (path, code); complete input is ("", 0).
path, code = result  # Verify signature on the installed version.
```

`apwn.Tree.NextIncomplete("")` can raise
`Aspen.Navigation: feature not active` even when the model is complete.

## 4. Strip PFD layout without breaking files

- Strip PFD only when explicitly requested; otherwise preserve the user's layout.
- `.bkp`: find `GRAPHICS_BACKUP` and the next `$_SUMMARY_FILE`, or `$_ADS_FILE`
  when SUMMARY is absent. Preserve prefix/suffix bytes; stop if a boundary is unknown.
  See [pfd-layout-preservation-and-review.md](pfd-layout-preservation-and-review.md).
- `.inp`: remove everything from `;PFS V 5.00` onward.
- `.apwz`: rewrite the inner `.bkp` and preserve the zip comment
  (`Aspen_Compound_File_Settings_v1.0` manifest). If the comment is lost,
  Aspen cannot open the `.apwz` (error 2041 "cannot open file").
- Saving an `.apwz` from a stripped `.bkp` makes Aspen regenerate a fresh
  `GRAPHICS_BACKUP`. That is acceptable when the requirement is only to remove
  the custom layout.

## 5. Report unit pitfalls

Reports may show `HEAT DUTY` in `WATT` or `CAL/SEC` depending on the case.
Do not assume every `CAL/SEC` uses 4.184 J/cal. The 2026-10-01 PDO V14 case
was calibrated against explicit WATT input/export and used 4.1868 J/cal. Check
UnitString and a known duty in the active unit set; record the measured conversion.
`NET WORK REQUIRED` is often in `KW`, but verify the report header. Read enthalpy
leaf values or export the report, not collection-root Value. See
[pdo-heat-integration-and-delivery-lessons.md](pdo-heat-integration-and-delivery-lessons.md).
