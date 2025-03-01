from locust import HttpUser, task, between
import random
# from ..pre_populate_script import SAMPLE_ITEMS, SAMPLE_USERS
SAMPLE_USERS = [
    {"id":"201a8e4a-c775-4266-a151-9db20b786f2d","name": "John Doe", "email": "john@example.com"},
    {"id":"2b035824-f340-44a0-bea3-16a61eb04358","name": "Jane Smith", "email": "jane@example.com"},
    {"id":"af798990-6dc6-47fd-b070-a8cacaba6d96","name": "Bob Wilson", "email": "bob@example.com"},
    {"id":"800a01c6-3809-4bec-a1e6-f703265f35f7","name": "Alice Brown", "email": "alice@example.com"},
    {"id":"6fdce818-259e-48b6-804a-c7acc4a46546","name": "Mike Johnson", "email": "mike@example.com"},
]

SAMPLE_ITEMS = [
    {"id":"22cb61f8-58fc-4a29-b6a1-65b469d58561","name": "Laptop", "description": "High performance laptop", "price": 999.99},
    {"id":"4cee3042-5a7c-4f63-b06e-3c7f6c5c2f0f","name": "Smartphone", "description": "Latest model", "price": 699.99},
    {"id":"95393f99-18f2-4363-872c-db5b7c8ec296","name": "Headphones", "description": "Wireless headphones", "price": 199.99},
    {"id":"f0d909fc-8218-48b2-ae50-2b98eb3cd4e1","name": "Mouse", "description": "Gaming mouse", "price": 49.99},
    {"id":"201a8e4a-c775-4266-a151-9db20b786f2d","name": "Keyboard", "description": "Mechanical keyboard", "price": 89.99},
    {"id":"48e6c2c6-1fc4-49fa-8a69-e31c12285af0","name": "Monitor", "description": "27-inch 4K display", "price": 299.99},
    {"id":"1f5a6b78-b5fe-4aa1-a198-c593fb3dea96","name": "Tablet", "description": "10-inch tablet", "price": 399.99}
]

class OrderCreationUser(HttpUser):
    wait_time = between(0.1, 0.5)  # Wait between 0.1 and 0.5 seconds between tasks
    
    @task
    def create_order(self):
        # Generate random order data
        random_item1 = random.choice(SAMPLE_ITEMS)
        random_item2 = random.choice(SAMPLE_ITEMS)
        random_user = random.choice(SAMPLE_USERS)

        payload = {
            "user_id": random_user["id"],
            "item_ids": [
                random_item1["id"],
                random_item2["id"]
            ],
            "total_amount": round(random_item2["price"]+random_item1["price"],1)
        }
        
        # Send POST request to create order
        self.client.post("/orders/", json=payload)

    # @task
    # def get_metrics(self):
    #     # Periodically check metrics
    #     self.client.get("/metrics") 