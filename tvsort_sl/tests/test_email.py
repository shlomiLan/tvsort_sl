from unittest import mock

import pytest
from python_http_client import UnauthorizedError

from tvsort_sl import messages


@mock.patch('tvsort_sl.messages.SendGridAPIClient')
def test_send_email(mock_sendgrid_client):
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_sendgrid_client.return_value.send.return_value = mock_response

    res = messages.send_email(content='This is test content', subject='Test subject')
    assert res.status_code in (200, 202)


@mock.patch('tvsort_sl.messages.SendGridAPIClient')
def test_send_email_wtih_sandbox(mock_sendgrid_client):
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_sendgrid_client.return_value.send.return_value = mock_response

    with mock.patch.dict('os.environ', {'SAND_BOX': 'true'}):
        res = messages.send_email(content='This is test content', subject='Test subject')
        assert res.status_code in (200, 202)



def test_no_api_key():
    with mock.patch.dict('os.environ', {'SENDGRID_API_KEY': ''}):
        with pytest.raises(UnauthorizedError):
            messages.send_email(content='This is test content', subject='Test subject')
