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

## Deployment
Every push to the `main` branch triggers a deployment to heroku.
To make this run you need to know a few details:
1. The github-action seems to support only one buildpack, making it mandatory to run `heroku buildpacks:add heroku/python -a ${HEROKU_APP_NAME}` after the first successful deployment.
2. As the process is run as a worker (see `Procfile`) we need to scale the number up with `heroku ps:scale worker=1 -a ${HEROKU_APP_NAME}` to have a running process 
3. You can watch the logs with: `heroku logs -a ${HEROKU_APP_NAME} -t`

## TODOs
- add github-actions for code formatting and tests
- extend url crawling
- improve caching implementation
- use json config and title cleanup to config (removal of prefixes and suffixes)
