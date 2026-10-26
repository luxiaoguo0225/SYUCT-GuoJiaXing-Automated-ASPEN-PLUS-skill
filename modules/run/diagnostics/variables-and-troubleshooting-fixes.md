# 从原案例/机制迁入的报错诊断

来源：variables-and-troubleshooting.md。以下观察仅支持原文限定的版本、条件与已闭合范围；不提升为普遍故障原因或默认参数。

## Common Failure Modes

- `AE_UNDERSPEC` on write: write the scalar leaf node (`Input\TEMP\MIXED`) instead of the parent (`Input\TEMP`).
- Error 2041 "cannot open file": use `InitFromFile2`, and check the `.inp` syntax. A `RadFrac` block with `VARY` but no flow spec in `COL-SPECS` fails translation; include `MOLE-B=` as the initial guess alongside `VARY`.
- Total condenser with noncondensables (e.g. H2): produces unphysical cryogenic overhead temperatures. Use `CONDENSER=PARTIAL-V` and a vapor distillate product instead.
- Component-level output may not appear in the COM tree when reopening a saved `.apwz`; read or export the report immediately after `Run2`.
- `EngineSimulation` property can raise a COM error on some documents; it is not required for open/edit/run/read workflows.
- `Visible = True` before initialization fails; initialize the document first.
- Leftover `AspenPlus.exe` process after `Quit()`: stop it with `Stop-Process` only if it was started by automation and the user is not actively using Aspen.
