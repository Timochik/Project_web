import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch
import unittest
from unittest.mock import MagicMock, patch
from fastapi import File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
sys.path.append(os.path.abspath('..'))
from src.database.models import Hashtag, User, Post
from src.repository.images import (
    create_images_post,
    get_image,
    get_images,
    del_image,
    put_image,
)
from src.repository.qr_code import get_qr_code_by_url
from src.repository.tags import get_or_create_tag

class TestImages(unittest.IsolatedAsyncioTestCase):
    def setUp(self):

        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_images(self):
        images = [Post(), Post(), Post()]
        self.session.query().filter().all.return_value = images
        result = await get_images(current_user=self.user, db=self.session)

        self.assertEqual(result, images)

    async def test_get_image(self):
        image = Post()
        self.session.query().filter().first.return_value = image
        result = await get_image(image_id=1, current_user=self.user, db=self.session)
        self.assertEqual(result, image)

    async def test_get_image_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_image(image_id=1, current_user=self.user, db=self.session)
        self.assertEqual(result, None)
    
    async def test_del_image_true_author_id(self):
        image = Post()
        self.session.query().filter().first.return_value = image
        image.author_id=1
        result = await del_image(image_id=1, current_user=self.user, db=self.session)
        self.assertEqual(result, {'msg': 'Post deleted'})

class TestPutImage(unittest.IsolatedAsyncioTestCase):
    async def test_put_image(self):
        # Mock dependencies
        
        db = MagicMock(spec=Session)
        current_user = User(id=1)
        image = MagicMock(id=1, author_id=1, description='old_description', image_url='https://example.com/image')
        db.query.return_value.filter.return_value.first.return_value = image

        # Call the function
        new_image = await put_image(1, 'new_description', current_user, db)

        # Assert that the image was updated correctly
        self.assertEqual(new_image.id, 1)
        self.assertEqual(new_image.author_id, 1)
        self.assertEqual(new_image.description, 'new_description')
        self.assertEqual(new_image.image_url, 'https://example.com/image')

        # Assert that the old image was deleted
        db.delete.assert_called_once_with(image)

        # Assert that the new image was added
        db.add.assert_called_once_with(new_image)

        # Assert that the database was committed
        db.commit.assert_called_once()

        # Assert that the new image was refreshed
        db.refresh.assert_called_once_with(new_image)

    async def test_put_image_with_permission_denied(self):
        # Mock dependencies
        db = MagicMock(spec=Session)
        current_user = MagicMock(id=2)
        image = MagicMock(id=1, author_id=1, description='old_description', image_url='https://example.com/image')
        db.query.return_value.filter.return_value.first.return_value = image

        # Call the function
        with self.assertRaises(HTTPException) as context:
            await put_image(1, 'new_description', current_user, db)

        # Assert that the HTTPException was raised with the correct status code and detail
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(context.exception.detail, "Permission denied")

if __name__ == '__main__':
    unittest.main()

