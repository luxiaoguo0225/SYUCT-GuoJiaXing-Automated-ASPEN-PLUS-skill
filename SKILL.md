---
name: aspen-plus-automation
description: Automate locally installed Aspen Plus on Windows through Apwn.Document COM and plan or verify chemical-process models from textbook principles. Use for properties, reactors, separation, pressure transport, heat integration, solids and special materials, optimization, batch or dynamic modeling preparation, and PFD or file delivery. Route to topic sections before cases; specialized-model support must be checked on the installed version. Includes V14-tested input and cold-start workflows; historical case values are not design defaults.
---

# Aspen Plus 自动化 (Aspen Plus Automation)

> **总纲：先原理与需求，后案例参考。** 本 skill 的所有内容按两级原则组织——**第一原则**：依据化工原理与用户/题目给出的要求建模；**第二原则**：已有案例只作学习参考，禁止照搬模仿。每次调用本 skill 都要先执行第一原则，第二原则仅在需要时辅助。**跑流程时的每个原理与数值都必须“有出处、可溯源”——来自权威教材/资料或用户规定，禁止臆想、杜撰公式、物性与经验值。**

## 1. 调用总原则 (Guiding Principles)

> 本节是最高优先级指令，优先于后面任何具体段落。它决定"一个新模拟应当如何开始"，而不是"如何点按钮"。

### 1.1 第一原则（最高优先级）：按原理与个人定义的要求建模

- **需求先行（个人定义的要求优先）**：先完整收集用户/题目给出的规定——进料组成与状态、目标产物、纯度/回收率、操作压力与温度、能耗或公用工程目标、允许与禁止的技术路线、塔型/拓扑要求（如串联/并联）、温度敏感组分与限温、验收标准等。用户明确规定的，必须按用户规定执行；用户未给全的，按合理工程假设补齐并明确说明假设。
- **原理驱动**：依据化工原理（热力学、相平衡、分离、反应工程、传递与单元操作）和工程判断，独立推导建模方案——物性方法、模块/塔型选择、设计规定（Design Spec）的数量与目标、操作条件与压力剖面等。每个建模决策都要能回答："这是由哪条原理或哪条用户要求推出的？"
- **教材溯源，禁止臆想**：建模所用的原理与数值必须有出处。优先级：用户/题目规定 > 权威教材原理 > 有据工程判断。本 skill 的八份独立教材覆盖与证据等级见 `references/textbook-source-coverage.md`；各主题判断以第2.1节链接的专题K条目为主，旧原理底稿见 `references/engineering-modeling-basics.md`（源自《化工原理》夏清/贾绍义 上、下册、《化学反应工程》朱炳辰 第5版、《化工过程模拟实训——Aspen Plus 教程》孙兰义 第2版等）与 `references/aspen-plus-textbook-guide.md`。凡是公式、物性数据、经验取值、压降、回流比、设计规定目标等，都要能回答“来自哪条教材原理/哪个出处”；查不到或记不准确时，回到教材/参考文档核对，或明确标注“假设”并说明理由——**绝不凭印象编造公式、物性、压降或“经验值”，绝不臆想原理**。
- **先方案后参考**：不得先翻案例再照着搭流程，案例不能替代需求分析与原理推导。
- **冲突处理**：当"已有案例的做法"与"原理/用户要求"冲突时，以原理和用户要求为准，并在交付说明中主动指出差异与理由。

### 1.2 第二原则（辅助）：已有案例只用于学习，不用于模仿

- 案例（本地案例库、已验证 flowsheet、文献复现、历史 `.inp`/`.bkp`）的正当用途是**学习**：理解"某条原理如何落地"、Aspen 的路径/语法写法、常见报错与收敛技巧、合理的取值区间。
- 从案例借鉴的任何数值、构型、压力降、回流比、设计规定等，都必须回到第一原则重新推导，或与用户要求核对；能解释"为什么"才可采纳。
- **案例不等于答案**：不得仅因"案例里就是这么写的"而照抄，也不得把案例的数值直接当作本任务的设定；引用案例时必须说明其适用条件与差异。

### 1.3 推荐的调用顺序

1. 收集并写清需求、目标与约束（用户规定优先，缺省处用合理工程假设并注明）。
2. 先按第2.1节定位主节/相关节，读取对应教材专题K条目，再独立完成原理分析，形成建模方案草案（物性方法、模块、设计规定、压力剖面、操作条件）。**草案中的每个原理与数值都要可溯源到教材/权威资料（拿不准就查 `references/` 或原教材后再定），不许臆想。**
3. 仅在需要时查阅第二原则资料（案例/模式/踩坑记录），用来补全或检验草案，而不是取代它。
4. 搭建/运行模拟，按 §7.1 验收规则校验，并把结果对照需求与原理复核后再交付。
5. 若任务涉及塔内件、管道、泵、阀门或换热器水力学，按 §7.4 和 `references/equipment-hydraulics-and-rating.md` 读取 Aspen 阶段水力数据、做初筛并标记验收等级；`scripts/hydraulic_screening.py` 仅做透明的初步算术，不能替代正式评级。

### 1.4 模块化调用规则（每次调用必须先执行）

本 skill 的“模块”就是下面第 2 节中的主题章节，不是额外的案例目录。每次调用先从用户任务的设备、现象、目标和约束中定位一个主模块及所有相关模块，然后在每个模块内部按固定顺序工作：

1. 先读取该模块的“原理层”，结合用户要求形成物性方法、单元模型、自由度、操作边界和验收指标的判断；
2. 原理判断完成后，才读取同一模块的“案例层”，只借鉴 Aspen 写法、拓扑、收敛手段和已知失败模式；
3. 对跨模块任务，先分别完成各模块的原理判断，再读取交叉案例并核对流股状态、压力、温度、热负荷和自由度接口；
4. 在工作记录或交付说明中列出“主模块/相关模块、原理文件、案例文件、未采用案例及原因”。

一个原理文件可以被多个模块引用，一个案例也可以被多个模块引用；模块章节是调用入口，`references/` 只是资料存放位置。

### 1.5 原理判断必须留下可检查的结论

在读取案例前，用本次实际相关的K条目写出：用户目标/约束、依据的K-ID和教材章页、选用模型与排除其他模型的理由、假设/参数来源、适用条件与量纲、跨节压力/温度/热量/组成接口，以及独立验算与验收指标。简单任务可以短写，但不能只列文档名。案例读取后只补实现机制、差异与验证，不倒过来用案例参数决定方案。

章节级摘要用于定位和判断。涉及具体相关式/参数、OCR数学符号、超出范围或本机未验证的专用模块时，回原教材相应页或权威技术资料核对，并记录核对状态。不得把“有教材条目”写成“已逐式核验”或“已V14运行验证”。

## 2. 概述 (Overview)

Drive a locally installed Aspen Plus through the `Apwn.Document` COM automation interface. The bundled bridge script handles opening cases, editing variables, running calculations, reading results, and saving copies without opening the Aspen GUI by hand.

### 2.1 主题模块总入口（原理与案例配对）

以下章节是本 skill 的实际模块。任务开始时先定位模块，再按该模块的“原理层 → 案例层”读取；不要先浏览全部案例库。模块之间允许多对多引用。

原来的20张 [`第一性原理卡片`](references/first-principles-cards.md) 保留作概览；它们不是知识上限。**主模块及相关模块必须继续读取下面对应的教材专题K条目，完成工程判断后再读案例**。按任务只读相关节，不一次加载全部教材。书目/章节/核对程度见 [`教材覆盖`](references/textbook-source-coverage.md)，原理与案例双向对应见 [`对应表`](references/principle-case-map.md)。

#### M01 需求、物性与流程边界

**适用任务**：新建流程、物性选型/估算/回归、相平衡、电解质和验收边界。

**原理层（先读）**：[textbook-properties-and-boundaries.md](references/textbook-properties-and-boundaries.md) 的 M01-K01–K10。落地细节按需查 `engineering-modeling-basics.md、aspen-plus-textbook-guide.md、general-modeling-mechanics.md`。

**案例层（后读）**：[对应表](references/principle-case-map.md) 中 C01/C02/C09/C13/C16/C19。

**输出与接口**：守恒/相态、数据来源、方法选择、自由度与不确定性。对所有工艺模块提供边界和物性。

#### M02 精馏塔与特殊精馏

**适用任务**：DSTWU/RadFrac、q/R/N/进料板、平衡/速率塔、萃取/共沸/变压/反应/三相精馏。

**原理层（先读）**：[textbook-distillation-and-towers.md](references/textbook-distillation-and-towers.md) 的 M02-K01–K10。落地细节按需查 `tianjin-distillation-9-5-calculation.md、sun-lanyi-ch7-4-radfrac-strict.md、feed-stage-sensitivity-curves.md`。

**案例层（后读）**：[对应表](references/principle-case-map.md) 中 C01/C04/C11/C13/C16。

**输出与接口**：物料与相平衡、MESH与规格、级数/效率、压力与热敏边界。压力连M04，热量连M05/M06，水力连M07，DS/收敛连M08；吸收/萃取等独立操作进M11。

#### M03 反应器、动力学与多相反应工程

**适用任务**：计量/平衡/速率、间歇/CSTR/PFR、RTD、催化内外传递、固定/流化床、气液/流固/三相反应。

**原理层（先读）**：[textbook-reaction-engineering.md](references/textbook-reaction-engineering.md) 的 M03-K01–K17。落地细节按需查 `kinetic-reactor-input-workflow-320-322.md、general-modeling-mechanics.md、input-file-and-rstoic.md`。

**案例层（后读）**：[对应表](references/principle-case-map.md) 中 C01/C03/C09/C15/C16/C18/C21。

**输出与接口**：反应集/速率基准、单位验证、尺寸/选择性、传递限制、热点和验证证据。反应热连M05，压损连M04，收敛连M08，固体连M10/M12。

#### M04 压力输送、压力网络与压力降

**适用任务**：静压/表绝压、黏性/流态、管网、泵/汽蚀、压缩/中冷、阀/闪蒸、流量测量。

**原理层（先读）**：[textbook-fluid-transport.md](references/textbook-fluid-transport.md) 的 M04-K01–K11。落地细节按需查 `equipment-hydraulics-and-rating.md、general-verification-methods.md`。

**案例层（后读）**：[对应表](references/principle-case-map.md) 中 C02/C05/C07/C08/C09/C18。

**输出与接口**：压力路径、真实压头源、几何/物性/压降依据、效率/轴功和最不利工况。向M02/M03/M05提供压力状态，正式设备能力连M07。

#### M05 传热、蒸发、热量集成与公用工程

**适用任务**：导热/对流/辐射、HeatX、U/LMTD/NTU/EDR、单多效蒸发、夹点/HEN、蒸汽动力/全厂公用工程。

**原理层（先读）**：[textbook-heat-and-energy.md](references/textbook-heat-and-energy.md) 的 M05-K01–K15。落地细节按需查 `heat-carrier-and-salt-properties.md、equipment-hydraulics-and-rating.md`。

**案例层（后读）**：[对应表](references/principle-case-map.md) 中 C05/C08/C09/C10/C14/C19。

**输出与接口**：热量/温位、壁温与相变边界、面积/压损、蒸发浓缩、热级联/网络及蒸汽供需。压力连M04，热泵连M06，评级连M07，经济目标连M14。

#### M06 热泵、多效与热耦合流程

**适用任务**：蒸汽再压缩、差压耦合、Petlyuk/DWC、多效精馏/蒸发、COP与能源品位。

**原理层（先读）**：[textbook-distillation-and-towers.md](references/textbook-distillation-and-towers.md) 的 M06-K01–K02，并读[传热与能源](references/textbook-heat-and-energy.md)的M06-K03。落地细节按需查 `general-verification-methods.md、heat-carrier-and-salt-properties.md`。

**案例层（后读）**：[对应表](references/principle-case-map.md) 中 C05/C06/C07/C08/C10/C14。

**输出与接口**：真实液汽连接、温差/热量/压力可行性、同产品基准热电比较；压缩比、节能率和串并联由当前任务决定。联读M02/M04/M05/M07/M08。

#### M07 设备水力学与评级边界

**适用任务**：塔板/填料、塔径、液泛/漏液/夹带、降液管、润湿/分布、泵阀管线和换热器评级。

**原理层（先读）**：[textbook-distillation-and-towers.md](references/textbook-distillation-and-towers.md) 的 M07-K01–K02，按对象联读M04-K03–K09、M05-K03–K07。落地细节按需查 `equipment-hydraulics-and-rating.md`。

**案例层（后读）**：[对应表](references/principle-case-map.md) 中 C04/C08/C09，以及scripts/hydraulic_screening.py、scripts/heat_carrier_screen.py。

**输出与接口**：最终负荷包络、尺寸/几何、压降、效率和证据等级；脚本只是透明初筛，正式评级需厂家/EDR。工况变化回读对应工艺章节。

#### M08 循环、Design Spec、收敛与结果验证

**适用任务**：SM/EO、Tear/Broyden、缩放、Calculator/DS、Sensitivity/拟合、.his、冷启动和数据调和。

**原理层（先读）**：[textbook-numerics-economics-and-custom-models.md](references/textbook-numerics-economics-and-custom-models.md) 的 M08-K01–K07。落地细节按需查 `run-verification-and-reconcile.md、aspen-input-completeness-and-delivery-lessons.md、calculator-flowsheeting-options.md`。

**案例层（后读）**：[对应表](references/principle-case-map.md) 中 C02/C04/C06/C08/C10/C12/C19。

**输出与接口**：自由度/残差、相正确初值、有效候选、诊断与最终验收、独立新开及哈希。服务所有工艺章节，不能以数值收敛代替物理可行。

#### M09 COM、输入文件与PFD/交付机制

**适用任务**：Apwn.Document、树路径/单位、许可、导入导出、输入完整、用户PFD保真与复现。

**原理层（先读）**：[textbook-numerics-economics-and-custom-models.md](references/textbook-numerics-economics-and-custom-models.md) 的 M09-K01。落地细节按需查 `general-modeling-mechanics.md、variables-and-troubleshooting.md、com-attach-and-license-env.md、pfd-layout-preservation-and-review.md`。

**案例层（后读）**：[对应表](references/principle-case-map.md) 中 C12/C19及scripts/aspen_plus_bridge.py。

**输出与接口**：接口/版本证据、可复现文件、PFD布局和冷启动；不决定工艺数值。仅操作已完成工程判断的输入。

#### M10 颗粒分离、固体床与流态化

**适用任务**：固体子物流/PSD、沉降、旋风/离心、过滤/洗涤、Ergun、最小流化、气力输送。

**原理层（先读）**：[textbook-solids-and-mass-transfer.md](references/textbook-solids-and-mass-transfer.md) 的 M10-K01–K07。落地细节按需查 `general-modeling-mechanics.md`。

**案例层（后读）**：[对应表](references/principle-case-map.md) 中 C15；原理—案例表明确本机验证缺口。

**输出与接口**：粒级/固体质量、面积/周期/压损、相态和传递适用范围。反应连M03，干燥/结晶连M11，非传统固体连M12。

#### M11 吸收、萃取、干燥、结晶与膜分离

**适用任务**：两膜/扩散/Henry、吸收/汽提、反应吸收、LLE、湿空气/干燥速率、过饱和/晶体PSD、膜。

**原理层（先读）**：[textbook-solids-and-mass-transfer.md](references/textbook-solids-and-mass-transfer.md) 的 M11-K01–K12。落地细节按需查 `general-modeling-mechanics.md、aspen-plus-textbook-guide.md`。

**案例层（后读）**：[对应表](references/principle-case-map.md) 中 C13/C15/C16；膜暂无本机案例，C19仅参考自定义机制。

**输出与接口**：驱动力、平衡/速率、溶剂/气量/面积、再生/母液/产品指标与数据缺口。电解质连M01，反应连M03，热量连M05，粒子连M10，自定义连M14。

#### M12 石油假组分、非常规固体与聚合物

**适用任务**：Assay/TBP、假组分/常减压/集总反应、煤/生物质/固废、气化热解、聚合链段/分布/动力学。

**原理层（先读）**：[textbook-special-materials-and-dynamics.md](references/textbook-special-materials-and-dynamics.md) 的 M12-K01–K08。落地细节按需查 `aspen-plus-textbook-guide.md、general-modeling-mechanics.md`。

**案例层（后读）**：[对应表](references/principle-case-map.md) 中 C15/C17/C20。

**输出与接口**：表征/基准/物性、切割/产率、元素/焓和产品分布；专用软件与参数核原页/本机。按对象联读M01/M02/M03/M05/M10/M11。

#### M13 动态、控制、开车与批次操作

**适用任务**：库存/ODE/DAE、压力驱动、PID、储槽/非等温CSTR、塔/深冷开车、裂解周期、BatchOp/BatchSep。

**原理层（先读）**：[textbook-special-materials-and-dynamics.md](references/textbook-special-materials-and-dynamics.md) 的 M13-K01–K08。落地细节按需查 `aspen-plus-textbook-guide.md`。

**案例层（后读）**：[对应表](references/principle-case-map.md) 中 C18；当前仅教材示例入口，不能声称所有动态功能已验证。

**输出与接口**：初始库存/控制与事件、时间轨迹/累计衡算、峰值与可操作性、本机许可/接口。稳态COM不能替代Dynamics；联读实际设备章节。

#### M14 经济优化、自定义模型、ROM与批量计算

**适用任务**：资本/OPEX/TAC、约束/离散优化、用户块/外控、ROM/训练域、批量并行与失败隔离。

**原理层（先读）**：[textbook-numerics-economics-and-custom-models.md](references/textbook-numerics-economics-and-custom-models.md) 的 M14-K01–K06。落地细节按需查 `general-verification-methods.md`。

**案例层（后读）**：[对应表](references/principle-case-map.md) 中 C19/C14；设备验证需另建独立基准。

**输出与接口**：方程/端口/自由度、价格/基年/边界、可行域、独立验证和完整模型复核；按用户目标使用，不因普通精馏自动扩大为经济优化。

## 3. 前置条件 (Prerequisites)

- Windows with Aspen Plus installed (V14 validated; `Apwn.Document` must be registered)
- Python with `pywin32`: `python -m pip install pywin32`

## 4. 快速开始 (Quick Start)

Run the built-in demo from the skill directory:

```powershell
python scripts/aspen_plus_bridge.py --demo
```

The demo opens `sour.apwz`, changes FEED temperature from 40 C to 50 C, reruns the simulation, prints FEED/BOT1/BOT2 results, and saves `aspen_demo_result.apwz`. (演示只示范自动化操作机制，不是建模答案。)

## 5. 自动化核心工作流 (Core Workflow)

1. List streams to discover names:

```powershell
python scripts/aspen_plus_bridge.py --open "C:\path\to\case.apwz" --streams
```

2. Edit an input, run, read a result, and save a copy:

```powershell
python scripts/aspen_plus_bridge.py --open "case.apwz" --set "\Data\Streams\FEED\Input\TEMP\MIXED=50" --run --get "\Data\Streams\BOT1\Output\RES_TEMP" --save "result.apwz"
```

## 6. 新建模拟：从需求与原理出发 (Build a New Simulation from Principles and Requirements)

> 本节是 §1.1 第一原则的操作化：**先做 6.1 的设计，再写文件**。6.3 中的既有示例/脚本属于第二原则的"学习参考"，不得照搬其数值。

### 6.0 模块定位记录（先完成）

按 §2.1 从任务描述定位主模块和相关模块。开始读取案例前，先在工作记录中写下：

```text
主模块：Mxx 模块名称
相关模块：Myy、Mzz（没有则写“无”）
原理层：本次实际读取的 references/... 文件
案例层：原理判断完成后实际读取的 references/...、assets/... 文件
```

模块定位不是标签工作：它决定先检查哪些自由度、物性、压力/温度边界和验收指标。一个案例若同时包含精馏、反应、压力网络和热集成，必须分别读取这些模块的原理层，再读取案例并标注其跨模块用途。

### 6.1 建模前的需求与原理检查清单（先完成）

- **需求清单**：分离/反应任务、进料组成与状态、目标纯度/回收率、操作压力与温度、温度敏感组分与限温、能耗/公用工程目标、允许与禁止的技术路线、拓扑要求、验收标准。
- **原理清单**：物性方法选择的依据（组分极性/缔合/电解质/水系统/压力温度范围）、模块与塔型选择的依据、自由度与所需规定数、压力剖面可行性、热量/物料平衡的预期量级。
- 设计草案完成后进入 6.2；需要原理支撑时查阅 §8.1（`references/engineering-modeling-basics.md`、`references/aspen-plus-textbook-guide.md`、`references/modeling-guide.md`）。二元连续精馏的 q 线、Rmin、理论板、进料板和优化流程见 `references/tianjin-distillation-9-5-calculation.md`。

### 6.2 用 `.inp` 落地并运行（机制）

Prefer an Aspen Plus input file (`.inp`) when a case does not already exist. Open it with `InitFromFile2` and run normally.

Run a generic build script:

```powershell
python scripts/build_from_input.py --inp "case.inp" --save "case.apwz" --report "case.rep"
```

- Set units explicitly so values are not misinterpreted:
  `IN-UNITS SI TEMP=C PRES=BAR MOLE-FLOW='KMOL/HR' MASS-FLOW='KG/HR'`
- Define components with `COMPONENTS <ID> <DATABANK-NAME>`, for example `EB ETHYLBENZENE / STY STYRENE / H2 HYDROGEN`.
- Set the global method with `PROPERTIES PENG-ROB` (PR) only when the principle analysis supports it (e.g. non-polar hydrocarbon systems); otherwise pick the method your 6.1 analysis justifies.
- The conversion reactor is the `RSTOIC` block; V14 has no separate `RConv` block.
- Define stoichiometry and conversion with `STOIC` and `CONV` sentences inside `BLOCK <name> RSTOIC`.
- For kinetic reactors, prefer the `General` form first when Aspen offers it, then map the literature rate law into `LHHW` or `PowerLaw`; only skip `General` when the source model or Aspen page forces a direct built-in form.
- For literature kinetics, separate what the paper actually gives from values inferred, retained from templates, or fitted. Do not present a missing `Keq(T)` or driving-force coefficient as literature data unless the source explicitly provides it.
- After running, read component flows from `\Data\Streams\<name>\Output\MOLEFLOW\MIXED\<comp>` and export a report with `Export(2, "result.rep")`.

### 6.3 可参考的落地示例（第二原则：学习模式，校验后使用）

- See [references/input-file-and-rstoic.md](references/input-file-and-rstoic.md) for a complete ethylbenzene-to-styrene example — 只学习其 `.inp` 语法与段落组织，体系数值须按你的需求重设。
- See [references/reactor-flash-column-example.md](references/reactor-flash-column-example.md) and `scripts/build_styrene_column.py` for a full reactor + flash + RadFrac flowsheet with a 99.9% purity design spec — 学习 flowsheet 结构与设计规定的写法，不要复制其纯度/能耗目标。
- For a split column with vapor recompression heat pump, use `assets/column-split/styrene_heatpump.inp` only as a pattern reference; verify every number against your own first-principle analysis.
- See [references/modeling-guide.md](references/modeling-guide.md) for stream input conventions, common property methods, block selection, and block/stream connection.

## 7. 关键规则 (Key Rules)

> 每条规则都先问：它属于第一原则（原理/用户要求）还是第二原则（案例经验）？**原理与用户要求优先**；案例经验作为参考，采用前必须回到第一原则校验。因此下面按三类组织：

### 7.1 第一原则类：原理与需求驱动的建模与验收规则

- COLUMN BUILD SCOPE: if the user only asks for tower basics, deliver the DSTWU/shortcut baseline only. If the user explicitly asks for 精馏塔严格计算, 第7.4节, 严格塔, 最佳理论板数/进料板/回流比, or Sensitivity, then the full Sun Lanyi Section 7.4 workflow is in scope: DSTWU baseline -> RadFrac rigorous tower -> product Design Specs + Vary -> S-1/S-2 strict Sensitivity -> convergence/penalty checks. Do not expand this into full economic/TAC optimization unless the user explicitly requests it.

- For binary continuous distillation, start from the Tianjin 9.5 sequence: mass balance -> q line -> `R_min` -> choose `R` -> Fenske/Gilliland `N` -> feed stage. Treat the textbook `1.1-2.0 R_min` range as an economic rule of thumb, not a mathematical optimum. Use bubble-point feed (`q=1`) as the default baseline when there is no special heat integration. A hotter feed lowers `q`, `V_prime`, and reboiler duty, but the preheat duty must be counted. Re-select the feed stage whenever `q` changes. MANDATORY feed-state gate: do not select the final feed state in one step. Compare the upstream actual state, `q=1` baseline, a hotter/two-phase candidate when heat is available, and saturated/superheated vapor for a vapor feed; exclude any candidate with a documented reason. For every candidate record `T/P/VFRAC/q`, `R_min`, `R`, integer `N/N_F`, `Q_reb`, `Q_cond`, preheat duty, column loads/diameter/flooding, utility cost or the user objective, and robustness. Determine the true optimum of `q`, `R`, integer `N`, and feed stage only with an explicit TAC/utility objective and constraints. See [references/tianjin-distillation-9-5-calculation.md](references/tianjin-distillation-9-5-calculation.md).
- GLOBAL ACCEPTANCE (every flowsheet, incl. heat pumps and double-effect):
  - Final result must show NO hidden errors in the `.his` file
    (`Summary of Simulation Errors` = 0 Severe / 0 Error / 0 Warning), AND the
    Aspen Control Panel must be free of any error/warning.
  - If hidden errors appear, try `Reconcile()` on streams and tower modules to
    seed/initialize values and resolve them; verify on a fresh open.
  - Pressure drop rule: EVERY module except mixers and pressure-changing
    devices (pumps/valves/compressors) must carry a justified pressure-drop
    treatment. Do not type a fixed value by habit. Estimate by fluid phase,
    density/viscosity, equipment type, duty, pressure level, and downstream
    pressure margin. For ordinary positive-pressure exchangers,
    condensers/reboilers, coolers/heaters, and similar equipment, use an
    case-derived starting point around -0.2 bar only when the matching user requirement and current equipment estimates support it; it is not a general design value. Use very small
    drops such as -0.01 to -0.05 bar only for vacuum/near-vacuum services,
    low-pressure loops, or cases where a return stream would otherwise become
    pressure-infeasible and no real pressure-boosting device is allowed.
- Account for pressure drops in every pressure-changing unit before running:
  column tray profile (`DP-STAGE`/`DP-COL`), heat exchanger hot/cold sides,
  condensers/reboilers, valves, splitters/mixers, and piping. Do not
  blanket-set zero pressure drops, do not use arbitrary empirical values, and
  do not default to tiny `0.0x bar` drops just to avoid pressure warnings.
  Estimate from stream and equipment conditions using chemical engineering
  principles, document the assumptions, and only relax toward very small drops
  after checking that the pressure network or vacuum service requires it.
  See [references/engineering-modeling-basics.md](references/engineering-modeling-basics.md).
- After every `Run2`, read the newest `.his` before reporting; the GUI summary
  can hide errors. See [references/run-verification-and-reconcile.md](references/run-verification-and-reconcile.md) for `.his` error checking, `Reconcile()` tear-stream initialization, complete HeatX specs, PFD stripping, and report unit conversion.
- Use a partial-vapor condenser when H2 or other noncondensables are present; a total condenser can produce unphysical cryogenic overhead temperatures.
- TEMPERATURE-SENSITIVE COMPONENTS FIRST: use sourced limits for the actual composition, inhibitor, residence time and local wall/film temperature. Compare every candidate's compression, tower-pressure and heat-exchange temperature changes. Heat pumps, thermal coupling and multi-effect each require an independent temperature/phase/pressure feasibility check; none is automatically temperature-safe. Use M02-K08, M03-K09 and M06-K01–K03 before the historical [thermal-coupling case](references/thermally-coupled-distillation.md).

- HEAT-CARRIER PROPERTIES ARE DESIGN DATA, NOT DEFAULT DATA: for molten salt / thermal oil / pressurized-water carriers take cp, rho, mu, k and the freezing/decomposition limits from an authoritative source (nitrate salt: INL/EXT-10-18297 = OSTI 980801; water: IAPWS-IF97). Aspen's databank is NOT usable for molten nitrates: measured here, 40 wt% KNO3 + 60 wt% NaNO3 gives cp ~1.15 kJ/(kg.K) and rho ~438 kg/m3 -> cp low by ~40%, density low by ~4x (pump power / volume flow / dT all wrong). ALWAYS audit a case by back-calculating cp = Q/(m*dT) from a Heater duty and rho = m/(FLUID_POWER/dP) from a Pump; reject any case whose back-calculated values differ from handbooks by >10%. Entering user property data additionally requires the GUI Prop-Data + Model Selection route - file injection alone is silently ignored. See [references/heat-carrier-and-salt-properties.md](references/heat-carrier-and-salt-properties.md).

### 7.2 工具与机制规则（COM / `.inp` 语法 / 文件处理；服务于任何原则）
- **跨版本通用机制/验证文档（工具与机制层，服从 §1 两级原则）**：见 [references/general-modeling-mechanics.md](references/general-modeling-mechanics.md) 与 [references/general-verification-methods.md](references/general-verification-methods.md)。二者只收录跨版本通用方法，不改变“原理+需求先行、禁臆想”的第一原则；其中任何树路径、单位、节点名、API 均须以本机安装版本实测为准，不得把其他版本的结论当通用事实套用。

- Open both `.bkp` and `.apwz` with `InitFromFile2(path, True)`. On V14, `InitFromArchive2` can fail with "cannot open file" for `.apwz`.
- Access simulation data through `Tree.FindNode("\\Data")`. Stream paths follow `\Data\Streams\<name>\Input\...` and `\Data\Streams\<name>\Output\...`.
- Write scalar inputs through leaf nodes such as `Input\TEMP\MIXED` or `Input\PRES\MIXED`. Writing `Input\TEMP` directly can raise `AE_UNDERSPEC`.
- Run synchronously with `Run2(False)`; save with `SaveAs2(path, True)`.
- Read result values such as `Output\RES_TEMP`, `Output\RES_PRES`, and `Output\RES_MASSFLOW`.
- Export the report immediately after `Run2`; component-level results may not reload into the COM tree from a saved `.apwz`.
- For recycle loops, run to a converged base first, then call
  `apwn.Reconcile(...)` with tear-stream flags to initialize inputs; its effect
  may not survive save/reopen, so always verify on a fresh open.
  See [references/run-verification-and-reconcile.md](references/run-verification-and-reconcile.md).
- Check input completeness with
  `Tree.FindNode(r"\Data").NextIncomplete("")`, not `Tree.NextIncomplete`.
- Set `Visible` after initialization. To keep the GUI open after automation, save the case and launch it with `os.startfile(apwz)`.
- COM automation may start the Aspen Plus GUI process; call `Quit()` in `finally`. Terminate leftovers only by verified PIDs belonging to this run, including confirmed child processes; preserve user and unknown instances. Respect any user prohibition on Computer Use or GUI inspection.
- **COM connection mechanics (measured)**: `Dispatch("Apwn.Document")` **never attaches** to an
  already-running instance - the COM SCM always spawns a fresh `aspenplus.exe -Automation -Embedding`,
  and `GetActiveObject` fails with `MK_E_UNAVAILABLE` (no ROT registration); so pre-launching
  `aspenplus.exe -Automation` to "attach" is pointless and only costs an extra process/seat. License
  checkout is decided by `LSHOST`/`LSFORCEHOST` in the **client** process environment (the spawned
  server inherits it). A successful `Dispatch` does NOT prove the license works - `2040 ... 无法核实许可 /
  无法实例化` surfaces only at `InitFromFile2`; when `LSHOST` is unresolvable and subnet broadcast is
  blocked there is no fallback, so set `LSFORCEHOST=<host>` explicitly. See
  [references/com-attach-and-license-env.md](references/com-attach-and-license-env.md).
- FlowSheet-level Design Specs in `.inp`: place after all `BLOCK` paragraphs and
  before `EO-CONV-OPTI`; use `DEFINE X MOLE-FLOW STREAM=S SUBSTREAM=MIXED
  COMPONENT=C` (the `STREAM-VAR ... COMPONENT=` form parses wrong or ignores the
  component), `VARY BLOCK-VAR BLOCK=FSPLIT SENTENCE=FRAC VARIABLE=FRAC ID1=out`,
  and tighten the tear tolerance to `CONV-OPTIONS PARAM TOL=0.00001` so outer
  Design Specs can converge. See [references/double-effect-distillation-and-design-spec.md](references/double-effect-distillation-and-design-spec.md).
- Deliverables: prefer `.inp` via `Export(4,...)` and `.bkp` via `Export(1,...)` from
  the saved case. `SaveAs2(...bkp)` has both successful and failed reopen histories;
  validate the chosen method on the local version. COM initialization can rewrite
  backups in the opened folder: do NOT initialize any file in the deliverable folder.
  Copy each candidate into a fresh scratch directory, then use `InitFromFile2` and
  `Run2(False)` there for cold-start validation. Record source/final hashes and actual
  file content/type; preserve the delivered bytes. Opening a GUI is not a substitute
  for run validation, and requires compatibility with the user's tool restrictions.
- PFD/layout work: read [references/pfd-layout-preservation-and-review.md](references/pfd-layout-preservation-and-review.md).
  Preserve the latest user layout, anchors and labels; align actual ports, not only
  equipment centers. Geometry checks, COM runs and visual/user acceptance are separate.
  Use `scripts/audit_pfd_layout.py` for read-only evidence, never as an approval gate.
  Do not globally reset labels or promote a user-rejected layout as an accepted example.
- Heat/enthalpy outputs: verify leaf nodes and UnitString; collection Value and missing
  output are not scalar results. Calibrate report conversion rather than assuming a
  universal calorie factor. See [references/pdo-heat-integration-and-delivery-lessons.md](references/pdo-heat-integration-and-delivery-lessons.md).

### 7.3 第二原则类：来自已验证案例的可复用经验（学习参考；采用前必须回到第一原则校验）

> 下面这些是历史案例/文献中沉淀的模式与踩坑记录。它们能显著加快收敛与避免返工，但都默认**适用于原案例的体系与前提**；用到你的任务前，须逐条用 §6.1 的原理/需求核对适用性。

- For a bare tower with an external reboiler loop, initialize the reboil-vapor
  tear stream a few degrees ABOVE the dew point (all vapor). A bubble-point
  initial T flashes to `V=0` (liquid), which makes RadFrac treat the vapor feed as
  liquid and produces a cluster of transient errors every run: `UDL03.3` top-tray
  dry-up, `UDL03.2` component-balance failure, and HeatX `HEATX.4` temperature
  crossover. Detect it by reading the first-flash `V` value in the `.his`.
  See [references/double-effect-distillation-and-design-spec.md](references/double-effect-distillation-and-design-spec.md).
- Column splitting (RadFrac `CONDENSER=NONE`/`REBOILER=NONE` with external condenser/reboiler) and stream HeatX integration: read [references/column-splitting-and-heat-integration.md](references/column-splitting-and-heat-integration.md) first.
- Reactor waste heat plus two-column integration: read [references/pdo-heat-integration-and-delivery-lessons.md](references/pdo-heat-integration-and-delivery-lessons.md) for stage remapping, steam-loop degrees of freedom, heat-grade matching, pressure budgets, units and cold-start evidence. The PDO energy subsystem was validated; its original deep-cold quench issue was not resolved. User layout reference and rejected automatic routing are documented separately; case numbers are not defaults.
- For vapor recompression heat pumps, sweep the compression ratio and check
  `REB-HX` overall and zone LMTD plus the condensing/boiling minimum approach;
  the original case limits compression ratio to 2.5; determine the current limit from machinery, discharge temperature, phase state and user constraints. See [references/column-splitting-and-heat-integration.md](references/column-splitting-and-heat-integration.md).
- For the styrene heat-pump split flowsheet, reuse and preserve the
  user-preferred PFD layout in `assets/column-split/styrene_heatpump_user_layout.bkp`;
  do not strip its `GRAPHICS_BACKUP` / `PFS` section unless explicitly asked.
- For differential-pressure thermal coupling (差压热耦合 = two-column vapor recompression): LP tower overhead vapour -> compressor -> HP tower bottom; HP overhead vapour -> HeatX -> LP reboiler (main coupling); auxiliary reboiler/condenser only for load mismatch. The cited case uses compression ratio <= 2.5 (not a universal cap); check HeatX LMTD/min-approach, use phase-correct tear-stream initial values, compare energy on the same product basis. C3 propylene/propane case: conventional 200-stage heat 6.39e7 kJ/h -> compressor 4.92e6 kJ/h (-92.3%). See [references/differential-pressure-thermal-coupling.md](references/differential-pressure-thermal-coupling.md).
- Three-component thermally coupled distillation (Petlyuk two-column equivalent): the coupling is STREAM-based, not tray-heat-duty-based - a prefractionator with CONDENSER=NONE REBOILER=NONE and EMPTY COL-SPECS gets its reflux (REF-PF liquid) and reboil vapor (REBV-PF vapor) from the main column as tear streams; verify PF duty 0/0. REBV-PF flow is the dominant B/C-split variable; side-draw stage must match the V-PF feed stage; more MC stages can make it WORSE (design spec lowers RR and starves the B/C stripping section). To clear transient UDL03.x dry-up errors in .his: seed the tear-stream inputs from converged results AND tighten the design-spec LIMITS around the solution - Reconcile() API alone does not fix them. See [references/three-component-thermal-coupling-case.md](references/three-component-thermal-coupling-case.md).
- The historical double-effect task preferred SERIES topology and specified >=35% energy saving, strict clean logs and no compensation pumps. Apply its topology, saving target and equipment restrictions when the current user requirements inherit them; otherwise choose and justify the current topology and target from M02/M04/M05/M06. Pressure drops require current geometry/phase/property evidence, not a blanket 0.2 bar. The case realization is in [references/double-effect-user-workflow.md](references/double-effect-user-workflow.md).

### 7.4 设备水力学与验收边界

- 水力学结论必须标明等级：`PRELIMINARY`、`SOURCE_BOUND`、`ASPEN_EVIDENCE`、`VENDOR_RATING` 或 `CLOSED`。不得把初估或工具调用成功写成最终设计通过。
- 塔器水力学至少检查面积闭合、降液管、堰和液层、开孔或填料几何、压降、漏液、夹带、液泛和正常/最小/最大/扰动负荷包络。填料塔还要检查湿润、分布、分段、再分布器、压降和 HETP。
- 换热面积用显式、有依据的U或详细模型；热阻/关联式的面积基准、流态和物性范围按M05-K03/K06核查。`U-OPTION=PHASE`在旧熔盐案例测试中返回默认850 W/(m²·K)，不代表通用设计U或所有版本行为。校核局部壁温/膜温的凝固、分解和腐蚀边界；旧案例10–25%面积裕量、凝固点+20 K仅为原任务起点，当前裕量由来源/设备/工况重新确定。见 [references/heat-carrier-and-salt-properties.md](references/heat-carrier-and-salt-properties.md)。
- `HYDRAULIC=NO` 的干净物料模拟只证明物料和能量计算，不证明塔内件水力学。任何塔径、压力、内件或负荷改变后，必须从同一最终 Aspen 工况重新导出阶段数据并复算。
- 换热器要区分 HeatX、Shortcut、Detailed 和真正的 Aspen EDR，并确认同设备身份、负荷、面积、压降、速度和材料证据。
- `scripts/hydraulic_screening.py` 可从 Aspen 结果中提取塔径、阶段负荷与水力数据做透明初筛；输出必须保留适用条件和证据等级，不能替代厂家评级。

## 8. 参考文档 (References)

> 按两级原则分组：8.1 是**第一原则支撑**（原理/方法/机制，设计时按需查阅）；8.2 是**第二原则支撑**（案例与已验证工程，只作学习参考，采用前回第一原则校验）。

### 8.0 读取顺序

第 2.1 节的 M01-M14 是实际主题入口；先按模块读取对应的原理文件，再按需读取同模块案例。下面的 8.1/8.2 只是完整的原理/案例反向索引，不代表调用顺序。

`references/first-principles-cards.md` 是旧概览卡片；本次任务的正文判断必须进入第2.1节教材专题K条目。`references/textbook-source-coverage.md` 提供章页与核对状态，`references/principle-case-map.md` 在判断完成后提供多对多案例引用。

### 8.1 原理与来源

- [教材来源与全部章节覆盖](references/textbook-source-coverage.md)：八份独立教材、重复本识别、原页入口和核对状态。
- 第2.1节14个章节已链接八份教材专题正文，任务时读取相关K条目；[旧概览卡](references/first-principles-cards.md)与[旧工程基础](references/engineering-modeling-basics.md)保留兼容。
- [Aspen教材指南](references/aspen-plus-textbook-guide.md)、[建模机制](references/general-modeling-mechanics.md)、[独立验证](references/general-verification-methods.md)用于本机落地，不替代专题原理。
- 按对象查[严格塔](references/sun-lanyi-ch7-4-radfrac-strict.md)、[二元计算](references/tianjin-distillation-9-5-calculation.md)、[动力学输入](references/kinetic-reactor-input-workflow-320-322.md)、[设备评级](references/equipment-hydraulics-and-rating.md)、[载热物性](references/heat-carrier-and-salt-properties.md)。

### 8.2 案例与机制

- [原理—案例双向对应](references/principle-case-map.md)是案例唯一完整索引：包含具体文件/章节、H/T/L/U证据、借鉴内容、参数/拓扑差异和验证缺口。
- [案例目录](references/distillation-case-library.md)仅在原理决定技术路线后定位模板；[Sensitivity范围](references/sensitivity-scope-and-configuration.md)保留用户规定的扫描与交付边界。
- 工具机制按需读[Calculator](references/calculator-flowsheeting-options.md)、[输入/RStoic](references/input-file-and-rstoic.md)、[输入完整/SEP](references/aspen-input-completeness-and-delivery-lessons.md)、[运行/Reconcile](references/run-verification-and-reconcile.md)、[COM/许可](references/com-attach-and-license-env.md)、[树变量/排错](references/variables-and-troubleshooting.md)、[PFD保真](references/pfd-layout-preservation-and-review.md)。
- 原始`assets/`和`scripts/`路径保留；文档维护成功不代表相应案例已重新运行，不通过修改案例记录提升验证等级。
