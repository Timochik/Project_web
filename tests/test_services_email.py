# test_email.py
import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from pydantic import EmailStr

from src.services.email import send_email, conf
from fastapi_mail.errors import ConnectionErrors


class TestSendEmail(unittest.TestCase):

    @patch('email.auth_service.create_email_token')
    @patch('email.FastMail')
    def test_send_email_success(self, MockFastMail, mock_create_email_token):
        mock_create_email_token.return_value = 'mock_token'
        mock_fastmail_instance = MockFastMail.return_value
        mock_fastmail_instance.send_message = AsyncMock()

        #Following instructions should be replaced with an actual data
        email = EmailStr('test@example.com')
        username = 'testuser'
        host = 'localhost'

        # Run the send_email function
        async def run_test():
            await send_email(email, username, host)
        
        import asyncio
        asyncio.run(run_test())

        # Check if token was created
        mock_create_email_token.assert_called_once_with({'sub': email})

        # Check if email was sent with correct parameters
        mock_fastmail_instance.send_message.assert_awaited_once()
        sent_message = mock_fastmail_instance.send_message.call_args[0][0]
        
        self.assertEqual(sent_message.subject, "Confirm your email ")
        self.assertEqual(sent_message.recipients, [email])
        self.assertEqual(sent_message.template_body['host'], host)
        self.assertEqual(sent_message.template_body['username'], username)
        self.assertEqual(sent_message.template_body['token'], 'mock_token')

    @patch('email.auth_service.create_email_token')
    @patch('email.FastMail')
    def test_send_email_connection_error(self, MockFastMail, mock_create_email_token):
        mock_create_email_token.return_value = 'mock_token'
        mock_fastmail_instance = MockFastMail.return_value
        mock_fastmail_instance.send_message = AsyncMock(side_effect=ConnectionErrors('Connection error'))

        email = EmailStr('test@example.com')
        username = 'testuser'
        host = 'localhost'

        # Run the send_email function
        async def run_test():
            await send_email(email, username, host)

        import asyncio
        asyncio.run(run_test())

        # Check if token was created
        mock_create_email_token.assert_called_once_with({'sub': email})

        # Check if ConnectionErrors was raised
        mock_fastmail_instance.send_message.assert_awaited_once()
        sent_message = mock_fastmail_instance.send_message.call_args[0][0]
        
        self.assertEqual(sent_message.subject, "Confirm your email ")
        self.assertEqual(sent_message.recipients, [email])
        self.assertEqual(sent_message.template_body['host'], host)
        self.assertEqual(sent_message.template_body['username'], username)
        self.assertEqual(sent_message.template_body['token'], 'mock_token')

if __name__ == '__main__':
    unittest.main()
