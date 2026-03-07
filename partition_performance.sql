-- =====================================
-- PostgreSQL Partitioning Demo Script
-- =====================================

-- How to run:
-- dropdb --if-exists partition_performance_demo && createdb partition_performance_demo && psql -f partition_performance.sql partition_performance_demo 

-- 1. Drop existing tables if they exist
DROP TABLE IF EXISTS orders_old CASCADE;
DROP TABLE IF EXISTS orders_partitioned CASCADE;

-- 2. Create a normal table
CREATE TABLE orders (
    id serial PRIMARY KEY,
    order_date date NOT NULL,
    customer_id int NOT NULL,
    amount numeric(10,2) NOT NULL
);

-- 3. Populate with demo data (1M rows over 3 years)
INSERT INTO orders (order_date, customer_id, amount)
SELECT
    date '2020-01-01' + (random() * 1095)::int,  -- random date over 3 years
    (random() * 1000)::int,
    (random() * 1000)::numeric(10,2)
FROM generate_series(1, 1000000);

-- 4. Index for faster queries
CREATE INDEX idx_orders_date ON orders(order_date);

-- 5. Query performance BEFORE partitioning
-- Choose a year for testing
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE order_date BETWEEN '2021-01-01' AND '2021-12-31';

-- 6. Create partitioned table
CREATE TABLE orders_partitioned (
    id serial,
    order_date date NOT NULL,
    customer_id int NOT NULL,
    amount numeric(10,2) NOT NULL,
    PRIMARY KEY (id, order_date) -- must include partitioning column
) PARTITION BY RANGE (order_date);

-- 7. Create partitions
CREATE TABLE orders_2020 PARTITION OF orders_partitioned
FOR VALUES FROM ('2020-01-01') TO ('2021-01-01');

CREATE TABLE orders_2021 PARTITION OF orders_partitioned
FOR VALUES FROM ('2021-01-01') TO ('2022-01-01');

CREATE TABLE orders_2022 PARTITION OF orders_partitioned
FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');

-- Optional default partition
CREATE TABLE orders_default PARTITION OF orders_partitioned DEFAULT;

-- 8. Migrate data from old table
INSERT INTO orders_partitioned (id, order_date, customer_id, amount)
SELECT id, order_date, customer_id, amount
FROM orders;

-- 9. Indexes on partitions (optional, important for large tables)
CREATE INDEX idx_orders_2020_date ON orders_2020(order_date);
CREATE INDEX idx_orders_2021_date ON orders_2021(order_date);
CREATE INDEX idx_orders_2022_date ON orders_2022(order_date);

-- 10. Query performance AFTER partitioning
EXPLAIN ANALYZE
SELECT * FROM orders_partitioned
WHERE order_date BETWEEN '2021-01-01' AND '2021-12-31';

-- 11. Optional: see routing of rows using tableoid
SELECT tableoid::regclass, COUNT(*) 
FROM orders_partitioned 
GROUP BY tableoid::regclass;
