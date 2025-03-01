# Setup Instructions

## 1. Create a Virtual Environment and Install Requirements
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Setup Redis
### Install Redis
#### For Linux:
```sh
sudo apt install redis-server
```
#### For macOS:
```sh
brew install redis
```

### Run Redis Server
```sh
redis-server --port 6000 --daemonize yes
```

## 3. Configure Environment Variables
Add a `.env` file inside `app/core/` and specify the `DB_PATH`. Example:
```sh
DB_PATH=/Users/vinit.kumar/order-process-system/test.db
```

## 4. Pre-Populate Database
Run the script to pre-populate data:
```sh
python pre_populate_script.py
```

## 5. Start the Server
```sh
uvicorn app.main:app --reload
```

## 6. Import Postman Collection
Import the provided Postman collection and start testing your API. 🚀

### Postman Collection Explanation
The Postman collection includes the following API requests:

#### 1. Create an Order (POST `/orders/`)
- **Request:**
  ```json
  {
    "user_id": "user123",
    "item_ids": ["item1", "item2"],
    "total_amount": 99.99
  }
  ```
- **Response:**
  ```json
  {
    "order_id": "ORD-1740795753808"
  }
  ```
- **Endpoints:**
  - `http://localhost:8000/orders/` (Localhost)
  - `http://51.20.56.95:8000/orders/` (AWS Server)

#### 2. Get Order Status (GET `/orders/{order_id}`)
- **Request:**
  ```sh
  GET http://localhost:8000/orders/ORD-1234567890
  ```
- **Response:**
  ```json
  {
    "order_id": "ORD-1740795753808",
    "status": "completed",
    "created_at": "2025-03-01T02:22:33.831868",
    "user_id": "201a8e4a-c775-4266-a151-9db20b786f2d",
    "total_amount": 999.99,
    "completed_at": "2025-03-01T02:22:34.062146",
    "updated_at": "2025-03-01T02:22:34.081146"
  }
  ```

#### 3. Get System Metrics (GET `/orders/metrics`)
- **Request:**
  ```sh
  GET http://localhost:8000/orders/metrics
  ```
- **Response:**
  ```json
  {
    "average_processing_time_seconds": 0,
    "order_status_counts": {
        "pending": 6,
        "processing": 4,
        "completed": 7765
    }
  }
  ```

#### 4. Get Orders Status in Queue (GET `/orders/status/`)
- **Request:**
  ```sh
  GET http://localhost:8000/orders/status/
  ```

This collection allows you to test order creation, order status retrieval, system metrics, and queue status. 🚀

# Scalable Order Processing System

## 🚀 Overview
This is a highly scalable order-processing system designed to handle **1000+ concurrent orders** efficiently. It utilizes **FastAPI, SQLite, Redis, and Custom Worker Processes** to process orders asynchronously and update order statuses dynamically.

## 🏗️ Architecture Design

### 📌 System Workflow
1️⃣ **Order Creation API (FastAPI)**
   - Accepts `user_id`, `item_ids`, and `total_amount`.
   - Stores order **in SQLite** (initially **PENDING** state).
   - Pushes `order_id` to **Redis queue** for background processing.
   - Returns `order_id` instantly.

2️⃣ **Redis Queue**
   - Acts as a **message broker**.
   - Stores orders in **FIFO order** for processing by workers.

3️⃣ **Custom Worker Process**
   - Fetches `order_id` from Redis queue.
   - Updates order **status → PROCESSING**.
   - Simulates order processing (e.g., payment verification, stock check).
   - Updates order **status → COMPLETED** in the database.
   - Updates Redis with **order metrics** (total orders processed, avg time, etc.).

4️⃣ **Metrics API (FastAPI)**
   - Fetches key insights:
     - **Total orders processed**.
     - **Average processing time**.
     - **Orders count per status (PENDING, PROCESSING, COMPLETED)**.
   - Uses **Redis for real-time metrics** to avoid slow DB queries.

## 📊 System Design Diagram
```
+-----------------------+
|   Order API (FastAPI) |
+-----------------------+
           │
           ▼
+---------------------+
|  SQLite Database  |
+---------------------+
           │
           ▼
+-------------------+
| Redis Queue      |
| ("order_queue")  |
+-------------------+
           │
           ▼
+------------------------+
| Background Worker (Custom) |
+------------------------+
       │               │
       ▼               ▼
+-------------+    +----------------+
| Order Status|    | Update Metrics |
| (DB Update) |    | (Redis)        |
+-------------+    +----------------+
       │
       ▼
+----------------------------+
| Metrics API (FastAPI)      |
+----------------------------+
```

## ⚡ Technologies Used
- **FastAPI** - For handling API requests.
- **SQLite** - Lightweight database for storing orders.
- **Redis** - In-memory queue for fast order processing.
- **Custom Worker** - To process orders asynchronously.
- **SQLAlchemy** - ORM for database interactions.
- **Docker / Kubernetes** - For containerized deployment and scalability.

## 🔥 Optimizations & Scalability
✅ **Batch Processing in Workers:** Process **10-50 orders at once** instead of one-by-one.

✅ **Multiple Worker Processes:** Run multiple worker instances for better parallel processing.

✅ **Redis Streams Instead of List:** Use **`XADD`/`XREADGROUP`** instead of `RPUSH`/`LPOP` for better durability & scaling.

✅ **SQLite Write Optimization:**
- Use **WAL (Write-Ahead Logging) mode** for better concurrency.
```sql
PRAGMA journal_mode=WAL;
```
- Increase timeout to **prevent database lock errors**.
```python
connect_args={"timeout": 30}
```

✅ **Horizontal Scaling (Kubernetes, Load Balancer):**
- Deploy **FastAPI behind a load balancer (Nginx)**.
- Use **Redis Cluster** for high availability.
- **Autoscale workers** based on queue size.

## 🚀 How to Run
### **1. Clone the Repository**
```sh
git clone https://github.com/your-repo/scalable-order-system.git
cd scalable-order-system
```

### **2. Start Redis** (via Docker Compose)
```sh
docker-compose up -d redis
```

### **3. Run FastAPI Application**
```sh
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **4. Start the Custom Worker**
```sh
python worker.py
```

### **5. Test the API**
Use `curl` or Postman to create an order:
```sh
curl -X POST "http://localhost:8000/orders/" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "item_ids": [101, 102], "total_amount": 250}'
```

## 🎯 Final Thoughts
This **design ensures scalability, efficiency, and fault tolerance**. With optimizations, it can **handle 10,000+ concurrent orders** easily! 🚀

Let me know if you need improvements! 😊


