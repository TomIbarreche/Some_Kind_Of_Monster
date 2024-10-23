import time
from fastapi import Depends
import pika.exceptions
import pika.spec
from sqlmodel.ext.asyncio.session import AsyncSession
import requests
from src.auth.service import UserService
from src.books.schemas import BookCreateModel
from src.db.models import User
from src.mail import create_message
from src.errors import UpdateRequestNotAllowed, UserVerificationFailed
import pika
import json
from src.auth.utils import UrlSerializer
from src.config import settings
connection_parameters = pika.ConnectionParameters('localhost')


class RequestService:
    def __init__(self, session: AsyncSession):
        self.session = session


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
        data = update_data.model_dump_json()
        data_dict = json.loads(data)
        message_data_dict = {}
        for book in current_user.books:
            if book.id == book_id:
                creator = await _userService.get_user_by_id(book.creator_id)
                message_data_dict["mail"] = creator.email
                token = UrlSerializer.create_url_safe_token({"email":creator.email})
                message_data_dict["token"] = token
                message_data_dict["subject"] = settings.update_request_mail_subject
                # data = json.dumps(data_dict)
                message_data = json.dumps(message_data_dict)
                try:
                    channel.queue_declare(queue=settings.routing_key, durable=True)
                    channel.basic_publish(exchange="", routing_key=settings.routing_key, body=message_data, properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE))
                except Exception as err:
                    print(f"Failed to publish message: {err}")
                finally:
                    channel.close()
                    connection.close()
        
        #raise UpdateRequestNotAllowed(info={"error":"You can only ask for update request on a book you have registered", "data":f"Book id: {book_id}"})

