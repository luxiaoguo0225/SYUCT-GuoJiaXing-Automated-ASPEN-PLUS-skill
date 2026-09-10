# Aspen Plus Automation Skill

面向 Codex 的 Aspen Plus V14 自动化 skill，重点覆盖 Windows COM（`Apwn.Document`）调用、`.inp`/`.bkp`/`.apwz` 案例操作、流程搭建、运行验证、结果读取与工程案例复用。如有问题请联系作者邮箱：2582693241@qq.com   //   luxiaoguo0225@gmail.com   

> **核心原则：先原理与需求，后案例参考。**
>
> 1. 第一原则：依据化工原理和用户明确要求建模；公式、物性、经验值和操作条件必须可溯源，禁止臆造。
> 2. 第二原则：仓库中的案例只用于学习工作流、Aspen 语法和排错方式；采用任何数值或构型前都必须回到第一原则重新校验。

## 功能范围

- 通过 COM 打开、编辑、运行、读取和另存 Aspen Plus 案例。
- 从 `.inp` 构建流程并导出 `.apwz`、`.rep` 等结果文件。
- 配置组分、物性方法、流股、反应器、闪蒸、RadFrac、HeatX、Calculator 和 Design Spec。
- 拆塔为裸 RadFrac + 外置冷凝器/再沸器，并建立蒸汽再压缩热泵与热集成。
- 支持热耦合、差压热耦合、双效精馏、吸收、反应工程及收敛排障。
- 使用 `.his`、Reconcile、物料/能量基准和四基准交叉验证检查结果可靠性。

## 环境要求

- Windows 10/11
- Aspen Plus V14（已安装并可通过 COM 启动）
- Python 3.10+
- `pywin32`

```powershell
python -m pip install -r requirements.txt
```

## 安装为 Codex Skill

克隆或下载本仓库后，将仓库目录复制到 Codex skills 目录：

```powershell
$target = Join-Path $env:USERPROFILE ".codex\skills\aspen-plus-automation"
New-Item -ItemType Directory -Force -Path $target | Out-Null
Copy-Item -Path .\* -Destination $target -Recurse -Force
```

重新启动或刷新 Codex 后，可通过 `$aspen-plus-automation` 调用。

## 快速开始

### 1. 使用 COM 桥接脚本

```powershell
python .\scripts\aspen_plus_bridge.py `
  --open .\examples\case.apwz `
  --run `
  --get "\Data\Streams\PRODUCT\Output\RES_TEMP"
```

### 2. 从 `.inp` 运行并导出结果

```powershell
python .\scripts\build_from_input.py `
  --inp .\scripts\styrene_column.inp `
  --save .\work\styrene_column.apwz `
  --report .\work\styrene_column.rep
```

### 3. 在 Codex 中调用

```text
Use $aspen-plus-automation to build and validate an Aspen Plus V14 case.
Start from the stated requirements and chemical engineering principles.
Use bundled cases only as learning references, never copy their values.
```

## 仓库结构

```text
.
├── SKILL.md                       # Codex skill 主入口与完整工作流
├── README.md                      # GitHub 首页与使用说明
├── 中文分类索引.md                 # 参考文档中文导航
├── agents/                        # Codex 智能体配置
├── assets/column-split/           # 拆塔、热泵、热集成案例资产
├── references/                    # 原理、机制、验证与案例文档
├── scripts/                       # COM 桥接、构建脚本和示例
├── .github/workflows/validate.yml # 基础 CI 校验
├── .gitattributes                 # 跨平台换行配置
└── .gitignore                     # 本地生成文件忽略规则
```

## 文档入口

- [SKILL.md](SKILL.md)：完整调用流程、规则、语法和验收方法。
- [中文分类索引.md](中文分类索引.md)：按“原理支撑 / 案例学习 / 工具资产”分类导航。
- [references/engineering-modeling-basics.md](references/engineering-modeling-basics.md)：流体流动、传热、分离与反应工程基础。
- [references/aspen-plus-textbook-guide.md](references/aspen-plus-textbook-guide.md)：Aspen Plus 物性、模块、收敛和 RadFrac 指南。
- [references/distillation-case-library.md](references/distillation-case-library.md)：热泵、变压、共沸、间歇、隔板、萃取和多效精馏案例索引。
- [references/run-verification-and-reconcile.md](references/run-verification-and-reconcile.md)：`.his`、Reconcile 与运行验收。

## GitHub 发布

仓库已经按 GitHub 常规目录组织，可直接使用 Git 上传：

```powershell
git init -b main
git add .
git commit -m "Initial release: Aspen Plus automation skill"
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin main
```

公开仓库前请再次确认：

1. Aspen 案例和结果文件不包含未授权的企业数据、客户数据或第三方资料。
2. `NOTICE.md` 中的商标与数据声明符合你的发布条件。
3. 如需允许他人复用，请自行添加 `LICENSE`；本仓库未替作者选择许可证。

## 验证

```powershell
python -m compileall -q .\scripts
```

GitHub Actions 会在每次 push 和 pull request 时检查 Python 语法及必需目录是否完整。Aspen 本身不会在 GitHub 托管 runner 上运行，因此流程必须在本机 Aspen Plus V14 环境完成最终验证。
