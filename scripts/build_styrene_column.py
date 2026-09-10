"""Build the styrene reactor + flash + distillation flowsheet in Aspen Plus."""

from __future__ import annotations

import os

import win32com.client


INPUT_TEXT = """TITLE 'Ethylbenzene Dehydrogenation with Styrene Distillation'

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
"""


def read(apwn, path):
    node = apwn.Tree.FindNode(path)
    return node.Value, node.UnitString


def component_flows(apwn, stream, comps=("EB", "STY", "H2")):
    result = {}
    for comp in comps:
        try:
            value, unit = read(
                apwn,
                rf"\Data\Streams\{stream}\Output\MOLEFLOW\MIXED\{comp}",
            )
            result[comp] = (value, unit)
        except Exception as exc:
            result[comp] = (None, str(exc))
    return result


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    inp = os.path.join(here, "styrene_column.inp")
    apwz = os.path.join(here, "styrene_column_result.apwz")
    rep = os.path.join(here, "styrene_column_result.rep")

    print("STEP 1: write input file with reactor + flash + RadFrac")
    with open(inp, "w", encoding="utf-8") as fh:
        fh.write(INPUT_TEXT)

    print("STEP 2: start Aspen Plus GUI (visible)")
    apwn = win32com.client.Dispatch("Apwn.Document")
    try:
        print("STEP 3: open flowsheet and build modules")
        apwn.InitFromFile2(inp, True)
        try:
            apwn.Visible = True
        except Exception as exc:
            print("  visible set failed:", exc)

        print("STEP 4: run simulation")
        apwn.Run2(False)
        print("  Run2 OK")

        print("STEP 5: read results")
        for stream in ("FEED", "RXOUT", "VAP", "LIQ", "EB-VAP", "STY-PROD"):
            try:
                temp, tunit = read(apwn, f"\\Data\\Streams\\{stream}\\Output\\RES_TEMP")
                pres, punit = read(apwn, f"\\Data\\Streams\\{stream}\\Output\\RES_PRES")
                flow, funit = read(apwn, f"\\Data\\Streams\\{stream}\\Output\\RES_MOLEFLOW")
                flows = component_flows(apwn, stream)
                print(f"\n  {stream}: T={temp} [{tunit}] P={pres} [{punit}] F={flow} [{funit}]")
                print("    comp flows:", flows)
            except Exception as exc:
                print(f"\n  {stream}: <{exc}>")

        try:
            total, _ = read(apwn, r"\Data\Streams\STY-PROD\Output\RES_MOLEFLOW")
            sty, _ = read(apwn, r"\Data\Streams\STY-PROD\Output\MOLEFLOW\MIXED\STY")
            print(f"\n  STY-PROD styrene purity: {sty / total:.4%}")
        except Exception as exc:
            print("\n  purity calculation failed:", exc)

        print("\nSTEP 6: export report and save case")
        apwn.Export(2, rep)
        print("  report:", rep)
        apwn.SaveAs2(apwz, True)
        print("  case:", apwz)
        print("\nSTEP 7: reopen case in a visible Aspen Plus window")
        try:
            os.startfile(apwz)
            print("  Aspen Plus opened:", apwz)
        except Exception as exc:
            print("  startfile failed:", exc)
    finally:
        try:
            apwn.Quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
