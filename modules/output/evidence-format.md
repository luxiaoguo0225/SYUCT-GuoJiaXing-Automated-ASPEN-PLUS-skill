# 输出检查的结构化记录

I01保存任务合同；合同包括 `task_id`、用户交付 `requirements`、`required_checks`、需要保护的 `original_files`。每项有 `id、description、kind、owner_modules`，M模块编号只能M01–M15。合同以check_delivery.contract_digest的规范JSON算法计算SHA-256，O01候选记录同一个 `contract_sha256`；修复不得删改要求/门槛或更新为更宽松合同。

候选包含 `task_id、contract_sha256、iteration_id、run_id、current_input、results`。`current_input`为实际输入文件的`path/sha256`；纯读取/说明任务可没有Aspen运行，`run_id`为null，但仍要标当前输入和输出版本。

每个结果以合同项目id为键，记录 `status`、必要的 `method/conclusion` 与 `evidence`。证据条目必须有 `path、sha256、iteration_id、run_id、input_sha256`，绑定本轮字节和输入。重新运行/修改输入后使关联旧证据失效，必须重新生成，不能只改标签沿用旧结论。

| kind | 机器检查范围 | 合同附加字段/要求 |
|---|---|---|
| file | 文件存在、非空、哈希一致、要求的扩展名 | extension；能打开/可编辑性另设review，不由扩展名证明 |
| numeric | 从证据JSON的value_key读取实际值，按ge/le/eq比较target，并核unit_key与unit | value_key、target、comparison；有量纲/基准时给unit/unit_key，不能用人工PASS覆盖不达标数值 |
| history | 当前唯一.his的编码、摘要、实际消息；无摘要轨迹须补同运行正常.rep，未知格式不通过 | evidence包含本次日志及需要的报告；必须有真实run_id |
| review | 方法、结论、证据身份完整性 | method/conclusion必须来自实际独立检查；脚本不代替科学推理、实验物性、设备评级或GUI可见验证 |

NOT_APPLICABLE仅在合同预先allow_na=true且有理由时接受，不能为规避失败临时更改；未知/缺失为UNVERIFIED。合同至少有用户要求和必需检查，空合同不能通过。

项目工作目录调用：

```powershell
python "<skill>/scripts/check_delivery.py" --contract "work/task-contract.json" --candidate "work/candidate.json" --report "work/check.json"
```

输出 `next_state=RUN` 时，按issues中的 `issue_id/check_id/owner_modules/recheck` 修复和重新取证：物性/范围问题路由P00，其余路由R00，再经当前准入及O01/O02；`DELIVER`只表示所声明合同及检查范围均有当前证据，不能超出审查/试验实际范围宣传工业有效性。合同真实性、完整捕捉用户要求及review推理仍由执行者负责。

## 即时检查合同

物性独立前置轨道/动力学即时检查按[阶段格式](../shared/validation-stages.md)，使用validation_stage=properties/kinetics及固定检查id；最终标final并登记validation_stages_required及EARLY-* review项。只有实际证据和完整方法/结论可支持PASS，不引入agent身份或隔离条件。

正式流程的物性阶段候选须包含property_snapshot={path,sha256}，由五项P01证据共同引用。每次正式运行前独立回读当前物性子快照并调用[流程准入](../properties/index.md)。经授权的原生估算数值联算单列工作记录。旧阶段报告hash保留，实际输入或范围改变须重验。
