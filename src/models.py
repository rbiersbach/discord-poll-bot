from typing import List

import attr


@attr.s(auto_attribs=True)
class Vote:
    """
    The vote for a specific emoji on a single message, containing display names of the voting users
    """
    emoji: str
    users: List[str]
    count: int


@attr.s(auto_attribs=True)
class MessageOverview:
    """
    An overview over all votes and the human readable title of a message
    """
    title: str
    votes: List[Vote]
