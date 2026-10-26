---
name: aspen-plus-automation
description: Automate and verify Aspen Plus on Windows through COM or available MCP tools. First classify flowsheet-building versus troubleshooting tasks, then use interconnected M01-M15 principle-and-case modules. Immediately check property sources after entry and kinetics against literature/industrial evidence after entry, then prepare output and check requirements; return failures to execution before delivery in one modular workflow. V14-tested mechanisms do not certify every model.
---
# Aspen Plus 自动化：任务 → 运行 → 输出与检查

## 1. 调用架构

本技能在同一会话内按任务、运行、输出与检查模块推进，不创建执行/验证子 agent，不要求私有记忆隔离或 agent 身份判定。独立复算指模型副本与新COM会话复现，不指另起智能体。

```mermaid
flowchart TD
  I[任务判断 I01] --> T{任务类型}
  T -->|搭建流程类| R[运行模块 R00]
  T -->|解决报错类| R
  R --> B[M01–M14 工艺及实现子模块：按需互调]
  R --> E[M15 报错诊断与修复：同级互通]
  B <--> E
  B --> S{本轮是否完成物性或动力学录入、变更？}
  E --> S
  S -->|物性录入或变更| P[P01 立即检查物性]
  S -->|动力学录入或变更| K[K01 立即检查动力学：先核有效物性]
  P -->|通过：CONTINUE继续本轮| R
  K -->|通过：CONTINUE继续本轮| R
  P -->|失败或缺证据：带问题回运行| R
  K -->|失败或缺证据：带问题回运行| R
  S -->|无待处理录入事件且已有候选| G{所有适用前置检查当前有效？}
  G -->|否：补查或修复后重查| R
  G -->|是，或I01已明确不适用| O[输出模块 O01：候选交付]
  O --> C{内部检查子模块 O02}
  C -->|不满足要求、报错或缺证据：问题清单| R
  C -->|全部必需项通过| D[最终交付]
```

1. 先读[I01任务判断](modules/intake.md)，区分搭建流程类、解决报错类；混合任务保留两个目标，纯读/导出等记录辅助动作。
2. 进入[R00运行模块](modules/run/index.md)。M01–M15同级，按问题和接口可多次联调，不限于一个模块。物性录入后立即调用[P01物性检查](modules/output/properties-validation.md)，动力学录入后立即调用[K01动力学检查](modules/output/kinetics-validation.md)；检查不通过返回运行，不等最终输出才检查。
3. 运行产生候选后进入[O01输出模块](modules/output/index.md)，按用户要求形成文件、图表、结果及说明。
4. O01必须调用内部[O02检查子模块](modules/output/check.md)。不符合用户要求、存在错误/警告、物理问题或缺少必需证据时，携问题清单回R00修复，再运行、再输出、再检查；不能直接跳过检查交付。

## 2. 运行子模块：同级、互通、原理加案例

| 模块 | 内容 |
|---|---|
| [M01](modules/run/M01-properties-and-boundaries.md) | 需求、物性与流程边界 |
| [M02](modules/run/M02-distillation.md) | 精馏塔与特殊精馏 |
| [M03](modules/run/M03-reactors.md) | 反应器、动力学与多相反应 |
| [M04](modules/run/M04-pressure-transport.md) | 压力输送与压力网络 |
| [M05](modules/run/M05-heat-and-energy.md) | 传热、蒸发、热集成与公用工程 |
| [M06](modules/run/M06-thermal-coupling.md) | 热泵、多效与热耦合 |
| [M07](modules/run/M07-hydraulics-rating.md) | 设备水力学与评级 |
| [M08](modules/run/M08-numerics.md) | 循环、Design Spec、收敛与验证 |
| [M09](modules/run/M09-execution-interfaces.md) | COM、MCP、输入文件与PFD机制 |
| [M10](modules/run/M10-solids.md) | 颗粒分离、固体床与流态化 |
| [M11](modules/run/M11-mass-transfer.md) | 吸收、萃取、干燥、结晶与膜 |
| [M12](modules/run/M12-special-materials.md) | 石油、非常规固体与聚合物 |
| [M13](modules/run/M13-dynamics-batch.md) | 动态、控制、开车与批次 |
| [M14](modules/run/M14-optimization-custom.md) | 经济优化、自定义、ROM与批量 |
| [M15](modules/run/M15-troubleshooting.md) | 报错诊断与修复 |

模块之间不是固定串行顺序；可直接调用登记的相关模块，也可经R00跨模块调度。P01/K01只是依赖使用前的检查点，不改变M01–M15同级互通关系。

每个子模块保留输入、原理层、案例层、跨模块接口和输出/返回要求。先读当前相关教材K条目，独立形成方案/根因判断，再查案例机制。一个原理可以关联多个案例，一个案例可被多个原理和模块共同调用，关系见[原理—案例双向表](references/principle-case-map.md)。无案例不阻止有据建模；不为套案例改题目。

RPlug 参数优化或仅限原生 Sensitivity 的复做，按需读 [专项方法](references/rplug-native-sensitivity-method.md)，并通过 M03/M14 与 M09/M15 联调；此专项不替代其他任务的工具与目标选择。

共享教材/案例保留单一正文，各模块引用；专门排错文档和混合文档中的修复章节归入M15，原位置只保留跳转。全部资料的主要归属及共享用途见[内容归属表](references/content-ownership.md)。

## 3. 全流程不变量

- 用户目标、禁止项、验收阈值、交付内容和最新PFD优先；用户给定目标不是物理可行证据。新建用原生默认排布，修复保留用户现有排布与真实端口/连线。
- 原理、公式、物性、动力学、单位和参数必须可溯源；文献事实、推导、假设、拟合及未核验外推分别记录。[共享约束](modules/shared/modeling-contract.md)、[教材来源](references/textbook-source-coverage.md)。
- 不得放宽求解或验收容差，必须核实际生效值；Custom/OTHERS仅在当前允许范围内、有数值诊断和复算支持时使用。不得用SEP人为组分分配、自定义模块或写入结果凑分离指标。[诚信边界](references/convergence-separation-and-energy-integrity.md)。
- 精馏搭塔前先物性核验与[相图分析](references/phase-diagram-before-distillation.md)；关键物性、压力或溶剂改变后重核相关判断。属性换库与修复通过M01/M15互通处理。
- 编辑和验证在副本中进行，不在交付目录初始化；保留原件和交付字节。只关闭本次拥有的COM会话，不影响用户/未知实例。接口、版本、许可和专用模块能力按本机核验。
- COM与MCP共用同一原理和验收；常用操作可用已核验MCP，复杂审计/批量/冷重开可用COM，接口成功不等于模型有效。细节由M09管理，不擅自重配环境。
- 数值收敛、物性有效、独立复现、水力/设备评级、图形可见和包完整分开验收。日志/Control Panel仍需零Severe/Error/Warning；缺证据不能通过。
- 保密项目只沉淀通用判断与边界，不加入原始参数、具体拓扑、模型、数据、路径、日志或其编码副本。

## 4. 执行与交付记录

I01冻结用户要求和必需检查；R00每轮记录实际调用模块、原理/案例、输入/设置、run_id和结果证据；O01形成当前候选；O02检查并输出DELIVER或返回RUN的问题清单。修复导致输入/接口变化时使关联旧证据失效，重新取证。

遇到同一原因不要无依据反复运行，先更新诊断。确实缺少外部数据/许可/权限或目标物理不可行时，完成可独立推进部分并报告未通过要求和证据，不能删要求或改门槛；这是明确的未完成边界，不是默认验收通过。

原有K/C编号、来源覆盖与案例证据等级保留；本次内容重组不声称重新运行所有案例。机器可读结构见[registry.json](modules/registry.json)，维护后执行`scripts/validate_modular_skill.py`和相关离线回归。
