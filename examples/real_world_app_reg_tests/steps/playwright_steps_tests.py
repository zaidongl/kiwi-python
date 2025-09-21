import unittest
from playwright_steps import PlaywrightSteps

class PlaywrightStepsTests(unittest.TestCase):
    def test_open_page(self):
        steps = PlaywrightSteps()
        steps.open_page("BrowserAgent", "/")

    def test_on_page(self):
        steps = PlaywrightSteps()
        steps.open_page("BrowserAgent", "/")
        steps.is_on_page("BrowserAgent", "Login-Page")


if __name__ == '__main__':
    unittest.main()
