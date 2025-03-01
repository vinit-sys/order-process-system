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
