import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

from linkpreview import link_preview

from message_utils import has_votes, this_year
from models import MessageOverview, Vote
from settings import EMOJIS, EMOJI_HIGHLIGHTING, URL_REGEX, BOT_NAME

executor = ThreadPoolExecutor(max_workers=10)
loop = asyncio.get_event_loop()


class Calculation:
    preview_request_cache: Dict[str, str] = {}

    async def _calculate_message(self, message) -> MessageOverview:
        # get all urls in the message
        url = re.findall(URL_REGEX, message.content)
        if url:
            try:
                # if there is an url then get the preview title
                title = await self.get_title_url(url[0][0])
            except Exception as e:
                print(e)
                # if it fails take the last part of the url
                title = url[0][0].removesuffix("/").split('/')[-1]
        else:
            # or the content as last resort
            title = message.content

        votes = []
        for emoji in EMOJIS:
            count = 0
            users = []
            reaction = next(filter(lambda reaction: reaction.emoji == emoji, message.reactions), None)
            if reaction:
                count = reaction.count
                users = await reaction.users().flatten()
            vote = Vote(emoji=emoji, users=[u.display_name for u in users], count=count)
            votes.append(vote)

        if not message.pinned:
            await message.pin()

        result = MessageOverview(
            title=title,
            votes=votes
        )
        return result

    async def calculate_overview(self, message):
        print("Starting calculation of overview!")
        await message.channel.send("on it :new_moon_with_face:")

        # calculate overview for all messages with votes in a certain time frame
        history_with_votes = message.channel.history().filter(has_votes).filter(this_year)
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

            if len(current_message + new_line) > 2000:
                scoreboard_messages.append(current_message)
                current_message = ""

            current_message = current_message + new_line

        scoreboard_messages.append(current_message)
        await self.delete_previous_messages(message)

        for scoreboard_message in scoreboard_messages:
            await message.channel.send(scoreboard_message)

        print("Finished calculation of overview!")

    async def get_title_url(self, url: str) -> str:
        # get preview of url from cache or http request
        preview = self.preview_request_cache.get(url)
        if not preview:
            preview = await loop.run_in_executor(None, link_preview, url)
            self.preview_request_cache[url] = preview

        removed_suffix = preview.title.removesuffix(" on Steam")
        removed_prefix = re.sub(r"Save \d{1,2}% on ", "", removed_suffix)
        removed_prefix = removed_prefix.removeprefix("Ubisoft - ")
        return removed_prefix

    async def delete_previous_messages(self, message):
        old_bot_messages = message.channel.history().filter(lambda message: message.author.name == BOT_NAME)
        await asyncio.gather(*[bot_message.delete() async for bot_message in old_bot_messages])
