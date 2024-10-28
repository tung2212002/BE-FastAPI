from fastapi import Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.auth.jwt.auth_handler import token_manager
from app.common.exception import CustomException


class BaseJWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, raise_error: bool = True):
        super(BaseJWTBearer, self).__init__(auto_error=auto_error)
        self.raise_error = raise_error

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            BaseJWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                if self.raise_error:
                    raise CustomException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        msg="Invalid authentication scheme.",
                    )
                return None

            payload = self.verify_jwt(credentials.credentials)
            if not payload:
                if self.raise_error:
                    raise CustomException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        msg="Invalid token or expired token.",
                    )
                return None

            return {"token": credentials.credentials, "payload": payload}
        else:
            if self.raise_error:
                raise CustomException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    msg="Forbidden",
                )
            return None

    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            payload = token_manager.decodeJWT(jwtoken)
        except:
            payload = None
        return payload


class JWTBearer(BaseJWTBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error, raise_error=True)


class JWTBearerOptional(BaseJWTBearer):
    def __init__(self, auto_error: bool = False):
        super(JWTBearerOptional, self).__init__(
            auto_error=auto_error, raise_error=False
        )
