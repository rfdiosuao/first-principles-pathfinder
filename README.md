# First-Principles Pathfinder

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Codex Skill for researching competing solution paths and choosing the shortest safe route to a complete, verified outcome.

这是一个面向 Codex 的“第一性原理最短路径”Skill。它不会因为某个开源项目最先被找到，就立刻安装和部署；它会先明确真正的完成标准、盘点已有能力、搜索不同机制的候选路线，再用硬约束、Pareto 剪枝和最小判别实验选择路径。

## 为什么做这个 Skill

解决问题时，最容易浪费时间的不是执行太慢，而是过早选择了错误的路线：

- 为了获取一批数据，先部署复杂项目，却忽略已有登录态或原生接口；
- 一个方案能处理单条记录，就误以为它能完成全量目标；
- 因为已经投入时间，继续调试明显不占优的路线；
- 把“程序运行成功”误当成“用户目标已经完成”。

这个 Skill 优化的是到达**完整且经过验证的结果**所需的预期总时间，而不是代码行数、点击次数或安装速度。

## 决策流程

```text
定义终点
  → 盘点本机和现有登录态能力
  → 搜索不同机制的路线族
  → 建立候选路线账本
  → 硬约束淘汰
  → Pareto 剪枝
  → 最小判别实验
  → 有界执行
  → 全量验收与失败回退
```

核心原则：

- 工具、仓库和框架都是可替换假设，用户目标才是固定点。
- 默认要求 `minimum_coverage = 1.0`；除非用户明确接受部分结果。
- 成功概率为零、违反权限或无法覆盖完整目标的路线直接淘汰。
- 不使用拍脑袋的加权总分掩盖关键缺陷。
- 只有路线胜出、空间足够且获得授权后，才安装依赖。
- 低风险操作可以直接执行；登录、付款、破坏性操作、生产变更和对外动作保留人工确认。

## 安装

### Windows PowerShell

```powershell
git clone https://github.com/rfdiosuao/first-principles-pathfinder.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse ".\first-principles-pathfinder\skills\first-principles-pathfinder" "$env:USERPROFILE\.codex\skills\"
```

### macOS / Linux

```bash
git clone https://github.com/rfdiosuao/first-principles-pathfinder.git
mkdir -p ~/.codex/skills
cp -R first-principles-pathfinder/skills/first-principles-pathfinder ~/.codex/skills/
```

如果目标目录已经存在，请先备份旧版本，再用仓库中的 Skill 目录更新它。安装后新建一个 Codex 任务，使技能列表重新载入。

## 使用

显式调用：

```text
使用 $first-principles-pathfinder，先调研并比较达到目标的候选路线，再执行最短可验证路径。
```

也可以直接描述意图：

```text
先不要部署项目。请调研不同实现机制，用第一性原理找出完成这件事的最短路径，并验证完整结果。
```

Skill 会在以下场景自动匹配：

- 需要选择最快、最简单或浪费最少的实现方式；
- 多个技术方案、开源项目或服务相互竞争；
- 准备部署爬虫、自动化栈、集成服务或自行开发之前；
- 当前方案只能处理样本，不确定能否覆盖全量目标。

## 路线账本与比较脚本

当候选路线不少于三个、约束复杂或选择存在争议时，可以把证据写成 JSON 账本，然后运行：

```bash
python skills/first-principles-pathfinder/scripts/rank_paths.py path/to/ledger.json
```

脚本执行以下确定性检查：

1. 校验输入结构与数值范围；
2. 淘汰违反硬约束、覆盖率不足或成功概率为零的路线；
3. 计算包含失败恢复成本的预期总耗时；
4. 标记 Pareto 前沿和被支配路线；
5. 按用户优先级给出稳定排序与推荐结果。

它不会生成一个掩盖取舍的加权总分。证据质量和关键未知量仍需由实际调查与最小实验确认。

## 验证

运行全部单元测试：

```bash
python -B skills/first-principles-pathfinder/tests/test_rank_paths.py
```

运行公众号示例账本：

```bash
python -B skills/first-principles-pathfinder/scripts/rank_paths.py skills/first-principles-pathfinder/tests/fixtures/wechat-paths.json
```

示例会选择复用现有登录态的轻量路线，并将复杂导出器与代理服务组合标记为被支配路线。

## 仓库结构

```text
skills/first-principles-pathfinder/
├── SKILL.md
├── agents/openai.yaml
├── references/decision-protocol.md
├── scripts/rank_paths.py
└── tests/
```

## 安全与合规

本项目用于选择和执行用户已授权范围内的解决路径。它不会扩大用户原始请求所授予的权限，也不应被用于绕过访问控制、抓取非公开数据或违反平台条款。遇到凭据提交、付款、生产环境变更、破坏性操作或对外通信时，应暂停并取得明确授权。

## License

[MIT](LICENSE)
