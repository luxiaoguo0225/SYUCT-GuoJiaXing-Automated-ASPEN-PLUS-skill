# M15 报错诊断与修复

与M01物性、M02精馏、M03反应器等同级，由[R00](index.md)调用；既承接报错类任务，也承接搭建过程异常和[O02检查退回](../output/check.md)。M08负责数值模型/循环/DS的原理与实现，M15组织跨原因诊断，不能把所有错误都归为收敛问题。

## 输入与取证

接收用户目标/约束、原件与最新PFD、活动/禁用对象、出错动作、本次run_id/日志、有效输入/设置/来源和检查问题清单。先只读留存事实，在副本中诊断；错误码和症状是线索，不能直接当根因。旧日志、旧结果和接口成功回显不能替代新运行证据。

## 原理层

| 原理ID | 判断与独立检查 | 共享原理来源 |
|---|---|---|
| M15-K01 | 先区分接口/输入翻译、物性与相数、规格/自由度、数值迭代、物理异常和交付问题；按实际执行链定位最早有效故障 | [M08-K01/K07、M09-K01](../../references/textbook-numerics-economics-and-custom-models.md) |
| M15-K02 | 物性来源、方程/方向、单位、温区与VLE/LLE/VLLE核查；参数零值不自动等于缺失，缺参也不能靠收敛修复 | [M01-K04–K08](../../references/textbook-properties-and-boundaries.md) |
| M15-K03 | 规格语义、独立自由度、变量所有权、压力闭合和真实压头；DS诊断扫描成对处理Spec/Vary | [M02-K04](../../references/textbook-distillation-and-towers.md)、[M04](../../references/textbook-fluid-transport.md)、[M08](../../references/textbook-numerics-economics-and-custom-models.md) |
| M15-K04 | 先查相正确初值、撕裂拓扑、缩放/残差及多根风险，再选择有依据数值策略；容差只保持/收紧且核实际判据 | [M08-K01–K04/K07](../../references/textbook-numerics-economics-and-custom-models.md)、[真实性边界](../../references/convergence-separation-and-energy-integrity.md) |
| M15-K05 | 反应基准、量纲、相态和焓/传热路径的独立检查；异常温度/负荷不能只靠手调规格掩盖 | [M03](../../references/textbook-reaction-engineering.md)、[M05](../../references/textbook-heat-and-energy.md) |
| M15-K06 | 核节点/容器/标量、实际单位、COM线程与会话身份、许可与文件格式；生成缓存错误不自动等于模型或许可失败 | [M09-K01](../../references/textbook-numerics-economics-and-custom-models.md)及下列本机机制资料 |
| M15-K07 | 修复要证明根因改变、原故障消失且未损坏相邻模块；新目录新COM复算和独立衡算，保留明示初值边界 | [M01-K02/K03](../../references/textbook-properties-and-boundaries.md)、[M08-K07](../../references/textbook-numerics-economics-and-custom-models.md) |
| M15-K08 | 交付文件/报告/PFD/图表必须来自同一最终输入和运行；有文件或XML定义不等于用户可见/有效 | [M09-K01](../../references/textbook-numerics-economics-and-custom-models.md)、[输出检查](../output/check.md) |

这些K条目是已有原理与本机经验的诊断组织，不冒充新增教材式号或全错误码运行认证。具体公式仍回原教材/权威技术资料核对。

## 诊断分派与跨模块调用

| 现象 | 首要区分 | 联动模块 |
|---|---|---|
| 未执行、输入不完整、2041/文件打不开 | 入口文件/运行类别、实际解析对象、输入规格、格式/许可/接口，不把所有2041归为同一原因 | [M09](M09-execution-interfaces.md)、[M08](M08-numerics.md)、实际设备模块 |
| 干净收敛但相态、溶解量、温度/热量异常 | 物性/相数、来源/温区、焓基准、单位或错误规格 | [M01](M01-properties-and-boundaries.md)、[M02](M02-distillation.md)、[M03](M03-reactors.md)、[M05](M05-heat-and-energy.md)、[M11](M11-mass-transfer.md) |
| 塔干板、相平衡/组分不闭合、循环不收敛 | 物性/压力/自由度先于算法，气液初值和撕裂拓扑；Reconcile只是特定初始化工具 | [M01](M01-properties-and-boundaries.md)、[M02](M02-distillation.md)、[M04](M04-pressure-transport.md)、[M08](M08-numerics.md) |
| 交叉温差、压缩机/热泵异常 | 全换热路径温位与相态、压比和温敏限制、压降及实际压头 | [M04](M04-pressure-transport.md)、[M05](M05-heat-and-energy.md)、[M06](M06-thermal-coupling.md)、[M07](M07-hydraulics-rating.md) |
| 反应转换/选择性/热量异常 | 反应身份、速率单位/基准、方程映射、传递及热路径 | [M03](M03-reactors.md)、[M01](M01-properties-and-boundaries.md)、[M05](M05-heat-and-energy.md)、[M10](M10-solids.md) |
| 保存重开失败、结果/来源丢失、图形不可见 | 文件字节/来源绑定、外部依赖、实际重开运行与用户可见结果分开检查 | [M09](M09-execution-interfaces.md)、[输出检查](../output/check.md) |

## 案例层：原理完成后读取

| 案例 | 对应原理 | 可借鉴与边界 |
|---|---|---|
| [C02](../../references/principle-case-map.md#c02) 含水芳烃 | K02/K03/K04/K07 | 三相与循环接口；物性组合不能通用 |
| [C03](../../references/principle-case-map.md#c03) 动力学 | K05/K07 | 速率与单位独立对照；常数限原体系 |
| [C04](../../references/principle-case-map.md#c04) 严格塔 | K03/K04/K07 | 规格/扫描/失败点；不继承最佳点 |
| [C06](../../references/principle-case-map.md#c06)、[C08](../../references/principle-case-map.md#c08) 热耦/双效 | K01/K03/K04/K07 | 迭代初值与隐藏故障；不是通用根因或能耗承诺 |
| [C09](../../references/principle-case-map.md#c09)、[C10](../../references/principle-case-map.md#c10) 载热/PDO | K02/K05/K07/K08 | 物性/单位/温位与子系统边界；未解决项继续保持U |
| [C12](../../references/principle-case-map.md#c12) 输入/Calculator | K01/K03/K06/K08 | 原生格式、激活状态、执行次序和文件身份；不能凑SEP分离结果 |
| [C19](../../references/principle-case-map.md#c19) 接口与批量 | K06/K07 | 接口和故障隔离；不证明所有专用模型可用 |

一条K关联多个C，一个C被M15及其他工艺模块共同引用；双向关系统一在[对应表](../../references/principle-case-map.md)维护。

## 已迁入的诊断正文

- [aspen-input-completeness-and-delivery-lessons](diagnostics/aspen-input-completeness-and-delivery-lessons.md)
- [aspen-plus-textbook-guide-fixes](diagnostics/aspen-plus-textbook-guide-fixes.md)
- [calculator-flowsheeting-options-fixes](diagnostics/calculator-flowsheeting-options-fixes.md)
- [com-attach-and-license-env](diagnostics/com-attach-and-license-env.md)
- [double-effect-distillation-and-design-spec-fixes](diagnostics/double-effect-distillation-and-design-spec-fixes.md)
- [general-verification-methods](diagnostics/general-verification-methods.md)
- [heat-carrier-and-salt-properties-fixes](diagnostics/heat-carrier-and-salt-properties-fixes.md)
- [historical-lessons](diagnostics/historical-lessons.md)
- [initialization-and-coupling-cases](diagnostics/initialization-and-coupling-cases.md)
- [pdo-heat-integration-and-delivery-lessons-fixes](diagnostics/pdo-heat-integration-and-delivery-lessons-fixes.md)
- [property-provenance-and-repair-gates](diagnostics/property-provenance-and-repair-gates.md)
- [run-verification-and-reconcile](diagnostics/run-verification-and-reconcile.md)
- [thermally-coupled-distillation-fixes](diagnostics/thermally-coupled-distillation-fixes.md)
- [three-component-thermal-coupling-case-fixes](diagnostics/three-component-thermal-coupling-case-fixes.md)
- [variables-and-troubleshooting-fixes](diagnostics/variables-and-troubleshooting-fixes.md)

- [双效案例的验收与排错](diagnostics/double-effect-user-workflow-fixes.md)

- [pdo-heat-integration-and-delivery-lessons-additional-fixes](diagnostics/pdo-heat-integration-and-delivery-lessons-additional-fixes.md)
- [kinetics-recycle-and-delivery-reasoning-additional-fixes](diagnostics/kinetics-recycle-and-delivery-reasoning-additional-fixes.md)
- [column-splitting-and-heat-integration-additional-fixes](diagnostics/column-splitting-and-heat-integration-additional-fixes.md)

- [RPlug 原生灵敏度复做](diagnostics/rplug-native-sensitivity-fixes.md)：文档/存表不一致、数据库兼容、分析改名残留、文本定义缺失、日志落盘和归档误判；与 M03/M09/M14 联调。

## 修复—返回合同

每轮记录 issue_id → 观测事实 → 根因假设及排除证据 → 调用模块 → 修改前后值/单位/来源 → 新运行与残差 → 关联影响 → 未解决项。禁止只清日志、隐藏报警、改输出、禁用必要对象或放宽容差来宣称修复。

根因明确后联动相关模块修复，返回[R00](index.md)形成候选，再进入[O01](../output/index.md)和其[O02检查](../output/check.md)。同一案例根因不能替代当前诊断；同一问题重复出现先更新诊断，缺少必要数据/许可且无法独立推进时保留未通过结果和具体阻碍。

萃取精馏的缺源/零值、USER回退、范围外推、开环/闭环、补料积累及负荷异常按[C23诊断矩阵](diagnostics/extractive-distillation-fixes.md)分派；物性问题回P00，数值/设备问题经M02/M08及相关模块修复，不能由单塔收敛推断全厂完成。
