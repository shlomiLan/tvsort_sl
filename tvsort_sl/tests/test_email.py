from unittest import mock

import pytest
from python_http_client import UnauthorizedError

from tvsort_sl import messages


def test_send_email():
    with pytest.raises(UnauthorizedError):
        messages.send_email(content='This is test content', subject='Test subject')


def test_no_api_key():
    with mock.patch.dict('os.environ', {'SENDGRID_API_KEY': ''}):
        with pytest.raises(UnauthorizedError):
            messages.send_email(content='This is test content', subject='Test subject')
