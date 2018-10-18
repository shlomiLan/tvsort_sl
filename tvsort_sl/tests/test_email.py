from unittest import mock

import pytest
from python_http_client import UnauthorizedError

from tvsort_sl import messages


@mock.patch('tvsort_sl.messages.send_email', return_value={'status_code': 202})
def test_send_email(_):
    res = messages.send_email(content='This is test content', subject='Test subject')
    assert res.get('status_code') == 202


def test_no_api_key():
    with mock.patch.dict('os.environ', {'SENDGRID_API_KEY': ''}):
        with pytest.raises(UnauthorizedError):
            messages.send_email(content='This is test content', subject='Test subject')
