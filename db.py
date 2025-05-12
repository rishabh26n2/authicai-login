import os
from databases import Database

# Fix the connection string (only one @)
DATABASE_URL = os.getenv("DATABASE_URL")
database = Database(DATABASE_URL)

async def insert_log(ip_address, location, user_agent):
    query = """
    INSERT INTO request_logs (ip_address, location, user_agent)
    VALUES (:ip_address, :location, :user_agent)
    """
    await database.execute(query, values={
        "ip_address": ip_address,
        "location": location,
        "user_agent": user_agent
    })

