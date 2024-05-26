from aioconsole import ainput
from email_validator import validate_email, EmailNotValidError

from src.repository.users import add_first_user_admin as add_admin

async def get_input(prompt: str, validate: callable = None):
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
        if password != password2:
            raise ValueError("Passwords do not match.")

async def add_first_user_admin() -> None:
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