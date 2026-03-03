CREATE TABLE tasks (
    task_id UUID PRIMARY KEY,
    task_status VARCHAR(30) DEFAULT 'pending',
    task_date TIMESTAMP DEFAULT NOW()
);
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(task_id),
    order_date TIMESTAMP DEFAULT NOW()
);
