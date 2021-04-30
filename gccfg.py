from gcspells import GCSpell

fights = {}

damage_source_combat = "combat"

death_cost = 20

pts_per_round = 30

spell_user_player = "players"
spell_user_enemy = "enemies"
spell_type_damage = "damage"
spell_type_defense = "defense"
spell_type_heal_target = "heal_target"
spell_type_heal_aoe = "heal_aoe"
spell_type_atk_buff = "attack_buff"
spell_type_def_buff = "defense_buff"

passive_types = [
    spell_type_atk_buff,
    spell_type_def_buff,
    spell_type_heal_aoe,
    spell_type_heal_target
]

spells = [
    GCSpell(
        name = "Throw Something!",
        aliases = ["basicdamage"],
        type = spell_type_damage,
        power = 1,
        cost = 1,
        users = [spell_user_player, spell_user_enemy]
    ),
    GCSpell(
        name = "Block Your Face!",
        aliases = ["basicblock"],
        type = spell_type_defense,
        power = 1,
        cost = 1,
        users = [spell_user_player]
    ),
    GCSpell(
        name = "Heal a friend!",
        aliases = ["targetheal"],
        type = spell_type_heal_target,
        power = 5,
        cost = 1,
        users = [spell_user_player]
    ),
    GCSpell(
        name = "Heal Everyone!",
        aliases = ["blanketheal"],
        type = spell_type_heal_aoe,
        power = 1,
        cost = 1,
        users = [spell_user_player]
    ),
    GCSpell(
        name = "Power Up!",
        aliases = ["atkbuff"],
        type = spell_type_atk_buff,
        power = 1,
        cost = 1,
        users = [spell_user_player]
    ),
    GCSpell(
        name = "Friendship Shield?",
        aliases = ["defbuff"],
        type = spell_type_def_buff,
        power = 1,
        cost = 1,
        users = [spell_user_player]
    )
]
spell_map = {}

for spell in spells:
    for name in spell.aliases:
        spell_map[name] = spell