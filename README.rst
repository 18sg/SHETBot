SHETBot -- An IRC Bot for SHET
==============================

Provides a bot which exposes events in the channel via SHET. It does not,
however, allow IRC users to interact with the SHET tree. It is up to other SHET
clients to link events in the channel with suitable responses.

Note to non house'rs: Currently the code is a touch messy (and nicks and
channels are hard-coded...).


General Channel Stuff -- ``/irc/``
----------------------------------

* Event: ``on_join -> nick`` -- Raised when a user joins the channel.
* Event: ``on_quit -> nick, message`` -- Raised when a user /quits.
* Event: ``on_say -> nick, message`` -- Raised when anyone speaks.
* Event: ``on_action -> nick, message`` -- Raised when anyone uses /me.


General User Stuff -- ``/user/irc/``
------------------------------------

Listed (in the source) users have their own IRC events in the ``irc`` directory
in their directory in SHET (rather than a directory named by their nick).

User channel events
```````````````````
* Event: ``on_join`` -- Raised when a user joins the channel.
* Event: ``on_quit -> message`` -- Raised when a user quits the channel.
* Event: ``on_say -> message`` -- Raised when the user speaks in the channel.
* Event: ``on_action -> message`` -- Raised when the user uses /me in the channel.

User being talked to/about
``````````````````````````
* Event: ``on_mention -> sender, message`` -- Raised when the user is
  mentioned in the channel.
* Event: ``on_address -> sender, message`` -- Raised when the user is
  addressed specifically in the channel.

Contact user via bot
````````````````````
* Action: ``bot_say_to(message)`` -- Send a message to the channel addressed to the user
* Action: ``bot_pm_to(message)`` -- Send a pm to the user

User interactions with the bot
``````````````````````````````
* Event: ``on_mention_bot -> message`` -- Raised when the user mentions the bot.
* Event: ``on_address_bot -> message`` -- Raised when the user addresses the
  bot specifically.
* Event: ``on_pm_bot -> message`` -- Raised when the user sends the bot a PM.
* Event: ``on_pm_action_bot -> message`` -- Raised when the user sends the bot a
  /me in a PM.


IRC Bot Specific Stuff -- ``/irc/bot/``
---------------------------------------

In addition to the things users have in their directories, the bot also has the
follwing:

* Action: ``say(message)`` -- Send a message to the channel
* Action: ``say_to(nick, message)`` -- Send an addressed message to nick the channel
* Action: ``action(message)`` -- Send a /me message to the channel
* Action: ``pm(nick, message)`` -- Send a pm to the given nick
* Action: ``pm_action(nick, message)`` -- Send a /me in a pm to the given nick

* Event: ``on_pm -> nick, message`` -- Raised when the bot recieves a PM
* Event: ``on_pm_action -> nick, message`` -- Raised when the bot recieves a /me
  in a PM.


