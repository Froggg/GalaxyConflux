import discord
import gccfg
import gcloader

client = gccfg.client

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    #load config jsons and get discord channels and roles
    gcloader.generate_cmd_map()
    gcloader.generate_spell_map()
    await gcloader.generate_channel_map()
    await gcloader.generate_role_map()

@client.event
async def on_message(message):

    # do not respond to self messages
    if message.author == client.user:
        return

    #message.content = message.content.lower()

    # respond command messages
    if message.content.startswith(gccfg.cmd_prefix):
        # get first word (the command name)
        term = (message.content.split(" ")[0]).lower()

        # get command fucntion from command map
        cmd_fn = gccfg.cmd_map.get(term)
        if cmd_fn != None:
            await cmd_fn(message)
        else:
            #TODO: add response for players typing unknown commands
            pass

# read token file
f = open("token")
token = f.readline().strip()

# connect to discord
try:
    client.run(token)
except:
    print("could not connect to discord with token")