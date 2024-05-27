from libgravatar import Gravatar
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.database.db import get_db
from src.database.models import User
from src.schemas import UserModel, UserUpdate
from src.services.auth import auth_service


async def get_user_by_email(email: str, db: Session) -> User:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user with that email. If no such user exists, it raises a
    HTTPException.
    
    :param email: str: Pass in the email of the user we want to get
    :param db: Session: Pass in the database session to the function
    :return: The first user found with the email address provided
    :doc-author: Trelent
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function creates a new user in the database.
    It takes a UserModel object as input and returns a User object.
    
    
    :param body: UserModel: Pass the user data from the request body to create_user
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    The update_token function updates the refresh token for a user.
    
    :param user: User: Specify the type of the user parameter
    :param token: str | None: Pass the token to the function
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user.refresh_token = token
    db.commit()

async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes an email and a database session as arguments.
    It then queries the database for the user with that email address, sets their confirmed field to True,
    and commits those changes to the database.
    
    :param email: str: Get the email address of the user
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function takes an email and a url as arguments.
    It then uses the get_user_by_email function to retrieve the user from the database.
    The avatar attribute of that user is set to be equal to the url argument, and then 
    the db session is committed.
    
    :param email: Get the user from the database
    :param url: str: Specify the type of data that is being passed to the function
    :param db: Session: Pass the database session to the function
    :return: The updated user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def get_user_by_username(username: str, db: Session) -> User:
    """
    The get_user_by_username function takes in a username and a database session,
    and returns the user with that username. If no such user exists, it raises a
    HTTPException.
    
    :param username: str: Specify the username of the user we want to get
    :param db: Session: Pass in the database session
    :return: The user with the given username
    :doc-author: Trelent
    """
    return db.query(User).filter(User.username == username).first()


async def update_user(user_id: int, user_update: UserUpdate, db: Session) -> User:
    """
    The update_user function updates a user's information in the database.
    
    :param user_id: int: Specify which user to update
    :param user_update: UserUpdate: Pass in the new user data
    :param db: Session: Access the database
    :return: The updated user object, or none if the user was not found
    :doc-author: Trelent
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    user.username = user_update.username
    user.email = user_update.email
    user.avatar = user_update.avatar
    db.commit()
    db.refresh(user)
    return user

async def get_user_by_id(user_id: int, db: Session = next(get_db())) -> User:
    """
    The get_user_by_id function takes in a user_id and a database session,
        and returns the User object associated with that id. If no such user exists,
        it raises an HTTPException.
    
    :param user_id: int: Specify the type of data that is expected to be passed into the function
    :param db: Session: Pass the database session to the function
    :return: A query object
    :doc-author: Trelent
    """
    return db.query(User).filter(User.id == user_id).first()

async def add_first_user_admin(username: str, email: str, password: str, db: Session = next(get_db())) -> None:
    """
    The add_first_user_admin function is used to add the first user to the database.
        This function will only work if there are no users in the database.
        The function takes a username, email, and password as arguments and adds them to a new User object. 
        The new User object is then added to the database using SQLAlchemy's db session.
    
    :param username: str: Pass in the username of the user
    :param email: str: Specify the email address of the user
    :param password: str: Get the password from the user
    :param db: Session: Pass in the database session
    :return: None
    :doc-author: Trelent
    """
    hash_password = auth_service.get_password_hash(password)
    new_user = User(id=1, username=username, email=email, password=hash_password, confirmed=True, role="admin", avatar=None)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)