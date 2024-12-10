from fastapi import status
from sqlalchemy.orm import Session
from typing import List

from app.crud import work_location as work_locationCRUD
from app.schema.work_location import (
    WorkLocatioCreate,
    WorkLocatioResponse,
    WorkLocatioUpdate,
)
from app.core.location.location_helper import location_helper
from app.model import WorkLocation
from app.common.exception import CustomException


class WorkLocationHepler:
    def get_by_job_id(self, db: Session, job_id: int) -> List[dict]:
        work_locations = work_locationCRUD.get_by_job_id(db, job_id)
        work_locations_response = []
        for work_location in work_locations:
            work_locations_response.append(self.get_info(db, work_location))
        return work_locations_response

    def get_by_id(self, db: Session, id: int) -> dict:
        work_location = work_locationCRUD.get(db, id)
        if not work_location:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Working time not found"
            )

        return self.get_info(db, work_location)

    def get_by_ids(self, db: Session, ids: List[int]) -> List[dict]:
        work_locations = [self.get_by_id(db, id) for id in ids]
        return work_locations

    def create_with_job_id(
        self, db: Session, job_id: int, data: List[dict]
    ) -> List[dict]:
        return [
            self.create(
                db,
                WorkLocatioCreate(job_id=job_id, **work_location),
            )
            for work_location in data
        ]

    def create(self, db: Session, data: WorkLocatioCreate) -> dict:
        work_location = work_locationCRUD.create(db, obj_in=data)

        return self.get_info(db, work_location)

    def update_with_job_id(
        self, db: Session, job_id: int, data: List[dict]
    ) -> List[dict]:
        work_locationCRUD.remove_by_job_id(db, job_id)

        return [
            self.create(
                db,
                WorkLocatioUpdate(job_id=job_id, **work_location),
            )
            for work_location in data
        ]

    def update(self, db: Session, id: int, data: dict) -> WorkLocatioResponse:
        work_location = work_locationCRUD.get(db, id)
        if not work_location:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Working time not found"
            )

        work_location = work_locationCRUD.update(db, work_location, data)

        return self.get_info(db, work_location)

    def delete(self, db: Session, id: int) -> None:
        work_location = work_locationCRUD.get(db, id)
        if not work_location:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Working time not found"
            )
        work_location = work_locationCRUD.remove(db, id)

        return work_location

    def get_info(self, db: Session, work_location: WorkLocation) -> WorkLocatioResponse:
        province = location_helper.get_province_info_by_id(
            db, work_location.province_id
        )
        district = location_helper.get_district_info_by_id(
            db, work_location.district_id
        )
        work_location_response = WorkLocatioResponse(
            **work_location.__dict__, province=province, district=district
        )

        return work_location_response

    def check_valid(self, db: Session, data: dict) -> dict:
        if not data:
            return data

        location_helper.check_valid_province_district(
            db, data["province_id"], data["district_id"]
        )

        return data

    def check_list_valid(self, db: Session, data: List[dict]) -> List[dict]:
        if not data or data is None:
            return data

        return [self.check_valid(db, province_district) for province_district in data]


work_location_helper = WorkLocationHepler()
