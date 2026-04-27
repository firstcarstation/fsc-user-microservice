from pydantic import BaseModel, Field


class AdminBulkProfilesRequest(BaseModel):
    user_ids: list[str] = Field(default_factory=list)


class AdminBulkProfilesResponse(BaseModel):
    users: list[dict]

