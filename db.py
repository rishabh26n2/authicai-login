import os
from databases import Database

# Read the database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
database = Database(DATABASE_URL)

async def insert_log(
    ip_address: str,
    location: str,
    user_agent: str,
    risk_score: int = 0,
    is_suspicious: bool = False
):
    """
    Insert a login attempt into request_logs, recording:
      - ip_address
      - location
      - user_agent
      - numeric risk_score (0–100)
      - boolean is_suspicious flag
    """
    query = """
    INSERT INTO request_logs (
      ip_address,
      location,
      user_agent,
      risk_score,
      is_suspicious
    ) VALUES (
      :ip_address,
      :location,
      :user_agent,
      :risk_score,
      :is_suspicious
    )
    """
    await database.execute(query, values={
        "ip_address":    ip_address,
        "location":      location,
        "user_agent":    user_agent,
        "risk_score":    risk_score,
        "is_suspicious": is_suspicious
    })
