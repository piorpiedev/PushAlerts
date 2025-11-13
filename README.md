# PushAlerts
This is a simple program to scan for updates on a very specific website, and sync them with a Telegram channel

IMPORTANT: As of right now, Telegram DOESN'T allow bots to delete messages older than 24 hours

## Todos:
- Send a message in the channel when another msg has been updated (EDIT event), and delete it after an x amount of time (or when it gets edited once again)

## Maybes:
- Make the whole thing async. Not really necessary, just a nice addiction to have
- Instead of using a local db, use the channel messages. It would probably be worse for performances, but can be useful to make sure that the channel is actually synced

## Updates over v1
- At every update the rows are confronted with the stored ones, and in case of changes, they are updated on the local db and the Telegram channel
- The bot chat has been completely removed, and everything has been moved to a channel
- In case of errors or rame limits the bot will wait for the rate limit to expire, instead of just crashing..
- By removing polling, the NoInternetConnectionException (or whatever was it called) spam in console has also been resolved
