<div align="center">

<h1>🧭 First-Principles Pathfinder</h1>

<p><strong>先调研，再下注。为 Codex 选择抵达完整结果的最短可验证路径。</strong></p>

<p>Research competing approaches, test decisive assumptions, and choose the shortest safe path to a complete, verified outcome.</p>

<p>
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/github/license/rfdiosuao/first-principles-pathfinder"></a>
  <img alt="Python 3.8 or newer" src="https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&amp;logoColor=white">
  <img alt="Runtime dependencies: Python standard library only" src="https://img.shields.io/badge/runtime%20dependencies-stdlib%20only-2ea44f">
  <a href="https://github.com/rfdiosuao/first-principles-pathfinder/commits/main"><img alt="Last commit" src="https://img.shields.io/github/last-commit/rfdiosuao/first-principles-pathfinder"></a>
</p>

<p>
  <a href="#quick-start">快速开始</a> ·
  <a href="#how-it-works">工作原理</a> ·
  <a href="#verified-example">验证示例</a> ·
  <a href="skills/first-principles-pathfinder/references/decision-protocol.md">决策协议</a> ·
  <a href="https://github.com/rfdiosuao/first-principles-pathfinder/issues">反馈问题</a>
</p>

</div>

---

## 为什么需要它

很多技术任务真正浪费的时间，不在执行，而在**过早选错路线**：

| 常见偏差 | Pathfinder 的处理方式 |
| --- | --- |
| 搜到第一个教程就开始部署 | 先覆盖不同机制的路线族，再比较证据 |
| 默认完整项目比小技巧可靠 | 先盘点本机能力、现有登录态、原生接口与可复用数据 |
| 单条样本成功就宣称任务完成 | 默认要求 <code>minimum_coverage = 1.0</code>，对照完整验收条件 |
| 用总分掩盖权限、风险或覆盖率缺陷 | 先执行硬约束淘汰，再做 Pareto 剪枝 |
| 因为已经投入时间而继续死磕 | 忽略沉没成本，用失败证据重新排序 |

这个 Skill 优化的不是代码行数、安装速度或点击次数，而是：

~~~text
到达完整、合规且经过验证的结果所需的预期总时间
~~~

适合在部署爬虫、自动化栈、开源项目、托管服务、依赖集成或自研方案**之前**调用。

<a id="quick-start"></a>

## 快速开始

### 前置条件

- 支持本地 Skills 的 Codex；
- Git；
- Python 3.8+，仅在运行确定性路线比较脚本时需要；脚本不依赖第三方包。

### 1. 安装 Skill

<details open>
<summary><strong>Windows PowerShell</strong></summary>

~~~powershell
git clone --depth 1 https://github.com/rfdiosuao/first-principles-pathfinder.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse ".\first-principles-pathfinder\skills\first-principles-pathfinder" "$env:USERPROFILE\.codex\skills\"
~~~

</details>

<details>
<summary><strong>macOS / Linux</strong></summary>

~~~bash
git clone --depth 1 https://github.com/rfdiosuao/first-principles-pathfinder.git
mkdir -p ~/.codex/skills
cp -R first-principles-pathfinder/skills/first-principles-pathfinder ~/.codex/skills/
~~~

</details>

如果目标目录已经存在，请先备份旧版本，再进行更新。安装后新建一个 Codex 任务或重启 Codex，使技能列表重新载入。

### 2. 直接调用

~~~text
使用 $first-principles-pathfinder，先调研并比较达到目标的候选路线，再执行最短可验证路径。
~~~

也可以使用自然语言触发：

~~~text
先不要部署项目。请调研不同实现机制，用第一性原理找出完成这件事的最短路径，并验证完整结果。
~~~

### 3. 你会得到什么

- 明确的目标状态、验收条件和硬约束；
- 至少三类可行机制的候选路线，或对缺失路线的具体排除理由；
- 事实、推断与待验证假设分离的路线账本；
- 胜出路线、关键依据、最小判别实验和回退条件；
- 对最终用户可见结果的完整验证，而不只是“命令运行成功”。

<a id="how-it-works"></a>

## 工作原理

~~~mermaid
flowchart LR
    A["定义终点<br/>验收条件与硬约束"] --> B["盘点现有能力<br/>文件、登录态、API、CLI"]
    B --> C["搜索不同路线族"]
    C --> D{"通过硬约束？"}
    D -- "否" --> X["淘汰"]
    D -- "是" --> E["Pareto 剪枝"]
    E --> F{"关键未知会改变赢家？"}
    F -- "是" --> G["最小判别实验"]
    F -- "否" --> H["执行胜出路线"]
    G --> H
    H --> I{"完整验收通过？"}
    I -- "是" --> J["交付结果"]
    I -- "否" --> K["更新证据与路线账本"]
    K --> C
~~~

### 八步协议

1. **定义终点**：把请求翻译为可观察的目标状态与验收条件。
2. **盘点起点**：检查本地工具、已有数据、登录态和原生能力。
3. **搜索路线族**：比较原生功能、直接接口、轻量组合、完整项目、UI 自动化和人工协作。
4. **建立账本**：记录证据质量、覆盖率、成功概率、生命周期耗时、风险与可逆性。
5. **淘汰与剪枝**：违反硬约束的路线直接出局，其余路线进入 Pareto 比较。
6. **最小实验**：只测试足以改变路线选择的关键未知量。
7. **有界执行**：赢家失败后更新证据并重新排序，不进入无限调试。
8. **全量验收**：验证用户真正需要的完整结果，而不是工具是否启动。

预期总耗时模型：

~~~text
T_expected = 调研 + 安装 + 执行 + 验证 + 清理
           + (1 - 成功概率) × 失败恢复成本
~~~

完整性、权限、安全和合法性始终是硬门槛，不能用更短时间抵消。

<a id="verified-example"></a>

## 验证示例：公众号评论路线

仓库内置的 [公众号路线账本](skills/first-principles-pathfinder/tests/fixtures/wechat-paths.json) 比较了两种均声称可覆盖全部公开评论的方案：

| 路线 | 覆盖率 | 预期总耗时 | 风险 | 侵入性 | 结果 |
| --- | ---: | ---: | ---: | ---: | --- |
| 复用现有登录态的轻量直连 | 100% | 106 分钟 | 1 | 0 | Pareto 前沿，推荐 |
| 导出器 + 本地代理服务栈 | 100% | 330.5 分钟 | 2 | 3 | 被支配 |

运行示例：

~~~bash
python -B skills/first-principles-pathfinder/scripts/rank_paths.py \
  skills/first-principles-pathfinder/tests/fixtures/wechat-paths.json
~~~

关键输出：

~~~json
{
  "dominated": ["exporter-plus-proxy-stack"],
  "pareto_front": ["direct-session-technique"],
  "recommended": "direct-session-technique"
}
~~~

这些数字来自仓库的固定测试样例，用于证明决策规则，不是对所有公众号任务的通用性能承诺。

## 路线比较脚本

当存在三个以上严肃候选、约束较多或选择有争议时，把路线写入 JSON 账本并运行：

~~~bash
python skills/first-principles-pathfinder/scripts/rank_paths.py path/to/ledger.json
~~~

脚本会：

- 校验输入结构和数值范围；
- 淘汰硬约束失败、覆盖率不足或成功概率为零的路线；
- 计算包含失败恢复成本的预期总耗时；
- 标记 Pareto 前沿和被支配路线；
- 根据用户明确优先级生成稳定排序。

它不会输出一个掩盖真实取舍的加权总分，也不会替代证据调查与运行时验证。

## 项目资源

| 资源 | 用途 |
| --- | --- |
| [SKILL.md](skills/first-principles-pathfinder/SKILL.md) | Codex 触发条件与核心执行流程 |
| [决策协议](skills/first-principles-pathfinder/references/decision-protocol.md) | 证据分级、路线账本、停止条件和完整案例 |
| [rank_paths.py](skills/first-principles-pathfinder/scripts/rank_paths.py) | 硬约束、Pareto 前沿与稳定排序 |
| [公众号 fixture](skills/first-principles-pathfinder/tests/fixtures/wechat-paths.json) | 可复现的路线比较输入 |
| [单元测试](skills/first-principles-pathfinder/tests/test_rank_paths.py) | 覆盖硬约束、完整率、零概率和确定性排序 |

## 验证

运行全部测试：

~~~bash
python -B skills/first-principles-pathfinder/tests/test_rank_paths.py
~~~

当前测试覆盖：

- 违反硬约束的最快路线仍会被淘汰；
- 部分覆盖路线不能战胜完整路线；
- 成功概率为零的路线永不推荐；
- 非法概率返回结构化错误；
- 相同候选产生稳定排序；
- 公众号示例选择轻量直连路线。

## 安全边界

Pathfinder 不会扩大用户请求本身授予的权限。以下动作在没有明确授权时必须暂停：

- 提交登录凭据或支付；
- 破坏性文件与系统操作；
- 修改安全设置或生产环境；
- 发送消息、发布内容或进行其他对外通信；
- 访问非公开数据或绕过访问控制。

项目不应被用于违反平台条款、侵犯隐私或抓取未经授权的数据。

## 参与项目

欢迎通过 [Issues](https://github.com/rfdiosuao/first-principles-pathfinder/issues) 提交可复现问题、真实路线案例和协议改进建议，也欢迎直接发起 Pull Request。

提交前请运行单元测试，并确保新增路线没有用速度、便利性或加权分数掩盖硬约束失败。

## License

本项目采用 [MIT License](LICENSE)。
