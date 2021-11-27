import discord

from calculation import Calculation
from message_utils import is_suggestion_channel, this_year
from settings import EMOJIS, BOT_NAME


class MyClient(discord.Client):
    calculation = Calculation()

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def _get_message_from_reaction_payload(self, payload):
        channel = self.get_channel(payload.channel_id)
        return await channel.fetch_message(payload.message_id)

    async def on_raw_reaction_add(self, payload):
        message = await self._get_message_from_reaction_payload(payload)
        if payload.emoji.name in EMOJIS and this_year(message) and is_suggestion_channel(message):
            print(f"Reaction {payload.emoji.name} added!")
            await self.calculation.calculate_overview(message)

    async def on_raw_reaction_remove(self, payload):
        message = await self._get_message_from_reaction_payload(payload)
        if payload.emoji.name in EMOJIS and this_year(message) and is_suggestion_channel(message):
            print(f"Reaction {payload.emoji.name} removed!")
            await self.calculation.calculate_overview(message)

    async def on_message(self, message):
        if is_suggestion_channel(message) and BOT_NAME in map(lambda mention: mention.name, message.mentions):
            await self.calculation.calculate_overview(message)
