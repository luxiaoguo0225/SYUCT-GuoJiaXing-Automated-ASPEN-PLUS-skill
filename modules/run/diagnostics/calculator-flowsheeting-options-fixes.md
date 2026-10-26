# 从原案例/机制迁入的报错诊断

来源：calculator-flowsheeting-options.md。以下观察仅支持原文限定的版本、条件与已闭合范围；不提升为普遍故障原因或默认参数。

## 6. 已排除的失败路径（不要再浪费时间）

- ❌ 手写精简 `.inp` 中直接加 `CALCULATOR` 段 → 2041。
- ❌ COM 创建：`Calculator.Elements.Add("CALC1")` 能建出空壳，但内部变量表（`FVN_*`/`FORTRAN_EXEC`/`READ_VAR`/`WRITE_VAR`）用 `InsertRow`/`NewChild`/`Add` 均无法填充（"该功能尚未生效"/AE_UNKERR）→ 不可行。
- ❌ `apwn.RunScript(...)` 探针无副作用（疑似未真正执行或环境隔离）→ 不可靠。
- ❌ 用流程级 `DESIGN-SPEC` 替代 Calculator 满足"必须用计算器"的需求 → 用户明确拒绝。
- ❌ `.inp` 转换器对空 `CALCULATOR CALC1`（无 DEFINE/F/READ/WRITE）也拒收 → 计算器必须写完整。
