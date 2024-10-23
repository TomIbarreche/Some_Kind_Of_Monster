import time
from fastapi import Depends
import pika.exceptions
import pika.spec
from sqlmodel.ext.asyncio.session import AsyncSession
import requests
from src.auth.service import UserService
from src.books.schemas import BookCreateModel
from src.db.models import Request, User
from src.mail import create_message
from src.errors import RequestNotFound, UpdateRequestNotAllowed, UserVerificationFailed, RequestCheckNotAllowed
import pika
import json
from src.auth.utils import UrlSerializer
from src.config import settings
from src.requests.repository import RequestRepository
connection_parameters = pika.ConnectionParameters('localhost')


class RequestService:
    def __init__(self, session: AsyncSession):
        self.repository = RequestRepository(session)

    def connect_to_rabbitmq(self):
        while True:
            try:
                connection = pika.BlockingConnection(connection_parameters)
                return connection
            except pika.exceptions.AMQPConnectionError:
                print("Failed to connect to RabbitMq. Retrying in 5seconds...")
                time.sleep(5)


    async def create_update_book_request(self,book_id, update_data: BookCreateModel, current_user:User, session: AsyncSession):
        _userService = UserService(session)
        connection = self.connect_to_rabbitmq()
        channel = connection.channel()
        message_data_dict = {}
        for book in current_user.books:
            if book.id == book_id:
                data = update_data.model_dump_json()
                creator = await _userService.get_user_by_id(book.creator_id)
                new_request = Request(requester_id=current_user.id, book_update_data=data, owner_id=creator.id, book_id=book.id)
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

    async def get_request_from_mail(self, token: str, current_user: User):
        try:
            token_data = UrlSerializer.decode_url_safe_token(token)
            user_email = token_data["email"]
            request_id = token_data["request_id"]

        except Exception:
            raise UserVerificationFailed(info={"error": "Can't access user email from token verification"})
            
        if user_email != current_user.email:
            raise RequestCheckNotAllowed(info={"error": "This request dont belong to the current_user", "data":f"Request owner email: {user_email}"})
        
        request = await self.get_request_by_id( request_id)

        if request.owner_id != current_user.id:
            raise RequestCheckNotAllowed(info={"error": "This request dont belong to the current_user", "data":f"Request owner email: {user_email}"})
        
        return request

    async def get_request_by_id(self, request_id: int):
        request = await self.repository.get_request_by_id(request_id)
        if request is None:
            raise RequestNotFound(info={"error": "This request wasnt found in DB", "data":f"Request id: {request_id}"})
        return request