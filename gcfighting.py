import asyncio
import random
import gccfg
from gcclasses import GCPlayer
from gcclasses import GCEnemy
import gcdb

fights = {}

class fight_data:
    def __init__(
            self,
            location = "downtown",
            player_queue = [],
            enemy_queue = [],
            enemy_ids = [],
            player_ids = []
    ):
        self.location = location
        self.player_queue = player_queue
        self.enemy_queue = enemy_queue
        self.enemy_ids = enemy_ids
        self.player_ids = player_ids
        fights[location] = self

async def initiate_combat(enemy, player, msg):
    # Check if there is already a fight happening in that district
    if player.location in fights:
        existing = fights[player.location]
        response = player.location + " was already being fought over!\n"
        if player.userid not in existing.player_ids:
            # Add player to fight if they werent already in it
            response += "\n but {} has now joined the battle!".format(msg.author.display_name)
            existing.player_ids.append(player.userid)
        if enemy.id not in existing.enemy_ids:
            # Add target to fight if they were not already involved
            response += "\n but {} has now joined the battle!".format(enemy.name)
            existing.enemy_ids.append(enemy.id)
        # Send the response and cut the function, dont need to start a second loop
        await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + response)
        return

    # Initialize the fight
    fight = fight_data(
        location = enemy.location,
        enemy_ids = [enemy.id],
        player_ids = [player.userid]
    )

    # Tell the user the fight started
    start_msg = "{} prepares to begin combat with {}! They have 30s to prepare attacks!".format(msg.author.display_name, enemy.name)
    await msg.channel.send('*' + str(msg.author.display_name) + ':* ' + start_msg)
    while (len(fight.enemy_ids) > 0 and len(fight.player_ids) > 0):
        await asyncio.sleep(30)

        # Separate player attacks by priority
        passives = []
        actives = []
        for spell in fight.player_queue:
            if spell.type in gccfg.passive_types:
                passives.append(spell)
            else:
                actives.append(spell)

        # Calculate first priority spells, pool all buffs
        defense_pool = 0
        attack_pool = 0
        healing_pool = 0
        passives_response = ""
        for spell in passives:
            if spell.type == gccfg.spell_type_def_buff:
                defense_pool += spell.power
            if spell.type == gccfg.spell_type_atk_buff:
                attack_pool += spell.power
            if spell.type == gccfg.spell_type_heal_aoe:
                healing_pool += spell.power
            if spell.type == gccfg.spell_type_heal_target:
                if spell.target_id in fight.player_ids:
                    # Grab player object from id and heal
                    passives_response += "<@{}> is healed for {} lofi!\n".format(spell.target_id, spell.power)
                    healed_target = GCPlayer(userid=spell.target_id)
                    healed_target.lofi += spell.power
                    healed_target.persist()

        # Distribute AOE healing
        heal_per_player = int(healing_pool / len(fight.player_ids))
        if heal_per_player > 0:
            passives_response += "Everyone is healed for {} lofi!\n".format(heal_per_player)
            for healed_id in fight.player_ids:
                # Grab player object from id and heal
                healed = GCPlayer(userid = healed_id)
                healed.lofi += heal_per_player
                healed.persist()

        # Build response for buffs
        if defense_pool > 0:
            passives_response += "Defense is buffed by {}%!\n".format(defense_pool * 10)
        if attack_pool > 0:
            passives_response += "Attacks are buffed by {}%!\n".format(attack_pool * 10)

        if passives_response != "":
            await msg.channel.send(passives_response)

        # Calculate secondary spells
        total_damage = 0
        total_defense = 0
        for spell in actives:
            if spell.type == gccfg.spell_type_damage:
                total_damage += spell.power
            if spell.type == gccfg.spell_type_defense:
                total_defense += spell.power

        # add 10% to damage per point in attack buffs
        if attack_pool != 0:
            attack_pool /= 10
            attack_pool += 1
            total_damage *= attack_pool

        # add 10% to defense per point in defense buffs
        if defense_pool != 0:
            defense_pool /= 10
            defense_pool += 1
            total_defense *= defense_pool

        # Apply damage to enemies
        damage_per_enemy = int(total_damage / len(fight.enemy_ids))
        player_damage_msg = "The Magical Girls deal {} damage to every enemy in the fight!\n".format(str(damage_per_enemy))
        iteration = -1
        slain_indexes = []
        for hurt_id in fight.enemy_ids:
            #TODO - add GCEnemy.change_hp and GCEnemy.die
            iteration += 1
            hurt = GCEnemy(id = hurt_id)
            hurt.hp -= damage_per_enemy
            if hurt.hp <= 0:
                player_damage_msg += "\n{} has been slain by the magical girls and removed from the fight!".format(hurt.name)
                # Dont FUCK with the id list while iterating over it
                slain_indexes.append(iteration)
                gcdb.deleteEnemy(hurt.id)
                #TODO - add rewards for kill
            else:
                hurt.persist()

        # is there a better way to do this? probably
        # pop out the indexes of slain monsters
        for index in slain_indexes:
            fight.enemy_ids.pop(index)
            counter = 0
            for remaining in slain_indexes:
                slain_indexes[counter] = remaining - 1
                counter += 1

        # potentially end the fight if no enemies are left
        if len(fight.enemy_ids) == 0:
            player_damage_msg += "\n\nThe last enemy in the fight has been slain! "
            if gcdb.findEnemies('location', fight.location):
                player_damage_msg += "{} is still not safe however...".format(fight.location)
            else:
                player_damage_msg += "{} is safe from the corruption!! For now...".format(fight.location)
            fights.pop(fight.location)
            await msg.channel.send(player_damage_msg)
            return

        await msg.channel.send(player_damage_msg)
        # Decide enemy attacks after players attack to ensure
        # all targeted enemies get to fight back as long as
        # they survived.
        avg_size = 0
        for monster_id in fight.enemy_ids:
            monster = GCEnemy(id = monster_id)
            avg_size += monster.size
            choice = random.randrange(0, len(monster.attacks))
            fight.enemy_queue.append(gccfg.spell_map[monster.attacks[choice]])
        # calculate avg size for damage multiplier
        avg_size /= len(fight.enemy_ids)

        # calculate total damage from enemies
        monster_damage = 0
        for spell in fight.enemy_queue:
            monster_damage += spell.power * avg_size

        # Subtract player defense, minimum zero damage
        monster_damage -= total_defense
        if monster_damage <= 0:
            monster_damage = 0

        # TODO - add GCPlayer.change_lofi and GCPlayer.die
        # distribute monster damage
        monster_damage_per_player = int(monster_damage / len(fight.player_ids))
        monster_damage_message = "The fighting monsters deal {} damage to each player!\n".format(str(monster_damage_per_player))
        iteration = -1
        for fighter_id in fight.player_ids:
            iteration += 1
            fighter = GCPlayer(userid = fighter_id)
            fighter.lofi -= monster_damage_per_player
            if fighter.lofi <= 0:
                # TODO - Figure out whats supposed to happen on player death
                monster_damage_message += "\n<@{}> Has been critically wounded and removed from the fight!".format(fighter.userid)
                fighter.lofi = 0
                fight.player_ids.pop(iteration)
            fighter.persist()

        # potentially end the fight if no players are left
        if len(fight.player_ids) == 0:
            monster_damage_message += "\n\nThe last player has been slain! {} remains in darkness...".format(fight.location)
            fights.pop(fight.location)
            await msg.channel.send(monster_damage_message)
            return
        await msg.channel.send(monster_damage_message)

        # Clear spell queues and inform players of new round
        fight.enemy_queue = []
        fight.player_queue = []
        new_round_msg = "The players once again have 30s to prepare their spells..."
        await msg.channel.send(new_round_msg)