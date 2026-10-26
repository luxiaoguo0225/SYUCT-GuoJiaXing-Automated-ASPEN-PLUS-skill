# I01 任务判断模块

## 入口原则

先判断任务的工作目标，不因出现某个设备名就直接进入一个工艺子模块。记录用户原话中的目标、文件、允许修改范围、禁止项、交付格式/内容/路径、图形要求、复算要求与验收阈值。缺省常规选择以有据假设完成，不把假设冒充用户要求。

## 两类主入口

| 主类型 | 判断依据 | 进入运行模块后的首次路由 |
|---|---|---|
| 搭建流程类 BUILD | 从要求新建/扩展流程、设计设备、建立物性/反应、扫描/优化或形成指定结果 | [R00](run/index.md) → 需求/物性M01 + 对应工艺子模块；实现时联动M08/M09 |
| 解决报错类 TROUBLESHOOT | 已有文件出现错误/警告、输入不完整、数值或物理异常、结果不一致、接口/保存/显示失败 | [R00](run/index.md) → 同级[M15](run/M15-troubleshooting.md)，由症状和证据再联调实际工艺模块 |

混合任务必须记录两个目标；例如“搭建严格塔并修复循环报错”，先确定实际依赖，BUILD和TROUBLESHOOT可交替发生。搭建任务中发现问题立即转M15，修复任务需要重建某工段时进入对应工艺模块，不重新询问已经明确的目标。

纯读取、导出、解释、验收或原有文件作图属于辅助动作，记录 `action`，不强行当作新流程设计。仍通过R00的M09或所需工艺模块，再进入输出/检查；无需无关的全流程重建。

## 输入合同

任务记录至少包含：task_id、primary_type、action、用户目标/约束、原件及哈希、交付清单requirements（每项唯一id、目标/格式/阈值和验收办法）、required_checks、主/相关模块、未知项与假设。要求只能因用户改变而更新，不能为取得检查通过而删项。

## 原理与案例

原理依据为[M01-K01任务边界/设计与校核](../references/textbook-properties-and-boundaries.md)和[M08/M09的执行与验收层次](../references/textbook-numerics-economics-and-custom-models.md)。分类服务于用户目标与修改范围，不能由一个错误码或设备名称替代完整问题判断。

形成判断后可参考[C04严格塔](../references/principle-case-map.md#c04)区分基础搭建与严格计算/扫描范围，[C12输入/Calculator](../references/principle-case-map.md#c12)区分接口/格式修复与工艺重建，[C08双效](../references/principle-case-map.md#c08)理解搭建和报错修复会交替。它们仍被多个M模块引用，不成为I01专属案例。

参考[共享建模约束](shared/modeling-contract.md)。任务判断完成后统一进入[运行模块](run/index.md)，不能直接宣称交付通过。

## 即时检查范围

实际模型任务在最终合同标记validation_stage=final，并登记validation_stages_required：使用/修改物性记录properties，使用/修改动力学记录properties与kinetics。旧模型先核现有证据，无有效证据就在依赖操作前补查。纯读取/解释或无反应模型按范围裁剪，不因失败删阶段。

每个适用阶段在最终required_checks中列EARLY-PROPERTIES/EARLY-KINETICS review项，不允许allow_na。阶段合同单独标记properties/kinetics，通过只CONTINUE；失败RUN；只有最终完整检查才能DELIVER。指标定义、可比条件和有据阈值在比较前冻结。无需agent id、隔离声明或另一智能体判定。
