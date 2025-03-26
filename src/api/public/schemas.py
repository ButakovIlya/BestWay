from typing import Annotated, Optional
from fastapi import UploadFile, File, Form
from pydantic import EmailStr, StringConstraints


class UserUpdateForm:
    def __init__(
        self,
        first_name: Optional[Annotated[str, StringConstraints(max_length=255)]] = Form(None),
        last_name: Optional[Annotated[str, StringConstraints(max_length=255)]] = Form(None),
        middle_name: Optional[Annotated[str, StringConstraints(max_length=255)]] = Form(None),
        email: Optional[EmailStr] = Form(None),
        phone: Optional[Annotated[
            str,
            StringConstraints(strip_whitespace=True)
        ]] = Form(None),
        photo: Optional[UploadFile] = File(None),
        remove_photo: Optional[bool] = Form(False)
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.email = email
        self.phone = phone
        self.photo = photo
        self.remove_photo = remove_photo
