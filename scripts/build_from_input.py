"""Open an Aspen Plus input file, run it, and save case + report."""

from __future__ import annotations

import argparse
import os

import win32com.client


def read(apwn, path):
    node = apwn.Tree.FindNode(path)
    return node.Value, node.UnitString


def list_streams(apwn):
    node = apwn.Tree.FindNode("\\Data\\Streams")
    names = []
    for i in range(1, node.Elements.Count + 1):
        try:
            name = node.Elements.Item(i).Name
        except Exception:
            continue
        if name:
            names.append(name)
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inp", required=True, metavar="PATH")
    parser.add_argument("--save", metavar="PATH", help="save .apwz copy")
    parser.add_argument("--report", metavar="PATH", help="export .rep report")
    args = parser.parse_args()

    apwn = win32com.client.Dispatch("Apwn.Document")
    try:
        apwn.InitFromFile2(os.path.abspath(args.inp), True)
        print("Opened:", args.inp)
        apwn.Run2(False)
        print("Run2 OK")

        for stream in list_streams(apwn):
            print(f"\nStream {stream}")
            for var in ("RES_TEMP", "RES_PRES", "RES_MOLEFLOW", "RES_MASSFLOW"):
                try:
                    value, unit = read(apwn, f"\\Data\\Streams\\{stream}\\Output\\{var}")
                    print(f"  {var} = {value!r} [{unit}]")
                except Exception as exc:
                    print(f"  {var} = <{exc}>")

        if args.report:
            apwn.Export(2, os.path.abspath(args.report))
            print("\nReport:", os.path.abspath(args.report))
        if args.save:
            apwn.SaveAs2(os.path.abspath(args.save), True)
            print("Case:", os.path.abspath(args.save))
    finally:
        try:
            apwn.Quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
