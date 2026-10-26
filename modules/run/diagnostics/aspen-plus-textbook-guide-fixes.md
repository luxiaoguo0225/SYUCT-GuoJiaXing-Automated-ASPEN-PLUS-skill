# 从原案例/机制迁入的报错诊断

来源：aspen-plus-textbook-guide.md。以下观察仅支持原文限定的版本、条件与已闭合范围；不提升为普遍故障原因或默认参数。

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
