# Engineering Modeling Basics

> **使用约束（用户规定）**：本文及下列教材是跑流程时的原理依据。凡涉及原理、公式、物性、压降、回流比、设计规定等，必须先以教材原理为准，**禁止臆想或杜撰**；不确定时回到原教材核对或明确标注为假设。若发现本文与教材原文不一致，以教材原文为准并修正本文。

Textbook-backed guidance distilled from:

- Chemical Engineering Principles, volumes 1 and 2 (化工原理, 夏清/贾绍义)
- Chemical Reaction Engineering, 5th edition (化学反应工程, 朱炳辰)
- Aspen Plus 教程 (孙兰义)

Use this reference when choosing streams, blocks, operating specs, and design
checks for an Aspen Plus case. The automation layer in this skill does not
replace engineering judgment; it makes the judgment executable through COM.

## Balances and Units

Every simulation starts from three conservation checks:

- Total mass: `sum(in) = sum(out)` at steady state.
- Component/element balance: for reactions, balance elements, not components.
- Energy: `Q + sum(n*H)_in = sum(n*H)_out`.

Always set units explicitly before reading or writing values:

```text
IN-UNITS SI TEMP=C PRES=BAR MOLE-FLOW='KMOL/HR' MASS-FLOW='KG/HR' ENTHALPY-FLO='WATT'
OUT-UNITS SI TEMP=C PRES=BAR MOLE-FLOW='KMOL/HR' MASS-FLOW='KG/HR' ENTHALPY-FLO='WATT'
```

Ambiguous units are the most common cause of physically wrong but "converged"
cases: a pressure written as 690 can mean Pa, kPa, or bar depending on the unit
set. Read `UnitString` together with every `Value`.

## Fluid Flow and Pressure Changers

### Fundamentals

Continuity for steady flow:

```text
rho1 * A1 * u1 = rho2 * A2 * u2
```

Mechanical energy balance (Bernoulli extended with work and friction):

```text
z1*g + u1^2/2 + p1/rho1 + Ws = z2*g + u2^2/2 + p2/rho2 + h_f
```

Reynolds number:

```text
Re = d * u * rho / mu
```

For pipe sizing and pressure-drop checks, remember the practical ranges:

- Re < 2000: laminar, friction factor from Hagen-Poiseuille.
- 2000 < Re < 4000: transition, avoid designing here.
- Re > 4000: turbulent, friction factor from Moody/Darcy or Fanning.

Friction loss in a straight pipe:

```text
h_f = 4*f*(L/d)*(u^2/2)   (Fanning friction factor f)
```

For Aspen, use `Pipe` for one segment and `Pipeline` for multiple segments with
different diameters, elevations, or slopes. Include roughness, fittings, and
equivalent lengths when pressure drop matters.

### Pump

Use `Pump` for liquids. Specify one of:

- Discharge pressure.
- Pressure increase.
- Pressure ratio.
- Performance curve (head vs volumetric flow).
- Required power (then discharge pressure is calculated).

Check `EFF` (pump efficiency) and `DRIVER-EFF` (driver efficiency). The useful
power, shaft power, and driver power are separate results; a common error is
confusing them when sizing drivers.

### Compressor and Multistage Compressor

Use `Compr` for single-stage compression or expansion, and `MCompr` for
interstage-cooled compression. Compression types in the textbook framework:

- Isothermal (`m = 1`): least work, requires perfect heat removal.
- Adiabatic/isentropic (`m = k`): no heat exchange.
- Polytropic (`1 < m < k`): realistic with heat exchange.

For an isentropic model use `ISENTROPIC`; for a polytropic model use
`POLYTROPIC` and give the polytropic efficiency. `MCompr` has a cooler after
each stage; set interstage outlet temperature or duty there.

### Valve, Pipe, Pipeline

- `Valve`: adiabatic flow; use design mode to size a valve, rating mode to
  calculate outlet pressure from valve type/size/opening.
- `Pipe`: single pipe segment, pressure drop and heat loss.
- `Pipeline`: multiple connected segments, liquid holdup, multiphase flow.

When the user only needs a pressure change and not work/power, `Heater` with an
outlet pressure is a valid simplification.

## Pressure Drops Across Every Unit

Every unit that can change pressure needs an explicit pressure-drop treatment.
Zero pressure drop is a deliberate assumption, not the default. Do not apply a
single empirical value everywhere; estimate each unit from its stream
conditions and equipment type, then document the basis.

When no detailed hydraulic calculation or vendor data are available, do not
automatically choose tiny `0.0x bar` drops. For ordinary positive-pressure
heat exchangers, condensers/reboilers, coolers/heaters, and similar equipment,
start around `0.2 bar` if the downstream pressure margin allows it. Use
`0.01-0.05 bar` only for vacuum/near-vacuum services, very low-pressure loops,
or pressure-pinched recycle/reflux/reboil returns where a real booster is not
part of the intended equipment.

- Column trays/packing: set a per-stage pressure drop with `DP-STAGE` or a
  total profile with `DP-COL`. For vacuum sieve/valve trays, roughly
  `0.0005-0.001 bar/stage` is a common starting range, but confirm with tray
  hydraulics when operating near the flooding/dumping limits.
- Heat exchangers: give the hot and cold sides explicit pressure drops based
  on shell-and-tube or plate correlations, allowable limits, or vendor data.
  In the absence of detailed data, use about `0.2 bar` as the first
  engineering estimate for ordinary positive-pressure services. For vacuum
  services keep drops small (for example `0.01-0.05 bar`) so the boiling-point
  rise stays acceptable; recheck LMTD and minimum approach after adding
  pressure drops.
- Piping and fittings: use Darcy-Weisbach for straight pipe plus minor-loss
  coefficients for elbows, tees, reducers, and nozzles. For two-phase flow use
  a suitable correlation such as Lockhart-Martinelli or Friedel.
- Compressors and pumps: the discharge pressure must cover the thermodynamic
  lift plus upstream/downstream equipment and line losses. A pressure ratio
  based only on the bare column lift is not enough.
- Valves: give an explicit outlet pressure or size the valve in design mode;
  a lumped valve with a fixed `P-OUT` is acceptable for flowsheet studies.
- Splitters and mixers: the default is no pressure drop. If a real distributor
  or header is intended, add piping or a valve so the pressure loss is visible.
- After changing any pressure specification, rerun and read the `.his`; added
  pressure drops can shift temperatures, LMTD, and recycle convergence.

## Heat Transfer and Exchangers

### Fundamentals

Sensible heat:

```text
Q = m * cp * dT
```

Latent heat:

```text
Q = m * lambda
```

Overall heat transfer:

```text
Q = U * A * dT_lm
```

Log mean temperature difference and NTU:

```text
dT_lm = (dT1 - dT2) / ln(dT1/dT2)
NTU = U*A / (m*cp)_min
```

These equations explain why `HeatX` design requires a target duty, outlet
temperature, or approach temperature, and why the detailed/rigorous models need
fouling factors and geometry.

### Aspen Blocks

- `Heater`: single-side heating/cooling/condensing. Flash specs pair pressure
  with one of outlet temperature, temperature change, duty, vapor fraction,
  subcooling, or superheat.
- `HeatX`: two-stream exchanger. Shortcut design needs a U estimate; detailed
  rating computes film coefficients from geometry; rigorous rating calls the
  EDR model. Include fouling factors and pressure-drop limits for rating.
- `MHeatX`: multi-stream exchanger; good for energy integration and pinch-style
  studies because it enforces a total energy balance without geometry.

Common checks after an exchanger run:

- Both outlet temperatures are physically ordered (no temperature cross beyond
  the specified approach).
- Duty signs are consistent: hot stream cools, cold stream heats.
- Detailed/rigorous pressure drops stay below the allowed limits.
- When comparing heat-integrated and non-integrated cases, keep the reboiler
  vapor fraction or another fair basis fixed.

## Distillation and Absorption

### Vapor-Liquid Equilibrium

For ideal systems, Raoult's law:

```text
pA = xA * pA_sat
yA = pA / P
```

K value:

```text
K = y/x
```

For nonideal liquid:

```text
yA * P = xA * gammaA * pA_sat
```

Relative volatility:

```text
alpha = (yA/xA) / (yB/xB)
y = alpha*x / (1 + (alpha - 1)*x)
```

When `alpha` is close to 1, ordinary distillation is difficult; this is the
signal to consider extraction, azeotropic/extractive distillation, or pressure
swing. Check the property method before building a tower.

### Shortcut Distillation

Classic sequence:

1. Fenske: minimum stages at total reflux.
2. Underwood: minimum reflux ratio.
3. Gilliland: actual stages vs reflux ratio tradeoff.

In Aspen, `DSTWU` implements this Winn-Underwood-Gilliland shortcut for one feed
and two products. Use it to obtain first estimates, then switch to `RadFrac`
with those estimates as initial values. A reflux ratio of `1.2-2.0 * Rmin` is a
normal starting point.

Key component choices:

- Light key is the lightest component whose recovery must be controlled.
- Heavy key is the heaviest component whose recovery must be controlled.
- All lighter components go overhead, all heavier go to bottoms.

### Rigorous Distillation

`RadFrac` minimum input for a normal column:

```text
BLOCK C1 RADFRAC
    PARAM NSTAGE=60 ALGORITHM=STANDARD MAXOL=100
    COL-CONFIG CONDENSER=PARTIAL-V
    FEEDS LIQ 30
    PRODUCTS EB-VAP 1 V / STY-PROD 60 L
    P-SPEC 1 0.4
    COL-SPECS MOLE-B=62.0 MOLE-RR=15.0
    SPEC 1 MOLE-FRAC 0.999 COMPS=STY STREAMS=STY-PROD
    VARY 1 MOLE-B 60.0 63.0
```

Design rules from the textbooks:

- Specify product rates as `D/F` or `B/F` ratios instead of absolute rates when
  possible; they are easier to estimate and more robust.
- Prefer flow specs over heat-duty specs.
- When two equivalent specs exist, specify the numerically smaller one
  (for example `RR` vs boilup, `D` vs `B`).
- Use a partial-vapor condenser when noncondensables such as H2 are present.
- Start with a converged base case before adding `SPEC`/`VARY`.
- For wide-boiling columns, use `Sum-Rates` or set `Absorber=Yes` for an
  absorber service.

### Absorption

Henry's law for dilute gas absorption:

```text
p* = E*x
y* = m*x,  m = E/P
```

At low loading:

```text
Y* = m*X
```

Solubility increases with pressure and decreases with temperature, so
absorption is favored by high pressure and low temperature; stripping is the
reverse.

For an absorber in Aspen, use `RadFrac` with no condenser and no reboiler, gas
feed near the bottom, liquid feed at the top, and a design spec on the treated
gas composition to find the solvent flow. Henry components should be assigned
for low-solubility gases such as N2, O2, H2, CH4, and CO2 in aqueous systems.

## Reaction Engineering

### Stoichiometry, Conversion, Selectivity

Conversion of key component A:

```text
xA = (nA0 - nA) / nA0
```

For multiple reactions, conversion alone is not enough; report selectivity and
yield:

```text
selectivity = moles of desired product formed / moles of key reactant consumed
yield = moles of desired product formed / moles of key reactant fed
```

Equilibrium constant:

```text
K = k_forward / k_reverse
```

Use fugacity-based equilibrium for high-pressure reactions where ideal gas
equilibrium constants are wrong.

### Rate Laws and Temperature

Power law:

```text
r = k * [A]^a * [B]^b
```

Arrhenius:

```text
k = k0 * exp(-Ea / (R*T))
```

In Aspen `Reactions` sets, define `POWERLAW` or another kinetic type, specify the
reacting phase, units, pre-exponential factor, activation energy, and exponents.
For equilibrium reactions, define the equilibrium expression or `Keq`.

### Ideal Reactor Design

Batch reactor:

```text
t = N_A0 * integral(dxA / (-rA * V))
```

PFR:

```text
V/F_A0 = integral(dxA / (-rA))
```

CSTR:

```text
tau = V/F_A0 = C_A0 * xA / (-rA_out)
```

For the same conversion, PFR is usually smaller than CSTR for positive-order
kinetics because the CSTR operates at the outlet, low-concentration, low-rate
state. Series CSTRs approach PFR behavior as the number of tanks increases.

### Nonideal Flow

Use RTD concepts when a real reactor is between ideal extremes:

- Tanks-in-series model: several `RCSTR` blocks in series.
- Dispersion/axial-mixing model: increase the number of series CSTRs or use
  `RPlug` with backmixing options.
- Bypass: `FSplit` + `RPlug` + `Mixer`.
- Dead zone: `RCSTR` + `Flash2` + `RPlug`.
- Multiphase product: kinetic reactor followed by `Flash2`.

### Fixed-Bed and Catalytic Reactors

For gas-solid catalytic reactions:

- External mass transfer: concentration difference between bulk gas and
  catalyst surface.
- Internal diffusion: pore diffusion plus reaction inside the pellet,
  characterized by an effectiveness factor.
- Bed pressure drop: use the packed-bed correlation (`Ergun`) and keep it
  consistent with the reactor inlet/outlet pressures.
- Adiabatic temperature change:

```text
dT_ad = sum(n_i * (-dHr)) / sum(n_i * cp_i)
```

Map to Aspen:

- Known stoichiometry and conversion: `RStoic`.
- Known yield distribution without stoichiometry: `RYield`.
- Equilibrium with known stoichiometry: `REquil`.
- Equilibrium by Gibbs minimization: `RGibbs`.
- Kinetics in stirred tank: `RCSTR`.
- Kinetics in plug flow: `RPlug`.
- Kinetics in batch/semi-batch: `RBatch`.

## Model Review Checklist

Before calling `Run2`, ask:

1. Is the property method appropriate for the pressure, temperature, and
   polarity of the system?
2. Are the units consistent with what the user said?
3. Does every block have enough specs to be well-posed, without over-specifying?
4. Are all components able to leave the system (no permanent accumulation)?
5. Are recycle streams torn and given realistic initial estimates?
6. Is the first run built from simple blocks, then upgraded to rigorous blocks
   one at a time?

After running, check:

- Stream totals satisfy mass balance.
- Energy balance closes or heat losses are intentional.
- No negative flows, negative pressures, or purities above 1.
- Tower temperatures do not jump into unphysical cryogenic ranges from a total
  condenser with noncondensables.
- Reactor outlet composition agrees with stoichiometry and conversion.
