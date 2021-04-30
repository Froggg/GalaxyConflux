import gccfg
from gcclasses import GCPlayer

"""Message fucntion that automates some of the formating"""
async def sent_message(msg, text, player_formatting = True):
    if player_formatting:
        text = '*' + str(msg.author.display_name) + ':* ' + text

    await msg.channel.send(text)


"""Update discord member roles to player location""" #TODO: update to pick and choose which roles to add and remove instead of remove all roles then add all correct roles
async def update_member_role(member):
    player_data = GCPlayer(member.id)
    
    roles_to_remove = []
    for role in member.roles:
        if role.name != "@everyone":
            roles_to_remove.append(role)

    #print(roles_to_remove)
    await member.remove_roles(*roles_to_remove)


    roles_to_add = []
    #get player location role
    location_role = gccfg.role_map.get(player_data.location)
    if location_role != None:
        roles_to_add.append(location_role)

    
    roles_to_add.append(gccfg.role_map.get("School Girl"))

    #print(roles_to_add)
    await member.add_roles(*roles_to_add)

def copy_list(target):
    copy = []
    for val in target:
        copy.append(val)

    return copy