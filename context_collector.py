import requests

GEOLOCATION_API_URL = "http://api.ipstack.com/"
API_KEY = "cd656120f01ff045bff14d33bb81b432"  # (temporary fix)

def get_location_from_ip(ip_address: str) -> str:
    try:
        response = requests.get(f"{GEOLOCATION_API_URL}{ip_address}?access_key={API_KEY}")
        response.raise_for_status()
        data = response.json()
        print("Geo API Response:", data)
        city = data.get("city")
        country = data.get("country_name")
        return f"{city}, {country}" if city and country else "Unknown Location"
    except requests.RequestException as e:
        print("Geo API Error:", str(e))
        return "Unknown Location"


def get_location_from_coordinates(lat: float, lon: float) -> str:
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {"User-Agent": "AuthicAI/1.0"}  # Required by Nominatim
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        address = data.get("address", {})

        # Improved fallback logic
        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("state")
            or address.get("county")
            or "Unknown"
        )
        country = address.get("country", "Unknown")
        return f"{city}, {country}"
    except Exception as e:
        print("Reverse geolocation failed:", e)
        return "Unknown Location"
