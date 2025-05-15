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
    is_suspicious: bool = False,
    username: str = None,
    latitude: float = None,
    longitude: float = None
):
    """
    Insert a login attempt into request_logs, recording:
      - ip_address
      - location
      - user_agent
      - username
      - latitude / longitude (if available)
      - numeric risk_score (0–100)
      - boolean is_suspicious flag
    """
    query = """
    INSERT INTO request_logs (
      ip_address,
      location,
      user_agent,
      username,
      latitude,
      longitude,
      risk_score,
      is_suspicious
    ) VALUES (
      :ip_address,
      :location,
      :user_agent,
      :username,
      :latitude,
      :longitude,
      :risk_score,
      :is_suspicious
    )
    """
    await database.execute(query, values={
        "ip_address":    ip_address,
        "location":      location,
        "user_agent":    user_agent,
        "username":      username,
        "latitude":      latitude,
        "longitude":     longitude,
        "risk_score":    risk_score,
        "is_suspicious": is_suspicious
    })

async def fetch_last_login(username: str):
    """
    Fetch the most recent login record for this username,
    returning timestamp, latitude, longitude, and location.
    """
    query = """
    SELECT
      timestamp,
      latitude,
      longitude,
      location
    FROM request_logs
    WHERE username = :username
    ORDER BY timestamp DESC
    LIMIT 1
    """
    row = await database.fetch_one(query, values={"username": username})
    return row   # will be a dict-like with keys 'timestamp','latitude','longitude','location'
