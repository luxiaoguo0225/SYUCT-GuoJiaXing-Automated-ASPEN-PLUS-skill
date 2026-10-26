# M03 反应器、动力学与多相反应

## 模块输入与调用范围

接收 [运行模块](index.md) 的任务记录：用户目标、当前文件/运行身份、允许修改范围、已知输入与接口、来源和待解决问题。主模块与相关模块可以多次互相调用，不是互斥入口。

工程判断先读下列原理层；形成独立判断后才读案例。共享原理/案例仍通过 [多对多对应表](../../references/principle-case-map.md) 复用，不复制为各模块专属参数库。

## 原理、案例与工艺接口

**适用任务**：计量/平衡/速率、间歇/CSTR/PFR、RTD、催化内外传递、固定/流化床、气液/流固/三相反应。

**原理层（先读）**：[textbook-reaction-engineering.md](../../references/textbook-reaction-engineering.md) 的 M03-K01–K17。落地细节按需查 `kinetic-reactor-input-workflow-320-322.md、general-modeling-mechanics.md、input-file-and-rstoic.md`。

**教材消化判断**：[R12–R17：实际反应类型、速率单位、热路径及用户实现](../../references/sun-lanyi-case-derived-reasoning.md#m03)。

**专项判断**：固定配比的参数可辨识性、循环净反应指标和独立积分的验证边界见[保密项目通用经验](../../references/kinetics-recycle-and-delivery-reasoning.md#m03)。

**原生灵敏度专项**：复做参数优化或用户限定只用 Sensitivity 时，读 [RPlug 参数扫描与交付方法](../../references/rplug-native-sensitivity-method.md)；它将入口边界、体积/催化基准、净指标和条件最优连到 M04/M05/M08/M09/M14，发现问题返回 M15。

**案例层（后读）**：[对应表](../../references/principle-case-map.md) 中 C01/C03/C09/C15/C16/C18/C21/C22。

**输出与接口**：反应集/速率基准、单位验证、尺寸/选择性、传递限制、热点和验证证据。反应热连M05，压损连M04，收敛连M08，固体连M10/M12。

## 与其他模块贯通

可直接联调：[M01](M01-properties-and-boundaries.md)、[M04](M04-pressure-transport.md)、[M05](M05-heat-and-energy.md)、[M08](M08-numerics.md)、[M10](M10-solids.md)、[M11](M11-mass-transfer.md)、[M12](M12-special-materials.md)、[M14](M14-optimization-custom.md)、[M15](M15-troubleshooting.md)。把跨模块流股的组成、流量、相态、T/P、焓/热量、单位基准、变量所有权及未验证项一起传递；接口改变后通知所有受影响模块复算。

本模块发现报错、异常结果、物理不合理或输入完整性问题时进入 [M15](M15-troubleshooting.md)，M15诊断后仍可返回本模块。建模过程中无需等到输出阶段才允许排错。

## 返回与输出接口

返回 [运行模块](index.md) 的是当前输入、实际执行/回读证据、模型决定、原理与案例引用、接口变更和残留问题；候选结果统一进入 [输出模块](../output/index.md)。不得在本模块单独跳过检查交付。检查退回时按问题清单修复并刷新受影响证据。

## 动力学录入后立即检查

动力学录入/修改后立即调用[K01动力学检查](../output/kinetics-validation.md)。物性检查有效后，以独立反应器副本对照原始文献和可比工业数据核速率、转化率和选择性；核单位、催化基准和副反应。单主反应的结构性100%选择性不能充当工业证据。失败先修实现或选择有据适用的模型，再录入、再检查，不能规定结果或任意调参凑指标。
