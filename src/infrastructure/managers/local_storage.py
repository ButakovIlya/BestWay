from datetime import UTC, datetime
from io import BytesIO
from os import makedirs
from pathlib import Path

from config.settings import Settings
from infrastructure.managers.base import StorageManager
from infrastructure.managers.enum import ModelType


class LocalStorageManager(StorageManager):
    STORAGE_ROOT_NAME: str = "storage"
    MEDIA_ROOT_NAME: str = "media"
    DEFAULT_PHOTO_EXTENSION: str = "jpg"
    FILENAME_TIMESTAMP_FORMAT: str = "%d-%m-%Y_%H-%M-%S"
    ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._max_file_size_bytes = settings.storage.max_file_size_mb * 1024 * 1024

    def save_user_photo(
        self,
        filename: str,
        file: BytesIO,
    ) -> str:
        self._validate_file(filename, file)

        new_filename = self._generate_filename(ModelType.USERS, filename)
        filepath = self._get_media_filepath(ModelType.USERS, new_filename)
        self._save_file(filepath, file)

        relative_path = filepath.relative_to(self._settings.storage.storage_path)
        return self.normalize_file_path(relative_path)

    def _validate_file(self, filename: str, file: BytesIO) -> None:
        extension = Path(filename).suffix.lower()
        if extension not in self.ALLOWED_PHOTO_EXTENSIONS:
            raise ValueError(
                f"Недопустимый формат файла: {extension}. Разрешены: {', '.join(self.ALLOWED_PHOTO_EXTENSIONS)}"
            )

        file_size = len(file.getvalue())
        if file_size > self._max_file_size_bytes:
            raise ValueError(
                f"Размер файла превышает допустимый лимит в {self._settings.storage.max_file_size_mb}MB"
            )

    def get_resource_file(self, filepath: str) -> BytesIO:
        return BytesIO((self._settings.storage.storage_path / filepath).read_bytes())

    def delete_resource_file_by_path(self, filepath: str) -> None:
        full_path = self._settings.storage.storage_path / filepath
        full_path.unlink(missing_ok=True)

    def _save_file(self, new_filepath: Path, file: BytesIO) -> None:
        makedirs(new_filepath.parent, exist_ok=True)
        with open(new_filepath, "wb") as new_file:
            new_file.write(file.getvalue())

    def _generate_filename(
        self, model_name: ModelType, filename: str | None
    ) -> str:
        timestamp = datetime.now(UTC).strftime(self.FILENAME_TIMESTAMP_FORMAT)
        extension = (
            Path(filename).suffix if filename else self.DEFAULT_PHOTO_EXTENSION
        )
        return f"{model_name.value}_{timestamp}{extension}"

    def _get_media_filepath(self, directory: str, filename: str) -> Path:
        return self._settings.storage.media_path / directory / filename

    @staticmethod
    def normalize_file_path(path: Path) -> str:
        return str(path).replace("\\", "/")
