from datetime import datetime

from settings import CHANNEL_NAMES, EMOJIS


def has_votes(message) -> bool:
    """
    Determines, if a message has any emoji reaction from the predefined list of emojis
    :param message: the message being checked
    :return: true, if at least one emoji exists
    """
    emojis = [reaction.emoji for reaction in message.reactions]
    return bool(set(emojis).intersection(set(EMOJIS)))


def this_year(message) -> bool:
    """
    Determines, if a message has been created this year
    :param message: the message being checked
    :return: true, if year of creation is the same as this year
    """
    return message.created_at.year == datetime.now().year


def is_in_configured_channels(message) -> bool:
    """
    Determines, if the message was sent to one of the configured channels
    :param message: the message being checked
    :return: true, if the name of the current channel is in the configurations
    """
    return message.channel.name in CHANNEL_NAMES
