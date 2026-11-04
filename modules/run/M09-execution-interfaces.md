# M09 COM、MCP、输入文件与PFD机制

## 模块输入与调用范围

接收 [P00物性前置轨道](../properties/index.md)、[流程运行模块](index.md)或I01纯读取辅助动作的任务记录：用户目标、当前文件/运行身份、允许修改范围、已知输入与接口、来源和待解决问题。主模块与相关模块可以多次互相调用，不是互斥入口。

工程判断先读下列原理层；形成独立判断后才读案例。共享原理/案例仍通过 [多对多对应表](../../references/principle-case-map.md) 复用，不复制为各模块专属参数库。

## 原理、案例与工艺接口

**适用任务**：Apwn.Document、树路径/单位、许可、导入导出、输入完整、文件交付与复现。

**原理层（先读）**：[textbook-numerics-economics-and-custom-models.md](../../references/textbook-numerics-economics-and-custom-models.md) 的 M09-K01。落地细节按需查 `general-modeling-mechanics.md、variables-and-troubleshooting.md、com-attach-and-license-env.md`。

**教材消化判断**：[R33–R34：激活状态、单位和计算分支](../../references/sun-lanyi-case-derived-reasoning.md#m09)。

**专项判断**：编辑图表、数值表、冷启动证据和交付包的一致性见[保密项目通用经验](../../references/kinetics-recycle-and-delivery-reasoning.md#m09)。

**修复核验**：用户另存文件的范围、来源绑定与新运行证据见[物性与流程修复关口](../../references/property-provenance-and-repair-gates.md#m09)。

**原生 Sensitivity 实现**：[RPlug 专项](../../references/rplug-native-sensitivity-method.md#6-结果到交付的检查)说明基准插入、真实表头、冻结文件冷重开及保留分析；跨版本、旧分析残留和日志落盘问题回 [M15专项](diagnostics/rplug-native-sensitivity-fixes.md)。

**案例层（后读）**：[对应表](../../references/principle-case-map.md) 中 C12/C19/C22/C23及scripts/aspen_plus_bridge.py。

**输出与接口**：接口/版本证据、可复现文件、冷启动及用户要求的PFD；新建无指定排布时采用Aspen默认，修复保留用户最新布局。接口层不决定工艺数值，只实现已经完成相应工程判断的输入；只读/导出不自动扩展为重建。

## 与其他模块贯通

可直接联调：[M01](M01-properties-and-boundaries.md)、[M08](M08-numerics.md)、[M14](M14-optimization-custom.md)、[M15](M15-troubleshooting.md)。把跨模块流股的组成、流量、相态、T/P、焓/热量、单位基准、变量所有权及未验证项一起传递；接口改变后通知所有受影响模块复算。

本模块发现报错、异常结果、物理不合理或输入完整性问题时进入 [M15](M15-troubleshooting.md)，M15诊断后仍可返回本模块。建模过程中无需等到输出阶段才允许排错。

## 返回与输出接口

返回 [运行模块](index.md) 的是当前输入、实际执行/回读证据、模型决定、原理与案例引用、接口变更和残留问题；候选结果统一进入 [输出模块](../output/index.md)。不得在本模块单独跳过检查交付。检查退回时按问题清单修复并刷新受影响证据。

## 流程执行前的硬性调用顺序

按[P00](../properties/index.md)保存并独立重开原生物性来源，生成真实当前回读快照。正式流程计算前调用check_process_gate.py确认PROCESS_READY。用户明确允许的[原生估算搭建与数值联算](../properties/index.md#native-estimate-diagnostic)按专节核对输入状态，在隔离副本用获准的接口执行。准入脚本验证证据和快照，科学适用性仍须核对。不得复制旧快照冒充当前状态。

通用aspen_plus_bridge.run及build_from_input入口要求property_gate_request；历史专用案例脚本调用前同样先过此准入。用户禁止Computer Use时仅用COM/MCP/原生文件等已授权通道，不以来源回读困难为由切换GUI自动化。

萃取精馏的NRTL数据库枚举节点、BDBANK与CID/VAL原生记录、展开INP及保存重开路径见[C23专项第4节](../../references/extractive-distillation-workflow.md#4-com与原生文件路径)；本机V14机制不自动适用于其他方法/版本，不把字段写入成功当有效来源绑定。

原生物性来源回读必须覆盖全部纯组分/二元/Henry/电解质等输入及覆盖；来源为USER、原生用户值标记或未知时不得执行依赖流程。INP导入导致来源退为USER也按失败处理，不以数值相同或setter成功豁免。
