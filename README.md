# Project_web "PhotoShare" 📷

<p align="center">
      <img src="https://i.imgur.com/JGVQtBS.png" width="1010">
</p>

<p align="center">
   <img src="https://img.shields.io/badge/Language-Python-9cf">
   <img src="https://img.shields.io/badge/FastAPI-0.111.0-brightgreen">
   <img src="https://img.shields.io/badge/SQLAlchemy-2.0.30-orange">
   <img src="https://img.shields.io/badge/Pytest-informational">
   <img src="https://img.shields.io/badge/License-MIT-yellow">
</p>


# PhotoShare ✨

**This project is an API for a photo gallery with the ability to add comments. Users can upload their photos, view photos from other users, and leave comments on them.**

## Installation 💻

1. Clone the repository:
    ```
    git clone https://github.com/Timochik/Project_web.git
    ```

2. Install dependencies:
    ```
    poetry install
    ```

3. Navigate to the directory:
    ```
    cd src
    ```

4. To work with the project, you will need an .env file with environment variables. Create it using the example file .env.example.py:
    ```
    POSTGRES_DB=postgres
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=secret_password
    POSTGRES_PORT=5432

    SQLALCHEMY_DATABASE_URL=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:${POSTGRES_PORT}/${POSTGRES_DB}

    SECRET_KEY=secret_key
    ALGORITHM=HS256

    MAIL_USERNAME=example@mail.com
    MAIL_PASSWORD=mail_password
    MAIL_FROM=example@mail.com
    MAIL_PORT=465
    MAIL_SERVER=smtp_server

    CLOUDINARY_NAME=name
    CLOUDINARY_API_KEY=api_key
    CLOUDINARY_API_SECRET=api_secret

    # folder name where project images will be stored on Cloudinary repository
    CLOUDINARY_FOLDER_NAME=project_web
    ```

5. Run the container:
    ```
    docker-compose up
    ```

6. Apply changes:
    ```
    alembic upgrade head
    ```

7. Run the server:
    ```
    cd ..
    python main.py
    ```
    
8. Run tests:  
    ```
    python -m pytest tests/filename -v
    ```

## Main Functionality

The application has the following main functionality:

* Authentication
    * JWT tokens
    * Administrator, moderator, and regular user roles
    * FastApi decorators are used to check the token and user role.

* Working with Photos 

    * The main functionality of working with photos is performed using HTTP requests (POST, DELETE, PUT, GET).
    * Unique tags for the entire application that can be added under a photo (up to 5 tags).
    * Users can perform basic actions with photos allowed by the Cloudinary service.
    * Links for viewing a photo as a URL and QR-code can be created and stored on the server.
    * Administrators can perform all CRUD operations with user photos.

* Commenting

    * Under each photo, there is a block with comments.
    * The creation and editing time of the comment is stored in the database.
    * Users can edit their comments but cannot delete them. Administrators and moderators can delete comments.

## Usage 

This project exposes 30+ endpoints through a REST API. To access these APIs, use any API client, such as Postman.

## Developers 

<div align="">
  <p>Scrum Master, developer: <a href="https://github.com/olhalialina">Olha lialina</a></p>
  <p>Team Lead, developer: <a href="https://github.com/Nyambevos">Ruslan Bilokoniuk</a></p>
  <p>Developer: <a href="https://github.com/andrii-trebukh">Andrii Trebukh</a></p>
  <p>Developer: <a href="https://github.com/Y3vh3n11">Yevhenii Vlasenko</a></p>
  <p>Developer: <a href="https://github.com/Timochik">Tymofii Svyrhun</a></p>
</div>

## License 

Project "PhotoShare" is distributed under the MIT license.
