import discord
import json
import os
import importlib
from pprint import pprint

from gcclasses import GCLocation
from gcclasses import GCSpell
import gccfg


def generate_cmd_map():
    gccfg.cmd_map = {}

    # grab command json
    f = open(os.path.join('json_cfg','cmd_cfg.json'))
    cmd_json = json.load(f)
    f.close()

    for element in cmd_json:
        element = cmd_json[element]
        
        function_name = element["function"]

        #get command fucntion from gccmd unless cmd_cfg.json specifies a differernt module file
        module_name = element.get("module", "gccmd")

        # get command function
        temp = importlib.__import__(module_name, fromlist = [function_name])
        cmd_fn = getattr(temp, function_name)
        
        # bind command names and funtions to cmd_map
        for command_name in element["command_names"]:
            gccfg.cmd_map.update({gccfg.cmd_prefix + command_name: cmd_fn})

    #pprint(gccfg.cmd_map)


async def generate_channel_map():
    gccfg.location_map = {}
    guild = gccfg.client.guilds[0]

    # grab command json
    f = open(os.path.join('json_cfg','location_cfg.json'), encoding="utf8")
    location_json = json.load(f)
    f.close()

    # construct GCLocation objects and map to location id
    for location_id in location_json:
        location_obj = GCLocation(location_id, _json_entry=location_json[location_id])
        gccfg.location_map.update({location_id: location_obj})


    # quick and dirty add missing channel feature
    if (gccfg.construct_mising_channels == True):
        for location in gccfg.location_map:
            location = gccfg.location_map[location]
            if location.channel_id == None:
                channel = await guild.create_text_channel(location.id)
                print(f"created channel for {location.id}")
                location.channel_id = channel.id

    #pprint(gccfg.location_map)



async def generate_role_map():
    guild = gccfg.client.guilds[0]

    # map location ids to roles
    for location in gccfg.location_map:
        location = gccfg.location_map[location]

        role = discord.utils.get(guild.roles, name=location.role_name)

        if role != None:
            gccfg.role_map.update({location.id: role})
        else:
            #quick and dirty add missing roles feature
            if (gccfg.construct_mising_roles == True):
                role = await guild.create_role(name=location.role_name)
                gccfg.role_map.update({location.id: role})
                print(f"created role {role.name}")

    # get other roles
    for role_name in ["School Girl"]:
        role = discord.utils.get(guild.roles, name=role_name)

        if role != None:
            gccfg.role_map.update({role_name: role})
        else:
            #quick and dirty add missing roles feature
            if (gccfg.construct_mising_roles == True):
                role = await guild.create_role(name=role_name)
                gccfg.role_map.update({role_name: role})
                print(f"created role {role.name}")


    #pprint(gccfg.role_map)

def generate_spell_map():
    gccfg.spell_map = {}

    # grab spell json
    f = open(os.path.join('json_cfg','spell_cfg.json'), encoding="utf8")
    spells_json = json.load(f)
    f.close()

    # construct GCLocation objects and map to location id
    for spell_name in spells_json:
        spell_obj = GCSpell(spell_name, json_entry=spells_json[spell_name])
        gccfg.spells.append(spell_obj)
        for alias in spell_obj.aliases:
            gccfg.spell_map.update({alias: spell_obj})