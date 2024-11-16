from typing import List
from sqlalchemy.orm import Session

from app.core.security import PasswordManager
from .base import CRUDBase
from app.model import Admin
from app.schema import admin as schema_admin
from app.hepler.enum import Role
from app.crud.manager import manager


class CRUDAdmin(CRUDBase[Admin, schema_admin.AdminCreate, schema_admin.AdminUpdate]):

    def get_by_email(self, db: Session, email: str) -> Admin:
        manager = manager.get_by_email(db, email)
        return (
            db.query(Admin).filter(Admin.id == manager.id).first() if manager else None
        )

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "id",
        order_by: str = "desc"
    ) -> List[Admin]:
        return super().get_multi(
            db, skip=skip, limit=limit, sort_by=sort_by, order_by=order_by
        )

    def create(self, db: Session, *, obj_in: schema_admin.AdminCreate) -> Admin:
        db_obj = Admin(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Admin:
        user = self.get_by_email(db, email)
        if not user:
            return None
        if not PasswordManager.verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: Admin) -> bool:
        return user.is_active

    def is_superuser(self, user: Admin) -> bool:
        return user.role == Role.SUPER_USER

    def set_active(self, db: Session, *, db_obj: Admin, is_active: bool) -> Admin:
        db_obj.is_active = is_active
        db.commit()
        db.refresh(db_obj)
        return db_obj


admin = CRUDAdmin(Admin)
