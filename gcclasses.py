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
            if SavedData:
                gcdb.setPlayerAttribute(userid, 'id', str(userid) + "_deprecated")
            self.userid = userid
            self.location = location
            self.purity = purity
            self.lofi = lofi
            self.money = money
            self.known_spells = known_spells
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
            self.hp = self.SizeToHP(size)
            self.attacks = self.getAttacks(size)
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

