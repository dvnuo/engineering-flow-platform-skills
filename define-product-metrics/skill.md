---
name: define-product-metrics
description: "Define product success metrics, calculation contracts, instrumentation needs, and guardrails for PMs and BAs. Use when specifying KPIs or a measurement plan, before building dashboards or analyzing experiments."
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /define-product-metrics
  - define product success metrics
  - specify KPI definitions and guardrails
  - 定义产品指标口径与埋点需求
  - 制定产品效果衡量方案
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

# 产品指标与观测计划

为 PM 和 BA 形成可供数据、研发和运营协作的指标字典与观测需求草稿。重点是何谓成功、怎样计算以及如何据此行动，不直接搭建 dashboard 或执行统计实验。

## 输入与证据

- 使用已提供的目标用户、产品价值、业务目标、关键流程、现有指标、数据源和约束；有口径文档时优先沿用并指出冲突。
- 确认要支持的决策，例如发现流失环节、评估某项能力效果或监测用户体验。
- 未提供真实数据时只产出定义和观测计划；不声称读过数据表、查询过数据或发现趋势。
- 给已有基线、指标口径和目标注明来源与日期。未知填“未知”，建议阈值明确为待确认建议，不能编造历史值。
- 本技能不要求连接分析平台、写 SQL、部署埋点、创建告警或修改 bundle。

## 1. 选择与目标相称的指标

从用户获得的价值开始，选择能影响本次决策的少量指标，区分：

- **结果指标**：要改善的用户/业务结果；适合时提出北极星候选，不能为套用框架强制所有业务共用一个。
- **驱动指标**：团队可影响、预期与结果有关的行为信号。
- **护栏指标**：避免优化目标同时损害体验、可靠性、成本或其他相关结果。
- **业务指标**：观察收入、成本等商业效果，使用与本次目标相关的部分。

逐项说明“它发生变化时会改变什么决定”。只有活动量而缺少价值解释的指标应补充质量、成功率或分群视角。指标间驱动关系标为假设；相关变化不等于因果证明。

## 2. 写出可复现的计算口径

每个指标分配 M 编号，至少定义：

- 业务含义、分析实体（用户/账户/任务/订单等）、单位和聚合粒度。
- 公式、分子、分母、合格人群和事件条件；计数指标明确无分母。
- 统计窗口、时区、时间起点与截止、自然周期或滚动窗口；留存类注明 cohort 进入条件与回访窗口。
- 去重键、重复/重试事件规则、排除条件和需比较的分群。
- 数据来源、已知字段、更新延迟和口径负责人；未知来源/字段保持待确认。
- 分母为零、事件缺失、迟到数据和部分窗口的处理；缺数不能悄悄写成零。

不能以“转化率”“活跃用户”等名称代替公式。比率聚合应说明按总分子/总分母计算还是其他明确权重，不默认平均各组百分比。口径不同或窗口不完整时标记不可直接比较。

## 3. 明确基线、目标和护栏

分别列实际基线、基线观测期、目标/方向、达标期限以及依据。只有方向没有数值依据时先描述期望改变，给出建立基线的计划。

每个主要结果至少检查一个相关护栏；没有适用项时说明理由。护栏定义同样要明确口径、阈值来源、观察窗口与负责人。把产品表现异常和数据质量异常分开，避免把采集失败当作用户行为变化。

告警仅形成响应建议：由谁看、什么持续时间/样本条件触发调查、先检查什么、何时停止或回滚相关试验。没有足够基线时不设置伪精确阈值；不把指标告警自动解释成业务因果结论。

## 4. 形成观测需求

把 M 编号映射到所需事件、属性、业务对象 ID、触发时机和计算来源。区分“已存在并有证据”“需验证是否可用”“建议新增”。

对于新增观测，描述触发一次的业务语义、幂等/去重规则、客户端或服务端来源以及必要字段；仅采集支持本次指标的必要信息。事件名和字段若尚无约定，标为提案。

提供验收样例：成功、失败/取消、重试、跨窗口、分母为零、事件迟到时预期怎样计数；按实际业务挑选相关情形。不要把验收计划写成已完成测试。

## 5. 输出和交接

使用 [指标定义模板](references/template.md) 交付指标结构、完整字典、观测映射、验收场景、复查节奏和未决问题。小任务可以只保留涉及的指标和章节。

建议呈现方式须服务决策：趋势看变化、漏斗看环节、分群看差异。每项给出查看频率和建议负责人；不凭模板假设数据每日可用。

最终复核不同分析人员是否能用同一输入得出同一数值，数据缺失是否可识别，目标与基线是否分开，护栏是否覆盖主要副作用。交接至研发/数据团队时引用 M 编号和待确认字段，不声称已实现埋点或上线看板。

## 来源与适配

方法与结构适配自 Pawel Huryn 的 phuryn/pm-skills，MIT；EFP 增加计算口径、缺数处理、事件契约及观测验收。版权和许可见 [上游 MIT 许可](references/LICENSE.upstream.txt)。固定版本：`8607e3b077817f89bf4a9b623246219734ac3be0`。

- [指标看板定义](https://github.com/phuryn/pm-skills/blob/8607e3b077817f89bf4a9b623246219734ac3be0/pm-product-discovery/skills/metrics-dashboard/SKILL.md)
- [北极星与驱动指标](https://github.com/phuryn/pm-skills/blob/8607e3b077817f89bf4a9b623246219734ac3be0/pm-marketing-growth/skills/north-star-metric/SKILL.md)
