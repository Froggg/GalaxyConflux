import gcdb
import random
import discord
import asyncio
from tinydb import TinyDB
import gcfighting
import gccfg
from gcclasses import GCPlayer, GCEnemy
import shlex

from gcutility import sent_message, update_member_role

GCplayers = gcdb.GCplayers

# Define commands
'''
    Adds 1 to lofi when sent in the study channel
'''
async def study_cmd(msg):
    #check if player is in proper channel
    if msg.channel.id == gccfg.location_map.get("study-hall").channel_id:
        #add 1 lofi
        player = GCPlayer(msg.author.id)
        player.lofi += 1
        player.persist()
    #TODO: add a response when players are in the wrong channel

'''
    Shows user their current lofi
'''
async def lofi_cmd(msg):
    player = GCPlayer(msg.author.id)
    response = "You have {} lofi.".format(player.lofi)
    await sent_message(msg, response)

'''
    Shows user their current money
'''
async def money_cmd(msg):
    player = GCPlayer(msg.author.id)
    response = "You have {} currency.".format(player.money)
    await sent_message(msg, response)

'''
    Shows user what is for sale at the cafe
'''
async def menu_cmd(msg):
    if msg.channel.id == gccfg.location_map.get("mall").channel_id:
        response = "The man at the counter glares at you. He is wearing a chef's hat and his hands are shaking violently as he drinks from a teacup, full to the brim.\n" + "strawberry cupcake: 5 money.\n" + "strawberry: 1 money.\n" + "cupcake: 3 money\n"
        await sent_message(msg, response)
    #TODO: add a response when players are in the wrong channel

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
    member = msg.author #The user
    player = GCPlayer(msg.author.id)
    desired_location = msg.content.split(' ', 1)[1] #the input with the command removed. Hopefully only the location name

    # check if desired location is a real location
    found_location = None
    for location in gccfg.location_map:
        location = gccfg.location_map[location]
        if location.is_alias(desired_location):
            found_location = location


    # location not found
    if found_location == None:
        response = "i dont know that location!"
        await sent_message(msg, response)

    # player already in location
    elif found_location.id == player.location:
        response = "You are already here"
        await sent_message(msg, response)

    # vaild desired location
    else:
        # Tell them they're moving
        response = 'You begin walking to ' + found_location.full_name + ". it will take 5 seconds"
        await sent_message(msg, response)

        #wait 5 seconds
        await asyncio.sleep(5)

        # change database location
        player = GCPlayer(msg.author.id)
        player.location = found_location.id
        player.persist()

        # update member roles
        await update_member_role(member)


'''
    Allows people to look where they are
'''
async def look_cmd(msg):
    response = None

    #get player location
    player = GCPlayer(msg.author.id)
    current_location = gccfg.location_map.get(player.location)

    if (current_location != None):
        response = current_location.look_txt
    else:
        response = "You are sitting in front of your parents' PC. There's a cup with some hot brew you made that you can't recall if it was tea or coffee, but it's gotten cold so who cares. You have bags under your eyes. You've been looking at this PC for way too long."
    await sent_message(msg, response)

'''
    Pays user per command, if done in mall
'''
async def work_cmd(msg):
    if msg.channel.id == gccfg.location_map.get("mall").channel_id:
        player = GCPlayer(msg.author.id)

        # make a random amount of money beween 1 and 5
        pay = random.randrange(1, 5)

        # add pay to player's money total
        player.money += pay
        player.persist()

        response = "you work long and hard at the mall to earn some cash. you made " + str(pay) + " cash!"
        await sent_message(msg, response)

    #TODO: add a response when players are in the wrong channel

'''
    Setup the user's database entry if they have none
'''
async def register_cmd(msg):
    if GCPlayer(userid=msg.author.id).new:
        await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + 'You registered!')
    else:
        await msg.channel.send('*' + str(msg.author.display_name) + ':*' + ' you already registered')

'''
    Allows the user to see their transformation into a magical girl
'''


async def transform_cmd(msg):  # In the future I'll turn it into a tag, for now it is just hard to unlock flavor text

    player = GCPlayer(msg.author.id)
    currentLofi = player.lofi

    if currentLofi >= 1000000:
        response = "Epic orchestral music starts to sound. You summon the power of friendship and love and scream your magical girl name with all your soul. Your regular student clothes begin to disappear to reveal a super cute outfit without ever showing anything NSFW to the camera. People around you are hypnotized by this transformation, you notice that thanks to the 'Damns' and 'Holy fucks' they let out. You are a magical girl now, go kick some bad guy's ass!"
    elif currentLofi >= 100000:
        response = "you focus REALLY hard, and feel a breeze whip around you! ... but nothing really happened... so close..."
    elif currentLofi >= 10000:
        response = "you spin in place, really believing this time it will work!!! \n you fall over into your chair, having only **transformed** your hair into a big mess"
    elif currentLofi >= 1000:
        response = "you clasp your hands and look up to the sky, the moon reflected in your big eyes. you feel tingly!!! \n .... its just because you have been sitting too long..."
    elif currentLofi >= 100:
        response = "you grab your pen and poirouette around the room! you jump off your bed ready to take flight and- \n you fall onto the conveniently placed beanbag. nope, cant fly yet."
    else:
        response = "you spin around your room, your beautiful Guardian Garb flowing around you, those bad guys better watch out!!! \n... ok time to stop playing pretend and get out of this cheap cosplay gear."

    await sent_message(msg, response)


'''
    Return the entire database as text for debugging
'''
async def db_cmd(msg):
    response = str(GCplayers.all())
    await sent_message(msg, response)

'''
    Returns all location names
'''
async def map_cmd(msg):
    #TODO: generate list from location_map
    response = "mall, study hall, cafe, downtown"
    await sent_message(msg, response)

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
async def lookout_cmd(msg):
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
        response = "{} isn't a real spell dummy. Try {}{}".format(target_spell_name, gccfg.cmd_prefix, "listspells")

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
