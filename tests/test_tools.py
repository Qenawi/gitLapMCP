import json
import unittest
from unittest import mock

from mcp_server.api import api


class GitLabToolTests(unittest.TestCase):
    def setUp(self):
        self.patcher = mock.patch('requests.request')
        self.mock_request = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def _mock_response(self, data):
        response = mock.Mock()
        response.raise_for_status.return_value = None
        response.text = json.dumps(data)
        response.json.return_value = data
        self.mock_request.return_value = response

    def test_list_merge_requests_on_branch(self):
        self._mock_response([{"id": 1}])
        result = api.list_merge_requests_on_branch(None, '1', 'main')
        self.assertEqual(result, [{"id": 1}])


if __name__ == '__main__':
    unittest.main()
