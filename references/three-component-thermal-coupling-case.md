# 三组分热耦精馏自建案例（Petlyuk 双塔等效，验证 2026-08-31）

> 系统：乙醇(A)/正丁醇(B)/1-己醇(C)，UNIQUAC；进料 2000 kg/h、25℃、2 bar、摩尔组成 0.2/0.6/0.2（B 最多、A≈C，符合文章推荐条件）
> 产品：D 乙醇 248.6 kg/h、侧线丁醇 1200 kg/h、B 己醇 551.4 kg/h，均 ≥99.9 wt%
> 结论速览：副塔零冷热负荷（真热耦）；vs 固定 RR=1.3 常规双塔再沸 -19.7%、冷凝 -25.6%；vs 近最小回流优化常规（54 板）能耗持平但省 1 台再沸器+1 台冷凝器
> 交付：`%USERPROFILE%\Documents\Codex\2026-08-31\a-b-b-c-a-c\outputs\`（thermally_coupled.* / conventional_baseline.* / conventional_refstyle.*）

## 0. 概念：热耦不是"在塔板上加热负荷"

- 三组分热耦精馏 = **副塔(预分塔 PF) + 主塔(MC)** 的 Petlyuk 双塔等效表示，**不是**"精馏塔+提馏塔"。
- PF：`CONDENSER=NONE REBOILER=NONE`、`COL-SPECS` 留空、只给 `P-SPEC` → 塔内汽液流量完全由耦合流股和进料决定，**不需要也不允许指定塔顶/塔底热负荷**（Q1/QN）。
- 耦合靠**两股循环流股（撕裂流）**，主塔热输入一次、在两塔间"重复利用"：
  - `REF-PF`（液相，MC 第 7 板 → PF 塔顶第 1 板）= 副塔的"冷凝回流"；
  - `REBV-PF`（汽相，MC 第 27 板 → PF 塔底第 20 板）= 副塔的"再沸蒸汽"；
  - 副塔顶 `V-PF`（汽）回主塔上部第 8 板；副塔底 `L-PF`（液）回主塔下部第 27 板。
- 验证：报告 PF `CONDENSER DUTY = 0`、`REBOILER DUTY = 0`，MC 才有负荷。

## 1. .inp 核心配置（可直接复用）

```
FLOWSHEET
    BLOCK PF IN=FEED REF-PF REBV-PF OUT=V-PF L-PF
    BLOCK MC IN=V-PF L-PF OUT=D B SIDE REF-PF REBV-PF

STREAM REF-PF                       ; 撕裂流初值：液相（<泡点）
    SUBSTREAM MIXED TEMP=98.83 PRES=1 MASS-FLOW=500.
    MASS-FRAC ETHAN-01 .198198 / N-BUT-01 .801791 / 1-HEX-01 1.1351E-05
STREAM REBV-PF                      ; 撕裂流初值：汽相（>露点）
    SUBSTREAM MIXED TEMP=123.65 PRES=1 MASS-FLOW=2400.
    MASS-FRAC ETHAN-01 2.066E-06 / N-BUT-01 .886360 / 1-HEX-01 .113637

BLOCK PF RADFRAC
    PARAM NSTAGE=19 ALGORITHM=NONIDEAL INIT-OPTION=STANDARD MAXOL=25 DAMPING=NONE
    COL-CONFIG CONDENSER=NONE REBOILER=NONE
    FEEDS FEED 10 / REF-PF 1 / REBV-PF 20
    PRODUCTS V-PF 1 V / L-PF 19 L
    P-SPEC 1 1.
    COL-SPECS                          ; 必须留空！

BLOCK MC RADFRAC
    PARAM NSTAGE=35 ALGORITHM=NONIDEAL INIT-OPTION=STANDARD MAXOL=200 DAMPING=NONE
    COL-CONFIG CONDENSER=TOTAL
    FEEDS V-PF 8 / L-PF 27             ; 轻汽进上部、重液进下部（接反会干板）
    PRODUCTS D 1 L / B 35 L / SIDE 13 L MASS-FLOW=1200. /
             REF-PF 7 L MASS-FLOW=500. / REBV-PF 27 V MASS-FLOW=2400.
    P-SPEC 1 1.
    COL-SPECS MASS-D=248.61 MASS-RR=6.37
    T-EST 1 78. / 35 156.

DESIGN-SPEC DS-A                        ; 产品规格走设计规定，RR 由 SECANT 求
    DEFINE XD MASS-FRAC STREAM=D SUBSTREAM=MIXED COMPONENT=ETHAN-01
    SPEC "XD" TO "0.999"
    TOL-SPEC "0.00001"
    VARY BLOCK-VAR BLOCK=MC VARIABLE=MASS-RR SENTENCE=COL-SPECS
    LIMITS "5" "8"                      ; 解在 6.37；收紧避免扫到低回流干板区

CONV-OPTIONS
    PARAM TEAR-METHOD=BROYDEN
```

- 侧线 `SIDE`/耦合流 `REF-PF`/`REBV-PF` 的流量用 `PRODUCTS ... MASS-FLOW=` 显式规定。
- 撕裂流：`TEAR-METHOD=BROYDEN` 自动识别 REF-PF/REBV-PF。
- 相态初值关键：REF-PF 给**液相**（<泡点）、REBV-PF 给**汽相**（>露点）；给反会闪错相态。

## 2. 调优经验（都实测过）

- **REBV-PF 是 B/C 分离瓶颈的主导变量**：2400 kg/h 是 ≥99.9% 达标临界点；2300 以下 B 己醇纯度掉到 ~95%。
- 侧线位置必须和 V-PF 进料板匹配：V-PF 在 8、SIDE 在 13 是平衡点；把 V-PF 下移（12/15）而 SIDE 跟着动会破坏 B/C 平衡。
- **MC 加到 40/45 板反而更差**：设计规定把 RR 压低（板多→乙醇分离容易）→ B/C 提馏段蒸汽不足。
- **REF-PF 加到 700 kg/h 更差**（副塔回流过大扰乱平衡）。
- 结论：回流比 × 再沸汽 × 侧线位置三者必须匹配，不是板越多越好。

## 3. 隐藏报错与调和（重要）

- 现象：收敛、`BLOCK STATUS` normal，但 `.his` 有 **36 个隐藏报错**（MC 主塔 `UDL03.1` + `UDL03.3` 塔板干涸，瞬态首轮/DS 迭代低回流区触发）。
- `Reconcile()` API 单独使用**无效**（实测输入没更新、报错数不变；且按 run-verification-and-reconcile.md 经验它本就无法消除此类瞬态干板报错，效果保存后丢失）。
- **有效方案（"调和"落地）**：
  1. 把已收敛撕裂流结果写回流股输入（REF-PF 液 98.83℃/500 kg/h/0.198-0.802；REBV-PF 汽 123.65℃/2400 kg/h/0.886-0.114）；
  2. 收紧 DS-A `LIMITS "5" "8"`（避免 SECANT 扫到 RR≈3.7 干板区）；
  3. 初值 `MASS-RR=6.37`（解附近）。
  → `.his` **36 → 0/0/0**，产品与能耗不变；**全新打开 .bkp/.apwz 重跑仍 0/0/0（可持久）**。
- 验收口径：控制面板/`.his` 应显示 `No Warnings were issued during Input Translation` + `No Errors or Warnings were issued during Simulation`（用户 2026-08-31 指定标准）。

## 4. 能耗对比（同进料、同产品规格）

| 方案 | 结构 | 再沸器 | 冷凝器 | 回流比 |
|---|---|---|---|---|
| 常规（固定 RR=1.3） | 21+17 板 | 754.7 kW | 581.3 kW | 1.3/1.3 |
| 常规（设计规定优化） | 30+24 板 | 603.8 kW | 430.5 kW | 0.80/0.67 |
| **热耦（本案例）** | PF 19 + MC 35 板 | **606.0 kW** | 432.6 kW | 6.37（主塔） |

- vs 固定 RR 常规：再沸 -19.7%、冷凝 -25.6%（对应文章"约 20%"）；
- vs 优化常规（同为 54 板）：能耗基本持平，但省 1 台再沸器 + 1 台冷凝器（设备投资下降）。
- 文章 20~40% 的前提是常规流程为"典型设计"；常规已近最小回流时热耦的能量优势被压缩，剩设备优势。
