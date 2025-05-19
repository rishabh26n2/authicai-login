import os
from databases import Database
from datetime import datetime, timedelta, timezone
from typing import List, Optional

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
    longitude: float = None,
    note: Optional[str] = None  # ✅ new field
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
      - optional note (e.g. "MFA passed")
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
      is_suspicious,
      note
    ) VALUES (
      :ip_address,
      :location,
      :user_agent,
      :username,
      :latitude,
      :longitude,
      :risk_score,
      :is_suspicious,
      :note
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
        "is_suspicious": is_suspicious,
        "note":          note  # ✅ pass optional note
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
    return row   # dict-like with keys 'timestamp','latitude','longitude','location'

async def fetch_login_history(
    username: str,
    limit: int = 100
) -> List[datetime]:
    """
    Retrieve the last `limit` login timestamps for a user.
    """
    query = """
    SELECT timestamp
    FROM request_logs
    WHERE username = :username
    ORDER BY timestamp DESC
    LIMIT :limit
    """
    rows = await database.fetch_all(query, values={"username": username, "limit": limit})
    return [row["timestamp"] for row in rows]

async def count_recent_attempts(
    username: str,
    seconds: int = 30
) -> int:
    """
    Count login attempts by `username` within the last `seconds` seconds.
    """
    threshold = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(seconds=seconds)
    query = """
    SELECT COUNT(*) AS count
    FROM request_logs
    WHERE username = :username
      AND timestamp >= :threshold
    """
    row = await database.fetch_one(query, values={"username": username, "threshold": threshold})
    return row["count"] if row and "count" in row else 0
