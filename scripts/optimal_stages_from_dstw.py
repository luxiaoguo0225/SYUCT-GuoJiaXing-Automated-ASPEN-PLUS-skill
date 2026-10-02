"""Find the DSTWU optimum from the minimum of NSTAGE * RR.

The method expected by the tutorial:
  1. Run Aspen DSTWU with PLOT=YES and OPT-NTRR=RR to obtain an NSTAGE-RR table.
  2. Compute NSTAGE * RR.
  3. Plot NSTAGE * RR versus NSTAGE.
  4. The minimum point gives the recommended theoretical-stage count. Read the
     corresponding RR from the same row.

The script accepts an Aspen .bkp containing DSET BLOCK DSTWU ... RR_TABLE or a
CSV with NSTAGE and RR columns.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import matplotlib.pyplot as plt

SCI = re.compile(r"[-+]?\d\.\d+D[+-]\d+")


def parse_bkp(path: Path) -> list[dict[str, float]]:
    lines = path.read_text(encoding="latin1", errors="ignore").splitlines()
    istart = next(
        (i for i, line in enumerate(lines) if "(NSTAGE)" in line and "IDSET" in line),
        None,
    )
    if istart is None:
        raise ValueError("NSTAGE IDSET not found.")
    iend = next((i for i in range(istart + 1, len(lines)) if "IDSET" in lines[i]), None)
    if iend is None:
        raise ValueError("Could not find end of NSTAGE IDSET.")
    stage_block = " ".join(lines[istart:iend])
    match = re.search(r"\(NSTAGE\)\s*\(\s*(.*?)\)", stage_block, re.S)
    if not match:
        raise ValueError("Could not parse NSTAGE values.")
    stages = [int(value) for value in re.findall(r"\d+", match.group(1))]

    rstart = next(
        (i for i, line in enumerate(lines) if "DSET BLOCK DSTWU" in line and "RR_TABLE" in line),
        None,
    )
    if rstart is None:
        raise ValueError("DSTWU RR_TABLE not found.")
    rend = next(
        (
            i
            for i in range(rstart + 1, len(lines))
            if lines[i].strip().startswith(("IDSET", "DSET"))
        ),
        None,
    )
    if rend is None:
        raise ValueError("Could not find end of RR_TABLE.")
    rr_text = " ".join(lines[rstart:rend])
    reflux = [float(value.replace("D", "E")) for value in SCI.findall(rr_text)]
    count = min(len(stages), len(reflux))
    return [{"NSTAGE": stages[i], "RR": reflux[i]} for i in range(count)]


def parse_csv(path: Path) -> list[dict[str, float]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = {name.upper(): name for name in (reader.fieldnames or [])}
        n_key = fields.get("NSTAGE") or fields.get("N")
        r_key = fields.get("RR") or fields.get("REFLUX_RATIO")
        if n_key is None or r_key is None:
            raise ValueError("CSV needs NSTAGE and RR columns.")
        return [
            {"NSTAGE": int(round(float(row[n_key]))), "RR": float(row[r_key])}
            for row in reader
        ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--bkp", type=Path)
    source.add_argument("--csv", type=Path)
    parser.add_argument("--outdir", type=Path, default=Path("outputs/dstw_optimum"))
    parser.add_argument("--prefix", default="dstw_NxRR_optimum")
    args = parser.parse_args(argv)

    rows = parse_bkp(args.bkp) if args.bkp else parse_csv(args.csv)
    rows.sort(key=lambda row: row["NSTAGE"])
    enriched = [
        {
            "NSTAGE": row["NSTAGE"],
            "RR": row["RR"],
            "NxRR": row["NSTAGE"] * row["RR"],
        }
        for row in rows
    ]
    optimum = min(enriched, key=lambda row: row["NxRR"])

    args.outdir.mkdir(parents=True, exist_ok=True)
    csv_path = args.outdir / f"{args.prefix}.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["NSTAGE", "RR", "NxRR"])
        writer.writeheader()
        writer.writerows(enriched)

    result = {
        "criterion": "minimum NSTAGE * RR",
        "recommended_theoretical_stages": optimum["NSTAGE"],
        "reflux_ratio": optimum["RR"],
        "NxRR_minimum": optimum["NxRR"],
        "note": "Stage count is discrete; inspect the neighboring points and DSTWU feed-stage output.",
    }
    json_path = args.outdir / f"{args.prefix}.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=200)
    ax.plot(
        [row["NSTAGE"] for row in enriched],
        [row["NxRR"] for row in enriched],
        "o-",
        linewidth=2,
        color="#1f4e79",
    )
    ax.scatter(
        [optimum["NSTAGE"]],
        [optimum["NxRR"]],
        s=70,
        color="#d62728",
        zorder=5,
        label=f"minimum: N={optimum['NSTAGE']}",
    )
    ax.axvline(optimum["NSTAGE"], color="#d62728", linestyle="--", linewidth=1)
    ax.set_xlabel("Theoretical stages, N")
    ax.set_ylabel("N x RR")
    ax.set_title("DSTWU shortcut: N x RR versus N")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    png_path = args.outdir / f"{args.prefix}.png"
    fig.savefig(png_path)
    plt.close(fig)

    print(json.dumps(result, ensure_ascii=False))
    print(csv_path)
    print(json_path)
    print(png_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())