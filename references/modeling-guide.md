# Aspen Plus Modeling Guide

## Stream Inputs

Define conventional material streams with the MIXED substream:

```text
DEF-STREAMS CONVEN ALL

STREAM FEED
    SUBSTREAM MIXED TEMP=650.0 PRES=0.4 MOLE-FLOW=100.0
    MOLE-FRAC EB 1.0
```

Composition can use `MOLE-FRAC`, `MASS-FRAC`, `MOLE-FLOW`, or `MASS-FLOW` followed by component/value pairs separated by `/`.

COM paths for a material stream:

```text
\Data\Streams\<name>\Input\TEMP\MIXED
\Data\Streams\<name>\Input\PRES\MIXED
\Data\Streams\<name>\Input\TOTFLOW
\Data\Streams\<name>\Input\FLOW\MIXED\<component>
\Data\Streams\<name>\Output\RES_TEMP
\Data\Streams\<name>\Output\RES_PRES
\Data\Streams\<name>\Output\RES_MOLEFLOW
\Data\Streams\<name>\Output\RES_MASSFLOW
\Data\Streams\<name>\Output\MOLEFLOW\MIXED\<component>
```

Write scalar leaves such as `Input\TEMP\MIXED`; writing `Input\TEMP` can raise `AE_UNDERSPEC`.

Always set explicit input/output units to avoid K/N-sqm/kmol-s surprises:

```text
IN-UNITS SI TEMP=C PRES=BAR MOLE-FLOW='KMOL/HR' MASS-FLOW='KG/HR' ENTHALPY-FLO='WATT'
OUT-UNITS SI TEMP=C PRES=BAR MOLE-FLOW='KMOL/HR' MASS-FLOW='KG/HR' ENTHALPY-FLO='WATT'
```

## Property Methods

Set the global method with `PROPERTIES <METHOD>` in an input file, or via:

```text
\Data\Properties\Specifications\Input\GBASEOPSET
```

Common methods and when to use them:

| Method | Typical use |
| --- | --- |
| `PENG-ROB` | Hydrocarbons, gas processing, high pressure (PR) |
| `RK-SOAVE` | Hydrocarbons and gases, SRK |
| `NRTL` | Polar, nonideal liquid mixtures, VLE/LLE |
| `UNIQUAC` | Polar, nonideal mixtures, VLE/LLE |
| `WILSON` | Strongly nonideal liquids, VLE |
| `ELECNRTL` | Electrolyte systems |
| `IDEAL` | Ideal gas/ideal solution approximations |
| `CHAO-SEA`, `BK10` | Petroleum and refinery-oriented methods |

After changing components or the global method, run the engine once so Aspen Plus refreshes binary interaction parameters (BIPs).

## Module Selection

Select blocks by the physics of the problem, then use the palette model name as the COM type string.

| Task | Block |
| --- | --- |
| Stoichiometric/conversion reactor | `RStoic` (add `STOIC` + `CONV` sentences) |
| Known product yields | `RYield` |
| Single-reaction equilibrium | `REquil` |
| Multi-reaction equilibrium, no stoich needed | `RGibbs` |
| Kinetics, stirred tank | `RCSTR` |
| Kinetics, plug flow | `RPlug` |
| Heater/cooler | `Heater` |
| Two-outlet flash | `Flash2` |
| Three-outlet flash | `Flash3` |
| Combine streams | `Mixer` |
| Split flow | `FSplit` |
| Pressure change | `Pump`, `Compr`, `Valve` |
| Heat exchange | `HeatX` |
| Shortcut distillation | `DSTWU` |
| Rigorous distillation | `Radfrac` |

### Placement and Connection

Create blocks and streams from the COM data tree:

```python
streams = tree.FindNode(r"\Data\Streams")
blocks = tree.FindNode(r"\Data\Blocks")
streams.Elements.Add("FEED!MATERIAL")
blocks.Elements.Add("R1!RStoic")
```

Connect a stream to a block port:

```python
block = blocks.Elements.Item("R1")
port = block.Elements.Item("Ports").Elements.Item("F(IN)")
port.Elements.Add("FEED")
```

Common ports: `F(IN)`, `P(OUT)`, `D(OUT)`, `B(OUT)`, `V(OUT)`, `L(OUT)`, `HS(IN)`, `HS(OUT)`.

In an input file, connectivity and block data are text sentences:

```text
FLOWSHEET
    BLOCK R1 IN=FEED OUT=PRODUCT

BLOCK R1 RSTOIC
    PARAM TEMP=650.0 PRES=0.4
    STOIC 1 MIXED EB -1.0 / STY 1.0 / H2 1.0
    CONV 1 MIXED EB 0.65
```
