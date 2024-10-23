from pydantic import BaseModel


class CreateRequest(BaseModel):
    requester_id: int
    book_update_data: str
    owner_id: int
    book_id: int

class CreateRequestOut(CreateRequest):
    id: int