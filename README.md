# Asynchronous Request-Reply with RabbitMQ
This project simulates the Asynchronous Reques-Reply pattern. When a client creates an order, the API responds immediately with a task_id and a status, while a worker processes the task in the background and updates the status in the database.

Requirements
- Docker
- Docker Compose

Step by Step
1. Start the containers with this command on the Linux terminal: sudo docker compose up -d --build

2. Verify the containers are running: sudo docker compose ps
You should see all 4 containers with status UP, being:
- rabbitmq_server
- postgres_server
- api_server
- worker_server

3. Verify RabbitMQ is working. Open your browser and go to: http://localhost:15672
- User: user
- Password: password
You should see the RabbitMQ management interface. Go to "Queues and Streams" and check the "tasks" queue exists. If it appears is working.

4. Test the API with the Swagger. Open your browser and go to: http://localhost:8000/docs
You should see the Swagger interface with all available endpoints.

5. Now test the project with one of the endpoints. Because there's no orders or tasks to look yet, first create an order (POST/orders).
- Click on POST/orders
- Click Try it out
- Click Execute
- You should get a 202 response with a task_id and a task_status: 'pending'

6. At this time the worker is working in the background, and to verify that is processing the task write this command on the terminal: sudo docker logs -f worker_server
Here you can see all the tasks that the worker process.

7. Also you can check the API logs to see all the requests made to the API in real time. In a terminal just run this command: sudo docker logs -f api_server

8. Check the task status if it change after you create an order(GET/tasks/{task_id})
- In the Swagger click on GET/tasks/{task_id}
- Click Try it out
- Paste the task_id from step 5
- Click Execute
- The task_status should now be 'completed' because the worker process it.

9. If you want to create more orders and change their status or delete one, your gonna need the task_id, and to see all the list you can check all the orders (GET/orders)
- In the Swagger click on GET/orders
- Click Try it out
- Click Execute
- You should see a list of all created orders

10. If you finish looking the project you can stop the containers with this command: sudo docker compose down
