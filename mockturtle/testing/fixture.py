#!/usr/bin/env python3

import unittest
import re
from typing import Any, Tuple
from types import ModuleType

import sopel.bot
import sopel.tests.factories
import sopel.trigger
from sopel.loader import clean_module

from mockturtle.testing.time import MockTime
from mockturtle.testing.config import MockConfig


class TestFixture(unittest.TestCase):
    """The test fixture for validating invite.py."""

    # TODO(phil): Allow testers to customize the channel names and nicks
    # involved here.

    def setUp(self, module: ModuleType) -> None:
        """Sets up the test."""
        self.time = MockTime()
        self.config = MockConfig()
        botfactory = sopel.tests.factories.BotFactory()
        self.bot = botfactory.preloaded(self.config)

        self.callables, self.jobs, self.shutdowns, self.urls = clean_module(
            module, self.bot.config)

    def tearDown(self) -> None:
        """Tears down the test."""
        self.config.cleanup()

    def _match(self, _: Any) -> None:
        """Helper for mocking sopel triggers."""
        # I think we're simulating a regex search result here. Not sure yet.
        # Returning None seems to make sopel happy so do that for now.
        return None

    def trigger_event(self, event_name: str) -> Tuple[int, bytes]:
        """Triggers an event registered via @sopel.module.event(...).

        If you have the following in your module:

            @sopel.module.event("JOIN")
            def announce_joins(bot, trigger):
                bot.reply("Welcome, %s" % trigger.nick)

        then you can trigger that in your unit test by calling this function
        with "JOIN" as an argument. Note that if you have multiple function
        trigger on the same event, calling this function will invoke all the
        relevant functions.

        Args:
            event_name: The name of the event to simulate. E.g. "JOIN".

        Returns:
            A tuple containing the number of functions that were triggered and
            the raw output of the bot.
        """
        # TODO(phil): Can we de-duplicate this and trigger_rule?
        full_message = ':hostmask %s #channel user :Some text' % event_name
        pretrigger = sopel.trigger.PreTrigger(self.bot.nick, full_message)
        trigger = sopel.trigger.Trigger(self.bot.config, pretrigger,
                                        self._match)
        wrapper = sopel.bot.SopelWrapper(self.bot, trigger)
        num_events = 0

        for function in self.callables:
            if not hasattr(function, "event"):
                continue

            for event in function.event:
                if event == event_name:
                    function(wrapper, trigger)
                    num_events += 1

        return (num_events, b"".join(wrapper.backend.message_sent))

    def trigger_rule(self, message: str) -> Tuple[int, bytes]:
        """Triggers a rule registered via @sopel.module.rule(...).

        If you have the following in your module:

            @sopel.module.rule(".* foobar .*")
            def reply_to_foobar(bot, trigger):
                bot.reply("Someone said 'foobar'!")

        then you can trigger that in your unit test by calling this function
        with "pretending to say foobar here" as an argument. Note that if you
        have multiple function with rules then all relevant ones will get
        triggered.

        Args:
            message: The message to mock being sent on the channel.

        Returns:
            A tuple containing the number of functions that were triggered and
            the raw output of the bot.
        """
        full_message = ':hostmask PRIVMSG #channel :%s' % message
        pretrigger = sopel.trigger.PreTrigger(self.bot.nick, full_message)
        trigger = sopel.trigger.Trigger(self.bot.config, pretrigger,
                                        self._match)
        wrapper = sopel.bot.SopelWrapper(self.bot, trigger)
        num_rules = 0

        for function in self.callables:
            if not hasattr(function, "rule"):
                continue

            for event in function.rule:
                match = re.match(event, message)
                if match:
                    function(wrapper, trigger)
                    num_rules += 1

        return (num_rules, b"".join(wrapper.backend.message_sent))
