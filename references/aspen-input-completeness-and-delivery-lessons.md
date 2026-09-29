# Aspen 输入完整性、BKP 交付与 SEP 分率规范教训

**日期**：2026-09-29  
**触发案例**：60 kt/a 1,3-PDO 动力学流程；H2PUR 被用户指出“输入不完整”，此前仍被错误交付。  
**适用版本**：Aspen Plus V14 已验证；同样适用于较新版本，但对象树路径需重新确认。

## 1. 最高优先级：交付前必须检查 `NextIncomplete`

仅检查 `.his` 的 `SEVERE ERROR / ERROR / WARNING` 不够。`.his` 可以没有错误，但输入对象树仍有 incomplete 节点；用户打开 BKP 时会直接看到模块未完成。

每次交付必须执行：

```python
n = app.Tree.FindNode(r"\Data").NextIncomplete("")
print(n)   # 合格结果必须是 ('', 0)
```

交付标准：

- `NextIncomplete()` 必须返回 `('', 0)`；
- 所有目标 RPlug / RadFrac / SEP 块状态为 0；
- `.his` 中 `SEVERE ERROR`、`TERMINAL ERROR`、`ERROR WHILE EXECUTING` 为 0；
- 若存在 `WARNING WHILE EXECUTING`，必须逐条判断，不能因为块状态为 0 就忽略；
- 冷启动交付 `.bkp` 后再次检查 `NextIncomplete()`，不能直接复用运行过 `.inp` 的内存状态。

## 2. `.inp` 换行与 `&` 续行：最常见的 incomplete 根因

**教训**：用 `Path.read_text()` 会把 CRLF 转成 LF；随后若在字符串中插入 `\r\n`，写回时会出现混合或 `\r\r\n`，在 `&` 续行之间产生空行。Aspen 会把空行当作续行终止，导致：

- 模块被标记 incomplete；
- 分率矩阵只解析到第一行；
- 打开时报 2041；
- 输入看似正确但对象树缺项。

**正确做法**：

```python
t = path.read_text(encoding="gb18030", errors="replace")
t = t.replace("\r\n", "\n")          # 先统一为 LF
# ... 用 \n 构造替换内容 ...
path.write_text(t, encoding="gb18030", newline="\n")
```

禁止：

- 在 CRLF 文件中混写 `\r\n` 与 `\n`；
- 在 `&` 后插入空行；
- 用 `Select-String`/编辑器自动格式化后不检查续行。

交付前可用：

```powershell
python -c "from pathlib import Path; b=Path('case.inp').read_bytes(); print(b.count(b'\r\n'), b.count(b'\n'))"
```

确认文件换行风格一致。

## 3. SEP 分率矩阵写法

Aspen 的 `SEP` 组件分离器需要把一个或多个组分显式分配到出口。推荐写法是**一条 FRAC 语句列出组件列表，再列出等长分率列表**：

```text
BLOCK H2PUR SEP
    PARAM
    FRAC STREAM=H2-PURE SUBSTREAM=MIXED COMPS=C3H6 C3H8 O2 N2 H2O ACR HPA PDO DIM &
        DIMH2 CO2 H2 ALLYL AH CAA AC CO FRACS=1.0 1.0 1.0 0.0 1.0 1.0 1.0 1.0 1.0 &
        1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0
```

要点：

1. `COMPS` 与 `FRACS` 数量必须完全一致；
2. 组件顺序最好与 `COMPONENTS` 段一致；
3. 未列出的组分默认可能进入另一个出口，这在 H2/N2 分离中会导致 DIMH2 进入 N2 排放流并触发 Henry 参数缺失；
4. 对“所有非目标组分回到主产品”的场景，应列出全部可能出现的组分，避免默认分流；
5. `&` 续行的下一行必须紧接，中间不能有空行；
6. 不要手工添加 `FLASH-SPECS`，除非确实需要。对 SEP 组件分离器，额外的 flash 规格可能导致对不需要闪蒸的流股做相平衡计算，从而触发 `HENRY CONSTANT MODEL ... MISSING FOR SUPERCRITICAL COMPONENT N2 WITH ALL SOLVENTS: DIMH2` 一类错误；
7. 若必须使用 `FLASH-SPECS`，先确认该流股中存在有效溶剂，并确认 Henry 参数齐全。

**H2PUR 本次失败链**：

```text
混合换行 + & 续行空行
  -> FRAC 矩阵未完整解析
  -> NextIncomplete = ('\\Blocks\\H2PUR', 1)
  -> 手工 FLASH-SPECS 触发 N2/DIMH2 缺失 Henry 参数
  -> 用户判定输入不完整并拒绝交付
```

**修复链**：

```text
统一 LF
  -> 一条完整 FRAC 语句（组件顺序与 COMPONENTS 一致，COMPS/FRACS 等长）
  -> 去掉不必要的 FLASH-SPECS
  -> NextIncomplete = ('', 0)
  -> 冷启动 BKP 后再次 NextIncomplete = ('', 0)
```

## 4. BKP 与 INP 同步规则

- `.inp` 修好后必须重新导出/另存 `.bkp`；不能把旧 BKP 当成已修复版本；
- 交付前把 BKP 复制到独立目录冷启动，而不是在原工作目录直接打开；
- 冷启动后重新导出一份 `.rep` 并捕获新的 `.his`；
- 交付目录中同时放 BKP、INP、REP、HIS 和说明书；
- 文件名中避免空格和逗号，防止某些 Windows/Aspen 路径问题；本次使用 `1,3-PDO_60kt_工业动力学版_输入完整版.bkp` 虽可打开，但更稳妥应写成 `1,3-PDO_60kt_工业动力学版_输入完整版.bkp` 这类无空格名称。

## 5. 收敛警告不能当作通过

本次最终完整版仍出现：

```text
WARNING WHILE EXECUTING CONVERGENCE BLOCK: "$OLVER02" (MODEL: "BRODYEN")
CONVERGENCE BLOCK $OLVER02 NOT CONVERGED IN 500 ITERATIONS
```

即使所有块状态为 0，也不能默认循环已可靠收敛。后续应：

- 检查 `$OLVER02` 的 tear 变量是否仍在漂移；
- 为 tear 流股提供更接近终值的初值；
- 提高 BROYDEN 最大迭代次数；
- 必要时改用 WEGSTEIN 或手动定义更合理的 tear 集；
- 在交付说明中如实报告收敛状态，不把“块状态 0”等同于“循环已收敛”。

## 6. 模块选择与用户沟通

- `SEP` 在 Aspen Plus 中常被用来表示 PSA/组分分离，但对用户而言它可能是“捷径模块”。若用户对模块真实性有要求，应优先考虑 Aspen Plus 中更真实的单元模型（膜、闪蒸、严格塔、用户模型等），或在说明中明确其物理意义；
- 用户明确说“不用管 SEP”时，仍需保证 SEP 输入完整，不能因为模块选择争议而跳过完整性检查；
- 不得在输入不完整时声称“已完成交付”；必须先解决 incomplete，再交付；
- 每个数值、物性和模块选择都要可追溯到用户要求、权威资料或明确标注的工程假设。

## 7. 交付前检查清单

```text
[ ] .inp 换行风格统一，& 续行无空行
[ ] 所有 COMPS / FRACS 数量一致
[ ] NextIncomplete() == ('', 0)
[ ] 所有目标块 BLKSTAT == 0
[ ] .his 无 SEVERE / TERMINAL / ERROR WHILE EXECUTING
[ ] 逐条检查 WARNING WHILE EXECUTING
[ ] 循环收敛块 $OLVER 已收敛
[ ] 导出了新的 BKP，而不是旧 BKP
[ ] 在独立目录冷启动 BKP 后再次通过以上检查
[ ] 交付目录包含 BKP / INP / REP / HIS / 说明书
```
