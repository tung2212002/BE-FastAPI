from fastapi import APIRouter

from app.api.api_v1.endpoint.business import (
    business,
    business_auth,
    business_admin,
    business_campaign,
    business_company,
    business_job,
    verify,
    business_cv_applications,
)

from app.api.api_v1.endpoint.config import (
    location,
    position,
    position_group,
    category,
    skill,
    field,
)

from app.api.api_v1.endpoint.user import user_auth, user, company, job, cv_applications
from app.api.api_v1.endpoint.admin import admin_approval_request_job
from app.api.api_v1.endpoint.chat import websocket, chat, conversation, contact, message

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(user_auth.router, prefix="/user", tags=["user_auth"])
api_router.include_router(user.router, prefix="/user/users", tags=["user"])
api_router.include_router(
    cv_applications.router, prefix="/user/cv_applications", tags=["cv_applications"]
)
api_router.include_router(location.router, prefix="/location", tags=["location"])
api_router.include_router(position.router, prefix="/position", tags=["position"])
api_router.include_router(
    position_group.router, prefix="/position_group", tags=["position_group"]
)
api_router.include_router(category.router, prefix="/category", tags=["category"])
api_router.include_router(skill.router, prefix="/skill", tags=["skill"])
api_router.include_router(field.router, prefix="/field", tags=["field"])
api_router.include_router(job.router, prefix="/job", tags=["job"])
api_router.include_router(company.router, prefix="/company", tags=["company"])

api_router.include_router(
    verify.router, prefix="/business/verify", tags=["business_verify"]
)
api_router.include_router(
    business_company.router,
    prefix="/business/business_company",
    tags=["business_company"],
)
api_router.include_router(
    business_job.router, prefix="/business/job", tags=["business_job"]
)
api_router.include_router(
    business_campaign.router, prefix="/business/campaign", tags=["business_campaign"]
)
api_router.include_router(
    business_cv_applications.router,
    prefix="/business/cv_applications",
    tags=["business_cv_applications"],
)
api_router.include_router(
    business_admin.router, prefix="/admin", tags=["business_admin"]
)
api_router.include_router(
    business.router, prefix="/business", tags=["business_business"]
)
api_router.include_router(
    business_auth.router, prefix="/business", tags=["business_auth"]
)

api_router.include_router(
    admin_approval_request_job.router,
    prefix="/admin/approval_request_job",
    tags=["admin_approval_request_job"],
)

api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(
    conversation.router, prefix="/conversation", tags=["conversation"]
)
api_router.include_router(message.router, prefix="/message", tags=["message"])
api_router.include_router(contact.router, prefix="/contact", tags=["contact"])
api_router.include_router(websocket.router, tags=["websocket"])
