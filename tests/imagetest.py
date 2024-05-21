import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
sys.path.append(os.path.abspath('..'))
from src.database.models import User, Post
from src.repository.images import (
    create_images_post,
    get_image,
    get_images,
    del_image,
    put_image,
)

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


if __name__ == '__main__':
    unittest.main()