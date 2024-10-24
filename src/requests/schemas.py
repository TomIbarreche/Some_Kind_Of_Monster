from pydantic import BaseModel

class CreateRequest(BaseModel):
    requester_id: int
    book_update_data: str
    owner_id: int
    book_id: int
    status: str

class CreateRequestOut(CreateRequest):
    id: int

class UpdateRequest(BaseModel):
    requester_id: int
    book_update_data: str
    owner_id: int
    book_id: int