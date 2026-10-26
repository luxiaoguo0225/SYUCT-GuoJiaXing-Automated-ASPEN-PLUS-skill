# M11 吸收、萃取、干燥、结晶与膜

## 模块输入与调用范围

接收 [运行模块](index.md) 的任务记录：用户目标、当前文件/运行身份、允许修改范围、已知输入与接口、来源和待解决问题。主模块与相关模块可以多次互相调用，不是互斥入口。

工程判断先读下列原理层；形成独立判断后才读案例。共享原理/案例仍通过 [多对多对应表](../../references/principle-case-map.md) 复用，不复制为各模块专属参数库。

## 原理、案例与工艺接口

**适用任务**：两膜/扩散/Henry、吸收/汽提、反应吸收、LLE、湿空气/干燥速率、过饱和/晶体PSD、膜。

**原理层（先读）**：[textbook-solids-and-mass-transfer.md](../../references/textbook-solids-and-mass-transfer.md) 的 M11-K01–K12。落地细节按需查 `general-modeling-mechanics.md、aspen-plus-textbook-guide.md`。

**教材消化判断**：[R35–R36：Henry/LLE、净回收与电解质口径](../../references/sun-lanyi-case-derived-reasoning.md#m11)。

**案例层（后读）**：[对应表](../../references/principle-case-map.md) 中 C13/C15/C16；膜暂无本机案例，C19仅参考自定义机制。

**输出与接口**：驱动力、平衡/速率、溶剂/气量/面积、再生/母液/产品指标与数据缺口。电解质连M01，反应连M03，热量连M05，粒子连M10，自定义连M14。

## 与其他模块贯通

可直接联调：[M01](M01-properties-and-boundaries.md)、[M03](M03-reactors.md)、[M05](M05-heat-and-energy.md)、[M07](M07-hydraulics-rating.md)、[M10](M10-solids.md)、[M14](M14-optimization-custom.md)、[M15](M15-troubleshooting.md)。把跨模块流股的组成、流量、相态、T/P、焓/热量、单位基准、变量所有权及未验证项一起传递；接口改变后通知所有受影响模块复算。

本模块发现报错、异常结果、物理不合理或输入完整性问题时进入 [M15](M15-troubleshooting.md)，M15诊断后仍可返回本模块。建模过程中无需等到输出阶段才允许排错。

## 返回与输出接口

返回 [运行模块](index.md) 的是当前输入、实际执行/回读证据、模型决定、原理与案例引用、接口变更和残留问题；候选结果统一进入 [输出模块](../output/index.md)。不得在本模块单独跳过检查交付。检查退回时按问题清单修复并刷新受影响证据。
