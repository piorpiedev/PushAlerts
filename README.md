# PushAlerts
This is a simple program to scan for updates on a very specific website, that i won't talk about, and sync them with a Telegram channel

## Todos:
- Send a message when another msg is updated (EDIT event), and delete it after an x amount of time, or when it gets edited again
- Make the whole think async. Not really necessary, just a nice addiction to have

## Updates over v1
- At every update the rows are confronted with the stored ones, and in case of changes, they are updated on the local db and the Telegram Channel.
- The bot chat has been completely removed, and everything has been moved to a channel
- In case of errors or rame limits the bot will wait for the rate limit to expire, instead of just crashing..
- By removing polling, has also been completely removed the problem with NoInternetConnectionException (or whatever was it called) spam in console
