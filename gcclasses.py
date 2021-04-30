import gcdb
import gccfg

class GCPlayer:
    # setup default values
    def __init__(
        self,
        userid = 0,
        location = "downtown",
        purity = "pure",
        lofi = 0,
        money = 0,
        known_spells = []
    ):
        # Check for and possibly load saved data
        SavedData = gcdb.getPlayerData(userid)
        try:
            self.userid = userid
            self.location = SavedData["location"]
            self.purity = SavedData["purity"]
            self.lofi = SavedData["lofi"]
            self.money = SavedData["money"]
            self.known_spells = SavedData["known_spells"]
            self.new = False
        # Or initialize from given values
        except:
            # Set defaults
            self.userid = userid
            self.location = location
            self.purity = purity
            self.lofi = lofi
            self.money = money
            self.known_spells = known_spells

            # If there was saved data that otherwise failed to set, set those values
            if SavedData:
                # Relabel old entry
                gcdb.setPlayerAttribute(userid, 'id', str(userid) + "_deprecated")
                for key in SavedData:
                    try:
                        # Don't move data that isn't included in the defaults
                        # getatt will throw an error so the except statement runs
                        self.__getattribute__(key)
                        self.__setattr__(key, SavedData[key])
                    except:
                        print("Failed to move old value for " + key + " for " + str(userid))

            gcdb.createEntry(self)
            self.new = True

    def persist(self):
        # Grab existing data
        SavedData = gcdb.getPlayerData(self.userid)

        # Iterate through all saved values
        for key in SavedData:
            if key != 'id': #and SavedData[key] != getattr(self, key):
                # Only Bother with changed values
                # We do a little bothering with unchanged values for the time being cause known_spells wasnt working
                gcdb.setPlayerAttribute(self.userid, key, getattr(self, key))

    """ Handle loss of health """
    def change_hp(self, amount, source):
        self.lofi += amount
        if self.lofi <= 0:
            self.die(source)
        self.persist()

    """ 
        Handle everything that might happen on death, resetting to a hosopital
        losing some money, maybe some purity, etc
    """
    def die(self, source):
        if source == gccfg.damage_source_combat:
            gccfg.fights[self.location].player_ids.remove(self.userid)
            # TODO: potential monster buffs for kills
        self.money -= gccfg.death_cost
        self.lofi = 0
        # Lower purity tier or something?
        self.location  = "downtown"
        self.persist()

class GCEnemy:
    # Set default values
    def __init__(
            self,
            name = "",
            id = 0,
            location = "",
            size = 0,
            hp = 0,
            attacks = []
    ):
        SavedData = gcdb.getEnemyData(id)
        if SavedData:
            self.id = id
            self.name = SavedData["name"]
            self.location = SavedData["location"]
            self.size = SavedData["size"]
            self.hp = SavedData["hp"]
            self.attacks = SavedData["attacks"]
        else:
            self.id = id
            self.name = name
            self.location = location
            self.size = size
            self.hp = self.SizeToHP(size) if hp == 0 else hp
            self.attacks = self.getAttacks(size) if attacks == [] else attacks
            gcdb.createEnemyEntry(self)

    """ Save new data to the database """
    def persist(self):
        # Grab existing data
        SavedData = gcdb.getEnemyData(self.id)

        # Iterate through all saved values
        for key in SavedData:
            if key != 'id' and SavedData[key] != getattr(self, key):
                # Only Bother with changed values
                gcdb.setEnemyAttribute(self.id, key, getattr(self, key))

    """ Return starting HP based on enemy size """
    def SizeToHP(self, size):
        return (size * 10)

    """ Grab 3 damage attacks at random """
    def getAttacks(self, size):
        attacks = []
        for spell in gccfg.spells:
            if spell.type == gccfg.spell_type_damage and gccfg.spell_user_enemy in spell.users:
                attacks.append(spell.name)
        return attacks

    def changeHp(self, amount):
        self.hp += amount
        if self.hp <= 0:
            self.die()
        else:
            self.persist()

    def die(self):
        gcdb.deleteEnemy(self.id)
        gccfg.fights[self.location].enemy_ids.remove(self.id)
        # TODO: distribute rewards to players left in fight?