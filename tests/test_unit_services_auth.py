import datetime
import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from passlib.context import CryptContext
from jose import jwt
from fastapi import HTTPException, status

from src.services.auth import auth_service
from src.database.models import User, UserRole
from src.services.auth import (
    is_admin,
    is_admin_or_moderator,
    check_is_admin_or_moderator
)


class TestAuth(unittest.IsolatedAsyncioTestCase):
    SECRET_KEY = "secret_key"
    ALGORITHM = "HS256"

    def setUp(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        auth_service.SECRET_KEY = self.SECRET_KEY
        auth_service.ALGORITHM = self.ALGORITHM
        self.session = MagicMock(spec=Session)

    def test_get_password_hash(self):
        password = "password"
        result = auth_service.get_password_hash(
            password=password
        )
        self.assertIsNotNone(result)

        result_verify = self.pwd_context.verify(
            secret=password,
            hash=result
        )
        self.assertTrue(result_verify)

    def test_verify_password(self):
        password = "password"
        hashed_password = self.pwd_context.hash(password)
        result = auth_service.verify_password(
            plain_password=password,
            hashed_password=hashed_password
        )
        self.assertTrue(result)

    def test_verify_password_wrong_password(self):
        password = "password"
        hashed_password = self.pwd_context.hash(password)
        wrong_password = "wrong_password"
        result = auth_service.verify_password(
            plain_password=wrong_password,
            hashed_password=hashed_password
        )
        self.assertFalse(result)

    async def test_create_access_token(self):
        email = "example@mail.com"
        data = {"sub": email}
        result = await auth_service.create_access_token(
            data=data
        )
        self.assertIsNotNone(result)

        decoded_token = jwt.decode(
            token=result,
            key=self.SECRET_KEY,
            algorithms=[self.ALGORITHM]
        )
        self.assertEqual(decoded_token.get("sub"), email)
        self.assertTrue(decoded_token.get("iat"))
        self.assertTrue(decoded_token.get("exp"))
        self.assertEqual(decoded_token.get("scope"), "access_token")

        result = await auth_service.create_access_token(
            data=data,
            expires_delta=900
        )
        self.assertIsNotNone(result)

        decoded_token = jwt.decode(
            token=result,
            key=self.SECRET_KEY,
            algorithms=[self.ALGORITHM]
        )
        self.assertEqual(decoded_token.get("sub"), email)
        self.assertTrue(decoded_token.get("iat"))
        self.assertTrue(decoded_token.get("exp"))
        self.assertEqual(decoded_token.get("scope"), "access_token")

    async def test_create_refresh_token(self):
        email = "example@mail.com"
        data = {"sub": email}
        result = await auth_service.create_refresh_token(
            data=data
        )
        self.assertIsNotNone(result)

        decoded_token = jwt.decode(
            token=result,
            key=self.SECRET_KEY,
            algorithms=[self.ALGORITHM]
        )
        self.assertEqual(decoded_token.get("sub"), email)
        self.assertTrue(decoded_token.get("iat"))
        self.assertTrue(decoded_token.get("exp"))
        self.assertEqual(decoded_token.get("scope"), "refresh_token")

        result = await auth_service.create_refresh_token(
            data=data,
            expires_delta=86400
        )
        self.assertIsNotNone(result)

        decoded_token = jwt.decode(
            token=result,
            key=self.SECRET_KEY,
            algorithms=[self.ALGORITHM]
        )
        self.assertEqual(decoded_token.get("sub"), email)
        self.assertTrue(decoded_token.get("iat"))
        self.assertTrue(decoded_token.get("exp"))
        self.assertEqual(decoded_token.get("scope"), "refresh_token")

    async def test_decode_refresh_token(self):
        email = "example@mail.com"
        scope = "refresh_token"
        data = {
            "sub": email,
            "scope": scope
        }
        token = jwt.encode(
            claims=data,
            key=self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )
        result = await auth_service.decode_refresh_token(
            refresh_token=token
        )
        self.assertEqual(result, email)

    async def test_decode_refresh_token_invalid_scope(self):
        email = "example@mail.com"
        invalid_scope = "invalid_scope"
        data = {
            "sub": email,
            "scope": invalid_scope
        }
        token = jwt.encode(
            claims=data,
            key=self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )
        try:
            result = await auth_service.decode_refresh_token(
                refresh_token=token
            )
            assert False
        except HTTPException as ex:
            result = ex
            assert True
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(result.detail, "Invalid scope for token")

    async def test_decode_refresh_token_invalid_token(self):
        invalid_token = "invalid_token"
        try:
            result = await auth_service.decode_refresh_token(
                refresh_token=invalid_token
            )
            assert False
        except HTTPException as ex:
            result = ex
            assert True
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(result.detail, "Could not validate credentials")

    async def test_get_current_user(self):
        email = "example@mail.com"
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)
        data = {
            "sub": email,
            "iat": datetime.datetime.now(datetime.UTC),
            "exp": expire,
            "scope": "access_token"
        }
        token = jwt.encode(
            claims=data,
            key=self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )

        user = User
        self.session.query().filter().first.return_value = user
        result = await auth_service.get_current_user(
            token=token,
            db=self.session
        )
        self.assertEqual(result, user)

    async def test_get_current_user_not_found(self):
        email = "example@mail.com"
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)
        data = {
            "sub": email,
            "iat": datetime.datetime.now(datetime.UTC),
            "exp": expire,
            "scope": "access_token"
        }
        token = jwt.encode(
            claims=data,
            key=self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )
        self.session.query().filter().first.return_value = None
        try:
            result = await auth_service.get_current_user(
                token=token,
                db=self.session
            )
            assert False
        except HTTPException as ex:
            result = ex
            assert True
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(result.detail, "Could not validate credentials")
        self.assertEqual(result.headers, {"WWW-Authenticate": "Bearer"})

    async def test_get_current_user_invalid_token(self):
        invalid_token = "invalid_token"
        try:
            result = await auth_service.get_current_user(
                token=invalid_token,
                db=self.session
            )
            assert False
        except HTTPException as ex:
            result = ex
            assert True
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(result.detail, "Could not validate credentials")
        self.assertEqual(result.headers, {"WWW-Authenticate": "Bearer"})

    async def test_get_current_user_invalid_scope(self):
        email = "example@mail.com"
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)
        invalid_data = {
            "sub": email,
            "iat": datetime.datetime.now(datetime.UTC),
            "exp": expire,
            "scope": "invalid_scope"
        }
        token = jwt.encode(
            claims=invalid_data,
            key=self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )
        try:
            result = await auth_service.get_current_user(
                token=token,
                db=self.session
            )
            assert False
        except HTTPException as ex:
            result = ex
            assert True
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(result.detail, "Could not validate credentials")
        self.assertEqual(result.headers, {"WWW-Authenticate": "Bearer"})

    def test_create_email_token(self):
        email = "example@mail.com"
        data = {"sub": email}
        result = auth_service.create_email_token(
            data=data
        )
        self.assertIsNotNone(result)

        decoded_token = jwt.decode(
            token=result,
            key=self.SECRET_KEY,
            algorithms=[self.ALGORITHM]
        )
        self.assertEqual(decoded_token.get("sub"), email)
        self.assertTrue(decoded_token.get("iat"))
        self.assertTrue(decoded_token.get("exp"))

    async def test_get_email_from_token(self):
        email = "example@mail.com"
        data = {
            "sub": email
        }
        token = jwt.encode(
            claims=data,
            key=self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )
        result = await auth_service.get_email_from_token(
            token=token
        )
        self.assertEqual(result, email)

        invalid_token = "invalid_token"
        try:
            result = await auth_service.get_email_from_token(
                token=invalid_token
            )
            assert False
        except HTTPException as ex:
            result = ex
            assert True
        self.assertEqual(
            result.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertEqual(result.detail, "Invalid token for email verification")

    async def test_is_admin_forbidden(self):
        user = User()
        try:
            result = await is_admin(current_user=user)
            assert False
        except HTTPException as ex:
            result = ex
            assert True
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(result.detail, "Not enough permissions")

    async def test_is_admin(self):
        user = User(role=UserRole.admin)
        result = await is_admin(current_user=user)
        self.assertEqual(result, user)

    async def test_is_admin_or_moderator_admin(self):
        user = User(role=UserRole.admin)
        result = await is_admin_or_moderator(current_user=user)
        self.assertEqual(result, user)

    async def test_is_admin_or_moderator_moderator(self):
        user = User(role=UserRole.moderator)
        result = await is_admin_or_moderator(current_user=user)
        self.assertEqual(result, user)

    async def test_is_admin_or_moderator_forbidden(self):
        user = User()
        try:
            result = await is_admin_or_moderator(current_user=user)
            assert False
        except HTTPException as ex:
            result = ex
            assert True
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(result.detail, "Not enough permissions")

    async def test_check_is_admin_or_moderator_false(self):
        user = User()
        result = await check_is_admin_or_moderator(current_user=user)
        self.assertFalse(result)

    async def test_check_is_admin_or_moderator_admin(self):
        user = User(role=UserRole.admin)
        result = await check_is_admin_or_moderator(current_user=user)
        self.assertTrue(result)

    async def test_check_is_admin_or_moderator_moderator(self):
        user = User(role=UserRole.moderator)
        result = await check_is_admin_or_moderator(current_user=user)
        self.assertTrue(result)
