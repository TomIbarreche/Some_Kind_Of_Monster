from datetime import timedelta, datetime
from src.errors import TokenDecodeFail
from passlib.context import CryptContext
import jwt
from src.config import settings
from itsdangerous import  URLSafeTimedSerializer
import logging, json, pika, time
connection_parameters = pika.ConnectionParameters('localhost')
url_serializer = URLSafeTimedSerializer(settings.url_secret_key, salt=settings.url_email_salt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hasher():

    @staticmethod
    def hash_password(password: str):
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(password: str, hashed_password:str) -> bool:
        return pwd_context.verify(password, hashed_password)
    
class TokenMaker():

    @staticmethod
    def create_jwt_token(data_to_encrypt: dict) -> str:
        to_encode = data_to_encrypt.copy()
        to_encode["exp"] = datetime.now() + timedelta(minutes=settings.access_token_expire_minutes)
        token = jwt.encode(payload=to_encode,key=settings.jwt_secret_key,algorithm=settings.jwt_algorithm)
        return token
    
    @staticmethod
    def decode_jwt_token(token: str) -> dict:
        try:
            token_data =jwt.decode(token,settings.jwt_secret_key , settings.jwt_algorithm)
            return token_data
        except Exception as err:
            raise TokenDecodeFail(info={"error":f"{err}"})
        
class UrlSerializer():
    @staticmethod
    def create_url_safe_token(token_data: dict) -> str:
        token = url_serializer.dumps(obj=token_data)
        return token
    
    @staticmethod
    def decode_url_safe_token(token: str):
        try:
            token_data = url_serializer.loads(token)
            return token_data
        except Exception as e:
            raise e


def connect_to_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(connection_parameters)
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("Failed to connect to RabbitMq. Retrying in 5seconds...")
            time.sleep(5)

class MailSender():
    @staticmethod
    def create_message(user_email:str, subject:str):
        message_data_dict = {}
        message_data_dict["mail"] = user_email
        message_data_dict["subject"] = subject
        token = UrlSerializer.create_url_safe_token({"email":user_email})
        message_data_dict["token"] = token
        message_data = json.dumps(message_data_dict)
        try:
            connection = connect_to_rabbitmq()
            channel = connection.channel()
            channel.queue_declare(queue=settings.routing_key, durable=True)
            channel.basic_publish(exchange="", routing_key=settings.routing_key, body=message_data, properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE))
        except Exception as err:
            print(f"Failed to publish message: {err}")
        finally:
            channel.close()
            connection.close()

        return message_data
        

