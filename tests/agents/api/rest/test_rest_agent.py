import unittest
from unittest.mock import patch, Mock

from kiwi.agents.api.rest.rest_agent import RestAgent
from kiwi.utils.json_utils import JsonUtils


class TestRestAgent(unittest.TestCase):
    def setUp(self):
        # Create a RestAgentConfig with test parameters
        from kiwi.agents.api.rest.rest_agent_config import RestAgentConfig
        self.agent_config = RestAgentConfig(
            name="TestRestAgent",
            base_url="http://localhost:8090/",
            connection_timeout=5000,
            verify=True
        )
        self.rest_agent = RestAgent(self.agent_config)

    @patch.object(RestAgent, '_make_request')
    def test_send_request(self, mock_make_request):
        # Mock the response of _make_request for a GET request
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = {
            "countryCode": "CHN",
            "population": 9996300
        }
        mock_make_request.return_value = mock_response
        # Test sending a GET request to a known endpoint
        result = self.rest_agent.send_request(method="GET", endpoint="city/Shanghai")
        self.assertEqual(result.status_code, 200)
        country_code = JsonUtils.get_value(result.content, "countryCode")
        population = JsonUtils.get_value(result.content, "population")
        self.assertEqual(country_code, "CHN")
        self.assertEqual(population, 9996300)

    @patch.object(RestAgent, '_make_request')
    def test_send_request_connection_error(self, mock_make_request):
        # Mock _make_request to raise a ConnectionError
        from requests.exceptions import ConnectionError
        mock_make_request.side_effect = ConnectionError("Connection failed")
        with self.assertRaises(ConnectionError):
            self.rest_agent.send_request(method="GET", endpoint="city/Shanghai")

    @patch.object(RestAgent, '_make_request')
    def test_send_request_timeout_error(self, mock_make_request):
        # Mock _make_request to raise a Timeout
        from requests.exceptions import Timeout
        mock_make_request.side_effect = Timeout("Request timed out")
        with self.assertRaises(Timeout):
            self.rest_agent.send_request(method="GET", endpoint="city/Shanghai")

    @patch.object(RestAgent, '_make_request')
    def test_send_request_404_error(self, mock_make_request):
        # Mock the response for a 404 error
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 404
        mock_response.content.return_value = {"error": "Not Found"}
        mock_make_request.return_value = mock_response
        result = self.rest_agent.send_request(method="GET", endpoint="city/NonExistent")
        self.assertEqual(result.status_code, 404)
        error_message = JsonUtils.get_value(result.content(), "error")
        self.assertEqual(error_message, "Not Found")

    @patch.object(RestAgent, '_make_request')
    def test_send_request_invalid_json(self, mock_make_request):
        # Mock the response with invalid JSON
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.content.side_effect = ValueError("Invalid JSON")
        mock_make_request.return_value = mock_response
        result = self.rest_agent.send_request(method="GET", endpoint="city/Shanghai")
        with self.assertRaises(ValueError):
            result.content()


if __name__ == '__main__':
    unittest.main()
