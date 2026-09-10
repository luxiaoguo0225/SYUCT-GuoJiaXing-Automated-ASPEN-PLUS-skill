# Calculator（Flowsheeting Options）调用指南

> 适用版本：Aspen Plus V14（COM `Apwn.Document` + `.inp`/`.bkp`/`.apwz`）。
> 结论先行：**Calculator 不是单独模块，而是 `Flowsheeting Options → Calculator` 功能类别（与全局 Design Spec 平级）**。
> 最可靠、经验证的调用方式：**在 GUI 导出的完整 `.inp` 中直接书写 `CALCULATOR` 段**，再 `InitFromFile2` 打开运行。
> 已由用户提供的实际案例（`1全流程模拟(无节能技术，无换热网络).bkp`，内含 `C-1`/`H2O` 两个计算器）验证。

## 1. 典型用途

实现"新鲜补加 = 总需要 − 循环量"，例如乙苯脱氢制苯乙烯流程中：

- `FRESH-EB = 总EB进料(514) − 未反应乙苯循环量`
- `FRESH-H2O = 总水进料(3633) − 工艺水循环量`

用户案例原文（官方可解析格式，两段完整示例）：

```text
CALCULATOR C-1
    DEFINE A MOLE-FLOW STREAM=S127 SUBSTREAM=MIXED  &
        COMPONENT=C6H6 UOM="kmol/hr"
    DEFINE B MOLE-FLOW STREAM=S107 SUBSTREAM=MIXED  &
        COMPONENT=C6H6 UOM="kmol/hr"
    DEFINE C MOLE-FLOW STREAM=S128 SUBSTREAM=MIXED  &
        COMPONENT=C6H6 UOM="kmol/hr"
F     B=4080-A-C
    READ-VARS A C
    WRITE-VARS B

CALCULATOR H2O
    DEFINE A MOLE-FLOW STREAM=S213 SUBSTREAM=MIXED  &
        COMPONENT=H2O UOM="kmol/hr"
    DEFINE B MOLE-FLOW STREAM=S215 SUBSTREAM=MIXED  &
        COMPONENT=H2O UOM="kmol/hr"
F     B=6600-A
    READ-VARS A
    WRITE-VARS B
    EXECUTE BEFORE BLOCK M203
```

## 2. 关键语法（按用户案例与官方导出格式）

- 段头：`CALCULATOR <ID>`，ID 建议 ≤ 8 字符（长 ID 会被截断，如 `H2O-MAKEUP` → `H2O-MAKE`）。
- `DEFINE <var> <简写类型> STREAM=<流股> SUBSTREAM=MIXED COMPONENT=<组分> UOM="kmol/hr"`
  - 简写类型直接用 `MOLE-FLOW` / `MASS-FLOW` / `MASS-DENSITY` 等，**不需要** `STREAM-VAR ... VARIABLE=` 长写法（长写法在 cumene 案例出现过，但简写 + `COMPONENT=` 是用户案例验证过的格式）。
- `F <Fortran 语句>`：一行或多行 Fortran 计算体。
- `READ-VARS <var1> <var2> ...`：输入变量（从流程读取）。
- `WRITE-VARS <var>`：输出变量（写回流股输入）。
- `EXECUTE BEFORE BLOCK <模块>`：指定执行时机（如混合器 M203 之前）。
- 段位置：放在 `EO-CONV-OPTI` 之后、`CONV-OPTIONS` 之前（与官方导出一致）。

## 3. 经验证的工作流（推荐）

1. **从 GUI 导出的完整 `.inp` 出发**（`Export(4, ...)` 或已交付的 `*_exported.inp`），不要从手写精简 `.inp` 直接塞 `CALCULATOR` 段。
   - 手写精简 `.inp` + `CALCULATOR` 段 → Aspen 转换器报 **2041 无法打开**。
   - GUI 导出格式（含 `DYNAMICS`、`MODEL-OPTION`、`DATABANKS`、`PROP-SOURCES`、`SOLVE`、`EO-CONV-OPTI` 等全套段落）→ 可正常解析。
2. 用文本替换在 `EO-CONV-OPTI` 后插入 `CALCULATOR` 段（注意保持 `\r\n` 换行、只插入一次，避免重复 `CONV-OPTIONS`）。
3. `InitFromFile2(inp, True)` 打开 → 应看到 `\Data\Flowsheeting Options\Calculator` 下计算器个数正确。
4. `Run2(False)` 运行 → 读取 `\Data\Streams\<被写流股>\Output\RES_MOLEFLOW` 验证计算器是否生效（如 FRESH-EB = 514 − 循环量）。
5. 从运行好的实例导出 `.apwz`/`.bkp`/`.rep`。

**注意 COM 状态污染**：同一进程连续 `InitFromFile2` 多个文件时，失败后的后续"OPEN OK"可能是假象（旧文档状态残留）。验证每个变体时**用独立 Python 子进程**逐个打开，避免误判。

## 4. 涉及循环/撕裂流股时的额外要求（经验证）

- FSPLIT 分流器语法必须用**流股名**：`FRAC <出口流股名> <分数>`（如 `FRAC EB-REC 0.95`）。
  - ❌ `PARAM FRAC 1 0.95`（序号写法）→ 2041。
  - ✅ `FRAC EB-REC 0.95`（官方导出写法）→ 可解析。
- 撕裂（循环）流股必须显式声明：在文件末尾加
  ```text
  TEAR EB-REC
  TEAR H2O-REC
  ```
- 撕裂流股**不要**在 `STREAM` 段同时给初值（会 2041 冲突）；初值由 Aspen 迭代收敛（可配 `CONV-OPTIONS PARAM TEAR-METHOD=WEGSTEIN` 或 BROYDEN）。
  - 用户案例导出的 `.inp` 中循环流股（如 `S213`）有 `STREAM` 初值，是因为那是 Aspen 导出时自动写入的元数据；手写时不要照抄这一条。
- 最小验证案例（Mixer + FSPLIT + TEAR + CALCULATOR）已跑通：`M1(FRESH, REC→MIX) → SPLIT(MIX→PROD, REC)` + `TEAR REC`。

## 5. COM 树结构（只读参考）

```text
\Data\Flowsheeting Options\Calculator\<ID>\Input
    METHOD=0                (Fortran)
    BLK_ID / BLOCK_TYPE / WHEN   (EXECUTE BEFORE BLOCK 的存储位置)
    FORTRAN_EXEC/#1 ...     (F 语句行)
    READ_VAR/#1 ...         (输入变量名)
    WRITE_VAR/#1 ...        (输出变量名)
    FVN_STREAM/<var>        (变量所在流股，行名=变量名)
    FVN_SUBS/<var>          (MIXED)
    FVN_COMPONEN/<var>      (组分)
    FVN_VARTYPE/<var>       (MOLE-FLOW 等)
    FVN_PHYS_QTY/<var>      (MOLE-FLOW 等)
    FVN_UOM/<var>           (kmol/hr)
\Data\Flowsheeting Options\Calculator\<ID>\Output
    READ_VAL / WRITE_VAL    (运行后的读/写值)
```

## 6. 已排除的失败路径（不要再浪费时间）

- ❌ 手写精简 `.inp` 中直接加 `CALCULATOR` 段 → 2041。
- ❌ COM 创建：`Calculator.Elements.Add("CALC1")` 能建出空壳，但内部变量表（`FVN_*`/`FORTRAN_EXEC`/`READ_VAR`/`WRITE_VAR`）用 `InsertRow`/`NewChild`/`Add` 均无法填充（"该功能尚未生效"/AE_UNKERR）→ 不可行。
- ❌ `apwn.RunScript(...)` 探针无副作用（疑似未真正执行或环境隔离）→ 不可靠。
- ❌ 用流程级 `DESIGN-SPEC` 替代 Calculator 满足"必须用计算器"的需求 → 用户明确拒绝。
- ❌ `.inp` 转换器对空 `CALCULATOR CALC1`（无 DEFINE/F/READ/WRITE）也拒收 → 计算器必须写完整。

## 7. 学习模板文件

- 用户案例：`%USERPROFILE%/Desktop/无节能无换热/1全流程模拟(无节能技术，无换热网络).bkp`
  （含 `CALCULATOR C-1`、`CALCULATOR H2O`；苯烷基化 + 乙苯脱氢联合流程）
- 本 skill 验证产物：`styrene_openloop` 系列（开环）与 `styrene_closed_calc*.inp`（闭环+计算器，含 TEAR）。
