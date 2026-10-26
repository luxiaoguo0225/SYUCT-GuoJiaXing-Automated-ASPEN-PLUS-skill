# 从混合案例迁入的故障处理

来源：column-splitting-and-heat-integration.md。历史参数/用户要求仅在原适用范围内有效，不作为当前任务默认设置。

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
