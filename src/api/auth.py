from application.use_cases.auth.check_code import VerifySmsCodeUseCase
from application.use_cases.auth.send_code import SendSmsCodeUseCase
from application.use_cases.auth.dto import TokenDTO, SmsPayloadDTO
from fastapi import status

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request

from config.containers import Container
from domain.validators.base import PhoneNumberValidator

router = APIRouter(tags=["Authorization"], prefix="/auth")



@router.get("/send-code", status_code=status.HTTP_200_OK)
@inject
async def send_code(
    request: Request,
    phone: PhoneNumberValidator = Depends(),
    use_case: SendSmsCodeUseCase = Depends(Provide[Container.send_code_use_case])
):
    """Эндпоинт для запроса кода по SMS."""
    return await use_case.execute(phone)


@router.post("/check-code", response_model=TokenDTO, status_code=status.HTTP_200_OK)
@inject
async def check_code(
    data: SmsPayloadDTO,
    use_case: VerifySmsCodeUseCase = Depends(Provide[Container.verify_sms_code_use_case])
):
    """Эндпоинт для проверки кода из SMS."""
    return await use_case.execute(data)
