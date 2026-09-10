# Reactor + Flash + Distillation Example

Complete flowsheet: RStoic conversion reactor, Flash2 hydrogen knockout, RadFrac distillation with a 99.9% styrene purity design spec.

```text
TITLE 'Ethylbenzene Dehydrogenation with Styrene Distillation'

IN-UNITS SI TEMP=C PRES=BAR MOLE-FLOW='KMOL/HR' MASS-FLOW='KG/HR' ENTHALPY-FLO='WATT'
OUT-UNITS SI TEMP=C PRES=BAR MOLE-FLOW='KMOL/HR' MASS-FLOW='KG/HR' ENTHALPY-FLO='WATT'

DEF-STREAMS CONVEN ALL

COMPONENTS
    EB ETHYLBENZENE /
    STY STYRENE /
    H2 HYDROGEN

PROPERTIES PENG-ROB

FLOWSHEET
    BLOCK R1 IN=FEED OUT=RXOUT
    BLOCK FL1 IN=RXOUT OUT=VAP LIQ
    BLOCK C1 IN=LIQ OUT=EB-VAP STY-PROD

STREAM FEED
    SUBSTREAM MIXED TEMP=650.0 PRES=0.4 MOLE-FLOW=100.0
    MOLE-FRAC EB 1.0

BLOCK R1 RSTOIC
    PARAM TEMP=650.0 PRES=0.4
    STOIC 1 MIXED EB -1.0 / STY 1.0 / H2 1.0
    CONV 1 MIXED EB 0.65

BLOCK FL1 FLASH2
    PARAM TEMP=40.0 PRES=0.4

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

## RadFrac Sentence Summary

- `PARAM NSTAGE=60 ALGORITHM=STANDARD MAXOL=100`: stage count and convergence control.
- `COL-CONFIG CONDENSER=PARTIAL-V`: partial-vapor condenser so H2 leaves as vapor.
- `FEEDS LIQ 30`: feed stream and stage number.
- `PRODUCTS EB-VAP 1 V / STY-PROD 60 L`: vapor distillate at stage 1, liquid bottoms at stage 60.
- `P-SPEC 1 0.4`: stage 1 pressure in bar.
- `COL-SPECS MOLE-B=62.0 MOLE-RR=15.0`: initial bottoms rate and reflux ratio.
- `SPEC 1 MOLE-FRAC 0.999 COMPS=STY STREAMS=STY-PROD`: purity design spec.
- `VARY 1 MOLE-B 60.0 63.0`: vary bottoms rate to meet the spec.

Keep `MOLE-B` in `COL-SPECS` as the initial guess even when `VARY` varies it; omitting it can make the `.inp` fail input translation.

## Expected Results

- FEED: 100 kmol/hr EB at 650 C, 0.4 bar
- RXOUT: 35 EB, 65 STY, 65 H2 kmol/hr
- Flash at 40 C, 0.4 bar: VAP carries ~65 H2 and small EB/STY; LIQ carries ~62.5 STY and ~33.1 EB
- EB-VAP: ~33.2 kmol/hr, mostly EB
- STY-PROD: ~62.4 kmol/hr, styrene purity ~99.9%

Use `\Data\Streams\STY-PROD\Output\MOLEFLOW\MIXED\STY` divided by `RES_MOLEFLOW` to verify purity.

## Related Script

`scripts/build_styrene_column.py` writes this input, runs it, prints stream results and purity, exports a `.rep`, saves a `.apwz`, and reopens the case in a visible Aspen Plus window.
