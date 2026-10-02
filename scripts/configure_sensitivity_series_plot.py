"""Create and persist an Aspen-native Sensitivity results curve.

Typical use:
  python configure_sensitivity_series_plot.py ^
    --bkp "Example7.3c-RadFrac.bkp" ^
    --sensitivity S-1 ^
    --out-apwz "Example7.3c-SensitivityPlot.apwz" ^
    --out-bkp "Example7.3c-SensitivityPlot.bkp"

The script sets Sensitivity Input\\SERIES=YES, runs the case, saves the .apwz,
exports a .bkp, and checks that the .apwz contains an Aspen Plot Wizard
Results Curve definition.  The actual X/Y/series selection still depends on
the Sensitivity block's Vary/Tabulate setup; this utility does not invent it.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

from aspen_plus_bridge import AspenPlus


def verify_native_plot(apwz: Path, output_name: str) -> bool:
    """Return True when the saved workbook contains an Aspen Results Curve."""
    try:
        with zipfile.ZipFile(apwz) as archive:
            payload = b"\n".join(
                archive.read(name)
                for name in archive.namelist()
                if name.lower().endswith((".apw", ".appdf"))
            )
    except Exception:
        return False
    return (
        b"ApwnPlotWizardScreenFactory" in payload
        and b'PlotID="Results Curve"' in payload
        and output_name.encode("ascii", "ignore") in payload
        and b"NSTAGE" in payload
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bkp", type=Path, required=True)
    parser.add_argument("--sensitivity", default="S-1")
    parser.add_argument("--output-name", default="QREB", help="Tabulated output name, e.g. QREB or RR")
    parser.add_argument("--out-apwz", type=Path, required=True)
    parser.add_argument("--out-bkp", type=Path, required=True)
    parser.add_argument(
        "--no-run",
        action="store_true",
        help="Set SERIES=YES and save without running the sensitivity.",
    )
    args = parser.parse_args(argv)

    args.out_apwz.parent.mkdir(parents=True, exist_ok=True)
    args.out_bkp.parent.mkdir(parents=True, exist_ok=True)

    app = AspenPlus().open(str(args.bkp))
    try:
        series_path = (
            rf"\Data\Model Analysis Tools\Sensitivity\{args.sensitivity}\Input\SERIES"
        )
        node = app.node(series_path)
        if node is None:
            raise RuntimeError(f"Sensitivity input node not found: {series_path}")
        node.Value = "YES"
        print(f"{args.sensitivity}: SERIES=YES")
        if not args.no_run:
            app.run(False)
            print("Run2 completed")
        app.save_as(str(args.out_apwz))
        app.app.Export(1, str(args.out_bkp))
        print(f"Saved: {args.out_apwz}")
        print(f"Exported: {args.out_bkp}")
    finally:
        app.close()

    ok = verify_native_plot(args.out_apwz, args.output_name)
    print(f"Native Aspen Results Curve present: {ok}")
    if not ok:
        print(
            "WARNING: the workbook was saved, but the native plot definition was "
            "not detected. Open Sensitivity Results and use Plot Wizard, then save "
            "the .apwz again.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
