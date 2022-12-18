from discord import Intents

from client import DiscordPollBotClient
from settings import DISCORD_BOT_TOKEN

# some events need to specifically be enabled with intents
intents = Intents.all()

# configure and start the client
client = DiscordPollBotClient(intents=intents)
client.run(DISCORD_BOT_TOKEN)
