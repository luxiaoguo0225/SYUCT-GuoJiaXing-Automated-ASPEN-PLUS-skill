"""Estimate minimum reflux ratio from a discrete NSTAGE -> RR asymptote.

Input can be:
  * an Aspen .bkp containing DSET SENSITIVITY ... SNS_TAB with one NSTAGE vary
    and an RR tabulation, or
  * a long CSV with columns NSTAGE, RR.

The default criterion is the first point where |delta RR| / RR_previous <= 0.1%.
The feed stage must be linked by the case itself (for Example 7.3d the Calculator
sets FSTAGE = 0.43*NSTAGE); this script does not invent that relation.
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
    start = next(
        (i for i, line in enumerate(lines) if "DSET SENSITIVITY" in line and "SNS_TAB" in line),
        None,
    )
    if start is None:
        raise ValueError("No SNS_TAB dataset found.")
    end = next(
        (
            j
            for j in range(start + 1, len(lines))
            if "DSET SENSITIVITY" in lines[j] and "BLKSTAT" in lines[j]
        ),
        None,
    )
    if end is None:
        raise ValueError("Could not find end of SNS_TAB dataset.")
    chunk = " ".join(lines[start:end])
    try:
        stage_part = chunk.split('"VARY   1"', 1)[1].split('"RR      "', 1)[0]
        rr_part = chunk.split('"RR      "', 1)[1]
    except IndexError as exc:
        raise ValueError("Expected a single VARY NSTAGE and tabulated RR.") from exc
    stages = [int(round(float(x.replace("D", "E")))) for x in SCI.findall(stage_part)]
    rrs = [float(x.replace("D", "E")) for x in SCI.findall(rr_part)]
    n = min(len(stages), len(rrs))
    if len(stages) == len(rrs) + 1:
        n = len(rrs)
    return [{"NSTAGE": stages[i], "RR": rrs[i]} for i in range(n)]


def parse_csv(path: Path) -> list[dict[str, float]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = {name.upper(): name for name in (reader.fieldnames or [])}
        n_key = next((fields[k] for k in ("NSTAGE", "STAGES") if k in fields), None)
        r_key = next((fields[k] for k in ("RR", "REFLUX_RATIO") if k in fields), None)
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
    parser.add_argument("--threshold-pct", type=float, default=0.1)
    parser.add_argument("--outdir", type=Path, default=Path("outputs/min_reflux"))
    parser.add_argument("--prefix", default="min_reflux_asymptote")
    args = parser.parse_args(argv)

    rows = parse_bkp(args.bkp) if args.bkp else parse_csv(args.csv)
    rows.sort(key=lambda row: row["NSTAGE"])
    enriched = []
    selected = None
    for i, row in enumerate(rows):
        if i == 0:
            delta = None
            rel = None
        else:
            delta = row["RR"] - rows[i - 1]["RR"]
            rel = abs(delta) / rows[i - 1]["RR"] * 100.0
            if selected is None and rel <= args.threshold_pct:
                selected = {"NSTAGE": row["NSTAGE"], "RR": row["RR"], "relative_change_pct": rel}
        enriched.append(
            {
                "NSTAGE": row["NSTAGE"],
                "RR": row["RR"],
                "delta_RR": delta,
                "relative_change_pct": rel,
            }
        )

    args.outdir.mkdir(parents=True, exist_ok=True)
    csv_path = args.outdir / f"{args.prefix}.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["NSTAGE", "RR", "delta_RR", "relative_change_pct"])
        writer.writeheader()
        writer.writerows(enriched)
    result = {
        "criterion": f"first |delta RR| / RR_previous <= {args.threshold_pct}%",
        "minimum_reflux_estimate": selected["RR"] if selected else rows[-1]["RR"],
        "at_NSTAGE": selected["NSTAGE"] if selected else rows[-1]["NSTAGE"],
        "relative_change_pct": selected["relative_change_pct"] if selected else None,
        "note": "Engineering asymptote estimate; expand NSTAGE if no point satisfies the threshold.",
    }
    json_path = args.outdir / f"{args.prefix}.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(7.4, 4.8), dpi=200)
    ax.plot([r["NSTAGE"] for r in enriched], [r["RR"] for r in enriched], "o-", lw=2)
    if selected:
        ax.axhline(selected["RR"], color="tab:red", ls="--")
        ax.scatter([selected["NSTAGE"]], [selected["RR"]], color="tab:red", zorder=5)
    ax.set_xlabel("NSTAGE")
    ax.set_ylabel("Reflux ratio, RR")
    ax.set_title("Reflux-ratio asymptote versus theoretical stages")
    ax.grid(alpha=0.25)
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