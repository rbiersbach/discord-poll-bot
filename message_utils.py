from datetime import datetime

from settings import CHANNEL_NAMES, EMOJIS


def has_votes(message) -> bool:
    emojis = [reaction.emoji for reaction in message.reactions]
    return bool(set(emojis).intersection(set(EMOJIS)))


def this_year(message) -> bool:
    return message.created_at.year == datetime.now().year


def is_suggestion_channel(message) -> bool:
    return message.channel.name in CHANNEL_NAMES
