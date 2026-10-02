"""Plot QREB versus feed stage for several RadFrac stage counts.

This utility supports the 2-D Aspen Sensitivity pattern used by Sun Lanyi's
Example 7.3c:

    Vary 1: RadFrac NSTAGE      62 ... 80 step 2
    Vary 2: RadFrac FEED-STAGE  20 ... 38 step 2
    Tabulate: RadFrac REB-DUTY (kW)

It either parses the Aspen backup's SNS_TAB results or accepts a long CSV with
columns NSTAGE, FEED_STAGE, QREB_kW.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

SCI = re.compile(r"[-+]?\d\.\d+D[+-]\d+")


def _parse_d(value: str) -> float:
    return float(value.replace("D", "E"))


def parse_bkp(path: Path) -> list[dict[str, float]]:
    text = path.read_text(encoding="latin1", errors="ignore")
    lines = text.splitlines()
    start = next(
        (i for i, line in enumerate(lines) if "DSET SENSITIVITY" in line and "SNS_TAB" in line),
        None,
    )
    if start is None:
        raise ValueError("No DSET SENSITIVITY ... SNS_TAB block found.")
    end = next(
        (
            j
            for j in range(start + 1, len(lines))
            if "DSET SENSITIVITY" in lines[j] and "BLKSTAT" in lines[j]
        ),
        None,
    )
    if end is None:
        raise ValueError("Could not find the end of the SNS_TAB block.")
    chunk = " ".join(lines[start:end])

    try:
        vary1 = chunk.split('"VARY   1"', 1)[1].split('"VARY   2"', 1)[0]
        after_vary2 = chunk.split('"VARY   2"', 1)[1]
        vary2, output = after_vary2.split('"QREB    "', 1)
    except IndexError as exc:
        raise ValueError(
            "This parser expects VARY 1, VARY 2 and QREB in the SNS_TAB dataset."
        ) from exc

    values1 = SCI.findall(vary1)
    values2 = SCI.findall(vary2)
    q_values = SCI.findall(output)
    counts = (len(values1), len(values2), len(q_values))
    # Aspen appends the current/base-case value when all lists are equal length.
    n_grid = counts[0] - 1 if len(set(counts)) == 1 else max(0, min(counts))
    return [
        {
            "NSTAGE": int(round(_parse_d(values1[i]))),
            "FEED_STAGE": int(round(_parse_d(values2[i]))),
            "QREB_kW": _parse_d(q_values[i]),
        }
        for i in range(n_grid)
    ]


def parse_csv(path: Path) -> list[dict[str, float]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = {name.upper(): name for name in (reader.fieldnames or [])}

        def pick(*names: str) -> str:
            for name in names:
                if name.upper() in fieldnames:
                    return fieldnames[name.upper()]
            raise ValueError(f"CSV needs one of: {', '.join(names)}")

        n_key = pick("NSTAGE", "STAGES", "THEORETICAL_STAGES")
        f_key = pick("FEED_STAGE", "FEEDSTAGE", "FEED")
        q_key = pick("QREB_KW", "QREB", "REB_DUTY", "REB-DUTY")
        return [
            {
                "NSTAGE": int(round(float(row[n_key]))),
                "FEED_STAGE": int(round(float(row[f_key]))),
                "QREB_kW": float(row[q_key]),
            }
            for row in reader
        ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--bkp", type=Path, help="Aspen .bkp with SNS_TAB results")
    source.add_argument("--csv", type=Path, help="Long CSV with NSTAGE/FEED_STAGE/QREB")
    parser.add_argument("--outdir", type=Path, default=Path("outputs/feedstage_sensitivity"))
    parser.add_argument("--prefix", default="radfrac_feedstage_sensitivity")
    args = parser.parse_args(argv)

    rows = parse_bkp(args.bkp) if args.bkp else parse_csv(args.csv)
    rows.sort(key=lambda r: (r["NSTAGE"], r["FEED_STAGE"]))
    args.outdir.mkdir(parents=True, exist_ok=True)

    long_csv = args.outdir / f"{args.prefix}_long.csv"
    with long_csv.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["NSTAGE", "FEED_STAGE", "QREB_kW"])
        writer.writeheader()
        writer.writerows(rows)

    by_stage: dict[int, list[dict[str, float]]] = defaultdict(list)
    for row in rows:
        by_stage[row["NSTAGE"]].append(row)

    minima = []
    for nstage in sorted(by_stage):
        point = min(by_stage[nstage], key=lambda row: row["QREB_kW"])
        minima.append(point)
    minima_csv = args.outdir / f"{args.prefix}_minima.csv"
    with minima_csv.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["NSTAGE", "FEED_STAGE", "QREB_kW"])
        writer.writeheader()
        writer.writerows(minima)

    stages = sorted(by_stage)
    colors = plt.cm.viridis([i / max(1, len(stages) - 1) for i in range(len(stages))])
    fig, ax = plt.subplots(figsize=(9.4, 6.1), dpi=200)
    for color, nstage in zip(colors, stages):
        points = sorted(by_stage[nstage], key=lambda row: row["FEED_STAGE"])
        ax.plot(
            [row["FEED_STAGE"] for row in points],
            [row["QREB_kW"] for row in points],
            marker="o",
            markersize=3.5,
            linewidth=1.6,
            color=color,
            label=f"NSTAGE={nstage}",
        )
        point = min(points, key=lambda row: row["QREB_kW"])
        ax.scatter(
            [point["FEED_STAGE"]],
            [point["QREB_kW"]],
            s=28,
            color=color,
            edgecolors="black",
            linewidths=0.4,
            zorder=5,
        )
    ax.set_xlabel("Feed stage")
    ax.set_ylabel("Reboiler duty, QREB (kW)")
    ax.set_title("QREB versus feed stage for different theoretical-stage counts")
    ax.grid(alpha=0.25)
    ax.legend(ncol=2, fontsize=8, title="Theoretical stages")
    fig.tight_layout()
    png = args.outdir / f"{args.prefix}.png"
    fig.savefig(png)
    plt.close(fig)

    print(f"rows: {len(rows)}")
    print(f"long CSV: {long_csv}")
    print(f"minima CSV: {minima_csv}")
    print(f"plot: {png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())