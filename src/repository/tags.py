from sqlalchemy.orm import Session

from src.database.models import Hashtag


async def get_or_create_tag(db: Session, name: str):
    """
    Retrieves a tag from the database with the given name, or creates a new tag if it doesn't exist.

    Args:
        db (Session): The database session.\n
        name (str): The name of the tag.\n

    Returns:
        Tag: The retrieved or created tag.
    """
    tag = db.query(Hashtag).filter(Hashtag.name == name).first()
    if not tag:
        tag = Hashtag(name=name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
    return tag