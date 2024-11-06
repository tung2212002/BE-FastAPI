from fastapi import status
from sqlalchemy.orm import Session

from app.crud import company as companyCRUD
from app.schema.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyCreateRequest,
    CompanyUpdateRequest,
    CompanyPagination,
)
from app.schema.page import Pagination
from app.schema.file import FileInfo
from app.hepler.enum import Role, FolderBucket
from app.core.auth.business_auth_helper import business_auth_helper
from app.core.field.field_helper import field_helper
from app.core.file.file_helper import file_helper
from app.core.company.company_helper import company_helper
from app.model import Manager, Account, Business
from app.common.exception import CustomException
from app.common.response import CustomResponse


class CompanyService:
    async def get(self, db: Session, data: dict, current_user: Account = None):
        page = Pagination(**data)

        if (
            data.get("business_id")
            and current_user
            and current_user.role == Role.BUSINESS
        ):
            if data.get("business_id") != current_user.id:
                raise CustomException(
                    status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
                )

            company = companyCRUD.get_by_business_id(db, current_user.id)
            response = company_helper.get_info(db, company)

            return CustomResponse(data=response)

        companies = companyCRUD.get_multi(db, **page.model_dump())
        response = []
        if data.get("fields"):
            response = company_helper.get_list_info(db, companies, detail=True)
        else:
            response = company_helper.get_list_info(db, companies)

        return CustomResponse(data=response)

    async def search(self, db: Session, data: dict):
        page = CompanyPagination(**data)

        total, companies = companyCRUD.search_multi(db, **page.model_dump())
        response = company_helper.get_list_info(db, companies, detail=True)

        return CustomResponse(
            data={
                "total": total,
                "companies": response,
            }
        )

    async def get_by_id(self, db: Session, company_id: int):
        company = companyCRUD.get(db, company_id)
        if not company:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Company not found"
            )

        response = company_helper.get_info(db, company)

        return CustomResponse(data=response)

    async def create(self, db: Session, data: dict, current_user: Account):
        business = current_user.business
        if not business:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Business not found"
            )

        business_auth_helper.verified_level(business, 2)
        if companyCRUD.get_by_business_id(db=db, business_id=current_user.id):
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
            )

        if companyCRUD.get_company_by_tax_code(db, data.get("tax_code")):
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Tax code already exists"
            )

        if companyCRUD.get_company_by_email(db, data.get("email")):
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Email already exists"
            )

        company_data = CompanyCreateRequest(**data)

        fields = company_data.fields
        if fields:
            field_helper.check_list_valid(db, fields)

        logo = company_data.logo
        if logo:
            file_info: FileInfo = await file_helper.upload_file(logo, FolderBucket.LOGO)
            company_data.logo = file_info.url

        if current_user.role == Role.BUSINESS:
            company_data = {
                **company_data.model_dump(),
                "business_id": current_user.id,
            }
        obj_in = CompanyCreate(**company_data.model_dump())
        company = companyCRUD.create(db, obj_in=obj_in)
        if fields:
            field_helper.create_with_company_id(db, company.id, fields)
        response = company_helper.get_private_info(db, company)

        return CustomResponse(status_code=status.HTTP_201_CREATED, data=response)

    async def update(self, db: Session, data: dict, current_user: Account):
        company_id = data.get("company_id")
        company = companyCRUD.get(db, company_id)
        if not company:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Company not found"
            )

        if company.business_id != current_user.id:
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
            )

        company_data = CompanyUpdateRequest(**data)

        logo = company_data.logo
        new_fields = company_data.fields
        if new_fields:
            field_helper.check_list_valid(db, new_fields)
        if logo:
            file_info: FileInfo = await file_helper.upload_file(logo, FolderBucket.LOGO)
            company_data.logo = file_info.url

        obj_in = CompanyUpdate(**company_data.model_dump())
        company = companyCRUD.update(db, db_obj=company, obj_in=obj_in)
        field_helper.update_with_company_id(db, company.id, new_fields)

        response = company_helper.get_private_info(db, company)

        return CustomResponse(data=response)

    async def delete(self, db: Session, company_id: int, current_user: Account):
        company = companyCRUD.get(db, company_id)
        manager: Manager = current_user.manager
        business: Business = manager.business

        if not company:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Company not found"
            )

        if company.business_id != business.id:
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
            )

        response = companyCRUD.remove(db, id=company_id)

        return CustomResponse(data=response)


company_service = CompanyService()
