"""Shortcut binary distillation calculations for Tianjin 9.5 pre-design.

Scope
-----
Constant relative volatility and constant molar overflow.  This is a screening
tool for ideal or nearly ideal binary systems, not a substitute for a rigorous
Aspen Plus RadFrac model.

Conventions
-----------
* Total condenser is not counted as a theoretical stage.
* N_MIN and N from Fenske/Gilliland exclude the reboiler, matching the
  textbook convention used in the 9.5 lecture material.  Add one for a
  reboiler equilibrium stage when reporting total equilibrium stages.
* Tray numbering starts at the top tray = 1.
* Flows are normalized by one mole of feed.

The script reports R_MIN, the q-line/operating-line intersection, shortcut
N/N_F estimates, and a constant-alpha McCabe-Thiele cross-check.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from typing import Iterable


EPS = 1e-12


@dataclass
class ColumnResult:
    q: float
    reflux_ratio: float
    reflux_factor: float
    d_over_f: float
    b_over_f: float
    x_pinch: float
    y_pinch: float
    r_min: float
    x_intersection: float
    y_intersection: float
    rectifying_slope: float
    rectifying_intercept: float
    stripping_slope: float
    stripping_intercept: float
    n_min_excl_reboiler: float
    n_shortcut_excl_reboiler: float
    n_shortcut_with_reboiler: float
    feed_stage_shortcut: int
    n_exact_excl_reboiler: int
    n_exact_with_reboiler: int
    feed_stage_exact: int
    stripping_vapor_per_feed: float


def _validate_inputs(x_f: float, x_d: float, x_b: float, alpha: float) -> None:
    if not (0.0 < x_b < x_f < x_d < 1.0):
        raise ValueError("Require 0 < xB < xF < xD < 1.")
    if alpha <= 1.0:
        raise ValueError("Relative volatility alpha must be > 1.")


def y_eq(x: float, alpha: float) -> float:
    """Equilibrium vapor composition for y = alpha*x/[1+(alpha-1)x]."""
    return alpha * x / (1.0 + (alpha - 1.0) * x)


def x_eq(y: float, alpha: float) -> float:
    """Inverse equilibrium function x = y/[alpha-(alpha-1)y]."""
    return y / (alpha - (alpha - 1.0) * y)


def q_line(x: float, q: float, x_f: float) -> float:
    if abs(q - 1.0) < 1e-10:
        raise ValueError("The q=1 q-line is vertical and has no finite slope form.")
    return (q * x - x_f) / (q - 1.0)


def _bisect(
    func,
    left: float,
    right: float,
    *,
    iterations: int = 100,
) -> float:
    f_left = func(left)
    for _ in range(iterations):
        mid = 0.5 * (left + right)
        f_mid = func(mid)
        if abs(f_mid) < 1e-13:
            return mid
        if f_left * f_mid <= 0.0:
            right = mid
        else:
            left = mid
            f_left = f_mid
    return 0.5 * (left + right)


def _roots_on_unit_interval(func, samples: int = 20000) -> list[float]:
    """Find sign-change roots on (0,1), sufficient for smooth binary curves."""
    xs = [i / samples for i in range(samples + 1)]
    roots: list[float] = []
    for i in range(samples):
        left, right = xs[i], xs[i + 1]
        f_left, f_right = func(left), func(right)
        if abs(f_left) < 1e-13:
            roots.append(left)
        if f_left * f_right < 0.0:
            roots.append(_bisect(func, left, right))
    if abs(func(1.0)) < 1e-13:
        roots.append(1.0)
    # Remove duplicates created by neighboring intervals.
    unique: list[float] = []
    for root in roots:
        if not unique or abs(root - unique[-1]) > 1e-7:
            unique.append(root)
    return unique


def pinch_at_q_line(q: float, x_f: float, alpha: float, x_d: float) -> tuple[float, float]:
    """Return the limiting q-line/equilibrium pinch for a normal curve."""
    if abs(q - 1.0) < 1e-10:
        return x_f, y_eq(x_f, alpha)

    def diff(x: float) -> float:
        return q_line(x, q, x_f) - y_eq(x, alpha)

    candidates: list[tuple[float, float, float]] = []
    for x_q in _roots_on_unit_interval(diff):
        if not (EPS < x_q < 1.0 - EPS):
            continue
        y_q = y_eq(x_q, alpha)
        denom = y_q - x_q
        if denom <= EPS or y_q >= x_d:
            continue
        r_candidate = (x_d - y_q) / denom
        if r_candidate > -EPS:
            candidates.append((x_q, y_q, r_candidate))

    if not candidates:
        raise ValueError(
            "No valid q-line/equilibrium pinch found. Check q, xF, xD, and the "
            "equilibrium curve; tangent or multiple pinches need a rigorous model."
        )
    x_q, y_q, _ = max(candidates, key=lambda item: item[2])
    return x_q, y_q


def r_min_normal(q: float, x_f: float, x_d: float, alpha: float) -> tuple[float, float, float]:
    x_q, y_q = pinch_at_q_line(q, x_f, alpha, x_d)
    value = (x_d - y_q) / (y_q - x_q)
    if value < -EPS:
        raise ValueError("Computed negative R_MIN for this normal-curve interpretation.")
    return max(0.0, value), x_q, y_q


def gilliland_y(x_value: float) -> float:
    """Eduljee correlation for the Gilliland Y coordinate."""
    if x_value <= 0.0:
        return 1.0
    if x_value >= 1.0:
        return 0.0
    term = ((1.0 + 54.4 * x_value) / (11.0 + 117.2 * x_value)) * (
        (x_value - 1.0) / math.sqrt(x_value)
    )
    return 1.0 - math.exp(term)


def fenske_n_min(x_light_top: float, x_light_bottom: float, alpha: float) -> float:
    ratio = (x_light_top / (1.0 - x_light_top)) * (
        (1.0 - x_light_bottom) / x_light_bottom
    )
    return max(0.0, math.log(ratio) / math.log(alpha) - 1.0)


def shortcut_stages(
    x_f: float,
    x_d: float,
    x_b: float,
    alpha: float,
    r_value: float,
    r_min_value: float,
) -> tuple[float, float, int]:
    if r_value <= r_min_value:
        raise ValueError("R must be greater than R_MIN for finite Gilliland stages.")
    y_value = gilliland_y((r_value - r_min_value) / (r_value + 1.0))
    n_min_total = fenske_n_min(x_d, x_b, alpha)
    n_min_rect = fenske_n_min(x_d, x_f, alpha)
    n_shortcut = (n_min_total + y_value) / (1.0 - y_value)
    n_rect = (n_min_rect + y_value) / (1.0 - y_value)
    feed_stage = max(1, round(n_rect) + 1)
    return n_shortcut, n_min_total, feed_stage


def mccabe_thiele(
    q: float,
    x_f: float,
    x_d: float,
    x_b: float,
    alpha: float,
    r_value: float,
    *,
    max_stages: int = 1000,
) -> ColumnResult:
    _validate_inputs(x_f, x_d, x_b, alpha)
    d_over_f = (x_f - x_b) / (x_d - x_b)
    b_over_f = 1.0 - d_over_f
    l_rect = r_value * d_over_f
    v_rect = (r_value + 1.0) * d_over_f
    l_strip = l_rect + q
    v_strip = v_rect - (1.0 - q)

    if v_strip <= EPS:
        raise ValueError("Stripping vapor flow is non-positive; feed q/R combination is infeasible.")

    r_min_value, x_q, y_q = r_min_normal(q, x_f, x_d, alpha)
    if r_value <= r_min_value:
        raise ValueError(f"R={r_value} must exceed R_MIN={r_min_value:.6g}.")

    rect_slope = r_value / (r_value + 1.0)
    rect_intercept = x_d / (r_value + 1.0)
    strip_slope = l_strip / v_strip
    strip_intercept = -b_over_f * x_b / v_strip

    if abs(r_value + q) < EPS:
        raise ValueError("R + q is zero; operating-line intersection is singular.")
    x_d_int = (x_d * (q - 1.0) + x_f * (r_value + 1.0)) / (r_value + q)
    y_d_int = rect_slope * x_d_int + rect_intercept

    if not (x_b <= x_d_int <= x_d) or not (0.0 <= y_d_int <= 1.0):
        raise ValueError(
            "Operating-line intersection lies outside the physical stepping range."
        )

    x_value = x_d
    feed_stage: int | None = None
    total_stage = 0

    for stage in range(1, max_stages + 1):
        if stage == 1:
            y_value = x_d  # total condenser: y1 = xD
        elif feed_stage is None:
            y_value = rect_slope * x_value + rect_intercept
        else:
            y_value = strip_slope * x_value + strip_intercept

        if not (0.0 <= y_value <= 1.0):
            raise ValueError(
                f"McCabe-Thiele left [0,1] at stage {stage}; check q/R and assumptions."
            )

        x_next = x_eq(y_value, alpha)
        if not (0.0 <= x_next <= 1.0):
            raise ValueError(f"Invalid equilibrium liquid x at stage {stage}.")

        if feed_stage is None and x_next <= x_d_int:
            feed_stage = stage

        x_value = x_next
        total_stage = stage
        if x_value <= x_b:
            break
    else:
        raise ValueError(f"Did not reach xB within {max_stages} stages.")

    if feed_stage is None:
        raise ValueError("No feed-stage crossing found within the stepping range.")

    n_shortcut, n_min_total, feed_shortcut = shortcut_stages(
        x_f, x_d, x_b, alpha, r_value, r_min_value
    )
    return ColumnResult(
        q=q,
        reflux_ratio=r_value,
        reflux_factor=r_value / r_min_value if r_min_value > EPS else math.inf,
        d_over_f=d_over_f,
        b_over_f=b_over_f,
        x_pinch=x_q,
        y_pinch=y_q,
        r_min=r_min_value,
        x_intersection=x_d_int,
        y_intersection=y_d_int,
        rectifying_slope=rect_slope,
        rectifying_intercept=rect_intercept,
        stripping_slope=strip_slope,
        stripping_intercept=strip_intercept,
        n_min_excl_reboiler=n_min_total,
        n_shortcut_excl_reboiler=n_shortcut,
        n_shortcut_with_reboiler=n_shortcut + 1.0,
        feed_stage_shortcut=feed_shortcut,
        n_exact_excl_reboiler=total_stage - 1,
        n_exact_with_reboiler=total_stage,
        feed_stage_exact=feed_stage,
        stripping_vapor_per_feed=v_strip,
    )


def _fmt(value: float) -> str:
    return f"{value:.6g}"


def _print_result(result: ColumnResult) -> None:
    print("Binary distillation 9.5 preview (constant alpha, constant molar overflow)")
    print(f"  q                         = {_fmt(result.q)}")
    print(f"  D/F, B/F                  = {_fmt(result.d_over_f)}, {_fmt(result.b_over_f)}")
    print(f"  R_min                     = {_fmt(result.r_min)}")
    print(f"  R, R/R_min                = {_fmt(result.reflux_ratio)}, {_fmt(result.reflux_factor)}")
    print(f"  pinch (x_q, y_q)          = ({_fmt(result.x_pinch)}, {_fmt(result.y_pinch)})")
    print(f"  d intersection (x_d,y_d)  = ({_fmt(result.x_intersection)}, {_fmt(result.y_intersection)})")
    print(f"  rectifying line           = y = {_fmt(result.rectifying_slope)} x + {_fmt(result.rectifying_intercept)}")
    print(f"  stripping line            = y = {_fmt(result.stripping_slope)} x + {_fmt(result.stripping_intercept)}")
    print(f"  N_min excl. reboiler      = {_fmt(result.n_min_excl_reboiler)}")
    print(f"  N shortcut excl. reboiler = {_fmt(result.n_shortcut_excl_reboiler)}")
    print(f"  N shortcut incl. reboiler = {_fmt(result.n_shortcut_with_reboiler)}")
    print(f"  N_F shortcut              = {result.feed_stage_shortcut}")
    print(f"  N exact excl. reboiler    = {result.n_exact_excl_reboiler}")
    print(f"  N exact incl. reboiler    = {result.n_exact_with_reboiler}")
    print(f"  N_F exact M-T             = {result.feed_stage_exact}")
    print(f"  V_stripping / F           = {_fmt(result.stripping_vapor_per_feed)}")
    print("  Preview only: validate the final design with rigorous Aspen Plus.")


def _json_result(result: ColumnResult) -> str:
    return json.dumps(result.__dict__, ensure_ascii=False, indent=2)


def _parse_q_grid(minimum: float, maximum: float, count: int) -> Iterable[float]:
    if minimum > maximum:
        raise ValueError("q-min must be <= q-max.")
    if count < 2:
        return [minimum]
    return [minimum + (maximum - minimum) * i / (count - 1) for i in range(count)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xF", type=float, required=True)
    parser.add_argument("--xD", type=float, required=True)
    parser.add_argument("--xB", type=float, required=True)
    parser.add_argument("--alpha", type=float, required=True)
    parser.add_argument("--q", type=float, default=1.0)
    parser.add_argument("--r", type=float, default=None, help="Absolute reflux ratio.")
    parser.add_argument(
        "--r-factor",
        type=float,
        default=1.5,
        help="R/R_MIN used when --r is omitted (default: 1.5).",
    )
    parser.add_argument("--max-stages", type=int, default=1000)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--sweep-r", action="store_true")
    parser.add_argument("--sweep-q", action="store_true")
    parser.add_argument("--r-min-factor", type=float, default=1.1)
    parser.add_argument("--r-max-factor", type=float, default=2.0)
    parser.add_argument("--r-steps", type=int, default=10)
    parser.add_argument("--q-min", type=float, default=0.0)
    parser.add_argument("--q-max", type=float, default=2.0)
    parser.add_argument("--q-steps", type=int, default=9)
    args = parser.parse_args(argv)

    if args.sweep_r and args.sweep_q:
        parser.error("Use only one of --sweep-r and --sweep-q per run.")
    _validate_inputs(args.xF, args.xD, args.xB, args.alpha)

    if args.sweep_r:
        base = mccabe_thiele(
            args.q,
            args.xF,
            args.xD,
            args.xB,
            args.alpha,
            max(args.r_min_factor, 1.000001)
            * r_min_normal(args.q, args.xF, args.xD, args.alpha)[0],
            max_stages=args.max_stages,
        )
        rmin = base.r_min
        if args.r_steps < 1:
            parser.error("--r-steps must be >= 1")
        rows = []
        for i in range(args.r_steps + 1):
            factor = args.r_min_factor + (args.r_max_factor - args.r_min_factor) * i / args.r_steps
            try:
                item = mccabe_thiele(
                    args.q,
                    args.xF,
                    args.xD,
                    args.xB,
                    args.alpha,
                    factor * rmin,
                    max_stages=args.max_stages,
                )
                rows.append(item.__dict__)
            except ValueError as exc:
                rows.append({"R_over_Rmin": factor, "error": str(exc)})
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            for row in rows:
                if "error" in row:
                    print(f"R/Rmin={row['R_over_Rmin']:.3g}: {row['error']}")
                else:
                    print(
                        f"R/Rmin={row['reflux_factor']:.3g}: "
                        f"N(excl.reb)={row['n_exact_excl_reboiler']}, "
                        f"N_F={row['feed_stage_exact']}, "
                        f"V_strip/F={row['stripping_vapor_per_feed']:.6g}"
                    )
        return 0

    if args.sweep_q:
        r_ref = args.r if args.r is not None else args.r_factor * r_min_normal(
            1.0, args.xF, args.xD, args.alpha
        )[0]
        rows = []
        for q_value in _parse_q_grid(args.q_min, args.q_max, args.q_steps):
            try:
                item = mccabe_thiele(
                    q_value,
                    args.xF,
                    args.xD,
                    args.xB,
                    args.alpha,
                    r_ref,
                    max_stages=args.max_stages,
                )
                rows.append(item.__dict__)
            except ValueError as exc:
                rows.append({"q": q_value, "R": r_ref, "error": str(exc)})
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            for row in rows:
                if "error" in row:
                    print(f"q={row['q']:.3g}, R={row['R']:.3g}: {row['error']}")
                else:
                    print(
                        f"q={row['q']:.3g}, Rmin={row['r_min']:.3g}, "
                        f"N(excl.reb)={row['n_exact_excl_reboiler']}, "
                        f"N_F={row['feed_stage_exact']}, "
                        f"V_strip/F={row['stripping_vapor_per_feed']:.6g}"
                    )
        return 0

    rmin = r_min_normal(args.q, args.xF, args.xD, args.alpha)[0]
    r_value = args.r if args.r is not None else args.r_factor * rmin
    try:
        result = mccabe_thiele(
            args.q,
            args.xF,
            args.xD,
            args.xB,
            args.alpha,
            r_value,
            max_stages=args.max_stages,
        )
    except ValueError as exc:
        parser.error(str(exc))
    if args.json:
        print(_json_result(result))
    else:
        _print_result(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())