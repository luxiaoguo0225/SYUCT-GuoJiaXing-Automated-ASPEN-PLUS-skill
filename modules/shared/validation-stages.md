# 物性与动力学即时检查格式

本格式适用于同一会话的运行→检查→失败返回运行，不创建子agent，不需要执行者/验证者身份、隔离声明或额外verdict。模型副本、原始反馈、独立衡算及新COM冷重开仍按任务要求完成。

| validation_stage | 固定required_checks |
|---|---|
| properties | PROP-SOURCES、PROP-ZEROS、PROP-APPLICABILITY、PROP-PHYSICAL、PROP-READBACK，全部review |
| kinetics | EARLY-PROPERTIES、KIN-INPUT、KIN-RATES、KIN-LITERATURE、KIN-INDUSTRIAL、KIN-SELECTIVITY为review；KIN-RUN为history，必须有真实反应器run_id |
| final | validation_stages_required登记适用properties/kinetics，required_checks含相应EARLY-PROPERTIES/EARLY-KINETICS review |

所有固定项禁止allow_na和NOT_APPLICABLE。动力学依赖有效的物性检查；最终登记kinetics也必须登记properties。阶段合同与最终合同分开冻结，参数来源、公式、单位、范围及原始结果做证据，不削减用户最终要求。

```powershell
python "<skill>/scripts/check_delivery.py" --contract "work/stage-contract.json" --candidate "work/stage-candidate.json" --report "work/stage-check.json"
```

阶段通过返回CONTINUE（退出码0），失败/未验证返回RUN（退出码2）；只有final全部必需检查通过才DELIVER。默认未标记阶段的旧合同按final兼容。标定/工业数据不足不补成PASS；工具只查覆盖、身份和可识别证据，不自动证明物性或工业有效性。

最终生成当前关口有效性审计，比较实际参数/范围子快照，保留原始阶段报告哈希与run_id。相关设置改变必须重查，不给旧证据换当前标签；无关对象改变也要核实子快照确实一致。

规则见[物性检查](../output/properties-validation.md)、[动力学检查](../output/kinetics-validation.md)和[最终检查](../output/check.md)。
