from fastapi import Depends, status, Query
from typing import List
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.auth.jwt.auth_bearer import JWTBearer, JWTBearerOptional
from app.crud import (
    user as userCRUD,
    social_network as social_networkCRUD,
    blacklist as blacklistCRUD,
    manager as managerCRUD,
    account as accountCRUD,
)
from app.hepler.enum import Role, TypeAccount
from app.common.exception import CustomException
from app.model import Manager, Account, Business, User, Blacklist
from app.core.auth.jwt.auth_handler import token_manager


class UserManagerService:
    def get_current_user_optional(
        self, data: dict = Depends(JWTBearerOptional()), db: Session = Depends(get_db)
    ) -> Account:
        if data is None:
            return None

        try:
            return self.get_account_from_data(data, db)
        except CustomException:
            return None

    def get_current_user(
        self, data: dict = Depends(JWTBearer()), db: Session = Depends(get_db)
    ) -> Account:
        return self.get_account_from_data(data, db)

    def get_account_from_data(self, data: dict, db: Session) -> Account:
        token_decode = data["payload"]
        if token_decode["type_account"] != TypeAccount.NORMAL:
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED, msg="Unauthorized"
            )

        token = data["token"]
        if self.check_blacklist(db, token):
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED, msg="Token revoked"
            )

        id = token_decode["id"]
        if token_decode["role"] == Role.USER:
            user: User = userCRUD.get(db, id)
            if user is None:
                raise CustomException(
                    status_code=status.HTTP_404_NOT_FOUND, msg="User not found"
                )

            return user.account
        elif token_decode["role"] == Role.SOCIAL_NETWORK:
            social_network = social_networkCRUD.get(db, id)
            if social_network is None:
                raise CustomException(
                    status_code=status.HTTP_404_NOT_FOUND, msg="User not found"
                )
            user: User = social_network.user
            return user.account

    def get_current_user_verify(
        self, data: dict = Depends(JWTBearer()), db: Session = Depends(get_db)
    ) -> Account:
        account = self.get_current_user(data, db)
        user: User = account.user
        if not user.is_verified:
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED, msg="User not verified"
            )
        return account

    def get_current_user_or_business_verify(
        self, data: dict = Depends(JWTBearer()), db: Session = Depends(get_db)
    ):
        token_decode = data["payload"]
        if token_decode["type_account"] == TypeAccount.NORMAL:
            account = self.get_current_user(data, db)
            user: User = account.user
            if not user.is_verified:
                raise CustomException(
                    status_code=status.HTTP_401_UNAUTHORIZED, msg="User not verified"
                )
            return account
        elif token_decode["type_account"] == TypeAccount.BUSINESS:
            account = self.get_current_business(data, db)
            manager: Manager = account.manager
            business: Business = manager.business
            if not business.is_verified_email:
                raise CustomException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    msg="Business not verified",
                )
            return account

    def get_current_business_by_role(self, db, data: dict, allowed_roles: List[Role]):
        token_decode = data["payload"]
        if token_decode["type_account"] != TypeAccount.BUSINESS:
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN, msg="Not permission"
            )

        token = data["token"]
        if self.check_blacklist(db, token):
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED, msg="Token revoked"
            )

        id = token_decode["id"]
        role = token_decode["role"]
        if role not in allowed_roles:
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
            )
        manager = managerCRUD.get(db, id)
        if manager is None:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="User not found"
            )
        return manager.account

    def get_current_business_admin(
        self, data: dict = Depends(JWTBearer()), db: Session = Depends(get_db)
    ):
        return self.get_current_business_by_role(db, data, [Role.BUSINESS, Role.ADMIN])

    def get_current_business_admin_superuser(
        self, data: dict = Depends(JWTBearer()), db: Session = Depends(get_db)
    ):
        return self.get_current_business_by_role(
            db, data, [Role.BUSINESS, Role.ADMIN, Role.SUPER_USER]
        )

    def get_current_business(
        self, data: dict = Depends(JWTBearer()), db: Session = Depends(get_db)
    ) -> Account:
        return self.get_current_business_by_role(db, data, [Role.BUSINESS])

    def get_current_admin(
        self, data: dict = Depends(JWTBearer()), db: Session = Depends(get_db)
    ) -> Account:
        return self.get_current_business_by_role(
            db, data, [Role.ADMIN, Role.SUPER_USER]
        )

    def get_current_superuser(
        self, data: dict = Depends(JWTBearer()), db: Session = Depends(get_db)
    ) -> Account:
        return self.get_current_business_by_role(db, data, [Role.SUPER_USER])

    def check_permission_business(
        db: Session,
        current_user: Account,
        roles: List[Role],
        business_id: int = None,
    ) -> Role:
        if business_id:
            if current_user.role not in [Role.SUPER_USER, Role.ADMIN]:
                if current_user.id != business_id:
                    raise CustomException(
                        status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
                    )

                else:
                    return Role.BUSINESS
        else:
            if current_user.role not in roles:
                raise CustomException(
                    status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
                )

            elif current_user.role == Role.BUSINESS:
                return Role.BUSINESS

        return Role.ADMIN

    def check_blacklist(self, db: Session, token: str) -> Blacklist:
        return blacklistCRUD.get_by_token(db, token)

    async def get_current_account_verify_websocket(
        self,
        token: str = Query(...),
        db: Session = Depends(get_db),
    ) -> Account:
        payload = token_manager.decodeJWT(token)
        if not payload or self.check_blacklist(db, token):
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED, msg="Token revoked"
            )
        id = payload["id"]
        account = accountCRUD.get(db, id)
        if not account:
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED, msg="Account not found"
            )
        if account.role in [Role.USER, Role.SOCIAL_NETWORK]:
            user: User = account.user
            if not user.is_verified:
                raise CustomException(
                    status_code=status.HTTP_401_UNAUTHORIZED, msg="User not verified"
                )
        return account


user_manager_service = UserManagerService()
