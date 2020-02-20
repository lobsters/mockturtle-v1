#!/usr/bin/env python3

import os
from tempfile import TemporaryDirectory

import sopel.config

# A minimal config.
DEFAULT_CONFIG = """
[core]
owner = Bar
nick = Sopel
enable = coretasks
"""


class MockConfig(sopel.config.Config):
    """Mocks a sopel config.

    Ideally we'd use upstream's sopel.tests.pytest_plugins.configfactory
    instead. However, as the name implies, it requires pytest. For simplicity
    let's use the unittest module. That means re-implementing a couple of
    things here.

    The intended use case is to instantiate one of these at the beginning of
    each test. Make sure to call cleanup() at the end of each test.
    """
    def __init__(self):
        self._tmpdir = TemporaryDirectory()
        self._tmpfile = os.path.join(self._tmpdir.name, "test.cfg")
        with open(self._tmpfile, "w") as file:
            file.write(DEFAULT_CONFIG)
        super().__init__(self._tmpfile)

    def cleanup(self) -> None:
        """Cleans up the temporary files for the mocked confic.

        Call this function at the end of each test.
        """
        self._tmpdir.cleanup()
