import json
from typing import Any
import datetime
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from random import choice
import string
import uuid


class CommonHelper:
    @staticmethod
    def utc_now() -> datetime.datetime:
        """Return current datetime in UTC timezone now."""
        return datetime.datetime.now(datetime.timezone.utc)

    @staticmethod
    def json_dumps(v: Any, *, default: json.JSONEncoder = json.JSONEncoder) -> str:
        """Transforms python-data to JSON-like string.

        Args:
            v (Any): Value that should be dumped into the JSON.
            default (json.JSONEncoder): JSON encoder instance to customize transformation behavior.

        Returns:
            (str): JSON-like string.
        """
        return json.dumps(v, cls=default)

    @staticmethod
    def json_loads(v: str, *, cls: json.JSONDecoder = json.JSONDecoder) -> Any:
        """Transform JSON-like string to python-data.

        Args:
            v (str): JSON-like string.
            cls (json.JSONDecoder): JSON decoder instance to customize transformation behavior.

        Returns:
            (Any): Python-data.
        """
        try:
            return json.loads(v, cls=cls)
        except json.JSONDecodeError:
            return v

    @staticmethod
    def get_timestamp(v: datetime.datetime) -> float:
        """Extract timestamp from datetime object and round for 3 decimal digits."""
        return round(v.timestamp(), 3)

    @staticmethod
    def get_current_time(db: Session):
        result = db.query(func.now()).first()[0]
        return result

    @staticmethod
    def generate_code(digits: int = 6) -> str:
        return "".join(choice(string.digits) for _ in range(digits))

    @staticmethod
    def generate_file_name(key: str = "", file_name: str = "") -> str:
        return (
            f"{key}/{uuid.uuid4()}.{file_name.split('.')[-1]}"
            if key
            else f"{uuid.uuid4()}.{file_name.split('.')[-1]}"
        )

    @staticmethod
    def generate_public_id() -> str:
        return str(uuid.uuid4())
