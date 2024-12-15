from app.core import constant
import re
from datetime import datetime, date
from fastapi import UploadFile
from typing import List

from app.hepler.common import CommonHelper
from app.hepler.enum import (
    Gender,
    FolderBucket,
    CampaignStatus,
    FilterCampaign,
    SortByJob,
    OrderType,
    AdminJobApprovalStatus,
    MessageType,
    CreateMessageType,
    JobStatus,
)
from app.hepler.common import CommonHelper


class SchemaValidator:
    @staticmethod
    def validate_phone_number(v):
        if v is not None:
            if not re.match(constant.REGEX_PHONE_NUMBER, v):
                raise ValueError("Invalid phone number")
        return v

    @staticmethod
    def validate_gender(v):
        if v is not None:
            if v not in Gender.__members__.values():
                raise ValueError("Invalid gender")
        return v

    @staticmethod
    def validate_email(v):
        if not re.match(constant.REGEX_EMAIL, v):
            raise ValueError("Invalid email")
        return v

    @staticmethod
    def validate_old_password(v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        elif len(v) > 50:
            raise ValueError("Password must be at most 50 characters")
        return v

    @staticmethod
    def validate_password(v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        elif len(v) > 50:
            raise ValueError("Password must be at most 50 characters")
        elif not re.match(constant.REGEX_PASSWORD, v):
            raise ValueError(
                "Password must contain at least one special character, one digit, one alphabet, one uppercase letter"
            )
        return v

    @staticmethod
    def validate_confirm_password(v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        elif "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        elif not re.match(constant.REGEX_PASSWORD, v):
            raise ValueError(
                "Password must contain at least one special character, one digit, one alphabet, one uppercase letter"
            )
        return v

    @staticmethod
    def validate_avatar_url(v):
        if v is not None:
            if not v.startswith("https://"):
                v = constant.BUCKET_URL + v
        return v

    @staticmethod
    def validate_avatar_upload_file(v):
        if v is not None:
            if v.content_type not in constant.ALLOWED_IMAGE_TYPES:
                raise ValueError("Invalid avatar type")
            elif v.size > constant.MAX_IMAGE_SIZE:
                raise ValueError("Avatar size must be at most 2MB")
        return v

    @staticmethod
    def validate_cv_upload_file(v: UploadFile):
        if v is not None:
            if v.content_type not in constant.ALLOWED_CV_TYPES:
                raise ValueError("Invalid cv type")
            elif v.size > constant.MAX_CV_SIZE:
                raise ValueError("CV size must be at most 2MB")
        return v

    @staticmethod
    def validate_files(v: List[UploadFile]):
        if v is not None:
            for file in v:
                if file.content_type not in constant.ALLOWED_FILE_TYPES:
                    raise ValueError("Invalid file type")
                # elif file.size > constant.MAX_IMAGE_SIZE:
                #     raise ValueError("File size must be at most 2MB")
                if file.content_type in constant.ALLOWED_IMAGE_TYPES:
                    if file.size > constant.MAX_IMAGE_SIZE:
                        raise ValueError("Image size must be at most 2MB")
                else:
                    if file.size > constant.MAX_FILE_SIZE:
                        raise ValueError("File size must be at most 5MB")
        return v

    @staticmethod
    def validate_cv_url(v):
        if v is not None:
            if not v.startswith("https://"):
                v = constant.BUCKET_URL + v
        return v

    @staticmethod
    def validate_logo_upload_file(v):
        if v is not None:
            if v.content_type not in constant.ALLOWED_IMAGE_TYPES:
                raise ValueError("Invalid image type")
            elif v.size > constant.MAX_IMAGE_SIZE:
                raise ValueError("Image size must be at most 2MB")
        return v

    @staticmethod
    def validate_attachment_url(v, values):
        if "name" in values and not v.startswith("https://"):
            v = constant.BUCKET_URL + values["name"]
        return v

    @staticmethod
    def validate_title(v):
        if len(v) < 1 or len(v) > 255:
            raise ValueError("Invalid title length")
        return v

    @staticmethod
    def validate_campaign_status(v):
        if not v in CampaignStatus.__members__.values():
            raise ValueError("Invalid status")
        return v or CampaignStatus.OPEN

    @staticmethod
    def validate_filter_campaign(v):
        if v and not v in FilterCampaign.__members__.values():
            raise ValueError("Invalid filter")
        return v

    @staticmethod
    def validate_id(v):
        if not v or v < 1:
            raise ValueError("Invalid id")
        return v

    @staticmethod
    def validate_company_name(v):
        if len(v) < 3:
            raise ValueError("Company name must be at least 3 characters")
        elif len(v) > 255:
            raise ValueError("Company name must be at most 255 characters")
        return v

    @staticmethod
    def validate_json_loads(v):
        if v is not None:
            return CommonHelper.json_loads(v) if isinstance(v, str) else v

    @staticmethod
    def validate_json_dumps(v):
        if v is not None:
            return CommonHelper.json_dumps(v)
        return v

    @staticmethod
    def validate_json_dumps_list(v):
        if v is not None:
            return CommonHelper.json_dumps(v) if isinstance(v, list) else v
        return v

    @staticmethod
    def validate_json_dumps_dict(v):
        if v is not None:
            return CommonHelper.json_dumps(v) if isinstance(v, dict) else v
        return v

    @staticmethod
    def validate_json_loads_list(v) -> list:
        if v is not None:
            return CommonHelper.json_loads(v) if isinstance(v, str) else v
        return v

    @staticmethod
    def validate_json_loads_dict(v) -> dict:
        if v is not None:
            return CommonHelper.json_loads(v) if isinstance(v, dict) else v
        return v

    @staticmethod
    def validate_logo(v):
        if v is not None:
            if not v.startswith("https://"):
                v = constant.BUCKET_URL + v
        return v

    @staticmethod
    def validate_limit(v):
        if v is not None and not isinstance(v, int):
            raise ValueError("Limit must be an integer")
        if v is not None and (v < 1 or v > 1000):
            raise ValueError("Invalid limit")
        return v or 10

    @staticmethod
    def validate_skip(v):
        if v is not None and (v < 0 or v > 100000):
            raise ValueError("Invalid skip")
        return v or 0

    @staticmethod
    def validate_job_sort_by(v):
        if v and v == SortByJob.SALARY:
            return "max_salary"
        return v or SortByJob.CREATED_AT

    @staticmethod
    def validate_job_updated_at(v):
        if v:
            if not isinstance(v, date):
                raise ValueError("Invalid updated_at")
            return datetime.combine(v, datetime.min.time())

    @staticmethod
    def validate_dealine(v):
        if v:
            if v < datetime.now().date():
                raise ValueError("Invalid deadline")
        return v

    @staticmethod
    def validate_email_contact(v):
        if v:
            if not isinstance(v, list):
                raise ValueError("Require list email")
            for email in v:
                if not re.match(constant.REGEX_EMAIL, email):
                    raise ValueError("Invalid email")
            if isinstance(v, list):
                v = CommonHelper.json_dumps(list(set(v)))
            return v
        raise ValueError("Require email contact")

    @staticmethod
    def validate_working_times(v):
        if not isinstance(v, list):
            raise ValueError("Invalid working_times")
        for item in v:
            if not isinstance(item, dict):
                raise ValueError("Invalid dict working_times")
        return v

    @staticmethod
    def validate_categories(v):
        if not isinstance(v, list):
            raise ValueError("Invalid categories")
        for item in v:
            if not isinstance(item, int):
                raise ValueError("Invalid int categories")
        return v

    @staticmethod
    def validate_locations(v):
        if not isinstance(v, list):
            raise ValueError("Invalid work_locations")
        for item in v:
            if not isinstance(item, dict):
                raise ValueError("Invalid dict work_locations")
        return v or []

    @staticmethod
    def validate_skills(v):
        if not isinstance(v, list):
            raise ValueError("Require list skills")
        for item in v:
            if not isinstance(item, int):
                raise ValueError("Require int skills")
        return v or []

    @staticmethod
    def validate_status_update_job(v):
        if v not in [
            AdminJobApprovalStatus.APPROVED,
            AdminJobApprovalStatus.REJECTED,
            AdminJobApprovalStatus.STOPPED,
        ]:
            raise ValueError("Invalid status")
        return v

    @staticmethod
    def validate_full_name(v):
        if v:
            if not re.match(constant.REGEX_FULL_NAME, v):
                raise ValueError("Invalid full name")
        return v

    @staticmethod
    def validate_date_of_week(v):
        if v < 1 or v > 7:
            raise ValueError("Date of week must be in range 1 to 7")
        return v

    @staticmethod
    def validate_code(v):
        if v.isdigit() and len(v) == 6:
            return v
        raise ValueError("Code must be 6 digits")

    @staticmethod
    def validate_fields(v):
        if not isinstance(v, list):
            raise ValueError("Invalid fields")
        elif len(v) == 0:
            raise ValueError("Fields must not be empty")
        return v

    @staticmethod
    def validate_list_member(v):
        if not isinstance(v, list):
            raise ValueError("Invalid list member")
        v = list(set(v))
        if len(v) < 1:
            raise ValueError("Invalid list member")
        return v

    @staticmethod
    def validate_message_type_and_data(v, values):
        if v == CreateMessageType.TEXT and (
            "content" not in values or len(values["content"]) == 0
        ):
            raise ValueError("Content is required")
        elif (v == CreateMessageType.ATTACHMENT) and (
            "attachments" not in values or len(values["attachments"]) == 0
        ):
            raise ValueError("attachments is required")
        return v

    @staticmethod
    def validate_job_status(v):
        if v not in JobStatus.__members__.values():
            raise ValueError("Invalid job status")
        return v
