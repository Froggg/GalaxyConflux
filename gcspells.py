class GCSpell:
    # Create the spell object
    def __init__(
            self,
            name = "",
            aliases = [],
            type = "damage",
            power = 0,
            cost = 0,
            users = []
    ):
        self.name = name
        self.aliases = aliases
        self.aliases.append(self.name)
        self.aliases.append(self.name.lower())
        self.type = type
        self.power = power
        self.cost = cost
        self.users = users

    # Returns a unique instance
    def new_copy(self):
        return (GCSpell(
            name = self.name,
            type = self.type,
            power = self.power,
            cost = self.cost,
            users = self.users
        ))