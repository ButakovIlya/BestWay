from io import BytesIO
from typing import List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.admin.schemas import PostPatch, PostPut, PostRead
from application.use_cases.common.dto import ModelPhotoDTO
from application.use_cases.common.list import ModelObjectListUseCase
from application.use_cases.common.retrieve import ModelObjectRetrieveUseCase
from application.use_cases.posts.create import PostCreateUseCase
from application.use_cases.posts.dto import CreatePostDTO
from common.exceptions import APIException
from config.containers import Container
from domain.entities.enums import ModelType
from domain.validators.dto import PaginatedResponse
from infrastructure.models.alchemy.posts import Post

router = APIRouter()


@router.get("/all", response_model=PaginatedResponse[PostRead], status_code=status.HTTP_200_OK)
@inject
async def list_posts(
    request: Request,
    # filters: PlacesFiltersDTO = Depends(),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    use_case: ModelObjectListUseCase = Depends(Provide[Container.object_list_use_case]),
) -> PaginatedResponse[PostRead]:
    """Получить список постов"""
    return await use_case.execute(
        request=request,
        model_type=ModelType.POSTS,
        page=page,
        page_size=page_size,
        ObjectDTO=PostRead,
    )


@router.get("/all/{post_id}", response_model=PostRead, status_code=status.HTTP_200_OK)
@inject
async def retrieve_post(
    post_id: int,
    use_case: ModelObjectRetrieveUseCase = Depends(Provide[Container.object_retrieve_use_case]),
) -> PostRead:
    """Получить пост по ID"""
    return await use_case.execute(
        obj_id=post_id,
        model_type=ModelType.POSTS,
        ObjectDTO=PostRead,
    )


@router.post("/", status_code=status.HTTP_200_OK)
@inject
async def create(
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    route_id: int = Form(...),
    photo: Optional[UploadFile] = File(None),
    photos: Optional[List[UploadFile]] = File(None),
    use_case: PostCreateUseCase = Depends(Provide[Container.create_post_use_case]),
):
    photo_data = ModelPhotoDTO(
        photo=BytesIO(await photo.read()) if photo else None,
        filename=photo.filename if photo else None,
    )
    photos_data = (
        [
            ModelPhotoDTO(
                photo=BytesIO(await file.read()) if file else None,
                filename=file.filename if file else None,
            )
            for file in photos
        ]
        if photos
        else []
    )

    data = CreatePostDTO(
        title=title,
        description=description,
        route_id=route_id,
        photo=photo_data,
        photos=photos_data,
    )
    user_id: int = request.state.user.id
    return await use_case.execute(data=data, user_id=user_id)


@router.patch("/{item_id}", response_model=PostRead)
@inject
async def patch(
    item_id: int,
    item_data: PostPatch,
    session: AsyncSession = Depends(Provide[Container.db.session]),
) -> PostRead:
    try:
        values = item_data.model_dump(exclude_unset=True)
        if not values:
            raise APIException(code=400, message="Нет данных для обновления")

        stmt = (
            update(Post)
            .where(Post.id == item_id)
            .values(**values)
            .execution_options(synchronize_session="fetch")
        )
        await session.execute(stmt)
        await session.commit()

        result = await session.execute(
            select(Post)
            .where(Post.id == item_id)
            .options(
                selectinload(Post.author),
                selectinload(Post.route),
            )
        )
        db_obj = result.scalar_one_or_none()

        if not db_obj:
            raise APIException(code=404, message="Item not found")

        return db_obj
    finally:
        await session.close()


@router.put("/{item_id}", response_model=PostRead)
@inject
async def put(
    item_id: int,
    item_data: PostPut,
    session: AsyncSession = Depends(Provide[Container.db.session]),
) -> PostRead:
    validated = PostPut(**item_data.model_dump(exclude_unset=False))

    stmt = (
        update(Post)
        .where(Post.id == item_id)
        .values(**validated.model_dump(exclude_unset=False))
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(stmt)
    await session.commit()

    result = await session.execute(
        select(Post)
        .where(Post.id == item_id)
        .options(
            selectinload(Post.author),
            selectinload(Post.route),
        )
    )
    db_obj = result.scalar_one_or_none()

    if not db_obj:
        raise APIException(code=404, message="Item not found")

    return db_obj
