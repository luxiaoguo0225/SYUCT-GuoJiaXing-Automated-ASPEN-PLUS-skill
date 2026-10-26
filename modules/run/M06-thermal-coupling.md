# M06 热泵、多效与热耦合

## 模块输入与调用范围

接收 [运行模块](index.md) 的任务记录：用户目标、当前文件/运行身份、允许修改范围、已知输入与接口、来源和待解决问题。主模块与相关模块可以多次互相调用，不是互斥入口。

工程判断先读下列原理层；形成独立判断后才读案例。共享原理/案例仍通过 [多对多对应表](../../references/principle-case-map.md) 复用，不复制为各模块专属参数库。

## 原理、案例与工艺接口

**适用任务**：蒸汽再压缩、差压耦合、Petlyuk/DWC、多效精馏/蒸发、COP与能源品位。

**原理层（先读）**：[textbook-distillation-and-towers.md](../../references/textbook-distillation-and-towers.md) 的 M06-K01–K02，并读[传热与能源](../../references/textbook-heat-and-energy.md)的M06-K03。落地细节按需查 `general-verification-methods.md、heat-carrier-and-salt-properties.md`。

**教材消化判断**：[R24–R26：同产品基准、四股耦合及逐板传热闭合](../../references/sun-lanyi-case-derived-reasoning.md#m06)。

**专项判断**：串联/并联的物料拓扑、双效与MVR的独立热量贡献及同边界比较见[收敛、分离模型与节能验证](../../references/convergence-separation-and-energy-integrity.md)第5–6节。

**案例层（后读）**：[对应表](../../references/principle-case-map.md) 中 C05/C06/C07/C08/C10/C14。

**输出与接口**：真实液汽连接、温差/热量/压力可行性、同产品基准热电比较；压缩比、节能率和串并联由当前任务决定。联读M02/M04/M05/M07/M08。

## 与其他模块贯通

可直接联调：[M01](M01-properties-and-boundaries.md)、[M02](M02-distillation.md)、[M04](M04-pressure-transport.md)、[M05](M05-heat-and-energy.md)、[M07](M07-hydraulics-rating.md)、[M08](M08-numerics.md)、[M14](M14-optimization-custom.md)、[M15](M15-troubleshooting.md)。把跨模块流股的组成、流量、相态、T/P、焓/热量、单位基准、变量所有权及未验证项一起传递；接口改变后通知所有受影响模块复算。

本模块发现报错、异常结果、物理不合理或输入完整性问题时进入 [M15](M15-troubleshooting.md)，M15诊断后仍可返回本模块。建模过程中无需等到输出阶段才允许排错。

## 返回与输出接口

返回 [运行模块](index.md) 的是当前输入、实际执行/回读证据、模型决定、原理与案例引用、接口变更和残留问题；候选结果统一进入 [输出模块](../output/index.md)。不得在本模块单独跳过检查交付。检查退回时按问题清单修复并刷新受影响证据。
