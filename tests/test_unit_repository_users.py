import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas import UserModel, UserUpdate
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
    get_user_by_username,
    update_user,
    get_user_by_id,
    add_first_user_admin
)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_user_by_email(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(
            email="example@mail.com",
            db=self.session
        )
        self.assertEqual(result, user)

    @patch("src.repository.users.Gravatar")
    async def test_create_user(self, GravatarMock):
        GravatarMock().get_image.return_value = "avatar_url"
        body = UserModel(
            username="user_name",
            email="example@mail.com",
            password="password"
        )
        result = await create_user(body=body, db=self.session)
        self.assertTrue(hasattr(result, "id"))
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "created_at"))
        self.assertIsNone(result.refresh_token)
        self.assertFalse(result.confirmed)
        self.assertIsNotNone(result.avatar)

    @patch(
        "src.repository.users.Gravatar",
        side_effect=ValueError("some error")
    )
    async def test_create_user_exception(self, GravatarMock):
        body = UserModel(
            username="user_name",
            email="example@mail.com",
            password="password"
        )
        result = await create_user(body=body, db=self.session)
        self.assertTrue(hasattr(result, "id"))
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "created_at"))
        self.assertIsNone(result.refresh_token)
        self.assertFalse(result.confirmed)
        self.assertIsNone(result.avatar)

    async def test_update_token(self):
        user = User()
        token = "token"
        await update_token(user=user, token=token, db=self.session)
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        user = User()
        email = "example@mail.com"
        self.session.query().filter().first.return_value = user
        await confirmed_email(email=email, db=self.session)
        self.session.commit.assert_called_once()

    async def test_update_avatar(self):
        user = User()
        email = "example@mail.com"
        url = "avatar_url"
        self.session.query().filter().first.return_value = user
        result = await update_avatar(
            email=email,
            url=url,
            db=self.session
        )
        self.session.commit.assert_called_once()
        self.assertEqual(result.avatar, url)

    async def test_get_user_by_username(self):
        user = User()
        username = "username"
        self.session.query().filter().first.return_value = user
        result = await get_user_by_username(username=username, db=self.session)
        self.assertEqual(result, user)

    async def test_update_user(self):
        user = User()
        user_update = UserUpdate(
            username="username",
            email="example@mail.com",
            avatar="avtar.url"
        )
        self.session.query().filter().first.return_value = user
        result = await update_user(
            user_id=1,
            user_update=user_update,
            db=self.session
        )
        self.session.commit.assert_called_once()
        self.assertEqual(result.username, user_update.username)
        self.assertEqual(result.email, user_update.email)
        self.assertEqual(result.avatar, user_update.avatar)

    async def test_update_user_not_found(self):
        user_update = UserUpdate(
            username="username",
            email="example@mail.com",
            avatar="avtar.url"
        )
        self.session.query().filter().first.return_value = None
        result = await update_user(
            user_id=1,
            user_update=user_update,
            db=self.session
        )
        self.assertIsNone(result)

    async def test_get_user_by_id(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await get_user_by_id(user_id=1, db=self.session)
        self.assertEqual(result, user)

    async def test_add_first_user_admin(self):
        await add_first_user_admin(
            username="username",
            email="example@mail.com",
            password="password",
            db=self.session
        )
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
