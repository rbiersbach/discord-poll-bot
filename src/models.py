from typing import List

import attr


@attr.s(auto_attribs=True)
class Vote:
    emoji: str
    users: List[str]
    count: int


@attr.s(auto_attribs=True)
class MessageOverview:
    title: str
    votes: List[Vote]
