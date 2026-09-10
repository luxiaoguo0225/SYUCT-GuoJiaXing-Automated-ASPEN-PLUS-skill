"""Aspen Plus V14 COM automation bridge.

Requires: Windows + Aspen Plus V14 + pywin32
  python -m pip install pywin32

Example:
  python aspen_plus_bridge.py --open sour.apwz ^
    --set "\\Data\\Streams\\FEED\\Input\\TEMP\\MIXED=50" ^
    --run --get "\\Data\\Streams\\BOT1\\Output\\RES_TEMP" ^
    --save result.apwz
"""

from __future__ import annotations

import argparse
import os
import sys


def _com_module():
    try:
        import win32com.client
    except ImportError:
        sys.exit("pywin32 is required. Run: python -m pip install pywin32")
    return win32com.client


class AspenPlus:
    """Thin wrapper around the Apwn.Document COM interface."""

    def __init__(self):
        com = _com_module()
        self.app = com.Dispatch("Apwn.Document")

    def open(self, path: str) -> "AspenPlus":
        self.app.InitFromFile2(os.path.abspath(path), True)
        return self

    def run(self, async_run: bool = False) -> "AspenPlus":
        self.app.Run2(async_run)
        return self

    def node(self, path: str):
        return self.app.Tree.FindNode(path)

    def get(self, path: str):
        node = self.node(path)
        return node.Value, node.UnitString

    def set(self, path: str, value) -> "AspenPlus":
        node = self.node(path)
        node.Value = value
        return self

    def save_as(self, path: str) -> "AspenPlus":
        self.app.SaveAs2(os.path.abspath(path), True)
        return self

    def list_streams(self):
        node = self.node("\\Data\\Streams")
        names = []
        for i in range(1, node.Elements.Count + 1):
            try:
                name = node.Elements.Item(i).Name
            except Exception:
                continue
            if name:
                names.append(name)
        return names

    def close(self) -> None:
        try:
            self.app.Quit()
        except Exception:
            pass


def _coerce(value: str):
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def _demo():
    case = (
        r"C:\Program Files\AspenTech\Aspen Plus V14.0\GUI\Examples"
        r"\Midstream\sour.apwz"
    )
    aspen = AspenPlus()
    try:
        aspen.open(case)
        print("Opened:", case)

        def report(label):
            print(f"\n{label}")
            for path in (
                r"\Data\Streams\FEED\Input\TEMP\MIXED",
                r"\Data\Streams\FEED\Input\PRES\MIXED",
                r"\Data\Streams\FEED\Output\RES_TEMP",
                r"\Data\Streams\BOT1\Output\RES_TEMP",
                r"\Data\Streams\BOT2\Output\RES_TEMP",
            ):
                value, unit = aspen.get(path)
                print(f"  {path} = {value!r} [{unit}]")

        report("BEFORE")
        aspen.set(r"\Data\Streams\FEED\Input\TEMP\MIXED", 50.0)
        print("\nSet FEED Input TEMP -> 50 C")
        aspen.run()
        print("Run2 OK")
        report("AFTER")

        out = os.path.join(os.getcwd(), "aspen_demo_result.apwz")
        aspen.save_as(out)
        print("\nSaved:", out)
    finally:
        aspen.close()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Drive Aspen Plus V14 through COM automation."
    )
    parser.add_argument("--open", metavar="PATH", help="case file (.bkp/.apwz)")
    parser.add_argument("--run", action="store_true", help="run the simulation")
    parser.add_argument(
        "--get", nargs="+", metavar="PATH", help="variable paths to read"
    )
    parser.add_argument(
        "--set", nargs="+", metavar="PATH=VALUE", help="variable paths to write"
    )
    parser.add_argument("--save", metavar="PATH", help="save result copy")
    parser.add_argument("--streams", action="store_true", help="list stream names")
    parser.add_argument("--demo", action="store_true", help="run built-in demo")
    args = parser.parse_args(argv)

    if args.demo:
        _demo()
        return
    if not args.open:
        parser.error("--open PATH is required (or use --demo)")

    aspen = AspenPlus()
    try:
        aspen.open(args.open)
        print("Opened:", args.open)
        if args.streams:
            print("\nStreams:", ", ".join(aspen.list_streams()))
        for item in args.set or []:
            path, _, value = item.rpartition("=")
            if not path:
                parser.error(f"--set expects PATH=VALUE, got: {item}")
            aspen.set(path, _coerce(value))
            print(f"Set {path} = {value}")
        if args.run:
            aspen.run()
            print("Run2 OK")
        for path in args.get or []:
            value, unit = aspen.get(path)
            print(f"{path} = {value!r} [{unit}]")
        if args.save:
            aspen.save_as(args.save)
            print("Saved:", os.path.abspath(args.save))
    finally:
        aspen.close()


if __name__ == "__main__":
    main()
