#!/usr/bin/env python3
"""Read-only audit of observed Aspen V14 PFS text; never certifies visual quality."""
import argparse
import hashlib
import itertools
import json
import math
import re
import shlex
from pathlib import Path

NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?"
POINT = re.compile(rf"^(\S+) (\S+) ({NUM}) ({NUM}) 0\s*$")
RECORD = re.compile(r"(?m)^(BLOCK|STREAM|ANNOTATION|TEXT|TABLE|LEGEND)\s*$")


def graphics_span(data, allow_graphics_only=False):
    start = data.find(b"GRAPHICS_BACKUP")
    if start < 0:
        return None
    ends = [data.find(marker, start) for marker in (b"$_SUMMARY_FILE", b"$_ADS_FILE")]
    ends = [v for v in ends if v >= 0]
    if not ends:
        if allow_graphics_only and start == 0 and b"PFSVData" in data:
            return None
        raise ValueError("GRAPHICS_BACKUP has no known end marker; refusing to guess")
    return start, min(ends)


def pair(line, prefix):
    match = re.match(rf"^{re.escape(prefix)} ({NUM}) ({NUM})(?:\s|$)", line)
    return [float(v) for v in match.groups()] if match else None


def connections(text):
    """Only the observed encoded BKP syntax; no proximity inference."""
    result = {}
    pattern = r'BLOCK\s+BLKID\s*=\s*("[^"]+"|[\w-]+).*?\bIN\s*=\s*\((.*?)\)\s*OUT\s*=\s*\((.*?)\)'
    for block, ins, outs in re.findall(pattern, text, re.S):
        for side, names in ((1, ins), (0, outs)):
            tokens = shlex.split(names)
            if len(tokens) % 2:
                raise ValueError(f"Unrecognized stream/type pairs at {block}")
            for stream in tokens[::2]:
                result.setdefault(stream, [None, None])[side] = block.strip('"')
    return result


def audit(path, tolerance=1e-5, near_distance=0.22, approach_length=2.0):
    data = Path(path).read_bytes()
    span = graphics_span(data, allow_graphics_only=Path(path).name.endswith('.pfs.txt'))
    raw = data[slice(*span)] if span else data
    text = raw.decode("latin1").replace("\r\n", "\n").replace("\r", "\n")
    pos = text.find("PFSVData")
    if pos < 0:
        raise ValueError("No PFSVData marker; this parser does not support .inp PFS")
    text = text[pos:]
    starts = list(RECORD.finditer(text))
    blocks, streams, warnings = {}, {}, []
    others = []
    for index, match in enumerate(starts):
        kind = match.group(1)
        body = text[match.end():starts[index + 1].start() if index + 1 < len(starts) else len(text)]
        ident = re.search(r"(?m)^ID:\s*(.+)$", body)
        if kind not in ("BLOCK", "STREAM"):
            others.append({"kind": kind, "id": ident.group(1).strip() if ident else None})
            continue
        if not ident:
            warnings.append(f"{kind} without ID")
            continue
        name = ident.group(1).strip()
        fields = {"at": [], "label_at": [], "routes": []}
        route = None
        for line in body.splitlines():
            line = line.strip()
            if line.startswith("At "):
                fields["at"].append(pair(line, "At"))
            elif line.startswith("Label At "):
                fields["label_at"].append(pair(line, "Label At"))
            elif line.startswith("Scale "):
                fields["scale_modifier"] = line
            elif line.startswith("ICON:"):
                fields["icon"] = line
            elif line.startswith(("GLOBAL ", "TYPE ")):
                fields.setdefault("display_config", []).append(line)
            elif line.startswith("ROUTE "):
                pieces = line.split()
                if len(pieces) != 3:
                    warnings.append(f"Unrecognized route header {name}: {line}")
                    route = None
                    continue
                route = {"end": pieces[1], "page": pieces[2], "points": [], "displacements": []}
                fields["routes"].append(route)
            elif route is not None:
                point = POINT.fullmatch(line)
                if point:
                    code1, code2, x, y = point.groups()
                    route["points"].append({"codes": [code1, code2], "xy": [float(x), float(y)]})
                elif line.startswith("$ D "):
                    route["displacements"].append(pair(line, "$ D"))
                elif re.match(r"^[rxytlud]\s", line):
                    warnings.append(f"Unparsed coordinate at {name}: {line}")
        target = blocks if kind == "BLOCK" else streams
        if name in target:
            warnings.append(f"Duplicate {kind} ID {name}; occurrences retained")
        target.setdefault(name, []).append(fields)
        if len(fields["at"]) > 1 or len({r["page"] for r in fields["routes"]}) > 1:
            warnings.append(f"Multiple anchors/pages at {name}; inspect each page")
    conn = connections(data[:span[0]].decode("latin1")) if span else {}
    if not conn:
        warnings.append("No supported physical connectivity: same-block endpoint checks unavailable")
    diagonals, endpoints = [], {}
    for name, occurrences in streams.items():
        for occurrence, fields in enumerate(occurrences):
            for route in fields["routes"]:
                points = route["points"]
                for a, b in zip(points, points[1:]):
                    if all(abs(u - v) > tolerance for u, v in zip(a["xy"], b["xy"])):
                        diagonals.append({"stream": name, "page": route["page"], "a": a["xy"], "b": b["xy"]})
                if not points or route["end"] not in ("0", "1"):
                    continue
                terminal = points[-1]
                end = int(route["end"])
                block = conn.get(name, [None, None])[end]
                if block and terminal["codes"][0] == "t":
                    endpoints.setdefault((block, end, route["page"]), []).append({
                        "stream": name, "occurrence": occurrence, "xy": terminal["xy"],
                        "displacements": route["displacements"],
                        "path_from_endpoint": [p["xy"] for p in reversed(points)],
                    })
    near, overlaps = [], []
    for (block, end, page), ports in endpoints.items():
        for a, b in itertools.combinations(ports, 2):
            if a["stream"] == b["stream"]:
                continue
            distance = math.dist(a["xy"], b["xy"])
            record = {"block": block, "end": end, "page": page,
                      "streams": [a["stream"], b["stream"]], "distance": distance}
            if distance < near_distance:
                near.append(record)
            lengths = [collinear_overlap(p, q, r, s, tolerance)
                       for p, q in clipped_segments(a["path_from_endpoint"], approach_length)
                       for r, s in clipped_segments(b["path_from_endpoint"], approach_length)]
            if lengths and max(lengths) > tolerance:
                overlaps.append({**record, "max_pair_overlap": max(lengths)})
    declared = re.search(r"# of PFS Objects\s*=\s*(\d+)", text)
    counts = {"blocks": sum(map(len, blocks.values())), "streams": sum(map(len, streams.values()))}
    if declared and int(declared.group(1)) != sum(counts.values()):
        warnings.append("Declared PFS objects differ from block+stream records; preserve other objects/header")
    return {
        "source": str(Path(path).resolve()), "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data), "counts": counts,
        "declared_pfs_objects": int(declared.group(1)) if declared else None,
        "blocks": blocks, "streams": streams, "other_records": others,
        "connections": conn, "diagonal_segments": diagonals,
        "near_same_block_endpoints": near, "shared_approach_segments": overlaps,
        "thresholds_graphic_units": {"tolerance": tolerance, "near_distance": near_distance, "approach_length": approach_length},
        "warnings": warnings,
        "limits": ["Stored coordinates only; no Aspen GUI or visual acceptance",
                   "Stored terminal includes any observed displacement; no automatic extra offset",
                   "Factory default labels, icon bounds and text occlusion are unknown",
                   "Physical connectivity supports observed encoded BKP syntax only"],
    }


def clipped_segments(points, length):
    for a, b in zip(points, points[1:]):
        distance = math.dist(a, b)
        if distance == 0:
            continue
        remaining = min(length, distance)
        end = [u + (v - u) * remaining / distance for u, v in zip(a, b)]
        yield a, end
        length -= remaining
        if length <= 0:
            return


def collinear_overlap(a, b, c, d, tolerance):
    for fixed, varying in ((0, 1), (1, 0)):
        if (abs(a[fixed] - b[fixed]) <= tolerance and abs(c[fixed] - d[fixed]) <= tolerance
                and abs(a[fixed] - c[fixed]) <= tolerance):
            return max(0, min(max(a[varying], b[varying]), max(c[varying], d[varying]))
                       - max(min(a[varying], b[varying]), min(c[varying], d[varying])))
    return 0


def compare(path_a, path_b, a, b):
    result = {}
    for category in ("blocks", "streams"):
        before, after = a[category], b[category]
        result[category] = {"added": sorted(after.keys() - before.keys()),
                            "removed": sorted(before.keys() - after.keys()), "changed": {}}
        for name in before.keys() & after.keys():
            if before[name] != after[name]:
                result[category]["changed"][name] = {"before": before[name], "after": after[name]}
    raw_a, raw_b = Path(path_a).read_bytes(), Path(path_b).read_bytes()
    span_a = graphics_span(raw_a, allow_graphics_only=Path(path_a).name.endswith('.pfs.txt'))
    span_b = graphics_span(raw_b, allow_graphics_only=Path(path_b).name.endswith('.pfs.txt'))
    result["outside_graphics_byte_equal"] = None
    if span_a and span_b:
        result["outside_graphics_byte_equal"] = (
            raw_a[:span_a[0]] == raw_b[:span_b[0]] and raw_a[span_a[1]:] == raw_b[span_b[1]:])
    result["physical_connections_equal"] = a["connections"] == b["connections"] if a["connections"] and b["connections"] else None
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--compare", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--tolerance", type=float, default=1e-5)
    parser.add_argument("--near-distance", type=float, default=0.22)
    parser.add_argument("--approach-length", type=float, default=2.0)
    args = parser.parse_args()
    if min(args.tolerance, args.near_distance, args.approach_length) <= 0:
        parser.error("Thresholds must be positive")
    if args.output and args.output.resolve() in {p.resolve() for p in (args.source, args.compare) if p}:
        parser.error("Output must not overwrite an input")
    result = audit(args.source, args.tolerance, args.near_distance, args.approach_length)
    if args.compare:
        other = audit(args.compare, args.tolerance, args.near_distance, args.approach_length)
        result["comparison"] = compare(args.source, args.compare, result, other)
    serialized = json.dumps(result, ensure_ascii=True, indent=2)
    if args.output:
        args.output.write_text(serialized + "\n", encoding="utf-8")
        print(json.dumps({"counts": result["counts"], "diagonals": len(result["diagonal_segments"]),
                          "near_endpoints": len(result["near_same_block_endpoints"]),
                          "shared_approaches": len(result["shared_approach_segments"]),
                          "warning_count": len(result["warnings"]),
                          "warning_examples": result["warnings"][:3],
                          "output": str(args.output)}, ensure_ascii=True))
    else:
        print(serialized)


if __name__ == "__main__":
    main()
