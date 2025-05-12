from databases import Database

# Fix the connection string (only one @)
DATABASE_URL = "postgresql+asyncpg://postgres:Pass@54321@localhost/fastapi_logs"

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

