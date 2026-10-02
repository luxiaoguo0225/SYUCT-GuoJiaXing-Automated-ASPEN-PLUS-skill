# 第一性原理卡片（Aspen Plus 模块入口）

本文件把 `SKILL.md` M01-M14 的原理层压缩成可执行的判断卡片。它不是教材替代品，也不是案例参数表。每张卡片都回答六个问题：

1. 原理是什么；
2. 依据哪份教材提炼文档；
3. 什么条件下适用；
4. 在 Aspen 中落到哪里；
5. 用什么案例或独立基准验证；
6. 什么时候必须停下来回到原始资料。

## 完整教材原理入口（本文件20张卡只作概览）

执行任务时必须接着读取主节/相关节的专题K条目并留下工程判断，不能读完概览就直接抄案例。来源章页和阅读证据见 [覆盖表](textbook-source-coverage.md)；判断后读取 [原理—案例对应](principle-case-map.md)。

| SKILL章节 | 教材专题正文 |
|---|---|
| M01-P01/P02 | [物性与边界](textbook-properties-and-boundaries.md)，M01-K01–K10 |
| M02-P01/P02/P03、M06-P01/P02、M07-P01/P02 | [精馏和塔器](textbook-distillation-and-towers.md)，M02-K01–K10、M06-K01–K02、M07-K01–K02 |
| M03-P01/P02/P03 | [反应工程](textbook-reaction-engineering.md)，M03-K01–K17 |
| M04-P01/P02 | [流体输送](textbook-fluid-transport.md)，M04-K01–K11 |
| M05-P01/P02、M06品位/COP | [传热与能源](textbook-heat-and-energy.md)，M05-K01–K15、M06-K03 |
| M08-P01/P02、M09-P01/P02、M14 | [数值/经济/自定义](textbook-numerics-economics-and-custom-models.md)，M08-K01–K07、M09-K01、M14-K01–K06 |
| M10/M11（新节） | [固体与传质操作](textbook-solids-and-mass-transfer.md)，M10-K01–K07、M11-K01–K12 |
| M12/M13（新节） | [特殊物料与动态](textbook-special-materials-and-dynamics.md)，M12-K01–K08、M13-K01–K08 |

## 使用规则

- 先按任务定位 M01-M14，概览后必须打开对应教材专题K条目；先判断后读案例。
- 卡片中的公式用于建立模型和检查量纲，不替代物性包、严格塔、详细评级或厂家数据。
- 任何经验数值必须标为假设或工程起点，并记录来源、适用条件和敏感性。
- Aspen 的节点名、单位和 API 以本机版本实测为准；卡片中的路径只是已验证的工作入口。

## M01 需求、物性与流程边界

### M01-P01 守恒与单位闭环

- **来源**：`engineering-modeling-basics.md` §Balances and Units；提炼自《化工原理》夏清/贾绍义。
- **适用条件**：所有稳态流程，尤其是新建流程、循环流程和有反应的流程。
- **核心关系**：总质量 `sum(in)=sum(out)`；反应体系按元素守恒；能量 `Q + sum(n*H)_in = sum(n*H)_out`。所有数值必须连同单位字符串解释。
- **Aspen 映射**：显式设置 `IN-UNITS/OUT-UNITS`；COM 读取 `Value` 时同时读取 `UnitString`；建模前列出流股、组件和能量基准。
- **验证**：每个模块做总量和组分/元素衡算；热负荷用 `Q=m*cp*dT` 或相变焓独立复核。
- **失效边界**：焓受到盐平衡或固体模型污染时，不能把异常焓直接用于绝热反算；应改用独立显热/潜热基准。

### M01-P02 物性方法由体系和工况决定

- **来源**：`aspen-plus-textbook-guide.md` §Property Method Selection；`general-modeling-mechanics.md` §2。
- **适用条件**：确定组分、极性/缔合、压力温度范围和是否存在水、固体或电解质之后。
- **核心判断**：非极性烃类/高压气体优先比较 `PENG-ROB/RK-SOAVE/SRK`；极性非理想液体优先比较 `NRTL/UNIQUAC/WILSON`；缺少二元参数时才考虑预测型方法，并记录不确定性。
- **Aspen 映射**：先建组件和属性方法，再设流股和单元；方法改变后先运行属性刷新，再检查 K 值、焓、密度、黏度和导热系数。
- **验证**：用已知泡点/露点、密度、焓或简单纯物质基准校准；对水/芳烃体系检查自由水、Henry 和三相闪蒸需求。
- **失效边界**：流程能收敛不等于物性方法正确；强非理想、缔合、电解质和固体析出不能由烃类状态方程默认外推。

## M02 精馏塔与其他分离

### M02-P01 相平衡是塔模型的边界条件

- **来源**：`engineering-modeling-basics.md` §Distillation and Absorption；`aspen-plus-textbook-guide.md` §Columns。
- **适用条件**：精馏、吸收、汽提和闪蒸中存在可定义的相平衡关系时。
- **核心关系**：平衡级要求气液组成与温度压力相容；`K_i` 由物性方法、组成、温度和压力共同决定。不要用固定相对挥发度代替强非理想体系的严格平衡。
- **Aspen 映射**：初步设计用 `DSTWU`；严格计算用 `RadFrac`；根据冷凝器、再沸器、进料相态和非凝气选择正确配置。
- **验证**：对关键级点检查泡点/露点和产品组成；产品纯度、回收率、塔负荷和物料衡算必须同时满足。
- **失效边界**：全回流、恒相对挥发度或平衡级假设不能直接代表真实效率、复杂三相体系或明显轴向压降。

### M02-P02 q 线、最小回流和理论板数

- **来源**：`tianjin-distillation-9-5-calculation.md` §3-§7；提炼自《化工原理》下册 9.5。
- **适用条件**：二元或可近似二元、连续、稳态、恒摩尔流的预设计阶段；严格塔仍需 Aspen 复核。
- **核心关系**：`q=(H_V-H_F)/(H_V-H_L)`；q 线 `y=q/(q-1)x-x_F/(q-1)`；夹紧点给出 `R_min`；Fenske 给 `N_min`；Gilliland 连接 `R/R_min` 与实际板数。改变 `q` 或 `R` 后必须重新找进料板。
- **Aspen 映射**：先用 `DSTWU` 得到可行基线，再把 `NSTAGE`、进料板、回流比和 Design Spec 传给 `RadFrac`；严格优化使用 `SNS_TAB`，不把 `1.1-2.0 R_min` 宣称为普适最优。
- **验证**：记录每个候选的 `T/P/VFRAC/q`、`R_min`、`R`、整数 `N/N_F`、`QREB/QCOND`、预热负荷、水力负荷和目标函数。
- **失效边界**：强非理想、多夹紧点、共沸、明显热集成或非恒摩尔流时，必须扫描全部有效夹紧点并回到严格模型。

### M02-P03 严格塔的自由度和压力剖面

- **来源**：`sun-lanyi-ch7-4-radfrac-strict.md`、`feed-stage-sensitivity-curves.md`、`engineering-modeling-basics.md` §Rigorous Distillation。
- **适用条件**：用户明确要求严格塔、最佳理论板/进料板/回流比、Sensitivity 或复杂塔结构时。
- **核心判断**：每个产品规格需要一个独立可调自由度；塔压、每级压降、冷凝器和再沸器类型必须与热力学和设备边界一致。
- **Aspen 映射**：先建可运行的基础 `RadFrac`，再逐步加入产品 `Design Spec + Vary`、Sensitivity、外部冷凝/再沸和拆塔 HeatX。
- **验证**：检查 `SNS_TAB` 有效行、Design Spec 误差、块状态、塔压剖面和 `.his`；拆塔时同时检查外部循环流相态。
- **失效边界**：只看产品纯度或只看 Design Spec 收敛，不能证明塔的压力、水力和能量方案可行。

## M03 反应器与反应动力学

### M03-P01 反应器类型由已知信息和流动状态决定

- **来源**：`engineering-modeling-basics.md` §Reaction Engineering；`aspen-plus-textbook-guide.md` §Reactors。
- **适用条件**：从化学计量、转化率、产率、速率式和反应器停留特性中选择 Aspen 单元时。
- **核心判断**：已知化学计量和转化率用 `RStoic`；已知产率分布用 `RYield`；平衡用 `REquil/RGibbs`；动力学搅拌釜用 `RCSTR`；动力学管式反应器用 `RPlug`。
- **Aspen 映射**：先建立反应集和相态，再把反应集挂到反应器；不要用 `RStoic` 伪装有温度、浓度和停留时间依赖的动力学。
- **验证**：分别检查元素守恒、转化率、选择性和产率；有反应热时独立检查能量方向和温升/降。
- **失效边界**：没有可靠反应机理或动力学数据时，不能从案例中的转化率反推普适速率常数。

### M03-P02 速率式、温度和单位必须成套核对

- **来源**：`kinetic-reactor-input-workflow-320-322.md`、`general-modeling-mechanics.md` §5；提炼自《化学反应工程》朱炳辰第 5 版。
- **适用条件**：`PowerLaw`、`LHHW`、`General` 和文献动力学落地时。
- **核心关系**：幂律 `r=k[A]^a[B]^b`；Arrhenius `k=k0*exp(-Ea/(R*T))`。Aspen 形式可用参考温度重参数化，但活化能单位必须以实际字段 `UnitString` 为准。
- **Aspen 映射**：先在 `General` 中整理文献表达式，再映射到 `LHHW` 或 `PowerLaw`；记录基准温度、浓度/分压基准、反应相、速率单位和吸附项。
- **验证**：在单一温度和组成下手算速率，逐项对照 Aspen；检查 `UnitString`、反应方向、限域项和反应热。
- **失效边界**：缺失 `Keq(T)`、驱动力系数或吸附常数时，不能把模板值写成文献数据；只能明确标为假设、拟合量或待补数据。

### M03-P03 反应器尺寸和非理想流动

- **来源**：`engineering-modeling-basics.md` §Ideal Reactor Design/Nonideal Flow/Fixed-Bed and Catalytic Reactors。
- **适用条件**：已确定速率式后估算体积、停留时间、轴向混合、固定床压降或多相行为时。
- **核心关系**：PFR `V/F_A0=integral(dx_A/(-r_A))`；CSTR `tau=C_A0*x_A/(-r_A,out)`；固定床压降用适用的 Ergun 形式；绝热温升由反应焓和热容共同决定。
- **Aspen 映射**：`RPlug` 负责轴向变化，`RCSTR` 负责完全混合，多个 CSTR 可近似串联混合；固定床必须把入口/出口压力和床层压降一起规定。
- **验证**：比较 PFR/CSTR 极限、体积或停留时间、出口相态、温度剖面和压降；反应器后接 `Flash2` 时检查分相是否符合组成和压力。
- **失效边界**：把所有反应器都当等温、无压降或完全混合会掩盖热失控、停留时间和传质限制。

## M04 压力输送、压力网络与压力降

### M04-P01 连续性、机械能和摩擦损失

- **来源**：`engineering-modeling-basics.md` §Fluid Flow and Pressure Changers；`equipment-hydraulics-and-rating.md` §5。
- **适用条件**：泵、压缩机、阀、管道、塔压降以及有回流/循环的压力网络。
- **核心关系**：连续性 `rho*A*u=constant`；扩展 Bernoulli 方程包含压力头、速度头、位差、设备功和摩擦损失；`Re=d*u*rho/mu`；直管摩擦损失按 Darcy/Fanning 体系并计入局部损失。
- **Aspen 映射**：液体升压用 `Pump`，气体升压用 `Compr/MCompr`，单段管线用 `Pipe`，多段或多相用 `Pipeline`，节流用 `Valve`；设备出口压力必须能覆盖下游压降。
- **验证**：画出从压力源到压力汇的路径，逐段列出绝对压力、压降、设备升压/压缩比和相态；变化压力后重跑并读取 `.his`。
- **失效边界**：只给“塔顶到塔底的压力差”而忽略冷凝器、换热器、管线和阀门损失，会得到不可实现的压力网络。

### M04-P02 压降是有依据的设备数据

- **来源**：`engineering-modeling-basics.md` §Pressure Drops Across Every Unit；`double-effect-distillation-and-design-spec.md`。
- **适用条件**：所有会改变压力的设备，包含塔板/填料、HeatX、加热器、冷凝器、再沸器和循环回路。
- **核心关系**：零压降是需要说明的假设；普通正压服务可从约 `0.2 bar` 起做工程估算，真空/低压或压差夹紧回路才可使用 `0.01-0.05 bar` 量级，并且必须记录理由。
- **Aspen 映射**：塔用 `DP-STAGE/DP-COL`；HeatX 用热/冷侧压降；Heater/Flash2 用模块压力字段；不要把压降写成不存在的语法节点。
- **验证**：压降改变后重新检查沸点、LMTD、压缩比、回流相态和循环收敛；把初估结论标为 `PRELIMINARY`，不能冒充评级。
- **失效边界**：用极小压降消除警告、用补偿泵掩盖错误压力网络、或对所有设备套同一数值，都会让热量和能耗结果失真。

## M05 换热、热量集成与公用工程

### M05-P01 热负荷和换热面积

- **来源**：`engineering-modeling-basics.md` §Heat Transfer and Exchangers；`heat-carrier-and-salt-properties.md` §3。
- **适用条件**：加热、冷却、冷凝、再沸、HeatX 设计和公用工程换热。
- **核心关系**：显热 `Q=m*cp*dT`；相变 `Q=m*lambda`；`Q=U*A*dT_lm`；`1/U` 必须分解为两侧膜阻、污垢阻和壁阻。压力降改变后必须重算端温差和 LMTD。
- **Aspen 映射**：简单单侧换热用 `Heater`；两侧换热用 `HeatX`；初筛可以 shortcut，但正式面积需要显式 U 或 Detailed/EDR，并写清 `SPEC/VALUE`。
- **验证**：用 Aspen duty、流量、真实物性和温差反算 `cp`/`U`；检查热端、冷端、最小接近温差和是否发生温度交叉。
- **失效边界**：`U-OPTION=PHASE` 的默认值不能自动当成设计 U；单纯调大面积不能修复错误的相态、压力或物性。

### M05-P02 载热介质物性是设计输入

- **来源**：`heat-carrier-and-salt-properties.md`；硝酸盐参考 INL/EXT-10-18297，水参考 IAPWS-IF97，相变温度参考 NIST。
- **适用条件**：熔盐、导热油、加压水、废热回收和蒸汽生产。
- **核心关系**：循环量随 `Q/(cp*dT)` 变化；泵和管径受密度、黏度、流速和压降控制；冷端壁温必须高于凝固点并留出安全裕量。
- **Aspen 映射**：记录载热介质的 `cp/rho/mu/k`、冻结和分解边界；用户物性不能只靠文件注入，必要时走 Prop-Data + Model Selection 路径。
- **验证**：从最终案例反算 `cp=Q/(m*dT)` 和 `rho=m/(FLUID_POWER/dP)`；与权威数据比较并标出偏差。
- **失效边界**：Aspen 默认数据库、案例中的盐物性或未经核对的水焓不能直接用于正式设计。

## M06 热泵、多效与热耦合流程

### M06-P01 热集成必须满足热力学可行性

- **来源**：`engineering-modeling-basics.md` §Heat Transfer；`thermally-coupled-distillation.md`；`column-splitting-and-heat-integration.md`。
- **适用条件**：热泵、多效精馏、差压热耦合、塔间 HeatX 和废热回收。
- **核心判断**：热源必须在换热端温度和压力下能提供足够高的热位；压缩机功、辅助冷凝/再沸和所有新增压降都要计入同一产品基准的能耗比较。
- **Aspen 映射**：LP 塔顶蒸气经压缩后供 HP 塔底，或 HP 塔顶经 HeatX 供 LP 再沸；辅助设备只补偿负荷差，不应隐藏主耦合失败。
- **验证**：检查两侧相态、LMTD、最小接近温差、压缩比、辅助负荷和产品收率；每个压力改变都回到 M04。
- **失效边界**：只比较再沸器 duty、忽略压缩功或提高温度而超过敏感组分限制，不能称为节能方案。

### M06-P02 温度敏感组分优先约束技术路线

- **来源**：`thermally-coupled-distillation.md`；`column-splitting-and-heat-integration.md`。
- **适用条件**：苯乙烯聚合、热分解、催化剂失活或任何有最高温度限制的体系。
- **核心判断**：热泵会压缩并过热塔顶蒸气；高压侧冷凝温度必须高于受热侧温度；因此要比较“节能收益”和“最高实际温度”两个约束。
- **Aspen 映射**：读取塔顶、压缩机出口、HeatX 热端和塔底温度；对敏感组分设置明确限值并保留裕量。
- **验证**：输出最高温度位置、停留时间假设、聚合/分解边界和能耗；必要时选择热集成或多效而不是蒸汽再压缩。
- **失效边界**：原塔温差满足要求，不代表压缩后的热泵流程仍满足温度限制。

## M07 设备水力学与评级边界

### M07-P01 负荷、几何和压降必须在同一工况闭合

- **来源**：`equipment-hydraulics-and-rating.md` §3-§5；`engineering-modeling-basics.md` §Fluid Flow。
- **适用条件**：塔径、塔板/填料、管道、泵、阀和换热器初筛或评级。
- **核心判断**：必须冻结最终流量、密度、黏度、温度、压力、相态、几何和允许压降；塔水力学至少检查液泛、漏液、夹带、降液管、堰和阶段压降。
- **Aspen 映射**：从最终 Aspen 工况导出阶段负荷、塔径、压降和设备输入；`HYDRAULIC=NO` 只能证明物料/能量模拟，不能证明内件通过。
- **验证**：按正常、最小、最大和扰动负荷做包络；脚本输出必须带假设和证据等级。
- **失效边界**：只用平均流量、只看液泛率、或在塔径/回流比改变后沿用旧水力数据，结论无效。

### M07-P02 证据等级决定结论措辞

- **来源**：`equipment-hydraulics-and-rating.md` §2。
- **适用条件**：需要向用户说明“初估、Aspen 证据、厂家评级”之间的边界时。
- **核心判断**：`PRELIMINARY`、`SOURCE_BOUND`、`ASPEN_EVIDENCE`、`VENDOR_RATING`、`CLOSED` 是不同证据等级；计算成功不自动升级等级。
- **Aspen 映射**：把 Aspen 结果、手算关联式、厂家数据和 EDR 身份分别列出，不混成一个“已设计”结论。
- **验证**：交付表逐项写出输入来源、适用关联式、结果、裕量和缺口。
- **失效边界**：没有内件几何、材料、厂家数据或正式评级时，不得写“最终设计通过”。

## M08 循环、Design Spec、收敛与结果验证

### M08-P01 收敛是物理闭环，不是没有弹窗

- **来源**：`general-verification-methods.md` §2/§4/§5；`run-verification-and-reconcile.md` §1-§2。
- **适用条件**：Recycle、Tear、BROYDEN、Design Spec、HeatX 外部循环和塔耦合。
- **核心判断**：真实闭环同时需要合理撕裂流初值、精确守恒和满足阈值的收敛判据；运行结束不代表结果物理可信。
- **Aspen 映射**：先建立无循环基线，再加入一个循环；必要时 `Reconcile()` 初始化撕裂流；用 `Tree.FindNode("\Data").NextIncomplete("")` 检查输入完整性。
- **验证**：读取最新 `.his`、Control Panel、块状态、Design Spec 误差、撕裂流偏差、物料/能量平衡，并在独立目录冷启动复跑。
- **失效边界**：只读 GUI 摘要、只看 Design Spec 误差或只在同一会话内成功，不能证明交付文件可复现。

### M08-P02 四个独立基准验证结果

- **来源**：`general-verification-methods.md` §2；`engineering-modeling-basics.md` §Model Review Checklist。
- **适用条件**：温度、焓、热负荷或产品结果看起来异常时。
- **核心关系**：总物料衡算、相平衡、焓/能量衡算、热负荷与显热/潜热理论四项必须交叉比较。
- **Aspen 映射**：运行后读取流股结果和设备 duty；不要只读 collection-root `Value`，要读具体叶节点并确认单位。
- **验证**：若显示异常但四个物理基准一致，先检查单位和回显；若基准也不一致，回到物性、相态或自由度设计。
- **失效边界**：单一结果、单一报告或单一案例不能替代独立基准。

## M09 COM、输入文件与 PFD/交付机制

### M09-P01 工程决策与自动化落地分层

- **来源**：`general-modeling-mechanics.md` §3；`variables-and-troubleshooting.md`；`com-attach-and-license-env.md`。
- **适用条件**：通过 COM、`.inp`、`.bkp`、`.apwz`、`.rep` 建立和交付流程时。
- **核心判断**：COM 只负责把已经确定的工程方案可靠写入和读出；对象树路径、叶节点、单位、版本和许可环境必须在本机验证。
- **Aspen 映射**：`InitFromFile2` 打开案例；通过 `Tree.FindNode("\Data")` 访问数据；标量写到叶节点；`Run2(False)` 后立即导出结果和 `.his`。
- **验证**：记录输入文件类型、源/目标哈希、实际单位、NextIncomplete 结果、冷启动结果和版本信息；含 PFD 的文件保留图形区段。
- **失效边界**：GUI 能打开、COM 能 Dispatch 或文件能保存，都不能单独证明流程正确、输入完整或许可证可用。

### M09-P02 案例和模板的可追溯使用

- **来源**：`general-modeling-mechanics.md` §6；`run-verification-and-reconcile.md` §4；`pfd-layout-preservation-and-review.md`。
- **适用条件**：从历史案例、官方示例或模板开始建模时。
- **核心判断**：案例只能提供语法、拓扑、初始化和排障线索；当前任务的物性、数值、压力、热负荷和验收目标必须重新推导。
- **Aspen 映射**：复制到 scratch 目录，逐个改动，导出完整 `.inp/.bkp`，在独立目录冷启动后再交付；用户 PFD 只有在明确要求时才修改或剥离。
- **验证**：保存案例来源、适用条件、采用的字段、未采用的字段及原因；对所有改动重新运行和读取 `.his`。
- **失效边界**：模板中的单位、组件顺序、设备身份、PFD 坐标和收敛初值不能跨任务默认继承。

## 卡片到案例的读取规则

完成原理判断后，按模块再读取案例：

- M01：案例用于核对流程边界和物性陷阱；
- M02：案例用于核对塔拓扑、Design Spec 和热耦合写法；
- M03：案例用于核对动力学输入顺序和单位验证；
- M04：案例用于核对压力预算和压降字段；
- M05：案例用于核对热载体、公用工程和 HeatX 规格；
- M06：案例用于核对热泵、多效和耦合流股初始化；
- M07：案例用于核对 Aspen 阶段数据如何送入水力初筛；
- M08：案例用于核对收敛、`.his` 和冷启动修复；
- M09：案例用于核对 COM、文件和 PFD 保真机制。

每次任务的记录至少包含：`模块 → 原理卡片 → 深入原理参考 → 用户要求推理 → 案例 → 独立验证`。
