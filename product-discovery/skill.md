---
name: product-discovery
description: "Turn research evidence into customer opportunities, competing solutions, and assumption-testing plans for PMs and BAs. Use for product discovery or interview planning before a build decision."
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /product-discovery
  - plan product discovery
  - synthesize customer research into opportunities
  - 产品发现与问题验证
  - 根据访谈梳理用户机会和实验
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

# 产品发现与验证计划

帮助 PM 和 BA 把用户材料变成可追踪的问题、解法与验证建议。交付分析草稿；已确定方案的详细需求规格不属于本技能的主要用途。

## 输入与工作边界

- 使用用户已提供的产品背景、目标用户、决策期限、访谈记录、反馈、数据摘要和约束；已有答案不重复追问。
- 优先识别要支持的决策，例如继续研究、选择问题、比较解法或进入需求细化。
- 信息不足时仅询问会改变该决策的问题，其余记录为“未知/待验证”并继续能完成的部分。
- 没有原始研究时输出问题假设、访谈提纲和验证计划；不生成虚构用户引语、访谈结果、数据或已验证结论。
- 本技能不要求联网、运行实验、联系受访者或写入 Jira、Confluence、bundle；提供可供后续交接的内容即可。

## 1. 整理证据

为材料建立 E 编号，记录来源、日期、具体页段或记录位置、用户群和局限。无法访问的来源注明“未读取”，不根据标题概括内容。

分开记录：

- **观察事实**：材料直接支持的行为、引语或数字，带 E 编号；引语保持原意，用户身份可用匿名编号。
- **解释/推断**：对原因或模式的分析，列支持与反对证据。
- **待验证假设**：尚无足够证据支持的判断，说明缺口及检验方法。

去重同一受访者或被转述多次的反馈；频次给出已知样本分母。质性样本不直接推断总体占比，不将重复出现当成已证明需求饱和。保留相互矛盾的材料及适用人群差异。

## 2. 定义问题和结果

用目标用户、触发场景、当前行为/替代办法、阻碍和后果描述问题；把“做一个功能”的请求还原为要改善的用户处境。

将用户价值与业务结果关联。结果应可观测；基线、目标值、截止时间只有在材料支持时填入，否则分别标未知或建议值，不能当作既有承诺。

已有访谈材料时综合洞见；需准备访谈时围绕最近一次实际经历、操作步骤、失败/绕行方式和现有投入设计开放问题。避免推销和“你会不会使用”式假设问题。输出记录字段与追问方向，不声称已开展访谈。

## 3. 比较机会与解法

按“结果 → 用户机会 O → 解法 S → 待验证假设 A”建立可引用结构。机会描述需求或困难，解法单列，不把内部功能名当作证据。

根据已知影响、覆盖人群、证据强弱和战略相关性比较机会；没有可靠量化输入时用定性理由，不自动打分。针对选中机会给出有实际差异的解法，通常比较两到三种，包括流程改进或复用现有能力的可能。

说明每个解法支持的机会、关键取舍及依赖。提出建议时同时记录未选方案和重新考虑它的条件。

## 4. 设计假设验证

从价值、可用性、可行性和业务可持续性检查决定成败的假设，优先处理影响大且证据薄弱的部分。确定性来自材料，不以评分代替证明。

为每项关键假设设计最小可行的检验卡，写明：

- 对应 A/O/S 编号、要消除的不确定性、现有证据和预期反证。
- 方法、目标人群、执行负责人、所需样本/时间及选择依据；未知项留待确认。
- 可观察行为、指标口径、成功与否定判据；拟议阈值明确标为建议。
- 保护用户体验或业务的护栏、停止条件以及不可判定时的后续动作。

访谈、原型任务或技术探查可以检验不同风险。选择 A/B 方法时只给设计草稿并注明分流、样本量和分析方案尚需确认；不将意愿表达等同实际行为，不把未达成功阈值一律判为失败。

## 5. 交付与复核

使用 [产物模板](references/template.md)，按任务范围保留需要的章节。交付证据摘要、问题/结果、机会与解法、假设实验卡和下一步建议。所有实验默认“计划中”；仅在用户提供实际结果时更新状态并引用来源。

检查结论是否能追溯证据、反证是否保留、观察与建议是否分离、关键未知是否影响建议成立。交接需求细化时给出问题/O/S/A 编号和未决问题；不要宣称已进入开发、已写 bundle 或已创建工单。

## 来源与适配

方法与结构适配自 Pawel Huryn 的 phuryn/pm-skills，MIT；EFP 增加中文流程、证据追踪、未知处理及执行边界。版权和许可见 [上游 MIT 许可](references/LICENSE.upstream.txt)。固定版本：`8607e3b077817f89bf4a9b623246219734ac3be0`。

- [访谈提纲](https://github.com/phuryn/pm-skills/blob/8607e3b077817f89bf4a9b623246219734ac3be0/pm-product-discovery/skills/interview-script/SKILL.md)
- [访谈综合](https://github.com/phuryn/pm-skills/blob/8607e3b077817f89bf4a9b623246219734ac3be0/pm-product-discovery/skills/summarize-interview/SKILL.md)
- [机会解法树](https://github.com/phuryn/pm-skills/blob/8607e3b077817f89bf4a9b623246219734ac3be0/pm-product-discovery/skills/opportunity-solution-tree/SKILL.md)
- [验证实验](https://github.com/phuryn/pm-skills/blob/8607e3b077817f89bf4a9b623246219734ac3be0/pm-product-discovery/skills/brainstorm-experiments-existing/SKILL.md)
