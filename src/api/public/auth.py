from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request, status

from api.permissions.is_authenticated import is_authenticated
from application.use_cases.auth.check_code import VerifySmsCodeUseCase
from application.use_cases.auth.dto import (
    ChangePhoneSmsPayloadDTO,
    PhoneDTO,
    SmsPayloadDTO,
    SmsResponseDTO,
    TokenDTO,
)
from application.use_cases.auth.phone_change import VerifyPhoneChangeSmsCodeUseCase
from application.use_cases.auth.send_code import SendSmsCodeUseCase
from config.containers import Container
from domain.entities.user import User
from domain.validators.base import PhoneNumberValidator

router = APIRouter(tags=["Authorization"], prefix="/auth")


@router.get("/send-code", status_code=status.HTTP_200_OK)
@inject
async def send_code(
    phone: PhoneNumberValidator = Depends(),
    use_case: SendSmsCodeUseCase = Depends(Provide[Container.send_code_use_case]),
) -> SmsResponseDTO:
    """Эндпоинт для запроса кода по SMS."""
    return await use_case.execute(phone)


@router.post("/check-code", status_code=status.HTTP_200_OK)
@inject
async def check_code(
    data: SmsPayloadDTO,
    use_case: VerifySmsCodeUseCase = Depends(Provide[Container.verify_sms_code_use_case]),
) -> TokenDTO:
    """Эндпоинт для проверки кода из SMS."""
    return await use_case.execute(data)


@router.get("/send-phone-change-code", status_code=status.HTTP_200_OK)
@is_authenticated
@inject
async def send_phone_change_code(
    request: Request, use_case: SendSmsCodeUseCase = Depends(Provide[Container.send_code_use_case])
) -> SmsResponseDTO:
    """Эндпоинт для запроса кода на смену телефона по SMS."""
    user: User = request.state.user
    data = PhoneDTO(phone=user.phone)
    return await use_case.execute(data=data)


@router.post("/check-change-phone-code", status_code=status.HTTP_200_OK)
@is_authenticated
@inject
async def check_phone_change_code(
    request: Request,
    data: ChangePhoneSmsPayloadDTO,
    use_case: VerifyPhoneChangeSmsCodeUseCase = Depends(Provide[Container.change_number_sms_code_use_case]),
) -> TokenDTO:
    """Эндпоинт для проверки кода из SMS."""
    user: User = request.state.user
    data.phone = user.phone
    return await use_case.execute(data)
