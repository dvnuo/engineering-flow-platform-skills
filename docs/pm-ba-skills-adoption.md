# PM / BA 技能吸收评估

评估日期：2026-09-18。目标用户是 Product Manager（PM）与 Business Analyst（BA）。本轮实际读取四个仓库的技能正文及相关模板，按以下固定提交评估；后续版本变化不自动进入 EFP。

## 来源与取舍

| 仓库及固定版本 | 本轮结论 | 适合吸收的部分 | 暂不吸收的部分 |
| --- | --- | --- | --- |
| [phuryn/pm-skills](https://github.com/phuryn/pm-skills/tree/8607e3b077817f89bf4a9b623246219734ac3be0) | 主要 PM 方法来源，MIT | 从证据到机会、假设和实验；优先级取舍；结果导向路线图；指标设计 | 整套插件与命令链、营销文案、定价、SQL 和统计执行工具 |
| [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD/tree/0a00053409731db811f2595ceb521dff9dde9a19) | 需求交付方法来源，MIT | PRD 的范围和追溯、价值切片的故事、实现前就绪判断 | Persona、菜单、安装器、`_bmad` 状态目录、编排框架及完整开发流程 |
| [deanpeters/Product-Manager-Skills](https://github.com/deanpeters/Product-Manager-Skills/tree/1b5a524ebb95e9497fa3f25002d8b8ec528d4444) | 完成评估，本轮不复制或改编正文 | 发现、优先级、路线图和指标的候选方法可供后续独立评估 | 当前为 CC BY-NC-SA 4.0；EFP 再分发与产品包装场景尚未确定，本轮不纳入其文本 |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills/tree/19392f7a08264ed00486a251f5b2098321771f94) | 补充 PM/BA 结构参考，MIT | PRD 模板、用户旅程、用户故事/验收和研究证据链；结合 EFP 扩展业务流程与变更分析 | 整库镜像、硬编码评分门槛/点数/产能、英文词频访谈分析脚本及未经验证的统计工具 |

许可证核验：[phuryn MIT](https://github.com/phuryn/pm-skills/blob/8607e3b077817f89bf4a9b623246219734ac3be0/LICENSE)、[BMAD MIT](https://github.com/bmad-code-org/BMAD-METHOD/blob/0a00053409731db811f2595ceb521dff9dde9a19/LICENSE)、[deanpeters CC BY-NC-SA](https://github.com/deanpeters/Product-Manager-Skills/blob/1b5a524ebb95e9497fa3f25002d8b8ec528d4444/LICENSE)、[claude-skills MIT](https://github.com/alirezarezvani/claude-skills/blob/19392f7a08264ed00486a251f5b2098321771f94/LICENSE)。

deanpeters 的 [README 许可说明](https://github.com/deanpeters/Product-Manager-Skills/blob/1b5a524ebb95e9497fa3f25002d8b8ec528d4444/README.md#license)明确允许在包括营利公司在内的日常工作、团队和 agent 中使用，并对改编分享和重新包装销售说明了限制。暂缓的原因是本次向 EFP 技能库再分发的边界，不是认定其禁止企业内部使用；不把其他仓库或旧版本的许可套用到它。

新增技能为中文 EFP 适配稿，保留英文发现描述、中英触发词和固定提交来源。各目录随附完整 `references/LICENSE.upstream.txt`，以便单个 skill 及 OpenCode 同步包保留相关上游通知。BMAD 的许可文件含商标通知，来源归属不表示获得其背书。流程分析中的决策表、变更基线及影响矩阵属于 EFP 补充设计；未声称 claude-skills 提供独立的 business-analyst 技能。

## 首批能力与输入输出

| EFP skill | 输入 | 核心产物与边界 |
| --- | --- | --- |
| [product-discovery](../product-discovery/skill.md) | 用户问题、访谈/反馈及来源 | 证据索引、机会、待验证假设、实验与证伪条件；没有资料时输出研究计划 |
| [prioritize-roadmap](../prioritize-roadmap/skill.md) | 候选项、目标、约束及有来源的估计 | 可复核比较与 Now/Next/Later 路线图；数据不足时用定性排序，不虚构 RICE 数字或承诺日期 |
| [define-product-metrics](../define-product-metrics/skill.md) | 业务目标、用户行为和数据现状 | 指标口径、分母/窗口、护栏、事件与数据检查；不编造基线或实验结论 |
| [write-product-requirements](../write-product-requirements/skill.md) | 问题、研究、流程和业务规则 | PRD、稳定需求 ID、验收与证据链；未知阈值保留待确认 |
| [break-down-user-stories](../break-down-user-stories/skill.md) | PRD 或已标识的需求 | 价值切片、故事/验收 ID、依赖及需求覆盖；不自动创建 Jira 工单 |
| [review-requirements-readiness](../review-requirements-readiness/skill.md) | 当前版本的需求及已有交付材料 | 有依据的就绪判断、阻断问题和修复责任；未提供的材料不会被宣称已审阅 |
| [analyze-business-process](../analyze-business-process/skill.md) | 现状流程、角色、规则和异常 | 现状/目标流程、角色交接、决策表与差距；目标流程建议不混成已确认事实 |
| [analyze-requirement-change](../analyze-requirement-change/skill.md) | 基线、变更请求和已有追溯关系 | 差异、影响链、备选方案及决策记录；没有基线时只能给初步影响 |

发现、优先级、PRD、故事和指标在多个上游重复出现。EFP 按用户任务合并为聚焦入口，避免同一请求同时命中多个近义技能。业务流程与变更影响补齐 BA 工作，不将 PM 增长框架直接等同于 BA 能力。

### 具体来源定位

每项技能末尾记录实际参考的文件与固定提交 URL。以下是本轮主要评估入口，模板与参考正文通过相应目录核验：

- phuryn：[`pm-product-discovery/skills`](https://github.com/phuryn/pm-skills/tree/8607e3b077817f89bf4a9b623246219734ac3be0/pm-product-discovery/skills) 下的 interview-script、summarize-interview、opportunity-solution-tree、prioritize-assumptions、brainstorm-experiments-existing、prioritize-features、metrics-dashboard，以及 [`pm-execution/skills`](https://github.com/phuryn/pm-skills/tree/8607e3b077817f89bf4a9b623246219734ac3be0/pm-execution/skills) 下的 prioritization-frameworks 和 outcome-roadmap。
- BMAD：[`bmad-prd`](https://github.com/bmad-code-org/BMAD-METHOD/tree/0a00053409731db811f2595ceb521dff9dde9a19/skills/bmad-prd)、[`bmad-create-epics-and-stories`](https://github.com/bmad-code-org/BMAD-METHOD/tree/0a00053409731db811f2595ceb521dff9dde9a19/skills/bmad-create-epics-and-stories) 及 [`readiness-gate.md`](https://github.com/bmad-code-org/BMAD-METHOD/blob/0a00053409731db811f2595ceb521dff9dde9a19/skills/bmad-sprint-planning/references/readiness-gate.md)。此版本已经使用 `skills/` 结构，不引用旧版本 `src/bmm` 路径。
- claude-skills：[`product-manager-toolkit`](https://github.com/alirezarezvani/claude-skills/tree/19392f7a08264ed00486a251f5b2098321771f94/product-team/skills/product-manager-toolkit)、[`agile-product-owner`](https://github.com/alirezarezvani/claude-skills/tree/19392f7a08264ed00486a251f5b2098321771f94/product-team/agile-product-owner/skills/agile-product-owner)、[`ux-researcher-designer`](https://github.com/alirezarezvani/claude-skills/tree/19392f7a08264ed00486a251f5b2098321771f94/product-team/skills/ux-researcher-designer) 及 [`product-research`](https://github.com/alirezarezvani/claude-skills/tree/19392f7a08264ed00486a251f5b2098321771f94/research-ops/skills/product-research)。
- deanpeters：已读 [discovery-process](https://github.com/deanpeters/Product-Manager-Skills/blob/1b5a524ebb95e9497fa3f25002d8b8ec528d4444/skills/discovery-process/SKILL.md)、[prioritization-advisor](https://github.com/deanpeters/Product-Manager-Skills/blob/1b5a524ebb95e9497fa3f25002d8b8ec528d4444/skills/prioritization-advisor/SKILL.md)、[roadmap-planning](https://github.com/deanpeters/Product-Manager-Skills/blob/1b5a524ebb95e9497fa3f25002d8b8ec528d4444/skills/roadmap-planning/SKILL.md)、[derisk-measurement-advisor](https://github.com/deanpeters/Product-Manager-Skills/blob/1b5a524ebb95e9497fa3f25002d8b8ec528d4444/skills/derisk-measurement-advisor/SKILL.md)。适合后续考虑其方法选型与引导结构；直接导入会带入交互步骤和其他 skill 依赖。它们不是本次新增技能或模板的改编来源。

## EFP 集成约定

1. 仓库根目录即 skill root；新增入口为 `<skill-name>/skill.md`，不引入嵌套 `skills/` 或生成后的 `.opencode/`。
2. 本轮均为 `tools: []`、`execution_kind: prompt_only`、`compatibility: full`、`permission.default: ask`。运行时读取随附模板，无新增 Python 执行器、第三方依赖或上游安装步骤。
3. `full` 指提示词及资源的适配范围；真实业务产出仍需 PM/BA 判断，元数据验证不等于模型质量评测或部署验收。
4. 核心产物是 Markdown 草稿。来源内容足够时直接推进，影响结论的重要未知项列为待确认；保持用户语言和模板，不为了填满表格捏造数据。
5. 可消费用户提供的 `requirements.yaml` / research-notes 内容，但不声称会自动读任意 bundle URL。需要外部资料时使用当前已授权、实际可用的集成，缺访问能力时说明限制。
6. 现有 `collect_requirements_to_bundle` 和 `collect_research_notes_to_bundle` 负责采集及原生 bundle 写入；实施计划、测试设计、Jira 批量创建仍由现有专用技能处理。分析草稿不是 runtime YAML schema，不直接覆盖 `requirements.yaml`。
7. `master` 为完整库，`business` 为角色子集；本批新增技能、模板和说明同步到两条分支。合并 PR 不自动更新已部署 agent，需按 README 的 skill branch/version 更新方式生效。

## 可复用的评审场景

这些场景用于读取技能后的人工/agent 行为核验，不用关键词匹配代替产出质量：

| 场景 | 检查实际产物 |
| --- | --- |
| 两份访谈记录包含同一受访者，另有反例 | 不把重复提及算作独立用户；保留反例和样本限制；没有研究结果时只给计划 |
| 功能 A 给出月触达，B 给出年触达，C 缺工作量 | 不直接混算 RICE；标明转换假设和缺项；必要依赖不被分数覆盖；不给虚假确定日期 |
| “提高留存”但没有数据和埋点 | 定义 eligible population、分母、窗口及事件；基线/目标待确认；不宣称显著提升 |
| PRD 写“快速审批”，拒绝/撤销流程未定义 | 形成可追溯需求，量化阈值待确认；故事暴露异常分支；就绪评审说明决策缺口 |
| 同一需求的两份文档定义冲突，故事只覆盖成功路径 | 引用双方版本和位置；保留冲突；覆盖矩阵显示遗漏；不得声称全部 ready |
| 金额恰在审批阈值且两条业务规则均匹配 | 决策表展示重叠或空白，无法判定时列问题而非私自选规则 |
| 要求改变退款规则但没有原始基线或下游映射 | 输出初步影响与待核查列表；不将未提供的服务/测试/负责人冒充已确认影响 |

结构验证使用仓库现有 validator、contract exporter、pytest 和 smoke script。新增 Markdown 与模板不增加只检查固定措辞的测试；实际行为评审另行记录在 PR 中。

## 后续候选

在首批用于真实需求后，可按反馈再评估竞争研究、利益相关者访谈、产品战略/OKR 与实验分析。引入计算脚本前单独验证公式、单位、边界和数据依赖；引入新的来源文本时重新核验固定版本许可。不要依据仓库 star 数量或技能总数批量镜像。

本评估覆盖所列 PM/BA 相关条目及其参考文件，不是对四个仓库全部内容的质量认证。
