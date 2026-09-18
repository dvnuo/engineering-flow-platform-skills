# 素材目录

所有文件在 `/app/skills/pptx-brand/assets/` 下，spec 里一律写绝对路径。
替换成真实品牌文件时保持文件名，
或者同步修改 `styles.json` 与本目录。总大小控制在 3 MB 以内：每个 pod 启动都会 clone 一次 skills 仓库。

## 1. 模板 `template/efp-brand-template.pptx`

- 16:9，13.333 × 7.5 英寸，一个母版，主题名 EFP。
- 主题色：dk1 `1F2933`，lt1 `FFFFFF`，dk2 `0B2545`，lt2 `F3F4F6`，accent1 `1F6FEB`，accent2 `E8590C`，accent3 `0F9D8A`，accent4 `8E44AD`，accent5 `C0392B`，accent6 `F2C94C`。
- 主题字体：Calibri，中文 Microsoft YaHei。
- 母版装饰：底部一条 0.12 英寸高的海军蓝横条，左端橙色。母版不含 logo，logo 由 `styles.json` 统一放置。
- 版式：Title Slide、Title and Content、Section Header、Two Content、Comparison、Title Only、Blank、Content with Caption、Picture with Caption 等 11 个，均为 python-pptx 默认版式。脚本在 Blank 版式上绘制，其他版式暂不使用。
- 示例页（文字示例，共 11 页）：封面、议程页、分节页、要点页、对比页、数字页、卡片页、图表页、表格页、引用页、结尾页。每页标题都是该版式的写法说明，议程页和要点页带讲稿备注。用 `--template` 构建时这些示例页会被移除，只保留母版、尺寸和主题。
- 读取方式：`python /app/skills/pptx/scripts/inspect_template.py /app/skills/pptx-brand/assets/template/efp-brand-template.pptx`。

`formal` 和 `training` 两种风格使用这个模板，`review` 和 `keynote` 不用母版。

## 2. 背景图 `backgrounds/`（1920 × 1080 JPEG）

| 文件 | 画面 | 明暗 | 文字安全区 | 用在 |
| --- | --- | --- | --- | --- |
| `cover-formal.jpg` | 海军蓝对角渐变，右侧一道浅蓝斜带和点阵 | 深 | 左侧 60% 放白字 | `formal` 封面；配 overlay 0.45 |
| `cover-keynote.jpg` | 近黑底色，右上蓝色光晕、左下橙色光晕 | 深 | 中左区域放白字，避开右上光晕 | `keynote` 封面与结尾；overlay 0.2 到 0.35 |
| `section-light.jpg` | 白到浅灰渐变，右侧淡色三角与橙色角标 | 浅 | 左侧 65% 放深色字 | `formal` 与 `training` 分节页；`text: dark`，overlay 0 |
| `section-dark.jpg` | 深蓝底，右侧同心圆弧，橙色圆点 | 深 | 左侧 60% 放白字 | `review` 封面、`keynote` 分节与引用页 |
| `closing.jpg` | 海军蓝到青绿的对角渐变，中部柔光 | 深 | 全幅可放白字，标题居左 | 各风格结尾页 |
| `training.jpg` | 白到淡绿渐变，两个薄荷色圆，底部青绿色条 | 浅 | 左侧与中部放深色字，避开右上圆 | `training` 封面；`text: dark`，overlay 0 |

背景只用于封面、分节、结尾、引用页，内容页不放背景图。深色背景压白字必须有 overlay。

## 3. 图标 `icons/`

- `icon-sheet.png`：4 × 4 合集图，透明底，海军蓝线条图标，是 `slice_icons.py` 的输入示例。
- `navy/`：切好的 16 个单图标（256 px 透明 PNG），用于浅色页面；同目录 `icons.json` 是切片清单，`contact-sheet.png` 是带编号的预览图。
- `white/`：同一组图标的白色版本，用于深色页面和实景背景。

| 名称 | 画面 | 适合表达 |
| --- | --- | --- |
| `target` | 同心圆靶心 | 目标、OKR、聚焦 |
| `chart-up` | 三根递增柱 | 增长、趋势、业绩 |
| `shield` | 盾牌加对勾 | 安全、合规、可靠 |
| `gear` | 齿轮 | 配置、流程、自动化 |
| `users` | 两个人形 | 成员、客户、团队 |
| `clock` | 时钟 | 时效、延迟、排期 |
| `check` | 对勾 | 完成、通过、成功率 |
| `warning` | 三角感叹号 | 风险、告警、阻塞 |
| `cloud` | 云 | 云服务、平台、部署 |
| `lock` | 挂锁 | 权限、隐私、加密 |
| `bolt` | 闪电 | 速度、性能、快速迭代 |
| `flag` | 旗帜 | 里程碑、目标达成、发布 |
| `document` | 文档 | 报告、文档、规范 |
| `server` | 三层机架 | 基础设施、runtime、实例数 |
| `globe` | 地球 | 全球、跨团队、开放 |
| `bulb` | 灯泡 | 想法、洞察、建议 |

同一页只用一种颜色的图标，KPI 页和卡片页每项一个图标，要点页不用图标。

## 4. logo `logo/`

- `logo-primary.png`：海军蓝方形标记加 EFP 字标，透明底，1200 × 360，用于白色和浅色页面。
- `logo-white.png`：白色版本，用于深色页面和实景背景。
- 放置由 `styles.json` 的 `logo` 字段控制：内容页右上角，封面、分节、结尾页右下角（`training` 风格为右上角）。spec 不需要也不应该再引用 logo 文件。

## 5. 风格文件 `references/styles.json`

四种风格 `formal`、`review`、`keynote`、`training`，每种包含配色、字体、模板、页脚、logo 和各类页面的默认背景。
列出方式：`python /app/skills/pptx/scripts/build_deck.py --list-styles --styles /app/skills/pptx-brand/references/styles.json`。
spec 里写 `"style"` 和 `"styles_file"` 即可，单页 `background` 可覆盖默认背景。
