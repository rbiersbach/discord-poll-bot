import os
from typing import List


def get_env_as_list(key: str, default: List[str] = None) -> List[str]:
    values = list(filter(bool, os.getenv(key, "").split(",")))
    if not values and not default:
        raise Exception(f"Mandatory environment variable {key} not provided!")
    return values or default


# used to connect to the bot
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
# identifies messages of the bot
BOT_NAME = os.getenv("BOT_NAME")
# comma separated channel names that should be considered for the processing
CHANNEL_NAMES = get_env_as_list("CHANNEL_NAMES")
# comma separated emojis that should be considered for the processing
EMOJIS = get_env_as_list("EMOJIS", default=["👍", "👎"])
# comma separated text highlighting for user names that voted for the specific emoji, same order as emojis
EMOJI_HIGHLIGHTING = get_env_as_list("EMOJI_HIGHLIGHTING", default=["*", "~~"])
# regex to determine urls in messages
URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s(" \
            r")<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
