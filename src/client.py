import discord

from calculation import Calculation
from message_utils import is_in_configured_channels, this_year
from settings import BOT_NAME, EMOJIS


class DiscordPollBotClient(discord.Client):
    """
    Client that listens to new messages and reactions to trigger the recalculation of the overall scoreboard
    """
    calculation = Calculation()

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def _get_message_from_reaction_payload(self, payload):
        """
        Gets a complete message object from the payload of a raw reaction
        :param payload: of a raw reaction
        :return: a complete message
        """
        channel = self.get_channel(payload.channel_id)
        return await channel.fetch_message(payload.message_id)

    async def on_raw_reaction_add(self, payload):
        """
        If a user adds one of the predefined reactions to qualified message in a qualified channel,
         the calculation is triggered
        :param payload: raw payload of a reaction
        :return:
        """
        message = await self._get_message_from_reaction_payload(payload)
        if payload.emoji.name in EMOJIS and this_year(message) and is_in_configured_channels(message):
            print(f"Reaction {payload.emoji.name} added!")
            await self.calculation.calculate_overview(message.channel)

    async def on_raw_reaction_remove(self, payload):
        """
        If a user removes one of the predefined reactions to qualified message in a qualified channel,
         the calculation is triggered
        :param payload: raw payload of a reaction
        :return:
        """
        message = await self._get_message_from_reaction_payload(payload)
        if payload.emoji.name in EMOJIS and this_year(message) and is_in_configured_channels(message):
            print(f"Reaction {payload.emoji.name} removed!")
            await self.calculation.calculate_overview(message.channel)

    async def on_message(self, message):
        """
        If a user mentions the bot in a qualified message, the calculation is triggered
        :param message: the incoming message
        :return:
        """
        if is_in_configured_channels(message) and BOT_NAME in map(lambda mention: mention.name, message.mentions):
            print(f"The bot was mentioned with this message: {message.content}")
            await self.calculation.calculate_overview(message.channel)
