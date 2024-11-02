from enum import Enum


class Role(str, Enum):
    SUPER_USER = "super_user"
    ADMIN = "admin"
    USER = "user"
    SOCIAL_NETWORK = "social_network"
    BUSINESS = "business"


class OrderType(str, Enum):
    ASC = "asc"
    DESC = "desc"


class SortBy(str, Enum):
    ID = "id"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class SortJobBy(str, Enum):
    ID = "id"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    DEADLINE = "deadline"


class SortByJob(str, Enum):
    ID = "id"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    DEADLINE = "deadline"
    QUANTITY = "quantity"
    SALARY = "salary"


class Provider(str, Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    GITHUB = "github"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class JobStatus(str, Enum):
    PENDING = "pending"
    PUBLISHED = "published"
    REJECTED = "rejected"
    EXPIRED = "expired"
    DRAFT = "draft"
    BANNED = "banned"
    STOPPED = "stopped"


class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    INTERNSHIP = "internship"


class JobApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    STOPPED = "stopped"


class RequestApproval(str, Enum):
    CREATE = "create"
    UPDATE = "update"


class AdminJobApprovalStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


class SalaryType(str, Enum):
    VND = "vnd"
    USD = "usd"
    DEAL = "deal"


class HistoryType(str, Enum):
    REGISTER = "register"
    LOGIN = "login"
    VERIFY_SUCCESS = "verify_success"
    CREATE_NEW_CAMPAIGN = "create_new_campaign"
    OFF_CAMPAIGN = "off_campaign"
    ON_CAMPAIGN = "on_campaign"
    DELETE_CAMPAIGN = "delete_campaign"
    UPDATE_CAMPAIGN = "update_campaign"
    APPROVE_JOB = "approve_job"
    REJECT_JOB = "reject_job"


class TypeAccount(str, Enum):
    NORMAL = "normal"
    BUSINESS = "business"


class TokenType(str, Enum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"


class CampaignStatus(str, Enum):
    STOPPED = "stopped"
    OPEN = "open"


class FilterCampaign(str, Enum):
    ONLY_OPEN = "only_open"
    HAS_NEW_CV = "has_new_cv"
    ACTIVED_CV_COUT = "actived_cv_count"
    HAS_PUBLISHING_JOB = "has_publishing_job"
    HAS_RUNNING_SERVICE = "has_running_service"
    EXPIRED_JOB = "expired_job"
    WAITING_APPROVAL_JOB = "waiting_approval_job"


class VerifyCodeStatus(str, Enum):
    ACTIVE = 1
    INACTIVE = 0


class VerifyCodeType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"


class CompanyType(str, Enum):
    COMPANY = "company"
    BUSINESS = "household"


class FolderBucket(str, Enum):
    AVATAR = "avatar"
    LOGO = "logo"
    CV = "cv"
    JOB = "job"
    COMPANY = "company"
    CAMPAIGN = "campaign"
    BUSINESS = "business"
    FIELD = "field"
    LABEL_COMPANY = "label_company"
    ATTACHMENT = "attachment"


class VerifyType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    COMPANY = "company"
    IDENTIFY = "identify"


class CVApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    INTERVIEW = "interview"
    VIEWED = "viewed"


class CVApplicationUpdateStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    STOPPED = "stopped"
    INTERVIEW = "interview"


class JobSkillType(str, Enum):
    MUST_HAVE = "must_have"
    SHOULD_HAVE = "should_have"


class ConversationType(str, Enum):
    PRIVATE = "private"
    GROUP = "group"


class AttachmentType(str, Enum):
    DOC = "application/msword"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    PDF = "application/pdf"
    JPG = "image/jpg"
    JPEG = "image/jpeg"
    PNG = "image/png"
    SVG = "image/svg+xml"


class ImageExtension(str, Enum):
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    SVG = "svg"


class DocumentExtension(str, Enum):
    DOC = "doc"
    DOCX = "docx"
    PDF = "pdf"


class ImageType(str, Enum):
    JPG = "image/jpg"
    JPEG = "image/jpeg"
    PNG = "image/png"
    SVG = "image/svg+xml"


class DocumentType(str, Enum):
    DOC = "application/msword"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    PDF = "application/pdf"


class CreateMessageType(str, Enum):
    TEXT = "text"
    ATTACHMENT = "attachment"


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    ADD_MEMBER = "add_member"
    REMOVE_MEMBER = "remove_member"
    LEAVE_GROUP = "leave_group"
    CREATE_GROUP = "create_group"
    RENAME_GROUP = "rename_group"
    CHANGE_AVATAR = "change_avatar"


class FileType(str, Enum):
    IMAGE = "image"
    FILE = "file"


class ReactionType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"


class MemberType(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


class WebsocketActionType(str, Enum):
    NEW_MESSAGE = "new_message"
    USER_TYPING = "user_typing"
    NEW_CONVERSATION = "new_conversation"
    ADD_MEMBER = "add_member"
    UPDATE_CONVERSATION = "update_conversation"
    UPDATE_AVATAR_CONVERSATION = "update_avatar_conversation"
