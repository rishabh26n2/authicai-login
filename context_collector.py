import requests
import time

API_KEY = "cd656120f01ff045bff14d33bb81b432"
GEOLOCATION_API_URL = "http://api.ipstack.com/"

def get_location_from_ip(ip_address: str):
    """
    Returns a tuple: (location_str, (latitude, longitude)).
    Tries IPStack → falls back to ipwho.is → logs reason clearly.
    """
    # --- Try IPStack first
    try:
        print(f"🌐 Trying IPStack for IP: {ip_address}")
        resp = requests.get(
            f"{GEOLOCATION_API_URL}{ip_address}",
            params={"access_key": API_KEY},
            timeout=4  # ⏱️ 4-second timeout
        )
        print("🔁 IPStack raw response:", resp.text)
        resp.raise_for_status()
        data = resp.json()

        if data.get("success") is False:
            print("⚠️ IPStack error:", data.get("error"))
            raise ValueError("IPStack quota hit or bad key")

        city = data.get("city")
        country = data.get("country_name")
        lat = data.get("latitude")
        lon = data.get("longitude")
        loc_str = f"{city}, {country}" if city and country else country or city or "Unknown Location"
        print(f"✅ IPStack location: {loc_str}")
        return loc_str, (lat, lon)

    except Exception as e:
        print("⚠️ IPStack failed, trying ipwho.is:", e)

    # --- Fallback to ipwho.is
    try:
        print(f"🌐 Trying ipwho.is for IP: {ip_address}")
        r2 = requests.get(f"https://ipwho.is/{ip_address}", timeout=4)
        print("🔁 ipwho.is raw response:", r2.text)
        r2.raise_for_status()
        data = r2.json()

        if not data.get("success"):
            print("⚠️ ipwho.is error:", data.get("message"))
            raise ValueError("ipwho.is failed")

        city = data.get("city")
        country = data.get("country")
        lat = data.get("latitude")
        lon = data.get("longitude")
        loc_str = f"{city}, {country}" if city and country else country or city or "Unknown Location"
        print("✅ ipwho.is location:", loc_str)
        return loc_str, (lat, lon)

    except Exception as e2:
        print("❌ Both IPStack and ipwho.is failed:", e2)

    return "Unknown Location", (None, None)


def get_location_from_coordinates(lat: float, lon: float) -> str:
    """
    Reverse-geocode GPS coords into a human-readable location.
    """
    try:
        print(f"🌍 Reverse-geocoding coordinates: {lat}, {lon}")
        url = (
            f"https://nominatim.openstreetmap.org/reverse?format=json"
            f"&lat={lat}&lon={lon}"
        )
        headers = {"User-Agent": "AuthicAI/1.0"}
        response = requests.get(url, headers=headers, timeout=4)
        print("🔁 Nominatim raw response:", response.text)
        response.raise_for_status()
        data = response.json()
        address = data.get("address", {})
        city = (
            address.get("city") or address.get("town") or address.get("village")
            or address.get("hamlet") or address.get("county") or address.get("state")
        )
        country = address.get("country")
        if city and country:
            location = f"{city}, {country}"
            print(f"✅ Reverse-geocoded location: {location}")
            return location
        return "Unknown Location"
    except Exception as e:
        print("⚠️ Nominatim error:", e)
        return "Unknown Location"
