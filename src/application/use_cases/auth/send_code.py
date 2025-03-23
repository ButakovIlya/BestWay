from fastapi import HTTPException
from infrastructure.managers.sms_client import SmsClient
from application.use_cases.base import UseCase
from application.use_cases.auth.dto import PhoneDTO, SmsPayloadDTO, SmsResponseDTO


class SendSmsCodeUseCase(UseCase):
    """Use Case для отправки SMS с кодом пользователю."""

    def __init__(self, sms_client: SmsClient):
        self._sms_manager = sms_client

    async def execute(self, data: PhoneDTO) -> SmsResponseDTO:
        """Генерирует код и отправляет SMS с кодом."""
        try:
            # Генерируем или получаем уже кешированный код
            code = await self._sms_manager.get_code(data.phone)
            payload = SmsPayloadDTO(phone=data.phone, code=code)  # Создаем DTO
            # Отправляем код по SMS
            await self._sms_manager.send_sms(payload)

            return SmsResponseDTO(message=code)

        except HTTPException as exc:
            raise exc  # Пробрасываем стандартные ошибки

        # except Exception as e:
        #     raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
