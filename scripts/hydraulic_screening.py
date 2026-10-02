#!/usr/bin/env python3
"""Preliminary hydraulic arithmetic for Aspen-derived equipment screening.

This script intentionally contains only transparent algebraic identities. It
does not implement vendor tray/packing correlations, pipe-network friction
factors, multiphase flow, water hammer, valve cavitation, or formal ratings.
All outputs are preliminary unless a separate source-bound or vendor check
closes the applicable evidence gate.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

G = 9.80665


class InputError(ValueError):
    pass


def number(value: Any, field: str, *, positive: bool = False,
           nonnegative: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{field} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise InputError(f"{field} must be finite")
    if positive and result <= 0.0:
        raise InputError(f"{field} must be > 0")
    if nonnegative and result < 0.0:
        raise InputError(f"{field} must be >= 0")
    return result


def optional_number(value: Any, field: str, *, positive: bool = False) -> float | None:
    if value is None:
        return None
    return number(value, field, positive=positive)


def fraction_sum(data: dict[str, Any], names: tuple[str, ...]) -> float:
    total = 0.0
    for name in names:
        value = number(data.get(name, 0.0), name, nonnegative=True)
        total += value
    if total >= 1.0:
        raise InputError("area fractions must sum to less than 1")
    return total


def tower_screen(data: dict[str, Any]) -> dict[str, Any]:
    q = number(data.get("vapor_volumetric_flow_m3_s"), "tower.vapor_volumetric_flow_m3_s", positive=True)
    design_u = number(data.get("design_velocity_m_s"), "tower.design_velocity_m_s", positive=True)
    basis = str(data.get("design_velocity_basis", "total_area"))
    if basis not in {"total_area", "active_area"}:
        raise InputError("tower.design_velocity_basis must be total_area or active_area")
    excluded = fraction_sum(data, (
        "downcomer_area_fraction",
        "receiving_area_fraction",
        "inactive_area_fraction",
        "other_unavailable_area_fraction",
    ))
    active_fraction = 1.0 - excluded
    if basis == "active_area":
        active_area = q / design_u
        total_area = active_area / active_fraction
    else:
        total_area = q / design_u
        active_area = total_area * active_fraction
    diameter = math.sqrt(4.0 * total_area / math.pi)
    total_velocity = q / total_area
    active_velocity = q / active_area
    result: dict[str, Any] = {
        "scope": "PRELIMINARY",
        "method": "area and velocity identities only",
        "design_velocity_basis": basis,
        "active_area_fraction": active_fraction,
        "total_cross_section_m2": total_area,
        "active_area_m2": active_area,
        "preliminary_inside_diameter_m": diameter,
        "superficial_velocity_total_area_m_s": total_velocity,
        "velocity_active_area_m_s": active_velocity,
        "formulas": [
            "A_total=A_active+A_downcomer+A_receiving+A_inactive+A_other",
            "Q=u*A",
            "D=sqrt(4*A_total/pi)",
        ],
        "does_not_prove": [
            "tray_or_packing_hydraulics",
            "flooding_capacity",
            "entrainment_pass",
            "weeping_pass",
            "final_internals_design",
        ],
    }
    density = optional_number(data.get("vapor_density_kg_m3"), "tower.vapor_density_kg_m3", positive=True)
    flood_factor = optional_number(data.get("flooding_f_factor_pa_0_5"), "tower.flooding_f_factor_pa_0_5", positive=True)
    if density is not None:
        result["f_factor_total_area_pa_0_5"] = total_velocity * math.sqrt(density)
        result["f_factor_active_area_pa_0_5"] = active_velocity * math.sqrt(density)
    if density is not None and flood_factor is not None:
        f_basis = str(data.get("f_factor_basis", basis))
        if f_basis not in {"total_area", "active_area"}:
            raise InputError("tower.f_factor_basis must be total_area or active_area")
        velocity = total_velocity if f_basis == "total_area" else active_velocity
        actual_f = velocity * math.sqrt(density)
        result["f_factor_basis"] = f_basis
        result["flood_fraction"] = actual_f / flood_factor
        result["flood_fraction_note"] = "Requires a source-bound F_flood for the same packing/tray, phase basis, pressure and geometry."
    return result


def pipe_screen(data: dict[str, Any]) -> dict[str, Any]:
    q = number(data.get("volumetric_flow_m3_s"), "pipe.volumetric_flow_m3_s", positive=True)
    target_u = number(data.get("target_velocity_m_s"), "pipe.target_velocity_m_s", positive=True)
    area = q / target_u
    required_d = math.sqrt(4.0 * area / math.pi)
    result: dict[str, Any] = {
        "scope": "PRELIMINARY",
        "method": "continuity only",
        "required_flow_area_m2": area,
        "required_inside_diameter_m": required_d,
        "formulas": ["A=Q/v", "D=sqrt(4*A/pi)"],
        "does_not_prove": [
            "total_pipe_pressure_drop",
            "fitting_and_valve_losses",
            "multiphase_flow",
            "water_hammer",
            "pipe_stress",
        ],
    }
    selected_d = optional_number(data.get("selected_inside_diameter_m"), "pipe.selected_inside_diameter_m", positive=True)
    if selected_d is not None:
        selected_area = math.pi * selected_d ** 2 / 4.0
        result["selected_inside_diameter_m"] = selected_d
        result["selected_flow_area_m2"] = selected_area
        result["actual_velocity_m_s"] = q / selected_area
    return result


def pump_screen(data: dict[str, Any]) -> dict[str, Any]:
    q = number(data.get("volumetric_flow_m3_s"), "pump.volumetric_flow_m3_s", positive=True)
    head = number(data.get("head_m"), "pump.head_m", positive=True)
    density = number(data.get("density_kg_m3"), "pump.density_kg_m3", positive=True)
    hydraulic_w = density * G * q * head
    result: dict[str, Any] = {
        "scope": "PRELIMINARY",
        "hydraulic_power_kw": hydraulic_w / 1000.0,
        "formulas": ["P_hydraulic=rho*g*Q*H"],
        "does_not_prove": [
            "vendor_duty_point",
            "maximum_pressure_drop",
            "cavitation_pass",
            "final_model",
        ],
    }
    efficiency = optional_number(data.get("pump_efficiency_fraction"), "pump.pump_efficiency_fraction", positive=True)
    if efficiency is not None:
        if efficiency > 1.0:
            raise InputError("pump.pump_efficiency_fraction must be <= 1")
        result["shaft_power_kw"] = hydraulic_w / efficiency / 1000.0
    npsha = optional_number(data.get("npsha_m"), "pump.npsha_m", positive=True)
    npshr = optional_number(data.get("npshr_m"), "pump.npshr_m", positive=True)
    if npsha is not None and npshr is not None:
        result["npsh_margin_m"] = npsha - npshr
        result["npsh_note"] = (
            "A positive arithmetic difference is not a pass. NPSHa and NPSHr "
            "must belong to the same duty and the margin must meet the project limit."
        )
    return result


def run(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise InputError("top-level JSON must be an object")
    out: dict[str, Any] = {
        "schema": "aspen-hydraulic-screening-v1",
        "scope": "PRELIMINARY_ONLY",
        "notice": "No formal hydraulic, vendor, mechanical or Aspen acceptance is implied.",
        "results": {},
        "open_items": [],
    }
    mapping = {"tower": tower_screen, "pipe": pipe_screen, "pump": pump_screen}
    for name, function in mapping.items():
        if name not in payload:
            continue
        data = payload[name]
        if not isinstance(data, dict):
            raise InputError(f"{name} must be an object")
        out["results"][name] = function(data)
    if not out["results"]:
        raise InputError("provide at least one of: tower, pipe, pump")
    out["open_items"].append(
        "Formal tray/packing hydraulics, pipe-network losses, multiphase/transient checks, "
        "vendor ratings and mechanical design remain outside this script."
    )
    return out


def example_payload() -> dict[str, Any]:
    return {
        "tower": {
            "vapor_volumetric_flow_m3_s": 1.0,
            "design_velocity_m_s": 1.5,
            "design_velocity_basis": "total_area",
            "downcomer_area_fraction": 0.10,
            "receiving_area_fraction": 0.02,
            "inactive_area_fraction": 0.03,
            "vapor_density_kg_m3": 2.0,
            "flooding_f_factor_pa_0_5": 2.5,
            "f_factor_basis": "total_area",
        },
        "pipe": {
            "volumetric_flow_m3_s": 0.01,
            "target_velocity_m_s": 2.0,
            "selected_inside_diameter_m": 0.08,
        },
        "pump": {
            "volumetric_flow_m3_s": 0.01,
            "head_m": 30.0,
            "density_kg_m3": 1000.0,
            "pump_efficiency_fraction": 0.70,
            "npsha_m": 5.0,
            "npshr_m": 3.0,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="JSON input file; use - for stdin")
    parser.add_argument("--output", help="optional JSON output file")
    parser.add_argument("--example", action="store_true", help="print an example input payload")
    parser.add_argument("--indent", type=int, default=2)
    args = parser.parse_args(argv)
    try:
        if args.example:
            result = example_payload()
        else:
            if not args.input:
                parser.error("--input is required unless --example is used")
            if args.input == "-":
                payload = json.load(sys.stdin)
            else:
                payload = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
            result = run(payload)
    except (InputError, json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    text = json.dumps(result, ensure_ascii=False, indent=args.indent)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
