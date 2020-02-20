#!/usr/bin/env python3

import os
import unittest
from unittest import mock
import logging
import sys

from mockturtle.testing.fixture import TestFixture

# Import the module under test.
from mockturtle import invite


class TestInvite(TestFixture):
    """The test fixture for validating invite.py."""
    def setUp(self) -> None:
        super().setUp(invite)

    @mock.patch("mockturtle.invite.time.time")
    def test_successful_hint(self, mock_time):
        """Validates that users joining and asking for invites get a hint."""
        mock_time.side_effect = self.time.time

        (num_events, output) = self.trigger_event("JOIN")
        self.assertEqual(num_events, 1)
        self.assertEqual(output, b"")

        (num_rules, output) = self.trigger_rule("Can I get an invite?")
        self.assertEqual(num_rules, 1)
        self.assertRegex(
            output, rb".*: If you would like an invite to lobste.rs, "
            rb"please look at the chat FAQ first\. .*")

    @mock.patch("mockturtle.invite.time.time")
    def test_no_hint_after_timeout(self, mock_time):
        """Validates that only recent users get the FAQ hint."""
        mock_time.side_effect = self.time.time

        (num_events, output) = self.trigger_event("JOIN")
        self.assertEqual(num_events, 1)
        self.assertEqual(output, b"")

        # Wait over an hour.
        self.time.sleep(4000)

        # Expect silence.
        (num_rules, output) = self.trigger_rule("Can I get an invite?")
        self.assertEqual(num_rules, 1)
        self.assertEqual(output, b"")

    @mock.patch("mockturtle.invite.time.time")
    def test_no_hint_without_join(self, mock_time):
        """Validates that without a user's join time the bot stays quiet."""
        mock_time.side_effect = self.time.time

        # Expect silence.
        (num_rules, output) = self.trigger_rule("Can I get an invite?")
        self.assertEqual(num_rules, 1)
        self.assertEqual(output, b"")


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    unittest.main()
