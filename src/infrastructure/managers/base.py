from abc import ABC, abstractmethod
from io import BytesIO

from infrastructure.managers.enum import ModelType


class StorageManager(ABC):
    @abstractmethod
    def save_photo(self, filename: str, file: BytesIO, model_name: ModelType) -> str:
        """Сохраняет фото и возвращает относительный путь к нему"""
        pass

    @abstractmethod
    def get_resource_file(self, filepath: str) -> BytesIO:
        """Возвращает файл как BytesIO по относительному пути"""
        pass

    @abstractmethod
    def delete_resource_file_by_path(self, filepath: str) -> None:
        """Удаляет файл по относительному пути"""
        pass
