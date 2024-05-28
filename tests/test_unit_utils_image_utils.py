import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
import cloudinary
from fastapi import HTTPException, status
from src.utils.image_utils import transform_image
from src.database.models import User, Post


class TestImageUtils(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.service = MagicMock(spec=cloudinary)
        self.session = MagicMock(spec=Session)

    async def test_transform_image_access_denied(self):
        user = User()
        image = Post()
        description = "description"
        try:
            result = await transform_image(
                image_id=image.id,
                transform_params="transform_params",
                description=description,
                db=self.session,
                current_user=user,
                service=self.service
            )
            assert False
        except HTTPException as ex:
            result = ex
            assert True
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(result.detail, "Access denied")

    async def test_transform_image_image_not_found(self):
        user = User()
        image = Post()
        description = "description"
        self.session.query().filter().first.return_value = None
        try:
            result = await transform_image(
                image_id=image.id,
                transform_params="transform_params",
                description=description,
                db=self.session,
                current_user=user,
                service=self.service
            )
            assert False
        except HTTPException as ex:
            result = ex
            assert True
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(result.detail, "Image not found")

    async def test_transform_image(self):
        test_url = "https://res.cloudinary.com/abcdefghi/image/upload/v1234567890/project_name/a96e4ceb-54de-4e37-9520-0d0d3a3a31a6"
        responce_url = "https://res.cloudinary.com/abcdefghi/image/upload/transformations/v1234567890/project_name/a96e4ceb-54de-4e37-9520-0d0d3a3a31a6"
        user = User()
        image = Post(
            author_id = user.id,
            image_url = test_url
        )
        description = "description"
        self.session.query().filter().first.return_value = image
        self.service.CloudinaryImage().build_url.return_value = responce_url
        result = await transform_image(
            image_id=image.id,
            transform_params={"transform": "transform_params"},
            description=description,
            db=self.session,
            current_user=user,
            service=self.service
        )
        self.assertEqual(result.description, description)
        self.assertEqual(result.author, user.id)
        self.assertEqual(result.image_url, responce_url)
