from discord import Intents

from client import MyClient
from settings import DISCORD_BOT_TOKEN

# some events need to specifically be enabled
intents = Intents.default()
intents.members = True
intents.presences = True

client = MyClient(intents=intents)
client.run(DISCORD_BOT_TOKEN)
