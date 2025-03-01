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
