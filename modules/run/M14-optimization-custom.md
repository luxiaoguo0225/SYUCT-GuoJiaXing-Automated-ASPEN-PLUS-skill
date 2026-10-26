# M14 经济优化、自定义、ROM与批量

## 模块输入与调用范围

接收 [运行模块](index.md) 的任务记录：用户目标、当前文件/运行身份、允许修改范围、已知输入与接口、来源和待解决问题。主模块与相关模块可以多次互相调用，不是互斥入口。

工程判断先读下列原理层；形成独立判断后才读案例。共享原理/案例仍通过 [多对多对应表](../../references/principle-case-map.md) 复用，不复制为各模块专属参数库。

## 原理、案例与工艺接口

**适用任务**：资本/OPEX/TAC、约束/离散优化、用户块/外控、ROM/训练域、批量并行与失败隔离。

**原理层（先读）**：[textbook-numerics-economics-and-custom-models.md](../../references/textbook-numerics-economics-and-custom-models.md) 的 M14-K01–K06。落地细节按需查 `general-verification-methods.md`。

**教材消化判断**：[R42：目标函数和优化结论的口径](../../references/sun-lanyi-case-derived-reasoning.md#m14)。

**专项判断**：部分可变费用、情景分析与完整经济结论的边界见[保密项目通用经验](../../references/kinetics-recycle-and-delivery-reasoning.md#m14)。

**反应器条件寻优**：原生扫描的目标、固定量、网格细化、平峰精度和单点保留见 [RPlug 灵敏度方法](../../references/rplug-native-sensitivity-method.md)；工艺有效性与 M03 联调，不将单变量峰值当作联合或经济最优。

**案例层（后读）**：[对应表](../../references/principle-case-map.md) 中 C19/C14/C22；设备验证需另建独立基准。

**输出与接口**：方程/端口/自由度、价格/基年/边界、可行域、独立验证和完整模型复核；按用户目标使用，不因普通精馏自动扩大为经济优化。

## 与其他模块贯通

可直接联调：[M03](M03-reactors.md)、[M01](M01-properties-and-boundaries.md)、[M05](M05-heat-and-energy.md)、[M08](M08-numerics.md)、[M09](M09-execution-interfaces.md)、[M11](M11-mass-transfer.md)、[M15](M15-troubleshooting.md)。把跨模块流股的组成、流量、相态、T/P、焓/热量、单位基准、变量所有权及未验证项一起传递；接口改变后通知所有受影响模块复算。

本模块发现报错、异常结果、物理不合理或输入完整性问题时进入 [M15](M15-troubleshooting.md)，M15诊断后仍可返回本模块。建模过程中无需等到输出阶段才允许排错。

## 返回与输出接口

返回 [运行模块](index.md) 的是当前输入、实际执行/回读证据、模型决定、原理与案例引用、接口变更和残留问题；候选结果统一进入 [输出模块](../output/index.md)。不得在本模块单独跳过检查交付。检查退回时按问题清单修复并刷新受影响证据。
