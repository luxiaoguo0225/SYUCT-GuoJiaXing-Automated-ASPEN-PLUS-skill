# COM 连接机制：`Dispatch` 不附着 + 许可看环境变量（Aspen Plus V14 本机实测）

> **层级**：工具与机制层，服从 `SKILL.md` §1 的两级原则。本文只回答"COM 能不能连上、许可什么时候校验、
> 失败怎么定位"，不改变"原理 + 需求先行、禁止臆想"的第一原则，也不提供任何建模取值。
> **适用**：Aspen Plus V14（OLE 服务内部版本 40.0），Sentinel RMS 许可服务器（`lservnt.exe`）与客户端同机。
> **证据**：2026-09-12 在开发机 `GUOJIAXING`（Windows / Python 3.13 / pywin32 312 / Aspen Plus V14）实测，
> 命令与观察值原样记录；全部试验只用案例的临时副本，未触碰任何交付目录。

## 0. 三句话结论

1. **`Dispatch("Apwn.Document")` 不会附着**到任何已在运行的 Aspen 实例。COM 的服务控制管理器（SCM）
   总是新起一个 `aspenplus.exe -Automation -Embedding`；"附着到已跑实例"这条路在 V14 上是封死的。
2. **预启动 `aspenplus.exe -Automation` 没有意义**：注册表 `LocalServer32` 本来就是这条命令行，
   COM 自己就是这么拉进程的；预启动的那个进程在无人连接时会自行退出，只多占内存和一个许可席位。
3. **`Dispatch` 成功 ≠ 许可通过**。许可校验发生在 `InitFromFile2` / `Run2`，失败签名是
   `2040 ... 无法核实许可 / 无法实例化`。真正决定成败的是**客户进程环境里的 `LSHOST` / `LSFORCEHOST`**
   ——它会被 SCM 拉起的服务器进程继承，因此**不需要 `Popen` 预启动**。

## 1. 证据一：`Dispatch` 不附着

| 步骤 | 观察（同一台机、同一时段） |
| --- | --- |
| 基线 | 进程表里只有用户自己开的 GUI：`aspenplus.exe "<case>.apwz"`（PID 27364） |
| 预启动 | 以 `LSHOST=LSFORCEHOST=guojiaxing` 启动 `aspenplus.exe -Automation` → PID 32696 |
| `Dispatch` | 独立的 Python 进程执行 `Dispatch("Apwn.Document")` → **2.0 s 返回**；进程表**新增** PID 24156，命令行为 `... -Automation -Embedding` |
| 对象内容 | `app.Tree.FindNode(r"\Data")` 报 `(2002, 'Aspen Plus 40.0 OLE 服务', '未初始化……请先调用 InitNew 或 InitFromFile')` → 拿到的是**全新的空文档**，既不是预启动实例，也不是用户 GUI 里已打开的案例 |
| 附着 API | `win32com.client.GetActiveObject("Apwn.Document")` → `MK_E_UNAVAILABLE (-2147221021)`：ROT 里没有任何注册 |
| 释放后 | 释放 COM 引用 3 s 后，`-Embedding` 进程自行消失；预启动的 32696 也在无客户端后自行退出 |

结论与推论：

- 不要为了"附着"去做预启动——它不会让 `Dispatch` 复用那个进程，只会多一个常驻 Aspen。
- 跨进程复用实例在 V14 无法实现；想省掉冷启动开销，只能让桥接脚本/服务**常驻**，在**同一个进程内**复用同一个 COM 对象。

## 2. 证据二：决定许可的是客户进程的环境变量

试验对象：安装自带案例 `GUI\Examples\Getting Started\Process\flash.bkp` 的**临时副本**
（按 §7.2 的规矩，绝不在交付目录里用 COM 打开 `.bkp`）。每次试验：设环境变量 → `Dispatch` → `InitFromFile2(copy, True)` →（成功则）`Run2(False)`。

| 试验 | 发起 Dispatch 的客户进程环境 | 结果 |
| --- | --- | --- |
| D | `LSHOST=no-such-host-12345`，无 `LSFORCEHOST` | `InitFromFile2` 失败 `(2040, 'Aspen Plus 40.0 OLE 服务', '无法实例化')`；**重复两次结果一致** |
| E | 假 `LSHOST` + `LSFORCEHOST=guojiaxing` | Init OK 7.3 s，Run2 OK 2.7 s |
| 对照 | `LSHOST=guojiaxing`（本机正常值） | Init OK 2.8 s，Run2 OK 1.8 s |
| F | 假 `LSHOST` + `LSFORCEHOST=guojiaxing:@guojiaxing` | Init OK 2.9 s |
| G | 假 `LSHOST` + `LSFORCEHOST=guojiaxing:5093@guojiaxing` | Init OK 2.6 s |
| H | 假 `LSHOST` + `LSFORCEHOST=127.0.0.1` | Init OK 3.9 s |

补充观察：**`Dispatch` 阶段根本不碰许可**——三组互不相同的环境变量下，`Dispatch` 都是约 2.0 s 返回、
进程行为一致，只有到 `InitFromFile2` 才分出差错。所以"Dispatch 成功"不能用来判断接口/许可可用。

## 3. 机制解释

- 注册表：`HKCR\CLSID\{CF916C06-D17A-4A07-8548-787F4B0F99CB}\LocalServer32 = "...\aspenplus.exe -Automation"`。
  `-Automation` 是 COM 自己的启动参数，不是需要外部构造的"接入技巧"。
- 调用链：`Dispatch` → `CoCreateInstance` → SCM → 以**客户端环境块**启动 `aspenplus.exe -Automation -Embedding`
  → 服务器进程继承 `LSHOST`/`LSFORCEHOST` → `InitFromFile2` 时向 Sentinel RMS 申请席位并校验。
- 因此关键在"让**服务器进程**看到正确的许可主机"；显式写环境变量之所以有效，是因为它同时摆正了客户端环境，
  而不是因为"预启动+附着"。由 §2 对照组可知：不预启动、只把客户端环境设对，同样通过。
- 跨进程复用：`LocalServer32` 未做 ROT 注册 → `Dispatch` 每次都新建进程；pywin32 的 `Dispatch` 也没有"有则复用"语义。

## 4. 推荐写法（含兜底）

```python
import os, socket, win32com.client

def prepare_license_env(force_host=None):
    host = (force_host
            or os.environ.get("LSHOST", "").strip()
            or os.environ.get("COMPUTERNAME", "").strip()
            or socket.gethostname())
    os.environ["LSHOST"] = host
    # 广播被拦的环境下这是唯一兜底；不设也能用（若 LSHOST 本就正确），设了更稳
    os.environ.setdefault("LSFORCEHOST", host)
    return host

prepare_license_env()                              # 必须在 Dispatch 之前
app = win32com.client.Dispatch("Apwn.Document")    # 不要 Popen 预启动 "-Automation"
app.InitFromFile2(case, True)                      # 许可校验点：这里报 2040 = 环境/许可问题
```

- `LSHOST` 与 `LSFORCEHOST` 都要在**发起 `Dispatch` 的那个进程**里设好，且必须在 `Dispatch` 之前。
- `LSFORCEHOST` 实测可用形式（三种都通过）：`<host>`、`<host>:<port>@<host>`、`127.0.0.1`。
- 只设 `LSHOST` 而它指错时**没有兜底**（本机子网广播被拦，见 §6），直接 2040；
  所以兜底逻辑是"`LSHOST` 为空或不可解析 → 用 `COMPUTERNAME`/`hostname` 覆盖，并显式设 `LSFORCEHOST`"。

## 5. 2040 排错清单

1. `InitFromFile2` 报 `2040` → 先查客户进程的 `os.environ["LSHOST"]` 是否指向**可解析**的主机；
   不要用 "Dispatch 成功" 判断接口可用。
2. 显式设 `LSFORCEHOST=<可解析主机>` 后重试（三种形式任选，§4）。
3. 确认许可服务在跑：`Get-Service "Sentinel RMS License Manager"`；UDP 5093 探测要有回包（§6）。
4. 在服务/非交互会话里跑时，机器级环境变量可能继承不到 → 显式写入进程环境再 `Dispatch`。
5. `.bkp` 的验证与本文无关：仍按 §7.2 的规矩用临时副本，不要在交付目录里用 COM 打开任何文件。

## 6. 本机事实清单（`GUOJIAXING`）

- `lservnt.exe`（Sentinel RMS Development Kit 9.6.0.0028）监听 **UDP 5093**，绑定 `0.0.0.0` 与 `[::]`；
  **没有任何 TCP 监听**（`Test-NetConnection 127.0.0.1 -Port 5093` → False；TCP 直连超时）。
  用 TCP 探测许可服务是错的方向，UDP 才是。
- UDP 探测 `127.0.0.1:5093` 与 `10.253.35.176:5093` 均收到 1432 B 应答 → 服务可达、回环与 LAN 均可。
- `LSHOST=GUOJIAXING`（机器级环境变量）→ 解析 `10.253.35.176`（另有 IPv6 `fe80::f069:bc02:49fe:77ee`）；本机自服务。
- **子网广播被拦**：`SLM Client Tools\lswhere.exe` 在 4 种环境变量组合（含 `LSFORCEHOST=guojiaxing`、
  `127.0.0.1`、带端口写法）下都报 `Error[17]: Probably no servers are running on this subnet`。
  它是广播搜索工具、不看 `LSHOST`/`LSFORCEHOST`，**别拿它当判据**；也正因广播不通，`LSHOST` 指错时没有兜底。
- 开销参考：首次 `Dispatch` 冷启动约 15 s；空白 `-Embedding` 实例常驻内存约 214 MB。

## 7. 与既有接入文档的差异（据实修正）

本机另一份接入文档（WorkBuddy 接入版）主张："**不要**让 COM 自己按需去拉 OLE 服务器；必须先由自己的进程
以 `LSHOST`/`LSFORCEHOST` 预启动 `aspenplus.exe -Automation`，再 `Dispatch` 附着。"据本机实测：

- "附着"不成立（§1）：预启动后 `Dispatch` 仍新建了 `-Automation -Embedding` 进程，且 `GetActiveObject` 无 ROT 注册可用。
- 起作用的只是环境变量（§2 的对照组在**完全没有预启动进程**时同样通过）；而环境变量由 SCM 拉起的服务器进程继承，
  所以预启动并非必要步骤。
- 该文档写的 `LSFORCEHOST=<host>:@<host>` 形式实测有效（试验 F），但裸 `<host>` 同样有效（试验 E）。
- 若那边确实观察到"预启动后才通过"，更可能的原因是**那一次 SCM 拉起的进程没有拿到正确的许可环境**
  （客户进程的 `LSHOST` 缺失/继承不到，或处在不同会话/完整性级别），预启动恰好把环境变量显式摆对了。
  排查方向应是"服务器进程继承了哪些环境变量"，而不是"有没有附着"。

## 8. 复现要点

- 最小复现只需三步：改环境变量 → `Dispatch` → `InitFromFile2(临时副本, True)`。
- 环境变量要在 `os.environ` 里改，再在**同一进程**里 `Dispatch`（SCM 拉起的服务器由此继承）。
- 每次试验后 `Quit()` 并按 PID 清理 `AspenPlus.exe` 残留；确认进程表里只剩你自己需要的实例。
- 用 `Get-CimInstance Win32_Process -Filter "Name='AspenPlus.exe'"` 看命令行，即可区分
  `-Automation`（预启动）与 `-Automation -Embedding`（SCM 新建）。
