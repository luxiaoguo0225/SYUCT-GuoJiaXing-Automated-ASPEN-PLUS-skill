# -*- coding: utf-8 -*-
import io
# 更新 SKILL.md：在 calculator 引用后加新文档引用
p = "SKILL.md"
c = io.open(p, encoding="utf-8").read()
anchor = "- See [references/calculator-flowsheeting-options.md](references/calculator-flowsheeting-options.md) for the verified Calculator (Flowsheeting Options) workflow: GUI-exported `.inp` + `CALCULATOR` section, `DEFINE` shorthand, `READ-VARS`/`WRITE-VARS`, `EXECUTE BEFORE BLOCK`, FSPLIT by stream name, and `TEAR` declarations."
new_ref = anchor + "\n- See [references/styrene-recycle-and-dewatering.md](references/styrene-recycle-and-dewatering.md) for water/aromatic systems: PR+UNIQUAC+HENRY+FREE-WATER properties (do NOT write `PR`/`UN` section IDs), FLASH3 three-phase cold recovery of noncondensables, stripper (CONDENSER=NONE, feed on stage 1) for dissolved water, Calculator-based EB/water recycle with tear-stream initial values, `<bar>` on DP-STAGE/DP-COL, and the warning-clearing checklist."
assert anchor in c, "anchor not found"
c = c.replace(anchor, new_ref, 1)
io.open(p, "w", encoding="utf-8").write(c)
print("SKILL.md updated")
# 更新中文分类索引
p2 = "中文分类索引.md"
c2 = io.open(p2, encoding="utf-8").read()
a2 = "| calculator-flowsheeting-options.md | **计算器(Flowsheeting Options)调用** | 已验证的 Calculator 调用路径：GUI 导出 .inp + CALCULATOR 段、DEFINE 简写、READ-VARS/WRITE-VARS、EXECUTE BEFORE BLOCK、FSPLIT 按流股名、循环 TEAR 声明；含失败路径与用户模板案例 |"
r2 = a2 + "\n| styrene-recycle-and-dewatering.md | **含水芳烃流程(苯乙烯闭环)** | PR+UNIQUAC+HENRY+FREE-WATER 物性、FLASH3 三相回收、汽提塔脱水、计算器循环+撕裂流股初值、DP 单位、警告清零清单 |"
assert a2 in c2, "index anchor not found"
c2 = c2.replace(a2, r2, 1)
io.open(p2, "w", encoding="utf-8").write(c2)
print("中文分类索引.md updated")
