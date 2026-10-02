# -*- coding: utf-8 -*-
"""Preliminary heat-carrier / HX screening (molten salt + water saturation table).

Sources: nitrate-salt properties from INL/EXT-10-18297 (OSTI 980801), correlations from
Janz et al. (1981); water saturation from IAPWS-IF97 (tabulated, linear interpolation).
PRELIMINARY screening only - formal design needs Aspen Detailed/EDR or a vendor rating.
"""
from __future__ import annotations
import argparse


def nitrate_cp(TK):
    return 5806.0 - 10.833 * TK + 7.2413e-3 * TK * TK      # J/(kg.K), 426-776 K, +-5%


def nitrate_rho(TK):
    return 2293.6 - 0.7497 * TK                           # kg/m3, 470-870 K, +-2%


def nitrate_mu(TK):
    return 0.4737 - 2.297e-3 * TK + 3.731e-6 * TK * TK - 2.019e-9 * TK ** 3   # Pa.s


INL_K_NITRATE = 0.55   # W/(m.K), INL Table 1.1 for NaNO3-KNO3 at 400 C

_TSAT_C = [0.0, 100.0, 150.0, 200.0, 223.96, 247.33, 250.36, 300.0, 311.0, 320.0, 350.0]
_PSAT_MPA = [0.000611, 0.101325, 0.476, 1.554, 2.500, 3.800, 3.976, 8.588, 10.0, 11.284, 16.529]


def water_psat_mpa(TC):
    if TC <= _TSAT_C[0]:
        return _PSAT_MPA[0]
    if TC >= _TSAT_C[-1]:
        return _PSAT_MPA[-1]
    for i in range(len(_TSAT_C) - 1):
        t0, t1 = _TSAT_C[i], _TSAT_C[i + 1]
        if t0 <= TC <= t1:
            p0, p1 = _PSAT_MPA[i], _PSAT_MPA[i + 1]
            return p0 + (p1 - p0) * (TC - t0) / (t1 - t0)
    return float("nan")


def screen(q_kw, dt_salt, t_mean_c, u_salt, d_mm, r_foul, h_water, wall_mm, wall_k, dp_bar, pump_eff, lmtd):
    TK = t_mean_c + 273.15
    cp, rho, mu, k = nitrate_cp(TK), nitrate_rho(TK), nitrate_mu(TK), INL_K_NITRATE
    pr = cp * mu / k
    m_dot = q_kw * 1000.0 / (cp * dt_salt)
    q_vol = m_dot / rho
    p_fluid = dp_bar * 1e5 * q_vol
    D = d_mm / 1000.0
    Re = rho * u_salt * D / mu
    Nu = 0.023 * Re ** 0.8 * pr ** 0.4
    h_salt = Nu * k / D
    R = 1.0 / h_salt + r_foul + (wall_mm / 1000.0) / wall_k + 1.0 / h_water
    U = 1.0 / R
    return dict(cp=cp, rho=rho, mu=mu, k=k, pr=pr, m_dot=m_dot, q_vol=q_vol, p_fluid=p_fluid,
                p_brake=p_fluid / pump_eff, Re=Re, Nu=Nu, h_salt=h_salt, U=U, R=R,
                area=q_kw * 1000.0 / (U * lmtd))


def main():
    ap = argparse.ArgumentParser(description="preliminary heat-carrier / HX screening")
    ap.add_argument("--q", type=float, default=605.086)
    ap.add_argument("--dt", type=float, default=72.3)
    ap.add_argument("--tmean", type=float, default=300.0)
    ap.add_argument("--u", type=float, default=0.5)
    ap.add_argument("--d", type=float, default=20.0)
    ap.add_argument("--rfoul", type=float, default=0.0004)
    ap.add_argument("--hwater", type=float, default=4000.0)
    ap.add_argument("--wall", type=float, default=2.0)
    ap.add_argument("--wallk", type=float, default=16.0)
    ap.add_argument("--dp", type=float, default=2.0)
    ap.add_argument("--eff", type=float, default=0.65)
    ap.add_argument("--lmtd", type=float, default=58.74)
    ap.add_argument("--tcold-salt", type=float, default=250.0, dest="tcold_salt")
    ap.add_argument("--tcold-water", type=float, default=202.45, dest="tcold_water")
    ap.add_argument("--tfreeze", type=float, default=222.0)
    a = ap.parse_args()
    r = screen(a.q, a.dt, a.tmean, a.u, a.d, a.rfoul, a.hwater, a.wall, a.wallk, a.dp, a.eff, a.lmtd)
    print("== INL nitrate-salt properties @ %.0f C ==" % a.tmean)
    print("   cp=%.0f J/(kg.K) | rho=%.0f kg/m3 | mu=%.5f Pa.s | k=%.2f W/(m.K) | Pr=%.2f"
          % (r["cp"], r["rho"], r["mu"], r["k"], r["pr"]))
    print("== carrier loop (Q=%.1f kW, dT=%.1f K) ==" % (a.q, a.dt))
    print("   mass flow %.3f kg/s = %.2f t/h | volume flow %.2f m3/h"
          % (r["m_dot"], r["m_dot"] * 3.6, r["q_vol"] * 3600.0))
    print("   pump dP=%.2f bar -> fluid %.2f kW, brake %.2f kW (eff %.2f)"
          % (a.dp, r["p_fluid"] / 1e3, r["p_brake"] / 1e3, a.eff))
    print("== heat transfer (salt in tubes, D=%.0f mm, u=%.2f m/s) ==" % (a.d, a.u))
    print("   Re=%.0f | Nu=%.1f | h_salt=%.0f -> U=%.0f W/(m2.K) -> A=%.2f m2 (LMTD %.2f K)"
          % (r["Re"], r["Nu"], r["h_salt"], r["U"], r["area"], a.lmtd))
    drop = (a.tcold_salt - a.tcold_water) * (1.0 / r["h_salt"]) / r["R"]
    tw = a.tcold_salt - drop
    print("== cold-end film check ==")
    print("   salt %.1f C, water %.1f C -> drop %.1f K -> wall-side salt %.1f C ; margin to %.0f C = %+.1f K"
          % (a.tcold_salt, a.tcold_water, drop, tw, a.tfreeze, tw - a.tfreeze))
    print("== U -> A sensitivity ==")
    for U in (400, 500, 600, 700, 850, 1000, 1200):
        print("   U=%4d -> A=%5.2f m2" % (U, a.q * 1000.0 / (U * a.lmtd)))
    if tw < a.tfreeze + 20.0:
        print("   [!] wall-side salt < freezing + 20 K: raise salt cold end / use lower-melting salt / raise velocity.")
    print("== water saturation points (IF97) ==")
    for t in (200, 250, 300, 320, 350):
        print("   T=%3d C -> Psat=%.2f MPa" % (t, water_psat_mpa(t)))


if __name__ == "__main__":
    main()
