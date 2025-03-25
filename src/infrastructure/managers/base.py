from abc import ABC, abstractmethod
from io import BytesIO


class StorageManager(ABC):
    @abstractmethod
    def save_user_photo(
        self,
        filename: str,
        file: BytesIO,
    ) -> str:
        pass

