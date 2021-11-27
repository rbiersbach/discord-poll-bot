import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

from linkpreview import link_preview

from message_utils import has_votes, this_year
from models import MessageOverview, Vote
from settings import BOT_NAME, EMOJIS, EMOJI_HIGHLIGHTING, URL_REGEX

executor = ThreadPoolExecutor(max_workers=10)
loop = asyncio.get_event_loop()


class Calculation:
    preview_request_cache: Dict[str, str] = {}

    async def calculate_overview(self, channel):
        """
        Creates a scoreboard for all messages in the current channel that contain a predefined reaction
        and orders it by number of votes.

        :param channel: the channel where the scoreboard calculation should take place
        :return:
        """
        print("Starting calculation of scoreboard overview!")
        await channel.send("on it :new_moon_with_face:")

        # calculate overview for all messages with votes in a certain time frame
        history_with_votes = channel.history().filter(has_votes).filter(this_year)
        overview_tasks = [self._calculate_message(channel_message) async for channel_message in history_with_votes]
        print(f"Processing {len(overview_tasks)} messages!")
        message_overviews = await asyncio.gather(*overview_tasks)

        # sort by entries with down-votes lowest then by highest up-votes
        sorted_message_overviews = sorted(message_overviews, key=lambda o: (o.votes[-1].count, -o.votes[0].count))

        # figure out longest title to have a clean alignment
        max_title_length = len(max(message_overviews, key=lambda o: len(o.title)).title)

        scoreboard_messages = []
        current_message = ""
        for overview in sorted_message_overviews:
            # fill title with spaces to fit max lenght
            title = overview.title.ljust(max_title_length, ' ')
            # show emojis with counts
            stats = " ".join(map(lambda vote: f"{vote.emoji}{vote.count}", overview.votes))

            # show user names differing by format depending on emoji
            highlighted_users = []
            for vote_highlight in zip(overview.votes, EMOJI_HIGHLIGHTING):
                vote, highlight = vote_highlight
                for user in vote.users:
                    highlighted_users.append(highlight + user + highlight)
            users = " ".join(highlighted_users)

            new_line = f"`{title} {stats}` {users}\n"

            # discord only allows messages with a maximum of 2000 characters
            if len(current_message + new_line) > 2000:
                # so we are splitting the scoreboard message up in multiple small ones
                scoreboard_messages.append(current_message)
                current_message = ""

            current_message = current_message + new_line
        scoreboard_messages.append(current_message)

        # as we don't want to spam the channel we are cleaning up all previous bot messages
        await self._delete_previous_messages(channel)

        # send the final scoreboard messages
        for scoreboard_message in scoreboard_messages:
            await channel.send(scoreboard_message)

        print("Finished calculation of overview!")

    async def _calculate_message(self, message) -> MessageOverview:
        """
        gathers insights like title of included url and votes from a message
        :param message: the message that is being processed
        :return: a message overview containing a human readable title and all emoji reactions, with users and counts
        """
        # get all urls in the message
        url = re.findall(URL_REGEX, message.content)
        if url:
            try:
                # if there is an url then get the preview title
                title = await self._get_title_url(url[0][0])
            except Exception as e:
                print(e)
                # if it fails take the last part of the url
                title = url[0][0].removesuffix("/").split('/')[-1]
        else:
            # or the content as last resort
            title = message.content

        votes = []
        # collect votes for reactions that have been configured
        for emoji in EMOJIS:
            count = 0
            users = []
            reaction = next(filter(lambda reaction: reaction.emoji == emoji, message.reactions), None)
            if reaction:
                count = reaction.count
                users = await reaction.users().flatten()
            vote = Vote(emoji=emoji, users=[u.display_name for u in users], count=count)
            votes.append(vote)

        # all messages with votes should be pinned to have an easier time navigating them
        if not message.pinned:
            await message.pin()

        result = MessageOverview(
            title=title,
            votes=votes
        )
        return result

    async def _get_title_url(self, url: str) -> str:
        """
        Get the preview title of a url to have a human readable text to display
        :param url: url that should be queried for a title
        :return: human readable text to display as a title
        """
        # get preview of url from cache or http request
        preview = self.preview_request_cache.get(url)
        if not preview:
            # run http request in an asynchronous context to prevent active waiting
            preview = await loop.run_in_executor(None, link_preview, url)
            print(f"Getting {url} for the first time, should be cached now!")
            self.preview_request_cache[url] = preview

        # remove common prefixes and suffix that reduce readability
        removed_suffix = preview.title.removesuffix(" on Steam")
        removed_prefix = re.sub(r"Save \d{1,2}% on ", "", removed_suffix)
        removed_prefix = removed_prefix.removeprefix("Ubisoft - ")
        return removed_prefix

    async def _delete_previous_messages(self, channel):
        """
        Deletes all
        :param message:
        :return:
        """
        old_bot_messages = channel.history().filter(lambda message: message.author.name == BOT_NAME)
        old_bot_message_tasks = [bot_message.delete() async for bot_message in old_bot_messages]
        print(f"Deleting {len(old_bot_message_tasks)} old messages!")
        await asyncio.gather(*old_bot_message_tasks)
