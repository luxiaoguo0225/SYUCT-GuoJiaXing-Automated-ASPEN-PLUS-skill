# Aspen Plus Automation：经验教训（2026-09-29）

本文件记录一次真实交付失败后的强制改进项，必须与 `references/aspen-input-completeness-and-delivery-lessons.md` 一起阅读。

## 一句话结论

**“能运行”不等于“输入完整”；交付 BKP 前必须用 `NextIncomplete()` 证明所有输入对象完整，并在独立目录冷启动验证。**

## 必须记住的十件事

1. 交付前必须执行 `NextIncomplete()`，合格结果必须是 `('', 0)`。
2. `.his` 无 ERROR 不代表输入完整；必须同时看 incomplete、块状态和收敛块。
3. 编辑 `.inp` 时禁止混合 CRLF/LF；`&` 续行之间不能出现空行。
4. 多组分 SEP 必须用一条 `FRAC` 列出 `COMPS` 和等长 `FRACS`，组件顺序最好与 `COMPONENTS` 一致。
5. 未列出的组分可能默认进入错误出口，导致 Henry 参数缺失、DIMH2 进入 N2 排放流等问题。
6. 不要给不需要相平衡的 SEP 随意添加 `FLASH-SPECS`。
7. 旧 BKP 不等于修复后的 BKP；修完 `.inp` 必须重新导出 BKP。
8. 新 BKP 必须在独立目录冷启动运行，并再次检查 `NextIncomplete()`。
9. `WARNING WHILE EXECUTING CONVERGENCE BLOCK` 不能忽略，必须解决或如实报告。
10. 不得在输入不完整、循环未收敛或结论未经校核时声称“已交付”。

详细规则、错误链、修复链与交付清单见：

`references/aspen-input-completeness-and-delivery-lessons.md`
