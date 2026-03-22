import json
import time
import pika
import psycopg2
import boto3
from botocore.exceptions import ClientError

time.sleep(30)

# Obtener parametro del Parameter Store
def get_ssm_parameter(name: str, default: str = None) -> str:
   client = boto3.client("ssm", region_name="us-east-1")
   try:
      response = client.get_parameter(Name=name)
      return response["Parameter"]["Value"]
   except ClientError as e:
      if e.response["Error"]["Code"] == "ParameterNotFound":
         print(f"[WARN] Parametro '{name}' no encontrado. Usando: '{default}'")
         return default
      raise

# Conexion a PostgreSQL leyendo IP del Parameter Store
def get_db():
   postgres_ip = get_ssm_parameter(
      name="/message-queue/dev/postgres/public_ip",
      default="localhost"
   )
   return psycopg2.connect(
      dbname="tasksdb",
      user="postgres",
      password="Sebas123",
      host=postgres_ip,
      port=5432
   )

def callback(ch, method, properties, body):
   message = json.loads(body) #Se convierte el mensaje json a dic
   task_id = message["task_id"]

   print(f"Procesando la tarea {task_id}")

   con = get_db()
   cur = con.cursor()

   #Actualiza el estado de la tarea a 'processing'
   cur.execute("UPDATE tasks SET task_status = %s WHERE task_id = %s", ('processing', task_id))
   con.commit()

   time.sleep(8) #Se simula que demora 8 seg en procesar

   #Actualiza el estado de la tarea a 'completed'
   cur.execute("UPDATE tasks SET task_status = %s WHERE task_id = %s", ('completed', task_id))
   con.commit()

   cur.close()
   con.close()

   print(f"Tarea {task_id} completada")

# Conexion a RabbitMQ leyendo IP del Parameter Store
rabbitmq_ip = get_ssm_parameter(
   name="/message-queue/dev/rabbitmq/public_ip",
   default="localhost"
)
credentials = pika.PlainCredentials('user', 'password')
connection = pika.BlockingConnection(
   pika.ConnectionParameters(host=rabbitmq_ip, credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue='tasks') #Cola de tasks

#RabbitMQ llama a callback cada vez que haya un mensaje
#Elimina el mensaje apenas se entregue al worker (True)
channel.basic_consume(queue='tasks', on_message_callback=callback, auto_ack=True)
channel.start_consuming() #El worker se queda escuchando...
