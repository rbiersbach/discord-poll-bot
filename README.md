# Discord Poll Bot
This bot is meant to ease bigger voting processes that are managed by multiple users in a discord channel.
1. It collects all messages with specified reactions in a specified time frame
2. If the message contains an url it will look up the preview title of the url
3. The results will be sorted and printed out in the channel

To trigger the bot you can mention it in the respective channel e.g. `@BotName` or add/remove one of the specified reactions.

## Configuration
The bot can be configured with environment variables:
    
    # mandatory - used to connect to the bot
    DISCORD_BOT_TOKEN=<insert token here>

    #  mandatory - identifies messages of the bot
    BOT_NAME=MyGreatBot

    # mandatory - comma separated channels that should be considered for the processing
    CHANNEL_NAMES=channel1,channel2

    # optional - comma separated emojis that should be considered for the processing
    EMOJIS=👍,👎

    # optional - comma separated list of highlighting for users that voted for a certain emoji
    EMOJI_HIGHLIGHTING=*,~~

