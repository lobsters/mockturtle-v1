#!/usr/bin/env python
# vi: set fileencoding=utf-8

import calendar
import sopel
import sopel.bot as bot
from sopel.logger import get_logger
import time

logger = get_logger(__name__)

@sopel.module.rule(r'.*[Ii]nvite.*')
@sopel.module.rate(900)
def invite(bot, trigger):
    """To new members that are looking for an invitation"""
    joinedTime = bot.db.get_nick_value(trigger.nick,
                                       'join_channel_' + trigger.sender)
    if joinedTime is None:
        logger.error("no join time for nick %s in channel %s",
                     trigger.nick, trigger.sender)
        return

    now = time.time()
    diff = now - joinedTime
    if diff >= 3600:
        logger.info("join time %f for nick %s in channel %s exceeds limit",
                    joinedTime, trigger.nick, trigger.sender)
        return

    bot.reply("If you would like an invite to lobste.rs, please look "
              "at the chat FAQ first. Thank you. https://lobste.rs/chat "
              "(I am a bot. (v).v.(v))")


@sopel.module.event('JOIN')
@sopel.module.priority('low')
@sopel.module.unblockable
def note(bot, trigger):
    if trigger.is_privmsg:
        logger.debug("Ignoring private JOIN message.")
    else:
        now = time.time()
        logger.info("nick %s joined channel %s at %f",
                    trigger.nick, trigger.sender, now)
        bot.db.set_nick_value(trigger.nick,
                              'join_channel_' + trigger.sender,
                              time.time())
        logger.debug("Noting JOIN time for user %s in channel %s" % (trigger.nick, trigger.sender))


if __name__ == "__main__":
    from sopel.test_tools import run_example_tests
    run_example_tests(__file__)
