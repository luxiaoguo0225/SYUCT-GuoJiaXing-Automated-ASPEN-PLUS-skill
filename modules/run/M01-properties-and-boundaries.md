# M01 需求、物性与流程边界

## 模块输入与调用范围

接收 [P00物性前置轨道](../properties/index.md) 或 [流程运行模块](index.md) 的任务记录：用户目标、当前文件/运行身份、允许修改范围、已知输入与接口、来源和待解决问题。主模块与相关模块可以多次互相调用，不是互斥入口。

工程判断先读下列原理层；形成独立判断后才读案例。共享原理/案例仍通过 [多对多对应表](../../references/principle-case-map.md) 复用，不复制为各模块专属参数库。

## 原理、案例与工艺接口

**适用任务**：新建流程、物性选型/估算/回归、相平衡、电解质和验收边界。

**原理层（先读）**：[textbook-properties-and-boundaries.md](../../references/textbook-properties-and-boundaries.md) 的 M01-K01–K10。落地细节按需查 `engineering-modeling-basics.md、aspen-plus-textbook-guide.md、general-modeling-mechanics.md`。

**教材消化判断**：[R01–R04：比较基准、物性证据、相数及回归](../../references/sun-lanyi-case-derived-reasoning.md#m01)。

**专项判断**：原料标准、产品质量与工业外推边界见[保密项目通用经验](../../references/kinetics-recycle-and-delivery-reasoning.md#m01)。

**修复核验**：物性来源、零系数及换库后的复算见[物性与流程修复关口](../../references/property-provenance-and-repair-gates.md#m01)。

**精馏前置分析**：物性核验后、精馏工段搭建前，执行[相图分析](../../references/phase-diagram-before-distillation.md)；相图结论受实际参数、温压与相稳定性验证范围约束。

**案例层（后读）**：[对应表](../../references/principle-case-map.md) 中 C01/C02/C09/C13/C16/C19/C23。

**输出与接口**：守恒/相态、数据来源、方法选择、自由度与不确定性。对所有工艺模块提供边界和物性。

## 与其他模块贯通

可直接联调：[M02](M02-distillation.md)、[M03](M03-reactors.md)、[M04](M04-pressure-transport.md)、[M05](M05-heat-and-energy.md)、[M08](M08-numerics.md)、[M11](M11-mass-transfer.md)、[M12](M12-special-materials.md)、[M15](M15-troubleshooting.md)。把跨模块流股的组成、流量、相态、T/P、焓/热量、单位基准、变量所有权及未验证项一起传递；接口改变后通知所有受影响模块复算。

本模块发现报错、异常结果、物理不合理或输入完整性问题时进入 [M15](M15-troubleshooting.md)，M15诊断后仍可返回本模块。建模过程中无需等到输出阶段才允许排错。

## 返回与输出接口

返回 [运行模块](index.md) 的是当前输入、实际执行/回读证据、模型决定、原理与案例引用、接口变更和残留问题；候选结果统一进入 [输出模块](../output/index.md)。不得在本模块单独跳过检查交付。检查退回时按问题清单修复并刷新受影响证据。

## 独立物性轨道的工程支持

物性输入由[P00](../properties/index.md)统一组织，在流程模拟之前运行。本模块负责边界、所需记录和来源合理性的工程判断；M09实现原生输入/保存重开。全局方法按[P00选型规则](../properties/index.md#method-selection-and-binary-gate)选一套适用方案。重点核实际必需二元记录的来源和完整性，有缺项或不适用再比较来源；[P01](../properties/check.md)及当前快照准入通过后才向R00交接。失败留在P00，经本模块/M09/M15修复，不能搭完流程再补查。

萃取精馏的实验数据路径、全体系包络及逐体系择源见[C23专项](../../references/extractive-distillation-workflow.md#3-p00完整体系选源及验证)，同时回读M01-K04–K07；非零、较宽库温区或实测区拟合通过均不能单独放行高温循环。

物性输入禁止USER/手工覆盖/自行回归写入。文献或回归分析只可用于比较和诊断，找不到合适原生数据库来源时回P00保留未通过，不把研究结果直接录成USER。
