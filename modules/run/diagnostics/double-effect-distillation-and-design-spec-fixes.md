# 从原案例/机制迁入的报错诊断

来源：double-effect-distillation-and-design-spec.md。以下观察仅支持原文限定的版本、条件与已闭合范围；不提升为普遍故障原因或默认参数。

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
