# 从原案例/机制迁入的报错诊断

来源：thermally-coupled-distillation.md。以下观察仅支持原文限定的版本、条件与已闭合范围；不提升为普遍故障原因或默认参数。

## 3. Initial estimates - PHASE matters (root cause of dry-up / severe errors)

- `REF-PF` (reflux, liquid): set initial T BELOW the bubble point so it flashes all-liquid
  (for BZ/TOL/EB at 0.24 bar use ~50 C).
- `REBV-PF` (reboil vapour): set initial T ABOVE the dew point so it flashes all-vapour
  (for BZ/TOL/EB at 0.24 bar use ~115 C).
- A bubble-point liquid initial guess for the reboil vapour gives `UDL03A.7640/7660`
  "A LIQUID/VAPOR FEED/PUMPAROUND TO THE TOP/BOTTOM STAGE IS REQUIRED WHEN Q1/QN=0".
