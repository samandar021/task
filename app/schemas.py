from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    id: int
    text: str


class ProcessRequest(BaseModel):
    data: str = Field(min_length=1, max_length=500)


class ProcessResponse(BaseModel):
    processed: str
