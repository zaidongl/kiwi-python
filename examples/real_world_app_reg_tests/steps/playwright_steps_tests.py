import unittest
import playwright_steps

class PlaywrightStepsTests(unittest.TestCase):
    def test_open_page(self):
        playwright_steps.open_page("BrowserAgent", "/")

    def test_on_page(self):
        playwright_steps.open_page("BrowserAgent", "/")
        playwright_steps.is_on_page("BrowserAgent", "Login-Page")


if __name__ == '__main__':
    unittest.main()
