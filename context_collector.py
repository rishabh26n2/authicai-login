import requests

GEOLOCATION_API_URL = "http://api.ipstack.com/"
API_KEY = "cd656120f01ff045bff14d33bb81b432"  # (temporary fix)

# def get_location_from_ip(ip_address: str) -> str:
#     try:
#         response = requests.get(f"{GEOLOCATION_API_URL}{ip_address}?access_key={API_KEY}")
#         response.raise_for_status()
#         data = response.json()
#         print("Geo API Response:", data)
#         city = data.get("city")
#         country = data.get("country_name")
#         return f"{city}, {country}" if city and country else "Unknown Location"
#     except requests.RequestException as e:
#         print("Geo API Error:", str(e))
#         return "Unknown Location"

def get_location_from_ip(ip_address: str):
    """
    Returns a tuple: (location_str, (latitude, longitude)).
    """
    try:
        resp = requests.get(
            f"{IPSTACK_URL}{ip_address}",
            params={"access_key": API_KEY}
        )
        resp.raise_for_status()
        data = resp.json()
        # Handle unsupported batch plan response
        if data.get("success") is False and data.get("error", {}).get("code") == 303:
            return "Unknown Location", (None, None)

        city = data.get("city")
        country = data.get("country_name")
        lat = data.get("latitude")
        lon = data.get("longitude")
        loc_str = f"{city}, {country}" if city and country else country or city or "Unknown Location"
        return loc_str, (lat, lon)
    except requests.RequestException:
        return "Unknown Location", (None, None)


def get_location_from_coordinates(lat: float, lon: float) -> str:
    """
    Reverse-geocode GPS coords into a human-readable location.
    """
    try:
        url = (
            f"https://nominatim.openstreetmap.org/reverse?format=json"
            f"&lat={lat}&lon={lon}"
        )
        headers = {"User-Agent": "AuthicAI/1.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        address = data.get("address", {})
        city = (
            address.get("city") or address.get("town") or address.get("village")
            or address.get("hamlet") or address.get("county") or address.get("state")
        )
        country = address.get("country")
        return f"{city}, {country}" if city and country else "Unknown Location"
    except Exception:
        return "Unknown Location"
