# 从原案例/机制迁入的报错诊断

来源：three-component-thermal-coupling-case.md。以下观察仅支持原文限定的版本、条件与已闭合范围；不提升为普遍故障原因或默认参数。

## 3. 隐藏报错与调和（重要）

- 现象：收敛、`BLOCK STATUS` normal，但 `.his` 有 **36 个隐藏报错**（MC 主塔 `UDL03.1` + `UDL03.3` 塔板干涸，瞬态首轮/DS 迭代低回流区触发）。
- `Reconcile()` API 单独使用**无效**（实测输入没更新、报错数不变；且按 run-verification-and-reconcile.md 经验它本就无法消除此类瞬态干板报错，效果保存后丢失）。
- **有效方案（"调和"落地）**：
  1. 把已收敛撕裂流结果写回流股输入（REF-PF 液 98.83℃/500 kg/h/0.198-0.802；REBV-PF 汽 123.65℃/2400 kg/h/0.886-0.114）；
  2. 收紧 DS-A `LIMITS "5" "8"`（避免 SECANT 扫到 RR≈3.7 干板区）；
  3. 初值 `MASS-RR=6.37`（解附近）。
  → `.his` **36 → 0/0/0**，产品与能耗不变；**全新打开 .bkp/.apwz 重跑仍 0/0/0（可持久）**。
- 验收口径：控制面板/`.his` 应显示 `No Warnings were issued during Input Translation` + `No Errors or Warnings were issued during Simulation`（用户 2026-08-31 指定标准）。
