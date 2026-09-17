---
name: analyze-requirement-change
description: Assess a proposed requirement change against a supplied baseline and trace impacts on stories, acceptance criteria, dependencies, and business decisions.
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /analyze-requirement-change
  - 分析需求变更影响
  - 评估范围变更和需求追踪
  - analyze requirement change impact
  - assess scope change and traceability
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

# 需求变更影响分析

对照用户提供的需求基线和变更请求，形成可审阅的影响分析与决策草稿，说明变什么、影响谁、需要哪些确认。
输入可来自文档片段、需求表、用户故事、验收标准或已有 bundle 内容；不依赖外部工具或指定项目系统。

## 确定基线与变更

记录基线的名称、版本/日期、已知状态及来源；“最新”或“已批准”只有在材料支持时才能使用。
若只有零散片段，明确分析覆盖范围，并将结论标为初步影响分析，不虚构完整基线。
逐项列出旧行为、拟议新行为、变更原因、提出者和期望生效范围；区分缺陷修正、澄清与范围改变。
保留已有 ID；没有 ID 时分配本次草稿编号并注明，不把临时 ID 当成 Jira key。
变更是否已批准与本次分析是否完成分别记录，不能用推荐方案代替批准记录。

## 分析路径

### 1. 核对差异

按新增、修改、删除或待澄清分类，记录业务规则、角色、输入/输出和验收行为的变化。
检查词义差异是否改变义务或边界，例如“可选→必填”“工作日→自然日”“大于→大于等于”。
多个材料冲突时保留相互矛盾的说法及来源，不以文件顺序或更强措辞自动决定优先级。
对未知基线仅描述拟议行为和待核对项，不声称已完成前后差异比对。

### 2. 建立追踪链

使用 `变更 → 需求 → 业务规则/流程 → 用户故事 → 验收标准 → 测试/依赖` 连接受影响对象。
仅在材料有依据时标为“确认受影响”或“确认不受影响”，其余标为“疑似影响”或“待核实”。
每条关系注明证据或推断理由；引用真实 ID，并区分直接变化、下游影响与尚未验证的间接影响。
缺少验收标准、测试或依赖材料时列为覆盖缺口；没有搜到不等于不存在。
沿提供的上下游关系追踪至稳定边界，说明边界外未评估的系统或交付团队。

### 3. 评估影响

按相关性检查用户行为、业务流程/职责、数据与历史记录、接口/上下游、权限、报表及运营支持。
对已有数据检查新规则是否适用于历史对象、进行中业务或仅新增对象；不猜测迁移和兼容策略。
对验收与测试检查哪些应保留、修改、新增或作废，以及是否需要回归相关业务场景。
同时记录收益、风险、工作项及依赖负责人；工作量和交期采用团队提供的估算及假设。
没有估算时给出需要估算的工作范围和不确定因素，不自动换算故事点或承诺日期。
“未受影响”结论须能说明证据范围；不能把没有资料的领域填成零成本或零风险。

### 4. 比较决策选项

结合请求比较接受变更、缩小/分阶段、暂缓及保持基线等有意义的选项，避免无差别枚举。
每个选项写明业务收益、代价/风险、依赖、可逆性和前置条件，并保持相同的评估口径。
提出推荐及其条件；关键事实未知时使用条件式建议，并列出什么证据会改变建议。
区分决定范围/优先级的业务角色、提供成本/技术判断的角色和最终决策人；未知则待确认。
既有授权和决策作为证据记录，不把每次分析都变成新的通用审批流程。

### 5. 形成更新清单

列出决定后需要同步的需求、规则、故事、验收、测试、说明文档和交付计划及其负责人。
标注哪些对象需重新确认；若尚未决定，所有更新保持拟议状态。
说明生效边界、回退/恢复需求和通知对象（仅在与变更相关时），不在此技能中执行通知。
保留旧基线引用及决策记录，确保下一次分析能看清版本差异。

## 输出与完成标准

需要成套分析时使用 [references/template.md](references/template.md)，小范围变更可缩减为差异、影响和建议三部分。
输出应包含基线/变更摘要、追踪矩阵、选项比较、决策状态、待确认项和拟议更新清单。
复核每项结论能追到证据或明确假设；关键未评估领域和可能推翻建议的缺口必须可见。
完成标准是可审阅的分析，而非假定已批准、已落地或已完成回归验证。
本技能不自动修改 bundle、Jira、排期或远端文档；用户提供的信息足以完成已知范围的草稿。

## 来源与 EFP 扩展

本技能为 EFP 原创 BA 扩展，上游并无同名需求变更技能；借鉴需求边界、风险/依赖与可测试验收条件的组织方式。
版本基线、影响传播、追踪关系状态、决策选项及变更记录是本次独立编写的 EFP 方法，未声称为上游功能。
参考版本：`19392f7a08264ed00486a251f5b2098321771f94`；MIT 完整许可见 [LICENSE.upstream.txt](references/LICENSE.upstream.txt)。
- [Product Manager Toolkit：PRD templates](https://github.com/alirezarezvani/claude-skills/blob/19392f7a08264ed00486a251f5b2098321771f94/product-team/skills/product-manager-toolkit/references/prd_templates.md)
- [Agile Product Owner：user-story templates](https://github.com/alirezarezvani/claude-skills/blob/19392f7a08264ed00486a251f5b2098321771f94/product-team/agile-product-owner/skills/agile-product-owner/references/user-story-templates.md)
