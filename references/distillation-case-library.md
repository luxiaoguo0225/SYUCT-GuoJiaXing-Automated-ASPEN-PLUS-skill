# Local Distillation Case Library (2026-08-11)

Use these local folders as workflow and model-pattern references when the user asks to study or reproduce distillation energy-saving cases. They are learning/reference cases, not authority for a new project: verify chemistry, property method, streams, pressures, and specs from the current project before copying anything.

## Source folders

| Technique | Folder | Representative files |
| --- | --- | --- |
| Heat pump distillation | `D:\BaiduNetdiskDownload\热泵精馏（甲醇-水）` | `甲醇-水常规精馏系统参数优化后最终文件.apwz`, `甲醇-水常规精馏系统模拟及优化.docx` |
| Pressure-swing distillation | `D:\BaiduNetdiskDownload\变压精馏` | `变压精馏-乙酸乙酯和甲醇.apwz`, `变压精馏-四氢呋喃和水.apwz` |
| Azeotropic distillation | `D:\BaiduNetdiskDownload\共沸精馏` | `共沸精馏-乙醇和水.apwz` |
| Batch distillation | `D:\BaiduNetdiskDownload\间歇精馏` | `aspen间歇模拟\1 变回流比.bkp`, `乙腈和水间歇精馏.apwz`, `乙酸乙酯和正庚烷，用水共沸间歇精馏.apwz` |
| Dividing wall column | `D:\BaiduNetdiskDownload\隔壁塔精馏` | `隔壁塔精馏模型-合并为1个塔10.14.apwz`, `隔壁塔精馏模型（双塔）.apwz` |
| Extractive distillation | `D:\BaiduNetdiskDownload\萃取精馏` | `萃取精馏-二氯甲烷和甲醇.apwz` |
| Double/multi-effect distillation | `D:\BaiduNetdiskDownload\双效-多效精馏（甲醇-水）` | `1.双效并流精馏\甲醇-水双效并流精馏.apwz`, `2.双效逆流\甲醇-水双效逆流精馏.apwz`, `4.三效顺流精馏\甲醇-水顺流三效精馏.apwz` |

Some files are older Aspen versions. Open them with V14 `InitFromFile2` directly; version mismatch is usually not a blocker.

## Methods demonstrated

- **Heat pump distillation**: overhead vapor split, superheater, ASME polytropic compressor, `HeatX` used as reboiler, valve return to column pressure, energy comparison against a conventional column.
- **Pressure-swing distillation**: two columns at different pressures to break a pressure-sensitive azeotrope, with recycle between columns and energy integration opportunities.
- **Azeotropic distillation**: entrainer/heterogeneous azeotrope handling, decanter or second liquid phase, recycle of the entrainer-rich stream.
- **Batch distillation**: RadFrac in batch mode, variable reflux ratio, multiple operating steps, pressure-specified heating, multi-component batch cases.
- **Dividing wall column**: equivalent two-column representation and a merged single-column model; compare the two to validate the wall split.
- **Extractive distillation**: solvent feed above the main feed, solvent recovery column, and solvent recycle; check binary parameters for the solvent-heavy component pair.
- **Double/multi-effect distillation**: co-current, counter-current, and parallel configurations; pressure optimization for the high-pressure tower; feed-concentration sensitivity; utility comparison between conventional, double-effect, and triple-effect systems.

## Today's validated Aspen automation paths

- Original user column: `%USERPROFILE%\Desktop\新建文件夹\8.11拆塔演示to codex.bkp`.
- Split-only deliverable: `%USERPROFILE%\Documents\Codex\2026-08-11\ni\outputs\8_11_column_split_heatpump\baseline_split\`.
- Heat pump deliverable: `%USERPROFILE%\Documents\Codex\2026-08-11\ni\outputs\8_11_column_split_heatpump\heatpump_split\`.

## Reusable workflow patterns

1. Run the original case first and record product flow, reflux, top/bottom temperatures, condenser duty, and reboiler duty.
2. Split a RadFrac into bare column plus external `Heater -> Flash2 -> FSplit` loops when the user asks for a column split.
3. For heat pump integration, keep the reboiler on a `HeatX` and the condenser on a `Heater + Flash2`; explicitly tear the recycle streams and give initial estimates.
4. Compare on the same product basis: fixed distillate flow and the same product purity target.
5. Export the report immediately after `Run2`; component-level COM reads from a reopened `.apwz` can return `None`.
6. For a shareable result, save `.bkp`/`.apwz` plus `.rep` and a short `README.md` in the same output folder.
