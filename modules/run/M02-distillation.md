# M02 精馏塔与特殊精馏

## 模块输入与调用范围

接收 [运行模块](index.md) 的任务记录：用户目标、当前文件/运行身份、允许修改范围、已知输入与接口、来源和待解决问题。主模块与相关模块可以多次互相调用，不是互斥入口。

工程判断先读下列原理层；形成独立判断后才读案例。共享原理/案例仍通过 [多对多对应表](../../references/principle-case-map.md) 复用，不复制为各模块专属参数库。

## 原理、案例与工艺接口

**适用任务**：DSTWU/RadFrac、q/R/N/进料板、平衡/速率塔、萃取/共沸/变压/反应/三相精馏。

**原理层（先读）**：[textbook-distillation-and-towers.md](../../references/textbook-distillation-and-towers.md) 的 M02-K01–K10。落地细节按需查 `tianjin-distillation-9-5-calculation.md、sun-lanyi-ch7-4-radfrac-strict.md、feed-stage-sensitivity-curves.md`。

**教材消化判断**：[R05–R11：塔问题分型、级位置、压力、再沸器及特殊分离](../../references/sun-lanyi-case-derived-reasoning.md#m02)。

**专项判断**：严格塔与指定分离率模型的边界、非理想多相解的验证见[收敛、分离模型与节能验证](../../references/convergence-separation-and-energy-integrity.md)第1–4节。

**修复核验**：严格塔规格、操纵量触界及诊断扫描见[物性与流程修复关口](../../references/property-provenance-and-repair-gates.md#m02)。

**搭塔前必须应用**：[精馏建模前相图分析](../../references/phase-diagram-before-distillation.md)。先用适用相图判断分离路线、关键组分、候选压力及夹带剂/溶剂，再用严格塔确定级数、进料板和回流比。改动关键物性、压力或溶剂后重新核查相图；不得靠盲目加板/调回流绕过热力学诊断。

**案例层（后读）**：[对应表](../../references/principle-case-map.md) 中 C01/C04/C11/C13/C16。

**输出与接口**：物料与相平衡、MESH与规格、级数/效率、压力与热敏边界。压力连M04，热量连M05/M06，水力连M07，DS/收敛连M08；吸收/萃取等独立操作进M11。

## 与其他模块贯通

可直接联调：[M01](M01-properties-and-boundaries.md)、[M04](M04-pressure-transport.md)、[M05](M05-heat-and-energy.md)、[M06](M06-thermal-coupling.md)、[M07](M07-hydraulics-rating.md)、[M08](M08-numerics.md)、[M11](M11-mass-transfer.md)、[M15](M15-troubleshooting.md)。把跨模块流股的组成、流量、相态、T/P、焓/热量、单位基准、变量所有权及未验证项一起传递；接口改变后通知所有受影响模块复算。

本模块发现报错、异常结果、物理不合理或输入完整性问题时进入 [M15](M15-troubleshooting.md)，M15诊断后仍可返回本模块。建模过程中无需等到输出阶段才允许排错。

## 返回与输出接口

返回 [运行模块](index.md) 的是当前输入、实际执行/回读证据、模型决定、原理与案例引用、接口变更和残留问题；候选结果统一进入 [输出模块](../output/index.md)。不得在本模块单独跳过检查交付。检查退回时按问题清单修复并刷新受影响证据。
