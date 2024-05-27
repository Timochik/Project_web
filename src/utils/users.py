from aioconsole import ainput
from email_validator import validate_email

from src.repository.users import add_first_user_admin as add_admin


async def get_input(prompt: str, validate: callable = None):
        """
        The get_input function is a coroutine that prompts the user for input.
        It takes two arguments:
        prompt - The string to display to the user when asking for input.
        validate - A callable that will be passed the value entered by the user, and should raise an exception if it's invalid. If no exception is raised, then it's assumed to be valid.
        
        :param prompt: str: Prompt the user for input
        :param validate: callable: Validate the input
        :return: A coroutine object
        :doc-author: Trelent
        """
        while True:
            value = await ainput(prompt)
            if not value:
                print("The value cannot be empty. Please try again.")
                continue
            if validate:
                try:
                    validate(value)
                except Exception as e:
                    print(f"Bad value: {e}. Please try again.")
                    continue
            return value

def validate_passwords(password: str, password2: str):
        """
        The validate_passwords function takes two arguments, password and password2.
        It raises a ValueError if the passwords do not match.
        
        :param password: str: Specify the type of data that is expected to be passed into the function
        :param password2: str: Make sure that the password and password2 are the same
        :return: A valueerror if the passwords do not match
        :doc-author: Trelent
        """
        if password != password2:
            raise ValueError("Passwords do not match.")

async def add_first_user_admin() -> None:
    """
    The add_first_user_admin function is used to add the first user to the database.
    This function will be called when there are no users in the database, and it will
    prompt for a username, email address, and password. The email address must be valid
    and both passwords must match.
    
    :return: None, but it does add a user to the database
    :doc-author: Trelent
    """
    username = await get_input("Username: ")
    email = await get_input("Email: ", lambda v: validate_email(v))
    while True:
        password = await get_input("Password: ")
        password2 = await get_input("Password again: ")

        try:
            validate_passwords(password, password2)
            break
        except ValueError as e:
            print(e)
    
    await add_admin(username, email, password)