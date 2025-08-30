from application.use_cases.base import UseCase
from application.use_cases.common.dto import ModelPhotoDTO, ObjectPhotoDTO
from application.use_cases.common.photo.photo import PhotoUpdateUseCase
from application.use_cases.common.photo.upload import UploadPhotosUseCase
from application.use_cases.posts.dto import CreatePostDTO, PostDTO
from common.exceptions import APIException
from domain.entities.post import Post
from infrastructure.managers.base import StorageManager
from infrastructure.managers.enum import ModelType
from infrastructure.uow.base import UnitOfWork


class PostCreateUseCase(UseCase):
    """
    Create post with photos.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        storage_manager: StorageManager,
        update_photo_use_case: PhotoUpdateUseCase,
    ) -> None:
        self._uow = uow
        self._storage_manager = storage_manager
        self._update_photo_use_case = update_photo_use_case

    async def execute(self, data: CreatePostDTO, user_id: int) -> PostDTO:
        async with self._uow(autocommit=True):
            print(data.model_dump())
            post: Post = await self._uow.posts.create(
                Post(**data.model_dump(exclude=["photo"]), author_id=user_id)
            )

        post = await self._set_photo(photo=data.photo, post=post)

        return PostDTO.model_validate(post)

    async def _set_photo(self, photo: ModelPhotoDTO, post: Post) -> Post:
        if not photo or not photo.photo:
            return post

        photo_data = ObjectPhotoDTO(
            photo=photo.photo,
            filename=photo.filename,
            filepath=post.photo,
            photo_field="photo",
            model_name=ModelType.POSTS,
        )
        filepath = await self._update_photo_use_case.execute(photo_data)
        post.photo = filepath
        async with self._uow(autocommit=True):
            await self._uow.posts.update(post)
            post: Post = await self._uow.posts.get_by_id(post.id)

        return post
