# M05 传热、蒸发、热集成与公用工程

## 模块输入与调用范围

接收 [运行模块](index.md) 的任务记录：用户目标、当前文件/运行身份、允许修改范围、已知输入与接口、来源和待解决问题。主模块与相关模块可以多次互相调用，不是互斥入口。

工程判断先读下列原理层；形成独立判断后才读案例。共享原理/案例仍通过 [多对多对应表](../../references/principle-case-map.md) 复用，不复制为各模块专属参数库。

## 原理、案例与工艺接口

**适用任务**：导热/对流/辐射、HeatX、U/LMTD/NTU/EDR、单多效蒸发、夹点/HEN、蒸汽动力/全厂公用工程。

**原理层（先读）**：[textbook-heat-and-energy.md](../../references/textbook-heat-and-energy.md) 的 M05-K01–K15。落地细节按需查 `heat-carrier-and-salt-properties.md、equipment-hydraulics-and-rating.md`。

**教材消化判断**：[R20–R23：设计/校核、温位、多效及内部夹紧](../../references/sun-lanyi-case-derived-reasoning.md#m05)。

**专项判断**：换热设计模式与固定设备校核、热电比较边界见[保密项目通用经验](../../references/kinetics-recycle-and-delivery-reasoning.md#m05)。

**案例层（后读）**：[对应表](../../references/principle-case-map.md) 中 C05/C08/C09/C10/C14/C19。

**输出与接口**：热量/温位、壁温与相变边界、面积/压损、蒸发浓缩、热级联/网络及蒸汽供需。压力连M04，热泵连M06，评级连M07，经济目标连M14。

## 与其他模块贯通

可直接联调：[M01](M01-properties-and-boundaries.md)、[M02](M02-distillation.md)、[M03](M03-reactors.md)、[M04](M04-pressure-transport.md)、[M06](M06-thermal-coupling.md)、[M07](M07-hydraulics-rating.md)、[M14](M14-optimization-custom.md)、[M15](M15-troubleshooting.md)。把跨模块流股的组成、流量、相态、T/P、焓/热量、单位基准、变量所有权及未验证项一起传递；接口改变后通知所有受影响模块复算。

本模块发现报错、异常结果、物理不合理或输入完整性问题时进入 [M15](M15-troubleshooting.md)，M15诊断后仍可返回本模块。建模过程中无需等到输出阶段才允许排错。

## 返回与输出接口

返回 [运行模块](index.md) 的是当前输入、实际执行/回读证据、模型决定、原理与案例引用、接口变更和残留问题；候选结果统一进入 [输出模块](../output/index.md)。不得在本模块单独跳过检查交付。检查退回时按问题清单修复并刷新受影响证据。
