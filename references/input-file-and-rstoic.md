# Building New Cases from Input Files

## Unit Overrides

Aspen Plus unit sets do not always match the units you want. Use explicit overrides:

```text
IN-UNITS SI TEMP=C PRES=BAR MOLE-FLOW='KMOL/HR' MASS-FLOW='KG/HR' ENTHALPY-FLO='WATT'
OUT-UNITS SI TEMP=C PRES=BAR MOLE-FLOW='KMOL/HR' MASS-FLOW='KG/HR' ENTHALPY-FLO='WATT'
```

Without these, `IN-UNITS SI` interprets temperature as K, pressure as N/sqm, and molar flow as kmol/s.

## RStoic Conversion Reactor

The conversion reactor is `RSTOIC`. Define stoichiometry and fractional conversion inside the block:

```text
BLOCK R1 RSTOIC
    PARAM TEMP=650.0 PRES=0.4
    STOIC 1 MIXED EB -1.0 / STY 1.0 / H2 1.0
    CONV 1 MIXED EB 0.65
```

`CONV` row label is the reaction number; `MIXED` is the substream; the component after `MIXED` is the basis component for conversion.

## Complete Example

Ethylbenzene dehydrogenation, 100 kmol/hr pure EB feed at 650 C and 0.4 bar, PR property method, 65% conversion:

```text
TITLE 'Ethylbenzene Dehydrogenation to Styrene'

IN-UNITS SI TEMP=C PRES=BAR MOLE-FLOW='KMOL/HR' MASS-FLOW='KG/HR' ENTHALPY-FLO='WATT'
OUT-UNITS SI TEMP=C PRES=BAR MOLE-FLOW='KMOL/HR' MASS-FLOW='KG/HR' ENTHALPY-FLO='WATT'

DEF-STREAMS CONVEN ALL

COMPONENTS
    EB ETHYLBENZENE /
    STY STYRENE /
    H2 HYDROGEN

PROPERTIES PENG-ROB

FLOWSHEET
    BLOCK R1 IN=FEED OUT=PRODUCT

STREAM FEED
    SUBSTREAM MIXED TEMP=650.0 PRES=0.4 MOLE-FLOW=100.0
    MOLE-FRAC EB 1.0

BLOCK R1 RSTOIC
    PARAM TEMP=650.0 PRES=0.4
    STOIC 1 MIXED EB -1.0 / STY 1.0 / H2 1.0
    CONV 1 MIXED EB 0.65
```

Expected results: PRODUCT has 35 kmol/hr EB, 65 kmol/hr STY, 65 kmol/hr H2, 165 kmol/hr total.

## Reading Results

- Totals: `\Data\Streams\<name>\Output\RES_TEMP`, `RES_PRES`, `RES_MOLEFLOW`, `RES_MASSFLOW`
- Component flows: `\Data\Streams\<name>\Output\MOLEFLOW\MIXED\<component>`
- Export a full report with `apwn.Export(2, "result.rep")`

A saved `.apwz` may not expose component-level output through the COM tree until the case is run again; export the report immediately after `Run2` when results are needed.
