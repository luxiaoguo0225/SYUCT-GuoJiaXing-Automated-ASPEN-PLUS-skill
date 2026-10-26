# 当前运行审计

本模块只定义可观测证据的检查方法。不能以修复叙述代替原始结果；问题定位后把证据和重验条件交回R00，不在验证中修复交付模型。

## 当前运行与日志

检查当前候选 input_sha256、iteration_id、run_id 和文件身份。独立核对输入完整性、活动块/循环/Design Spec是否实际执行，不能用Run2返回或GUI摘要代替执行证据。只读本轮完整 .his 和Control Panel，必须零Severe/Error/Warning，临时错误也不得被最终摘要遮盖。

.apwz可能解包到子目录，日志可能在会话关闭后消失；应在验证会话仍打开时复制原始日志，绑定本轮身份。使用[history_check.py](../../../scripts/history_check.py)识别编码、实际消息和完成轨迹，再由[check_delivery.py](../../../scripts/check_delivery.py)核身份。未知格式、旧日志、空日志或缺少必要正常报告均为UNVERIFIED。

## 设置、单位与初始化

逐项回读实际生效容差、算法、初始化、Spec/Vary目标及禁用状态，对比用户原件/冻结合同，禁止放宽容差。报告与节点量纲同时核单位字符串和基准；不要假设CAL/SEC换算常数或热/功率单位，必要时在验证副本上用已知物理基准标定。

## 冷重开与物理边界

从冻结候选复制到新工作目录，用本轮自建的新COM会话冷重开、复算、回读设置及结果并取当前日志；不在交付目录初始化，不改原件/候选字节，只关闭自己拥有的会话。披露温度/组成剖面、撕裂初值等依赖，带已保存初值的复现不能称无初值稳定。

按[通用基准](../../run/diagnostics/general-verification-methods.md)和[工艺验收](../process-acceptance.md)独立核物性适用性、相稳定性、总量/组分或元素/电荷、能量/压力/温位。数值收敛、物性、复现、设备评级和GUI可见性分项判断，参照[诚信边界](../../../references/convergence-separation-and-energy-integrity.md)。

发现不符时以[O02](../check.md)规定的issue_id、期望/实际、证据、责任模块和重验条件返回R00。修复和Reconcile等输入写操作由R00完成，修改后新候选必须重新验证。
