from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import Request

class RequestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_book_update_request(self,new_request: Request):
        self.session.add(new_request)
        await self.session.commit()
        await self.session.refresh(new_request)
        return new_request

    async def get_request_by_id(self, request_id: int):
        statement = select(Request).where(Request.id == request_id)
        result = await self.session.exec(statement)
        request = result.first()
        return request
    
    async def get_all_requests(self, limit: int, offset: int):
        statement = select(Request).limit(limit).offset(offset).order_by(Request.created_at)
        result = await self.session.exec(statement)
        requests = result.unique().all()
        return requests
    
    async def update_request(self, request: Request, request_data_dict: dict):
        for k,v in request_data_dict.items():
            setattr(request, k,v)

        await self.session.commit()
        return request