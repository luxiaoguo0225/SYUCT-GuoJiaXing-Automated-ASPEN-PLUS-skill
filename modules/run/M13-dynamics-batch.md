# M13 动态、控制、开车与批次

## 模块输入与调用范围

接收 [运行模块](index.md) 的任务记录：用户目标、当前文件/运行身份、允许修改范围、已知输入与接口、来源和待解决问题。主模块与相关模块可以多次互相调用，不是互斥入口。

工程判断先读下列原理层；形成独立判断后才读案例。共享原理/案例仍通过 [多对多对应表](../../references/principle-case-map.md) 复用，不复制为各模块专属参数库。

## 原理、案例与工艺接口

**适用任务**：库存/ODE/DAE、压力驱动、PID、储槽/非等温CSTR、塔/深冷开车、裂解周期、BatchOp/BatchSep。

**原理层（先读）**：[textbook-special-materials-and-dynamics.md](../../references/textbook-special-materials-and-dynamics.md) 的 M13-K01–K08。落地细节按需查 `aspen-plus-textbook-guide.md`。

**教材消化判断**：[R39–R41：压力驱动、操纵机理与动态验收](../../references/sun-lanyi-case-derived-reasoning.md#m13)。

**案例层（后读）**：[对应表](../../references/principle-case-map.md) 中 C18；当前仅教材示例入口，不能声称所有动态功能已验证。

**输出与接口**：初始库存/控制与事件、时间轨迹/累计衡算、峰值与可操作性、本机许可/接口。稳态COM不能替代Dynamics；联读实际设备章节。

## 与其他模块贯通

可直接联调：[M01](M01-properties-and-boundaries.md)、[M02](M02-distillation.md)、[M03](M03-reactors.md)、[M04](M04-pressure-transport.md)、[M05](M05-heat-and-energy.md)、[M08](M08-numerics.md)、[M09](M09-execution-interfaces.md)、[M15](M15-troubleshooting.md)。把跨模块流股的组成、流量、相态、T/P、焓/热量、单位基准、变量所有权及未验证项一起传递；接口改变后通知所有受影响模块复算。

本模块发现报错、异常结果、物理不合理或输入完整性问题时进入 [M15](M15-troubleshooting.md)，M15诊断后仍可返回本模块。建模过程中无需等到输出阶段才允许排错。

## 返回与输出接口

返回 [运行模块](index.md) 的是当前输入、实际执行/回读证据、模型决定、原理与案例引用、接口变更和残留问题；候选结果统一进入 [输出模块](../output/index.md)。不得在本模块单独跳过检查交付。检查退回时按问题清单修复并刷新受影响证据。
