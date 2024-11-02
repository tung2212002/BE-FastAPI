from fastapi import status
from sqlalchemy.orm import Session

from app.crud import user as userCRUD, account as accountCRUD
from app.schema.user import (
    UserGetRequest,
    UserCreateRequest,
    UserCreate,
    UserUpdateRequest,
    UserUpdate,
)
from app.schema.account import AccountCreate, AccountUpdate
from app.schema.page import Pagination
from app.schema.file import FileInfo
from app.core.auth.jwt.auth_handler import token_manager
from app.core.user.user_helper import user_helper
from app.core.file.file_helper import file_helper
from app.model import Account
from app.common.exception import CustomException
from app.common.response import CustomResponse


class UserService:
    async def get_me(self, db: Session, current_user: Account):
        if current_user is None:
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED, msg="Unauthorized"
            )

        user = current_user.user
        response = user_helper.get_info(db, current_user, user)

        return CustomResponse(data=response)

    async def get_by_email(self, db: Session, data: dict):
        user_data = UserGetRequest(**data)

        user = userCRUD.get_by_email(db, user_data.email)
        if not user:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="User not found"
            )
        resposne = user_helper.get_info_by_user(db, user)

        return CustomResponse(data=resposne)

    async def get_by_id(self, db: Session, id: int):
        user = userCRUD.get(db, id)
        if not user:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="User not found"
            )

        response = user_helper.get_info_by_user(db, user)

        return CustomResponse(data=response)

    async def get(self, db: Session, data: dict):
        page = Pagination(**data)

        users = userCRUD.get_multi(db, **page.model_dump())
        if not users:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Users not found"
            )

        response = [user_helper.get_info_by_user(db, user) for user in users]

        return CustomResponse(data=response)

    async def create(self, db: Session, data: dict):
        user_data = UserCreateRequest(**data)

        user = userCRUD.get_by_email(db, user_data.email)
        if user:
            raise CustomException(
                status_code=status.HTTP_409_CONFLICT, msg="Email already registered"
            )
        avatar = user_data.avatar
        if avatar:
            file_info: FileInfo = await file_helper.upload_file(avatar)
            user_data.avatar = file_info.name

        account = accountCRUD.create(db, obj_in=AccountCreate(**user_data.model_dump()))
        user = userCRUD.create(
            db, obj_in=UserCreate(**user_data.model_dump(), id=account.id)
        )

        user_reponse = user_helper.get_info(db, account, user)

        payload = token_manager.create_payload(account)
        access_token = token_manager.signJWT(payload)
        refresh_token = token_manager.signJWTRefreshToken(payload)

        return CustomResponse(
            status_code=status.HTTP_201_CREATED,
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user_reponse,
            },
        )

    async def update(self, db: Session, data: dict, current_user: Account):
        user_data = UserUpdateRequest(**data)

        avatar = user_data.avatar
        if avatar:
            file_info: FileInfo = await file_helper.upload_file(avatar)
            user_data.avatar = file_info.name

        account_data = AccountUpdate(**user_data.model_dump())
        account = accountCRUD.update(db, obj_in=account_data, db_obj=current_user)
        user_data = UserUpdate(**user_data.model_dump())
        user = userCRUD.update(db, obj_in=user_data, db_obj=current_user.user)

        response = user_helper.get_info(db, account, user)

        return CustomResponse(data=response)

    async def delete(self, db: Session, id: int, current_user: Account):
        if id != current_user.id:
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED, msg="Unauthorized"
            )

        if id is None:
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Id is required"
            )

        accountCRUD.remove(db, id=id)

        return CustomResponse(msg="User has been deleted successfully")


user_service = UserService()
