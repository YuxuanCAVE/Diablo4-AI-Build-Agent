# Diablo4 AI Build Agent

本项目用于把本地保存的暗黑核 / d2core Build JSON 整理成适合 LLM 分析的输入文件。当前阶段不做网页爬虫、不接真实 LLM API、不做前端。

## Recommended Workflow

普通 Build 分析只生成一个文件：

```powershell
python .\src\prepare_llm_input.py --raw data\raw\d2core_raw_001.json --variant 4
```

输出：

```text
outputs/build_analysis_input.json
```

如果还要让 LLM 探索可能替换项、降配项或测试项：

```powershell
python .\src\prepare_llm_input.py --raw data\raw\d2core_raw_001.json --variant 4 --with-candidates --candidate-limit 15
```

输出：

```text
outputs/build_analysis_input.json
outputs/build_candidate_pool.json
```

实际投给 LLM 时，优先使用这 1 到 2 个文件。

## Output Files

`outputs/build_analysis_input.json`

- 面向普通 Build 分析。
- 包含任务规则、报告结构和 `current_build`。
- 包含 `mechanic_summary`，用于解释伤害类型、技能标签、加法/乘法伤害倾向、触发机制、防御层、资源循环和覆盖率依赖。
- `current_build` 内已嵌入当前 BD 用到的技能、威能、暗金、词条、符文、雕文和传奇节点描述。

`outputs/build_candidate_pool.json`

- 可选文件。
- 用于候选替换、降配、测试项探索。
- 候选项来自 `data/reference/`，按职业、关键词、标签和当前 Build 机制筛选。
- 候选池不是优化结论，只是“可能相关”的选择列表。

## Data Layout

```text
data/
|-- raw/          # 原始 d2core 响应 JSON
|-- reference/    # 游戏资料库：威能、暗金、词条、巅峰、符文、技能树等
|-- examples/     # 示例 JSON 和手工整理模板
|-- converted/    # 开发调试用：转换后的 Build JSON
`-- candidates/   # 开发调试用：候选池 JSON

outputs/
|-- build_analysis_input.json
`-- build_candidate_pool.json
```

## Developer Tools

这些脚本保留为开发工具，日常使用优先跑 `prepare_llm_input.py`。

转换 raw JSON 到 converted JSON：

```powershell
python .\src\convert_d2core_raw.py --raw data\raw\d2core_raw_001.json --variant 4
```

校验 Build JSON：

```powershell
python .\src\validate_build_json.py data\converted\d2core_1STz_variant_4.json
```

检查数据质量：

```powershell
python .\src\check_build_quality.py data\converted\d2core_1STz_variant_4.json
```

生成 Markdown prompt：

```powershell
python .\src\generate_prompt.py --build data\converted\d2core_1STz_variant_4.json --output outputs\d2core_1STz_variant_4_prompt.md
```

单独生成候选池：

```powershell
python .\src\generate_candidate_pool.py --build data\converted\d2core_1STz_variant_4.json --limit 15
```

## LLM Usage

普通分析时，把 `outputs/build_analysis_input.json` 给 LLM，并要求它按 JSON 内的 `rules` 和 `report_sections` 输出报告。

候选探索时，同时给：

- `outputs/build_analysis_input.json`
- `outputs/build_candidate_pool.json`

并要求 LLM 区分：

- 可能提升输出
- 可能提升生存
- 可能降低装备门槛
- 不建议替换的核心件
- 需要实测或当前数据不足的部分

`mechanic_summary` 是解释辅助，不是完整数值模拟器。它会提醒 LLM 不要计算真实 DPS，不要把加法伤害和乘法伤害混为一谈，并在讨论暴击、易伤、压制、幸运一击时说明触发可靠性。

## Current Boundaries

- 不做网页爬虫。
- 不接真实 LLM API。
- 不做数据库、账号、登录或前端。
- 不计算完整伤害、防御、减伤公式。
- 候选池不是强度排序，也不是自动优化结果。
