# 从原案例/机制迁入的报错诊断

来源：heat-carrier-and-salt-properties.md。以下观察仅支持原文限定的版本、条件与已闭合范围；不提升为普遍故障原因或默认参数。

## 4. Aspen 写入用户物性的实测限制（重要）
**结论：纯脚本/文件注入不足以让 Aspen 采用新的纯组分物性。**
| 尝试（V14 实测） | 结果 |
|---|---|
| `.bkp` 末尾（`"\@"` 前）追加 `? PROPERTIES PARAMETERS UNARY "T-DEPENDENT" "CPDIEC-1"` | 能开能跑，cp/ρ 完全不变 |
| 单位集改成案例实际用的 `SET1_MOLE`；插到 `? PROPERTIES PARAMETERS BINARY` 之前 | 仍不变 |
| 换 `CPLPOL`/`CPLDIP`/`DNLDIP` | 仍不变（DNLDIP 7 参数形式还会 2041） |
| 官方 `Export(4)` 的 `.inp` + `PROP-DATA CPDIEC-1 / PROP-LIST CPDIEC / PVAL KNO3 …` | 解析通过、能跑，cp 仍不变 → **数据存下却未被路由** |
| COM 树可写节点（`\Data\Properties\Data`、`Estimation`、`Property Methods\<M>`） | 无可写输入（Data 空、Estimation 只有 Compare、方法对象只有 CC Nodes） |

**正确路径（GUI，必须）**：① `Properties → Data → Prop-Data` 新建数据集（Model 选 CPDIEC 或 CPLDIP 填 cp、DNLDIP 填密度，分别指定组分）；
② `Properties → Model Selection` 把该模型排到**第一**；③ Run 后用 §1 的方法**复测 cp/ρ**确认生效。
辅助事实：`AprSystem\Engine\Xeq\pp1.dat` 给模型名与参数个数（CPDIEC 3、CPLDIP 7、CPLPOL 7、DNLDIP 7、MULDIP 7、RKTZRA 1）；
数据集第二字段是**单位集 ID**（本例 `SET1_MOLE`），写错会静默忽略。
