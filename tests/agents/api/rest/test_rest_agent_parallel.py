import unittest
from unittest.mock import patch, Mock

from kiwi.agents.api.rest.rest_agent import RestAgent


class TestRestAgentParallel(unittest.TestCase):
    def setUp(self):
        # Create a minimal RestAgentConfig-like object
        from kiwi.agents.api.rest.rest_agent_config import RestAgentConfig
        self.agent_config = RestAgentConfig(
            name="TestRestAgentParallel",
            base_url="http://localhost:8090/",
            connection_timeout=5000,
            verify=True
        )
        self.rest_agent = RestAgent(self.agent_config)

    @patch.object(RestAgent, 'send_request')
    def test_send_requests_parallel_ordering(self, mock_send_request):
        # Prepare three mock responses with different return delays to simulate out-of-order completion
        resp_a = Mock()
        resp_a.status_code = 200
        resp_b = Mock()
        resp_b.status_code = 201
        resp_c = Mock()
        resp_c.status_code = 202

        def side_effect(method, endpoint, headers=None, params=None, body=None):
            import time
            # reverse sleep order so responses complete out of order
            if endpoint == '/a':
                time.sleep(0.2)
                return resp_a
            if endpoint == '/b':
                time.sleep(0.1)
                return resp_b
            if endpoint == '/c':
                time.sleep(0.01)
                return resp_c
            return None

        mock_send_request.side_effect = side_effect

        requests_data = ['/a', '/b', '/c']
        results = self.rest_agent.send_requests_parallel('GET', requests_data, max_workers=3)

        # Ensure ordering is preserved (results[0] corresponds to '/a', etc.)
        self.assertEqual(len(results), 3)
        self.assertIs(results[0], resp_a)
        self.assertIs(results[1], resp_b)
        self.assertIs(results[2], resp_c)

    @patch.object(RestAgent, 'send_request')
    def test_send_requests_parallel_handles_exceptions(self, mock_send_request):
        # One request raises an exception, others return responses
        resp_ok = Mock()
        resp_ok.status_code = 200

        def side_effect(method, endpoint, headers=None, params=None, body=None):
            if endpoint == '/fail':
                raise RuntimeError('simulated failure')
            return resp_ok

        mock_send_request.side_effect = side_effect

        requests_data = ['/ok1', '/fail', '/ok2']
        results = self.rest_agent.send_requests_parallel('POST', requests_data, max_workers=2)

        self.assertEqual(len(results), 3)
        self.assertIs(results[0], resp_ok)
        # failed request should result in None
        self.assertIsNone(results[1])
        self.assertIs(results[2], resp_ok)


if __name__ == '__main__':
    unittest.main()

