from typing import Annotated, Optional
from fastapi import UploadFile, File, Form
from pydantic import EmailStr, StringConstraints


class UserUpdateForm:
    def __init__(
        self,
        first_name: Optional[Annotated[str, StringConstraints(max_length=255)]] = Form(None),
        email: Optional[EmailStr] = Form(None),
        phone: Optional[Annotated[
            str,
            StringConstraints(
                strip_whitespace=True,
                pattern=r'^\d{11}$'  # формат: 11 цифр, например: 79991234567
            )
        ]] = Form(None),
        photo: Optional[UploadFile] = File(None)
    ):
        self.first_name = first_name
        self.email = email
        self.phone = phone
        self.photo = photo
