import gcdb
import random
import discord
import asyncio
from tinydb import TinyDB
from gcclasses import GCPlayer
from gcclasses import GCEnemy
import gcfighting
import gccfg
import shlex

GCplayers = TinyDB("./GCplayers.json")
GCenemies = TinyDB("./GCenemies.json")

#this part defines commands
cmd_prfx = '~'
study = 'study'
bake = 'bake'
allow = 'allowance'
lofi = 'lofi'

# Define command prefixes
study_txt = 'study'
lofi_txt = 'lofi'
money_txt = 'money'
register_txt = 'register'
menu_txt = 'menu'
work_txt = 'work'
goto_txt = 'goto'
order_txt = 'order'
db_txt = 'database'
map_txt = 'map'
spawn_txt = 'spawn'
lookout_txt = 'lookout'
fight_txt = 'fight'
test_txt = 'test'
list_spells_txt = 'spelllist'
known_spells_txt = 'spells'
learn_spell_txt = 'learnspell'
queue_spell_txt = 'qspell'

#this part assigns locations with their chanenl ID
study_hall_channel_id = 788095887884288052
moonlight_cafe_channel_id = 805464853967929344
mall_channel_id = 798059805172170782

#command responses
study_response = "You work on your homework while vibing to some nice LoFi beats!"
bake_response = 'you take a break to bake a nice batch of cookies.'
allow_response = 'What a good girl! here, have some allowance.'

# Define commands
'''
    Adds 1 to lofi when sent in the study channel
'''
async def study_cmd(msg):
    if msg.channel.id == study_hall_channel_id:
        currentLofi = int(gcdb.getPlayerAttribute(msg.author.id, 'lofi'))
        gcdb.setPlayerAttribute(msg.author.id, 'lofi', currentLofi + 1)

'''
    Shows user their current lofi
'''
async def lofi_cmd(msg):
    response = "You have {} lofi.".format(gcdb.getPlayerAttribute(msg.author.id, 'lofi'))
    await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + str(response))

'''
    Shows user their current money
'''
async def money_cmd(msg):
    response = "You have {} currency.".format(gcdb.getPlayerAttribute(msg.author.id, 'money'))
    await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + str(response))

'''
    Shows user what is for sale at the cafe
'''
async def menu_cmd(msg):
    if msg.channel.id == moonlight_cafe_channel_id:
        response = "The man at the counter glares at you. He is wearing a chef's hat and his hands are shaking violently as he drinks from a teacup, full to the brim.\n" + "strawberry cupcake: 5 money.\n" + "strawberry: 1 money.\n" + "cupcake: 3 money\n"
        await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + response)

''' 
    Buys food for user if they have the funds
'''
async def order_cmd(msg):
    # Setup Necessary Variables
    foodNames = ["strawberry cupcake", "strawberry", "cupcake"]  # the food items. Their order matches with their prices and responses in the other lists. Same indexes.
    prices = [15, 10, 5]  # Food/Prices/Descriptions should be defined at the base of a file, defining each time something runs is a little slow
    foodResponses = ["You recieve a pink cupcake. You're thinking that the fact its strawberry just because its pink is offensive to you until you bite down and discover the TRUE strawberry at the core, hidden. The strawberry is frozen for some reason and is making the cupcake soggy.", "Its a strawberry. You insert it into the inside of your mouth -where you eat it. Yum!",
                     "Its a brown cupcake. Tastes pretty good but its on the dry side. It could use some strawberries."]
    order = msg.content.split(' ', 1)[1] # splits the text into a list of two strings at the first " "

    # Ensure food exists
    if order in foodNames:
        # Check price
        cost = prices[foodNames.index(order)]  # matchin up the values via index.
        wallet = gcdb.getPlayerAttribute(msg.author.id, 'money')
        if wallet - cost >= 0:
            # Subtract cost and send response if they can afford it
            gcdb.setPlayerAttribute(msg.author.id, 'money', wallet - cost)
            response = foodResponses[foodNames.index(order)]
            await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + response)
        else:
            # Tell them if they're a broke ass bitch
            response = "Now just how do you plan to pay for that? You only gave me {} money!".format(wallet)
            await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + response)
    else:
        # Tell them the food doesn't exist
        response = "Whats that supposed to be? Go bake it yourself, kid!"
        await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + response)

'''
    Moves the user to target location
'''
async def goto_cmd(msg):
    # Setup necessary variables
    locationsList = ["mall", "study hall", "cafe", "downtown"] #List of all locations
    member = msg.author #The user
    location = msg.content.split(' ', 1)[1] #the input with the command removed. Hopefully only the location name

    # Check if they're going to a real place
    if location not in locationsList:
        # Tell them they're wrong
        response = "i dont know that location!"
        await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + response)
    else:
        # Tell them they're moving
        response = 'You begin walking to the' + ' ' + location
        await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + response + ". it will take 5 seconds")
        await asyncio.sleep(5)

        # Grab target role
        role = discord.utils.get(member.guild.roles, name=location) #This should hopefully be the same as just: name="Mall". But they can enter mall or Mall.

        # Grab current role names to search
        user_role_names = []
        for r in msg.author.roles:
            user_role_names.append(r.name) #list of their roles.

        # Ensure all existing Location Roles are removed
        for LocationName in locationsList: #I dont know if 'For loops' are okay with a bot. But it should be fine cus asyncio...?
            if (LocationName in user_role_names): #finding which location role the user has.
                role2 = discord.utils.get(member.guild.roles, name=LocationName)
                await member.remove_roles(role2)
                print('removed' + str(role2))

        # Always add target role
        await member.add_roles(role)
        print('added' + str(role))

'''
    Pays user per command, if done in mall
'''
async def work_cmd(msg):
    if msg.channel.id == mall_channel_id:
        pay = random.randrange(1, 5)
        total = pay + gcdb.getPlayerAttribute(msg.author.id, 'money')
        response = "you work long and hard at the mall to earn some cash. you made " + str(pay) + " cash!"
        gcdb.setPlayerAttribute(msg.author.id, 'money', total)
        await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + response)

'''
    Setup the user's database entry if they have none
'''
async def register_cmd(msg):
    if GCPlayer(userid=msg.author.id).new:
        await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + 'You registered!')
    else:
        await msg.channel.send('*' + str(msg.author.display_name) + ':*' + ' you already registered')

'''
    Return the entire database as text for debugging
'''
async def db_cmd(msg):
    response = str(GCplayers.all())
    await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + response)

'''
    Returns all location names
'''
async def map_cmd(msg):
    response = "mall, study hall, cafe, downtown"
    await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + response)

'''
    Spawn an enemy
'''
async def spawn_enemy(msg):
    id = 0
    while gcdb.getEnemyData(id):
        id += 1
    spawned = GCEnemy(
        id = id,
        name = "generic",
        location = "downtown",
        size = random.randrange(1,5)
    )

    response = "Spawned " + spawned.name + " with id " + str(spawned.id) + " and " + str(spawned.attacks) + " for attacks."
    await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + response)

'''
    Return enemies in user's current district
'''
async def lookout(msg):
    user_data = GCPlayer(userid = msg.author.id)
    enemies = gcdb.findEnemies("location", user_data.location)

    response = "In " + user_data.location + " you see: \n"
    if enemies:
        for enemy_data in enemies:
            response += "\nA size {} {}. ID: {}".format(str(enemy_data["size"]), enemy_data["name"], enemy_data["id"])

    await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + response)

'''
    Initiate combat sequence
'''
async def fight(msg):
    target_id = int(msg.content.split(' ', 1)[1])
    enemy_data = gcdb.getEnemyData(target_id)

    response = ""
    if enemy_data:
        enemy = GCEnemy(id = target_id)
        player = GCPlayer(userid = msg.author.id)
        if enemy.location != player.location:
            response = "That enemy is not present here."
        else:
            await gcfighting.initiate_combat(enemy, player, msg)
            return
    else:
        response = "No enemy with id {} exists".format(target_id)

    await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + response)

'''
    Fill in with whatever to test certain functionality
'''
async def test(msg):
    player = GCPlayer(userid = msg.author.id)
    player.lofi -= 1
    player.money += 1
    player.persist()

'''
    List all spells available for players to learn
'''
async def list_spells(msg):
    # compile all user usable spell names
    player_spell_names = []
    for spell in gccfg.spells:
        if gccfg.spell_user_player in spell.users:
            player_spell_names.append(spell.name)

    # Build and send response
    response = "Currently learnable spells are: \n"
    for name in player_spell_names:
        response += "\n" + name

    await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + response)

'''
    List all spells known by player
'''
async def known_spells(msg):
    # compile all user usable spell names
    player = GCPlayer(userid = msg.author.id)
    player_spells = []
    for spell_name in player.known_spells:
        if spell_name in gccfg.spell_map:
            player_spells.append(gccfg.spell_map[spell_name])

    # Build and send response
    response = "Currently known spells are: \n"
    for spell in player_spells:
        response += "\nName: {} | Cost: {}".format(spell.name, spell.cost)

    await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + response)

'''
    add spell to player's known spells
'''
async def learn_spell(msg):
    target_spell_name = msg.content.split(' ', 1)[1]
    if target_spell_name in gccfg.spell_map:
        spell = gccfg.spell_map[target_spell_name]
        player = GCPlayer(userid = msg.author.id)
        player.known_spells.append(spell.name)
        player.persist()
        response = "You have successfully learned {}".format(spell.name)
    else:
        response = "{} isn't a real spell dummy. Try {}{}".format(target_spell_name, cmd_prfx, list_spells_txt)

    await msg.channel.send('*{}:* {}'.format(msg.author.display_name, response))

'''
    Queue a spell for the current fight is user is in one and can queue
'''
async def queue_spell(msg):
    # Parse target spell and get player
    target_spell_name = shlex.split(msg.content)[1]
    player = GCPlayer(userid = msg.author.id)

    # Ensure spell exists and is known
    if (target_spell_name in gccfg.spell_map and gccfg.spell_map[target_spell_name].name in player.known_spells):
        spell = gccfg.spell_map[target_spell_name].new_copy()
        # Check for fight and ensure player participation
        if player.location in gccfg.fights:
            fight = gccfg.fights[player.location]
            if player.userid in fight.player_ids:
                # TODO - add point system
                if player.lofi > spell.cost:
                    if spell.cost <= fight.pts_remaining[player.userid]:
                        response = ""

                        # Parse target for targeted spells
                        if spell.type == gccfg.spell_type_heal_target:
                            mentions = msg.mentions
                            if len(mentions) == 1:
                                spell.target_id = mentions[0].id
                                if spell.target_id not in fight.player_ids:
                                    response = "The target must be fighting with you!"
                            if len(mentions) < 1:
                                response = "You need to mention a target!"
                            if len(mentions) > 1:
                                response = "This spell can only target one player"

                        if response != "":
                            await msg.channel.send('*{}:* {}'.format(msg.author.display_name, response))
                            return

                        player.lofi -= int(spell.cost)
                        fight.pts_remaining[player.userid] -= int(spell.cost)
                        fight.player_queue.append(spell)

                        # Build list of enemy names for flavortext
                        enemy_names = ""
                        enemy_number = 0
                        for enemy_id in fight.enemy_ids:
                            enemy_number += 1
                            enemy = GCEnemy(id = enemy_id)
                            if enemy_number > 1 and enemy_number == len(fight.enemy_ids):
                                enemy_names += ", and {} id: {}".format(enemy.name, enemy.id)
                            elif enemy_number > 1:
                                enemy_names += ", {} id: {}".format(enemy.name, enemy.id)
                            else:
                                enemy_names += "{} id: {}".format(enemy.name, enemy.id)

                        response = "Successfully queued {} against {} for {} lofi".format(spell.name, enemy_names, spell.cost)

                        player.persist()
                    else:
                        response = "You only have {} points remaining! that spell costs {}.".format(fight.pts_remaining[player.userid], spell.cost)
                else:
                    response = "You only have {} lofi! You need {} to queue that.".format(player.lofi, spell.cost)
            else:
                response = "You are not participating in the present fight."
        else:
            response = "There are no fights to attack for here."
    else:
        response = "You don't know that spell."

    await msg.channel.send('*{}:* {}'.format(msg.author.display_name, response))

# Create cmd dictionary
cmd_dict = {
    study_txt : study_cmd,
    lofi_txt : lofi_cmd,
    money_txt : money_cmd,
    work_txt : work_cmd,
    goto_txt : goto_cmd,
    order_txt : order_cmd,
    menu_txt : menu_cmd,
    register_txt : register_cmd,
    db_txt : db_cmd,
    map_txt : map_cmd,
    spawn_txt : spawn_enemy,
    lookout_txt : lookout,
    fight_txt : fight,
    test_txt : test,
    list_spells_txt : list_spells,
    known_spells_txt : known_spells,
    learn_spell_txt : learn_spell,
    queue_spell_txt : queue_spell
}