# M08 循环、Design Spec、收敛与验证

## 模块输入与调用范围

接收 [运行模块](index.md) 的任务记录：用户目标、当前文件/运行身份、允许修改范围、已知输入与接口、来源和待解决问题。主模块与相关模块可以多次互相调用，不是互斥入口。

工程判断先读下列原理层；形成独立判断后才读案例。共享原理/案例仍通过 [多对多对应表](../../references/principle-case-map.md) 复用，不复制为各模块专属参数库。

## 原理、案例与工艺接口

**适用任务**：SM/EO、Tear/Broyden、缩放、Calculator/DS、Sensitivity/拟合、.his、冷启动和数据调和。

**原理层（先读）**：[textbook-numerics-economics-and-custom-models.md](../../references/textbook-numerics-economics-and-custom-models.md) 的 M08-K01–K07。落地细节按需查 `run-verification-and-reconcile.md、aspen-input-completeness-and-delivery-lessons.md、calculator-flowsheeting-options.md`。

**教材消化判断**：[R28–R32：有效规格、变量所有权、残差与可辨识性](../../references/sun-lanyi-case-derived-reasoning.md#m08)。

**专项判断**：灵敏度比较时的控制约束、最终日志身份与失败点处理见[保密项目通用经验](../../references/kinetics-recycle-and-delivery-reasoning.md#m08)。

**修复核验**：断流后收敛拓扑与压力闭合见[物性与流程修复关口](../../references/property-provenance-and-repair-gates.md#m08)。

**收敛设置核验**：Custom的适用条件、输入/实际容差差异、独立重开与初值稳健性边界见[收敛、分离模型与节能验证](../../references/convergence-separation-and-energy-integrity.md)第1–4节。

**案例层（后读）**：[对应表](../../references/principle-case-map.md) 中 C02/C04/C06/C08/C10/C12/C19。

**输出与接口**：自由度/残差、相正确初值、有效候选、诊断与最终验收、独立新开及哈希。服务所有工艺章节，不能以数值收敛代替物理可行。

## 与其他模块贯通

可直接联调：[M01](M01-properties-and-boundaries.md)、[M02](M02-distillation.md)、[M03](M03-reactors.md)、[M06](M06-thermal-coupling.md)、[M09](M09-execution-interfaces.md)、[M14](M14-optimization-custom.md)、[M15](M15-troubleshooting.md)。把跨模块流股的组成、流量、相态、T/P、焓/热量、单位基准、变量所有权及未验证项一起传递；接口改变后通知所有受影响模块复算。

本模块发现报错、异常结果、物理不合理或输入完整性问题时进入 [M15](M15-troubleshooting.md)，M15诊断后仍可返回本模块。建模过程中无需等到输出阶段才允许排错。

## 返回与输出接口

返回 [运行模块](index.md) 的是当前输入、实际执行/回读证据、模型决定、原理与案例引用、接口变更和残留问题；候选结果统一进入 [输出模块](../output/index.md)。不得在本模块单独跳过检查交付。检查退回时按问题清单修复并刷新受影响证据。
