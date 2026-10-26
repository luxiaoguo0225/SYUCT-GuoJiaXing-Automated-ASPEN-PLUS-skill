# Aspen Plus COM Reference

## COM Entry Point

- ProgID: `Apwn.Document`
- Dispatch from Python with `win32com.client.Dispatch("Apwn.Document")`
- The typed interface is `Aspen Plus GUI 40.0 Type Library` on V14.

## File Operations

- `InitFromFile2(filename, readonly=True)` opens `.bkp`, `.apwz`, and `.inp` files.
- `InitFromArchive2(filename)` can fail for local `.apwz` files with error code 2041; prefer `InitFromFile2`.
- `SaveAs2(filename, overwrite=True)` saves a copy.
- `Export(2, filename.rep)` exports a calculation report.
- `Visible` must be set after `InitNew`/`InitFromFile`, not before initialization.
- To keep the GUI open after automation: save the case, launch it with `os.startfile(apwz)`, then let the automation instance `Quit()`.
- `Quit()` closes the document, but an empty `AspenPlus.exe` window may remain; stop leftover processes only when they were started by automation.

## Data Tree Access

- `Tree` property returns an `IHNode` root; `Tree.FindNode("\\Data")` returns the simulation data root.
- `RootModel(path)` requires a path argument and is not needed for normal variable access.
- `IHNode` key members:
  - `Name`, `Value`, `UnitString`, `ValueType`
  - `Elements.Count`, `Elements.Item(index)` for children (1-based)
  - `FindNode(path)` to navigate relative paths
- Table nodes use 0-based rows: `Elements.RowCount(0)`, `Elements.Label(0, row)`, `Elements.Item(row).Value`.
- `IHNodeCol.ItemName(location)` can fail on some special nodes; use `Item(index).Name` with error handling instead.

## Variable Paths

Common stream paths:

```text
\Data\Streams\<name>\Input\TEMP\MIXED
\Data\Streams\<name>\Input\PRES\MIXED
\Data\Streams\<name>\Input\TOTFLOW
\Data\Streams\<name>\Input\FLOW\MIXED\<component>
\Data\Streams\<name>\Output\RES_TEMP
\Data\Streams\<name>\Output\RES_PRES
\Data\Streams\<name>\Output\RES_MOLEFLOW
\Data\Streams\<name>\Output\RES_MASSFLOW
\Data\Streams\<name>\Output\MOLEFLOW\MIXED\<component>
```

`Input\TEMP` and `Input\PRES` are container nodes; the scalar value lives under the `MIXED` child for material streams.

## Common Failure Modes

[M15中的诊断与修复正文](../modules/run/diagnostics/variables-and-troubleshooting-fixes.md)。本处保留案例上下文与旧锚点；修复规则统一维护在M15。

## Automation Sequence

```python
import os
import win32com.client

apwn = win32com.client.Dispatch("Apwn.Document")
try:
    apwn.InitFromFile2(r"C:\path\to\case.inp", True)
    apwn.Visible = True
    tree = apwn.Tree
    node = tree.FindNode(r"\Data\Streams\FEED\Input\TEMP\MIXED")
    node.Value = 50.0
    apwn.Run2(False)
    print(tree.FindNode(r"\Data\Streams\PRODUCT\Output\RES_TEMP").Value)
    apwn.Export(2, r"C:\path\to\result.rep")
    apwn.SaveAs2(r"C:\path\to\result.apwz", True)
    os.startfile(r"C:\path\to\result.apwz")
finally:
    apwn.Quit()
```
