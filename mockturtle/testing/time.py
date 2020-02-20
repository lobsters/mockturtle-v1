#!/usr/bin/env python3


class MockTime():
    """Mocks time for unit testing purposes.

    The purpose of this class is to simulate time in such a way that is
    predictable and that passage of time is instantenous. The clock starts at
    zero. Sleeps will return immediately and move the clock forward
    appropriately.

    Use this class to mock time in a specific module along the lines of:

        import module

        def MyTest(unittest.TestCase):
            def setUp(self):
                self.clock = TimeMock()

            @mock.patch("module.time.sleep")
            @mock.patch("module.time.time")
            def test_module(self, mock_time, mock_sleep):
                mock_time.side_effect = self.clock.time
                mock_sleep.side_effect = self.clock.sleep
                module.function_to_be_tested()
    """
    def __init__(self):
        self._fake_time = 0.0

    def sleep(self, duration: float) -> None:
        """Fakes the time.sleep() function."""
        self._fake_time += duration

    def time(self) -> float:
        """Fakes the time.time() function."""
        return self._fake_time
