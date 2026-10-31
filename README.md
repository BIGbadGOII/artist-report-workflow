# Artist Report Generation Workflow

艺术家研究报告的核心生成规范：从艺术家身份确认开始，经多源检索、结构化事实抽取、冲突检查和引用核验，最终生成 JSON、可读报告与浏览器交付页面。

这个仓库只保留“生成报告”本身和可安装的 Codex Skill（含校验/渲染脚本、示例和测试），不包含完整 Web 产品、移动端、视频或后台业务系统。`viewer/` 是遗留原型，见下文。

> 推荐通过 `skills/artist-report` 在 Codex 中运行。Codex 使用自身的联网检索能力完成研究，不需要额外部署模型 API。

## 生成流程

1. **身份消歧**：根据姓名、别名、出生年份、媒介、地区和稳定标识确认目标艺术家，禁止仅凭同名合并记录。
2. **来源检索**：优先检索艺术家官方资料、博物馆与公共机构、画廊、展览机构和拍卖行原始记录。
3. **证据登记**：保存来源 URL、标题、发布或访问时间、来源层级，以及支持具体陈述的证据。
4. **结构化抽取**：先把身份、创作、展览、机构收藏、画廊代理和公开市场事实写入固定 schema。
5. **覆盖与冲突检查**：为缺失、有限或互相矛盾的数据设置明确状态，不用推测补齐空白。
6. **叙述生成**：只在事实抽取后生成概览与分析；区分艺术家陈述、机构/画廊解释、独立评论和系统综合。
7. **潜力评估**：只用已核实的事实整理动能信号（机构展览、奖项、画廊代理、艺博会、评论关注、公共收藏、市场事实）和反向信号/风险，每条附来源；不做价格预测或买卖建议。
8. **质量检查**：`render_report.py --check` 校验 schema、展览日期与状态、拍品结果、图片来源与路径、潜力评估来源、禁用投资语言。
9. **交付**：输出 `report.json`、`sources.md`、`image-audit.md`、`assets/` 与单文件 `report.html`，并标注生成时间、信息截止日期、版本与资料覆盖状态。

## 输入与输出

最小输入：

- 艺术家姓名；
- 用户确认的艺术家实体；
- 可选的别名、国家/地区、媒介或画廊信息，仅用于消歧。

也可以让 Skill 从一个艺博会（或双年展、奖项名单）里挑选艺术家：它会先从主办方官方名单核实参展信息，列出 3–5 位候选及理由，写入 `selection-notes.md`。

输出目录：`artist-reports/<artist-slug>-<YYYYMMDD>/`

```text
report.json          符合 v2.1 schema 的结构化报告（唯一数据源）
sources.md           编号来源登记：URL、访问日期、来源层级、支持的章节
image-audit.md       每张图片一行的语义审核表
assets/              经核实、有来源与署名的本地图片
report.html          由 report.json 渲染的中英双语单文件网页，可打印为 PDF
selection-notes.md   （仅当艺术家是从艺博会等名单中挑选时）候选名单与选择理由
```

报告中会写明冲突、资料缺口（`gap` 字段）、市场数据限制和信息截止日期。

## 文件

```text
skills/artist-report/                      ★ 可安装的 Codex Skill（唯一现行规范）
  SKILL.md                                 工作流与编辑红线
  references/report-schema.json            现行 schema（v2.1）
  references/research-standard.md          来源、潜力评估、艺博会选人规则
  references/visual-standard.md            章节顺序与图片规则
  assets/                                  image-audit / selection-notes 模板
  scripts/render_report.py                 校验 + 渲染（仅 Python 标准库）
  scripts/templates/                       HTML / CSS / JS 模板
examples/marc-chalme-20260805/             通过 --check 的 v2.1 示例（由 v0.1 迁移）
tests/                                     校验器与渲染器的 unittest 测试（仅标准库）
product-spec/                              遗留 v0.1 规范与 schema（仅存档）
reports/                                   遗留 v0.1 样例（JSON / Markdown）
viewer/                                    遗留原型：写死的杉本博司页面
```

## 在 Codex 中使用

把 `skills/artist-report` 安装到 Codex 的 skills 目录，重新打开 Codex 后即可调用：

```text
使用 $artist-report 研究 Louise Bourgeois，并输出中英文网页报告。
```

Skill 会执行身份消歧、实时联网检索、来源分级、冲突检查和双语写作，并输出上面列出的文件。网页默认中文，章节全部展开，只保留章节导航、中英文切换与“保存 PDF”。

## 校验、渲染与测试

```bash
python3 skills/artist-report/scripts/render_report.py --check --input examples/marc-chalme-20260805/report.json
python3 skills/artist-report/scripts/render_report.py --input <dir>/report.json --output <dir>/report.html
python3 -m unittest discover -s tests -v
```

单文件 HTML 目标小于 10 MB：超过 8 MB 时提示，超过 10 MB 时警告（`--check` 给出估算值）。

CI 工作流文件位于 `ci/github-actions-test.yml`，它会运行测试并校验、渲染示例报告。如需启用 GitHub Actions，须由仓库所有者手动复制为 `.github/workflows/test.yml`：

```bash
mkdir -p .github/workflows && cp ci/github-actions-test.yml .github/workflows/test.yml
```

## 浏览器查看与保存 PDF

直接用浏览器打开 `report.html`。“保存 PDF”会打开打印面板并使用 A4 打印样式；导出的 PDF 只包含当前语言，工具栏和导航不会出现在成品里。

`viewer/` 是遗留原型：它只用 iframe 加载预编译的 Expo 包和写死的杉本博司图片，不读取 `report.json`，也不使用渲染脚本，无法显示其他艺术家。详见 `viewer/README.md`。

## 产品边界

报告不提供作品鉴定、单件作品估值、买卖建议或价格上涨预测（“潜力评估”只陈述有来源的事实与风险），也不能替代法律、税务、保存修复或专业尽调。付费艺术市场数据库的数据不得在没有相应 API 或商业授权时自动化再分发。
