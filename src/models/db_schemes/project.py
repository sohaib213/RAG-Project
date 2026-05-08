from pydantic import BaseModel, Field, validator
from bson import ObjectId


class Project(BaseModel):

    id: str = None
    project_id: str

    @validator("project_id")
    def project_id_must_be_alphanumeric(cls, value):
        if not value.isalnum():
            raise ValueError("Project ID must be alphanumeric only")
        return value

    class Config:
        arbitrary_types_allowed = True