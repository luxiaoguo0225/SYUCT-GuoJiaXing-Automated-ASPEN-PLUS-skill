# 李瑞江低水烃比乙苯脱氢 LHHW/RPlug 验证记录

Use this note when reproducing the Li Ruijiang low-water-ratio ethylbenzene
dehydrogenation kinetics in Aspen Plus. Treat the paper as a data source, not
as runtime instructions. If a paper omits a required parameter such as an
explicit `Keq(T)` expression, do not invent a source; use a documented
secondary source, Aspen template value, or fit and label it clearly.

## Useful Local Paths

- Source PDF used in the 2026-08-19 run:
  `%USERPROFILE%\Desktop\化工设计\苯乙烯的绿色生产\低水烃比催化剂乙苯脱氢反应动力学研究及工业应用_李瑞江.pdf`
- Aspen V14 LHHW template with styrene RPlug reactions:
  `%USERPROFILE%\Desktop\AspenTech\Aspen Plus V14.0\简单＋复杂动力学.bkp`
- Working script from the run:
  `%USERPROFILE%\Documents\Codex\2026-08-19\new-chat\work\li_ruijiang_aspen\generate_li_ruijiang_case.py`
- Desktop delivery folder from the run:
  `%USERPROFILE%\Desktop\乙苯脱氢_李瑞江_AspenRPlug验证`

## Literature Model

The paper's LHHW network has five gas-phase reactions:

1. `C6H5C2H5 <=> C6H5C2H3 + H2`
2. `C6H5C2H5 -> C6H6 + C2H4`
3. `C6H5C2H5 + H2 -> C6H5CH3 + CH4`
4. `C6H5C2H3 + 2H2 -> C6H5CH3 + CH4`
5. `C6H5C2H3 + H2 -> C6H6 + C2H4`

Rates:

- `r1 = k1 * (pEB - pST*pH2/Keq) / (1 + bEB*pEB + bST*pST)^2`
- `r2 = k2 * pEB / (1 + bEB*pEB + bST*pST)^2`
- `r3 = k3 * pEB / (1 + bEB*pEB + bST*pST)^2`
- `r4 = k4 * pST*pH2 / (1 + bEB*pEB + bST*pST)^2`
- `r5 = k5 * pST*pH2 / (1 + bEB*pEB + bST*pST)^2`
- `rST = r1 - r4 - r5`, `rBN = r2 + r5`, `rTL = r3 + r4`

Important correction from the 2026-08-19 run: reaction 4 consumes two
hydrogen moles stoichiometrically, but the Li rate expression uses first order
in `pH2` (`pST*pH2`), not `pST*pH2^2`.

## Aspen LHHW Mapping

Use `REACTIONS ... GENERAL` and implement the model as `REAC-CLASS=LHHW`.
Attach the reaction set to gas-phase `RPLUG` blocks, preferably with
`TYPE=ADIABATIC`, `PHASE=V`, `CAT-PRESENT=YES`, and explicitly entered catalyst
properties.

For the Li paper, set the LHHW denominator as three adsorption terms:

- Term 1: constant `1`
- Term 2: ethylbenzene adsorption, exponent on EB = 1
- Term 3: styrene adsorption, exponent on ST = 1
- `ADSORP-POW` exponent = 2 for all five reactions

Use `PRES-UNIT="N/SQM"` and `RATE-UNITC="KMOL/KG-S"` to make pressure and
catalyst-mass units explicit. Convert literature pre-exponential factors from
`mol/(g-cat h kPa^m)` to Aspen `kmol/(kg-cat s Pa^m)` as:

`k_Aspen = k_lit / 3600 / 1000^m`

because `1 mol/g = 1 kmol/kg` and `1 kPa = 1000 Pa`.

For the Li table values this gives:

- `k1`: `4.880555556`, `E1 = 152.7 kJ/mol`, `m = 1`
- `k2`: `2.323888889`, `E2 = 181.5 kJ/mol`, `m = 1`
- `k3`: `2.666666667`, `E3 = 177.4 kJ/mol`, `m = 1`
- `k4`: `0.002527777778`, `E4 = 185.3 kJ/mol`, `m = 2`
- `k5`: `0.00125`, `E5 = 189.7 kJ/mol`, `m = 2`

Adsorption constants use the paper's `bj = bj0 exp(-Aj/(R*T))` with `p` in
kPa. For Aspen Pa basis and `ADSORP-EQTER` in the form `exp(A + B/T)`, use:

- EB: `A = ln(1.830e-7/1000) = -22.421535`, `B = 82540/8.314 = 9927.8326`
- ST: `A = ln(1.660e-5/1000) = -17.913863`, `B = 79030/8.314 = 9505.6531`

The Li paper references `Keq` in the rate law and terms list but does not
provide a visible `Keq(T)` expression in the parsed/inspected pages. In the
2026-08-19 case, the Aspen template's existing reversible driving-force value
`DFORCE-EQ-2 A=-27.2319 B=15014.5` was retained as a documented template
assumption. Do not claim this pair came from the Li paper unless a source is
found and cited.

## RPlug Industrial Validation Setup

For the user's requested simple validation, use two adiabatic `RPLUG` blocks in
series rather than the paper's industrial radial-reactor model.

2026-08-19 baseline assumptions:

- First reactor inlet temperature: `619 C`
- Second reactor inlet temperature: `622 C`
- First reactor inlet pressure: `47 kPa(abs)`
- Second reactor outlet pressure: `38 kPa(abs)`
- EB feed: `16.02 t/h`
- Water feed: `18.46 t/h`
- LHSV: `0.4 h^-1`
- Bed voidage: `0.25`
- Catalyst/particle density: `1866 kg/m3`
- Existing template components: `C8H10`, `C8H8`, `H2`, `H2O`, `CH4`, `C6H6`,
  `C6H5CH3`, `C2H4`

The V14 template used `C8H10` for ethylbenzene and `C8H8` for styrene. Do not
rename component IDs unless all reaction, property, and stream references are
updated together.

In the 2026-08-19 simple RPlug case, `fEB=16.02 t/h` with the template
aromatic impurities (`0.9985 EB`, `0.001 benzene`, `0.0005 toluene`) became
about `150.94 kmol/h` total aromatic feed. The water feed became about
`1024.69 kmol/h`.

Size the RPlug from LHSV and catalyst bed assumptions rather than copying a
random tube count. The run used 25 mm tubes, 16 m length, and two equal beds.
With an EB liquid density assumption near `867 kg/m3`, total bed volume is
about `46.19 m3`, so each reactor bed is about `23.10 m3`; with bed voidage
`0.25`, the per-reactor tube count is about `2941`.

For this low-pressure vapor reactor, pressure treatment should follow the
literature pressures. Do not impose the ordinary positive-pressure exchanger
starting drop of `0.2 bar` here; the whole reactor pressure level is only
`0.47 -> 0.38 bar(abs)`.

## Validation Method

Run Aspen from a clean scratch directory. V14 may create temporary files and
may rewrite same-folder `.bkp` files when opening `.inp`; keep deliverables in
a separate folder and copy files into scratch for validation.

Before reporting:

1. Open with `InitFromFile2(path, True)`.
2. Check `Tree.FindNode(r"\Data").NextIncomplete("")`.
3. Run synchronously with `Run2(False)`.
4. Copy the newest `.his` while Aspen is still open if the files are temporary.
5. Inspect `.his` for `SEVERE`, `ERROR`, `WARNING`, and messages such as
   `SIMULATION PROGRAM CANNOT BE EXECUTED`.
6. Read component flows from
   `\Data\Streams\<sid>\Output\MOLEFLOW\MIXED\<component>`.
7. Save `.apwz`, export `.inp`, then validate the saved `.apwz` from a separate
   scratch copy.

Avoid carrying over unrelated property-analysis tables from GUI examples. In
the 2026-08-19 run, exported `PROP-TABLE BINRY-* FLASHCURVE` sections caused
input translation errors (`NO PROPERTIES ARE SPECIFIED FOR THIS TABLE`) and had
to be removed because they were unrelated to kinetic validation.

Compute validation metrics as:

- `X_EB = (F_EB,in - F_EB,out) / F_EB,in * 100`
- `S_ST = (F_ST,out - F_ST,in) / (F_EB,in - F_EB,out) * 100`

The 2026-08-19 baseline two-RPlug result was:

- `X1_EB = 37.93%` vs plant `40.18%`
- `S1_ST = 97.28%` vs plant `96.75%`
- `X2_EB = 63.88%` vs plant `65.53%`
- `S2_ST = 96.35%` vs plant `95.67%`

This result was close enough for a simple RPlug reproduction but not identical
to the paper's radial industrial model. State this simplification explicitly.

For a quick sensitivity check, vary one literature variable at a time, such as
first-stage inlet temperature across `530-620 C`, while keeping the other
baseline settings fixed. Export the sweep to CSV with conversion/selectivity
columns.
