import json
import time
import pika
import psycopg2

time.sleep(30)

def get_db():
   return psycopg2.connect(
      dbname = "tasksdb",
      user = "postgres",
      password = "Sebas123",
      host = "postgres"
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

credentials = pika.PlainCredentials('user', 'password')
connection = pika.BlockingConnection(
   pika.ConnectionParameters(host='rabbitmq', credentials=credentials)) #El rabbit esta en mi maqu>
channel = connection.channel()

channel.queue_declare(queue='tasks') #Cola de tasks

#RabbitMQ llama a callback cada vez que haya un mensaje
#Elimina el mensaje apenas se entregue al worker (True)
channel.basic_consume(queue='tasks', on_message_callback=callback, auto_ack=True)
channel.start_consuming() #El worker se queda escuchando...
