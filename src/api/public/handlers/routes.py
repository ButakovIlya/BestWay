# from io import BytesIO
# from typing import List, Optional

# from dependency_injector.wiring import Provide, inject
# from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
# from sqlalchemy import select, update
# from sqlalchemy.ext.asyncio import AsyncSession

# from api.admin.schemas import MiniRouteSchema, RoutePatchSchema, RouteRead
# from application.use_cases.common.dto import ModelPhotoDTO
# from application.use_cases.common.photo.delete import DeletePhotoUseCase
# from application.use_cases.routes.add_photos import RoutePhotosAddUseCase
# from application.use_cases.routes.avatar import RoutePhotoUpdateUseCase
# from application.use_cases.routes.create import RouteCreateUseCase
# from application.use_cases.routes.dto import RouteCreateDTO
# from application.use_cases.routes.enums import RouteGenerationMode as Mode
# from application.use_cases.tasks.route_generate import StartChatGPTRouteGenerateTaskUseCase
# from common.exceptions import APIException
# from config.containers import Container
# from domain.entities.enums import CityCategory, RouteType

# router = APIRouter()


# @router.post("/feed", status_code=status.HTTP_200_OK)
# @inject
# async def route_feed(
#     self,
#     request: Request,
#     survey_id: int,
#     mode: Mode = Mode.FULL,
#     use_case: StartChatGPTRouteGenerateTaskUseCase = Depends(
#         Provide[Container.start_route_chatgpt_generate_task]
#     ),
# ) -> str:
#     user_id: int = request.state.user.id

#     await use_case.execute(user_id, survey_id, mode)
#     return "Задача запущена"


# @router.post("/feed/{route_id}", status_code=status.HTTP_200_OK)
# @inject
# async def create_route(
#     self,
#     request: Request,
#     route_id: int,
#     mode: Mode = Mode.FULL,
#     use_case: StartChatGPTRouteGenerateTaskUseCase = Depends(
#         Provide[Container.start_route_chatgpt_generate_task]
#     ),
# ) -> str:
#     user_id: int = request.state.user.id

#     await use_case.execute(user_id, route_id, mode)
#     return "Задача запущена"
