# RadFrac：不同理论板数下的 QREB–进料位置曲线

> 来源模式：孙兰义《化工过程模拟实训——Aspen Plus 教程》第 2 版，例题
> `Example7.3c-RadFrac.bkp` 的 `Sensitivity S-1`。本文件只总结方法，不复制教材正文。

> 第7.4节严格计算与灵敏度配置的完整映射见 [sun-lanyi-ch7-4-radfrac-strict.md](sun-lanyi-ch7-4-radfrac-strict.md)。

## 1. 图形表达的内容

这类图通常是：

- 横坐标：理论进料板位置 `FEED-STAGE`；
- 纵坐标：再沸器热负荷 `REB-DUTY` 或 `QREB`；
- 每条曲线：一个固定的理论板数 `NSTAGE`；
- 每个点：在固定产品纯度/回收率规定下，重新求解回流比和采出率后的严格收敛结果。

因此它回答两个耦合问题：

1. 给定理论板数时，哪一个进料板位置使再沸器负荷最低；
2. 增加理论板数后，最低再沸器负荷如何下降，最佳进料板如何移动。

## 2. 例题 `S-1` 的设置

在 `Example7.3c-RadFrac.bkp` 中：

```text
Define/结果变量：
  QREB = Block-Var
  Block = RADFRAC
  Variable = REB-DUTY
  Sentence = Results
  Unit = kW

Vary 1:
  Block = RADFRAC
  Variable = NSTAGE
  Sentence = PARAM
  Lower = 62
  Upper = 80
  Increment = 2

Vary 2:
  Block = RADFRAC
  Variable = FEED-STAGE
  Sentence = FEEDS
  Stream = FEED
  Lower = 20
  Upper = 38
  Increment = 2

Tabulate:
  QREB
```

自由度不是被 Sensitivity 直接替代。每个工况仍由 RadFrac 的 Design Spec 和 Vary 重新收敛：

```text
塔顶 EB 质量分数 = 0.99
塔底 STY 质量分数 = 0.997
操作变量：回流比 RR、塔底/进料比 B:F
```

所以不同曲线之间比较的前提是：产品规格相同，且所有工况都真正收敛。若某个工况未收敛或有级干涸，
必须将该点标为无效或留空，不能把失败点的热负荷画进曲线。

## 3. Aspen GUI 生成步骤

1. 先建立并收敛一个 RadFrac 基准工况。
2. 进入 `Model Analysis Tools > Sensitivity`，新建 `S-1`。
3. 在 `Define` 页定义 `QREB`：
   - Category: `Block-Var`
   - Block: `RADFRAC`
   - Variable: `REB-DUTY`
   - Sentence: `Results`
4. 在 `Vary` 页加入 `NSTAGE`：
   - Block-Var，Block `RADFRAC`，Variable `NSTAGE`，Sentence `PARAM`
   - Range，Lower 62，Upper 80，Increment 2
5. 再加入 `FEED-STAGE`：
   - Block-Var，Block `RADFRAC`，Variable `FEED-STAGE`
   - Sentence `FEEDS`，Stream `FEED`
   - Range，Lower 20，Upper 38，Increment 2
6. 在 `Tabulate` 页选择 `QREB`。
7. 运行 Sensitivity。
8. 打开结果，用 Plot Wizard 设置：
   - X Axis: `FEED-STAGE`
   - Y Axis: `QREB`
   - Curves: group/series by `NSTAGE`
9. 检查每个点的 `BLKSTAT`、设计规定误差和各塔段流率后再导出图。

### 3.1 在 Aspen 内保存多曲线图（推荐）

- 二维全组合图使用 `SERIES = NO`；实测 `SERIES = YES` 会让 Aspen 变成单变量逐项扫描（OFAT），得不到完整的 `NSTAGE × FEED-STAGE` 网格。
- 基准 RadFrac 的 `NSTAGE` 必须等于 Sensitivity 中 `NSTAGE` 的上限，并将塔底采出级与 `NSTAGE` 联动。
- 运行 Sensitivity。
- 打开 Results，使用 Plot/Plot Wizard 生成 Results Curve。
- 将结果保存为 `.apwz`，不要把 `.bkp` 当作原生图的主交付文件；`.bkp` 主要保存输入和 SNS_TAB 数据，`.apwz` 才可靠保存 Aspen 工作区的原生 plot 定义。
- Aspen V14 保存后，`ApwnShellSettings` 中会出现 `ApwnPlotWizardScreenFactory`、`PlotID="Results Curve"`、`PersistXML` 及其 X/Y/series 定义。
- 复查 `PersistXML` 中的 `Xlab`、`Ylab`、`Nvars` 和 `Legend`，确认横轴是进料板、纵轴是再沸器负荷、系列是 NSTAGE。

### 3.2 2026-09-25 实测修正

- 二维全组合必须确认 `SERIES = NO`。`SERIES = YES` 可能只生成 OFAT 行。
- 基准 RadFrac 的 `NSTAGE` 应等于 Sensitivity 的 `NSTAGE` 上限；Example 7.3c 是基准 80、上限 80。
- 改变 `NSTAGE` 时，塔底采出级必须跟随。块变量正确写法是 `PROD-STAGE` + `PRODUCTS` + 塔底产品流股 ID，不是 `STAGE`。
- 从 `DSET SENSITIVITY ... SNS_TAB` 取 Aspen 灵敏度数据，并按输出 `ROWSTAT=0` 过滤失败行。
- 只有数据严格来自 `SNS_TAB` 时，外部绘图才能标注为“Aspen Sensitivity 数据图”。

## 4. 外部提取和绘图

Aspen 的 `.bkp` 会把灵敏度结果保存成 `DSET SENSITIVITY ... SNS_TAB` 数据集。项目脚本：

```powershell
python scripts/plot_radfrac_feedstage_sensitivity.py ^
  --bkp "Example7.3c-RadFrac.bkp" ^
  --outdir "outputs/example7_3c_sensitivity"
```

脚本输出：

- 长表 CSV：`NSTAGE, FEED_STAGE, QREB_kW`；
- 每个理论板数下的最优进料板与最小 QREB；
- 多曲线 PNG。

也可以先用 Aspen 导出结果表，再用 `--csv` 交给脚本绘图。

## 5. 例题结果的学习结论

从该例题的 `S-1` 数据可复算得到：

| NSTAGE | 最低 QREB 的进料板 | QREB_min / kW |
|---:|---:|---:|
| 62 | 26 | 5264.78 |
| 64 | 28 | 5111.00 |
| 66 | 30 | 4994.99 |
| 68 | 30 | 4883.34 |
| 70 | 32 | 4797.43 |
| 72 | 32 | 4718.27 |
| 74 | 34 | 4646.31 |
| 76 | 34 | 4593.66 |
| 78 | 36 | 4540.69 |
| 80 | 38 | 4502.65 |

趋势：

- 每个 `NSTAGE` 下，`QREB` 对进料板都呈 U 形，存在明确的最低点；
- 理论板数增加时，最低 QREB 下降，但边际收益递减；
- 最佳进料板随 NSTAGE 增大而向塔底方向移动；
- 因此不能固定一个经验进料板去比较不同理论板数，必须对每个 NSTAGE 重新优化 FEED-STAGE。

该例题基准工况 `NSTAGE=80, FEED-STAGE=25` 的 QREB 约为 4963.52 kW；在本扫描范围内，
`NSTAGE=80, FEED-STAGE=38` 约为 4502.65 kW，相差约 460.9 kW（约 9.3%），但进料板已经
移动到扫描区间的上边界，正式设计还需向外扩展扫描范围确认真正最小值。

## 6. 易错点

- 改变 `NSTAGE` 时，塔底产品板若固定为末端板，必须确认 Aspen 是否自动跟随最后一级；
  否则各 NSTAGE 工况并不是同一套有效设备结构。
- `NSTAGE` 是整数，不能用连续优化器直接在非整数级数上求解。
- 不能只比较 `QREB`：同时检查产品纯度、回收率、回流比、B:F、塔径/泛液和压降。
- 进料板最优值落在扫描边界时，必须扩大扫描范围，不能把边界点误报成内部最优。
- 颜色只表示 NSTAGE，不可把不同产品规格的曲线叠加在同一张图上而不说明。
## 7. 理论板数渐近法求最小回流比

`Example7.3d-RadFrac.bkp` 给出了另一类灵敏度图：横轴是理论板数 `NSTAGE`，纵轴是满足产品纯度所需的回流比 `RR`。

例题设置：

```text
Calculator C-1, execute before RADFRAC:
  FSTAGE = 0.43 * NSTAGE

Sensitivity S-1:
  Vary NSTAGE = 60 ... 180, step 20
  Tabulate RR = RADFRAC / RR / Results
  Design specs:
    ETHBZ-PD EB mass fraction = 0.99
    STYR-PD STY mass fraction = 0.997
```

判据：

- 每个 NSTAGE 都重新求解满足产品规定的 RR；
- 进料板必须随 NSTAGE 联动，而不是固定；
- 当连续两个 NSTAGE 的 RR 相对变化很小（例如 `|Delta R|/R <= 0.1%`）时，取末段 RR 作为最小回流比的工程估计。

例题复算结果：

| NSTAGE | RR | 相对变化 |
|---:|---:|---:|
| 60 | 5.863725 | — |
| 80 | 4.686599 | 20.0747% |
| 100 | 4.406491 | 5.9768% |
| 120 | 4.327987 | 1.7816% |
| 140 | 4.301193 | 0.6191% |
| 160 | 4.292556 | 0.2008% |
| 180 | 4.291246 | 0.0305% |

因此：

```text
R_min ~= 4.29125
```

若没有点满足变化阈值，应继续提高 NSTAGE 上限；不得把扫描上限直接当作已经收敛的 `R_min`。

配套脚本：

```powershell
python scripts/estimate_min_reflux_asymptote.py ^
  --bkp "Example7.3d-RadFrac.bkp" ^
  --threshold-pct 0.1 ^
  --outdir "outputs/example7_3d_min_reflux"
```
## 8. DSTWU：简洁塔法提供基础值

RadFrac 设计前的可靠基础值通常先由 Aspen `DSTWU` 简洁塔模型得到。DSTWU 的核心是 Fenske–Underwood–Gilliland 类近似：

- 物料衡算确定塔顶/塔底产品分配；
- Underwood 方程估算最小回流比 `Rmin`；
- Fenske 方程估算最少理论板 `Nmin`；
- Gilliland 关联 `N` 与 `R`；
- Kirkbride 关联估算进料板位置。

典型 DSTWU 输入需要：

- 轻关键组分和重关键组分；
- 轻关键组分在塔顶的回收率、重关键组分在塔底的回收率；
- 塔顶/塔底压力；
- 冷凝器类型；
- 实际回流比或 `R/Rmin` 倍数，或指定理论板数。

典型输出：

- `Rmin`、`Nmin`；
- 实际理论板数 `N`；
- 进料板位置；
- 塔顶/塔底流量和热负荷。

使用边界：

- DSTWU 结果只作为 RadFrac 的初值和设计范围，不能替代严格塔；
- DSTWU 的 `Rmin` 与 RadFrac 的高理论板数渐近值可能不同，原因包括物性、压力、回收率、产品规定和严格级平衡；
- 因此，例题 7.3d 中的 `Rmin约4.291` 应明确标记为**严格 RadFrac 渐近值**；如果另做 DSTWU，应单独报告其 shortcut `Rmin`。
### 8.1 DSTWU 合理理论板数：取 N × RR 最小值

DSTWU 在 `PLOT=YES`、`OPT-NTRR=RR` 时给出 `NSTAGE–RR` 表。把该表粘贴到 Excel，并新增：

```text
NxRR = NSTAGE * RR
```

以 `NSTAGE` 为横轴、`NxRR` 为纵轴作图，曲线最低点对应的 NSTAGE 就是简洁塔法推荐的合理理论板数；从同一行读取对应的 RR 和 DSTWU 给出的进料板位置。

原因：

- NSTAGE 增加会使塔高/设备费用增加；
- RR 增加会使冷凝器和再沸器公用工程增加；
- `N×RR` 的最低点是在简洁塔法的近似尺度上同时考虑塔板投资与回流能耗的折中点。

在 `Example7.1-DSTWU.bkp` 的 RR_TABLE 中复算得到：

```text
NSTAGE = 65
RR = 5.10317857
NxRR_min = 331.70660705
```

这只是该 DSTWU 输入条件下的简洁塔法最优。更换产品规定、压力、回收率或物性方法后，最低点会改变；最终还要用 RadFrac 做严格复核。脚本 `optimal_stages_from_dstw.py` 可自动解析 RR_TABLE、计算 N×RR 并输出最低点。