from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.schemas import BookCreateModel
from src.db.models import User
from src.errors import UpdateRequestNotAllowed
import pika
import json
connection_parameters = pika.ConnectionParameters('localhost')

connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()

channel.queue_declare(queue="letterbox")



def on_message_received(channel, method, properties, body):
    print(f"receive new message {body}")
    channel.stop_consuming()


class RequestService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_update_book_request(self,book_id, update_data: BookCreateModel, current_user:User):
        data = update_data.model_dump_json()
        for book in current_user.books:
            if book.id == book_id:
                print(data)
                print("Create the request message for rabbitmq")
                print(book.creator_id)
                

            

                channel.basic_publish(exchange="", routing_key="letterbox", body=data)

                print(f"sent message {data} ")

                

        #raise UpdateRequestNotAllowed(info={"error": "User can ask for an update request only on his registered books"})

    async def check_requests(self):
        channel.basic_consume(queue="letterbox", auto_ack=True, on_message_callback=on_message_received)

        print('starting consuming')
        
        channel.start_consuming()

        print("stop")
        return {}