import requests
import sys

api_key = "896a85bb7f651d22eef2296c826a332f"


def main() -> int:
    print("Testing OpenWeather API...")
    print(f"API Key: {api_key}\n")

    # Test with HTTP
    print("1. Testing with HTTP:")
    r = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q=Paris&appid={api_key}')
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   City: {data.get('name')}")
        print(f"   Temp: {data.get('main', {}).get('temp')} K")
    else:
        print(f"   Error: {r.text[:100]}")

    # Test with HTTPS
    print("\n2. Testing with HTTPS:")
    r = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q=Paris&appid={api_key}')
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   City: {data.get('name')}")
        print(f"   Temp: {data.get('main', {}).get('temp')} K")
        print("\n✓ OpenWeather API is working!")
        return 0

    print(f"   Error: {r.text[:100]}")
    print("\n✗ API key needs time to activate (wait 10-30 minutes)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
