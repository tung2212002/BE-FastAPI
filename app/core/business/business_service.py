from fastapi import status
from sqlalchemy.orm import Session

from app.crud import (
    manager as managerCRUD,
    business as businessCRUD,
    account as accountCRUD,
)
from app.core.auth.jwt.auth_handler import token_manager
from app.core.business.business_helper import business_helper
from app.core.admin.admin_helper import admin_helper
from app.core.location.location_helper import location_helper
from app.core.file.file_helper import file_helper
from app.model import Account
from app.common.exception import CustomException
from app.common.response import CustomResponse
from app.schema.business import (
    BusinessCreateRequest,
    BusinessUpdateRequest,
    BusinessGetByEmailRequest,
    BusinessCreate,
    BusinessUpdate,
)
from app.schema.page import Pagination
from app.schema.account import AccountCreate, AccountUpdate
from app.schema.manager import ManagerCreate, ManagerUpdate
from app.schema.file import FileInfo


class BusinessService:
    async def get_me(self, db: Session, current_user: Account):
        response = None
        if current_user.manager.business is None:
            response = admin_helper.get_info_by_manager(db, current_user.manager)
        else:
            response = business_helper.get_info_by_account(db, current_user)
        return CustomResponse(data=response)

    async def get_by_email(self, db: Session, data: dict):
        business_data = BusinessGetByEmailRequest(**data)

        business = businessCRUD.get_by_email(db, business_data.email)
        if not business:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Business not found"
            )

        response = business_helper.get_info_by_business(db, business)

        return CustomResponse(data=response)

    async def get_by_id(self, db: Session, id: int):
        business = businessCRUD.get(db, id)
        if not business:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Business not found"
            )

        response = business_helper.get_info_by_business(db, business)

        return CustomResponse(data=response)

    async def get(self, db: Session, data: dict):
        page = Pagination(**data)

        managers = managerCRUD.get_multi(db, **page.model_dump())
        if not managers:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Businesss not found"
            )

        response = [
            business_helper.get_info_by_manager(db, manager) for manager in managers
        ]

        return CustomResponse(data=response)

    async def create(self, db: Session, data: dict):
        business_data = BusinessCreateRequest(**data)

        location_helper.check_valid_province_district(
            db, business_data.province_id, business_data.district_id
        )

        manager = managerCRUD.get_by_email(db, business_data.email)
        if manager:
            raise CustomException(
                status_code=status.HTTP_409_CONFLICT, msg="Email already registered"
            )

        avatar = business_data.avatar
        if avatar:
            file_info: FileInfo = await file_helper.upload_file(avatar)
            business_data.avatar = file_info.name

        account = accountCRUD.create(
            db, obj_in=AccountCreate(**business_data.model_dump())
        )
        manager = managerCRUD.create(
            db, obj_in=ManagerCreate(**business_data.model_dump(), id=account.id)
        )
        business = businessCRUD.create(
            db, obj_in=BusinessCreate(**business_data.model_dump(), id=account.id)
        )

        business_response = business_helper.get_info(db, account, manager, business)

        payload = token_manager.create_payload(account)
        access_token = token_manager.signJWT(payload)
        refresh_token = token_manager.signJWTRefreshToken(payload)

        return CustomResponse(
            status_code=status.HTTP_201_CREATED,
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": business_response,
            },
        )

    async def update(self, db: Session, data: dict, current_user: Account):
        business_data = BusinessUpdateRequest(**data)

        location_helper.check_valid_province_district(
            db, business_data.province_id, business_data.district_id
        )

        avatar = business_data.avatar
        if avatar:
            file_info: FileInfo = await file_helper.upload_file(avatar)
            business_data.avatar = file_info.name

        account = accountCRUD.update(
            db=db,
            db_obj=current_user,
            obj_in=AccountUpdate(**business_data.model_dump()),
        )
        manager = managerCRUD.update(
            db=db,
            db_obj=current_user.manager,
            obj_in=ManagerUpdate(**business_data.model_dump()),
        )
        business = businessCRUD.update(
            db=db,
            db_obj=current_user.manager.business,
            obj_in=BusinessUpdate(**business_data.model_dump()),
        )

        response = business_helper.get_info(db, account, manager, business)

        return CustomResponse(data=response)

    async def delete(self, db: Session, id: int, current_user: Account):
        if current_user is None or id != current_user.id:
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED, msg="Unauthorized"
            )

        accountCRUD.remove(db, current_user.id)

        return CustomResponse(msg="Business has been deleted successfully")

    async def set_user_active(self, db: Session, id: int, active: bool):
        if id is None:
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Id is required"
            )

        manager = managerCRUD.get(db, id)
        response = managerCRUD.set_active(db, manager, active)

        return CustomResponse(data=response)


business_service = BusinessService()
