from unittest import mock

import pytest
from python_http_client import UnauthorizedError

from tvsort_sl import messages


def test_send_email():
    res = messages.send_email(content='This is test content', subject='Test subject')
    assert res.status_code in (200, 202)


def test_no_api_key():
    with mock.patch.dict('os.environ', {'SENDGRID_API_KEY': ''}):
        with pytest.raises(UnauthorizedError):
            messages.send_email(content='This is test content', subject='Test subject')
