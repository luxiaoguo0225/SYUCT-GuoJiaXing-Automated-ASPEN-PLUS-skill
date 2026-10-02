# Sensitivity 范围、全组合配置与数据来源边界

> 依据 2026-09-25 对 `Example7.3c-RadFrac.bkp`、`Example7.3d-RadFrac.bkp` 及苯乙烯 C1/B6 复现过程整理。本文是高优先级工作边界，优先于任何“自动扩大优化”的倾向。

## 1. 用户范围边界（最高优先）

- 用户只要求“简洁塔确定基础参数”时，只交付 DSTWU 基础参数，不擅自开展严格塔多工况优化、最小回流比渐近分析、全塔经济核算或大量 Sensitivity 扫描。
- 不得把“学案例”自动扩展成“对用户流程做完整经济优化”。详细优化必须由用户明确要求。
- 用户要求“继续/优化”时，也要先按用户刚刚明确的范围执行；不得再用额外目标替换用户目标。
- 若已获得的数据是 COM 逐点重算而非 Aspen Sensitivity 结果，不得在交付中把它称为 Aspen Sensitivity 数据或灵敏度图。

## 2. DSTWU 基础参数（默认交付）

DSTWU 负责提供：轻/重关键组分、塔顶轻关键回收率、塔底重关键回收率、`PTOP/PBOT`、冷凝器类型、`N-RR` 表、`N×RR` 最小点对应的理论板数和回流比，以及 DSTWU 给出的进料板位置。

`N×RR` 最小值只是简洁塔法的基础参数，不等于严格塔的全局经济最优。除非用户明确要求，不得继续扩展到 TAC 优化。

## 3. Sensitivity 的两种独立任务

### 3.1 第一套：理论板数 × 进料板 → QREB

Aspen `S-1`：

```text
Vary 1: Block-Var, Block=RADFRAC, Variable=NSTAGE, Sentence=PARAM
Vary 2: Block-Var, Block=RADFRAC, Variable=FEED-STAGE, Sentence=FEEDS, ID1=FEED
Tabulate: QREB (and RR/QCOND if needed)
```

关键配置：

- `SERIES = NO` 才会得到真正的二维全组合。实测 `SERIES=YES` 会导致 Aspen 只做单变量逐项扫描（OFAT），SNS_TAB 行数不足。
- 基准 RadFrac 的 `NSTAGE` 必须等于 Sensitivity 中 `NSTAGE` 的上限。案例 7.3c 的基准 NSTAGE=80，Sensitivity 上限也是 80；否则高 N 工况或联合工况会失败。
- 基准进料板应落在 Sensitivity 的进料板范围内。
- 改变 `NSTAGE` 时，塔底采出级必须跟随 `NSTAGE`。正确 Calculator 变量是：

```text
DEFINE BOT:
  VARTYPE  = BLOCK-VAR
  BLOCK    = RADFRAC
  VARIABLE = PROD-STAGE
  SENTENCE = PRODUCTS
  ID1      = 塔底产品流股
FORTRAN: BOT = NSTG
EXECUTE BEFORE RADFRAC
```

- 不能使用 `Variable = STAGE`，它会触发“必须指定变量/必须指定语句”错误。
- 若不做 Calculator，至少把塔底采出级设在 NSTAGE 上限，并确认 Aspen 在每个 N 下把塔底采出映射到有效末级；交付前必须逐点检查。
- 运行完成后从 `.bkp` 读取 `DSET SENSITIVITY ... SNS_TAB`，并用 Aspen 输出 `ROWSTAT=0` 过滤成功行；失败行不得参与最优值或曲线。
- 只有 `SNS_TAB` 中的数据才可称为 Aspen Sensitivity 数据。外部绘图若使用该表，必须在交付说明中标注数据源。

### 3.2 第二套：理论板数 → RR，求最小回流比

Aspen `S-2`：

```text
Calculator:
  FEED-STAGE = ratio * NSTAGE
  (必要时 BOT = NSTAGE)

Vary:
  NSTAGE

Tabulate:
  RR
```

- 进料板由 Calculator 联动，不再自由扫描；必要时将 `FEED-STAGE` 的 Sensitivity Vary 设为 DISABLE。
- 每个 `NSTAGE` 都必须重新满足同一套产品规定。
- 当相邻两个 N 的 `|ΔRR|/RR <= 0.1%` 时，末段 RR 可作为 `R_min` 的工程估计。
- 示例 7.3d 使用 `FSTAGE = 0.43 * NSTAGE`。用户明确指定比值时按用户值；否则可用案例得到的比例并说明来源。
- 不用把能源最优当成经济最优；回流比、板数、设备成本和运行成本的目标不同，除非用户明确要求经济优化。

## 4. 运行与绘图边界

- COM 优先：建立输入、设置 Vary/Tabulate、运行 Sensitivity、导出 `.bkp/.rep/.inp` 和读取 SNS_TAB。
- COM 不能生成 Aspen 原生 Plot Wizard 持久化对象时，才使用 Aspen GUI 的 Plot Wizard；不要调用 Computer Use。
- `.bkp` 主要保存输入和 SNS_TAB；原生图定义保存在 `.apw/.apwz` 的 `ApwnShellSettings`。
- 外部 PNG/PDF/SVG 只能作为结果展示，不得冒充 Aspen 原生图。
- 对失败工况、报警工况和未收敛工况必须显式过滤或标注，不能绘制成正常曲线。

## 5. 交付前检查

- Sensitivity 的 Vary 范围是否真正形成二维全组合；
- `SERIES` 设置是否与目标一致；
- 基准 `NSTAGE` 是否等于扫描上限；
- 塔底采出级是否随 `NSTAGE` 联动；
- SNS_TAB 行数是否等于有效组合数；
- `ROWSTAT=0` 是否已过滤；
- 数据源、目标函数和未执行范围是否在交付说明中写清楚。

## 6. 两份 Sensitivity 文件交付边界（2026-09-25）

- 第一份 S-1：`NSTAGE × FEED-STAGE` 全组合，用于求最佳理论板数和最佳进料板。
- 第二份 S-1 单点：固定第一份选出的最佳 `NSTAGE` 和 `FEED-STAGE`，只输出该设计点的 `RR/QREB/QCOND`。
- 用户明确说“不再计算其他理论板数”时，第二份绝对不能继续扫 NSTAGE。
- 单点 Sensitivity 的稳健写法是保留块名 `S-1`，把两个 Vary 范围分别固定为同一个值；实测这比新建或改名 S-2 块更稳定。
- 若用户明确要求教材 7.3d 的渐近最小回流比，才使用固定 `F/N` 比值并变化 `NSTAGE`；这是另一类任务。
