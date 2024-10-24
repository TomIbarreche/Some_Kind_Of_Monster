from datetime import datetime
import time
from typing import List
import pika.exceptions
import pika.spec
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import UserService
from src.books.schemas import BookCreateModel, BookModelOut
from src.books.service import BookService
from src.db.models import Request, User
from src.enums import RequestStatus
from src.errors import RequestNotFound, RequestStatusNotFound, TokenVerificationEmailNotMatch, UpdateRequestNotAllowed, UserVerificationFailed, RequestCheckNotAllowed, ValidateRequestNotAllowed
import pika
import json
from src.auth.utils import UrlSerializer
from src.config import settings
from src.requests.repository import RequestRepository
from src.requests.schemas import CreateRequest, CreateRequestOut

connection_parameters = pika.ConnectionParameters('localhost')


class RequestService:
    def __init__(self, session: AsyncSession):
        self.repository = RequestRepository(session)
        self._userService = UserService(session)
        self._bookService = BookService(session)

    def connect_to_rabbitmq(self):
        while True:
            try:
                connection = pika.BlockingConnection(connection_parameters)
                return connection
            except pika.exceptions.AMQPConnectionError:
                print("Failed to connect to RabbitMq. Retrying in 5seconds...")
                time.sleep(5)


    async def create_update_book_request(self,book_id, update_data: BookCreateModel, current_user:User, session: AsyncSession)-> CreateRequestOut:
        connection = self.connect_to_rabbitmq()
        channel = connection.channel()
        message_data_dict = {}
        for book in current_user.books:
            if book.id == book_id:
                data = update_data.model_dump_json()
                creator = await self._userService.get_user_by_id(book.creator_id)
                new_request = Request(requester_id=current_user.id, book_update_data=data, owner_id=creator.id, book_id=book.id, status=RequestStatus.CREATED.value)
                new_request = await self.repository.create_book_update_request(new_request)
                message_data_dict["mail"] = creator.email
                token = UrlSerializer.create_url_safe_token({"email":creator.email, "request_id": new_request.id})
                message_data_dict["token"] = token
                message_data_dict["subject"] = settings.update_request_mail_subject
                message_data = json.dumps(message_data_dict)
                try:
                    channel.queue_declare(queue=settings.routing_key, durable=True)
                    channel.basic_publish(exchange="", routing_key=settings.routing_key, body=message_data, properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE))
                except Exception as err:
                    print(f"Failed to publish message: {err}")
                finally:
                    channel.close()
                    connection.close()
                return new_request

        raise UpdateRequestNotAllowed(info={"error":"You can only ask for update request on a book you have registered", "data":f"Book id: {book_id}"})

    async def get_request_from_mail(self, token: str, current_user: User) -> CreateRequestOut:
        try:
            token_data = UrlSerializer.decode_url_safe_token(token)
            user_email = token_data["email"]
            request_id = token_data["request_id"]

        except Exception:
            raise UserVerificationFailed(info={"error": "Can't access user email from token verification"})
            
        if user_email != current_user.email:
            raise TokenVerificationEmailNotMatch(info={"error": "This request dont belong to the current_user", "data":f"Request owner email: {user_email}"})
        
        request = await self.get_request_by_id( request_id)

        if request.owner_id != current_user.id:
            raise RequestCheckNotAllowed(info={"error": "This request dont belong to the current_user", "data":f"Request owner email: {user_email}"})
        
        return request

    async def get_request_by_id(self, request_id: int) -> CreateRequestOut:
        request = await self.repository.get_request_by_id(request_id)
        if request is None:
            raise RequestNotFound(info={"error": "This request wasnt found in DB", "data":f"Request id: {request_id}"})
        return request
    
    async def get_requests_for_user(self, user_id: int, current_user: User) -> List[CreateRequestOut]:
        if user_id != current_user.id:
            raise RequestCheckNotAllowed(info={"error": "You cant access request of an other user", "data":f"User id: {user_id}"})
        user = await self._userService.get_user_by_id(user_id)
        return user.requests

    async def get_all_requests(self, limit: int, offset: int) -> List[CreateRequestOut]:
        return await self.repository.get_all_requests(limit, offset)

    async def validate_request(self, request_id: int, current_user: User)-> BookModelOut:
        request = await self.get_request_by_id(request_id)
        if request.owner_id != current_user.id:
            raise UpdateRequestNotAllowed(info={"error": "This request dont belong to the current_user", "data":f"Request owner id: {request.owner_id}"})
        
        if request.status == RequestStatus.CANCELLED.value:
            raise ValidateRequestNotAllowed(info={"error": "This request have been cancelled"})
        
        if request.status == RequestStatus.VALIDATED.value:
            raise ValidateRequestNotAllowed(info={"error": "This request have already been validated"})
        await self.repository.update_request(request, {"status":RequestStatus.VALIDATED.value})

        book_to_update = await self._bookService.get_book_by_id(request.book_id)
        updated_book_data_dict = json.loads(request.book_update_data)
        date = datetime.strptime(updated_book_data_dict["published_date"], "%Y-%d-%m").date()
        updated_book_data_dict["published_date"] = date
        updated_book= await self._bookService.repository.update_book(book_to_update, updated_book_data_dict)

        connection = self.connect_to_rabbitmq()
        channel = connection.channel()
        message_data_dict = {}
        requester = await self._userService.get_user_by_id(request.requester_id)
        message_data_dict["mail"] = requester.email

        token = UrlSerializer.create_url_safe_token({"email":requester.email, "book_id": request.book_id})
        message_data_dict["token"] = token
        message_data_dict["subject"] = settings.validate_request_mail_subject
        message_data = json.dumps(message_data_dict)
        try:
            channel.queue_declare(queue=settings.routing_key, durable=True)
            channel.basic_publish(exchange="", routing_key=settings.routing_key, body=message_data, properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE))
        except Exception as err:
            print(f"Failed to publish message: {err}")
        finally:
            channel.close()
            connection.close()

        return updated_book

    async def update_request(self, request_id: int, request_data: CreateRequest, current_user: User) -> CreateRequestOut:
        request = await self.get_request_by_id(request_id)
        if request.owner_id != current_user.id:
            raise UpdateRequestNotAllowed(info={"error": "This request dont belong to the current_user", "data":f"Request owner id: {request.owner_id}"})
        
        request_data_dict = request_data.model_dump()
        updated_request = await self.repository.update_request(request, request_data_dict)
        return updated_request
       

