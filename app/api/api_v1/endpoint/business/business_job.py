from fastapi import (
    APIRouter,
    Depends,
    Request,
    Body,
    Query,
    Path,
)
from sqlalchemy.orm import Session
from redis.asyncio import Redis

from app.db.base import get_db
from app.storage.redis import get_redis
from app.core.auth.user_manager_service import user_manager_service
from app.core.job.job_service import job_service
from app.hepler.enum import (
    SortBy,
    OrderType,
    JobStatus,
    JobApprovalStatus,
    JobType,
    SortJobBy,
    SalaryType,
)

router = APIRouter()


@router.get("", summary="Get list of job.")
async def get_job(
    request: Request,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user=Depends(user_manager_service.get_current_business_admin_superuser),
    skip: int = Query(None, description="The number of users to skip.", example=0),
    limit: int = Query(None, description="The number of users to return.", example=10),
    sort_by: SortBy = Query(
        None, description="The field to sort by.", example=SortBy.ID
    ),
    order_by: OrderType = Query(
        None, description="The order to sort by.", example=OrderType.DESC
    ),
    business_id: int = Query(None, description="The business id.", example=1),
    company_id: int = Query(None, description="The company id.", example=1),
    job_status: JobStatus = Query(
        None, description="The job status.", example=JobStatus.PUBLISHED
    ),
    job_approve_status: JobApprovalStatus = Query(
        None, description="The job approve status.", example=JobApprovalStatus.PENDING
    ),
):
    """
    Get list of job by business.

    This endpoint allows getting a list of job by business.

    Parameters:
    - skip (int): The number of users to skip.
    - limit (int): The number of users to return.
    - sort_by (str): The field to sort by.
    - order_by (str): The order to sort by.
    - business_id (int): The business id.
    - company_id (int): The company id.
    - job_status (str): The job status.
    - job_approve_status (str): The job approve status.
    - campaign_id (int): The campaign id.

    Returns:
    - status_code (200): The list of job has been found successfully.
    - status_code (400): The request is invalid.
    - status_code (403): The permission is denied.

    """
    args = {item[0]: item[1] for item in request.query_params.multi_items()}

    return await job_service.get_by_business(db, redis, {**args}, current_user)


@router.get("/search", summary="Search list of job.")
async def search_job(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user=Depends(user_manager_service.get_current_business_admin_superuser),
    skip: int = Query(None, description="The number of users to skip.", example=0),
    limit: int = Query(None, description="The number of users to return.", example=100),
    sort_by: SortJobBy = Query(
        None, description="The field to sort by.", example=SortJobBy.ID
    ),
    order_by: OrderType = Query(
        None, description="The order to sort by.", example=OrderType.DESC
    ),
    company_id: int = Query(None, description="The company id.", example=1),
    business_id: int = Query(None, description="The business id.", example=1),
    job_status: JobStatus = Query(
        None, description="The job status.", example=JobStatus.PUBLISHED
    ),
    province_id: int = Query(None, description="The province id.", example=1),
    district_id: int = Query(None, description="The district id.", example=1),
    category_id: int = Query(None, description="The category id.", example=1),
    field_id: int = Query(None, description="The field id.", example=1),
    employment_type: JobType = Query(
        None, description="The employment type.", example=JobType.FULL_TIME
    ),
    job_experience_id: int = Query(None, description="The experience id.", example=1),
    min_salary: int = Query(None, description="The min salary.", example=1000000),
    max_salary: int = Query(None, description="The max salary.", example=10000000),
    salary_type: SalaryType = Query(
        None, description="The type salary.", example=SalaryType.VND
    ),
    job_position_id: int = Query(None, description="The position id.", example=1),
    keyword: str = Query(None, description="The keyword.", example="developer"),
):
    """
    Get list of job by business.

    This endpoint allows getting a list of job by user.

    Parameters:
    - skip (int): The number of users to skip.
    - limit (int): The number of users to return.
    - sort_by (str): The field to sort by.
    - order_by (str): The order to sort by.
    - company_id (int): The company id.
    - province_id (int): The province id.
    - district_id (int): The district id.
    - category_id (int): The category id.
    - field_id (int): The field id.
    - employment_type (str): The employment type.
    - job_experience_id (int): The experience id.
    - job_position_id (int): The position id.
    - min_salary (int): The min salary.
    - max_salary (int): The max salary.
    - salary_type (str): The type salary.
    - keyword (str): The keyword.
    - status (str): The job status.
    - business_id (int): The business id.

    Returns:
    - status_code (200): The list of job has been found successfully.
    - status_code (400): The request is invalid.
    - status_code (403): The permission is denied.

    """
    args = locals()

    return await job_service.search_by_business(
        db,
        redis,
        current_user,
        {**args},
    )


@router.get("/{job_id}", summary="Get job by id.")
async def get_job_by_id(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user=Depends(user_manager_service.get_current_business_admin_superuser),
    job_id: int = Path(
        ...,
        description="The job id.",
        example=1,
    ),
):
    """
    Get job by id.

    This endpoint allows getting a job by id.

    Parameters:
    - job_id (int): The job id.

    Returns:
    - status_code (200): The job has been found successfully.
    - status_code (403): The permission is denied.
    - status_code (404): The job is not found.

    """
    return await job_service.get_by_id_for_business(db, redis, job_id, current_user)


@router.post("", summary="Create a new job.")
async def create_job(
    # db = CurrentSession,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user=Depends(user_manager_service.get_current_business),
    data: dict = Body(
        ...,
        description="The information of the job.",
        example={
            "title": "Tuyển thực tập sinh Backend FastAPI ",
            "min_salary": 5000000,
            "max_salary": 10000000,
            "salary_type": "vnd",
            "locations": [
                {"province_id": 1, "district_id": 1, "description": "Địa chỉ 1"},
            ],
            "gender_requirement": "other",
            "job_description": "<p>Job description</p>",
            "job_requirement": "<p>Job requirement</p>",
            "job_benefit": "<p>Job benefit</p>",
            "employment_type": "full_time",
            "deadline": "2024-05-03",
            "full_name_contact": "Nhà tuyển dụng",
            "phone_number_contact": "0328493879",
            "email_contact": ["tung@gmail.com"],
            "campaign_id": 1,
            "quantity": 5,
            "categories": [1, 2, 3],
            "working_times": [
                {
                    "date_from": 1,
                    "date_to": 5,
                    "start_time": "08:30",
                    "end_time": "18:00",
                }
            ],
            "working_time_text": "Thời gian làm việc từ 8h30 đến 18h",
            "must_have_skills": [2, 3],
            "should_have_skills": [1, 4],
            "job_position_id": 1,
            "job_experience_id": 2,
            "job_location": "Chuyên viên Nhân sự",
        },
    ),
):
    """
    Create a new job.

    This endpoint allows creating a new job with the provided information.

    Parameters:
    - data (dict): The information of the job.

    Returns:
    - status_code (201): The job has been created successfully.
    - status_code (401): The job is not authorized.
    - status_code (400): The request is invalid.
    - status_code (409): The job is already registered.

    """
    return await job_service.create(db, redis, data, current_user)


@router.put("/{job_id}", summary="Update a new job.")
async def Update_job(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user=Depends(user_manager_service.get_current_business),
    job_id: int = Path(
        ...,
        description="The job id.",
        example=1,
    ),
    data: dict = Body(
        ...,
        description="The information of the job.",
        example={
            "title": "Tuyển thực tập sinh Backend FastAPI ",
            "min_salary": 5000000,
            "max_salary": 10000000,
            "salary_type": "vnd",
            "locations": [
                {"province_id": 1, "district_id": 1, "description": "Địa chỉ 1"},
            ],
            "gender_requirement": "other",
            "job_description": "<p>Job description</p>",
            "job_requirement": "<p>Job requirement</p>",
            "job_benefit": "<p>Job benefit</p>",
            "employment_type": "full_time",
            "deadline": "2024-05-03",
            "full_name_contact": "Nhà tuyển dụng",
            "phone_number_contact": "0328493879",
            "email_contact": ["tung@gmail.com"],
            "quantity": 5,
            "categories": [1, 2, 3],
            "working_times": [
                {
                    "date_from": 1,
                    "date_to": 5,
                    "start_time": "08:30",
                    "end_time": "18:00",
                }
            ],
            "working_time_text": "Thời gian làm việc từ 8h30 đến 18h",
            "must_have_skills": [2, 3],
            "should_have_skills": [1, 4],
            "job_position_id": 1,
            "job_experience_id": 2,
            "job_location": "Chuyên viên Nhân sự",
        },
    ),
):
    """
    Update a new job.

    This endpoint allows update a new job with the provided information.

    Parameters:
    - job_id (int): The job id.
    - data (dict): The information of the job.

    Returns:
    - status_code (200): The job has been updated successfully.
    - status_code (401): The job is not authorized.
    - status_code (400): The request is invalid.
    - status_code (404): The job is not found.

    """
    return await job_service.update(db, redis, {**data, "job_id": job_id}, current_user)


@router.put("/{job_id}/status", summary="Update job status.")
async def update_job_status(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user=Depends(user_manager_service.get_current_business_admin_superuser),
    job_id: int = Path(
        ...,
        description="The job id.",
        example=1,
    ),
    data: dict = Body(
        ...,
        description="The job status data.",
        example={"status": JobStatus.PUBLISHED},
    ),
):
    """
    Update job status.

    This endpoint allows updating a job status.

    Parameters:
    - job_id (int): The job id.
    - status (bool): The job status.

    Returns:
    - status_code (200): The job has been updated successfully.
    - status_code (400): The request is invalid.
    - status_code (403): The permission is denied.
    - status_code (404): The job is not found.

    """
    return await job_service.update_status(
        db, redis, {**data, "id": job_id}, current_user
    )


@router.delete("/{job_id}", summary="Delete a job.")
async def delete_job(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user=Depends(user_manager_service.get_current_business_admin_superuser),
    job_id: int = Path(
        ...,
        description="The job id.",
        example=1,
    ),
):
    """
    Delete a job.

    This endpoint allows delete a job with the provided information.

    Parameters:
    - job_id (int): The job id.

    Returns:
    - status_code (200): The job has been deleted successfully.
    - status_code (401): The job is not authorized.
    - status_code (404): The job is not found.
    - status_code (403): The permission is denied.

    """
    return await job_service.delete(db, redis, job_id, current_user)
