# 孙兰义教材第 7.4 节：精馏塔严格计算（RadFrac）

> 依据 `Example7.3a–7.3e-RadFrac.bkp` 的 `RADFRAC`、Design Spec、Calculator 和 Sensitivity 配置整理。本文说明“第 7.4 节严格计算”与用户要求的“严格塔 + 灵敏度分析”是同一工作流，不是额外的经济优化。

## 1. 严格计算的范围

第 7.4 节的严格计算包括：

- 用 RadFrac 严格求解平衡级、物料衡算和能量衡算；
- 设置总板数、进料板、塔顶/塔底产品板；
- 设置冷凝器/再沸器类型和压力剖面；
- 用 Design Spec 满足产品纯度或回收率；
- 用 Vary 调节回流比、采出率等操作变量；
- 检查收敛状态、温度/流量剖面和产品规定误差；
- 在严格塔基础上再做灵敏度分析。

这与用户要求的工作流一致：

```text
DSTWU 简洁塔基础参数
→ RadFrac 严格塔
→ Design Spec/Vary 使产品规定收敛
→ Sensitivity S-1/S-2
→ 判断最佳理论板数、进料板和最小回流比
```

`DSTWU` 只是初始设计，RadFrac 第 7.4 节严格计算才是对塔的正式校核和优化基础。

## 2. Example7.3a：基本严格塔

`Example7.3a-RadFrac.bkp` 的配置：

```text
RadFrac:
  NSTAGE = 65
  Feed = FEED, stage 25
  Products = ETHBZ-PD stage 1 / STYR-PD stage 65
  Condenser = TOTAL
  P-SPEC = stage 1: 6 kPa / stage 65: 6.7 kPa
  COL-SPECS = D:F=0.5853, DP-COL=7.3 kPa, MOLE-RR=5.11
```

特点：

- 不设 Design Spec；
- 直接给定 `D:F` 和 `RR`；
- 用来验证给定的初值和严格塔收敛；
- 如果产品纯度不能满足，进入 7.3b。

## 3. Example7.3b：严格塔 + 产品 Design Spec

同一 `RADFRAC` 增加：

```text
Design Spec 1:
  MASS-FRAC = 0.99, component=EB, stream=ETHBZ-PD

Design Spec 2:
  MASS-FRAC = 0.997, component=STYRENE, stream=STYR-PD

Vary 1:
  MOLE-RR = 4 … 8

Vary 2:
  B:F = 0.4 … 0.43
```

作用：

- 用两个操作变量同时满足塔顶和塔底产品规定；
- 产品规格固定后，不同设计或不同灵敏度工况才可比较；
- 严格塔的可行性判断必须在所有工况收敛后进行。

不能把例题中的 `0.99`、`0.997`、`65`、`25` 直接照搬到用户塔。用户塔要使用用户自己的产品规定、进料组成和压力条件，只学习这一套配置结构。

## 4. Example7.3c：严格塔灵敏度，理论板数 × 进料板

在 7.3b 的严格塔上增加 Sensitivity：

```text
Vary 1: NSTAGE = 62 … 80 step 2
Vary 2: FEED-STAGE = 20 … 38 step 2
Tabulate: QREB
```

关键点：

- 基准 RadFrac 的 `NSTAGE` 等于灵敏度上限 80；
- 严格塔的最优进料板要在每个 `NSTAGE` 下重新确定；
- 二维全组合必须确认 `SERIES=NO`；
- 从 `SNS_TAB` 读取 Aspen 严格灵敏度结果，失败行用 `ROWSTAT=0` 过滤；
- 画图时 X=`FEED-STAGE`，系列=`NSTAGE`，Y=`QREB`。

## 5. Example7.3d：严格塔灵敏度，求最小回流比

配置：

```text
Calculator:
  FSTAGE = 0.43 * NSTAGE
  Execute before RADFRAC

Sensitivity:
  Vary NSTAGE = 60 … 180 step 20
  Tabulate RR
```

- 进料板跟随 `NSTAGE`，不自由扫描；
- 每个 N 都要求满足同一产品规定；
- 当相邻 N 的 `|ΔRR|/RR <= 0.1%` 时，末段 RR 作为严格塔 `R_min` 的工程估计；
- 本例计算结果趋近约 `RR=4.29125`。

如果改变理论板数导致塔底板编号变化，还要让塔底采出级跟随 `NSTAGE`；正确变量为：

```text
PROD-STAGE + PRODUCTS + 塔底产品流股 ID
```

不是 `STAGE`。

## 6. Example7.3e：小范围 RR–N 灵敏度

`Example7.3e-RadFrac.bkp` 是同一类严格塔灵敏度：

```text
Calculator:
  FSTAGE = 0.43 * NSTAGE

Sensitivity:
  Vary NSTAGE = 36 … 60 step 2
  Tabulate RR
```

它用于较短 NSTAGE 范围内观察 RR 降低趋势，适合作为 7.3d 的补充。

## 7. 应用到用户塔的顺序

1. 用户用自己的进料组成、压力、产品规定建立 RadFrac。
2. DSTWU 提供 `NSTAGE/RR/feed stage` 初值。
3. 按 7.3a 设置 RadFrac 基础严格塔。
4. 按 7.3b 加产品 Design Spec 和 Vary。
5. 收敛后按 7.3c 做 `NSTAGE × FEED-STAGE → QREB`。
6. 按 7.3d/e 做 `NSTAGE → RR` 的 `R_min` 分析。
7. 用户的“最佳理论板数、进料板、回流比”就由这两个灵敏度结果分别确定。
8. 只有在用户明确要求时才继续做设备成本或 TAC 优化。

## 8. 与范围规则的关系

- 用户说“精馏塔严格计算”或“按第 7.4 节做”时，RadFrac + Design Spec + Vary + 严格收敛检查属于明确要求，必须执行。
- 用户说“简洁塔确定基础参数”时，只做 DSTWU。
- 用户说“做灵敏度/优化最佳板数/进料板/回流比”时，第 7.4 节的 S-1/S-2 严格灵敏度属于要求范围内。
- 用户没有明确要求时，不把严格塔进一步扩展为经济/TAC 全局优化。

## 9. 两份 Aspen 文件交付模式（2026-09-25 验证）

当用户要求同时交付“最佳理论板数/进料板”和“该设计点最小回流比”时，按两份独立 Aspen 文件交付：

### 文件 1：最佳理论板数 × 进料板
```text
Sensitivity: S-1
Vary 1: NSTAGE
Vary 2: FEED-STAGE
Tabulate: QREB, RR, QCOND
```
- 用 Aspen 二维严格灵敏度找每个 NSTAGE 下的 QREB 最小点。
- 用 N×RR 或用户指定的经济目标选择推荐 NSTAGE 和 FEED-STAGE。
- 数据必须来自 SNS_TAB，失败行用 ROWSTAT=0 过滤。

### 文件 2：固定第一份最佳点的最小回流比
当用户说“直接用第一次结果”或“不再计算其他理论板数”时：
```text
固定 NSTAGE = 第一份最佳值
固定 FEED-STAGE = 第一份最佳值
Aspen Sensitivity 单点运行
输出 RR、QREB、QCOND
```
- 不扫描其他 NSTAGE。
- 已验证的稳健做法：保留 Sensitivity 块名 `S-1`，把 NSTAGE 和 FEED-STAGE 的范围都固定为同一个值，例如 `NSTAGE=90…90`、`FEED=45…45`。
- 不要为了单点交付额外改名 Sensitivity 块或添加不必要的 Calculator；这些修改容易使输入失效。
- 第二份得到的是“该已选严格塔设计点满足产品规定所需的最小回流比”，不是热力学渐近 R_min。
- 若用户要求的是教材 7.3d 的渐近法，才改为固定 F/N 比值并变化 NSTAGE；两种要求不能混用。

### 已验证的 C1/B6 结果
```text
最佳点 1: NSTAGE=90, FEED=45, RR=9.18295947, QREB=21283.0944 kW
最佳点 2（单点复核）: RR=9.1824973, QREB=21282.1255 kW, QCOND=-21284.7181 kW
```
