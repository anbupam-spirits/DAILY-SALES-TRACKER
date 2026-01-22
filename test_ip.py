import requests

def get_ip_location():
    print("Testing IP Location...")
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        data = response.json()
        print(f"Response: {data}")
        if 'loc' in data:
            lat, lon = data['loc'].split(',')
            print(f"Success: {lat}, {lon}")
            return float(lat), float(lon)
        else:
            print("No 'loc' in response")
    except Exception as e:
        print(f"Error: {e}")
    return None, None

get_ip_location()
