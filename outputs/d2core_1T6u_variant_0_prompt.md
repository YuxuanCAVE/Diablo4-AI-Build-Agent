# Diablo 4 Build Analysis Prompt

你是一名暗黑破坏神 4 Build 分析助手。你的任务是基于用户提供的结构化 Build JSON，生成一份适合普通玩家理解的中文分析报告。

## 强制规则

1. 只能基于输入 JSON 中存在的信息进行分析。
2. 不允许编造 JSON 中没有出现的技能、装备、威能、暗金、巅峰盘、雕文、传奇节点或游戏机制。
3. 如果某个报告章节需要的信息在 JSON 中缺失或不充分，必须明确写出“当前数据不足”，并说明缺少哪些字段。
4. 可以给出建议，但必须说明建议依据来自 JSON 中的哪个字段或组合。
5. 不要把示例数据当作官方攻略或真实强度结论。
6. 输出应面向普通玩家，避免过度术语化；必要术语需要用一句话解释。
7. 不要输出和 Build 无关的泛泛游戏建议。
8. 如果 JSON 同时提供名称和 description / affix_details / selected_mods / bonus / legendary_bonus，必须优先依据这些描述分析，不要只凭名称推断机制。
9. 如果 JSON 中的 `_conversion_quality` 提示某些字段为自动推断，报告里需要把相关结论标注为“根据当前数据推测”。

## 输出格式

请按以下结构输出 Markdown 报告：

### Build Overview

概括职业、Build 名称、Build 类型、赛季/版本，以及整体玩法定位。

### Core Mechanism

说明这个 Build 的核心伤害或运转机制。只引用 JSON 中的技能、威能、暗金、词条、巅峰盘和作者备注。
优先引用技能 description、selected_mods、威能 description、暗金 description、雕文 bonus 和传奇节点 description。

### Skill Synergy

解释核心技能、被动技能之间的配合关系。如果技能信息不足，说明当前数据不足。
如果 passive_skills 为空，可以基于 core_skills 和 selected_mods 分析主动技能联动，但必须说明“被动技能数据当前不足”。

### Gear Dependency

说明哪些装备、威能或暗金是高依赖项，哪些只是可选增强。需要区分 required=true 和 required=false。
分析装备时优先使用 gear.affix_details、aspects.description、uniques.description 和 sockets.description。

### Affix Priority Explanation

解释词条优先级为什么这样排列。必须基于 affix_priorities、core_skills、gear 或 author_notes。
如果 affix_priorities 标注为自动汇总，不要把它说成官方优先级，只能解释这些词条在当前装备中体现出的倾向。

### Paragon and Glyph Logic

解释巅峰盘、雕文和传奇节点的选择逻辑。如果相关字段为空，说明当前数据不足。

### Strengths

列出 Build 的主要优势。每个优势都要有 JSON 依据。

### Weaknesses

列出 Build 的主要短板或风险。不能凭空假设，只能基于缺失字段、required 装备、作者备注或结构化数据推断。

### Beginner Friendliness

判断新手友好度，并说明原因。重点考虑装备依赖、机制复杂度、是否需要特定暗金或关键威能。

### Missing Gear Alternatives

如果 JSON 中存在可选暗金或非必需装备，说明缺少它们时可以优先保证哪些功能性需求。不能编造替代装备名称。

### Final Recommendation

给出最终建议：适合什么玩家、优先补什么、什么时候不建议使用。

## Build JSON

```json
{
  "source_url": "https://www.d2core.com/d4/planner/1T6u",
  "game_version": "",
  "season": "Season 13",
  "class": "Warlock",
  "build_name": "地狱火 「全屏爆爆爆」每日更装备►天塔第一 127层 泽泽没烦恼 - Variant 0",
  "build_type": [
    "farm",
    "endgame",
    "race"
  ],
  "core_skills": [
    {
      "name": "幽冥行走",
      "key": "warlock_nether_step",
      "rank": 1,
      "role": "defense",
      "description": [
        "冷却时间: 12 秒",
        "穿行于地狱阴影间并在目标位置现身，获得 4 层暗影形态，同时获得 50%[x] 移动速度加成，该效果在 {val1} 秒内逐渐衰减。"
      ],
      "damage_type": "",
      "tags": [
        "防御",
        "秘术",
        "深渊",
        "机动",
        "暗影形态",
        "幽冥行走",
        "冷却时间",
        "移动"
      ],
      "selected_mods": [
        {
          "name": "伤害减免",
          "eng_name": "Damage Reduction",
          "key": "2218211_2686060761",
          "description": [
            "幽冥行走提供 60% 伤害减免，该效果会随其移动速度加成一同衰减。"
          ]
        },
        {
          "name": "移动速度",
          "eng_name": "Movement Speed",
          "key": "2218211_2686060764",
          "description": [
            "幽冥行走的移动速度加成延长 50%。"
          ]
        },
        {
          "name": "幽影行者",
          "eng_name": "Gloomwalker",
          "key": "2218211_2686060810",
          "description": [
            "幽冥行走现在能让你在深渊中奔行，在此期间获得免疫效果，最多持续 3 秒。再次施放可提前退出。"
          ]
        }
      ],
      "notes": "rank=1; active_bar=true"
    },
    {
      "name": "命令瓦洛克",
      "key": "warlock_command_valloch",
      "rank": 0,
      "role": "summon_command",
      "description": [
        "支配力消耗: 20",
        "被动: 瓦洛克使你的最大压制层数提高 4 层且愤怒上限提高 40 点。",
        "主动: 命令瓦洛克虹吸自身力量，使你的压制超额填充 2 层，并在 6 秒内使愤怒回复速度提高 {val1}%[+]。"
      ],
      "damage_type": "物理伤害",
      "tags": [
        "灵魂碎片",
        "恶魔学",
        "召唤",
        "高阶恶魔",
        "压制",
        "灵魂碎片命令"
      ],
      "selected_mods": [],
      "notes": "rank=0; active_bar=true"
    },
    {
      "name": "炽焰尖啸",
      "key": "warlock_blazing_scream",
      "rank": 15,
      "role": "main_damage_or_core",
      "description": [
        "愤怒消耗: 35",
        "幸运一击几率: 25%",
        "释放一个恶魔头骨，沿途造成 {val1}% 点伤害。"
      ],
      "damage_type": "火焰伤害",
      "tags": [
        "核心",
        "地狱火",
        "恶魔学",
        "高阶恶魔",
        "炽焰尖啸",
        "核心",
        "伤害",
        "火焰",
        "愤怒"
      ],
      "selected_mods": [
        {
          "name": "冲击动能",
          "eng_name": "Impact Velocity",
          "key": "2213860_2686060761",
          "description": [
            "炽焰尖啸根据你的移动速度加成，最多获得 30%[x] 伤害加成和速度加成。"
          ]
        },
        {
          "name": "消耗减免",
          "eng_name": "Cost Reduction",
          "key": "2213860_2686060762",
          "description": [
            "命中任意敌人时，炽焰尖啸的消耗降低 25%，持续 2 秒。"
          ]
        },
        {
          "name": "凿颅者",
          "eng_name": "Skull Splitter",
          "key": "2213860_2686060809",
          "description": [
            "炽焰尖啸会射出更小的低阶恶魔头骨追踪敌人，造成 29% 点伤害。"
          ]
        }
      ],
      "notes": "rank=15; active_bar=true"
    },
    {
      "name": "末日浩劫",
      "key": "warlock_apocalypse",
      "rank": 15,
      "role": "ultimate",
      "description": [
        "冷却时间: 67 秒",
        "幸运一击几率: 50%",
        "创造一个巨大的符印，在 2.0 秒后爆炸，对范围内的所有敌人造成 {val1}% 点伤害。",
        "此仪式不受冷却时间缩减影响。"
      ],
      "damage_type": "火焰伤害",
      "tags": [
        "终极技能",
        "秘术",
        "地狱火",
        "末日浩劫",
        "冷却时间",
        "伤害",
        "火焰",
        "终极技能"
      ],
      "selected_mods": [
        {
          "name": "双重爆裂",
          "eng_name": "Double Blast",
          "key": "2221260_2686060763",
          "description": [
            "末日浩劫的最后一击有 20% 几率命中两次。若末日浩劫受到易爆强化，则该几率提高至 100%。"
          ]
        },
        {
          "name": "幸存伤害",
          "eng_name": "Survivor Damage",
          "key": "2221260_2686060762",
          "description": [
            "在末日浩劫中存活的敌人在接下来 2 秒内受到来自你的伤害提高 100%[x]。对被妖术的敌人，此加成的持续时间延长 200%。"
          ]
        },
        {
          "name": "歼灭",
          "eng_name": "Annihilation",
          "key": "2221260_2686060810",
          "description": [
            "末日浩劫会投掷一枚至少拥有 20 层的毁灭炸弹，造成 33% 点伤害。地狱火技能命中敌人会生成最多 100 层，每层使炸弹的爆炸范围和伤害提高 40%[x]。"
          ]
        }
      ],
      "notes": "rank=15; active_bar=true"
    },
    {
      "name": "颠覆符印",
      "key": "warlock_sigil_of_subversion",
      "rank": 1,
      "role": "support",
      "description": [
        "冷却时间: 10 秒",
        "幸运一击几率: 20%",
        "创造一个持续 10 秒的亵渎仪式，对敌人施加妖术。",
        "在仪式中消灭 8 名敌人或恶魔会为仪式充能，使其生成持续 {val1} 秒的暗影小径。当你身处小径中时，周期性获得 1 层暗影形态。",
        "最多可同时存在 3 条暗影小径。"
      ],
      "damage_type": "",
      "tags": [
        "符印",
        "秘术",
        "深渊",
        "妖术",
        "暗影形态",
        "颠覆符印",
        "冷却时间"
      ],
      "selected_mods": [],
      "notes": "id=2218209; rank=1; active_bar=false"
    },
    {
      "name": "混沌符印",
      "key": "warlock_sigil_of_chaos",
      "rank": 15,
      "role": "main_damage_or_core",
      "description": [
        "冷却时间: 10 秒",
        "幸运一击几率: 35%",
        "创造一个持续 10 秒的毁灭仪式，身处仪式范围内会使你获得易爆状态。",
        "在仪式中消灭敌人或恶魔会为混沌地狱之火注入能量，提高敌人死亡时发生爆炸并造成 {val1}% 点伤害的几率。"
      ],
      "damage_type": "火焰伤害",
      "tags": [
        "符印",
        "秘术",
        "地狱火",
        "易爆",
        "混沌符印",
        "火焰",
        "伤害",
        "冷却时间"
      ],
      "selected_mods": [],
      "notes": "id=2218213; rank=15; active_bar=false"
    },
    {
      "name": "召唤符印",
      "key": "warlock_sigil_of_summons",
      "rank": 1,
      "role": "support",
      "description": [
        "冷却时间: 10 秒",
        "幸运一击几率: 35%",
        "创造一个持续 10 秒的约束仪式，延长你召唤物的持续时间。",
        "在仪式中消灭 8 名敌人或恶魔会为仪式充能，使其召唤一个恶魔，持续 20 秒，恶魔会攻击附近的敌人，每次命中造成 {val1}% 点伤害。",
        "你最多可以同时激活 3 个恶魔。"
      ],
      "damage_type": "物理伤害",
      "tags": [
        "符印",
        "恶魔学",
        "召唤",
        "低阶恶魔",
        "召唤符印",
        "物理",
        "伤害",
        "冷却时间"
      ],
      "selected_mods": [],
      "notes": "id=2221240; rank=1; active_bar=false"
    },
    {
      "name": "暗黑监牢",
      "key": "warlock_dark_prison",
      "rank": 15,
      "role": "defense",
      "description": [
        "冷却时间: 20 秒",
        "幸运一击几率: 20%",
        "生成一个持续 {val1} 秒的暗影图腾，用锁链束缚敌人，将他们困在区域内并防止其逃脱。"
      ],
      "damage_type": "",
      "tags": [
        "防御",
        "秘术",
        "深渊",
        "暗黑监牢",
        "冷却时间",
        "控制"
      ],
      "selected_mods": [],
      "notes": "id=2418214; rank=15; active_bar=false"
    }
  ],
  "passive_skills": [],
  "gear": [
    {
      "slot": "Helm",
      "item_type": "unique",
      "name": "堕狱传承",
      "required": true,
      "recommended_affixes": [
        "+12.0% 暴击几率",
        "+20.0% 幸运一击几率",
        "+20% 移动速度",
        "+2 至核心技能",
        "+[1,000 - 1,500] 生命上限"
      ],
      "affix_details": [
        {
          "key": "UBERUNIQUE_CritChance_HeirOfPerdition",
          "description": "+12.0% 暴击几率",
          "template": "+[{VALUE}*100|1%|] 暴击几率",
          "is_tempered": false
        },
        {
          "key": "UBERUNIQUE_Luck_HeirOfPerdition",
          "description": "+20.0% 幸运一击几率",
          "template": "+[{VALUE}*100|1%|] 幸运一击几率",
          "is_tempered": false
        },
        {
          "key": "UBERUNIQUE_Movement_Speed_HeirOfPerdition",
          "description": "+20% 移动速度",
          "template": "+[{VALUE}*100|%|] 移动速度",
          "is_tempered": false
        },
        {
          "key": "UBERUNIQUE_SkillRankBonus_Generic_Category_Core_HeirOfPerdition",
          "description": "+2 至核心技能",
          "template": "+[{VALUE2}|0|] 至核心技能",
          "is_tempered": false
        },
        {
          "key": "Tempered_Generic_LifeMax_Tier3",
          "description": "+[1,000 - 1,500] 生命上限",
          "template": "+[{VALUE}] 生命上限",
          "is_tempered": true
        }
      ],
      "sockets": [
        {
          "type": "gem",
          "key": "Item_Gem_Sapphire_09",
          "name": "Item_Gem_Sapphire_09",
          "description": []
        },
        {
          "type": "gem",
          "key": "Item_Gem_Sapphire_09",
          "name": "Item_Gem_Sapphire_09",
          "description": []
        }
      ]
    },
    {
      "slot": "ChestArmor",
      "item_type": "unique",
      "name": "血肉铭文甲壳",
      "required": true,
      "recommended_affixes": [
        "+[100 - 121] 点意力",
        "+[2,452 - 2,900] 生命上限",
        "+[524 - 630] 点火焰抗性",
        "+[1,963 - 2,450] 护甲值",
        "+[1,000 - 1,500] 生命上限"
      ],
      "affix_details": [
        {
          "key": "S04_CoreStat_Willpower",
          "description": "+[100 - 121] 点意力",
          "template": "[{VALUE}|~|] 点意力",
          "is_tempered": false
        },
        {
          "key": "S04_Life",
          "description": "+[2,452 - 2,900] 生命上限",
          "template": "+[{VALUE}] 生命上限",
          "is_tempered": false
        },
        {
          "key": "S04_Resistance_Single_Fire",
          "description": "+[524 - 630] 点火焰抗性",
          "template": "+[{VALUE2}] 点火焰抗性",
          "is_tempered": false
        },
        {
          "key": "X2_Armor_Greater",
          "description": "+[1,963 - 2,450] 护甲值",
          "template": "+[{VALUE}] 护甲值",
          "is_tempered": false
        },
        {
          "key": "Tempered_Generic_LifeMax_Tier3",
          "description": "+[1,000 - 1,500] 生命上限",
          "template": "+[{VALUE}] 生命上限",
          "is_tempered": true
        }
      ],
      "sockets": [
        {
          "type": "rune",
          "key": "Rune_Condition_CastRepeatSkill",
          "name": "策尔",
          "description": [
            "获得： 300 份供品",
            "施放 5 个技能后会陷入 3 秒的疲惫状态。"
          ],
          "value": 300,
          "quality": "Magic"
        },
        {
          "type": "rune",
          "key": "Rune_Effect_SummonSpiritWolf",
          "name": "塞赫",
          "description": [
            "需要： 100 份供品",
            "冷却时间： 1 秒",
            "召唤狼灵同伴攻击敌人，持续 8 秒。 （溢出：召唤多只狼灵）"
          ],
          "value": 100,
          "quality": "Magic"
        }
      ]
    },
    {
      "slot": "Gloves",
      "item_type": "unique",
      "name": "灭世者之手",
      "required": true,
      "recommended_affixes": [
        "+[3.5 - 5.0]% 意力",
        "x[12 - 20]% 全伤害增倍",
        "x[26 - 50]% 暴击伤害增倍",
        "+[6.5 - 8.5]% 暴击几率",
        "+[7.0 - 10.0]% 每层压制伤害"
      ],
      "affix_details": [
        {
          "key": "X2_Transfiguration_CoreStat_WillpowerPercent",
          "description": "+[3.5 - 5.0]% 意力",
          "template": "+[{vALUE2}*100|1%|] 意力",
          "is_tempered": false
        },
        {
          "key": "X2_Damage_All_Greater",
          "description": "x[12 - 20]% 全伤害增倍",
          "template": "x[{VALUE}*100|%|] 全伤害增倍",
          "is_tempered": false
        },
        {
          "key": "X2_CritDamage_Greater",
          "description": "x[26 - 50]% 暴击伤害增倍",
          "template": "x[{VALUE}*100|%|] 暴击伤害增倍",
          "is_tempered": false
        },
        {
          "key": "S04_CritChance",
          "description": "+[6.5 - 8.5]% 暴击几率",
          "template": "+[{VALUE}*100|1%|] 暴击几率",
          "is_tempered": false
        },
        {
          "key": "Tempered_Generic_Overpower_DamagePerStack_Tier3",
          "description": "+[7.0 - 10.0]% 每层压制伤害",
          "template": "+[{VALUE}*100|1%|] 每层压制伤害",
          "is_tempered": true
        }
      ],
      "sockets": []
    },
    {
      "slot": "Legs",
      "item_type": "legendary",
      "name": "主宰的威能",
      "required": true,
      "recommended_affixes": [
        "+[100 - 121] 点意力",
        "+[2,452 - 2,900] 生命上限",
        "+[3 - 4] 愤怒回复",
        "+[1,963 - 2,450] 护甲值",
        "+[1,000 - 1,500] 生命上限"
      ],
      "affix_details": [
        {
          "key": "S04_CoreStat_Willpower",
          "description": "+[100 - 121] 点意力",
          "template": "[{VALUE}|~|] 点意力",
          "is_tempered": false
        },
        {
          "key": "S04_Life",
          "description": "+[2,452 - 2,900] 生命上限",
          "template": "+[{VALUE}] 生命上限",
          "is_tempered": false
        },
        {
          "key": "S04_Resource_Per_Second_Wrath",
          "description": "+[3 - 4] 愤怒回复",
          "template": "[{VALUE2}|~|] 愤怒回复",
          "is_tempered": false
        },
        {
          "key": "X2_Armor_Greater",
          "description": "+[1,963 - 2,450] 护甲值",
          "template": "+[{VALUE}] 护甲值",
          "is_tempered": false
        },
        {
          "key": "Tempered_Generic_LifeMax_Tier3",
          "description": "+[1,000 - 1,500] 生命上限",
          "template": "+[{VALUE}] 生命上限",
          "is_tempered": true
        }
      ],
      "sockets": [
        {
          "type": "rune",
          "key": "Rune_Condition_Summons",
          "name": "纳古",
          "description": [
            "获得： 100 份供品",
            "维持 1 个激活召唤物的时间至少达到 5 秒，每有一个召唤物都可获得一份供品，最多对 5 个召唤物生效。"
          ],
          "value": 100,
          "quality": "Rare"
        },
        {
          "type": "rune",
          "key": "Rune_Effect_Warlock_ChainPrison",
          "name": "普瑞德",
          "description": [
            "需要： 250 份供品",
            "冷却时间： 3 秒",
            "施放术士的暗黑监牢技能，将敌人束缚在区域内 3 秒。 （溢出：延长暗黑监牢持续时间）"
          ],
          "value": 250,
          "quality": "Magic"
        }
      ]
    },
    {
      "slot": "Boots",
      "item_type": "legendary",
      "name": "不死威能",
      "required": true,
      "recommended_affixes": [
        "+[100 - 121] 点意力",
        "+[2,452 - 2,900] 生命上限",
        "+[1 - 2] 至地狱火技能",
        "+[20 - 24]% 移动速度",
        "+[30.0 - 50.0]% 符印的持续时间"
      ],
      "affix_details": [
        {
          "key": "S04_CoreStat_Willpower",
          "description": "+[100 - 121] 点意力",
          "template": "[{VALUE}|~|] 点意力",
          "is_tempered": false
        },
        {
          "key": "S04_Life",
          "description": "+[2,452 - 2,900] 生命上限",
          "template": "+[{VALUE}] 生命上限",
          "is_tempered": false
        },
        {
          "key": "X2_SkillRankBonus_Warlock_Category_Hellfire",
          "description": "+[1 - 2] 至地狱火技能",
          "template": "+[{VALUE2}|0|] 至地狱火技能",
          "is_tempered": false
        },
        {
          "key": "S04_Movement_Speed",
          "description": "+[20 - 24]% 移动速度",
          "template": "+[{VALUE}*100|%|] 移动速度",
          "is_tempered": false
        },
        {
          "key": "Tempered_Duration_Tag_War_Sigil_Tier3",
          "description": "+[30.0 - 50.0]% 符印的持续时间",
          "template": "+[{VALUE2}*100|1%|] 符印的持续时间",
          "is_tempered": true
        }
      ],
      "sockets": []
    },
    {
      "slot": "Axe2H",
      "item_type": "legendary",
      "name": "焚炉的威能",
      "required": true,
      "recommended_affixes": [
        "+[1,831 - 2,200] 生命上限",
        "x[6 - 10]% 全伤害增倍",
        "+[94 - 157] 武器伤害",
        "+[789 - 948] 击中回复生命",
        "+[2.5 - 5.0]% 暴击几率"
      ],
      "affix_details": [
        {
          "key": "X2_Life_Greater",
          "description": "+[1,831 - 2,200] 生命上限",
          "template": "+[{VALUE}] 生命上限",
          "is_tempered": false
        },
        {
          "key": "S04_Damage_All",
          "description": "x[6 - 10]% 全伤害增倍",
          "template": "x[{VALUE}*100|%|] 全伤害增倍",
          "is_tempered": false
        },
        {
          "key": "X2_Fast_Weapon_Damage_2HBow",
          "description": "+[94 - 157] 武器伤害",
          "template": "+[{VALUE}] 武器伤害",
          "is_tempered": false
        },
        {
          "key": "X2_LifePerHit_2H",
          "description": "+[789 - 948] 击中回复生命",
          "template": "+[{vALUE}] 击中回复生命",
          "is_tempered": false
        },
        {
          "key": "Tempered_Generic_CritChance_Tier3",
          "description": "+[2.5 - 5.0]% 暴击几率",
          "template": "+[{VALUE}*100|1%|] 暴击几率",
          "is_tempered": true
        }
      ],
      "sockets": [
        {
          "type": "gem",
          "key": "Item_Gem_Ruby_09",
          "name": "Item_Gem_Ruby_09",
          "description": []
        },
        {
          "type": "gem",
          "key": "Item_Gem_Ruby_09",
          "name": "Item_Gem_Ruby_09",
          "description": []
        }
      ]
    },
    {
      "slot": "Amulet",
      "item_type": "legendary",
      "name": "焦灼之威能",
      "required": true,
      "recommended_affixes": [
        "+[150 - 180] 点意力",
        "x[12 - 20]% 全伤害增倍",
        "x[26 - 50]% 暴击伤害增倍",
        "x[14 - 24]% 火焰 伤害增倍",
        "+[7.0 - 10.0]% 每层压制伤害"
      ],
      "affix_details": [
        {
          "key": "X2_CoreStat_Willpower_Greater",
          "description": "+[150 - 180] 点意力",
          "template": "[{VALUE}|~|] 点意力",
          "is_tempered": false
        },
        {
          "key": "X2_Damage_All_Greater",
          "description": "x[12 - 20]% 全伤害增倍",
          "template": "x[{VALUE}*100|%|] 全伤害增倍",
          "is_tempered": false
        },
        {
          "key": "X2_CritDamage_Greater",
          "description": "x[26 - 50]% 暴击伤害增倍",
          "template": "x[{VALUE}*100|%|] 暴击伤害增倍",
          "is_tempered": false
        },
        {
          "key": "X2_DamageType_Fire_Greater",
          "description": "x[14 - 24]% 火焰 伤害增倍",
          "template": "x[{VALUE2}*100|%|] 火焰 伤害增倍",
          "is_tempered": false
        },
        {
          "key": "Tempered_Generic_Overpower_DamagePerStack_Tier3",
          "description": "+[7.0 - 10.0]% 每层压制伤害",
          "template": "+[{VALUE}*100|1%|] 每层压制伤害",
          "is_tempered": true
        }
      ],
      "sockets": [
        {
          "type": "gem",
          "key": "Item_Gem_Ruby_09",
          "name": "Item_Gem_Ruby_09",
          "description": []
        }
      ]
    },
    {
      "slot": "Ring",
      "item_type": "legendary",
      "name": "暴烈拳师的威能",
      "required": true,
      "recommended_affixes": [
        "x[7 - 10]% 火焰 伤害增倍",
        "+[3.5 - 5.0]% 暴击几率",
        "x[13 - 25]% 暴击伤害增倍",
        "x[8 - 14]% 易伤伤害增倍",
        "+[7.0 - 10.0]% 每层压制伤害"
      ],
      "affix_details": [
        {
          "key": "X2_DamageType_Fire",
          "description": "x[7 - 10]% 火焰 伤害增倍",
          "template": "x[{VALUE2}*100|%|] 火焰 伤害增倍",
          "is_tempered": false
        },
        {
          "key": "S04_CritChanceJewelry",
          "description": "+[3.5 - 5.0]% 暴击几率",
          "template": "+[{VALUE}*100|1%|] 暴击几率",
          "is_tempered": false
        },
        {
          "key": "S04_CritDamage",
          "description": "x[13 - 25]% 暴击伤害增倍",
          "template": "x[{VALUE}*100|%|] 暴击伤害增倍",
          "is_tempered": false
        },
        {
          "key": "S04_Damage_to_Vulnerable",
          "description": "x[8 - 14]% 易伤伤害增倍",
          "template": "x[{VALUE}*100|%|] 易伤伤害增倍",
          "is_tempered": false
        },
        {
          "key": "Tempered_Generic_Overpower_DamagePerStack_Tier3",
          "description": "+[7.0 - 10.0]% 每层压制伤害",
          "template": "+[{VALUE}*100|1%|] 每层压制伤害",
          "is_tempered": true
        }
      ],
      "sockets": [
        {
          "type": "gem",
          "key": "Item_Gem_Diamond_09",
          "name": "Item_Gem_Diamond_09",
          "description": []
        }
      ]
    },
    {
      "slot": "Ring",
      "item_type": "legendary",
      "name": "引燃之威能",
      "required": true,
      "recommended_affixes": [
        "+[100 - 121] 点意力",
        "x[7 - 10]% 火焰 伤害增倍",
        "+[3.5 - 5.0]% 暴击几率",
        "x[13 - 25]% 暴击伤害增倍",
        "+[7.0 - 10.0]% 每层压制伤害"
      ],
      "affix_details": [
        {
          "key": "S04_CoreStat_Willpower",
          "description": "+[100 - 121] 点意力",
          "template": "[{VALUE}|~|] 点意力",
          "is_tempered": false
        },
        {
          "key": "X2_DamageType_Fire",
          "description": "x[7 - 10]% 火焰 伤害增倍",
          "template": "x[{VALUE2}*100|%|] 火焰 伤害增倍",
          "is_tempered": false
        },
        {
          "key": "S04_CritChanceJewelry",
          "description": "+[3.5 - 5.0]% 暴击几率",
          "template": "+[{VALUE}*100|1%|] 暴击几率",
          "is_tempered": false
        },
        {
          "key": "S04_CritDamage",
          "description": "x[13 - 25]% 暴击伤害增倍",
          "template": "x[{VALUE}*100|%|] 暴击伤害增倍",
          "is_tempered": false
        },
        {
          "key": "Tempered_Generic_Overpower_DamagePerStack_Tier3",
          "description": "+[7.0 - 10.0]% 每层压制伤害",
          "template": "+[{VALUE}*100|1%|] 每层压制伤害",
          "is_tempered": true
        }
      ],
      "sockets": [
        {
          "type": "gem",
          "key": "Item_Gem_Diamond_09",
          "name": "Item_Gem_Diamond_09",
          "description": []
        }
      ]
    }
  ],
  "aspects": [
    {
      "name": "主宰的威能",
      "key": "Affix_legendary_generic_117",
      "slot": "Legs",
      "priority": "high",
      "description": "你获得 [100 - 150]%[+] 总护甲值，但闪避的冷却时间增加 100%。",
      "aspect_type": "Defensive",
      "filters": [
        "FILTER_Build_All_Generic",
        "FILTER_Legendary_Defensive",
        "Search_Evade",
        "Search_Armor",
        "Search_Cooldown"
      ],
      "notes": "source=variant gear"
    },
    {
      "name": "不死威能",
      "key": "Affix_legendary_generic_119",
      "slot": "Boots",
      "priority": "high",
      "description": "施放技能为你恢复 [2.0 - 3.0]% 生命上限。在受伤状态时，此加成翻倍。",
      "aspect_type": "Utility",
      "filters": [
        "FILTER_Legendary_Utility",
        "HoradricCube_Legendary_Utility_Mobility",
        "Search_Healing",
        "Search_Life",
        "Raid_Legendaries",
        "Keyword_Injured"
      ],
      "notes": "source=variant gear"
    },
    {
      "name": "焚炉的威能",
      "key": "Affix_legendary_fireUser_001_x2",
      "slot": "Axe2H",
      "priority": "high",
      "description": "你拥有 4 层或更多压制时，你施放的火焰技能伤害提高 [70 - 100]%[x]。",
      "aspect_type": "Offensive",
      "filters": [
        "FILTER_Legendary_Offensive",
        "FILTER_Build_Sorc_Fire",
        "Skill_Fire",
        "Search_Damage",
        "Archetype_Sorcerer_Pyromancy_Signature",
        "Keyword_Overpower",
        "Search_Fire",
        "Skill_Hellfire"
      ],
      "notes": "source=variant gear"
    },
    {
      "name": "焦灼之威能",
      "key": "Affix_legendary_warlock_010_x2",
      "slot": "Amulet",
      "priority": "high",
      "description": "你的地狱火技能造成的伤害提高，数值相当于你火焰抗性伤害减免的 [60 - 80]%。",
      "aspect_type": "Offensive",
      "filters": [
        "FILTER_Legendary_Offensive",
        "Search_Damage",
        "Search_Resistance",
        "Skill_Hellfire",
        "Archetype_Warlock_Vanguard_Signature"
      ],
      "notes": "source=variant gear"
    },
    {
      "name": "暴烈拳师的威能",
      "key": "Affix_legendary_generic_127",
      "slot": "Ring",
      "priority": "high",
      "description": "施放终极技能使你的伤害提高 [35 - 55]%[x]，持续 8 秒。终极技能级别额外提高 2 级。",
      "aspect_type": "Offensive",
      "filters": [
        "Search_Copy_Ultimate",
        "Search_Damage",
        "Search_Cooldown",
        "FILTER_Legendary_Offensive"
      ],
      "notes": "source=variant gear"
    },
    {
      "name": "引燃之威能",
      "key": "Affix_legendary_warlock_014_x2",
      "slot": "Ring",
      "priority": "high",
      "description": "受易爆强化的技能额外造成 40%[x] 的伤害，并且施放受强化的技能时，你有 [24.0 - 40.0]% 几率保留易爆效果。",
      "aspect_type": "Offensive",
      "filters": [
        "FILTER_Legendary_Offensive",
        "Keyword_Volatility",
        "Search_Damage",
        "Archetype_Warlock_Vanguard_Signature"
      ],
      "notes": "source=variant gear"
    }
  ],
  "uniques": [
    {
      "name": "堕狱传承",
      "key": "Helm_Unique_Generic_004",
      "slot": "Helm",
      "required": true,
      "description": [
        "+12.0% 暴击几率",
        "+20.0% 幸运一击几率",
        "+20% 移动速度",
        "+2 至核心技能",
        "屈服于憎恨并获得圣母的宠爱，从而使你造成的伤害提高 80%[x]。消灭敌人可以从附近盟友身上短暂窃取圣母的宠爱效果。"
      ],
      "flavor": "虚假的先知会披上绵羊的伪装，但恶狼的臭气还留在他们身上。你们务必小心提防，审视其言行便知其真实模样。要知道，好树从来结不出恶果，从荆棘上也尝不出甜香。",
      "damage_details": [],
      "is_mythic": true,
      "notes": "item_power=900; source=variant gear"
    },
    {
      "name": "血肉铭文甲壳",
      "key": "Chest_Unique_Warlock_001",
      "slot": "ChestArmor",
      "required": true,
      "description": [
        "符印技能造成的伤害提高 [70 - 90]%[x]。激活的符印每秒获得 1 个击杀数，未使用的击杀数将在符印失效时保留。"
      ],
      "flavor": "“……我们的仪祭绝非以墨水书写，而是以鲜血浇灌；绝非铭刻于顽石，而是烙印在活人的血肉之上……”——《塔菲亚》13:6",
      "damage_details": [],
      "is_mythic": false,
      "notes": "item_power=900; source=variant gear"
    },
    {
      "name": "灭世者之手",
      "key": "Gloves_Unique_Warlock_004",
      "slot": "Gloves",
      "required": true,
      "description": [
        "当在混沌符印中施放时，末日浩劫造成的伤害最高提高 [340 - 400]%[x]，具体取决于该符印记录的击杀数。 末日浩劫现在也视为符印技能。"
      ],
      "flavor": "“对于那些以毁灭为本性的恶魔而言，终点究竟在何方？当周遭的一切皆化为废墟，我相信它们最后的毁灭之举，便是将自己撕碎。”——迪卡德·凯恩",
      "damage_details": [],
      "is_mythic": false,
      "notes": "item_power=900; source=variant gear"
    }
  ],
  "affix_priorities": [
    {
      "category": "offense",
      "priority_order": [
        "+12.0% 暴击几率",
        "+2 至核心技能",
        "x[12 - 20]% 全伤害增倍",
        "x[26 - 50]% 暴击伤害增倍",
        "+[6.5 - 8.5]% 暴击几率",
        "+[7.0 - 10.0]% 每层压制伤害",
        "+[1 - 2] 至地狱火技能",
        "x[6 - 10]% 全伤害增倍",
        "+[94 - 157] 武器伤害",
        "+[2.5 - 5.0]% 暴击几率",
        "x[14 - 24]% 火焰 伤害增倍",
        "x[7 - 10]% 火焰 伤害增倍",
        "+[3.5 - 5.0]% 暴击几率",
        "x[13 - 25]% 暴击伤害增倍",
        "x[8 - 14]% 易伤伤害增倍"
      ],
      "affix_details": [
        {
          "key": "UBERUNIQUE_CritChance_HeirOfPerdition",
          "description": "+12.0% 暴击几率",
          "template": "+[{VALUE}*100|1%|] 暴击几率",
          "is_tempered": false
        },
        {
          "key": "UBERUNIQUE_SkillRankBonus_Generic_Category_Core_HeirOfPerdition",
          "description": "+2 至核心技能",
          "template": "+[{VALUE2}|0|] 至核心技能",
          "is_tempered": false
        },
        {
          "key": "X2_Damage_All_Greater",
          "description": "x[12 - 20]% 全伤害增倍",
          "template": "x[{VALUE}*100|%|] 全伤害增倍",
          "is_tempered": false
        },
        {
          "key": "X2_CritDamage_Greater",
          "description": "x[26 - 50]% 暴击伤害增倍",
          "template": "x[{VALUE}*100|%|] 暴击伤害增倍",
          "is_tempered": false
        },
        {
          "key": "S04_CritChance",
          "description": "+[6.5 - 8.5]% 暴击几率",
          "template": "+[{VALUE}*100|1%|] 暴击几率",
          "is_tempered": false
        },
        {
          "key": "Tempered_Generic_Overpower_DamagePerStack_Tier3",
          "description": "+[7.0 - 10.0]% 每层压制伤害",
          "template": "+[{VALUE}*100|1%|] 每层压制伤害",
          "is_tempered": true
        },
        {
          "key": "X2_SkillRankBonus_Warlock_Category_Hellfire",
          "description": "+[1 - 2] 至地狱火技能",
          "template": "+[{VALUE2}|0|] 至地狱火技能",
          "is_tempered": false
        },
        {
          "key": "S04_Damage_All",
          "description": "x[6 - 10]% 全伤害增倍",
          "template": "x[{VALUE}*100|%|] 全伤害增倍",
          "is_tempered": false
        },
        {
          "key": "X2_Fast_Weapon_Damage_2HBow",
          "description": "+[94 - 157] 武器伤害",
          "template": "+[{VALUE}] 武器伤害",
          "is_tempered": false
        },
        {
          "key": "Tempered_Generic_CritChance_Tier3",
          "description": "+[2.5 - 5.0]% 暴击几率",
          "template": "+[{VALUE}*100|1%|] 暴击几率",
          "is_tempered": true
        },
        {
          "key": "X2_DamageType_Fire_Greater",
          "description": "x[14 - 24]% 火焰 伤害增倍",
          "template": "x[{VALUE2}*100|%|] 火焰 伤害增倍",
          "is_tempered": false
        },
        {
          "key": "X2_DamageType_Fire",
          "description": "x[7 - 10]% 火焰 伤害增倍",
          "template": "x[{VALUE2}*100|%|] 火焰 伤害增倍",
          "is_tempered": false
        },
        {
          "key": "S04_CritChanceJewelry",
          "description": "+[3.5 - 5.0]% 暴击几率",
          "template": "+[{VALUE}*100|1%|] 暴击几率",
          "is_tempered": false
        },
        {
          "key": "S04_CritDamage",
          "description": "x[13 - 25]% 暴击伤害增倍",
          "template": "x[{VALUE}*100|%|] 暴击伤害增倍",
          "is_tempered": false
        },
        {
          "key": "S04_Damage_to_Vulnerable",
          "description": "x[8 - 14]% 易伤伤害增倍",
          "template": "x[{VALUE}*100|%|] 易伤伤害增倍",
          "is_tempered": false
        }
      ],
      "notes": "Auto-collected from equipped gear affixes. Order reflects first appearance, not a verified priority ranking."
    },
    {
      "category": "defense",
      "priority_order": [
        "+[1,000 - 1,500] 生命上限",
        "+[2,452 - 2,900] 生命上限",
        "+[524 - 630] 点火焰抗性",
        "+[1,963 - 2,450] 护甲值",
        "+[1,831 - 2,200] 生命上限",
        "+[789 - 948] 击中回复生命"
      ],
      "affix_details": [
        {
          "key": "Tempered_Generic_LifeMax_Tier3",
          "description": "+[1,000 - 1,500] 生命上限",
          "template": "+[{VALUE}] 生命上限",
          "is_tempered": true
        },
        {
          "key": "S04_Life",
          "description": "+[2,452 - 2,900] 生命上限",
          "template": "+[{VALUE}] 生命上限",
          "is_tempered": false
        },
        {
          "key": "S04_Resistance_Single_Fire",
          "description": "+[524 - 630] 点火焰抗性",
          "template": "+[{VALUE2}] 点火焰抗性",
          "is_tempered": false
        },
        {
          "key": "X2_Armor_Greater",
          "description": "+[1,963 - 2,450] 护甲值",
          "template": "+[{VALUE}] 护甲值",
          "is_tempered": false
        },
        {
          "key": "X2_Life_Greater",
          "description": "+[1,831 - 2,200] 生命上限",
          "template": "+[{VALUE}] 生命上限",
          "is_tempered": false
        },
        {
          "key": "X2_LifePerHit_2H",
          "description": "+[789 - 948] 击中回复生命",
          "template": "+[{vALUE}] 击中回复生命",
          "is_tempered": false
        }
      ],
      "notes": "Auto-collected from equipped gear affixes. Order reflects first appearance, not a verified priority ranking."
    },
    {
      "category": "utility",
      "priority_order": [
        "+20.0% 幸运一击几率",
        "+20% 移动速度",
        "+[100 - 121] 点意力",
        "+[3.5 - 5.0]% 意力",
        "+[3 - 4] 愤怒回复",
        "+[20 - 24]% 移动速度",
        "+[30.0 - 50.0]% 符印的持续时间",
        "+[150 - 180] 点意力"
      ],
      "affix_details": [
        {
          "key": "UBERUNIQUE_Luck_HeirOfPerdition",
          "description": "+20.0% 幸运一击几率",
          "template": "+[{VALUE}*100|1%|] 幸运一击几率",
          "is_tempered": false
        },
        {
          "key": "UBERUNIQUE_Movement_Speed_HeirOfPerdition",
          "description": "+20% 移动速度",
          "template": "+[{VALUE}*100|%|] 移动速度",
          "is_tempered": false
        },
        {
          "key": "S04_CoreStat_Willpower",
          "description": "+[100 - 121] 点意力",
          "template": "[{VALUE}|~|] 点意力",
          "is_tempered": false
        },
        {
          "key": "X2_Transfiguration_CoreStat_WillpowerPercent",
          "description": "+[3.5 - 5.0]% 意力",
          "template": "+[{vALUE2}*100|1%|] 意力",
          "is_tempered": false
        },
        {
          "key": "S04_Resource_Per_Second_Wrath",
          "description": "+[3 - 4] 愤怒回复",
          "template": "[{VALUE2}|~|] 愤怒回复",
          "is_tempered": false
        },
        {
          "key": "S04_Movement_Speed",
          "description": "+[20 - 24]% 移动速度",
          "template": "+[{VALUE}*100|%|] 移动速度",
          "is_tempered": false
        },
        {
          "key": "Tempered_Duration_Tag_War_Sigil_Tier3",
          "description": "+[30.0 - 50.0]% 符印的持续时间",
          "template": "+[{VALUE2}*100|1%|] 符印的持续时间",
          "is_tempered": true
        },
        {
          "key": "X2_CoreStat_Willpower_Greater",
          "description": "+[150 - 180] 点意力",
          "template": "[{VALUE}|~|] 点意力",
          "is_tempered": false
        }
      ],
      "notes": "Auto-collected from equipped gear affixes. Order reflects first appearance, not a verified priority ranking."
    }
  ],
  "paragon_boards": [
    {
      "name": "开始",
      "key": "Paragon_Warlock_00",
      "purpose": "Auto-converted from board key Paragon_Warlock_00.",
      "important_nodes": [
        "至尊",
        "支配",
        "韧性",
        "扭曲"
      ],
      "important_node_details": [
        {
          "name": "至尊",
          "key": "Generic_Rare_075",
          "description": "+10% 伤害 4.0% 生命上限",
          "tags": [
            "Search_Damage",
            "Search_Life"
          ]
        },
        {
          "name": "支配",
          "key": "Warlock_Rare_004",
          "description": "+15.0% 对精英的伤害 +10 点意力",
          "tags": [
            "Search_Elite",
            "Search_Damage",
            "Search_Willpower"
          ]
        },
        {
          "name": "韧性",
          "key": "Generic_Rare_001",
          "description": "+3.0% 全元素抗性 4.0% 生命上限",
          "tags": [
            "Search_Resistance",
            "Search_Life",
            "Search_NonPhysical"
          ]
        },
        {
          "name": "扭曲",
          "key": "Warlock_Rare_003",
          "description": "+10% 伤害 +10 点意力",
          "tags": [
            "Search_Damage",
            "Search_Willpower"
          ]
        }
      ],
      "selected_node_count": 39
    },
    {
      "name": "炎灼",
      "key": "Paragon_Warlock_04",
      "purpose": "Auto-converted from board key Paragon_Warlock_04.",
      "important_nodes": [
        "焦灼血肉",
        "炽焰",
        "燃烧",
        "炽热护盾",
        "炎灼",
        "炼狱防护",
        "炎火噬灭"
      ],
      "important_node_details": [
        {
          "name": "焦灼血肉",
          "key": "Warlock_Rare_026",
          "description": "4.0% 生命上限 +2.0% 总护甲",
          "tags": [
            "Search_Life",
            "Search_Armor"
          ]
        },
        {
          "name": "炽焰",
          "key": "Warlock_Rare_028",
          "description": "+10% 伤害 +10 点意力",
          "tags": [
            "Search_Damage",
            "Search_Willpower"
          ]
        },
        {
          "name": "燃烧",
          "key": "Warlock_Rare_027",
          "description": "+15.0% 地狱火伤害 +10 点意力",
          "tags": [
            "Skill_Hellfire",
            "Search_Willpower"
          ]
        },
        {
          "name": "炽热护盾",
          "key": "Warlock_Rare_025",
          "description": "+10% 伤害 +3.0% 全元素抗性",
          "tags": [
            "Search_Damage",
            "Search_Resistance"
          ]
        },
        {
          "name": "炎灼",
          "key": "Warlock_Legendary_004",
          "description": "地狱火技能对450%[x]健康敌人造成的伤害提高 。 术士",
          "tags": [
            "Search_Damage",
            "Keyword_Healthy"
          ]
        },
        {
          "name": "炼狱防护",
          "key": "Warlock_Rare_024",
          "description": "+3.0% 全元素抗性 +2.0% 总护甲",
          "tags": [
            "Search_Resistance",
            "Search_Willpower"
          ]
        },
        {
          "name": "炎火噬灭",
          "key": "Warlock_Rare_023",
          "description": "4.0% 生命上限 +6.0% 受到的治疗",
          "tags": [
            "Search_Life",
            "Search_Healing"
          ]
        }
      ],
      "selected_node_count": 72
    },
    {
      "name": "强力妖术",
      "key": "Paragon_Warlock_06",
      "purpose": "Auto-converted from board key Paragon_Warlock_06.",
      "important_nodes": [
        "治愈守护",
        "妖术守卫",
        "死亡印记",
        "强力妖术"
      ],
      "important_node_details": [
        {
          "name": "治愈守护",
          "key": "Warlock_Rare_038",
          "description": "4.0% 生命上限 +6.0% 受到的治疗",
          "tags": [
            "Search_Life",
            "Search_Healing"
          ]
        },
        {
          "name": "妖术守卫",
          "key": "Warlock_Rare_037",
          "description": "4.0% 生命上限 +2.0% 总护甲",
          "tags": [
            "Search_Life",
            "Search_Armor"
          ]
        },
        {
          "name": "死亡印记",
          "key": "Warlock_Rare_040",
          "description": "+10% 伤害 +13% 易伤伤害",
          "tags": [
            "Search_Damage",
            "Search_Willpower"
          ]
        },
        {
          "name": "强力妖术",
          "key": "Warlock_Legendary_006",
          "description": "对敌人施加妖术、易伤或虚弱会永久降低其对你造成的伤害 25%，且其受到来自你的伤害提高 75%[x]。 术士",
          "tags": [
            "Search_Damage",
            "Skill_Abyss",
            "Keyword_Hex",
            "Keyword_Weaken"
          ]
        }
      ],
      "selected_node_count": 54
    },
    {
      "name": "仪祭",
      "key": "Paragon_Warlock_07",
      "purpose": "Auto-converted from board key Paragon_Warlock_07.",
      "important_nodes": [
        "黑暗印记",
        "堕落",
        "仪祭",
        "蓄势之怒",
        "蒙难之地",
        "恶性循环",
        "初露锋芒"
      ],
      "important_node_details": [
        {
          "name": "黑暗印记",
          "key": "Warlock_Rare_044",
          "description": "4.0% 生命上限 +3.0% 总护甲",
          "tags": [
            "Search_Life",
            "Search_Armor"
          ]
        },
        {
          "name": "堕落",
          "key": "Warlock_Rare_046",
          "description": "+10% 伤害 4.0% 生命上限",
          "tags": [
            "Search_Life",
            "Search_Damage"
          ]
        },
        {
          "name": "仪祭",
          "key": "Warlock_Legendary_007",
          "description": "施放符印技能后，你造成的伤害提高 90%[x]，持续 15 秒。在符印范围内死亡的高阶恶魔现在计作 10 次击杀。 术士",
          "tags": []
        },
        {
          "name": "蓄势之怒",
          "key": "Warlock_Rare_045",
          "description": "+17.5% 妖术伤害加成 +15% 暴击伤害",
          "tags": [
            "Keyword_Hex",
            "Search_Damage"
          ]
        },
        {
          "name": "蒙难之地",
          "key": "Warlock_Rare_043",
          "description": "+3.0% 总护甲 +3.0% 全元素抗性",
          "tags": [
            "Search_Armor",
            "Search_Resistance"
          ]
        },
        {
          "name": "恶性循环",
          "key": "Warlock_Rare_042",
          "description": "+2.0% 每层压制伤害 +10 点意力",
          "tags": [
            "Keyword_Overpower",
            "Search_Damage",
            "Search_Willpower"
          ]
        },
        {
          "name": "初露锋芒",
          "key": "Warlock_Rare_041",
          "description": "+17.5% 易爆伤害加成 +10 点意力",
          "tags": [
            "Search_Willpower",
            "Keyword_Volatility",
            "Search_Damage"
          ]
        }
      ],
      "selected_node_count": 90
    },
    {
      "name": "混沌",
      "key": "Paragon_Warlock_08",
      "purpose": "Auto-converted from board key Paragon_Warlock_08.",
      "important_nodes": [
        "电荷过载",
        "变异",
        "控制",
        "熵能坍缩",
        "混沌"
      ],
      "important_node_details": [
        {
          "name": "电荷过载",
          "key": "Warlock_Rare_048",
          "description": "+2.0% 每层压制伤害 +10 点意力",
          "tags": [
            "Keyword_Overpower",
            "Search_Damage",
            "Search_Willpower"
          ]
        },
        {
          "name": "变异",
          "key": "Warlock_Rare_049",
          "description": "+3.0% 总护甲 +3.0% 全元素抗性",
          "tags": [
            "Search_Armor",
            "Search_Resistance"
          ]
        },
        {
          "name": "控制",
          "key": "Warlock_Rare_050",
          "description": "4.0% 生命上限 +4 愤怒上限",
          "tags": [
            "Search_Life",
            "Search_Armor"
          ]
        },
        {
          "name": "熵能坍缩",
          "key": "Warlock_Rare_051",
          "description": "+2.5% 幸运一击几率 +15% 暴击伤害",
          "tags": [
            "Search_LuckyHit",
            "Search_Critical"
          ]
        },
        {
          "name": "混沌",
          "key": "Warlock_Legendary_008",
          "description": "当你拥有压制时，你的秘术技能造成的伤害提高 100%[x]，但当你失去一层时，你要么获得 2 层要么额外失去 1 层。 术士",
          "tags": [
            "Search_Damage",
            "Skill_Occult",
            "Keyword_Overpower"
          ]
        }
      ],
      "selected_node_count": 70
    }
  ],
  "glyphs": [
    {
      "name": "地狱熔炉",
      "key": "ParagonGlyph_116",
      "board": "开始",
      "priority": "high",
      "description": "每购买辐射范围内 5 点意力，你的地狱火技能造成的伤害提高 +{val1}%。",
      "bonus": "被易爆强化的技能额外造成 x15% 伤害。",
      "legendary_bonus": "地狱火技能造成的伤害提高 15.4%。",
      "threshold_requirements": [
        {
          "value": 25,
          "name": "Intelligence"
        }
      ],
      "notes": "socket=6_10_Generic_Socket; rank=100"
    },
    {
      "name": "解禁",
      "key": "ParagonGlyph_115",
      "board": "炎灼",
      "priority": "high",
      "description": "给予辐射范围内所有魔法节点 +{val1}% 加成。",
      "bonus": "消耗 50 点愤怒后，你造成的伤害提高 x10%，且愤怒回复速度提高 25%，持续 3 秒。",
      "legendary_bonus": "伤害提高 15.4%。",
      "threshold_requirements": [
        {
          "value": 25,
          "name": "Intelligence"
        }
      ],
      "notes": "socket=8_10_Generic_Socket; rank=100"
    },
    {
      "name": "邪视",
      "key": "ParagonGlyph_120",
      "board": "强力妖术",
      "priority": "high",
      "description": "每购买辐射范围内 5 点意力，你对易伤目标造成的伤害提高 +{val1}%。",
      "bonus": "对易伤目标造成伤害会使你造成的伤害提高 x3%，持续 20 秒，最高叠加至 x18%。",
      "legendary_bonus": "对易伤目标造成的伤害提高 15.4%。",
      "threshold_requirements": [
        {
          "value": 40,
          "name": "Willpower"
        }
      ],
      "notes": "socket=12_10_Generic_Socket; rank=100"
    },
    {
      "name": "秘术师",
      "key": "ParagonGlyph_114",
      "board": "仪祭",
      "priority": "high",
      "description": "每购买辐射范围内 5 点意力，你的秘术技能造成的伤害提高 +{val1}%。",
      "bonus": "对敌人的压制打击会使其受到来自你的伤害提高 x12%，持续 10 秒。",
      "legendary_bonus": "秘术技能造成的伤害提高 15.4%。",
      "threshold_requirements": [
        {
          "value": 25,
          "name": "Intelligence"
        }
      ],
      "notes": "socket=15_5_Generic_Socket; rank=100"
    },
    {
      "name": "强能",
      "key": "ParagonGlyph_129",
      "board": "混沌",
      "priority": "high",
      "description": "每购买辐射范围内 5 点意力，你每层造成的压制伤害提高 +{val1}%。",
      "bonus": "当你拥有压制时，你的秘术技能造成的伤害提高 [SF_0 * 100 |%x|]。",
      "legendary_bonus": "伤害提高 15.4%。",
      "threshold_requirements": [
        {
          "value": 40,
          "name": "Willpower"
        }
      ],
      "notes": "socket=5_5_Generic_Socket; rank=100"
    }
  ],
  "legendary_nodes": [
    {
      "name": "炎灼",
      "key": "Warlock_Legendary_004",
      "board": "炎灼",
      "priority": "high",
      "description": "地狱火技能对450%[x]健康敌人造成的伤害提高 。 术士",
      "tags": [
        "Search_Damage",
        "Keyword_Healthy"
      ],
      "notes": "selected on board Paragon_Warlock_04"
    },
    {
      "name": "强力妖术",
      "key": "Warlock_Legendary_006",
      "board": "强力妖术",
      "priority": "high",
      "description": "对敌人施加妖术、易伤或虚弱会永久降低其对你造成的伤害 25%，且其受到来自你的伤害提高 75%[x]。 术士",
      "tags": [
        "Search_Damage",
        "Skill_Abyss",
        "Keyword_Hex",
        "Keyword_Weaken"
      ],
      "notes": "selected on board Paragon_Warlock_06"
    },
    {
      "name": "仪祭",
      "key": "Warlock_Legendary_007",
      "board": "仪祭",
      "priority": "high",
      "description": "施放符印技能后，你造成的伤害提高 90%[x]，持续 15 秒。在符印范围内死亡的高阶恶魔现在计作 10 次击杀。 术士",
      "tags": [],
      "notes": "selected on board Paragon_Warlock_07"
    },
    {
      "name": "混沌",
      "key": "Warlock_Legendary_008",
      "board": "混沌",
      "priority": "high",
      "description": "当你拥有压制时，你的秘术技能造成的伤害提高 100%[x]，但当你失去一层时，你要么获得 2 层要么额外失去 1 层。 术士",
      "tags": [
        "Search_Damage",
        "Skill_Occult",
        "Keyword_Overpower"
      ],
      "notes": "selected on board Paragon_Warlock_08"
    }
  ],
  "author_notes": [
    "神符带 无名者 手套出处 格林高列 衣服出处 齐尔 项链出处 巴图克 项链穷哥们就带暗金 或者 摩洛克的跳动之焰 打到好的换传奇项链（市场没货） 30日更新装备 大家注意看符文 策尔 塞赫 + 纳古 普瑞德 火伤 和 全伤 只能保留一条 俩条有哪个用哪个！ 暗金神符：放逐领主 神符套装不全的要手动放技能 必须要有暗金手套 泽泽同款过滤 新号慎用 CoEBCgzms5XluIjpnovlrZAQAB",
    "神符带 无名者 手套出处 格林高列 衣服出处 齐尔 项链出处 巴图克 项链穷哥们就带暗金 或者 摩洛克的跳动之焰 打到好的换传奇项链（市场没货） 30日更新装备 大家注意看符文 策尔 塞赫 + 纳古 普瑞德 火伤 和 全伤 只能保留一条 俩条有哪个用哪个！ 暗金神符：放逐领主 神符套装不全的要手动放技能 必须要有暗金手套 泽泽同款过滤 新号慎用 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",
    "Converted from d2core raw build id=1T6u variant_index=0."
  ],
  "ai_analysis_status": {
    "status": "needs_review",
    "missing_fields": [],
    "last_analyzed_at": null,
    "notes": "Auto-converted from d2core raw JSON. Review inferred roles and affix priorities before using as final analysis data."
  },
  "_conversion_quality": {
    "variant_index": 0,
    "variant_name": "",
    "unresolved_references": [
      "None"
    ],
    "warnings": [
      "passive_skills are not separated from active skill data yet.",
      "affix_priorities are collected from gear mods and are not true ranked priorities.",
      "skill roles are inferred from tags/ranks and should be manually reviewed."
    ]
  }
}
```
