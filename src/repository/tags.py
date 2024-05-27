from sqlalchemy.orm import Session

from src.database.models import Hashtag


async def get_or_create_tag(db: Session, name: str):
    """
    The get_or_create_tag function retrieves a tag from the database with the given name, or creates a new tag if it doesn't exist.
    
    :param db: Session: Pass the database session to the function
    :param name: str: Specify the name of the tag
    :return: A tag
    :doc-author: Trelent
    """
    tag = db.query(Hashtag).filter(Hashtag.name == name).first()
    if not tag:
        tag = Hashtag(name=name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
    return tag