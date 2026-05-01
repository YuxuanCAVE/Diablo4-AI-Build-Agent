# Build JSON Schema Design

当前 MVP 使用文档化 schema，不引入 JSON Schema 校验依赖。字段命名保持简单，方便后续接入校验、网页解析和数据库。

## 顶层字段

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `source_url` | string | 是 | 原始暗黑核 / d2core BD 页面链接。 |
| `game_version` | string | 否 | 游戏版本，例如 `2.2.0`。 |
| `season` | string | 否 | 赛季信息，例如 `Season 7`。 |
| `class` | string | 是 | 职业，例如 `Rogue`、`Sorcerer`。 |
| `build_name` | string | 是 | Build 名称。 |
| `build_type` | string[] | 是 | Build 类型，例如 `leveling`、`endgame`、`bossing`、`speed farming`。 |
| `core_skills` | object[] | 是 | 核心技能列表。 |
| `passive_skills` | object[] | 否 | 被动技能列表。 |
| `gear` | object[] | 否 | 装备列表，按部位组织。 |
| `aspects` | object[] | 否 | 传奇威能列表。 |
| `uniques` | object[] | 否 | 暗金装备列表。 |
| `affix_priorities` | object[] | 否 | 词条优先级。 |
| `paragon_boards` | object[] | 否 | 巅峰盘。 |
| `glyphs` | object[] | 否 | 雕文。 |
| `legendary_nodes` | object[] | 否 | 传奇节点。 |
| `author_notes` | string[] | 否 | 作者备注或人工整理备注。 |
| `ai_analysis_status` | object | 是 | AI 分析状态。 |

## `core_skills[]`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | 技能名称。 |
| `role` | string | 技能角色，例如 `main_damage`、`mobility`、`defense`、`damage_enabler`。 |
| `notes` | string | 技能用途说明。 |

## `passive_skills[]`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | 被动技能名称。 |
| `priority` | string | 优先级，例如 `high`、`medium`、`low`。 |
| `notes` | string | 被动技能作用。 |

## `gear[]`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `slot` | string | 装备部位，例如 `helm`、`amulet`、`ranged_weapon`。 |
| `item_type` | string | 装备类型，例如 `legendary`、`unique`、`rare`。 |
| `name` | string | 装备名称。 |
| `required` | boolean | 是否是 Build 高依赖装备。 |
| `recommended_affixes` | string[] | 推荐词条。 |

## `aspects[]`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | 威能名称。 |
| `slot` | string | 推荐放置部位。 |
| `priority` | string | 优先级。 |
| `notes` | string | 选择原因。 |

## `uniques[]`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | 暗金名称。 |
| `slot` | string | 装备部位。 |
| `required` | boolean | 是否必须。 |
| `notes` | string | 使用说明。 |

## `affix_priorities[]`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `category` | string | 分类，例如 `offense`、`defense`、`utility`。 |
| `priority_order` | string[] | 从高到低排列的词条。 |
| `notes` | string | 排序依据。 |

## `paragon_boards[]`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | 巅峰盘名称。 |
| `purpose` | string | 该盘在 Build 中的目的。 |
| `important_nodes` | string[] | 重要稀有节点或路线节点。 |

## `glyphs[]`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | 雕文名称。 |
| `board` | string | 所属巅峰盘。 |
| `priority` | string | 优先级。 |
| `notes` | string | 使用原因。 |

## `legendary_nodes[]`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | 传奇节点名称。 |
| `board` | string | 所属巅峰盘。 |
| `priority` | string | 优先级。 |
| `notes` | string | 选择原因。 |

## `ai_analysis_status`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `status` | string | 状态，例如 `draft`、`ready_for_analysis`、`analyzed`、`needs_review`。 |
| `missing_fields` | string[] | 当前缺失字段。 |
| `last_analyzed_at` | string/null | 最近分析时间，建议使用 ISO 8601。 |
| `notes` | string | 额外说明。 |

## 设计原则

- 字段尽量接近玩家理解方式，而不是数据库范式。
- `required` 用于区分硬依赖和可选增强。
- `notes` 字段保留人工整理信息，方便 LLM 解释依据。
- 不在 schema 中强制推导游戏机制，机制解释交给分析阶段，但必须受 JSON 限制。
