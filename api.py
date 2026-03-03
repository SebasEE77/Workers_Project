import uuid
import json
import psycopg2
import pika
import time
from fastapi import FastAPI

app = FastAPI()

def get_db():
   return psycopg2.connect(
      dbname = "tasksdb",
      user = "postgres",
      password = "Sebas123",
      host = "postgres"
   )

def get_rabbitMQ():
   credentials = pika.PlainCredentials('user', 'password')
   connection = pika.BlockingConnection(
      pika.ConnectionParameters(host='rabbitmq', credentials=credentials)) #El rabbit esta en mi maquina
   channel = connection.channel()

   channel.queue_declare(queue='tasks') #Cola de tasks
   return connection, channel

#Se llama a este endpoint para crear una orden
@app.post("/orders", status_code=202)
def create_order():
   task_id = str(uuid.uuid4())
   con = get_db()
   cur = con.cursor() #Cursor de la BD para ejecutar consultas

   #Inserta los datos en las tablas
   cur.execute("INSERT INTO tasks (task_id, task_status) VALUES (%s, %s)", (task_id, 'pending'))
   cur.execute("INSERT INTO orders (task_id) VALUES (%s)", (task_id,))

   con.commit()
   cur.close()
   con.close()

   connection, channel = get_rabbitMQ()
   channel.basic_publish(
      exchange = '',
      routing_key = 'tasks', #Nombre de la cola a que se envia el mensaje
      body = json.dumps({"task_id": task_id}) #Se manda el task_id como mensaje
   )
   connection.close()

   #Responde al cliente
   return {"task_id": task_id, "task_status": "pending"}

#Se llama a este endpoint para saber el estado de la tarea
@app.get("/tasks/{task_id}")
def get_task(task_id: str):
   con = get_db()
   cur = con.cursor()

   #Se busca la tarea por su ID
   cur.execute("SELECT task_id, task_status, task_date FROM tasks WHERE task_id = %s", (task_id,))

   row = cur.fetchone() #Ayuda a obtener el primer resultado encontrado
   cur.close()
   con.close()

   #Si se encontro la tarea se devuelve, sino imprime un mensaje
   if not row:
      return {"Error": "No se encontro la Tarea"}
   else:
      return {
        "task_id": str(row[0]),
        "task_status": row[1],
	"task_date": str(row[2])
      }

#Devuelve las ordenes creadas
@app.get("/orders")
def get_orders():
   con = get_db()
   cur = con.cursor()

   #Se obtienen las ordenes
   cur.execute("SELECT order_id, task_id, order_date FROM orders")

   rows = cur.fetchall() #Ayuda a obtener todos los resultados
   cur.close()
   con.close()

   #Devuelve la lista de ordenes que haya
   return [{ "order_id": r[0],
        "task_id": str(r[1]),
        "task_date": str(r[2])} for r in rows]

#Actualiza el estado de una tarea
@app.put("/tasks/{task_id}")
def update_task(task_id: str, new_status: str):
   con = get_db()
   cur = con.cursor()

   #Se actualiza la tarea en la BD
   cur.execute("UPDATE tasks SET task_status = %s WHERE task_id = %s", (new_status, task_id))

   if cur.rowcount == 0:
      cur.close()
      con.close()
      return {"Error": "No se encontro la tarea"}

   con.commit()
   cur.close()
   con.close()

   #Se actualiza con los valores correctamente
   return { "task_id": task_id, "task_status": new_status}

#Elimina una tarea de la BD
@app.delete("/tasks/{task_id}")
def update_task(task_id: str):
   con = get_db()
   cur = con.cursor()

   #Se elimina la orden asociada a la tarea
   cur.execute("DELETE FROM orders WHERE task_id = %s", (task_id,))

   #Se elimina la tarea de la BD
   cur.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))

   con.commit()
   cur.close()
   con.close()

   return {"message": f"Tarea {task_id} se elimino"}


