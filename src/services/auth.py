from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, UserRole
from src.repository import users as repository_users
from src.conf.config import settings

class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and hashed
        password as arguments. It then uses the CryptContext instance to verify that
        the plain-text password matches the hashed version. If it does, it returns True;
        otherwise, False.
        
        :param self: Represent the instance of the class
        :param plain_password: Pass in the password that is entered by the user
        :param hashed_password: Check if the password entered by the user is correct
        :return: True if the password is correct, and false otherwise
        :doc-author: Trelent
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password and returns the hashed version of it.
        The hashing algorithm is defined in the settings file.
        
        :param self: Represent the instance of the class
        :param password: str: Specify the password that will be hashed
        :return: A hash of the password
        :doc-author: Trelent
        """
        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates a new access token.
            The function takes in the following parameters:
                data (dict): A dictionary containing the claims to be encoded into the JWT.
                expires_delta (Optional[float]): An optional parameter that specifies how long until this token expires, in seconds. If not specified, it defaults to 15 minutes.
        
        :param self: Refer to the current object
        :param data: dict: Pass the data to be encoded in the jwt token
        :param expires_delta: Optional[float]: Set the expiration time of the access token
        :return: A token that is encoded with the user's information
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token for the user.
            The function takes in two arguments: data and expires_delta.
            Data is a dictionary containing the user's id, username, email address, and password hash.
            Expires_delta is an optional argument that specifies how long the refresh token will be valid for.
        
        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded into the token
        :param expires_delta: Optional[float]: Set the expiration time of the refresh token
        :return: A string that contains the encoded refresh token
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function takes a refresh token and decodes it.
                    If the scope is 'refresh_token', then the email address of the user is returned.
                    Otherwise, an HTTPException with status code 401 (UNAUTHORIZED) is raised.
        
        :param self: Represent the instance of the class
        :param refresh_token: str: Pass in the refresh token that is sent to the server
        :return: The email of the user who is trying to refresh their token
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        The get_current_user function is a dependency that will be called by FastAPI to
            retrieve the current user for each request. It uses the OAuth2PasswordBearer
            to validate and decode the JWT token in the Authorization header of each request.
        
        :param self: Refer to the class itself
        :param token: str: Get the token from the request header
        :param db: Session: Get the database session
        :return: The user object corresponding to the email in the jwt payload
        :doc-author: Trelent
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception
        
        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user
    
    def create_email_token(self, data: dict):
        """
        The create_email_token function creates a token that is used to verify the user's email address.
        The token contains the following information:
        - iat (issued at): The time when the token was created.
        - exp (expiration): The time when this token will expire and no longer be valid. This is set to 7 days from creation date by default, but can be changed in settings.py if desired.
        
        :param self: Make the function a method of the class
        :param data: dict: Create a dictionary of the data that will be encoded into the token
        :return: A token that is encoded using the jwt library
        :doc-author: Trelent
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
    
    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
        If the token is invalid, it raises an HTTPException.
        
        :param self: Represent the instance of the class
        :param token: str: Pass in the token that was sent to the user's email address
        :return: The email address of the user if the token is valid
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                          detail="Invalid token for email verification")


auth_service = Auth()


async def is_admin(current_user: User =  Depends(auth_service.get_current_user)) -> User:
        """
        The is_admin function is a dependency that checks if the user has admin permissions.
        If not, it raises an HTTPException with status code 403 (Forbidden).
        
        
        :param current_user: User: Get the current user from the auth_service
        :return: A user object, which is the same as the current_user parameter
        :doc-author: Trelent
        """
        if current_user.role != UserRole.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return current_user
        
async def is_admin_or_moderator(current_user: User =  Depends(auth_service.get_current_user)) -> User:
    """
    The is_admin_or_moderator function is a dependency that checks if the current user has admin or moderator permissions.
    If not, it raises an HTTPException with status code 403 (Forbidden).
    
    
    :param current_user: User: Get the current user from the auth_service
    :return: The current user if the role is admin or moderator
    :doc-author: Trelent
    """
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user

async def check_is_admin_or_moderator(current_user: User) -> bool:
    """
    The check_is_admin_or_moderator function checks if the current user is an admin or moderator.
        If so, it returns True. Otherwise, it raises a HTTPException with status code 403 (Forbidden).
    
    
    :param current_user: User: Pass the current user into the function
    :return: True if the user is an admin or moderator
    :doc-author: Trelent
    """
    if current_user.role in ["admin", "moderator"]:
        return True
