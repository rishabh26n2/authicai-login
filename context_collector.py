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

def get_location_from_ip(ip_address: str) -> str:
    try:
        r = requests.get(f"{GEOLOCATION_API_URL}{ip_address}?access_key={API_KEY}")
        r.raise_for_status()
        data = r.json()

        # If IPStack says "batch_not_supported_on_plan", bail out
        if data.get("success") is False and data.get("error", {}).get("code") == 303:
            return "Unknown Location"

        city = data.get("city")
        country = data.get("country_name")
        if city and country:
            return f"{city}, {country}"
        return "Unknown Location"
    except requests.RequestException:
        return "Unknown Location"

def get_location_from_coordinates(lat: float, lon: float) -> str:
    """
    Reverse-geocode GPS coords into the most specific location possible.
    Tries: city → town → village → hamlet → municipality → county → suburb → state → Unknown
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {"User-Agent": "AuthicAI/1.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        address = data.get("address", {})

        # Look for the most precise field available
        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("hamlet")
            or address.get("municipality")
            or address.get("county")
            or address.get("suburb")
            or address.get("state")
            or "Unknown"
        )
        country = address.get("country", "Unknown")
        return f"{city}, {country}"
    except Exception as e:
        print("Reverse geolocation failed:", e)
        return "Unknown Location"
