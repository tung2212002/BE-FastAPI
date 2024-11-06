from fastapi import status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import requests
from fastapi import Request

from app.core import constant
from app.crud import (
    user as userCRUD,
    social_network as social_networkCRUD,
    blacklist as blacklistCRUD,
    account as accountCRUD,
)
from app.schema.auth import AuthLogin, AuthChangePassword
from app.schema.account import AccountCreate
from app.schema.user import UserCreate
from app.schema.social_network import (
    SocialNetworkCreate,
)
from app.core.auth.jwt.auth_handler import token_manager
from app.hepler.enum import Provider
from app.model import User, Account
from app.common.exception import CustomException
from app.common.response import CustomResponse
from app.core.user.user_helper import user_helper
from app.hepler.enum import Provider, Role, TypeAccount


class UserAuthService:
    async def authenticate(self, db: Session, data: dict):
        user_data = AuthLogin(**data)

        user = userCRUD.get_by_email(db, user_data.email)
        if not user:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="User not found"
            )

        if not userCRUD.authenticate(
            db, email=user_data.email, password=user_data.password
        ):
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED, msg="Incorrect password"
            )

        account = user.account
        payload = token_manager.create_payload(account)
        access_token = token_manager.signJWT(payload)
        refresh_token = token_manager.signJWTRefreshToken(payload)

        user = user_helper.get_info(db, account, user)

        return CustomResponse(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user,
            }
        )

    async def authenticate_google(self, db: Session, data: dict):
        token = data.get("access_token")
        if token is None:
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Token is required"
            )

        url = f"{constant.GOOGLE_GET_USER_INFO_URL}{token}"
        response = requests.get(url)
        if response.status_code != 200:
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Invalid token"
            )

        data = response.json()
        email = data.get("email")
        if email is None:
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Invalid token"
            )

        account = None
        user = None
        social_network = social_networkCRUD.get_by_email(db, email, Provider.GOOGLE)
        if not social_network:
            user = userCRUD.get_by_email(db, email)
            if user:
                userCRUD.set_verify(db, user, True)
                social_network_data = SocialNetworkCreate(
                    type=Provider.GOOGLE,
                    social_id=data.get("id"),
                    avatar=data.get("picture"),
                    email=email,
                    access_token=token,
                    id=user.id,
                )
                social_network = social_networkCRUD.create(
                    db=db, obj_in=social_network_data
                )
                account = user.account
            else:
                account_data = AccountCreate(
                    full_name=data.get("name"),
                    avatar=data.get("picture"),
                    role=Role.SOCIAL_NETWORK,
                    type_account=TypeAccount.NORMAL,
                )
                account = accountCRUD.create(db=db, obj_in=account_data)

                user_data = UserCreate(id=account.id, phone_number=None, email=email)
                user = userCRUD.create(db=db, obj_in=user_data)
                social_network_data = SocialNetworkCreate(
                    type=Provider.GOOGLE,
                    social_id=data.get("id"),
                    avatar=data.get("picture"),
                    email=email,
                    access_token=token,
                    id=account.id,
                )
                social_network = social_networkCRUD.create(
                    db=db, obj_in=social_network_data
                )
        else:
            user = userCRUD.get_by_email(db, email)
            account = user.account
        payload = token_manager.create_payload(account)
        access_token = token_manager.signJWT(payload)
        refresh_token = token_manager.signJWTRefreshToken(payload)

        user = user_helper.get_info(db, account, user)
        return CustomResponse(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user,
            }
        )

    async def check_verify_token(self, db: Session, token: str):
        token_decode = token_manager.decodeJWT(token)
        exp = token_decode["exp"]
        now = datetime.now(timezone.utc)
        if now > datetime.fromtimestamp(exp, timezone.utc):
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED, msg="Token expired"
            )

        check_blacklist = blacklistCRUD.get_by_token(db, token)
        if check_blacklist:
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED, msg="Token revoked"
            )

        return CustomResponse(data=token_decode)

    async def refresh_token(self, db: Session, request: Request):
        refresh_token = request.headers.get("Authorization").split(" ")[1]
        token_decode = token_manager.decodeJWT(refresh_token)
        if token_decode["type"] != "refresh_token":
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED, msg="Invalid token"
            )

        id = token_decode["id"]
        user = userCRUD.get(db, id)
        if user is None:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="User not found"
            )

        account = user.account
        payload = token_manager.create_payload(account)
        access_token = token_manager.signJWT(payload)

        user = user_helper.get_info(db, account, user)

        return CustomResponse(data={"access_token": access_token, "user": user})

    async def logout(self, db: Session, request: Request):
        token = request.headers.get("Authorization").split(" ")[1]
        blacklistCRUD.create(db=db, token=token)

        return CustomResponse(msg="Logout successfully")

    async def change_password(self, db: Session, data: dict, current_user: Account):
        user_data = AuthChangePassword(**data)

        if user_data.old_password == user_data.new_password:
            raise CustomException(
                status_code=status.HTTP_409_CONFLICT,
                msg="Old password and new password are the same",
            )

        user: User = current_user.user
        if not userCRUD.authenticate(
            db, email=user.email, password=user_data.old_password
        ):
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED, msg="Incorrect password"
            )

        userCRUD.update(db=db, obj_in=user_data, db_obj=user)

        return CustomResponse(msg="Change password successfully")


user_auth_service = UserAuthService()
