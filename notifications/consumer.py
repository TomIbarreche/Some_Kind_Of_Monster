import pika, os, sys, time,requests, json

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()
    channel.queue_declare(queue="letterbox", durable=True)

    def callback(channel, method, properties, body):
        try:
            data = json.loads(body.decode())
            print(f"[x] Message received: {data}")
            response = requests.post(
                        url=f"http://localhost:80/api/v1/mail/send_email",
                        json={
                            "receiver":data["mail"],
                            "subject":data["subject"],
                            "token":data["token"]
                        })
            
            if response.status_code != 200:
                channel.basic_nack(delivery_tag=method.delivery_tag)
                print("Something went wrong")
            else:
                channel.basic_ack(delivery_tag=method.delivery_tag)
                print("Response OK")
        except Exception as err:
            print(f"Error processing message: {err}")
            channel.basic_nack(delivery_tag=method.delivery_tag)

            
    channel.basic_consume(
        queue="letterbox", on_message_callback= callback
    )

    print("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)