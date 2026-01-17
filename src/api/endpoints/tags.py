from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from ..api.dependencies import get_db_session_dependency
from ..infrastructure.database.repositories.tag_repository import TagRepository
from ..domain.models.task import TagCreate, TagUpdate, TagResponse


router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=TagResponse)
async def create_tag(
    tag: TagCreate,
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = 1  # In a real app, this would come from authentication
):
    """Create a new tag"""
    tag_repository = TagRepository(db_session)
    # Check if tag already exists for this user
    existing_tag = await tag_repository.get_tag_by_name_and_user(tag.name, user_id)
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag already exists for this user")
    
    created_tag = await tag_repository.create_tag_for_user(tag.name, user_id, tag.color)
    return TagResponse.from_orm(created_tag)


@router.get("/", response_model=List[TagResponse])
async def get_tags(
    db_session: AsyncSession = Depends(get_db_session_dependency),
    user_id: int = 1  # In a real app, this would come from authentication
):
    """Get all tags for a user"""
    tag_repository = TagRepository(db_session)
    tags = await tag_repository.get_tags_by_user(user_id)
    return [TagResponse.from_orm(tag) for tag in tags]