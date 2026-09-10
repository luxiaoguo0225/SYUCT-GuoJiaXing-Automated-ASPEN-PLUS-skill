# 含水芳烃流程：物性方案、三相回收、脱水与循环（苯乙烯闭环经验）

> 来源：25 万吨/年乙苯脱氢制苯乙烯闭环流程（含 Calculator 循环）实战验证。
> 核心结论：**水/芳烃体系必须用 PR + UNIQUAC + HENRY + FREE-WATER 物性组合**；
> 不凝气回收必须用 **FLASH3 三相闪蒸**；溶解水在精馏段前用 **汽提塔** 集中脱除；
> 循环补加用 **Calculator**，撕裂流股要显式 TEAR + 给初值。

## 1. 物性方法（决定成败）

PENG-ROB 单独使用会**错误预测水+芳烃的汽液/液液平衡**：
- FLASH2 两相闪蒸时，水相占据液相，EB/STY 被"锁"在气相，深冷也无法回收（0°C 下 EB 分压 0.014 bar > 蒸气压 0.0025 bar 却不冷凝）。
- 水在塔中会被预测成重组分沉底，汽提塔无法脱水。

正确组合（来自已验证的完整苯乙烯 .bkp 案例）：

```text
PROPERTIES PENG-ROB 
    PROPERTIES PENG-ROB FREE-WATER=STEAM-TA SOLU-WATER=3  &
        TRUE-COMPS=YES / UNIQUAC HENRY-COMPS=HC-1  &
        FREE-WATER=STEAM-TA SOLU-WATER=3 TRUE-COMPS=YES 

HENRY-COMPS HC-1 H2 CH4 C2H4 
```

- **不要写 `PROPERTIES PENG-ROB PR ... / UNIQUAC UN ...` 中的 `PR` / `UN` section ID**：
  手写 .inp 会报 `SECPO.6 INVALID SECTION ID PR/UN`（2 个警告）。去掉 PR/UN 后 0 警告，且物性正常。
- `HENRY-COMPS` 必须在 `COMPONENTS` 之后、`SOLVE` 之前声明。
- `PROP-DATA HENRY-1`（H2/CH4/C2H4 在水/苯/甲苯/乙苯中的亨利常数）和
  `PROP-DATA UNIQ-1`（EB/STY/BZ/TOL/H2O 的 UNIQUAC 二元参数）放在 `ESTIMATE ALL` 之后，
  **不要**放在 BLOCK 段之后（位置不对会导致物性不加载、全流股 0 值）。
- UNIQUAC 参数可直接复用已验证案例的 BPVAL 数值（EB-STY、EB-H2O、EB-BZ、EB-TOL、
  STY-H2O、STY-BZ、H2O-BZ、H2O-TOL、BZ-TOL 及其对称项）。

## 2. 不凝气（OFFGAS）回收：必须 FLASH3 三相闪蒸

- FL1（Flash3, 40°C）：COOL-OUT → OFFGAS / ORG / AQ-W，分出大部分水相。
- OFFGAS（H2/CH4/C2H4 + 芳烃蒸气 + 水蒸气）进 **FL2 必须用 FLASH3**（0°C 深冷）：
  `BLOCK FL2 FLASH3 PARAM TEMP=0.0 PRES=0.0`，输出 `FUELGAS / ORG2 / COND2`。
- 用 FLASH2 的后果：EB 12.8 + STY 15.8 kmol/h 全部跑进燃料气（损失 ~1.4 t/h）；
  改 FLASH3 后燃料气只带走 EB 1.2 + STY 1.0（损失降 90%+）。
- 深冷冷凝液：ORG2（有机相，回汽提塔再脱水）、COND2（水相，回水循环）。
- 注意：多股进料直接写 `BLOCK FL2 IN=OFFGAS STR-V OUT=FUELGAS ORG2 COND2`，
  **不要**加混合器（Flash 支持多进料，混合器是无用工段）。

## 3. 溶解水：精馏段前用汽提塔集中脱除

- FL1 只能分出大部分水（AQ-W ~3543 kmol/h）；ORG 仍溶解 ~27 kmol/h 水。
- 用 **STRIP 汽提塔（RadFrac, CONDENSER=NONE）**：
```text
BLOCK STRIP RADFRAC 
    PARAM NSTAGE=8 ALGORITHM=STANDARD MAXOL=50 DAMPING=NONE 
    PARAM2 
    COL-CONFIG CONDENSER=NONE 
    FEEDS ORG 1 / ORG2 1 
    PRODUCTS STR-V 1 V / STR-BOT 8 L 
    P-SPEC 1 .31 
    COL-SPECS DP-COL=.030 <bar> MOLE-D=30.0 
    SPEC 1 MOLE-FLOW .10 COMPS=H2O STREAMS=STR-BOT  &
        SPEC-DESCRIP="Water in bottoms, .10, PRODUCT" 
    VARY 1 MOLE-D 10.0 60.0 
```
- **CONDENSER=NONE 的塔进料必须在第 1 级**（`FEEDS ... 1`），否则 2041。
- 塔顶汽相 STR-V（水 + 少量芳烃）并入 FL2 深冷回收；塔底 STR-BOT 含水可到 0.1 kmol/h。
- 脱水后 C1/C2/C3 精馏塔**不需要**任何澄清器/分水器（DEC3/DEC4/DEC5 全部删除）。

## 4. 乙苯 + 水循环（Calculator + TEAR）

- 乙苯循环：C2-BOT（未反应 EB）→ 泵 P-EB → EB-REC → M1。
- 水循环：AQ-W + COND2 → M4 → H2O-REC → M1。
- 计算器（Flowsheeting Options → Calculator）：
```text
CALCULATOR EBMAKE
    DEFINE EBREC MOLE-FLOW STREAM=EB-REC SUBSTREAM=MIXED  &
        COMPONENT=EB UOM="kmol/hr" 
    DEFINE EBFRS MOLE-FLOW STREAM=FRESH-EB SUBSTREAM=MIXED  &
        COMPONENT=EB UOM="kmol/hr" 
F     EBFRS=514.0-EBREC 
    READ-VARS EBREC 
    WRITE-VARS EBFRS 
```
- **撕裂流股**：文件末尾 `TEAR EB-REC / TEAR H2O-REC`，且**必须在 STREAM 段给撕裂流股初值**
  （EB-REC、H2O-REC、MIX-OUT、STR-V），否则首次迭代全部块 ZERO FEED（十几个警告）。
  - Aspen 会自动选择撕裂流股（可能是 MIX-OUT/STR-V 而非你声明的），给这些流股初值即可。
  - 初值用组分 MOLE-FLOW 形式且要归一/匹配总量，避免 `MOLE FRACTIONS NORMALIZED` 警告。
- **循环压力闭合**：ORG2 从 FL2 回 STRIP，FL2 必须 `PRES=0.0`（冷凝器等压），
  否则 FL2 每降 0.01 bar 后 ORG2 永远低于 STRIP 塔顶（FEED PRESSURE LOWER THAN STAGE 警告）。

## 5. 压降与单位（.inp 手写易错）

- IN-UNITS 里 `PDROP='N/sqm'` 时，**`DP-STAGE` / `DP-COL` 必须显式带 `<bar>`**：
  `DP-STAGE=.00060 <bar>`、`DP-COL=.030 <bar>`。
  否则 0.0006 被当成 N/sqm（≈0 bar），塔内压降≈0，下游进料压力不足产生警告。
- 压力级联示例（无泵）：STRIP 塔顶 0.31 → C1 塔顶 0.30（STR-BOT 塔底 0.34 足够进 C1 第 38 级 0.322）；
  C2 0.24 → C3 0.20 → C4 0.10（真空）。
- 循环回料需升压时用泵（P-EB：C2-BOT 0.24 → 0.52），泵属压力变送装置。

## 6. 警告清零清单（实战排雷）

| 警告代码/文本 | 原因 | 解决 |
|--------------|------|------|
| SECPO.6 INVALID SECTION ID PR/UN | PROPERTIES 段写了 `PENG-ROB PR` / `UNIQUAC UN` | 去掉 PR/UN |
| ZERO FEED (ITER 0) | 撕裂流股无初值 | STREAM 段给 EB-REC/H2O-REC/MIX-OUT/STR-V 初值 |
| WEGSTN2.1 VARIABLES MISSING | 撕裂流股零流量 | 同上 |
| UDL03A.7260 FEED PRESSURE LOWER THAN STAGE | 循环/进料压力低于塔级 | DP-STAGE/DP-COL 标 <bar>；FL2 等压；调 P-SPEC |
| UDL03.6 DESIGN SPEC middle loop not converged | 塔设计规定收敛难 | 调整 VARY 范围、TOL-SPEC；塔压力合理 |
| MOLE FRACTIONS NORMALIZED | STREAM 初值未归一 | 用组分 MOLE-FLOW 且总和匹配 |
| 2041 cannot open | 手写段位置/语法错误 | CONDENSER=NONE 进料第 1 级；TEAR 在 CONV-OPTIONS 内会 2041，放文件末尾 |

## 7. 验证结果（本案例）

- STY-PROD 306.4 kmol/h ≈ 31 969 kg/h，质量纯度 99.8% ≈ 25.6 万吨/年。
- 质量衡算闭合偏差 0.000%（含 BZ-RAW/TOL-PROD/TAR/FUELGAS 全部出料）。
- .his：0 Severe / 0 Error / 0 Warning；.apwz/.bkp/.inp 重开复算一致。
