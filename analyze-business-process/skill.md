---
name: analyze-business-process
description: Model current and proposed business processes, roles, decision rules, and exceptions from supplied evidence for BA review.
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /analyze-business-process
  - 梳理业务流程和业务规则
  - 分析现状流程与目标流程
  - analyze business process and decision rules
  - map as-is and to-be process
tools: []
output_format: markdown
references:
  - references/template.md
  - references/LICENSE.upstream.txt
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
    - business-analysis
---

# 业务流程与规则分析

将访谈、操作说明、需求片段或已有 bundle 内容整理为可审阅的 BA 草稿，连接现状流程、目标流程、业务规则及异常处理。
本技能仅依赖提供的内容；流程表和决策表足以表达结果，无需外部绘图工具。

## 输入与范围

- 优先识别业务目标、流程起止事件、涉及角色/系统、当前问题和拟议改变。
- 记录材料名称、版本/日期和可定位章节；无链接的用户说明使用 `SRC-01` 等本次引用编号。
- 若范围不完整，列出采用的工作边界并继续分析已知部分；只对影响正确性的关键缺口提问。
- 用户只要求现状时，产出现状及问题；目标方案不自动成为实施承诺。

## 分析步骤

### 1. 建立现状（as-is）

按触发、角色动作、输入、判断、输出及交接列出步骤；保留已有 ID，否则分配本次草稿的 `AS-01` 等 ID。
每步区分负责执行者、决策者与接收者；未知人员写“待确认”，不按职位名称猜测审批权限。
将“实际做法”“书面规定”“受访者建议”分开，冲突材料并列注明来源及待确认人。
标记等待、返工、重复录入、职责空档和系统边界；没有测量数据时描述问题，不虚构耗时或节省比例。

### 2. 显式化业务规则

给每项规则稳定的 `BR-01` 等 ID，写明适用范围、条件、结果、依据及状态。
涉及多个条件时使用决策表；为条件定义口径，包括单位、币种、时区和包含边界（仅在相关时）。
逐行检查条件重叠与缺口：多条命中时的优先级、无命中时的处理都应明确或列为待决。
区分“否”“未知”“不适用”；输入缺失不能默认为不满足条件。
业务阈值、职责和政策依据必须来自材料；建议的新规则明确标为提案，不当成已批准规则。

### 3. 覆盖异常与恢复

沿各交接点检查退回、取消、重复提交、超时、系统失败及越权等与本流程相关的情形。
每个异常记录触发、受影响状态、负责角色、用户可见结果及恢复/升级路径。
将“异常被忽略”“系统自动补偿”等无证据行为列为待确认，不补写为现状。
只为与业务目标有关的例外建模，不把所有可能故障强加给简单流程。

### 4. 形成目标流程（to-be）

围绕已确认痛点提出目标步骤，使用 `TO-01` 等 ID，并映射被保留、合并、替代或新增的现状步骤。
每项变化解释业务价值、影响角色、规则变化、系统/数据依赖及仍需验证的假设。
比较目标方案与保持现状的选项；只有用户要求或权衡需要时才展开多个方案。
把端到端成功定义成可观察结果；指标的基线、目标和时间窗口未知时分别注明。

### 5. 交接需求

为拟转入需求的流程/规则变化建立映射：`步骤 → BR → REQ → 验收场景`。
保留已有需求 ID；新需求使用明确标注的候选 ID，未编写的验收场景标为待补充。
提供涉及正常、边界和异常行为的验收意图，供后续 PRD、用户故事或测试设计使用。
将事实、推断、方案和待决问题分列，避免把目标流程混进当前业务事实。

## 输出与复核

需要完整报告时使用 [references/template.md](references/template.md)；简单问题仅保留相关表格。
默认输出 Markdown 草稿，包含范围/来源、现状、规则、异常、目标变化和待决事项。
复核起止是否闭合、交接是否有接收者、规则是否可判定、目标变化是否能追到问题来源。
现状缺证据的部分明确标为“未验证”；不把“未发现问题”写成“流程无风险”。
完成标准是证据支持的可审阅分析及缺口清单；不以补齐未知信息为由停止其余工作。
本技能不自动写入 bundle、创建 Jira 事项或更改业务配置，也不宣称完成了这些操作。

## 来源与 EFP 扩展

本技能为 EFP 原创 BA 扩展，上游并无同名业务分析技能；借鉴用户旅程的范围/步骤/痛点以及需求边界与风险组织方式。
as-is/to-be 映射、职责区分、业务决策表、异常恢复及需求追踪是本次独立编写的 EFP 方法，未声称由上游提供。
参考版本：`19392f7a08264ed00486a251f5b2098321771f94`；MIT 完整许可见 [LICENSE.upstream.txt](references/LICENSE.upstream.txt)。
- [UX Researcher & Designer：journey mapping](https://github.com/alirezarezvani/claude-skills/blob/19392f7a08264ed00486a251f5b2098321771f94/product-team/skills/ux-researcher-designer/SKILL.md)
- [Product Manager Toolkit：PRD templates](https://github.com/alirezarezvani/claude-skills/blob/19392f7a08264ed00486a251f5b2098321771f94/product-team/skills/product-manager-toolkit/references/prd_templates.md)
