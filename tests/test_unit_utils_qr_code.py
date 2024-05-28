import unittest
from unittest.mock import MagicMock
import cloudinary
from src.utils.qr_code import get_qr_code_by_url, delete_qr_code_by_url


class TestQrCode(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.service = MagicMock(spec=cloudinary)

    async def test_get_qr_code_by_url(self):
        test_url = "http://www.google.com"
        responce_url = "https://res.cloudinary.com/abcdefghi/image/upload/v1234567890/project_name/qrcode/a96e4ceb-54de-4e37-9520-0d0d3a3a31a6"
        self.service.CloudinaryImage().build_url.return_value = responce_url
        result = await get_qr_code_by_url(url=test_url, service=self.service)
        self.assertEqual(result, responce_url)

    async def test_delete_qr_code_by_url(self):
        test_url = "https://res.cloudinary.com/abcdefghi/image/upload/v1234567890/project_name/qrcode/a96e4ceb-54de-4e37-9520-0d0d3a3a31a6"
        self.service.uploader.destroy.return_value = {"result": "ok"}
        result = await delete_qr_code_by_url(
            url=test_url,
            service=self.service
        )
        self.assertIsNone(result)

        self.service.uploader.destroy.return_value = {"result": "not found"}
        try:
            result = await delete_qr_code_by_url(
                url=test_url,
                service=self.service
            )
            assert False
        except FileNotFoundError:
            assert True
