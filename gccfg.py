#not to many thing should be imported here to avoid circular imports
import discord

# create client here so that its global
client = discord.Client()

cmd_prefix = "~"

# maps that get setup in gcloader later
cmd_map = {}
location_map = {}
role_map = {}
spell_map = {}

# options to make bot automatically setup channels and roles
# needs more testing and polishing and should not be use on main server yet
# very convienent for test server where channel and roles can be created and deleted without consequence
construct_mising_channels = False
construct_mising_roles = False

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

spells = []

passive_types = [
    spell_type_atk_buff,
    spell_type_def_buff,
    spell_type_heal_aoe,
    spell_type_heal_target
]
