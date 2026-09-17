---
name: prioritize-roadmap
description: "Prioritize product initiatives and draft outcome-based roadmaps with explicit scoring, dependencies, capacity, and decision trade-offs. Use when PMs or BAs must rank a backlog or sequence a roadmap."
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /prioritize-roadmap
  - prioritize a product backlog
  - create an outcome roadmap
  - 需求优先级与路线图规划
  - 用 RICE 排序产品需求
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
    - product-management
---

# 产品优先级与结果路线图

交付能复核取舍依据的排序和路线图草稿。将用户/业务结果、证据、资源与依赖连起来，保留决策者尚未确认的部分。

## 输入和范围

- 读取已提供的目标、候选需求、研究证据、现行排序、团队容量、依赖、时间窗口和已有承诺。
- 为候选项保留原 ID；没有 ID 时创建本地 I 编号，并注明并非 Jira 工单号。
- 只做排序时无需生成完整路线图。既有方法适用时沿用，不为套用框架而重建流程。
- 关键目标或比较口径不清时提出少量必要问题；其他缺口写“未知”。不虚构 Reach、成本、置信度、容量或发布日期。
- 输出分析草稿和可交接表格，不自动调整 Jira、发布路线图或写入 bundle。

## 1. 先处理硬约束

将输入中已确认的截止日期、合同义务、安全或合规要求、依赖和不可用资源单列，注明证据及负责人。未经确认的限制记为假设。

区分必须完成、可选、需先验证和当前被阻塞的工作。评分不能取消已确认义务；硬约束相互冲突或容量不足时标明不可行之处与待决策取舍，不用低分掩盖冲突。

## 2. 统一比较依据

每个候选项说明目标用户、问题、预期结果、证据、成本与风险。将“上线功能”改写为可观测的用户/业务改变，并保留原条目对应关系。

数据充分且可比时可用 RICE；数据不足时用影响/投入的定性比较，明确依据和不确定性。不要把未知当成零或中间档，不给完全不同口径的分数排出统一总榜。

采用 RICE 时在计算前声明：

- **R（Reach）**：同一时间窗、同一实体的受影响数量，例如每季度受影响账户数；账户不能与用户人数混算。
- **I（Impact）**：对共同目标的单位影响，使用已同意的评分尺度；建议尺度需标明待确认。不要再将 Reach 乘进 Impact。
- **C（Confidence）**：将输入百分比规范为 0–1 比例，80% 写为 0.8；附证据依据，不从描述语气猜测数值。
- **E（Effort）**：同一单位的投入，例如人周，说明涵盖设计、研发、测试和协调的范围；必须大于零。
- **计算**：`RICE = R × I × C / E`，展示原始输入、单位、计算值和来源；缺数、E=0、负值或超范围输入不产生有效分数。

如用户已有 ICE、加权评分或 MoSCoW 方法，明示其尺度、权重及规则；方法不匹配时解释局限，不能静默换算成 RICE。

## 3. 给出取舍建议

将机械得分与最终建议次序分开。若依赖、已确认义务或战略选择改变得分顺序，逐项写明理由、证据与待确认决策人。

给出优先推进、先做验证、暂缓和未选项及理由；不机械凑满前五。相近分数不代表确定胜负；使用已有合理估算范围查看结论是否会改变，没有范围则描述会改变排序的未知项。

对重叠覆盖人群或重复业务收益注明可能重复计算；组合价值不能直接把每项独立收益相加。高影响但低置信度项目可以先安排验证，不因低分永久淘汰。

## 4. 形成结果路线图（需要时）

用 Now/Next/Later 或用户已有的季度/发布窗口组织；每项记录目标用户、期望结果、观测指标、候选交付物、依赖、负责人和置信度依据。

先画清前置关系并检查循环、遗漏前置项及跨团队依赖，再考虑排序。依赖关系不是日期承诺；没有可靠工期与容量时只能给顺序建议。

按团队和同一时间单位检查已知投入是否超过可用容量；考虑已知维护/运行投入。容量未知时注明“容量可行性未确认”，不说路线图已可执行。

Now/Next/Later 表示规划顺序，不自动等于已承诺/已批准。用户已有的承诺日期与建议调整分开列；确实无法满足时展示冲突与选项，不擅自删除或推迟承诺。

## 5. 输出与复核

使用 [排序和路线图模板](references/template.md)。交付目标及比较口径、约束、排序表、取舍记录、路线图和未决项；请求仅涉及排序时省略路线图部分。

复核单位、分母、数值范围和公式；逐项检查依赖、容量结论及承诺状态。保留缺少证据的条目，说明补什么证据可能改变决定。后续交接引用 I 编号和已有工单链接，不宣称已修改任何外部系统。

## 来源与适配

方法与结构适配自 Pawel Huryn 的 phuryn/pm-skills，MIT；EFP 增加硬约束、可复核计算、缺数处理和容量/承诺检查。版权和许可见 [上游 MIT 许可](references/LICENSE.upstream.txt)。固定版本：`8607e3b077817f89bf4a9b623246219734ac3be0`。

- [候选需求排序](https://github.com/phuryn/pm-skills/blob/8607e3b077817f89bf4a9b623246219734ac3be0/pm-product-discovery/skills/prioritize-features/SKILL.md)
- [优先级方法](https://github.com/phuryn/pm-skills/blob/8607e3b077817f89bf4a9b623246219734ac3be0/pm-execution/skills/prioritization-frameworks/SKILL.md)
- [结果路线图](https://github.com/phuryn/pm-skills/blob/8607e3b077817f89bf4a9b623246219734ac3be0/pm-execution/skills/outcome-roadmap/SKILL.md)
