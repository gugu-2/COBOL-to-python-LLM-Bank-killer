import os
import logging
from sqlalchemy import create_engine, text
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)

@dataclass
class CustomerRecord:
    cust_id: int
    cust_name: str
    cust_bal: float

class CustomerManager:
    def __init__(self):
        # SECURITY UPGRADE: Fetching credentials from environment instead of hardcoding
        self.db_user = os.environ.get("DB_USER", "default_user")
        self.db_pass = os.environ.get("DB_PASS", "default_pass")
        
        # SQLAlchemy modern connection string
        self.db_url = f"postgresql://{self.db_user}:{self.db_pass}@localhost:5432/db2database"
        self.engine = create_engine(self.db_url)

    def fetch_customer(self, cust_id: int):
        with self.engine.connect() as conn:
            query = text("SELECT NAME, BALANCE FROM CUSTOMERS WHERE ID = :cust_id")
            result = conn.execute(query, {"cust_id": cust_id}).fetchone()
            
            if result:
                logging.info(f"Fetched Customer: {result[0]} Balance: {result[1]}")
            else:
                logging.warning(f"Customer {cust_id} not found.")

    def call_external_svc(self, cust_id: int):
        # Replaced proprietary Mainframe CALL with modern REST API request
        import requests
        response = requests.post("https://api.internal.com/auth", json={"id": cust_id})
        logging.info(f"Auth Service Status: {response.status_code}")

if __name__ == "__main__":
    app = CustomerManager()
    app.fetch_customer(10045)
