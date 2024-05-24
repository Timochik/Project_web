import pytest
from sqlalchemy.orm import Session

from src.database.models import Hashtag
from src.repository.tags import get_or_create_tag


@pytest.mark.asyncio
async def test_get_or_create_tag(session: Session):

    tag_name = "test_tag"

    tag = session.query(Hashtag).filter(Hashtag.name == tag_name).first()
    assert tag is None

    tag = await get_or_create_tag(session, tag_name)
    assert tag is not None
    assert tag.name == tag_name

    tag_from_db = session.query(Hashtag).filter(Hashtag.name == tag_name).first()
    assert tag_from_db is not None
    assert tag_from_db.name == tag_name

    existing_tag = await get_or_create_tag(session, tag_name)
    assert existing_tag is not None
    assert existing_tag.id == tag.id
    assert existing_tag.name == tag.name
